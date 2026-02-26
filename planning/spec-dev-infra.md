# spec-dev-infra

## Problem
- 기능 개발과 운영 인프라가 분리되어 정의되지 않아 개발 속도, 배포 안정성, 장애 대응 기준이 불명확하다.
- 로컬 개발 환경과 AWS 운영 환경 간 차이를 조기에 설계하지 않으면 전환 시 회귀와 운영 리스크가 커진다.

## Target User
- EchoDiary 백엔드/인프라를 구현하고 운영하는 1인 개발자.

## User Value
- 로컬에서 빠르게 개발하고, 이후 AWS(EC2/RDS)로 무리 없이 전환할 수 있다.
- CI/CD, 모니터링, 배포 기준이 명확해 변경 리스크를 줄인다.

## Use Cases
- 개발자가 Docker Compose로 FastAPI/Postgres/모니터링 스택을 로컬에서 실행한다.
- PR/merge 시 GitHub Actions가 테스트/빌드/이미지 푸시를 자동 수행한다.
- ArgoCD가 GitOps 방식으로 배포 상태를 동기화한다.
- 운영 중 Prometheus/Grafana로 API 오류율/지연/DB 상태를 확인한다.

## Corner Cases
- 로컬과 운영(Postgres 버전/설정) 차이로 마이그레이션 실패.
- EC2 롤링 배포 중 헬스체크 실패로 서비스 다운타임 발생.
- RDS 연결 제한 초과로 API 오류 급증.
- Prometheus 스크랩 실패로 관측 공백 발생.

## Behavior Spec
- 애플리케이션 프레임워크는 FastAPI를 사용한다.
- 로컬 개발은 Docker Compose 기반으로 구성한다.
- 로컬 기본 구성: `api(FastAPI)`, `db(Postgres)`, `prometheus`, `grafana`.
- CI는 GitHub Actions로 운영한다.
- CI 단계: `lint/test` -> `docker build` -> `image push` -> 배포 매니페스트 업데이트(PR 또는 main 반영).
- CD는 ArgoCD를 사용해 Git 저장소의 매니페스트 상태를 클러스터/대상 환경과 동기화한다.
- 개발 단계에서는 로컬 Compose 중심으로 진행하고, 운영 단계에서 AWS로 이관한다.
- 운영 인프라는 AWS EC2(애플리케이션 런타임) + AWS RDS PostgreSQL(관리형 DB) 조합을 사용한다.
- 애플리케이션은 환경 변수로 DB/외부 API/모니터링 설정을 주입한다.
- 비밀정보는 Git에 커밋하지 않고, 환경별 시크릿 저장소(예: AWS SSM Parameter Store 또는 Secrets Manager)로 관리한다.
- Prometheus는 FastAPI 메트릭 엔드포인트를 스크랩한다.
- Grafana는 최소 대시보드로 API RPS, p95 latency, error rate, DB 연결 수를 제공한다.
- 배포 게이트: 헬스체크 실패 시 자동 롤백(또는 즉시 이전 리비전 복구) 가능한 절차를 유지한다.

## Cost and Complexity
- 고비용 요소:
- ArgoCD 도입, AWS 인프라 구성(IAM/VPC/보안그룹), 모니터링 운영.
- 저비용 대안:
- 초기에는 단일 EC2 + 수동 배포 + CloudWatch 기본 모니터링.
- 비교:
- 저비용 대안은 시작은 빠르지만 배포 일관성과 변경 추적성(GitOps), 관측성이 낮다.

## Usability
- 로컬 온보딩은 `docker compose up` 한 번으로 시작 가능해야 한다.
- CI 실패 원인은 PR에서 즉시 확인 가능해야 한다.
- 운영 대시보드는 장애 판단에 필요한 지표만 우선 노출한다.

## Risks and Mitigations
- Risk: 인프라 범위 확장으로 초기 개발 일정 지연.
- Mitigation: 1단계(로컬+CI) -> 2단계(AWS 배포) -> 3단계(관측 고도화)로 단계 분리.
- Risk: ArgoCD/GitHub Actions 파이프라인 복잡도 증가.
- Mitigation: 배포 경로를 단일화(main 브랜치 기준)하고 템플릿화.
- Risk: DB 마이그레이션 실패로 배포 실패.
- Mitigation: 배포 전 마이그레이션 검증 단계와 백업/롤백 절차 포함.
- Risk: 모니터링 미흡으로 장애 탐지 지연.
- Mitigation: 필수 알람(error rate, DB 연결 실패, 인스턴스 다운)부터 우선 적용.

## Decision
- 개발 표준 스택은 `FastAPI + Postgres + Docker + GitHub Actions + ArgoCD + Prometheus + Grafana`로 확정한다.
- 개발 중에는 로컬 Compose를 기준으로 구현하고, 운영 전환 시 `EC2 + RDS`로 배포한다.
- CD는 GitOps(ArgoCD) 방식으로 일관되게 운영한다.

## MVP Scope
- 포함:
- 로컬 Docker Compose 실행 환경(FastAPI/Postgres/Prometheus/Grafana).
- GitHub Actions CI 파이프라인(lint/test/build/push).
- ArgoCD 기반 배포 동기화 경로 정의.
- AWS EC2/RDS 배포 토폴로지와 환경 변수/시크릿 관리 원칙 정의.
- 비포함(Non-goal):
- 멀티 AZ/멀티 리전 고가용성.
- 오토스케일링 고도화(HPA/Cluster Autoscaler).
- 분산 트레이싱(Tempo/Jaeger) 및 비용 최적화 자동화.

## Success Metrics
- 신규 개발 환경 세팅 시간(목표: 30분 이내).
- CI 성공률 및 평균 실행 시간.
- 배포 성공률과 평균 복구 시간(MTTR).
- API p95 latency, error rate.
- RDS 연결 오류율 및 DB 자원 사용률.

## Open Questions
- ArgoCD 대상 실행 환경을 단일 EC2 기반으로 시작할지, 초기부터 K8s(EKS/k3s)로 갈지.
- 이미지 레지스트리를 GHCR로 고정할지, ECR로 조기 전환할지.
- 모니터링 장기 보관을 Prometheus 단독으로 할지, CloudWatch 연계를 병행할지.

## Next Actions
- `infra/docker-compose.yml` 초안 작성(FastAPI/Postgres/Prometheus/Grafana).
- FastAPI `/health`, `/metrics` 엔드포인트 표준 확정.
- GitHub Actions 워크플로우(`ci.yml`) 초안 작성.
- ArgoCD 애플리케이션 매니페스트 저장소 구조 정의.
- AWS EC2/RDS 최소 네트워크/IAM 체크리스트 문서화.
