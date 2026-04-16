"""
광고 반응 시뮬레이션 서비스
MiroFish의 LLMClient를 사용해 가상 소비자들이 광고에 반응하는 시뮬레이션 실행
"""

import concurrent.futures
import threading
import traceback
from typing import Dict, Any, List

from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..database.adsim_db import AdSimDB
from ..prompts.ad_consumer_persona import (
    create_ad_consumer_system_prompt,
    create_ad_evaluation_user_prompt,
    create_sentiment_analysis_prompt,
)
from .persona_manager import generate_agents

logger = get_logger("adsim.simulation")


def _run_single_agent(
    agent: Dict[str, Any],
    seed_content: str,
    total_rounds: int,
    llm: LLMClient,
) -> Dict[str, Any]:
    """
    단일 에이전트의 전체 라운드 실행

    Returns:
        {agent, conversation_log, sentiment, sentiment_score, key_reactions}
    """
    system_prompt = create_ad_consumer_system_prompt(agent)
    conversation_log = []
    previous_reactions = ""

    # 최대 4라운드로 제한 (프롬프트가 4개만 정의됨)
    rounds_to_run = min(total_rounds, 4)

    for round_num in range(1, rounds_to_run + 1):
        user_prompt = create_ad_evaluation_user_prompt(
            seed_content=seed_content,
            round_number=round_num,
            previous_reactions=previous_reactions if round_num > 1 else None,
        )

        # 이전 대화 이력도 함께 전달
        messages = [{"role": "system", "content": system_prompt}]
        # 이전 라운드 대화 포함
        for msg in conversation_log:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = llm.chat(
                messages=messages,
                temperature=0.8,
                max_tokens=400,
            )
        except Exception as e:
            logger.error(f"에이전트 {agent['name']} 라운드 {round_num} 실패: {e}")
            response = "(응답 실패)"

        conversation_log.append({
            "round": round_num,
            "role": "user",
            "content": user_prompt,
        })
        conversation_log.append({
            "round": round_num,
            "role": "assistant",
            "content": response,
        })

        # 다음 라운드를 위한 요약
        previous_reactions = response[:200]

    # 감정 분석
    sentiment_prompt = create_sentiment_analysis_prompt(conversation_log)
    try:
        sentiment_result = llm.chat_json(
            messages=[{"role": "user", "content": sentiment_prompt}],
            temperature=0.2,
            max_tokens=500,
        )
    except Exception as e:
        logger.error(f"에이전트 {agent['name']} 감정 분석 실패: {e}")
        sentiment_result = {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "key_reactions": ["분석 실패"],
        }

    return {
        "agent": agent,
        "conversation_log": conversation_log,
        "sentiment": sentiment_result.get("sentiment", "neutral"),
        "sentiment_score": float(sentiment_result.get("sentiment_score", 0.0)),
        "key_reactions": sentiment_result.get("key_reactions", []),
    }


def run_simulation(
    simulation_id: str,
    seed_content: str,
    persona_config: Dict[str, Any],
    total_rounds: int,
    agent_count: int,
    max_workers: int = 5,
) -> None:
    """
    시뮬레이션 실행 (백그라운드 스레드에서 호출)

    1. N명의 다양한 에이전트 생성
    2. 각 에이전트가 광고에 반응 (병렬)
    3. 결과를 DB에 저장
    4. 상태 업데이트
    """
    logger.info(f"시뮬레이션 시작: {simulation_id}, agents={agent_count}, rounds={total_rounds}")

    try:
        AdSimDB.update_simulation_status(simulation_id, "running", current_round=0)

        # 1. 에이전트 생성
        agents = generate_agents(persona_config, agent_count)
        logger.info(f"{len(agents)}명의 에이전트 생성됨")

        # 2. LLM 클라이언트
        llm = LLMClient()

        # 3. 병렬 실행 (max_workers만큼 동시에)
        completed = 0
        lock = threading.Lock()

        def task(agent):
            nonlocal completed
            result = _run_single_agent(agent, seed_content, total_rounds, llm)
            with lock:
                completed += 1
                # DB 저장
                AdSimDB.save_agent_response(
                    simulation_id=simulation_id,
                    agent_id=agent["agent_id"],
                    agent_name=agent["name"],
                    agent_persona=agent,
                    sentiment=result["sentiment"],
                    sentiment_score=result["sentiment_score"],
                    key_reactions=result["key_reactions"],
                    conversation_log=result["conversation_log"],
                )
                # 진행률 업데이트
                progress_round = min(total_rounds, round(completed / len(agents) * total_rounds))
                AdSimDB.update_simulation_status(
                    simulation_id, "running", current_round=progress_round
                )
                logger.info(f"진행: {completed}/{len(agents)} - {agent['name']} 완료")
            return result

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(task, agent) for agent in agents]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"에이전트 처리 실패: {e}")

        # 4. 완료 처리
        AdSimDB.update_simulation_status(
            simulation_id, "completed", current_round=total_rounds
        )
        logger.info(f"시뮬레이션 완료: {simulation_id}")

        # 5. 보고서 생성 (import 지연: 순환 참조 방지)
        from .ad_report_service import generate_report
        generate_report(simulation_id, seed_content, persona_config.get("name", "타겟"))

    except Exception as e:
        logger.error(f"시뮬레이션 실패: {e}\n{traceback.format_exc()}")
        AdSimDB.update_simulation_status(simulation_id, "failed")
