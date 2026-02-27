# AGENTS.md

## 프로젝트 개요
- 프로젝트명: EchoDiary
- 목적: 키워드/자연어 입력을 기반으로 AI 일기 초안을 생성하고 저장하는 서비스

## 현재 스택
- Frontend: React (Vite), Nginx
- Backend: FastAPI, SQLAlchemy
- DB: PostgreSQL
- AI: OpenAI API, LangChain, LangGraph
- Infra: Docker Compose, Prometheus, Grafana

## 실행 명령
- 전체 실행: `docker compose up -d --build`
- 전체 종료: `docker compose down`
- 백엔드 테스트: `source .venv/bin/activate && pytest -q`

## 환경 변수
- `.env` 파일 사용
- 필수 키:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (기본: `gpt-4.1-mini`)

## 코드 작업 원칙
- 백엔드/프론트 모두 MVP 기능 우선 구현
- API 변경 시 `tests/` 테스트 갱신
- 비밀키/민감정보는 절대 Git 커밋 금지
- 문서보다 동작 코드와 테스트를 우선 유지
- PR을 생성하는 변경은 `README.md`에 변경 요약(무엇이 바뀌었는지)도 함께 기록
- PR 생성 전 `Playwright MCP`로 클라이언트를 직접 실행해 메인 화면과 주요 동작 단계별 화면을 검증
- PR 본문에 단계별 스크린샷(메인 화면, 핵심 액션 전/후)을 첨부하고 각 스크린샷의 동작 설명을 함께 작성

## 주요 경로
- Backend: `app/`
- Frontend: `web/`
- Infra: `docker-compose.yml`, `infra/prometheus/`
- Planning: `planning/`
- Implementation log: `implementation/`
