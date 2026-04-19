"""
A/B 비교 보고서 프롬프트
두 광고안의 시뮬레이션 결과를 비교 분석
"""

from typing import Dict, List


def create_comparison_prompt(
    seed_a_content: str,
    seed_b_content: str,
    persona_name: str,
    report_a: Dict,
    report_b: Dict,
) -> str:
    """
    두 시뮬레이션 보고서를 비교해 우위안과 이유를 분석하는 프롬프트
    """
    sa = report_a.get("overall_sentiment", {})
    sb = report_b.get("overall_sentiment", {})

    def _fmt_list(items: List[str]) -> str:
        return "\n".join(f"- {x}" for x in items) if items else "(없음)"

    return f"""당신은 마케팅 분석 전문가입니다.
동일한 타겟 페르소나({persona_name})에 두 개의 광고안을 테스트한 결과를 비교 분석해주세요.

## 광고안 A
{seed_a_content}

## 광고안 B
{seed_b_content}

## A안 시뮬레이션 결과
- 긍정 {sa.get('positive', 0)}% / 중립 {sa.get('neutral', 0)}% / 부정 {sa.get('negative', 0)}%
- 핵심 인사이트:
{_fmt_list(report_a.get("key_insights", []))}
- 우려사항:
{_fmt_list(report_a.get("concerns", []))}

## B안 시뮬레이션 결과
- 긍정 {sb.get('positive', 0)}% / 중립 {sb.get('neutral', 0)}% / 부정 {sb.get('negative', 0)}%
- 핵심 인사이트:
{_fmt_list(report_b.get("key_insights", []))}
- 우려사항:
{_fmt_list(report_b.get("concerns", []))}

## 요청
두 광고안을 비교하여 다음 JSON 형식으로 답해주세요:
{{
  "winner": "A" | "B" | "tie",
  "winner_reason": "A/B 중 더 효과적인 안이 무엇이며 왜 그런지 2~3문장",
  "a_strengths": ["A안의 강점 2~3개"],
  "a_weaknesses": ["A안의 약점 2~3개"],
  "b_strengths": ["B안의 강점 2~3개"],
  "b_weaknesses": ["B안의 약점 2~3개"],
  "key_differences": ["두 안의 핵심 차이점 3~5개"],
  "recommendation": "종합 추천안을 3~4문장으로. 승자안의 개선점도 포함"
}}

판단 기준:
- 감정 분포(긍정 비율)와 핵심 인사이트의 질을 종합 고려
- 페르소나 적합성, 설득력, 우려 요소의 심각도
- 단순히 긍정 % 차이만 보지 말고, 우려사항의 중요도도 반영
"""
