"""
LLM 클라이언트 (Anthropic Claude SDK)
MiroFish의 모든 LLM 호출을 Claude로 처리
"""

import json
import re
from typing import Optional, Dict, Any, List
from anthropic import Anthropic

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

        self.client = Anthropic(api_key=self.api_key)

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
    ) -> str:
        """
        채팅 요청

        Args:
            messages: 메시지 리스트 (OpenAI 형식)
            temperature: 온도
            max_tokens: 최대 토큰
            response_format: {"type": "json_object"} 형식 - JSON 응답 강제

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

        kwargs = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        # Extract text from response
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        # 일부 모델은 <think> 블록을 포함할 수 있음
        content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
        return content

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
