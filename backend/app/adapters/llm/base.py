from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> str:
        """Return a single generated answer."""

    async def stream(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> AsyncIterator[str]:
        yield await self.generate(system_prompt, user_message, max_tokens, temperature)

