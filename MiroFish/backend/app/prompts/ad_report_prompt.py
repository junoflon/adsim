"""
광고 분석 보고서 프롬프트
시뮬레이션 결과를 종합해서 마케팅 보고서를 생성
"""

from typing import Dict, Any, List


def create_report_prompt(
    seed_content: str,
    persona_name: str,
    agent_responses: List[Dict[str, Any]],
    sentiment_counts: Dict[str, int]
) -> str:
    """
    시뮬레이션 결과 종합 분석 보고서 생성 프롬프트
    """
    total = sum(sentiment_counts.values())
    positive_pct = round(sentiment_counts.get("positive", 0) / total * 100) if total > 0 else 0
    negative_pct = round(sentiment_counts.get("negative", 0) / total * 100) if total > 0 else 0
    neutral_pct = round(sentiment_counts.get("neutral", 0) / total * 100) if total > 0 else 0

    # 상위 반응 샘플 (긍정/부정 각 3개씩)
    positive_samples = [r for r in agent_responses if r.get("sentiment") == "positive"][:3]
    negative_samples = [r for r in agent_responses if r.get("sentiment") == "negative"][:3]

    samples_text = "\n\n".join([
        f"[{r['agent_name']} - {r['sentiment']}]\n" + ", ".join(r.get("key_reactions", []))
        for r in (positive_samples + negative_samples)
    ])

    return f"""당신은 한국 시장의 마케팅 분석 전문가입니다.

## 분석 대상 광고
{seed_content[:1500]}

## 시뮬레이션 개요
- 타겟 페르소나: {persona_name}
- 가상 소비자 수: {total}명
- 긍정 반응: {sentiment_counts.get('positive', 0)}명 ({positive_pct}%)
- 중립 반응: {sentiment_counts.get('neutral', 0)}명 ({neutral_pct}%)
- 부정 반응: {sentiment_counts.get('negative', 0)}명 ({negative_pct}%)

## 주요 반응 샘플
{samples_text}

## 분석 요구사항
위 데이터를 바탕으로 실제 마케팅 팀이 활용할 수 있는 분석 보고서를 작성하세요.
반드시 다음 JSON 형식으로 응답하세요:

{{
  "script_analysis": {{
    "hook_strength": "훅(첫 3초) 강도 평가 1~2문장. 몇 초 안에 주의를 잡는 요소가 있는지, 없는지.",
    "core_message": "이 대본의 핵심 메시지 1문장. 소비자가 떠올리는 '결국 뭘 말하려는 광고'.",
    "tone": "톤/스타일 키워드 2~4개 (예: '감성적', '자극적', '교훈형', '유머', '정보형', '공포 소구', '셀럽 의존적' 등)",
    "strengths": ["대본 자체의 장점 2~3개. 반응과 별개로 대본 구성상의 강점"],
    "weaknesses": ["대본 자체의 약점 2~3개. 메시지/구성/표현에서 개선 여지"],
    "platform_fit": "이 대본이 잘 맞을 것 같은 매체와 안 맞을 것 같은 매체를 각각 이유와 함께 2~3문장",
    "risks": ["잠재적 리스크 1~3개. 규제·표현·타겟 반감 등 운영상 주의점. 없으면 빈 배열."]
  }},
  "key_insights": [
    "인사이트 1 (소비자들이 공통으로 느낀 것)",
    "인사이트 2",
    "인사이트 3"
  ],
  "concerns": [
    "우려사항 1 (개선이 필요한 부분)",
    "우려사항 2"
  ],
  "recommendations": [
    "추천사항 1 (구체적인 개선 방안)",
    "추천사항 2",
    "추천사항 3"
  ],
  "full_report_text": "## 종합 분석\\n\\n[2~3단락의 마크다운 서술형 보고서. 긍정 요인, 부정 요인, 개선 방향을 자연스럽게 연결]"
}}

주의사항:
- script_analysis는 **대본 자체**의 구성을 평가 (에이전트 반응과 별개의 관점). 반응이 부정적이어도 대본에 강점이 있으면 강점으로 기록.
- 인사이트/우려/추천은 각 2~4개, 각 1문장 이내로 구체적으로
- full_report_text는 한국어로, 마케팅팀이 실제로 쓸 만한 수준으로
- 과장하지 말고 데이터에 근거해서 작성. 반응이 다 부정적이어도 대본에 냉정하게 좋은 점이 있으면 그것도 짚으세요.
- JSON 외 다른 텍스트는 절대 포함하지 말 것
"""
