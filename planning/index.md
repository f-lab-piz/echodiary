# 플래닝 인덱스

## 현재 방향
- Ideation 1번 항목인 `키워드/자연어 기반 일기 자동 작성`을 1차 MVP 주제로 선택함.

## 중요성
- 일기 작성 진입 장벽을 낮춰 기록 지속성을 확보하는 핵심 기능임.

## MVP 범위
- 키워드/자연어 입력 기반 일기 생성.
- 계정 단위 페르소나 보유 + 일기장 단위 다중 연결/전환.
- 페르소나 생성(템플릿/수정/LLM 대화) 및 이미지 생성 재시도 정책.
- 관리자 전역 공급자 선택(OpenAI/Gemini) + 모델 타입(`text-small`, `text-large`, `image`) 라우팅 정책.
- 개발 인프라 표준화(Docker, GitHub Actions, ArgoCD, Prometheus, Grafana, FastAPI, Postgres) 및 AWS 전환(EC2/RDS) 정책.

## 활성 스펙
- `planning/README.md`
- `planning/spec-diary-writing.md`
- `planning/spec-admin-llm-provider.md`
- `planning/spec-dev-infra.md`

## 열린 질문
- 페르소나 대화 생성의 턴 제한과 완료 조건을 어떻게 정의할지?
- 이미지 생성 비용 상한과 모델 선택 기준을 어떻게 정할지?
- 전환 시 draft 기본 처리(`유지` vs `재생성`)를 무엇으로 할지?
- 공급자별 실제 모델명 업데이트 주기와 검증 절차를 어떻게 운영할지?
- ArgoCD 대상 환경을 초기부터 K8s로 둘지, EC2 단일 런타임으로 시작할지?
