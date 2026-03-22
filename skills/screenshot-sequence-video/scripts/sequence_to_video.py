#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


KNOWN_FFMPEG = Path(r"D:\Download\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe")
IMAGE_EXTENSIONS = {".bmp", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class SequenceItem:
    source_path: Path
    sequence_id: str
    capture_index: int
    frame: int | None
    duration_seconds: float | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class NumberedPattern:
    directory: Path
    prefix: str
    suffix: str
    start_number: int
    zero_pad: int

    @property
    def pattern(self) -> str:
        token = f"%0{self.zero_pad}d" if self.zero_pad > 1 else "%d"
        return str((self.directory / f"{self.prefix}{token}{self.suffix}").resolve())


@dataclass(frozen=True)
class SequenceValidation:
    width: int
    height: int
    image_format: str
    image_mode: str


def ensure_dir(path: str | Path) -> Path:
    value = Path(path)
    value.mkdir(parents=True, exist_ok=True)
    return value


def read_json(path: str | Path) -> Any:
    value = Path(path)
    if not value.exists():
        raise RuntimeError(f"File not found: {value}")
    raw = value.read_text(encoding="utf-8-sig").strip()
    if not raw:
        raise RuntimeError(f"JSON file is empty: {value}")
    return json.loads(raw)


def write_json(path: str | Path, data: Any) -> Path:
    value = Path(path)
    ensure_dir(value.parent)
    value.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return value


def parse_int(value: Any, *, field_name: str, default: int | None = None) -> int:
    if value is None or value == "":
        if default is None:
            raise RuntimeError(f"Missing integer field: {field_name}")
        return default
    try:
        return int(value)
    except Exception as exc:
        raise RuntimeError(f"Invalid integer for {field_name}: {value!r}") from exc


def parse_float(value: Any, *, field_name: str, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception as exc:
        raise RuntimeError(f"Invalid float for {field_name}: {value!r}") from exc


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    slug = re.sub(r"-+", "-", slug).strip("-._")
    return slug or "sequence"


def natural_sort_key(value: str) -> list[Any]:
    parts = re.split(r"(\d+)", value)
    key: list[Any] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def resolve_ffmpeg(explicit_path: str | None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        if not path.exists():
            raise RuntimeError(f"Explicit ffmpeg path not found: {path}")
        return path
    if KNOWN_FFMPEG.exists():
        return KNOWN_FFMPEG
    resolved = shutil.which("ffmpeg")
    if resolved:
        return Path(resolved)
    raise RuntimeError(
        f"ffmpeg executable not found. Expected {KNOWN_FFMPEG} or an ffmpeg on PATH."
    )


def ffmpeg_quote(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace("'", r"'\''")


def choose_sequence_id(item: dict[str, Any], fallback_fields: list[str], fallback_index: int) -> str:
    for field in fallback_fields:
        candidate = str(item.get(field) or "").strip()
        if candidate:
            return candidate
    return f"sequence-{fallback_index:04d}"


def load_manifest_items(manifest_path: Path, group_fields: list[str]) -> list[SequenceItem]:
    data = read_json(manifest_path)
    if not isinstance(data, list) or not data:
        raise RuntimeError(f"Manifest must be a non-empty JSON list: {manifest_path}")
    items: list[SequenceItem] = []
    for index, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise RuntimeError(f"Manifest entry #{index} is not an object.")
        image_path = raw.get("image_path")
        if not image_path:
            raise RuntimeError(f"Manifest entry #{index} is missing image_path.")
        source_path = Path(str(image_path)).resolve()
        sequence_id = choose_sequence_id(raw, group_fields, index)
        items.append(
            SequenceItem(
                source_path=source_path,
                sequence_id=sequence_id,
                capture_index=parse_int(raw.get("capture_index"), field_name="capture_index", default=index),
                frame=parse_int(raw.get("frame"), field_name="frame", default=None) if raw.get("frame") is not None else None,
                duration_seconds=parse_float(raw.get("duration_seconds"), field_name="duration_seconds", default=None),
                raw=dict(raw),
            )
        )
    return items


def load_folder_items(input_dir: Path, glob_pattern: str, sequence_id: str | None) -> list[SequenceItem]:
    if not input_dir.exists() or not input_dir.is_dir():
        raise RuntimeError(f"Input directory not found: {input_dir}")
    candidates = [path for path in input_dir.glob(glob_pattern) if path.is_file()]
    candidates = [path for path in candidates if path.suffix.lower() in IMAGE_EXTENSIONS]
    if not candidates:
        raise RuntimeError(f"No image files matched {glob_pattern!r} in {input_dir}")
    candidates.sort(key=lambda path: natural_sort_key(path.name))
    resolved_sequence_id = sequence_id or input_dir.name
    items: list[SequenceItem] = []
    for index, path in enumerate(candidates):
        items.append(
            SequenceItem(
                source_path=path.resolve(),
                sequence_id=resolved_sequence_id,
                capture_index=index,
                frame=None,
                duration_seconds=None,
                raw={"image_path": str(path.resolve())},
            )
        )
    return items


def group_items(items: list[SequenceItem]) -> dict[str, list[SequenceItem]]:
    groups: dict[str, list[SequenceItem]] = {}
    for item in items:
        groups.setdefault(item.sequence_id, []).append(item)
    for sequence_items in groups.values():
        sequence_items.sort(
            key=lambda item: (
                item.capture_index,
                item.frame if item.frame is not None else -1,
                natural_sort_key(item.source_path.name),
            )
        )
    return dict(sorted(groups.items(), key=lambda pair: pair[0]))


def validate_sequence_images(items: list[SequenceItem]) -> SequenceValidation:
    if not items:
        raise RuntimeError("Sequence is empty.")
    for item in items:
        if not item.source_path.exists():
            raise RuntimeError(f"Missing image file: {item.source_path}")
    width: int | None = None
    height: int | None = None
    image_format: str | None = None
    image_mode: str | None = None
    for item in items:
        with Image.open(item.source_path) as image:
            current_width, current_height = image.size
            current_format = str(image.format or item.source_path.suffix.lstrip(".")).upper()
            current_mode = str(image.mode or "unknown")
        if width is None:
            width = current_width
            height = current_height
            image_format = current_format
            image_mode = current_mode
            continue
        if (current_width, current_height) != (width, height):
            raise RuntimeError(
                f"Mixed image dimensions in sequence {items[0].sequence_id!r}: "
                f"expected {(width, height)}, got {(current_width, current_height)} at {item.source_path}"
            )
        if current_format != image_format:
            image_format = "MIXED"
        if current_mode != image_mode:
            image_mode = "MIXED"
    return SequenceValidation(width=width, height=height, image_format=image_format or "UNKNOWN", image_mode=image_mode or "UNKNOWN")


def infer_numbered_pattern(items: list[SequenceItem]) -> NumberedPattern | None:
    if not items:
        return None
    directories = {item.source_path.parent.resolve() for item in items}
    if len(directories) != 1:
        return None
    suffixes = {item.source_path.suffix.lower() for item in items}
    if len(suffixes) != 1:
        return None
    prefix: str | None = None
    suffix: str | None = None
    numbers: list[int] = []
    zero_pad = 0
    for item in items:
        match = re.match(r"^(.*?)(\d+)([^\d]*)$", item.source_path.stem)
        if not match:
            return None
        current_prefix, digits, current_suffix = match.groups()
        if prefix is None:
            prefix = current_prefix
            suffix = current_suffix + item.source_path.suffix
            zero_pad = len(digits)
        elif prefix != current_prefix or suffix != current_suffix + item.source_path.suffix:
            return None
        elif zero_pad != len(digits):
            zero_pad = 0
        numbers.append(int(digits))
    numbers.sort()
    expected = list(range(numbers[0], numbers[0] + len(numbers)))
    if numbers != expected:
        return None
    return NumberedPattern(
        directory=next(iter(directories)),
        prefix=prefix or "",
        suffix=suffix or "",
        start_number=numbers[0],
        zero_pad=zero_pad,
    )


def choose_strategy(items: list[SequenceItem], validation: SequenceValidation, requested: str, fps: int) -> tuple[str, str, NumberedPattern | None]:
    numbered_pattern = infer_numbered_pattern(items)
    has_custom_durations = any(item.duration_seconds is not None for item in items)
    image2_ok = numbered_pattern is not None and validation.image_format != "MIXED" and validation.image_mode != "MIXED" and not has_custom_durations
    if requested == "image2":
        if not image2_ok:
            raise RuntimeError(
                f"Sequence {items[0].sequence_id!r} cannot use image2: require one contiguous numbered pattern, "
                f"uniform format/mode, and no per-frame custom durations."
            )
        return "image2", "forced image2", numbered_pattern
    if requested == "concat":
        return "concat", "forced concat", numbered_pattern
    if image2_ok:
        return "image2", "auto-selected contiguous numbered sequence", numbered_pattern
    return "concat", "auto-selected concat for sparse or non-uniform input", numbered_pattern


def write_concat_file(staging_dir: Path, sequence_slug: str, items: list[SequenceItem], fps: int) -> Path:
    concat_path = staging_dir / f"{sequence_slug}.ffconcat"
    default_duration = 1.0 / float(fps)
    lines = ["ffconcat version 1.0"]
    for item in items[:-1]:
        lines.append(f"file '{ffmpeg_quote(item.source_path)}'")
        duration = item.duration_seconds if item.duration_seconds is not None else default_duration
        lines.append(f"duration {duration:.12f}")
    lines.append(f"file '{ffmpeg_quote(items[-1].source_path)}'")
    if items[-1].duration_seconds is not None:
        lines.append(f"duration {items[-1].duration_seconds:.12f}")
        lines.append(f"file '{ffmpeg_quote(items[-1].source_path)}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return concat_path


def build_common_output_args(args: argparse.Namespace, out_path: Path) -> list[str]:
    command = [
        "-vf",
        f"fps={args.fps},format={args.pix_fmt}",
        "-c:v",
        args.codec,
        "-preset",
        args.preset,
        "-pix_fmt",
        args.pix_fmt,
        "-movflags",
        "+faststart",
    ]
    if args.codec == "libx264":
        command.extend(["-tune", "stillimage", "-crf", str(args.crf)])
    command.append(str(out_path))
    return command


def encode_concat(ffmpeg_exe: Path, args: argparse.Namespace, concat_file: Path, out_path: Path) -> None:
    command = [
        str(ffmpeg_exe),
        "-y" if args.overwrite else "-n",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        *build_common_output_args(args, out_path),
    ]
    subprocess.run(command, check=True)


def encode_image2(ffmpeg_exe: Path, args: argparse.Namespace, pattern: NumberedPattern, out_path: Path) -> None:
    command = [
        str(ffmpeg_exe),
        "-y" if args.overwrite else "-n",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(args.fps),
        "-start_number",
        str(pattern.start_number),
        "-i",
        pattern.pattern,
        *build_common_output_args(args, out_path),
    ]
    subprocess.run(command, check=True)


def build_output_name(sequence_id: str, existing: set[str]) -> str:
    base = slugify(sequence_id)
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}-{suffix}"
        suffix += 1
    existing.add(candidate)
    return candidate


def parse_group_fields(value: str) -> list[str]:
    fields = [part.strip() for part in value.split(",") if part.strip()]
    if not fields:
        raise RuntimeError("--group-by must contain at least one field name.")
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert screenshot sequences into deterministic MP4 review clips.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--manifest", help="JSON list with image_path and optional sequence fields.")
    source_group.add_argument("--input-dir", help="Folder containing image files for a single sequence.")
    parser.add_argument("--glob", default="screen_capture_*.bmp", help="Glob used with --input-dir. Default: screen_capture_*.bmp")
    parser.add_argument("--sequence-id", help="Sequence id for folder mode.")
    parser.add_argument("--group-by", default="sequence_id,attempt_label", help="Comma-separated manifest fallback fields for grouping.")
    parser.add_argument("--output-dir", required=True, help="Directory where MP4 clips and the report will be written.")
    parser.add_argument("--strategy", choices=["auto", "concat", "image2"], default="auto")
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--codec", default="libx264")
    parser.add_argument("--preset", default="veryfast")
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--pix-fmt", default="yuv420p")
    parser.add_argument("--ffmpeg", help="Explicit ffmpeg executable path.")
    parser.add_argument("--report-path", help="Explicit JSON report path. Default: <output-dir>/video_report.json")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fps <= 0:
        raise RuntimeError("--fps must be positive.")

    ffmpeg_exe = resolve_ffmpeg(args.ffmpeg)
    output_dir = ensure_dir(args.output_dir)
    report_path = Path(args.report_path).resolve() if args.report_path else output_dir / "video_report.json"

    if args.manifest:
        items = load_manifest_items(Path(args.manifest).resolve(), parse_group_fields(args.group_by))
        input_summary = {"mode": "manifest", "manifest_path": str(Path(args.manifest).resolve())}
    else:
        items = load_folder_items(Path(args.input_dir).resolve(), args.glob, args.sequence_id)
        input_summary = {"mode": "folder", "input_dir": str(Path(args.input_dir).resolve()), "glob": args.glob}

    groups = group_items(items)
    if not groups:
        raise RuntimeError("No sequences were loaded.")

    staging_dir = ensure_dir(output_dir / "_staging")
    used_names: set[str] = set()
    sequence_reports: list[dict[str, Any]] = []

    for sequence_id, sequence_items in groups.items():
        validation = validate_sequence_images(sequence_items)
        strategy, strategy_reason, numbered_pattern = choose_strategy(sequence_items, validation, args.strategy, args.fps)
        output_name = build_output_name(sequence_id, used_names)
        out_path = output_dir / f"{output_name}.mp4"
        if strategy == "image2":
            assert numbered_pattern is not None
            encode_image2(ffmpeg_exe, args, numbered_pattern, out_path)
        else:
            concat_file = write_concat_file(staging_dir, output_name, sequence_items, args.fps)
            encode_concat(ffmpeg_exe, args, concat_file, out_path)

        sequence_reports.append(
            {
                "sequence_id": sequence_id,
                "output_name": output_name,
                "video_path": str(out_path.resolve()),
                "strategy": strategy,
                "strategy_reason": strategy_reason,
                "frame_count": len(sequence_items),
                "capture_index_range": [sequence_items[0].capture_index, sequence_items[-1].capture_index],
                "frame_range": [sequence_items[0].frame, sequence_items[-1].frame],
                "image_dimensions": [validation.width, validation.height],
                "image_format": validation.image_format,
                "image_mode": validation.image_mode,
                "source_images": [str(item.source_path) for item in sequence_items],
                "numbered_pattern": None if numbered_pattern is None else {
                    "pattern": numbered_pattern.pattern,
                    "start_number": numbered_pattern.start_number,
                    "zero_pad": numbered_pattern.zero_pad,
                },
            }
        )

    for concat_file in staging_dir.glob("*.ffconcat"):
        concat_file.unlink()
    if not any(staging_dir.iterdir()):
        staging_dir.rmdir()

    report = {
        "tool": "screenshot-sequence-video",
        "ffmpeg_exe": str(ffmpeg_exe),
        "fps": args.fps,
        "codec": args.codec,
        "preset": args.preset,
        "pix_fmt": args.pix_fmt,
        "input_summary": input_summary,
        "sequence_count": len(sequence_reports),
        "sequences": sequence_reports,
    }
    write_json(report_path, report)
    print(json.dumps({"report_path": str(report_path.resolve()), "sequence_count": len(sequence_reports)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())