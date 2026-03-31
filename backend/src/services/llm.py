"""LLM 服务 - 支持 Ollama / OpenAI / DeepSeek / MiniMax"""

import json
from abc import ABC, abstractmethod
from typing import AsyncIterator

import httpx

from src.core.config import get_settings


class BaseLLMService(ABC):
    """LLM 服务抽象基类"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """同步生成（非流式）"""
        ...

    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式生成"""
        ...


class OllamaService(BaseLLMService):
    """Ollama 本地模型服务"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        """调用 Ollama /api/generate（非流式）"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs,
                },
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """调用 Ollama /api/generate（流式）"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    **kwargs,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token


class ChatCompletionsMixin(ABC):
    """Chat Completions API 混入类 - OpenAI/DeepSeek/MiniMax 共用"""

    base_url: str
    api_key: str
    model: str

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, prompt: str, stream: bool = False, **kwargs) -> dict:
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
            **kwargs,
        }

    async def _post(self, endpoint: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/{endpoint}",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def _stream_post(self, endpoint: str, payload: dict) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/{endpoint}",
                headers=self._get_headers(),
                json=payload,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line and line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content


class OpenAIService(ChatCompletionsMixin, BaseLLMService):
    """OpenAI API 服务"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str, **kwargs) -> str:
        """调用 OpenAI Chat Completions API（非流式）"""
        payload = self._build_payload(prompt, stream=False, **kwargs)
        data = await self._post("chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """调用 OpenAI Chat Completions API（流式）"""
        payload = self._build_payload(prompt, stream=True, **kwargs)
        async for token in self._stream_post("chat/completions", payload):
            yield token


class DeepSeekService(ChatCompletionsMixin, BaseLLMService):
    """DeepSeek API 服务"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str, **kwargs) -> str:
        """调用 DeepSeek Chat Completions API（非流式）"""
        payload = self._build_payload(prompt, stream=False, **kwargs)
        data = await self._post("chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """调用 DeepSeek Chat Completions API（流式）"""
        payload = self._build_payload(prompt, stream=True, **kwargs)
        async for token in self._stream_post("chat/completions", payload):
            yield token


class MiniMaxService(ChatCompletionsMixin, BaseLLMService):
    """MiniMax API 服务"""

    def __init__(
        self,
        api_key: str,
        model: str = "MiniMax-Text-01",
        base_url: str = "https://api.minimax.chat/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate(self, prompt: str, **kwargs) -> str:
        """调用 MiniMax Chat Completions API（非流式）"""
        payload = self._build_payload(prompt, stream=False, **kwargs)
        data = await self._post("text/chatcompletion_v2", payload)
        return data["choices"][0]["message"]["content"]

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """调用 MiniMax Chat Completions API（流式）"""
        payload = self._build_payload(prompt, stream=True, **kwargs)
        async for token in self._stream_post("text/chatcompletion_v2", payload):
            yield token


def get_llm_service() -> BaseLLMService:
    """根据配置获取 LLM 服务实例"""
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return OllamaService(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
        )
    elif settings.llm_provider == "openai":
        return OpenAIService(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    elif settings.llm_provider == "deepseek":
        return DeepSeekService(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    elif settings.llm_provider == "minimax":
        return MiniMaxService(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    else:
        # 默认使用 Ollama
        return OllamaService(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
        )
