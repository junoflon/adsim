# AdSim -- 프로젝트 스펙

> AI가 코드를 짤 때 지켜야 할 규칙과 절대 하면 안 되는 것.
> 이 문서를 AI에게 항상 함께 공유하세요.

---

## 기술 스택

| 영역 | 선택 | 이유 |
|------|------|------|
| 프레임워크 (프론트) | Vue 3 + Vite 7 | MiroFish 기존 프론트엔드를 그대로 확장. 새로 배울 것 없이 기존 컴포넌트 재사용 가능. |
| 프레임워크 (백엔드) | Flask + Flask-CORS | MiroFish 기존 백엔드 구조 유지. 시뮬레이션 엔진(OASIS)과의 연동이 이미 구현되어 있음. |
| 시뮬레이션 엔진 | CAMEL-OASIS v0.2.5 | MiroFish 핵심 엔진. 에이전트 간 소셜 상호작용 시뮬레이션에 최적화. |
| LLM | OpenAI 호환 API (기본: Qwen-plus) | MiroFish 기본 설정 유지. 비용 효율적이며 한국어 지원 양호. |
| 메모리/지식그래프 | Zep Cloud | MiroFish 기존 에이전트 기억 시스템 재사용. 무료 티어로 시작 가능. |
| 시각화 | D3.js v7 | MiroFish 기존 GraphPanel 컴포넌트 활용. Phase 2 대시보드에도 사용. |
| 파일 처리 | PyMuPDF | MiroFish 기존 PDF 파싱 기능 재사용. |
| 디스코드 봇 | discord.py (Phase 2) | Python 백엔드와 동일 언어. 시뮬레이션 실행 함수를 직접 호출 가능. |
| 배포 | Docker + docker-compose | MiroFish 기존 Docker 설정 확장. 단일 명령어로 전체 스택 실행. |
| 패키지 관리 | uv (Python) + npm (Node) | MiroFish 기존 구성 유지. |

---

## 프로젝트 구조

MiroFish를 fork한 뒤 광고 시뮬레이션 전용 모듈을 추가합니다.

```
MiroFish/  (fork)
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── graph.py                  # (기존) 그래프 API
│   │   │   ├── simulation.py             # (기존) 시뮬레이션 API
│   │   │   ├── report.py                 # (기존) 보고서 API
│   │   │   └── adsim.py                  # (신규) 광고 시뮬레이션 전용 API
│   │   ├── services/
│   │   │   ├── simulation_runner.py      # (기존) 시뮬레이션 실행
│   │   │   ├── report_agent.py           # (기존) 보고서 생성
│   │   │   ├── ad_simulation_service.py  # (신규) 광고 시뮬레이션 서비스
│   │   │   ├── usp_test_service.py       # (신규) USP 테스트 서비스
│   │   │   └── persona_manager.py        # (신규) 페르소나 관리
│   │   ├── models/
│   │   │   └── adsim_models.py           # (신규) AdSim 데이터 모델
│   │   ├── prompts/
│   │   │   ├── ad_consumer_persona.py    # (신규) 광고 소비자 에이전트 프롬프트
│   │   │   ├── usp_evaluator_persona.py  # (신규) USP 평가 에이전트 프롬프트
│   │   │   └── ad_report_prompt.py       # (신규) 광고 분석 보고서 프롬프트
│   │   └── utils/
│   ├── run.py
│   └── pyproject.toml
│
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── AdSimHome.vue             # (신규) AdSim 메인 페이지
│       │   ├── AdSimProject.vue          # (신규) 프로젝트 상세
│       │   ├── AdSimResult.vue           # (신규) 시뮬레이션 결과
│       │   └── AgentChatLog.vue          # (신규) 에이전트 대화 로그
│       ├── components/
│       │   ├── SeedUploader.vue          # (신규) 시드 자료 업로드
│       │   ├── PersonaSelector.vue       # (신규) 페르소나 설정
│       │   ├── SimulationProgress.vue    # (신규) 시뮬레이션 진행률
│       │   └── ReportViewer.vue          # (신규) 보고서 뷰어
│       └── router/
│
├── .env.example
├── docker-compose.yml
└── Dockerfile
```

---

## 절대 하지 마 (DO NOT)

> AI에게 코드를 시킬 때 이 목록을 반드시 함께 공유하세요.

