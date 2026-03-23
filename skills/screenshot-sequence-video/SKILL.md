---
name: screenshot-sequence-video
description: Convert screenshot or image sequences into deterministic MP4 review clips. Use when Codex needs to merge screenshots or still-image frames into video from a folder, glob, numbered pattern, or JSON manifest, especially for sparse frame-step captures, per-sequence review clips, or sidecar report generation.
---

# Screenshot Sequence Video

Use this skill to turn screenshot or image sequences into reviewable MP4 clips without rewriting ffmpeg glue each time.

## Quick decision

- Use `scripts/sequence_to_video.py --manifest ...` when the input already has a JSON manifest with `image_path` and optional grouping fields such as `sequence_id` or `attempt_label`.
- Use `scripts/sequence_to_video.py --input-dir ... --glob ...` when the input is a single folder of screenshots.
- Keep outputs outside the repository unless the user explicitly asks for repo-owned video artifacts.

## Workflow

1. Choose an external output directory.
2. Prefer `--strategy auto`.
3. Let the script choose:
   - `image2` when files form one contiguous numbered sequence with matching shape/format.
   - `concat` when the input is sparse, manifest-driven, mixed-path, or otherwise not a clean numbered sequence.
4. Read the generated `video_report.json` to confirm which strategy was used for each output clip.

## Why this skill exists

This workflow is based on FFmpeg's standard image-sequence mechanisms, but optimized for our review flow:

- group outputs by `sequence_id` instead of flattening everything into one video
- accept sparse frame-step capture manifests directly
- sort deterministically by `capture_index`, `frame`, then path instead of fragile lexical filename order
- fail fast on missing files or mixed image dimensions
- write a sidecar JSON report so downstream review tooling can trace every clip back to its source images
- default to `60 fps`, `libx264`, `+faststart`, and `stillimage` tuning for quick human review

## Commands

### Manifest-driven review clips

```bash
python scripts/sequence_to_video.py \
  --manifest ./captures/capture_manifest.json \
  --output-dir ./captures/videos
```

### Single folder to one clip

```bash
python scripts/sequence_to_video.py \
  --input-dir ./captures/gap-closeup \
  --glob "screen_capture_*.bmp" \
  --sequence-id gap-closeup \
  --output-dir ./captures/videos
```

## Output contract

The script writes:

- one MP4 per sequence
- `video_report.json` with sequence metadata, ffmpeg strategy, and source image references

## Validation rules

- Require at least one image.
- Require all source files to exist.
- Require identical image dimensions within each output sequence.
- Reject `image2` when filenames are not one contiguous numbered pattern.
- Do not silently skip bad inputs or guess around missing frames.

## Resources

- Script: [scripts/sequence_to_video.py](scripts/sequence_to_video.py)
- Learning log: [references/learning-log.md](references/learning-log.md)
