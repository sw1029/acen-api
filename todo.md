acen API 구현 TODO

목표: README의 목적/구성에 따라 서버, DB, 모델 래퍼, 평가/피드백/추천을 포함한 API를 단계적으로 구현한다. 각 항목은 선행 요구사항을 먼저 완료한 뒤 진행한다.

공통 원칙
- [ ] Python 3.11 이상 고정, 코드 포맷/린트 일관성 유지
- [ ] 단순성을 우선: SQLite, 최소 의존성, 작은 모듈 단위
- [ ] 에러 처리/로깅/유효성 검증을 모든 계층에 포함
- [x] src 기반 패키지 구조 사용 (`src/acen_api`)

0. 선행 요구사항 / 환경 세팅
- [x] Python 버전 고정 및 가상환경 생성 (venv/uv/poetry 중 택1) — 현재 anaconda `acen` 환경(3.11) 사용, `.python-version` 추가
- [x] 패키지 관리 도구 결정 및 초기화 — `requirements.txt` 작성(설치 대기)
  - [x] FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-multipart, Pillow, numpy
  - [x] (모델) torch, ultralytics(가용 시), torchvision 또는 timm (분류 대안) — torch/vision/audio 기본 설치 확인, ultralytics 추후 검토
  - [x] 테스트: pytest, httpx[testclient]
  - [x] 개발 편의: pydantic-settings, python-dotenv, loguru 또는 표준 logging
- [x] `.env.example` 작성 (DB 경로, 모델 경로, 로그 레벨 등)
- [x] 기본 디렉터리 준비: `data/`, `data/uploads/`, `data/models/`
완료 기준: 가상환경에서 `uvicorn --help` 실행 가능, `python -c "import fastapi, sqlalchemy"` 성공

1. 프로젝트 골격 생성
- [x] 패키지 스켈레톤 생성
  - [x] `src/acen_api/__init__.py`
  - [x] `src/acen_api/main.py` (FastAPI 앱 팩토리)
  - [x] `src/acen_api/config.py` (환경설정 로딩)
  - [x] `src/acen_api/core/` (db, logging, deps, errors)
  - [x] `src/acen_api/api/routers/` (엔드포인트 모듈)
  - [x] `src/acen_api/models/` (ORM 도메인 모델)
  - [x] `src/acen_api/schemas/` (Pydantic 스키마)
  - [x] `src/acen_api/repositories/`
  - [x] `src/acen_api/services/`
- [x] 기본 앱 실행 진입점 추가: `uvicorn acen_api.main:app --reload`
완료 기준: `/health` 라우트로 200 응답 반환(더미)

2. 데이터베이스 계층 (SQLite)
선행: 1 완료
- [x] DB 파일 경로: `data/acen.db` 구성
- [x] `core/db.py`
  - [x] SQLAlchemy Engine/SessionLocal 생성, `get_db()` 의존성
  - [x] 초기 테이블 생성 유틸 (create_all) 제공 (`init_db()` 추가)
- [x] ORM 모델 정의 (`models/`)
  - [x] Template, Schedule (Template-1:N-Schedule)
  - [x] Calendar, Date (Calendar-1:N-Date)
  - [x] ModelResult (감지/분류 결과 요약, 이미지 경로 참조)
  - [x] Feedback (텍스트/카테고리/지표)
  - [x] Product (추천 대상, 이름/태그/설명)
  - [x] Suggest (추천 이력: Product 참조, 근거 태그/스코어)
- [x] 초기 스키마 생성 스크립트(간단 create_all) 또는 SQL 초기화 스크립트 작성
완료 기준: 애플리케이션 기동 시 최초 1회 테이블 자동 생성

3. 스키마 (Pydantic)
선행: 2 일부(도메인 필드 확정)
- [ ] 요청/응답 DTO 스키마 분리 (Create/Update/Read)
  - [x] Template{Create,Update,Read}
  - [x] Schedule{Create,Update,Read}
  - [x] Date{Create,Read} (일정 수행 로그, 이미지 메타)
  - [x] Model{DetectRequest, DetectResponse, ClassifyRequest, ClassifyResponse}
  - [x] Evaluator{Metrics}
  - [x] Feedback{Read}
  - [x] Suggest{Read}
- [x] 공통 에러 응답 스키마 정의 (후속 단계)
완료 기준: OpenAPI 스키마에서 모델 간 참조가 올바르게 생성됨