- [ ] API 키나 비밀번호를 코드에 직접 쓰지 마 (.env 파일 사용)
- [ ] MiroFish 기존 코드의 핵심 로직을 수정하지 마 (fork 후 추가만)
- [ ] 기존 MiroFish API 엔드포인트를 변경하지 마 (신규 엔드포인트 추가만)
- [ ] 시뮬레이션 결과를 하드코딩하거나 목업으로 대체하지 마
- [ ] pyproject.toml/package.json의 기존 의존성 버전을 변경하지 마
- [ ] 에이전트 수를 100명 이상으로 기본 설정하지 마 (LLM 비용 폭증)
- [ ] 시뮬레이션 라운드를 40 이상으로 기본 설정하지 마 (MiroFish 권장)
- [ ] 사용자 입력을 검증 없이 LLM 프롬프트에 직접 삽입하지 마 (프롬프트 인젝션 방지)
- [ ] 테스트 없이 배포하지 마
- [ ] 한 커밋에 백엔드+프론트엔드 변경을 섞지 마 (분리 커밋)

---

## 항상 해 (ALWAYS DO)

- [ ] 변경하기 전에 계획을 먼저 보여줘
- [ ] 환경변수는 .env 파일에 저장 (.env.example에 설명 추가)
- [ ] 에러가 발생하면 사용자에게 한국어 친절한 메시지 표시
- [ ] 시뮬레이션 실행 중 진행률을 프론트엔드에 표시
- [ ] 에이전트 프롬프트에 한국어 페르소나 사용 (한국 소비자 시뮬레이션)
- [ ] MiroFish 기존 컴포넌트/서비스를 최대한 재사용
- [ ] 새 API 엔드포인트는 /api/adsim/ 프리픽스 사용
- [ ] 시드 자료 입력 시 최대 글자 수 체크 (LLM 컨텍스트 초과 방지)

---

## 테스트 방법

```bash
# 백엔드 실행
cd backend && uv run python run.py

# 프론트엔드 실행
cd frontend && npm run dev

# 전체 스택 (Docker)
docker-compose up

# 시뮬레이션 테스트 (curl)
curl -X POST http://localhost:5000/api/adsim/simulate \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test", "type": "ad_reaction", "seed": "테스트 광고 대본"}'
```

---

## 배포 방법

Docker 기반 배포 (MiroFish 기존 설정 확장):

```bash
# 1. .env 파일 설정
cp .env.example .env
# LLM_API_KEY, ZEP_API_KEY 등 입력

# 2. Docker 빌드 및 실행
docker-compose up -d --build

# 3. 접속 확인
# 프론트엔드: http://서버IP:3000
# 백엔드 API: http://서버IP:5000
```

---

## 환경변수

| 변수명 | 설명 | 어디서 발급 |
|--------|------|------------|
| LLM_API_KEY | LLM API 키 (Qwen-plus 등) | 알리바바 바이리안 플랫폼 |
| LLM_API_BASE_URL | LLM API 엔드포인트 | 알리바바 바이리안 플랫폼 |
| LLM_MODEL | 사용할 LLM 모델명 | 예: qwen-plus |
| ZEP_API_KEY | Zep Cloud API 키 | zep.ai |
| BOOST_LLM_API_KEY | (선택) 보조 빠른 모델 API 키 | 동일 플랫폼 |
| BOOST_LLM_MODEL | (선택) 보조 모델명 | 예: qwen-turbo |
| DISCORD_BOT_TOKEN | (Phase 2) 디스코드 봇 토큰 | Discord Developer Portal |

> .env 파일에 저장. 절대 GitHub에 올리지 마세요.

---

## 확정된 설정

| 항목 | 결정 |
|------|------|
| 에이전트 수 | 사용자가 매번 선택 (기본값 30, 범위 10~100) |
| 시뮬레이션 라운드 | 기본 30라운드 (사용자 조절 가능) |
| DB | SQLite |
| 배포 | 로컬/내부 서버 (Docker) |
| LLM | OpenRouter 경유 Claude |

## [NEEDS CLARIFICATION]

- [ ] MiroFish fork 시 upstream 업데이트를 어떻게 반영할지 전략
- [ ] 시뮬레이션 실행 큐/동시 실행 제한 (팀원이 동시에 돌리면?)
- [ ] 에이전트 프롬프트 커스터마이징 범위 (사용자가 프롬프트를 수정할 수 있게 할지)
