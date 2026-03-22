#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests


DEFAULT_BASE_URL = "https://api.openai.com"


def compact_error(body):
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            return {
                "message": err.get("message"),
                "type": err.get("type"),
                "param": err.get("param"),
                "code": err.get("code"),
            }
        return body
    return {"message": str(body)}


def trim_text(value, limit=160):
    if not value:
        return ""
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def request_json(method, url, headers, timeout, *, payload=None, params=None):
    started = time.perf_counter()
    response = requests.request(
        method,
        url,
        headers=headers,
        json=payload,
        params=params,
        timeout=timeout,
    )
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    try:
        body = response.json()
    except ValueError:
        body = {"raw_text": trim_text(response.text, 400)}
    return response, body, latency_ms


def secret_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def check_chat(args):
    result = {"check": "chat", "ok": False}
    api_key = os.environ.get(args.secret_key_env)
    if not api_key:
        result["error"] = {
            "message": f"Missing environment variable {args.secret_key_env}"
        }
        return result

    payload = {
        "model": args.chat_model,
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: ok",
            }
        ],
        "max_tokens": 16,
    }
    response, body, latency_ms = request_json(
        "POST",
        f"{args.base_url}/v1/chat/completions",
        secret_headers(api_key),
        args.timeout,
        payload=payload,
    )
    result["status"] = response.status_code
    result["latency_ms"] = latency_ms
    if response.ok:
        choice = ((body.get("choices") or [{}])[0]).get("message") or {}
        result["ok"] = True
        result["model"] = body.get("model", args.chat_model)
        result["reply_preview"] = trim_text(choice.get("content"))
    else:
        result["error"] = compact_error(body)
    return result


def extract_responses_text(body):
    text = body.get("output_text")
    if text:
        return text

    parts = []
    for item in body.get("output", []) or []:
        for block in item.get("content", []) or []:
            if block.get("type") == "output_text":
                parts.append(block.get("text", ""))
    return " ".join(part for part in parts if part)


def check_responses(args):
    result = {"check": "responses", "ok": False}
    api_key = os.environ.get(args.secret_key_env)
    if not api_key:
        result["error"] = {
            "message": f"Missing environment variable {args.secret_key_env}"
        }
        return result

    payload = {
        "model": args.responses_model,
        "input": "Reply with exactly: ok",
        "max_output_tokens": 16,
    }
    response, body, latency_ms = request_json(
        "POST",
        f"{args.base_url}/v1/responses",
        secret_headers(api_key),
        args.timeout,
        payload=payload,
    )
    result["status"] = response.status_code
    result["latency_ms"] = latency_ms
    if response.ok:
        result["ok"] = True
        result["model"] = body.get("model", args.responses_model)
        result["response_id"] = body.get("id")
        result["reply_preview"] = trim_text(extract_responses_text(body))
    else:
        result["error"] = compact_error(body)
    return result


def check_images(args):
    result = {"check": "images", "ok": False}
    api_key = os.environ.get(args.secret_key_env)
    if not api_key:
        result["error"] = {
            "message": f"Missing environment variable {args.secret_key_env}"
        }
        return result

    payload = {
        "model": args.image_model,
        "prompt": "A single small blue square icon on a white background.",
        "size": "1024x1024",
    }
    response, body, latency_ms = request_json(
        "POST",
        f"{args.base_url}/v1/images/generations",
        secret_headers(api_key),
        args.timeout,
        payload=payload,
    )
    result["status"] = response.status_code
    result["latency_ms"] = latency_ms
    if response.ok:
        data = body.get("data") or []
        result["ok"] = True
        result["model"] = args.image_model
        result["items"] = len(data)
        result["has_payload"] = bool(data)
    else:
        result["error"] = compact_error(body)
    return result


def check_admin(args):
    result = {"check": "admin", "ok": False}
    admin_key = os.environ.get(args.admin_key_env)
    if not admin_key:
        result["error"] = {
            "message": f"Missing environment variable {args.admin_key_env}"
        }
        return result

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=args.admin_days)
    params = {
        "start_time": int(start.timestamp()),
        "end_time": int(now.timestamp()),
    }
    response, body, latency_ms = request_json(
        "GET",
        f"{args.base_url}/v1/organization/costs",
        {
            "Authorization": f"Bearer {admin_key}",
        },
        args.timeout,
        params=params,
    )
    result["status"] = response.status_code
    result["latency_ms"] = latency_ms
    if response.ok:
        buckets = body.get("data") or []
        result["ok"] = True
        result["bucket_count"] = len(buckets)
        result["nonempty_bucket_count"] = sum(
            1 for bucket in buckets if bucket.get("results")
        )
    else:
        result["error"] = compact_error(body)
    return result


def parse_checks(raw_checks):
    values = [item.strip().lower() for item in raw_checks.split(",") if item.strip()]
    allowed = {"chat", "responses", "images", "admin"}
    invalid = sorted(set(values) - allowed)
    if invalid:
        raise ValueError(f"Unsupported checks: {', '.join(invalid)}")
    return values or ["chat"]


def main():
    parser = argparse.ArgumentParser(
        description="Probe OpenAI API key and admin key usability."
    )
    parser.add_argument("--checks", default="chat")
    parser.add_argument("--chat-model", default="gpt-4.1-mini")
    parser.add_argument("--responses-model", default="gpt-5-mini")
    parser.add_argument("--image-model", default="gpt-image-1")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--secret-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--admin-key-env", default="OPENAI_ADMIN_API_KEY")
    parser.add_argument("--admin-days", type=int, default=30)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    try:
        checks = parse_checks(args.checks)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    runners = {
        "chat": check_chat,
        "responses": check_responses,
        "images": check_images,
        "admin": check_admin,
    }

    results = [runners[name](args) for name in checks]
    payload = {
        "ok": all(result.get("ok") for result in results),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "checks": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