4. 리포지토리 계층 (CRUD)
선행: 2 완료
- [x] TemplateRepository: CRUD, 템플릿-스케줄 함께 로딩
- [x] ScheduleRepository: CRUD
- [x] DateRepository: 생성(수행여부, 메모, 이미지 경로), 조회(기간별)
- [x] ProductRepository: 태그 기반 조회/검색
- [x] FeedbackRepository, SuggestRepository: 생성/조회
완료 기준: 각 리포지토리 단위 테스트(인메모리 SQLite) 통과 — `tests/test_repositories.py`

5. 스토리지/업로드 서비스
선행: 1, 2 완료
 - [ ] `services/storage.py` 이미지 저장/검증(확장자/크기), 경로 생성
 - [ ] 파일명 충돌 방지(UUID), EXIF 회전 보정(optional)
- [x] `services/storage.py` 이미지 저장/검증(확장자/크기), 경로 생성
- [x] 파일명 충돌 방지(UUID), EXIF 회전 보정(optional)
완료 기준: 업로드 후 파일 시스템에 안전 저장, DB에 경로 기록

6. 모델 래퍼 계층
선행: 0(모델 의존성), 1 완료
- [x] 공통 인터페이스 정의: `ModelWrapper`
  - [x] `load(device: str|None) -> None`
  - [x] `detect(image) -> list[Box]` (x,y,w,h,score,label)
  - [x] `classify(image) -> list[LabelScore]`
- [x] 기본 구현
  - [x] `detector_ultralytics.py`: YOLO 가능 시 사용, 불가 시 우회(모의)
  - [x] `classifier_stub.py`: 초기엔 더미/간단 분류(라벨/스코어 고정 규칙)
- [ ] 전처리/후처리 유틸: 리사이즈, 정규화, NMS(필요 시) — Ultralytics post-process는 모델 결과 사용, 별도 유틸은 추후 정의
- [x] 디바이스 선택 로직(CUDA/CPU)
완료 기준: 더미 모델로도 API가 일관된 응답 형식 제공

7. 평가(Evaluator) 설계/구현
선행: 4, 6 일부
- [x] 입력: Date 레코드들, ModelResult(감지 수/분류 점수), 스케줄 수행여부
- [x] 지표 정의/구현
  - [x] 일정 수행률: 완료 수/예정 수
  - [x] 7일 이동 평균 수행률
  - [x] 피부 상태 변화: 감지 박스 수 변화율, 분류 심각도 평균/추세
  - [x] 정상화/스코어링 유틸 (0~1)
- [x] 출력: `EvaluatorMetrics`(adherence, trend, severity, notes)
완료 기준: 고정 입력에 대해 결정론적 지표 산출 단위 테스트 통과

8. 피드백/추천 서비스
선행: 7 완료, 4 일부(Product)
- [x] 규칙 기반 피드백
  - [x] 수행률 < 0.6: 루틴 개선 권고
  - [x] 악화 추세: 제품/루틴 점검 권고, 자극 단축 제안
  - [x] 개선 추세: 유지/점진적 변경 권고
- [x] 태그 생성 로직 (예: 진정, 보습, 각질케어)
- [x] 추천: Product 태그 매칭 상위 N, 점수 산정
- [x] 결과 영속화(Feedback, Suggest)
완료 기준: 동일 입력→동일 피드백/추천 세트 반환, 저장 확인

9. API 라우터 구현 (FastAPI)
선행: 3~8 단계별 종속
- [x] `/health` GET
- [x] 템플릿/스케줄 CRUD
  - [x] `POST /templates`, `GET /templates`, `GET /templates/{id}`
  - [x] `POST /templates/{id}/schedules`, `PATCH/DELETE`
- [x] 일정/수행 로그(Date)
  - [x] `POST /dates` (스케줄 수행 기록 + 이미지 업로드 경로)
  - [x] `GET /dates?from=&to=`
- [x] 모델 연동
  - [x] `POST /model/detect` (이미지 업로드/경로 입력 지원)
  - [x] `POST /model/classify`
- [x] 평가/피드백/추천
  - [x] `GET /evaluate?range=7d|30d`
  - [x] `POST /feedback` (평가 입력→피드백 생성/저장)
  - [x] `GET /suggest?top=3`
