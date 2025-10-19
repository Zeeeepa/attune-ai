"""
LLM Provider Adapters

Unified interface for different LLM providers (OpenAI, Anthropic, local models).

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any]


class BaseLLMProvider(ABC):
    """
    Base class for all LLM providers.

    Provides unified interface regardless of backend.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific options

        Returns:
            LLMResponse with standardized format
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model being used"""
        pass

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Rough approximation: ~4 chars per token
        """
        return len(text) // 4


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic (Claude) provider.

    Supports Claude 3 family models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.model = model

        # Lazy import to avoid requiring anthropic if not used
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API"""

        # Build kwargs for Anthropic
        api_kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system_prompt:
            api_kwargs["system"] = system_prompt

        # Add any additional kwargs
        api_kwargs.update(kwargs)

        # Call Anthropic API
        response = self.client.messages.create(**api_kwargs)

        # Convert to standardized format
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            metadata={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "provider": "anthropic"
            }
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model information"""
        model_info = {
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "cost_per_1m_input": 15.00,
                "cost_per_1m_output": 75.00
            },
            "claude-3-5-sonnet-20241022": {
                "max_tokens": 200000,
                "cost_per_1m_input": 3.00,
                "cost_per_1m_output": 15.00
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 200000,
                "cost_per_1m_input": 0.25,
                "cost_per_1m_output": 1.25
            }
        }

        return model_info.get(self.model, {
            "max_tokens": 200000,
            "cost_per_1m_input": 3.00,
            "cost_per_1m_output": 15.00
        })


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider.

    Supports GPT-4, GPT-3.5, and other OpenAI models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.model = model

        # Lazy import
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API"""

        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Convert to standardized format
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason,
            metadata={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "provider": "openai"
            }
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        model_info = {
            "gpt-4-turbo-preview": {
                "max_tokens": 128000,
                "cost_per_1m_input": 10.00,
                "cost_per_1m_output": 30.00
            },
            "gpt-4": {
                "max_tokens": 8192,
                "cost_per_1m_input": 30.00,
                "cost_per_1m_output": 60.00
            },
            "gpt-3.5-turbo": {
                "max_tokens": 16385,
                "cost_per_1m_input": 0.50,
                "cost_per_1m_output": 1.50
            }
        }

        return model_info.get(self.model, {
            "max_tokens": 128000,
            "cost_per_1m_input": 10.00,
            "cost_per_1m_output": 30.00
        })


class LocalProvider(BaseLLMProvider):
    """
    Local model provider (Ollama, LM Studio, etc.).

    For running models locally.
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model: str = "llama2",
        **kwargs
    ):
        super().__init__(api_key=None, **kwargs)
        self.endpoint = endpoint
        self.model = model

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> LLMResponse:
        """Generate response using local model"""
        import aiohttp

        # Format for Ollama-style API
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/chat",
                json=payload
            ) as response:
                result = await response.json()

                return LLMResponse(
                    content=result.get("message", {}).get("content", ""),
                    model=self.model,
                    tokens_used=result.get("eval_count", 0) + result.get("prompt_eval_count", 0),
                    finish_reason="stop",
                    metadata={
                        "provider": "local",
                        "endpoint": self.endpoint
                    }
                )

    def get_model_info(self) -> Dict[str, Any]:
        """Get local model information"""
        return {
            "max_tokens": 4096,  # Depends on model
            "cost_per_1m_input": 0.0,  # Free (local)
            "cost_per_1m_output": 0.0,
            "endpoint": self.endpoint
        }
