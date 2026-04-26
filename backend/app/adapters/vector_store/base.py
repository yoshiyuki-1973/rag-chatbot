from abc import ABC, abstractmethod

from app.models.schemas import SearchResult


class BaseVectorStore(ABC):
    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int,
        min_similarity: float = 0.0,
        min_authority_score: float = 0.0,
    ) -> list[SearchResult]:
        """Return similar document chunks."""

    @abstractmethod
    async def save_chat_history(
        self,
        session_id: str | None,
        query: str,
        response: str,
        sources: list[dict],
    ) -> None:
        """Persist a chat turn when a session id is provided."""

