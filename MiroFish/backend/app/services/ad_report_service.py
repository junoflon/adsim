"""
광고 분석 보고서 서비스
시뮬레이션 결과를 종합해서 마케팅 분석 보고서 생성
"""

import traceback
from collections import Counter
from typing import Dict, Any

from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..database.adsim_db import AdSimDB
from ..prompts.ad_report_prompt import create_report_prompt

logger = get_logger("adsim.report")


def generate_report(
    simulation_id: str,
    seed_content: str,
    persona_name: str,
) -> Dict[str, Any]:
    """
    시뮬레이션 결과 기반 분석 보고서 생성

    Args:
        simulation_id: 시뮬레이션 ID
        seed_content: 분석 대상 광고 내용
        persona_name: 타겟 페르소나 이름
    """
    logger.info(f"보고서 생성 시작: {simulation_id}")

    try:
        # 에이전트 반응 수집
        responses = AdSimDB.list_responses(simulation_id)
        if not responses:
            logger.warning(f"응답이 없음: {simulation_id}")
            return None

        # 감정 분포 계산
        sentiment_counts = Counter(r["sentiment"] for r in responses)
        total = len(responses)
        overall_sentiment = {
            "positive": round(sentiment_counts.get("positive", 0) / total * 100),
            "neutral": round(sentiment_counts.get("neutral", 0) / total * 100),
            "negative": round(sentiment_counts.get("negative", 0) / total * 100),
        }
        # 합계 100 맞추기 (반올림 오차)
        diff = 100 - sum(overall_sentiment.values())
        if diff != 0:
            max_key = max(overall_sentiment, key=overall_sentiment.get)
            overall_sentiment[max_key] += diff

        # LLM에 분석 요청
        llm = LLMClient()
        prompt = create_report_prompt(
            seed_content=seed_content,
            persona_name=persona_name,
            agent_responses=responses,
            sentiment_counts=dict(sentiment_counts),
        )

        try:
            analysis = llm.chat_json(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000,
            )
        except Exception as e:
            logger.error(f"LLM 분석 실패: {e}")
            # 폴백: LLM 분석 실패 시 기본 보고서
            analysis = {
                "key_insights": [f"{total}명 중 {sentiment_counts.get('positive', 0)}명이 긍정 반응"],
                "concerns": ["자동 분석 실패 - 수동 검토 권장"],
                "recommendations": ["시뮬레이션을 재실행해주세요"],
                "full_report_text": f"시뮬레이션 완료: 긍정 {overall_sentiment['positive']}%, 중립 {overall_sentiment['neutral']}%, 부정 {overall_sentiment['negative']}%",
            }

        # DB 저장
        report = AdSimDB.save_report(
            simulation_id=simulation_id,
            overall_sentiment=overall_sentiment,
            key_insights=analysis.get("key_insights", []),
            concerns=analysis.get("concerns", []),
            recommendations=analysis.get("recommendations", []),
            full_report_text=analysis.get("full_report_text", ""),
            script_analysis=analysis.get("script_analysis"),
        )

        logger.info(f"보고서 생성 완료: {report['report_id']}")
        return report

    except Exception as e:
        logger.error(f"보고서 생성 실패: {e}\n{traceback.format_exc()}")
        return None
