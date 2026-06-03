#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

try:
    from hermes_constants import get_hermes_home
except Exception:  # pragma: no cover
    def get_hermes_home() -> Path:
        return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def _read_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        data[key.strip()] = raw_value.strip().strip('"').strip("'")
    return data


def _load_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value

    hermes_home = get_hermes_home()
    candidates = [
        hermes_home / ".env",
        Path.home() / ".hermes" / ".env",
        Path.home() / ".env",
    ]
    for env_path in candidates:
        value = _read_env_file(env_path).get(name, "").strip()
        if value:
            return value
    return ""


def _infer_profile(hermes_home: Path) -> str:
    parts = hermes_home.resolve().parts
    if "profiles" in parts:
        idx = parts.index("profiles")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return os.environ.get("HERMES_PROFILE", "default").strip() or "default"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "page"


def _default_title(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip() or "Hermes page"
        return stripped[:120]
    return "Hermes page"


def _teaser(content: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", content).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _build_source_context(source: str, hermes_home: Path, profile: str) -> dict[str, Any]:
    raw = (source or "").strip()
    if not raw:
        raw = "hermes-chat"

    if raw.startswith("{"):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed

    return {
        "label": raw,
        "tool": "hermes-publish-html",
        "profile_home": str(hermes_home),
        "profile": profile,
    }


def _artifact_paths(hermes_home: Path, title: str) -> tuple[Path, Path, str]:
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%d-%H%M%S")
    slug = _slugify(title)
    artifact_id = f"{stamp}-{slug}"
    base_dir = hermes_home / "workspace" / "publish-html" / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / artifact_id
    input_path = base_dir / "source.md"
    metadata_path = base_dir / "metadata.json"
    return input_path, metadata_path, artifact_id


def _read_input(input_path: str | None) -> str:
    if input_path:
        return Path(input_path).expanduser().read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise SystemExit("No input provided. Pass a file path or pipe markdown on stdin.")
    return sys.stdin.read()


@dataclass
class PublishResult:
    url: str
    artifact_id: str | None
    expires_at: str | None
    stored_input_path: str
    stored_metadata_path: str
    title: str
    profile: str
    teaser: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "artifact_id": self.artifact_id,
            "expires_at": self.expires_at,
            "stored_input_path": self.stored_input_path,
            "stored_metadata_path": self.stored_metadata_path,
            "title": self.title,
            "profile": self.profile,
            "teaser": self.teaser,
        }


def _publish(payload: dict[str, Any], endpoint: str, token: str) -> dict[str, Any]:
    request = urllib_request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Hermes-Token": token,
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Publish gateway HTTP {exc.code}: {body}") from exc
    except urllib_error.URLError as exc:
        raise SystemExit(f"Publish gateway request failed: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Publish gateway returned non-JSON response: {raw[:500]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish markdown to the Hermes publish-gateway and store a local source snapshot.")
    parser.add_argument("input", nargs="?", help="Markdown file to publish. If omitted, stdin is used.")
    parser.add_argument("--title", help="Page title. Defaults to the first heading or first non-empty line.")
    parser.add_argument("--ttl-days", type=int, default=None, help="Override TTL in days.")
    parser.add_argument("--source", default="hermes-chat", help="Source label sent to the publish-gateway.")
    parser.add_argument("--output", choices=["json", "url", "summary"], default="json", help="Output format.")
    parser.add_argument("--endpoint", default="", help="Publish-gateway endpoint. Defaults to HERMES_PUBLISH_GATEWAY_URL.")
    parser.add_argument("--token", default="", help="Publish-gateway token. Defaults to HERMES_PUBLISH_GATEWAY_TOKEN.")
    args = parser.parse_args()

    hermes_home = get_hermes_home()
    profile = _infer_profile(hermes_home)
    content = _read_input(args.input).strip()
    if not content:
        raise SystemExit("Refusing to publish empty content.")

    title = (args.title or _default_title(content)).strip()
    endpoint = (args.endpoint or _load_setting("HERMES_PUBLISH_GATEWAY_URL")).strip()
    token = (args.token or _load_setting("HERMES_PUBLISH_GATEWAY_TOKEN")).strip()
    ttl_days = args.ttl_days if args.ttl_days is not None else int((_load_setting("HERMES_PUBLISH_TTL_DAYS") or "30").strip())

    if not endpoint:
        raise SystemExit("Missing HERMES_PUBLISH_GATEWAY_URL.")
    if not token:
        raise SystemExit("Missing HERMES_PUBLISH_GATEWAY_TOKEN.")

    input_path, metadata_path, local_artifact_id = _artifact_paths(hermes_home, title)
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(content + "\n", encoding="utf-8")

    payload = {
        "profile": profile,
        "title": title,
        "content": content,
        "content_format": "markdown",
        "ttl_days": ttl_days,
        "source": _build_source_context(args.source, hermes_home=hermes_home, profile=profile),
    }
    response_body = _publish(payload, endpoint=endpoint, token=token)
    url = str(response_body.get("url") or "").strip()
    if not url:
        raise SystemExit(f"Publish gateway response missing url: {json.dumps(response_body, ensure_ascii=False)}")

    metadata = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "title": title,
        "request": payload,
        "response": response_body,
        "local_artifact_id": local_artifact_id,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = PublishResult(
        url=url,
        artifact_id=response_body.get("artifact_id") or local_artifact_id,
        expires_at=response_body.get("expires_at"),
        stored_input_path=str(input_path),
        stored_metadata_path=str(metadata_path),
        title=title,
        profile=profile,
        teaser=_teaser(content),
    )

    if args.output == "url":
        print(result.url)
    elif args.output == "summary":
        print(f"Published '{result.title}' for profile '{result.profile}': {result.url}")
    else:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
