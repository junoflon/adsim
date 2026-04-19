"""
A/B 비교 시뮬레이션 서비스
동일한 페르소나로 2개 광고안을 동시에 시뮬레이션하고 비교 보고서 생성
"""

import threading
import traceback
from typing import Dict, Any

from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..database.adsim_db import AdSimDB
from ..prompts.ad_comparison_prompt import create_comparison_prompt
from .ad_simulation_service import run_simulation

logger = get_logger("adsim.comparison")


def _wait_and_get_report(simulation_id: str, timeout_sec: int = 1800) -> Dict[str, Any]:
    """시뮬레이션 완료 대기 후 보고서 반환"""
    import time
    elapsed = 0
    interval = 3
    while elapsed < timeout_sec:
        sim = AdSimDB.get_simulation(simulation_id)
        if not sim:
            return None
        if sim["status"] == "completed":
            return AdSimDB.get_report(simulation_id)
        if sim["status"] == "failed":
            return None
        time.sleep(interval)
        elapsed += interval
    return None


def run_comparison(
    comparison_id: str,
    project_id: str,
    persona_config: Dict[str, Any],
    seed_a: Dict[str, Any],
    seed_b: Dict[str, Any],
    total_rounds: int = 4,
    agent_count: int = None,
) -> None:
    """
    A/B 비교 실행 (백그라운드 스레드)
    1. 두 시뮬레이션을 동시 실행
    2. 각 보고서 생성 대기
    3. LLM으로 비교 분석
    4. 비교 결과 저장
    """
    logger.info(f"A/B 비교 시작: {comparison_id}")

    try:
        AdSimDB.update_comparison(comparison_id, status="running")

        agents = agent_count or persona_config.get("agent_count", 30)

        # 1. 두 시뮬레이션 생성
        sim_a = AdSimDB.create_simulation(
            project_id=project_id,
            persona_config_id=persona_config["persona_id"],
            seed_id=seed_a["seed_id"],
            total_rounds=total_rounds,
        )
        sim_b = AdSimDB.create_simulation(
            project_id=project_id,
            persona_config_id=persona_config["persona_id"],
            seed_id=seed_b["seed_id"],
            total_rounds=total_rounds,
        )
        AdSimDB.update_comparison(
            comparison_id,
            simulation_a_id=sim_a["simulation_id"],
            simulation_b_id=sim_b["simulation_id"],
        )

        # 2. 병렬 실행
        t_a = threading.Thread(target=run_simulation, kwargs={
            "simulation_id": sim_a["simulation_id"],
            "seed_content": seed_a.get("content", "") or "",
            "persona_config": persona_config,
            "total_rounds": total_rounds,
            "agent_count": agents,
        }, daemon=True)
        t_b = threading.Thread(target=run_simulation, kwargs={
            "simulation_id": sim_b["simulation_id"],
            "seed_content": seed_b.get("content", "") or "",
            "persona_config": persona_config,
            "total_rounds": total_rounds,
            "agent_count": agents,
        }, daemon=True)
        t_a.start()
        t_b.start()
        t_a.join()
        t_b.join()

        # 3. 보고서 대기 & 수집
        report_a = _wait_and_get_report(sim_a["simulation_id"])
        report_b = _wait_and_get_report(sim_b["simulation_id"])

        if not report_a or not report_b:
            logger.error(f"보고서 생성 실패 A={bool(report_a)} B={bool(report_b)}")
            AdSimDB.update_comparison(comparison_id, status="failed")
            return

        # 4. LLM 비교 분석
        llm = LLMClient()
        prompt = create_comparison_prompt(
            seed_a_content=seed_a.get("content", "") or "",
            seed_b_content=seed_b.get("content", "") or "",
            persona_name=persona_config.get("name", "타겟"),
            report_a=report_a,
            report_b=report_b,
        )
        try:
            analysis = llm.chat_json(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000,
            )
        except Exception as e:
            logger.error(f"비교 분석 LLM 실패: {e}")
            # 폴백: 감정 점수 기반 단순 비교
            pa = report_a["overall_sentiment"].get("positive", 0)
            pb = report_b["overall_sentiment"].get("positive", 0)
            winner = "A" if pa > pb else ("B" if pb > pa else "tie")
            analysis = {
                "winner": winner,
                "winner_reason": f"긍정 비율 A={pa}% vs B={pb}%",
                "a_strengths": [], "a_weaknesses": [],
                "b_strengths": [], "b_weaknesses": [],
                "key_differences": ["자동 비교 분석 실패"],
                "recommendation": "LLM 비교 분석이 실패했습니다. 각 보고서를 개별 검토해주세요.",
            }

        # 감정 분포 요약 첨부
        analysis["sentiment_a"] = report_a["overall_sentiment"]
        analysis["sentiment_b"] = report_b["overall_sentiment"]

        AdSimDB.update_comparison(
            comparison_id,
            status="completed",
            comparison_result=analysis,
        )
        logger.info(f"A/B 비교 완료: {comparison_id}, winner={analysis.get('winner')}")

    except Exception as e:
        logger.error(f"A/B 비교 실패: {e}\n{traceback.format_exc()}")
        AdSimDB.update_comparison(comparison_id, status="failed")
