# EchoDiary

## 프로젝트 개요
EchoDiary는 짧은 키워드/메모 입력만으로 일기 초안을 빠르게 생성하는 AI 다이어리 서비스입니다.

## 프로젝트 목표
- 일기 작성 진입 장벽을 낮춰 기록 지속성을 높인다.
- 페르소나(톤) 기반으로 일관된 문체의 초안을 생성한다.
- MVP 단계에서 생성-수정-저장의 핵심 플로우를 빠르게 검증한다.

## 기술 스택
- Frontend: React, Vite, Nginx
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- AI/Agent: OpenAI API, LangChain, LangGraph
- Infra: Docker, Docker Compose, Prometheus, Grafana
- CI: GitHub Actions

## 실행 방법
1. `.env` 파일에 `OPENAI_API_KEY`를 설정합니다.
2. 아래 명령으로 실행합니다.

```bash
docker compose up -d --build

## 개발 모드 (Hot Reload)
- 개발 중에는 `docker-compose.dev.yml`을 사용하면 `--build` 없이 코드 변경이 반영됩니다.
- 백엔드: `uvicorn --reload`로 자동 재시작
- 프론트엔드: Vite dev server로 즉시 반영(HMR)

```bash
docker compose -f docker-compose.dev.yml up -d
```

```bash
docker compose -f docker-compose.dev.yml down
```
```

## 최근 변경
- `docker-compose.yml`의 `api` 서비스에 `.env` 주입(`env_file`)을 추가해 컨테이너에서도 OpenAI 키/모델을 사용하도록 수정했습니다.
- `implementation/playwright-checks/0101-current-status/`에 Playwright 기반 단계별 동작 점검 기록(스크린샷 4장 + 설명 문서)을 추가했습니다.
- 인증 화면을 `/login`, `/signup`으로 분리하고, 메인(`/`)에서는 `오늘 하루는 어떠신가요` 기반 입력→생성→저장 동선으로 UI를 재구성했습니다.
- `/diaries` 보관함 페이지를 추가해 저장된 일기 목록(작성일/본문)을 확인할 수 있도록 개선했습니다.
- `GET /api/diaries?account_id=...` API와 entries 응답의 `created_at` 필드를 추가해 보관함 조회를 지원했습니다.
- `implementation/playwright-checks/0103-issue14-main-redesign/`에 이슈 #14 검증 기록(스크린샷 6장 + 설명 문서)을 추가했습니다.

## 서비스 엔드포인트
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

## 핵심 API
- `POST /api/personas`
- `GET /api/personas?account_id=...`
- `POST /api/diaries`
- `POST /api/diaries/{diary_id}/personas/{persona_id}`
- `POST /api/entries/generate`
- `POST /api/entries/{entry_id}/save`
- `GET /api/diaries/{diary_id}/entries`
