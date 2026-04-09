# AdSim -- 디자인 문서

> Show Me The PRD로 생성됨 (2026-04-09)
> MiroFish 기반 광고/USP 시뮬레이션 플랫폼

## 문서 구성

| 문서 | 내용 | 언제 읽나 |
|------|------|----------|
| [01_PRD.md](./01_PRD.md) | 뭘 만드는지, 누가 쓰는지 | 프로젝트 시작 전 |
| [02_DATA_MODEL.md](./02_DATA_MODEL.md) | 데이터 구조 | DB 설계할 때 |
| [03_PHASES.md](./03_PHASES.md) | 단계별 계획 | 개발 순서 정할 때 |
| [04_PROJECT_SPEC.md](./04_PROJECT_SPEC.md) | AI 규칙 | AI에게 코드 시킬 때마다 |
| [05_CODE_DESIGN.md](./05_CODE_DESIGN.md) | 코드 설계서 | 구현할 때 참고 |

## 다음 단계

Phase 1을 시작하려면 [03_PHASES.md](./03_PHASES.md)의 "Phase 1 시작 프롬프트"를 참고하세요.

## 확정 사항

- 에이전트 수: 사용자가 매번 선택 (기본 30명, 범위 10~100)
- 라운드 수: 기본 30라운드 (사용자 조절 가능)
- LLM: OpenRouter 경유 Claude
- DB: SQLite
- 배포: 로컬/내부 서버 (Docker)

## 미결 사항 (남은 것)

- [ ] Zep Cloud 무료/유료 전환 시점
- [ ] 페르소나 프리셋 목록
- [ ] 에이전트 대화 로그 저장 형식 (OASIS 출력 포맷 확인)
- [ ] 시드 자료 최대 용량/글자 수 제한
- [ ] ReportAgent 커스텀 여부
- [ ] MiroFish upstream 업데이트 전략
- [ ] 시뮬레이션 동시 실행 제한
- [ ] 에이전트 프롬프트 커스터마이징 범위
