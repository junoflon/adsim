"""
LLM 클라이언트 (Anthropic Claude SDK)
MiroFish의 모든 LLM 호출을 Claude로 처리
"""

import json
import random
import re
import time
from typing import Optional, Dict, Any, List
from anthropic import Anthropic, APIError, APIStatusError, RateLimitError, APIConnectionError

from ..config import Config


class LLMClient:
    """Claude LLM 클라이언트"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,  # kept for backward compatibility, ignored
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.model = model or Config.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("LLM_API_KEY가 설정되지 않았습니다 (.env 파일에서 ANTHROPIC API 키를 설정하세요)")

        # 타임아웃 60초로 제한 — 훅이 멈추지 않도록
        self.client = Anthropic(api_key=self.api_key, timeout=60.0)

    def _split_system_and_messages(
        self, messages: List[Dict[str, str]]
    ) -> tuple[Optional[str], List[Dict[str, str]]]:
        """
        OpenAI 형식 messages를 Claude 형식으로 변환
        - system 메시지는 별도 인자로
        - 나머지는 user/assistant 메시지로
        """
        system_parts = []
        chat_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            else:
                chat_messages.append({"role": role, "content": content})

        # Claude requires at least one user message
        if not chat_messages:
            chat_messages = [{"role": "user", "content": ""}]

        # Claude requires first message to be from user
        if chat_messages[0]["role"] != "user":
            chat_messages.insert(0, {"role": "user", "content": "."})

        system = "\n\n".join(system_parts) if system_parts else None
        return system, chat_messages

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        cache_system: bool = True,
    ) -> str:
        """
        채팅 요청

        Args:
            messages: 메시지 리스트 (OpenAI 형식)
            temperature: 온도
            max_tokens: 최대 토큰
            response_format: {"type": "json_object"} 형식 - JSON 응답 강제
            cache_system: 시스템 프롬프트를 prompt caching으로 감쌀지 (기본 True)
                          반복 호출에서 input 토큰 ~90% 절감 → rate limit 회피

        Returns:
            모델 응답 텍스트
        """
        system, chat_messages = self._split_system_and_messages(messages)

        # JSON 응답 모드: 시스템 프롬프트에 JSON 강제 지시 추가
        if response_format and response_format.get("type") == "json_object":
            json_instruction = (
                "\n\nIMPORTANT: You must respond with valid JSON only. "
                "Do not include any explanation, markdown formatting, or text outside the JSON object."
            )
            system = (system or "") + json_instruction

        # Prompt caching: system 프롬프트를 ephemeral cache로 감싼다 (5분 TTL).
        # 같은 에이전트의 여러 라운드가 동일 system을 공유하므로 90%+ 토큰 절감.
        if system and cache_system and len(system) > 500:  # 짧은 프롬프트는 캐시 오히려 오버헤드
            system_param = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }]
        else:
            system_param = system

        # 메시지 내 첫 user 메시지(보통 긴 시드 콘텐츠 포함)도 캐시 가능하도록 구성
        # 단, 마지막 메시지는 캐시하지 않음 (매번 다르기 때문)
        if cache_system and len(chat_messages) >= 2:
            processed = []
            for i, msg in enumerate(chat_messages):
                content = msg.get("content", "")
                # 첫 user 메시지(보통 시드 포함)만 캐시 대상 — 충분히 긴 경우
                if i == 0 and msg.get("role") == "user" and isinstance(content, str) and len(content) > 1500:
                    processed.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                        ],
                    })
                else:
                    processed.append(msg)
            chat_messages = processed

        kwargs = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_param:
            kwargs["system"] = system_param

        # 지수 백오프 재시도 (rate limit / transient 실패 대응)
        max_retries = 5
        last_err: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(**kwargs)
                content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text
                content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
                if not content:
                    raise ValueError("LLM 응답이 비어있습니다")
                return content
            except RateLimitError as e:
                last_err = e
                # Rate limit은 Anthropic 권장: 60초 기본, 지수 증가
                wait = min(75, 15 * (attempt + 1) + random.uniform(0, 3))
                time.sleep(wait)
            except APIConnectionError as e:
                last_err = e
                wait = min(30, (2 ** attempt) + random.uniform(0, 1.5))
                time.sleep(wait)
            except APIStatusError as e:
                last_err = e
                status = getattr(e, "status_code", None)
                if status == 429:
                    wait = min(75, 15 * (attempt + 1) + random.uniform(0, 3))
                    time.sleep(wait)
                elif status in (408, 500, 502, 503, 504):
                    wait = min(20, (2 ** attempt) + random.uniform(0, 1.5))
                    time.sleep(wait)
                else:
                    raise
            except APIError as e:
                last_err = e
                time.sleep(1 + attempt)
        # 모든 재시도 실패
        raise last_err if last_err else RuntimeError("LLM 호출이 여러 차례 실패했습니다")

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        JSON 응답 채팅 요청

        Args:
            messages: 메시지 리스트
            temperature: 온도
            max_tokens: 최대 토큰

        Returns:
            파싱된 JSON 객체
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # 마크다운 코드 블록 정리
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # 응답에서 JSON 부분만 추출 시도
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"LLM이 유효하지 않은 JSON을 반환했습니다: {cleaned[:200]}")