- [x] 공통 예외 처리, 응답 표준화, OpenAPI 태그/예시 추가
완료 기준: 로컬에서 주요 경로 200/4xx 정상, OpenAPI 문서 확인

10. 보안/검증/한도
선행: 9 일부
- [x] 업로드 파일 크기/확장자 제한, 이미지 MIME 검사 — `/uploads` (multipart), `ImageStorageService` 기반
- [ ] 요청 스키마 유효성, 경계값 검사
 - [x] 간단 API 키 또는 토큰 훅(미니멈) — `X-API-Key` 헤더, `API_KEY` 환경변수
완료 기준: 비정상 입력에 대해 4xx + 명확한 에러 메시지

11. 테스트
선행: 각 모듈별 병행
- [ ] 유닛: repositories, evaluator, feedback/suggest, storage
- [ ] API: TestClient로 happy-path/에러-path
- [ ] 회귀: 고정 입력→고정 출력 스냅샷
완료 기준: CI 등에서 테스트 전부 통과 (임시 로컬 스크립트 가능)

12. 운영/개발자 경험(선택)
- [ ] 로깅 포맷/레벨 설정, 요청/응답 요약 로그
- [ ] Dockerfile, compose(선택), 실행 스크립트
- [ ] 린트/포맷(pre-commit, ruff/black), 타입체크(mypy 선택)
완료 기준: `make run`, `make test` 등 빠른 워크플로우

13. DB 입력 UI/스크립트 (웹 UI + 시드 스크립트)
선행: 9(API 라우터), 4(리포지토리)
- [x] UI 아키텍처/정적 자원 서빙
  - [x] 디렉터리 생성: `src/acen_api/ui/` (예: `index.html`, `assets/main.js`, `assets/styles.css`)
  - [x] FastAPI `StaticFiles`로 `/ui` 라우트에 정적 자원 서빙
  - [x] (선택) `UI_ENABLED` 환경변수로 노출 여부 제어 (`.env.example` 반영)
- [x] 폼 구성(체크리스트/문자열/숫자 입력)
  - [x] Template 폼: `name`(text), `description`(text), `theme`(text)
  - [x] Schedule 반복 입력: `title`(text), `order_index`(number), `tags`(text), `extra_info`(text)
  - [x] 제출 시 `/templates`로 POST
  - [ ] Schedule 단독 폼: `template_id`(number) 지정 후 `/templates/{id}/schedules` POST
  - [x] 기타 DB 폼
    - [x] Product: `name`(text), `brand`(text), `tags`(text), `description`(text)
    - [x] Calendar: `name`(text)
    - [x] Date: `calendar_id`(number), `scheduled_date`(date), `schedule_done`(number), `schedule_total`(number), `notes`(text), `image_path`(text)
- [x] API 확장(UI 연동용 간단 CRUD)
  - [x] `POST /products`, `GET /products` (ProductRepository 연동)
  - [x] `POST /calendars`, `GET /calendars` (CalendarRepository 연동)
- [ ] 클라이언트 유효성/오류 처리
  - [ ] 필수값/숫자 범위(>=0) 검증 메시지 보강
  - [x] API 실패 시 `ErrorResponse` 매핑하여 알림 영역 표시(필드별 메시지)
- [x] 시드 스크립트/데이터
  - [x] `scripts/seed.py` 작성(환경변수 `BASE_URL` 사용, httpx로 API 호출)
  - [x] `scripts/seed.sh` 작성(cURL 기반 대안)
- [x] 테스트
  - [x] `/ui` GET 200 스모크 테스트 추가
  - [x] Product/Calendar 엔드포인트 최소 테스트 추가
- 완료 기준: 브라우저에서 `/ui` 접속하여 템플릿/스케줄/제품/캘린더/일자 레코드를 생성할 수 있고, `scripts/seed.py`로 동일 데이터가 삽입됨

14. 사용자(User) 도입 및 사용자 단위 캘린더/일자 관리
선행: 2(모델), 4(레포지토리), 9(API)
- [x] 도메인 모델 확장
  - [x] `User` 엔티티 추가 (`users` 테이블: id, external_id/username, display_name, email, created_at 등)
  - [x] `Calendar`에 `user_id` FK 추가, `relationship` 설정
  - [x] `Date`에 `user_id` 컬럼 추가하여 조회 최적화
