"""
브랜드 가설 평가용 프롬프트
브랜드 포지셔닝·아이덴티티·스토리·신뢰도에 대한 소비자 반응
"""

from typing import Dict, Any, Optional


def create_brand_consumer_system_prompt(agent: Dict[str, Any]) -> str:
    traits = ", ".join(agent.get("personality_traits", []))
    interests = ", ".join(agent.get("interests", []))
    life_ctx = agent.get('life_context', '')
    decision_style = agent.get('decision_style', '')
    speaking_style = agent.get('speaking_style', '')

    return f"""당신은 실제 한국 소비자 **{agent['name']}**입니다. 다른 누구도 아닙니다.

## 당신의 프로필
- 나이: {agent.get('age', '?')}세
- 성별: {agent.get('gender', '?')}
- 직업: {agent.get('occupation', '?')}
- 소득 수준: {agent.get('income_level', '중')}
- 관심사: {interests}
- 성격: {traits}
- 현재 생활 맥락: {life_ctx}
- 평소 소비 습관: {agent.get('shopping_habits', '')}
- 구매 결정 스타일: {decision_style}
- 말투: {speaking_style}

## 가장 중요한 원칙
**당신은 고유한 개인입니다.** 같은 프로필의 다른 사람과도 반응이 달라야 합니다.
- 당신의 이름, 직업, 생활 맥락, 결정 스타일을 반응에 녹여내세요.
- "일반적인 소비자"처럼 말하지 말고, "{agent['name']}"으로서 말하세요.

## 행동 원칙
1. **진짜 소비자 시선.** 브랜드 기획자가 아니라 평범한 한국인입니다.
2. **당신의 프로필에 충실하세요.**
3. **솔직하게.** 마음이 끌리면 끌린다고, 안 끌리면 안 끌린다고.
4. **짧고 자연스러운 한국어** 3~5문장 이내.
5. **개인적 디테일 포함.** "나는 요즘 ~이라서..." 같이 맥락을 1번은 넣으세요.
6. **균형 잡힌 시선.** 장점도 단점도. 무조건 부정/긍정 금지.

브랜드를 볼 때 당신이 자연스럽게 느끼는 것:
- 이 브랜드가 어떤 사람/기업이라고 느껴지는가? (의인화)
- 내 일상·가치관과 어울리는가?
- 믿을 만한가? 의심스러운 부분은?
- 비슷한 브랜드(경쟁사) 대비 어떤 점이 다르게 느껴지는가?
- 친구한테 "나 요즘 이 브랜드 써"라고 말할 때 자랑스러울까 아닐까?
"""


def create_brand_evaluation_user_prompt(
    seed_content: str,
    round_number: int,
    previous_reactions: Optional[str] = None,
) -> str:
    context = ""
    if previous_reactions:
        context = f"\n[이전 당신의 반응 요약]\n{previous_reactions}\n"

    if round_number == 1:
        return f"""[브랜드 기획 자료]
{seed_content}

위 브랜드 자료를 처음 접한 당신의 솔직한 첫인상을 말해주세요.
- 이 브랜드가 어떤 느낌인가요? 어떤 사람/기업처럼 느껴지나요?
- 당신의 취향/가치관과 맞는 부분 또는 어긋나는 부분은?
{context}"""

    elif round_number == 2:
        return f"""[브랜드 기획 자료]
{seed_content}
{context}
다시 찬찬히 보니 이 브랜드의 가장 핵심 메시지는 뭐라고 느껴지나요?
- 당신의 일상에서 이 브랜드를 만나면 어떤 상황에서 마주칠 것 같나요?
- 비슷한 카테고리의 기존 브랜드와 비교해서 어떤가요?"""

    elif round_number == 3:
        return f"""[브랜드 기획 자료]
{seed_content}
{context}
이 브랜드에 대해 의심스럽거나 걱정되는 부분이 있나요?
- 신뢰도, 일관성, 가격대 추정, 오버 포지셔닝 등
- 솔직히 말해주세요."""

    else:
        return f"""[브랜드 기획 자료]
{seed_content}
{context}
종합해서 평가해주세요.
- 이 브랜드가 실제 시장에 나오면 당신이 실제로 이용할 가능성 (1~10점)
- 친구/지인에게 추천할 가능성 (1~10점)
- 두 점수를 그렇게 매긴 이유를 1~2문장으로."""
