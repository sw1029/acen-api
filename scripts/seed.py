#!/usr/bin/env python3
"""
acen API 시드 스크립트

환경 변수
- BASE_URL: 기본 http 주소 (기본값: http://localhost:8000)

사용 예시
    python scripts/seed.py
"""

from __future__ import annotations

import json
import os
from datetime import date

import httpx


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY")

USER_ID: int | None = None


def post_json(client: httpx.Client, path: str, payload: dict, *, headers: dict | None = None) -> dict:
    r = client.post(f"{BASE_URL}{path}", json=payload, timeout=10, headers=headers)
    try:
        data = r.json()
    except Exception:
        data = {"text": r.text}
    if r.status_code >= 400:
        raise RuntimeError(f"{path} failed: {r.status_code} {json.dumps(data, ensure_ascii=False)}")
    return data


def auth_headers(require_user: bool = True) -> dict:
    headers: dict[str, str] = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    if require_user:
        if USER_ID is None:
            raise RuntimeError("USER_ID not initialised")
        headers["X-User-Id"] = str(USER_ID)
    return headers


def seed_user(client: httpx.Client) -> int:
    payload = {"username": "seed-user", "display_name": "Seed User"}
    headers = auth_headers(require_user=False)
    user = post_json(client, "/users", payload, headers=headers)
    return user["id"]


def seed_products(client: httpx.Client) -> list[int]:
    ids: list[int] = []
    for payload in [
        {"name": "진정 토너", "tags": "진정", "description": "민감 피부용"},
        {"name": "보습 크림", "tags": "보습", "description": "수분 보충"},
    ]:
        res = post_json(client, "/products", payload, headers=auth_headers(require_user=False))
        ids.append(res["id"])
    return ids


def seed_calendar_and_dates(client: httpx.Client) -> int:
    cal = post_json(
        client,
        "/calendars",
        {"name": "기본 캘린더", "description": "seed"},
        headers=auth_headers(),
    )
    cal_id = cal["id"]
    # 2일치 일자 생성
    d1 = post_json(
        client,
        "/dates",
        {
            "calendar_id": cal_id,
            "scheduled_date": date(2024, 1, 1).isoformat(),
            "schedule_done": 1,
            "schedule_total": 2,
        },
        headers=auth_headers(),
    )
    d2 = post_json(
        client,
        "/dates",
        {
            "calendar_id": cal_id,
            "scheduled_date": date(2024, 1, 2).isoformat(),
            "schedule_done": 2,
            "schedule_total": 2,
        },
        headers=auth_headers(),
    )
    return cal_id


def seed_template(client: httpx.Client) -> int:
    payload = {
        "name": "아침 루틴",
        "description": "기본 관리",
        "schedules": [
            {"title": "세안", "order_index": 0},
            {"title": "보습", "order_index": 1, "tags": "보습"},
        ],
    }
    tpl = post_json(client, "/templates", payload, headers=auth_headers(require_user=False))
    return tpl["id"]


def main() -> None:
    with httpx.Client() as client:
        print(f"Seeding to {BASE_URL}")
        if API_KEY:
            print("- using API key")
        global USER_ID
        USER_ID = seed_user(client)
        print(f"- user: {USER_ID}")
        prod_ids = seed_products(client)
        print(f"- products: {prod_ids}")
        cal_id = seed_calendar_and_dates(client)
        print(f"- calendar: {cal_id}")
        tpl_id = seed_template(client)
        print(f"- template: {tpl_id}")
        print("Done.")


if __name__ == "__main__":
    main()