- [x] 스키마/레포지토리 업데이트
  - [x] `CalendarCreate/Read`에 `user_id` 필드 포함
  - [x] `DateRead`에 `user_id` 노출
  - [x] `CalendarRepository` 생성/목록/조회 시 `user_id` 필터 지원
  - [x] `DateRepository.list_by_range`에 `user_id` 필터 적용
- [x] 서비스/의존성
  - [x] `deps.get_current_user` 의존성 추가 (`X-User-Id` 헤더)
  - [x] Evaluator/Feedback 서비스에서 사용자 검증
- [x] API 라우터 수정
  - [x] `/users` CRUD 라우터 추가 (생성/삭제 포함)
  - [x] `/calendars`, `/dates`, `/feedback/generate`, `/evaluate` 등 사용자 필터/검증 반영
  - [ ] 사용자 삭제 시 연관 캘린더/일자/피드백 cascade 확인 (사이드이팩트 테스트 필요)
- [ ] UI/스크립트 변경
  - [x] `/ui` 폼에 `user_id` 입력 추가, 사용자 생성 폼 제공
  - [ ] 사용자 삭제 UI 제공 (옵션)
  - [x] 시드 스크립트에 사용자 생성 → 해당 사용자 기준 데이터 삽입
- [x] 테스트
  - [x] 사용자별 접근 제한 테스트 (타 사용자 캘린더 접근 시 404/403)
  - [x] `/users` CRUD 및 `/ui` 사용자 선택 스모크 테스트
- 완료 기준: 사용자 단위로 캘린더/일자/피드백이 분리 관리되며 사용자 생성/삭제/데이터 입력이 UI와 API에서 가능

15. API Key DB 관리 및 발급/회수 시스템
선행: 14(User 구조), 9(API)
- [x] DB 스키마/모델
  - [x] `api_keys` 테이블 추가 (`id`, `key`, `description`, `created_at`, `revoked_at` 등)
  - [x] ORM 모델/스키마(`ApiKeyCreate`, `ApiKeyRead`) 정의
- [x] 리포지토리/서비스
  - [x] `ApiKeyRepository` (생성/목록/회수/검증)
  - [x] `deps.require_api_key`가 DB 조회 기반으로 전환
  - [ ] 유효 키 캐시 전략(선택) 또는 ORM 조회 최적화
- [x] API 라우터
  - [x] `POST /api-keys`
  - [x] `GET /api-keys`
  - [x] `DELETE /api-keys/{id}` (회수)
  - [x] 인증 정책: 최초 한 건은 무인증 허용, 이후 키 필요
- [x] UI/스크립트 연동
  - [x] `/ui`에 API Key 관리 섹션 추가 (발급→키 표시, 목록/회수 기능)
  - [x] `generate_api_key.py`를 API 호출 기반으로 변경
- [x] 기존 보호 로직 교체
  - [x] `X-API-Key` 헤더 검증이 DB 키 기반으로 동작
  - [x] 키 폐기 후 API 호출 재인증 확인 (테스트 포함)
- [x] 테스트
  - [x] 키 발급/회수/목록 API 단위 테스트
  - [x] 보호된 엔드포인트에서 허용/차단 시나리오 검증
  - [x] UI 스모크 테스트 (발급→회수)
- 완료 기준: API 호출만으로 키 발급/회수가 가능하고, 모든 보호 엔드포인트가 DB 기반 키 검증을 사용

부록: 구현 세부 제안(파일/심화)
- 앱 팩토리: `create_app()`에서 라우터 등록, 미들웨어(CORS, GZip)
- 의존성: `get_db`, `get_storage`, `get_model`
- 에러: 도메인 오류→HTTPException 매핑 계층 `core/errors.py`
- 모델 경량화: 초기는 더미/간소화된 모델로 일단 API 일관성 확보 → 이후 교체
- 데이터 경로: 상대경로 안전화, 경로 순회 차단
- 성능: 잦은 모델 호출 시 싱글톤 로딩/캐시

메모: YOLOv11l 가용성 확인
- [ ] `ultralytics` 최신 버전에서 v11 지원 여부 확인
- [ ] 미지원 시 YOLOv8로 대체, 인터페이스 동일 유지
- [ ] 분류는 timm/torchvision 사전학습 모델 + 간단 규칙/미세튜닝 설계(후순위)
