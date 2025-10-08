# acen API

acen 프로젝트의 애플리케이션 API를 제공하기 위한 Python 기반 서비스입니다. 초기 스케줄 템플릿, 모델 detection/classification, DB API를 제공합니다.

## 주요 목표
- 여드름 관련 피드백과 스케줄링 기능을 통합 제공하는 서비스입니다.
- 모델 inference 결과와 사용자 데이터를 연계하여 맞춤형 피드백을 도출합니다.

## 디렉터리 구조
- `src/`: 서비스 로직, DB, 모델 연동 등 핵심 코드가 위치합니다.

## 구성 요소
- **서버**: REST API 제공.
- **데이터베이스**: 프로젝트 디렉터리 내에 생성되는 경량 SQL DB 사용.
- **모델 래퍼**: detection/classification 결과를 반환하는 wrapper 클래스 (`yolov11l` 기본값).

### 도메인 스키마 및 클래스
| 분류 | 설명 |
| --- | --- |
| `Template` | 템플릿 정의. 하위에 `Schedule` 포함 |
| `Schedule` | 단일 일정(예: 세안)과 부가 정보를 표현 |
| `Model` | detection/classification 래퍼 |
| `Calendar` | 날짜별 수행 로그 관리, 하위에 `Date` 포함 |
| `Date` | 일정 수행 정보, 템플릿 진행률, 촬영 데이터 등 |
| `Evaluator` | `Date`/`Calendar` 데이터를 통계 및 지표로 변환 |
| `Feedback` | `Evaluator` 결과를 바탕으로 피드백 생성 |
| `Suggest` | `Feedback` 정보를 기반으로 제품(이름/태그/설명) 추천 |
| `Research` | DB 미흡 시 진행하는 심화 분석. 선택 구현 항목 |

## 개발 메모
- 필요에 따라 추가 스키마를 정의할 예정입니다.
- 각 컴포넌트 구현은 `src/` 디렉터리 하위에서 진행합니다.

## 빠른 시작
```bash
# (선택) 가상환경 활성화 후 패키지 설치
pip install -r requirements.txt

# uvicorn으로 로컬 실행
uvicorn acen_api.main:app --reload

# 테스트 실행
pytest
```

## API 호출 예시

모든 예시는 기본 URL을 `http://localhost:8000`으로 가정합니다.

- **헬스 체크**
  ```bash
  curl http://localhost:8000/health
  ```

- **템플릿 목록 조회**
  ```bash
  curl http://localhost:8000/templates
  ```

- **템플릿 생성**
  ```bash
  curl -X POST http://localhost:8000/templates \
    -H "Content-Type: application/json" \
    -d '{
      "name": "아침 루틴",
      "description": "기본 피부 관리",
      "schedules": [
        {"title": "세안", "order_index": 0},
        {"title": "보습", "order_index": 1}
      ]
    }'
  ```

- **일자 로그 생성**
  ```bash
  curl -X POST http://localhost:8000/dates \
    -H "Content-Type: application/json" \
    -d '{
      "calendar_id": 1,
      "scheduled_date": "2024-01-01",
      "schedule_done": 1,
      "schedule_total": 2
    }'
  ```

- **평가 지표 조회**
  ```bash
  curl "http://localhost:8000/evaluate?calendar_id=1&start=2024-01-01&end=2024-01-07"
  ```

- **피드백 생성 및 추천 조회**
  ```bash
  curl -H "X-User-Id: 1" -X POST "http://localhost:8000/feedback/generate?calendar_id=1&start=2024-01-01&end=2024-01-07"
  curl "http://localhost:8000/feedback/suggest?feedback_id=1"
  ```

- **모델 탐지/분류 호출 (이미지 경로 사용)**
  ```bash
  curl -X POST http://localhost:8000/model/detect \
    -H "Content-Type: application/json" \
    -d '{"image_path": "data/uploads/sample.jpg"}'

  curl -X POST http://localhost:8000/model/classify \
    -H "Content-Type: application/json" \
    -d '{"image_path": "data/uploads/sample.jpg", "top_k": 3}'
  ```

## Users UI 및 입력 도구
- 브라우저에서 `http://localhost:8000/ui` 접속
  - 상단에서 `API Key`와 `User ID`를 입력
  - 사용자 생성 폼으로 새로운 사용자 생성 시 `User ID` 자동 설정
  - 해당 사용자로 템플릿/캘린더/일자 데이터를 입력
- 스크립트로 데이터 삽입
  ```bash
  API_KEY=your_key BASE_URL=http://localhost:8000 python scripts/seed.py
  # 혹은 cURL 버전
  API_KEY=your_key BASE_URL=http://localhost:8000 ./scripts/seed.sh
  ```

## API Key 발급 및 관리
- API를 통해 키 발급/회수 수행 (`/api-keys`)
  ```bash
  # 최초 키 발급 (키가 하나도 없을 때는 인증 없이 발급 가능)
  curl -X POST http://localhost:8000/api-keys -H "Content-Type: application/json" -d '{"description":"admin"}'

  # 키가 존재한 이후 발급/목록/회수는 X-API-Key 헤더 필요
  curl -X GET http://localhost:8000/api-keys -H "X-API-Key: <발급받은키>"
  curl -X DELETE http://localhost:8000/api-keys/1 -H "X-API-Key: <발급받은키>"
  ```
- `scripts/generate_api_key.py`로 API 호출 기반 발급 가능
  ```bash
  python scripts/generate_api_key.py --base-url http://localhost:8000 --admin-key <기존키>
  ```
