"""
LiteLLM Provider implementation.

Uses litellm.completion() to support 100+ LLM providers and models.
https://docs.litellm.ai/
"""
import os
from typing import List, Dict, Any, Optional
from .base import LLMProvider, Message, ToolCall, ToolDefinition


class LiteLLMProvider(LLMProvider):
    """
    LiteLLM unified LLM provider.

    Supports 100+ providers including:
    - Anthropic: anthropic/claude-opus-4-6
    - OpenAI: openai/gpt-4o
    - Google: google/gemini-pro
    - Cohere: cohere/command-r
    - And many more...

    See https://docs.litellm.ai/ for full list of supported models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "anthropic/claude-opus-4-6",
        **kwargs
    ):
        """
        Initialize LiteLLM provider.

        Args:
            api_key: API key. If None, reads from environment variable based on model prefix.
                For example, anthropic/ models use ANTHROPIC_API_KEY.
                Can also use LITELLM_API_KEY as a fallback.
            model: Model name in litellm format (e.g., "anthropic/claude-opus-4-6").
            **kwargs: Additional litellm parameters (drop_params, etc.).
        """
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "LiteLLM provider requires 'litellm' package. "
                "Please install: uv pip install litellm"
            )

        # LiteLLM automatically handles API keys from environment variables
        # based on the model prefix (e.g., ANTHROPIC_API_KEY for anthropic/ models)
        if api_key:
            # Set the API key for the specific provider
            self._set_api_key_for_model(model, api_key)

        super().__init__(model)
        self.litellm = litellm
        self.litellm_params = kwargs

    def _set_api_key_for_model(self, model: str, api_key: str):
        """Set API key for the model's provider."""
        import litellm

        # Extract provider from model name (e.g., "anthropic/claude-opus-4-6" -> "anthropic")
        provider = model.split("/")[0].lower()

        # Map provider names to litellm's expected env var names
        env_var_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "cohere": "COHERE_API_KEY",
            "azure": "AZURE_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "huggingface": "HUGGING_FACE_API_KEY",
            "together": "TOGETHERAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "bedrock": "AWS_ACCESS_KEY_ID",
        }

        # Set the environment variable for the provider
        if provider in env_var_map:
            os.environ[env_var_map[provider]] = api_key
        else:
            # Fall back to generic litellm API key
            os.environ["LITELLM_API_KEY"] = api_key

    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request using litellm.completion().

        Args:
            messages: List of Message objects.
            tools: Optional list of ToolDefinition objects.
            **kwargs: Additional parameters (max_tokens, temperature, etc.).

        Returns:
            Dictionary with 'content' and optional 'tool_calls'.
        """
        # Convert messages to litellm format
        litellm_messages = self._convert_messages(messages)

        # Convert tools to litellm format
        litellm_tools = None
        if tools:
            litellm_tools = self._convert_tools(tools)

        # Set up parameters
        params = {
            "model": self.model,
            "messages": litellm_messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        if litellm_tools:
            params["tools"] = litellm_tools

        # Add optional parameters
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]

        # Add any litellm-specific parameters from initialization
        params.update(self.litellm_params)

        # Make the API call
        response = self.litellm.completion(**params)

        # Parse response
        result = {"content": "", "tool_calls": []}

        # Handle different response formats
        if hasattr(response, "choices"):
            # OpenAI-style response
            choice = response.choices[0]

            if hasattr(choice.message, "content") and choice.message.content:
                result["content"] = choice.message.content

            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    result["tool_calls"].append(
                        ToolCall(
                            name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                            id=tool_call.id,
                        )
                    )
        elif hasattr(response, "content"):
            # Anthropic-style response (list of content blocks)
            for block in response.content:
                if block.type == "text":
                    result["content"] += block.text
                elif block.type == "tool_use":
                    result["tool_calls"].append(
                        ToolCall(
                            name=block.name,
                            arguments=block.input,
                            id=block.id,
                        )
                    )

        # Add usage information if available
        if hasattr(response, "usage"):
            if hasattr(response.usage, "prompt_tokens"):
                result["usage"] = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                    if hasattr(response.usage, "completion_tokens")
                    else response.usage.output_tokens,
                }

        return result

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert Message objects to litellm format."""
        litellm_messages = []
        current_assistant_message = None

        for msg in messages:
            if msg.role == "system":
                litellm_messages.append({"role": "system", "content": msg.content})
            elif msg.role == "user":
                # Add any pending assistant message first
                if current_assistant_message:
                    litellm_messages.append(current_assistant_message)
                    current_assistant_message = None
                litellm_messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                # Check if this is a tool execution result (heuristic)
                if "工具执行结果" in msg.content or "文件已更新" in msg.content:
                    # This is a tool result, treat as user message
                    if current_assistant_message:
                        litellm_messages.append(current_assistant_message)
                        current_assistant_message = None
                    litellm_messages.append({"role": "user", "content": msg.content})
                else:
                    # Regular assistant response
                    if current_assistant_message:
                        litellm_messages.append(current_assistant_message)
                        current_assistant_message = None
                    current_assistant_message = {"role": "assistant", "content": msg.content}
            elif msg.role == "tool":
                # Tool result - needs tool_use_id
                if current_assistant_message:
                    litellm_messages.append(current_assistant_message)
                    current_assistant_message = None

                # Use Anthropic-style tool_result format
                litellm_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.tool_call_id,
                                "content": msg.content,
                            }
                        ],
                    }
                )

        # Add any pending assistant message
        if current_assistant_message:
            litellm_messages.append(current_assistant_message)

        return litellm_messages

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        """Convert ToolDefinition objects to litellm format."""
        litellm_tools = []

        for tool in tools:
            litellm_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": tool.parameters,
                            "required": list(tool.parameters.keys()),
                        },
                    },
                }
            )

        return litellm_tools

    def supports_tools(self) -> bool:
        """Most modern LLMs support tool calling."""
        return True
