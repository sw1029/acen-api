#!/usr/bin/env python3
"""API를 통해 단일 API Key를 발급하는 스크립트."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="API를 통해 단일 API Key 발급")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API 기본 URL")
    parser.add_argument("--admin-key", help="이미 존재하는 API Key (생성된 키가 있을 경우 필요)")
    parser.add_argument("--description", help="새 키 설명", default=None)
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="발급한 키를 현재 디렉터리의 .env 파일에 기록",
    )
    args = parser.parse_args()

    headers = {"Content-Type": "application/json"}
    if args.admin_key:
        headers["X-API-Key"] = args.admin_key

    payload = {"description": args.description}

    with httpx.Client() as client:
        res = client.post(
            f"{args.base_url}/api-keys",
            headers=headers,
            json=payload,
            timeout=10,
        )
        try:
            data = res.json()
        except json.JSONDecodeError:
            data = {"text": res.text}
        if res.status_code != 201:
            raise SystemExit(f"발급 실패 ({res.status_code}): {data}")

    key = data.get("key")
    if not key:
        raise SystemExit("응답에 key 값이 없습니다.")

    print(key)

    if args.write_env:
        env_path = Path(".env")
        lines: list[str] = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
        lines = [line for line in lines if not line.startswith("API_KEY=")]
        lines.append(f"API_KEY={key}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f".env 파일에 API_KEY를 갱신했습니다: {env_path.resolve()}")


if __name__ == "__main__":
    main()
