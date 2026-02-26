# 구현 인덱스

## 현재 상태
- 진행 중: 인프라/앱 부트스트랩 1차 구현 완료.

## 마지막 완료 슬라이스
- FastAPI 최소 앱(`/`, `/health`, `/metrics`) + 로컬 Docker Compose + CI 워크플로우 추가.

## 테스트 상태
- `pytest -q` 통과.

## 열린 구현 작업
- `#3` 데이터 스키마 초안(SQLAlchemy 또는 SQL DDL) 구현 및 테스트.
- DB 연동 상태체크/설정 로딩 분리.
- ArgoCD 매니페스트 초안 추가.
