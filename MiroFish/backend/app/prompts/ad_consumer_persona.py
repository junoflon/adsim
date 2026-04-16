"""
광고 소비자 에이전트 프롬프트
개별 가상 소비자에게 광고를 평가시키기 위한 프롬프트 생성
"""

from typing import Dict, Any, Optional


def create_ad_consumer_system_prompt(agent: Dict[str, Any]) -> str:
    """
    광고 소비자 에이전트의 시스템 프롬프트 생성

    Args:
        agent: {
            "name": "김지연",
            "age": 28,
            "gender": "여성",
            "occupation": "직장인",
            "interests": ["건강", "다이어트"],
            "personality_traits": ["신중함", "가격민감"],
            "income_level": "중",
            "shopping_habits": "편의점 음료 주 3회 이상"
        }
    """
    traits = ", ".join(agent.get("personality_traits", []))
    interests = ", ".join(agent.get("interests", []))

    return f"""당신은 실제 한국 소비자 {agent['name']}입니다.

## 당신의 프로필
- 나이: {agent.get('age', '?')}세
- 성별: {agent.get('gender', '?')}
- 직업: {agent.get('occupation', '?')}
- 소득 수준: {agent.get('income_level', '중')}
- 관심사: {interests}
- 성격: {traits}
- 평소 소비 습관: {agent.get('shopping_habits', '')}

## 행동 원칙
1. **진짜 소비자처럼 반응하세요.** 마케팅 전문가가 아니라 평범한 한국 소비자입니다.
2. **당신의 프로필에 충실하세요.** 나이, 성별, 소득 수준, 성격에 맞게 판단하세요.
3. **솔직하게 감정을 표현하세요.** 좋으면 좋다, 별로면 별로다. 과장 금지.
4. **짧고 자연스러운 한국어**로 답하세요. 3~5문장 이내.
5. 한국 소비자 특성을 반영하세요: 가격 민감도, 리뷰/입소문 중시, 브랜드 신뢰도.

광고를 볼 때는 다음을 자연스럽게 고려하세요:
- 이 제품이 내 일상에 맞는가?
- 가격 대비 가치가 있어 보이는가?
- 신뢰가 가는가? 의심스러운 부분은 없는가?
- 주변 사람들이 어떻게 반응할까?
"""


def create_ad_evaluation_user_prompt(
    seed_content: str,
    round_number: int,
    previous_reactions: Optional[str] = None
) -> str:
    """
    라운드별 광고 평가 프롬프트
    """
    context = ""
    if previous_reactions:
        context = f"\n[이전 당신의 반응 요약]\n{previous_reactions}\n"

    if round_number == 1:
        return f"""[광고 내용]
{seed_content}

위 광고를 처음 본 당신의 솔직한 첫인상을 말해주세요.
- 어떤 느낌이 드나요?
- 눈에 띄는 장점 또는 걸리는 부분이 있나요?
{context}"""

    elif round_number == 2:
        return f"""[광고 내용]
{seed_content}
{context}
다시 이 광고를 찬찬히 보니 어떤가요?
- 가장 설득력 있게 다가온 부분은 무엇인가요?
- 당신의 일상과 연결되는 부분이 있나요?"""

    elif round_number == 3:
        return f"""[광고 내용]
{seed_content}
{context}
이 광고/제품에 대해 불안하거나 의심스러운 부분이 있나요?
- 가격, 품질, 신뢰성, 필요성 등에서
- 솔직히 말해주세요."""

    else:
        return f"""[광고 내용]
{seed_content}
{context}
종합해서, 이 제품을 실제로 구매할 가능성은 얼마나 될까요?
- 1~10점 (1=절대 안 산다, 10=꼭 사고 싶다)
- 그렇게 판단한 이유도 1~2문장으로."""


def create_sentiment_analysis_prompt(conversation_log: list) -> str:
    """
    개별 에이전트의 대화 로그를 분석해서 감정 점수 추출
    """
    conversation_text = "\n".join([
        f"[라운드 {msg.get('round', '?')}] {msg['role']}: {msg['content']}"
        for msg in conversation_log
    ])

    return f"""다음은 한 소비자가 광고를 보고 여러 라운드에 걸쳐 반응한 대화입니다.
이 소비자의 전체 반응을 분석해주세요.

[대화 내용]
{conversation_text}

다음 JSON 형식으로 응답하세요:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "sentiment_score": <-1.0 ~ 1.0 사이 실수. 1.0=매우 긍정, -1.0=매우 부정>,
  "key_reactions": ["핵심 반응 1", "핵심 반응 2", ...] (2~4개)
}}

sentiment_score 가이드:
- 0.7 이상: 매우 긍정적, 구매 의향 높음
- 0.3 ~ 0.7: 긍정적, 관심 있음
- -0.3 ~ 0.3: 중립, 결정 못함
- -0.7 ~ -0.3: 부정적, 우려 있음
- -0.7 이하: 매우 부정적, 거부감
"""
