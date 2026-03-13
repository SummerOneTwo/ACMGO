"""
LLM 提供商实现。

此包支持多个 LLM 提供商：
- Anthropic: 使用 Anthropic SDK 的 Claude 模型
- OpenAI: 使用 OpenAI SDK 的 GPT 模型
- LiteLLM: 使用 litellm.completion() 支持 100+ 提供商
"""

from .base import LLMProvider, Message, ToolCall, ToolDefinition
from .factory import create_provider, list_providers

# Lazy imports for optional providers
def __getattr__(name: str):
    if name == "AnthropicProvider":
        from .anthropic import AnthropicProvider
        return AnthropicProvider
    elif name == "OpenAIProvider":
        from .openai import OpenAIProvider
        return OpenAIProvider
    elif name == "LiteLLMProvider":
        from .litellm import LiteLLMProvider
        return LiteLLMProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "LLMProvider",
    "Message",
    "ToolCall",
    "ToolDefinition",
    "AnthropicProvider",
    "OpenAIProvider",
    "LiteLLMProvider",
    "create_provider",
    "list_providers",
]
