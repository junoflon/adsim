# AdSim -- 코드 설계서

> 생성일: 2026-04-10
> MiroFish 코드 분석 + PRD 기반 구체적 구현 설계

---

## 1. MiroFish 시뮬레이션 동작 구조

### 1.1 전체 파이프라인

```
문서 업로드
  → Step 1: Zep 지식그래프 구축 (OntologyGenerator → GraphBuilder)
  → Step 2: 에이전트 프로필 자동 생성 (ZepEntityReader → OasisProfileGenerator)
  → Step 3: OASIS 엔진 시뮬레이션 (Twitter + Reddit 병렬)
  → Step 4: ReportAgent 분석 보고서 생성
  → Step 5: 에이전트와 대화 상호작용
```

### 1.2 핵심 API 호출 순서

```
Step 1:
  POST /api/graph/ontology/generate  → 본체 생성
  POST /api/graph/build              → 그래프 구축 (비동기)

Step 2:
  POST /api/simulation/create        → 시뮬레이션 인스턴스 생성
  POST /api/simulation/prepare       → 에이전트 프로필 + 설정 생성 (비동기)

Step 3:
  POST /api/simulation/start         → OASIS 서브프로세스 실행
  GET  /api/simulation/run/{simId}   → 진행률 폴링 (500ms)

Step 4:
  POST /api/report/generate          → 보고서 생성 (비동기)

Step 5:
  POST /api/report/chat              → ReportAgent와 대화
  POST /api/simulation/interview     → 개별 에이전트와 대화
```

### 1.3 에이전트 액션 로그 형식 (JSONL)

```json
{"round": 1, "event_type": "round_start", "simulated_hour": 0}
{"round": 1, "agent_id": 42, "agent_name": "Alice", "action_type": "CREATE_POST", "action_args": {"content": "..."}, "success": true}
{"round": 1, "event_type": "round_end", "actions_count": 47}
{"event_type": "simulation_end", "total_rounds": 72, "total_actions": 2456}
```

**액션 타입**:
- Twitter: CREATE_POST, LIKE_POST, REPOST, FOLLOW, QUOTE_POST, DO_NOTHING
- Reddit: CREATE_POST, CREATE_COMMENT, LIKE_POST, DISLIKE_POST, LIKE_COMMENT, DISLIKE_COMMENT, SEARCH_POSTS, DO_NOTHING

### 1.4 데이터 저장 구조

```
backend/uploads/
├── projects/{project_id}/
│   ├── extracted_text.txt
│   ├── ontology.json
│   └── project.json
├── simulations/{simulation_id}/
│   ├── state.json
│   ├── run_state.json
│   ├── simulation_config.json
│   ├── reddit_profiles.json
│   ├── twitter_profiles.csv
│   ├── simulation.log
│   ├── twitter/actions.jsonl
│   └── reddit/actions.jsonl
└── reports/{report_id}/
    ├── report.md
    ├── report.json
    ├── metadata.json
    └── agent_log.jsonl
```

### 1.5 설정 기본값

| 항목 | 기본값 |
|------|--------|
| 시뮬레이션 시간 | 72시간 (3일) |
| 1라운드 = | 60분 |
| 피크 시간 | 19~22시 (활동 1.5배) |
| 오프피크 | 0~5시 (활동 0.05배) |
| ReportAgent 도구 호출 | 최대 5회/섹션 |

---

## 2. AdSim 신규 파일 목록

### 2.1 백엔드

```
backend/app/
├── api/
│   └── adsim.py                          # (신규) AdSim API 블루프린트
├── services/
│   ├── ad_simulation_service.py          # (신규) 광고 반응 시뮬레이션
│   ├── usp_test_service.py               # (신규) USP 테스트
│   ├── persona_manager.py                # (신규) 페르소나 관리
│   └── ad_report_service.py              # (신규) 보고서 생성
├── prompts/
│   ├── ad_consumer_persona.py            # (신규) 광고 소비자 프롬프트
│   ├── usp_evaluator_persona.py          # (신규) USP 평가 프롬프트
│   └── ad_report_prompt.py               # (신규) 보고서 생성 프롬프트
└── database/
    ├── adsim_schema.sql                  # (신규) SQLite 스키마
    └── adsim_db.py                       # (신규) DB 관리 클래스
```

### 2.2 프론트엔드

```
frontend/src/
├── views/
│   ├── AdSimHome.vue                     # (신규) 프로젝트 목록
│   ├── AdSimProject.vue                  # (신규) 프로젝트 상세
│   ├── AdSimResult.vue                   # (신규) 시뮬레이션 결과
│   └── AgentChatLog.vue                  # (신규) 에이전트 대화 상세
├── components/
│   ├── SeedUploader.vue                  # (신규) 시드 업로드
│   ├── PersonaSelector.vue               # (신규) 페르소나 설정
│   ├── SimulationProgress.vue            # (신규) 진행률 표시
│   ├── ReportViewer.vue                  # (신규) 보고서 뷰어
│   ├── AgentResponseList.vue             # (신규) 반응 목록
│   └── SimulationConfigForm.vue          # (신규) 시뮬레이션 설정 폼
├── api/
│   └── adsim.js                          # (신규) API 호출 함수
└── router/
    └── adsim-routes.js                   # (신규) 라우트 정의
```

