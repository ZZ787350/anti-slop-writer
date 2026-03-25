"""Unit tests for OpenAI-compatible HTTP provider.

Tests the HTTP layer including:
- Normal response parsing
- Error handling (401, 429, 5xx)
- Retry logic
- Timeout handling
- Malformed response handling
"""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from anti_slop_writer.providers.base import (
    AuthenticationError,
    MalformedResponseError,
    NetworkError,
    RateLimitError,
)
from anti_slop_writer.providers.config import ProviderConfig
from anti_slop_writer.providers.openai_compatible import OpenAICompatibleProvider


@pytest.fixture
def provider_config() -> ProviderConfig:
    """A valid ProviderConfig for testing."""
    return ProviderConfig(
        api_key="test-api-key-1234",
        endpoint="https://api.example.com/v1",
        model="gpt-4o-mini",
        timeout=10.0,
        max_retries=2,
    )


class TestOpenAICompatibleProviderInit:
    """Tests for provider initialization."""

    def test_init_with_valid_config(self, provider_config: ProviderConfig) -> None:
        """Provider initializes with valid config."""
        provider = OpenAICompatibleProvider(provider_config)
        assert provider._config is provider_config
        assert provider._client is None


class TestOpenAICompatibleProviderCall:
    """Tests for the call method."""

    @pytest.mark.asyncio
    async def test_call_successful_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Successful API call returns LLMResponse."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [
                    {
                        "message": {
                            "content": "This is the rewritten text."
                        }
                    }
                ],
                "model": "gpt-4o-mini",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="You are a helpful assistant.",
                user_prompt="Rewrite this text.",
            )

            assert response.content == "This is the rewritten text."
            assert response.model == "gpt-4o-mini"
            assert response.usage is not None
            assert response.usage["total_tokens"] == 30
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_401_raises_authentication_error(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """401 response raises AuthenticationError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"error": {"message": "Invalid API key"}},
            status_code=401,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(AuthenticationError):
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_429_retries_then_raises_rate_limit_error(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """429 response retries and eventually raises RateLimitError."""
        # Add multiple 429 responses (will exhaust retries)
        for _ in range(provider_config.max_retries + 1):
            httpx_mock.add_response(
                url="https://api.example.com/v1/chat/completions",
                method="POST",
                json={"error": {"message": "Rate limit exceeded"}},
                status_code=429,
            )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(RateLimitError):
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_429_retries_then_succeeds(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """429 response retries and succeeds on second attempt."""
        # First call: 429 rate limit
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"error": {"message": "Rate limit exceeded"}},
            status_code=429,
        )
        # Second call: success
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [{"message": {"content": "Success after retry"}}],
                "model": "gpt-4o-mini",
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )
            assert response.content == "Success after retry"
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_5xx_retries_then_raises_provider_error(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """5xx server errors retry and eventually raise ProviderError."""
        # Add multiple 500 responses (will exhaust retries)
        for _ in range(provider_config.max_retries + 1):
            httpx_mock.add_response(
                url="https://api.example.com/v1/chat/completions",
                method="POST",
                json={"error": {"message": "Internal server error"}},
                status_code=500,
            )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(Exception) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            # Should be a ProviderError with server error message
            assert "Server error" in str(exc_info.value) or "500" in str(exc_info.value)
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_5xx_retries_then_succeeds(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """5xx server errors retry and succeed on second attempt."""
        # First call: 500 server error
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"error": {"message": "Internal server error"}},
            status_code=500,
        )
        # Second call: success
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [{"message": {"content": "Success after server error"}}],
                "model": "gpt-4o-mini",
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )
            assert response.content == "Success after server error"
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_timeout_raises_network_error(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Timeout exception raises NetworkError after retries exhausted."""
        import httpx

        # Add timeout exceptions for all retry attempts
        for _ in range(provider_config.max_retries + 1):
            httpx_mock.add_exception(
                httpx.TimeoutException("Connection timed out"),
                url="https://api.example.com/v1/chat/completions",
            )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(NetworkError):
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_timeout_retries_and_succeeds(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Timeout retries and succeeds on second attempt."""
        import httpx

        # First call: timeout
        httpx_mock.add_exception(
            httpx.TimeoutException("Connection timed out"),
            url="https://api.example.com/v1/chat/completions",
        )
        # Second call: success
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [{"message": {"content": "Success after timeout"}}],
                "model": "gpt-4o-mini",
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )
            assert response.content == "Success after timeout"
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_call_connection_error_raises_network_error(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Connection error raises NetworkError after retries exhausted."""
        import httpx

        # Add exceptions for all retry attempts
        for _ in range(provider_config.max_retries + 1):
            httpx_mock.add_exception(
                httpx.ConnectError("Connection refused"),
                url="https://api.example.com/v1/chat/completions",
            )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(NetworkError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "Connection" in str(exc_info.value)
        finally:
            await provider.close()


class TestOpenAICompatibleProviderResponseParsing:
    """Tests for response parsing."""

    @pytest.mark.asyncio
    async def test_parse_json_failure_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Invalid JSON response raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            text="This is not valid JSON",
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "Failed to parse JSON" in str(exc_info.value)
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_missing_choices_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response missing 'choices' raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"model": "gpt-4o-mini"},  # Missing choices
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "choices" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_empty_choices_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response with empty choices array raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"choices": [], "model": "gpt-4o-mini"},
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            # Empty array is falsy, so it's caught as "missing"
            assert "choices" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_missing_message_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response missing 'message' in choices[0] raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"choices": [{}], "model": "gpt-4o-mini"},  # Missing message
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "message" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_missing_content_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response with None content raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            # message exists but content is explicitly None
            json={"choices": [{"message": {"content": None}}], "model": "gpt-4o-mini"},
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "content" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_empty_content_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response with empty/whitespace content raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"choices": [{"message": {"content": "   "}}], "model": "gpt-4o-mini"},
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "empty" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_non_string_content_raises_malformed_response(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response with non-string content raises MalformedResponseError."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={"choices": [{"message": {"content": 123}}], "model": "gpt-4o-mini"},
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            with pytest.raises(MalformedResponseError) as exc_info:
                await provider.call(
                    system_prompt="System prompt",
                    user_prompt="User prompt",
                )
            assert "string" in str(exc_info.value).lower()
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_response_without_usage(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response without usage field succeeds."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [{"message": {"content": "Response without usage"}}],
                "model": "gpt-4o-mini",
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )
            assert response.content == "Response without usage"
            assert response.usage is None
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_parse_response_uses_config_model_when_missing(
        self, provider_config: ProviderConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Response without model field uses config model."""
        httpx_mock.add_response(
            url="https://api.example.com/v1/chat/completions",
            method="POST",
            json={
                "choices": [{"message": {"content": "Response"}}],
                # Missing model field
            },
            status_code=200,
        )

        provider = OpenAICompatibleProvider(provider_config)
        try:
            response = await provider.call(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )
            assert response.model == provider_config.model
        finally:
            await provider.close()


class TestOpenAICompatibleProviderClose:
    """Tests for provider cleanup."""

    @pytest.mark.asyncio
    async def test_close_releases_client(self, provider_config: ProviderConfig) -> None:
        """Close method releases HTTP client resources."""
        provider = OpenAICompatibleProvider(provider_config)
        await provider.close()
        assert provider._client is None

    @pytest.mark.asyncio
    async def test_close_idempotent(self, provider_config: ProviderConfig) -> None:
        """Close method can be called multiple times safely."""
        provider = OpenAICompatibleProvider(provider_config)
        await provider.close()
        await provider.close()  # Should not raise
        assert provider._client is None
