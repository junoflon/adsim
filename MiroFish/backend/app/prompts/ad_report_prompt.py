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
- 인사이트/우려/추천은 각 2~4개, 각 1문장 이내로 구체적으로
- full_report_text는 한국어로, 마케팅팀이 실제로 쓸 만한 수준으로
- 과장하지 말고 데이터에 근거해서 작성
- JSON 외 다른 텍스트는 절대 포함하지 말 것
"""
