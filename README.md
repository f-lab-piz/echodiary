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
```

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