---

## 3. API 엔드포인트 설계

### 3.1 프로젝트 관리

```
POST   /api/adsim/projects                    # 프로젝트 생성
GET    /api/adsim/projects                    # 프로젝트 목록
GET    /api/adsim/projects/{project_id}       # 프로젝트 상세
DELETE /api/adsim/projects/{project_id}       # 프로젝트 삭제
```

요청 예시:
```json
POST /api/adsim/projects
{
  "name": "신규 음료 TV광고 테스트",
  "type": "ad_reaction",
  "description": "제로칼로리 음료 광고 소비자 반응 확인"
}
```

### 3.2 시드 자료

```
POST   /api/adsim/projects/{project_id}/seeds         # 시드 업로드
GET    /api/adsim/projects/{project_id}/seeds         # 시드 목록
DELETE /api/adsim/projects/{project_id}/seeds/{seed_id}  # 시드 삭제
```

요청 예시:
```json
POST /api/adsim/projects/{project_id}/seeds
Content-Type: multipart/form-data
{
  "type": "ad_script",
  "content": "광고 대본 텍스트...",
  "file": <PDF 파일>
}
```

### 3.3 페르소나 설정

```
POST   /api/adsim/projects/{project_id}/personas      # 페르소나 생성
GET    /api/adsim/projects/{project_id}/personas      # 페르소나 목록
GET    /api/adsim/personas/presets                     # 프리셋 목록
DELETE /api/adsim/projects/{project_id}/personas/{id}  # 페르소나 삭제
```

요청 예시:
```json
POST /api/adsim/projects/{project_id}/personas
{
  "name": "2030 건강 관심 여성",
  "age_range": "25-35",
  "gender": "여성 70%, 남성 30%",
  "interests": ["건강", "다이어트", "운동"],
  "consumption_habits": "편의점 음료 주 3회 이상 구매",
  "agent_count": 30,
  "is_preset": false
}
```

### 3.4 시뮬레이션 실행

```
POST   /api/adsim/projects/{project_id}/simulations     # 시뮬레이션 시작
GET    /api/adsim/simulations/{simulation_id}           # 상태 조회
GET    /api/adsim/simulations/{simulation_id}/progress  # 실시간 진행률
PATCH  /api/adsim/simulations/{simulation_id}/cancel    # 취소
```

요청 예시:
```json
POST /api/adsim/projects/{project_id}/simulations
{
  "seed_id": "seed-def456",
  "persona_id": "persona-ghi789",
  "total_rounds": 30,
  "custom_agent_count": 30
}
```

### 3.5 결과 및 보고서

```
GET /api/adsim/simulations/{simulation_id}/report              # 분석 보고서
GET /api/adsim/simulations/{simulation_id}/responses           # 에이전트 반응 목록
GET /api/adsim/simulations/{simulation_id}/responses/{agent_id}  # 특정 에이전트 대화
GET /api/adsim/simulations/{simulation_id}/rounds              # 라운드별 기록
```

---

## 4. SQLite 스키마

```sql
-- 프로젝트
CREATE TABLE adsim_projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,          -- "ad_reaction" | "usp_test"
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 시드 자료
CREATE TABLE adsim_seed_materials (
    seed_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    type TEXT NOT NULL,          -- "ad_script" | "usp_text" | "competitor_info"
    content TEXT,
    file_path TEXT,
    file_size INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE
);

-- 페르소나 설정
CREATE TABLE adsim_persona_configs (
    persona_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    age_range TEXT NOT NULL,
    gender TEXT,
    interests TEXT,              -- JSON 배열
    consumption_habits TEXT,
    agent_count INTEGER NOT NULL DEFAULT 30,
    is_preset INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE
);

-- 시뮬레이션
CREATE TABLE adsim_simulations (
    simulation_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    persona_config_id TEXT NOT NULL,
    seed_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | running | completed | failed
    total_rounds INTEGER NOT NULL DEFAULT 30,
    current_round INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES adsim_projects(project_id) ON DELETE CASCADE
);

-- 에이전트 반응
CREATE TABLE adsim_agent_responses (
    response_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    agent_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    agent_persona TEXT NOT NULL,     -- JSON
    sentiment TEXT NOT NULL,         -- positive | negative | neutral
    sentiment_score REAL NOT NULL,   -- -1.0 ~ 1.0
    key_reactions TEXT NOT NULL,     -- JSON 배열
    conversation_log TEXT NOT NULL,  -- JSON 배열
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);

-- 라운드 기록
CREATE TABLE adsim_simulation_rounds (
    round_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    summary TEXT,
    sentiment_snapshot TEXT NOT NULL,  -- JSON: {positive: 10, negative: 2, neutral: 3}
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);

-- 보고서
CREATE TABLE adsim_reports (
    report_id TEXT PRIMARY KEY,
    simulation_id TEXT NOT NULL UNIQUE,
    overall_sentiment TEXT NOT NULL,   -- JSON: {positive: 68, negative: 22, neutral: 10}
    key_insights TEXT NOT NULL,        -- JSON 배열
    concerns TEXT NOT NULL,            -- JSON 배열
    recommendations TEXT NOT NULL,     -- JSON 배열
    full_report_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES adsim_simulations(simulation_id) ON DELETE CASCADE
);
```

