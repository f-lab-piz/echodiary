# 구현 로그

## 2026-02-22 - 구현 워크스페이스 초기화

### 계획 입력
- 플래닝 산출물을 기반으로 구현 워크플로를 초기화함.

### 구현 내용
- 구현 스킬과 프로젝트 로깅 워크스페이스를 추가함.

### 테스트 커버리지
- 해당 없음 (아직 제품 코드를 수정하지 않음).

### 테스트 명령 및 결과
- 명령: `N/A`
- 결과: pass

### 결정 사항
- 향후 모든 구현 세션에서 단위 테스트 필수 규칙을 적용함.
- 구현 범위를 작게 유지하고, 추측성 추상화를 피함.

### 다음 액션
- 첫 플래닝 항목을 선택해 구현하고 단위 테스트를 실행함.

## 2026-02-26 - 데이터 스키마 초안 1차 구현 (#3)

### 계획 입력
- `planning/spec-diary-writing.md`
- GitHub Issue `#3`

### 구현 내용
- SQLAlchemy 모델 추가 (`app/models.py`):
- `personas`
- `diaries`
- `diary_personas`
- `entries`
- 핵심 제약 반영:
- `diary_personas(diary_id, persona_id)` 유니크 제약
- `entries` 입력 필수 체크 제약(`input_keywords` 또는 `input_text`)
- 모델 메타데이터 검증 테스트 추가 (`tests/test_models.py`).

### 테스트 커버리지
- 필수 4개 테이블 존재 여부 검증.
- 다대다 매핑 유니크 제약 존재 검증.
- 엔트리 입력 필수 체크 제약 존재 검증.

### 테스트 명령 및 결과
- 명령: `source .venv/bin/activate && pytest -q`
- 결과: pass (`3 passed`)

### 결정 사항
- DB 스키마 초안은 SQLAlchemy Declarative로 우선 정의해 API 구현과 함께 진화시키기로 함.
- 마이그레이션 툴은 다음 슬라이스에서 도입 여부를 결정함.

### 다음 액션
- 생성/전환/재시도/저장 API 초안 구현(`#4`).
- 스키마를 실제 DB 마이그레이션 규칙으로 연결.

## 2026-02-26 - API/웹 MVP 통합 구현 (#4)

### 계획 입력
- `planning/spec-diary-writing.md`
- `planning/spec-dev-infra.md`
- GitHub Issue `#4`

### 구현 내용
- FastAPI 실행 엔트리 추가 (`app/main.py`).
- SQLite 기반 DB 세션(`app/database.py`) 및 요청 스키마(`app/schemas.py`) 추가.
- MVP API 구현:
- `POST /api/personas`
- `GET /api/personas`
- `POST /api/diaries`
- `POST /api/diaries/{diary_id}/personas/{persona_id}`
- `POST /api/entries/generate`
- `POST /api/entries/{entry_id}/save`
- `GET /api/diaries/{diary_id}/entries`
- 최소 프론트 화면 추가 (`web/index.html`): 생성/저장 플로우 수동 검증 가능.
- 개발 인프라 파일 추가:
- `Dockerfile`
- `infra/docker-compose.yml`
- `infra/prometheus/prometheus.yml`
- `.github/workflows/ci.yml`

### 테스트 커버리지
- `/health` 응답 검증.
- Persona/Diary 생성 -> 연결 -> Entry 생성 -> 저장 흐름 검증.
- 모델 메타데이터/제약 테스트 기존 3건 유지.

### 테스트 명령 및 결과
- 명령: `source .venv/bin/activate && pytest -q`
- 결과: pass (`5 passed`)

### 결정 사항
- 속도 우선으로 SQLite 기반 MVP API를 먼저 구현하고, 이후 Postgres로 전환한다.
- 프론트는 빠른 검증을 위해 단일 HTML/JS 화면으로 시작한다.

### 다음 액션
- 실제 LLM 생성 로직 연결.
- 페르소나 전환 시 draft 처리 정책 API 추가.
- 인증/권한 및 운영자 공급자 설정 API 구현.

## 2026-02-27 - OpenAI 일기 생성 연동 시작

### 계획 입력
- `planning/spec-diary-writing.md`
- `planning/spec-admin-llm-provider.md`

### 구현 내용
- OpenAI 호출 모듈 추가 (`app/llm.py`).
- `/api/entries/generate`에서 LLM 호출하도록 변경.
- `.env` 기반 `OPENAI_API_KEY`, `OPENAI_MODEL` 설정 로딩 추가.
- 키가 없을 때는 기존 로컬 폴백 문구로 동작하도록 처리.

### 테스트 커버리지
- 기존 API 흐름 테스트 5건 유지.

### 테스트 명령 및 결과
- 명령: `source .venv/bin/activate && pytest -q`
- 결과: pass (`5 passed`)

### 결정 사항
- API 키는 `.env`로만 관리하고 Git 커밋 대상에서 제외한다.

### 다음 액션
- 생성 실패 사유 구조화 응답 개선.
- 공급자 다중화(OpenAI/Gemini) 라우팅 계층 추가.
