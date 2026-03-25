"""Base class for LLM provider integrations.

This module defines the abstract interface for LLM providers that can be used
for text rewriting.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from anti_slop_writer.providers.config import ProviderConfig


@dataclass(frozen=True)
class LLMResponse:
    """Represents a response from an LLM provider.

    Attributes:
        content: The generated text content.
        model: The model used for generation.
        usage: Token usage information (prompt, completion, total).
    """

    content: str
    model: str
    usage: dict[str, int] | None = None


class BaseProvider(ABC):
    """Abstract base class for LLM provider integrations.

    Providers handle communication with LLM APIs and must implement
    the call method for making requests.

    Attributes:
        config: Provider configuration including endpoint and credentials.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider with configuration.

        Args:
            config: Provider configuration.
        """
        self._config = config

    @property
    def config(self) -> ProviderConfig:
        """Get the provider configuration."""
        return self._config

    @abstractmethod
    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Make a call to the LLM API.

        Args:
            system_prompt: System message content.
            user_prompt: User message content.
            temperature: Sampling temperature (0.0-2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            LLMResponse containing the generated content.

        Raises:
            ProviderError: If the API call fails after retries.
            AuthenticationError: If API credentials are invalid.
            NetworkError: If network connection fails.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the provider and release resources.

        Should be called when the provider is no longer needed.
        """
        ...

    async def __aenter__(self) -> BaseProvider:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()


class ProviderError(Exception):
    """Base exception for provider-related errors."""

    def __init__(self, message: str, *, exit_code: int = 5) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class AuthenticationError(ProviderError):
    """Error when API authentication fails."""

    def __init__(self, message: str = "Authentication failed. Check your API key.") -> None:
        super().__init__(message, exit_code=3)


class NetworkError(ProviderError):
    """Error when network connection fails."""

    def __init__(
        self, message: str = "Network error. Could not connect to API endpoint."
    ) -> None:
        super().__init__(message, exit_code=4)


class RateLimitError(ProviderError):
    """Error when rate limited by the API."""

    def __init__(
        self, message: str = "Rate limited. Please wait and try again."
    ) -> None:
        super().__init__(message, exit_code=3)


class MalformedResponseError(ProviderError):
    """Error when the API returns a malformed response."""

    def __init__(
        self, message: str = "Received malformed response from API."
    ) -> None:
        super().__init__(message, exit_code=5)