---

## 5. 에이전트 프롬프트 설계

### 5.1 광고 소비자 시스템 프롬프트

```
당신은 {이름}입니다.

## 기본 정보
- 나이: {나이}세, 성별: {성별}, 직업: {직업}
- 관심사: {관심사 목록}
- 소비 습관: {소비 습관}

## 성격 특성
{성격 특성 목록}

## 역할
당신은 이 캐릭터로 완전히 역할하며, 성격과 경험에 맞게 광고에 반응합니다.
솔직한 감정을 표현하고, 자연스러운 한국어로 답변하세요.
```

### 5.2 라운드별 평가 프롬프트

| 라운드 | 질문 |
|--------|------|
| 1 (첫인상) | "이 광고를 보고 느낀 첫 인상을 솔직하게 말해주세요" |
| 2 (설득력) | "가장 설득력 있게 느껴진 부분은? 왜?" |
| 3 (우려사항) | "불안하거나 의심스러운 부분이 있었나요?" |
| 4+ (구매의향) | "실제로 구매할 가능성은? (1~10점) 이유는?" |

### 5.3 페르소나 프리셋 (10개)

| 이름 | 연령 | 특성 |
|------|------|------|
| 2030 건강 여성 | 25-35 | 건강, 다이어트, SNS 활동 |
| 3040 직장인 남성 | 30-45 | 경제 의식, 실용주의, 시간 절약 |
| 2030 트렌드 세터 | 20-30 | SNS 활동, 신제품 호기심, 가성비 |
| 4050 가족 중심 | 40-55 | 가족, 안정성, 검증된 브랜드 |
| 2030 학생 | 18-25 | 가격 민감, 편의점 문화, 트렌드 |
| 3040 프리미엄 소비자 | 30-45 | 품질 우선, 브랜드 가치, 건강기능 |
| 전 연령 일반 | 20-55 | 다양한 성향 혼합 |
| 시니어 보수층 | 50-65 | 전통 가치, 신뢰, 품질 |
| 2030 MZ 감성 | 20-35 | 감성 소비, 인스타그래머블, 경험 중시 |
| 3040 워킹맘 | 30-45 | 시간 부족, 간편함, 아이 건강 |

---

## 6. MiroFish 재사용 부분

| 기존 코드 | 재사용 방법 |
|-----------|------------|
| `utils/llm_client.py` | OpenRouter 경유 Claude 호출 (수정 없이 그대로) |
| `services/zep_tools.py` | 에이전트 메모리 검색 (그대로) |
| `services/text_processor.py` | PDF → 텍스트 파싱 (그대로) |
| `services/oasis_profile_generator.py` | 프로필 생성 로직 참고하여 AdSim용 커스텀 |
| `services/report_agent.py` | 보고서 ReACT 패턴 참고하여 AdSim용 간소화 |
| `utils/logger.py` | 로깅 (그대로) |
| `utils/locale.py` | 한국어 지원 (그대로) |

---

## 7. 프론트엔드 라우터

```javascript
// frontend/src/router/adsim-routes.js
const adSimRoutes = [
  { path: '/adsim',                                    name: 'AdSimHome',    component: AdSimHome },
  { path: '/adsim/project/:projectId',                 name: 'AdSimProject', component: AdSimProject },
  { path: '/adsim/simulation/:simulationId',           name: 'AdSimResult',  component: AdSimResult },
  { path: '/adsim/simulation/:simulationId/agent/:agentId', name: 'AgentChatLog', component: AgentChatLog }
]
```

---

## 8. 사용자 흐름 (통합)

```
1. /adsim → 프로젝트 생성 ("신규 음료 TV광고 테스트")
2. /adsim/project/{id} →
   a. 시드 업로드 (광고 대본 텍스트 or PDF)
   b. 페르소나 선택 (프리셋 or 커스텀 + 에이전트 수 슬라이더)
   c. 시뮬레이션 설정 (라운드 수) + 실행 버튼
3. 시뮬레이션 진행 중 → 프로그레스 바 + 예상 남은 시간
4. /adsim/simulation/{id} →
   a. 보고서 (긍정/부정 비율, 인사이트, 우려사항, 추천)
   b. 에이전트 반응 목록 (테이블)
5. /adsim/simulation/{id}/agent/{agentId} →
   a. 개별 에이전트의 전체 대화 로그
```
