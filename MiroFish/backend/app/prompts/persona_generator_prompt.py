"""
페르소나 자동 생성 프롬프트
사용자 입력 + 고정 연령/성별 + 기존 페르소나 회피
"""

from typing import List, Dict


def create_persona_generation_prompt(
    description: str,
    age_min: int,
    age_max: int,
    female_ratio: int,
    existing_personas: List[Dict] = None,
) -> str:
    existing_personas = existing_personas or []
    existing_block = ""
    if existing_personas:
        lines = []
        for i, p in enumerate(existing_personas, 1):
            interests = ", ".join(p.get("interests", []) or [])
            lines.append(f"{i}. {p.get('name')} (관심사: {interests} | 소비: {p.get('consumption_habits', '')[:60]})")
        existing_block = (
            "\n## 이미 존재하는 페르소나 — 아래와 유사/중복되지 않도록 반드시 다른 각도로 작성하세요\n"
            + "\n".join(lines) + "\n"
        )

    male_ratio = 100 - female_ratio
    return f"""당신은 마케팅 리서치 전문가입니다.
사용자가 입력한 타겟 설명을 바탕으로 상세한 타겟 페르소나를 만들어주세요.

## 사용자 입력
{description}

## 고정 조건 (반드시 그대로 유지 — 바꾸지 마세요)
- 연령대: {age_min}~{age_max}세
- 성별 구성: 여성 {female_ratio}% / 남성 {male_ratio}%
{existing_block}
## 요청
다음 JSON 형식으로 응답하세요. 연령/성별 필드는 출력하지 마세요 (고정값 사용).
{{
  "name": "페르소나 이름 — 20자 이내, 이 집단의 정체성이 드러나게 (예: '편의점 신상 애용 2030 직장인')",
  "interests": ["관심사1", "관심사2", ...] (5~8개, 한국 소비자 맥락의 구체적 관심사. '건강' 같은 추상적 단어 대신 '홈트 기구', 'SNS 바이럴 뷰티', '편의점 신상', '절약 재테크' 처럼 구체적으로),
  "consumption_habits": "소비 습관과 구매 맥락을 2~4문장으로. 언제/어디서/얼마나 자주/가격대/의사결정 방식까지 포함. 이 사람이 광고나 제품을 볼 때 어떻게 반응할지 판단할 수 있을 만큼 맥락이 풍부해야 함.",
  "personality_tags": ["성격 태그 2~4개"] - 다음 중에서만 선택: '신중함', '트렌드 민감', '가성비 추구', '프리미엄 선호', '의심 많음', '입소문 전파', '충동구매 성향', '브랜드 충성'
}}

가이드라인:
- 고정된 연령/성별 구성과 자연스럽게 어울리는 특성으로 작성
- 기존 페르소나 목록이 있다면, 관심사·소비 맥락·성격이 서로 겹치지 않도록 다른 각도로 포지셔닝
- JSON 외 다른 텍스트는 출력하지 마세요.
"""
