"""OpenAI-compatible LLM provider implementation.

This module provides an HTTP client for LLM APIs that follow the OpenAI
chat completions protocol (e.g., OpenAI, Azure OpenAI, Zhipu GLM).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from anti_slop_writer.providers.base import (
    AuthenticationError,
    BaseProvider,
    LLMResponse,
    MalformedResponseError,
    NetworkError,
    ProviderError,
    RateLimitError,
)
from anti_slop_writer.providers.config import ProviderConfig

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseProvider):
    """OpenAI-compatible HTTP provider for LLM API calls.

    This provider implements the OpenAI chat completions API protocol
    with retry logic, timeout handling, and proper error categorization.

    Attributes:
        config: Provider configuration including endpoint and credentials.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider with configuration.

        Args:
            config: Provider configuration.
        """
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client.

        Returns:
            httpx.AsyncClient instance.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._config.timeout, connect=10.0),
                follow_redirects=True,
            )
        return self._client

    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Make a call to the LLM API with retry logic.

        Args:
            system_prompt: System message content.
            user_prompt: User message content.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            LLMResponse containing the generated content.

        Raises:
            AuthenticationError: If API credentials are invalid.
            RateLimitError: If rate limited by the API.
            NetworkError: If network connection fails after retries.
            MalformedResponseError: If API returns malformed response.
            ProviderError: For other API errors.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        url = f"{self._config.endpoint}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            try:
                client = await self._get_client()

                logger.debug(
                    "Making API request",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self._config.max_retries,
                        "endpoint": self._config.endpoint,
                        "model": self._config.model,
                    },
                )

                start_time = time.monotonic()
                response = await client.post(url, json=payload, headers=headers)
                elapsed_ms = int((time.monotonic() - start_time) * 1000)

                # Handle HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError()

                if response.status_code == 429:
                    raise RateLimitError()

                if response.status_code >= 500:
                    # Server error - retry
                    last_error = ProviderError(
                        f"Server error: {response.status_code}"
                    )
                    if attempt < self._config.max_retries:
                        await self._backoff(attempt)
                        continue
                    raise last_error

                if response.status_code >= 400:
                    # Client error - don't retry
                    error_body = self._safe_error_body(response)
                    raise ProviderError(f"API error: {response.status_code} - {error_body}")

                # Parse response
                return self._parse_response(response, elapsed_ms)

            except AuthenticationError:
                raise
            except RateLimitError:
                # Retry rate limits with backoff
                if attempt < self._config.max_retries:
                    logger.warning("Rate limited, retrying...")
                    await self._backoff(attempt)
                    continue
                raise
            except httpx.TimeoutException as e:
                last_error = NetworkError(f"Request timed out: {e}")
                if attempt < self._config.max_retries:
                    logger.warning("Request timed out, retrying...")
                    await self._backoff(attempt)
                    continue
            except httpx.ConnectError as e:
                last_error = NetworkError(f"Connection failed: {e}")
                if attempt < self._config.max_retries:
                    logger.warning("Connection failed, retrying...")
                    await self._backoff(attempt)
                    continue
            except httpx.HTTPError as e:
                last_error = NetworkError(f"HTTP error: {e}")
                if attempt < self._config.max_retries:
                    logger.warning("HTTP error, retrying...")
                    await self._backoff(attempt)
                    continue

        # All retries exhausted
        if last_error:
            raise last_error
        raise NetworkError("Request failed after all retries")

    def _parse_response(self, response: httpx.Response, elapsed_ms: int) -> LLMResponse:
        """Parse the API response into an LLMResponse.

        Args:
            response: HTTP response object.
            elapsed_ms: Time taken for the request in milliseconds.

        Returns:
            LLMResponse with the parsed content.

        Raises:
            MalformedResponseError: If response structure is invalid.
        """
        try:
            data = response.json()
        except Exception as e:
            raise MalformedResponseError(f"Failed to parse JSON response: {e}") from e

        # Validate response structure per spec:
        # Response must have choices[0].message.content that is non-empty after stripping
        choices = data.get("choices")
        if not choices or not isinstance(choices, list):
            raise MalformedResponseError("Response missing 'choices' array")

        if len(choices) == 0:
            raise MalformedResponseError("Response 'choices' array is empty")

        choice = choices[0]
        if not isinstance(choice, dict):
            raise MalformedResponseError("Invalid 'choices' element type")

        message = choice.get("message")
        if not message or not isinstance(message, dict):
            raise MalformedResponseError("Response missing 'message' in choices[0]")

        content = message.get("content")
        if content is None:
            raise MalformedResponseError("Response missing 'content' in message")

        if not isinstance(content, str):
            raise MalformedResponseError("'content' must be a string")

        if not content.strip():
            raise MalformedResponseError("'content' is empty or whitespace only")

        model = data.get("model", self._config.model)
        usage = data.get("usage")

        logger.debug(
            "API response parsed",
            extra={
                "elapsed_ms": elapsed_ms,
                "model": model,
                "has_usage": usage is not None,
            },
        )

        return LLMResponse(
            content=content,
            model=model,
            usage=usage,
        )

    def _safe_error_body(self, response: httpx.Response) -> str:
        """Safely extract error body without exposing sensitive data.

        Args:
            response: HTTP response object.

        Returns:
            Sanitized error message.
        """
        try:
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                error = data["error"]
                if isinstance(error, dict) and "message" in error:
                    # Truncate and sanitize
                    msg = str(error["message"])[:200]
                    # Remove any potential API keys or tokens
                    return msg.replace(self._config.api_key, "***")
            return f"Status {response.status_code}"
        except Exception:
            return f"Status {response.status_code}"

    async def _backoff(self, attempt: int) -> None:
        """Exponential backoff for retries.

        Args:
            attempt: Current attempt number (0-indexed).
        """
        # Exponential backoff: 1s, 2s, 4s, ...
        delay = min(2**attempt, 10)  # Cap at 10 seconds
        logger.debug("Backing off for %s seconds", delay)
        await asyncio.sleep(delay)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
