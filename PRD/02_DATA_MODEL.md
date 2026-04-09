# AdSim -- 데이터 모델

> 이 문서는 앱에서 다루는 핵심 데이터의 구조를 정의합니다.
> 개발자가 아니어도 이해할 수 있는 "개념적 ERD"입니다.

---

## 전체 구조

```
[프로젝트] --1:N--> [시드 자료]
    |
    +--1:N--> [페르소나 설정]
    |
    +--1:N--> [시뮬레이션] --1:N--> [에이전트 반응]
                  |
                  +--1:N--> [라운드 기록]
                  |
                  +--1:1--> [보고서]
```

---

## 엔티티 상세

### 프로젝트 (Project)
하나의 광고/USP 테스트 캠페인을 묶는 최상위 단위.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | proj-abc123 | O |
| name | 프로젝트 이름 | "신규 음료 TV광고 테스트" | O |
| type | 시뮬레이션 유형 | "ad_reaction" 또는 "usp_test" | O |
| description | 프로젝트 설명 | "제로칼로리 음료 광고 소비자 반응 확인" | X |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |
| updated_at | 수정 날짜 (자동) | 2026-04-09 | O |

### 시드 자료 (SeedMaterial)
업로드한 광고 대본, USP 설명, 경쟁사 정보 등 원본 자료.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | seed-def456 | O |
| project_id | 어떤 프로젝트 소속인지 | proj-abc123 | O |
| type | 자료 유형 | "ad_script", "usp_text", "competitor_info" | O |
| content | 텍스트 내용 | "제로칼로리인데 맛있다..." | O |
| file_path | 업로드 파일 경로 (PDF 등) | "/uploads/ad_script.pdf" | X |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |

### 페르소나 설정 (PersonaConfig)
가상 소비자 집단의 특성 정의.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | persona-ghi789 | O |
| project_id | 어떤 프로젝트 소속인지 | proj-abc123 | O |
| name | 페르소나 이름 | "2030 건강 관심 여성" | O |
| age_range | 연령대 | "25-35" | O |
| gender | 성별 분포 | "여성 70%, 남성 30%" | X |
| interests | 관심사 목록 | ["건강", "다이어트", "운동"] | O |
| consumption_habits | 소비 습관 | "편의점 음료 주 3회 이상 구매" | X |
| agent_count | 생성할 에이전트 수 | 50 | O |
| is_preset | 프리셋 여부 | true | O |

### 시뮬레이션 (Simulation)
MiroFish 엔진으로 실행한 한 번의 시뮬레이션.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | sim-jkl012 | O |
| project_id | 어떤 프로젝트 소속인지 | proj-abc123 | O |
| persona_config_id | 어떤 페르소나 설정 사용 | persona-ghi789 | O |
| status | 실행 상태 | "pending", "running", "completed", "failed" | O |
| total_rounds | 전체 라운드 수 | 30 | O |
| current_round | 현재 진행 라운드 | 15 | O |
| started_at | 시작 시각 | 2026-04-09 14:30:00 | X |
| completed_at | 완료 시각 | 2026-04-09 15:00:00 | X |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |

### 에이전트 반응 (AgentResponse)
각 가상 소비자의 개별 반응과 대화 내용.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | resp-mno345 | O |
| simulation_id | 어떤 시뮬레이션 소속 | sim-jkl012 | O |
| agent_name | 에이전트 이름 | "김지연 (28세, 직장인)" | O |
| agent_persona | 에이전트 성격/설정 요약 | "건강 관심 높음, 가격 민감" | O |
| sentiment | 전체 감정 | "positive", "negative", "neutral" | O |
| sentiment_score | 감정 점수 (-1.0 ~ 1.0) | 0.7 | O |
| key_reactions | 핵심 반응 요약 | ["광고 톤이 신선함", "가격 언급 없어서 불안"] | O |
| conversation_log | 전체 대화 내용 | [{role, content, round}] | O |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |

### 라운드 기록 (SimulationRound)
시뮬레이션 진행 단계별 스냅샷.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | round-pqr678 | O |
| simulation_id | 어떤 시뮬레이션 소속 | sim-jkl012 | O |
| round_number | 라운드 번호 | 5 | O |
| summary | 이 라운드 요약 | "가격에 대한 토론이 시작됨" | O |
| sentiment_snapshot | 이 시점 감정 분포 | {positive: 60, negative: 25, neutral: 15} | O |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |

### 보고서 (Report)
시뮬레이션 결과 종합 분석.

| 필드 | 설명 | 예시 | 필수 |
|------|------|------|------|
| id | 고유 식별자 (자동 생성) | rpt-stu901 | O |
| simulation_id | 어떤 시뮬레이션의 보고서 | sim-jkl012 | O |
| overall_sentiment | 전체 긍정/부정 비율 | {positive: 68, negative: 22, neutral: 10} | O |
| key_insights | 핵심 인사이트 목록 | ["가격 미언급이 최대 우려", "톤이 신선하다는 평가 다수"] | O |
| concerns | 우려 사항 | ["가격 경쟁력 의문", "타겟 연령 미스매치 가능성"] | O |
| recommendations | 추천 사항 | ["가격 정보 추가 권장", "30대 타겟에 맞게 톤 조정"] | O |
| full_report_text | 전체 보고서 텍스트 | "..." | O |
| created_at | 만든 날짜 (자동) | 2026-04-09 | O |

---

## 관계

- **프로젝트** 1개에 여러 개의 **시드 자료**를 업로드할 수 있음
- **프로젝트** 1개에 여러 개의 **페르소나 설정**을 만들 수 있음
- **프로젝트** 1개에 여러 번의 **시뮬레이션**을 실행할 수 있음
- **시뮬레이션** 1번에 여러 개의 **에이전트 반응**이 생성됨
- **시뮬레이션** 1번에 여러 개의 **라운드 기록**이 쌓임
- **시뮬레이션** 1번에 **보고서** 1개가 생성됨

---

## 왜 이 구조인가

MiroFish의 기존 데이터 흐름(시드 자료 → 그래프 구축 → 환경 설정 → 시뮬레이션 → 보고서)을 그대로 반영한 구조입니다.

- **확장성**: Phase 2에서 A/B 비교 추가 시, 동일 프로젝트에 시뮬레이션 2개를 실행하고 보고서를 비교하면 됨. 디스코드 봇은 프로젝트 ID만 있으면 바로 연동 가능.
- **단순성**: MiroFish가 이미 처리하는 에이전트 생성/시뮬레이션/보고서 생성을 재사용하고, 프로젝트와 페르소나 설정만 새로 추가.

---

## [NEEDS CLARIFICATION]

- [ ] 에이전트 대화 로그 저장 형식 (MiroFish OASIS 출력 포맷 확인 필요)
- [ ] 시드 자료 최대 용량/글자 수 제한
- [ ] 보고서 생성에 MiroFish ReportAgent를 그대로 쓸지, 커스텀 프롬프트를 만들지
