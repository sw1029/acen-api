#!/usr/bin/env bash
# 간단 cURL 기반 시드 스크립트
# BASE_URL 기본값: http://localhost:8000

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_KEY_HEADER=()
if [[ -n "${API_KEY:-}" ]]; then
  API_KEY_HEADER=(-H "X-API-Key: ${API_KEY}")
fi

echo "Seeding to ${BASE_URL}"

USER_ID=$(curl -sS -X POST "${BASE_URL}/users" \
  "${API_KEY_HEADER[@]}" \
  -H 'Content-Type: application/json' \
  -d '{"username":"seed-user","display_name":"Seed User"}' | jq -r '.id')

echo "- user: ${USER_ID}"

COMMON_HEADERS=(-H "Content-Type: application/json" -H "X-User-Id: ${USER_ID}")
if [[ -n "${API_KEY:-}" ]]; then
  COMMON_HEADERS+=(-H "X-API-Key: ${API_KEY}")
fi

curl -sS -X POST "${BASE_URL}/products" \
  "${COMMON_HEADERS[@]}" \
  -d '{"name":"진정 토너","tags":"진정","description":"민감 피부용"}' | jq -r '.id'

curl -sS -X POST "${BASE_URL}/products" \
  "${COMMON_HEADERS[@]}" \
  -d '{"name":"보습 크림","tags":"보습","description":"수분 보충"}' | jq -r '.id'

CAL_ID=$(curl -sS -X POST "${BASE_URL}/calendars" \
  "${COMMON_HEADERS[@]}" \
  -d '{"name":"기본 캘린더","description":"seed"}' | jq -r '.id')

curl -sS -X POST "${BASE_URL}/dates" \
  "${COMMON_HEADERS[@]}" \
  -d "{\"calendar_id\":${CAL_ID},\"scheduled_date\":\"2024-01-01\",\"schedule_done\":1,\"schedule_total\":2}" | jq -r '.id'

curl -sS -X POST "${BASE_URL}/dates" \
  "${COMMON_HEADERS[@]}" \
  -d "{\"calendar_id\":${CAL_ID},\"scheduled_date\":\"2024-01-02\",\"schedule_done\":2,\"schedule_total\":2}" | jq -r '.id'

curl -sS -X POST "${BASE_URL}/templates" \
  "${COMMON_HEADERS[@]}" \
  -d '{"name":"아침 루틴","description":"기본 관리","schedules":[{"title":"세안","order_index":0},{"title":"보습","order_index":1,"tags":"보습"}]}' | jq -r '.id'

echo "Done."
