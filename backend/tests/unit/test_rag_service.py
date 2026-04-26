import pytest
from fastapi import HTTPException

from app.models.schemas import SearchResult
from app.services.rag_service import RAGService


# ── フェイクオブジェクト ──────────────────────────────────────────────

class FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def _make_result(
    title: str = "FIFA サッカー競技規則",
    content: str = "オフサイドに関する説明",
) -> SearchResult:
    return SearchResult(
        document_id="550e8400-e29b-41d4-a716-446655440001",
        title=title,
        source_url="https://example.com/rules.pdf",
        organization="FIFA",
        authority_score=0.95,
        chunk_index=2,
        similarity=0.88,
        content=content,
    )


class FakeVectorStore:
    def __init__(self, results: list[SearchResult] | None = None):
        self.results: list[SearchResult] = results if results is not None else [_make_result()]
        self.last_top_k: int | None = None
        self.saved: dict | None = None

    async def search(
        self, query_embedding, top_k, min_similarity=0.0, min_authority_score=0.0
    ) -> list[SearchResult]:
        self.last_top_k = top_k
        return self.results

    async def save_chat_history(self, session_id, query, response, sources) -> None:
        self.saved = {
            "session_id": session_id,
            "query": query,
            "response": response,
            "sources": sources,
        }


class FailingHistoryVectorStore(FakeVectorStore):
    async def save_chat_history(self, session_id, query, response, sources) -> None:
        raise RuntimeError("history failed")


class FakeLLM:
    """呼び出し引数を記録するフェイク LLM（assert を含まない）"""

    def __init__(self, return_value: str = "コンテキストに基づく回答です。"):
        self.last_system_prompt = ""
        self.last_user_message = ""
        self.return_value = return_value

    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 1000, temperature: float = 0.1
    ) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        return self.return_value


class FailingEmbedder:
    async def embed(self, text: str) -> list[float]:
        raise RuntimeError("embedding failed")


class FailingLLM:
    async def generate(
        self, system_prompt: str, user_message: str, max_tokens: int = 1000, temperature: float = 0.1
    ) -> str:
        raise RuntimeError("llm failed")


# ── 既存テスト ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_returns_answer_and_sources():
    vector_store = FakeVectorStore()
    llm = FakeLLM()
    service = RAGService(FakeEmbedder(), vector_store, llm)

    response = await service.chat("オフサイドとは？", "session-1", 5)

    assert response.answer == "コンテキストに基づく回答です。"
    assert response.session_id == "session-1"
    assert response.sources[0].title == "FIFA サッカー競技規則"
    assert vector_store.saved["session_id"] == "session-1"
    # コンテキスト注入の検証はテスト本体で行う（FakeLLM 内 assert は排除済み）
    assert "オフサイドに関する説明" in llm.last_system_prompt
    assert llm.last_user_message == "オフサイドとは？"


@pytest.mark.asyncio
async def test_chat_returns_answer_when_history_save_fails():
    service = RAGService(FakeEmbedder(), FailingHistoryVectorStore(), FakeLLM())

    response = await service.chat("オフサイドとは？", "session-1", 5)

    assert response.answer == "コンテキストに基づく回答です。"
    assert response.sources[0].title == "FIFA サッカー競技規則"


@pytest.mark.asyncio
async def test_chat_wraps_search_errors():
    service = RAGService(FailingEmbedder(), FakeVectorStore(), FakeLLM())

    with pytest.raises(HTTPException) as exc_info:
        await service.chat("オフサイドとは？", "session-1", 5)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail["code"] == "SEARCH_ERROR"


@pytest.mark.asyncio
async def test_chat_wraps_llm_errors():
    service = RAGService(FakeEmbedder(), FakeVectorStore(), FailingLLM())

    with pytest.raises(HTTPException) as exc_info:
        await service.chat("オフサイドとは？", "session-1", 5)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail["code"] == "LLM_ERROR"


# ── RAG-02: 検索結果 0 件 ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_empty_search_results_returns_empty_sources():
    """RAG-02: 検索結果 0 件のとき sources は空リストで LLM にはコンテキスト空が渡される"""
    vector_store = FakeVectorStore(results=[])
    llm = FakeLLM()
    service = RAGService(FakeEmbedder(), vector_store, llm)

    response = await service.chat("存在しない質問", "session-1", 5)

    assert response.sources == []
    # _build_context が "" を返すためシステムプロンプトのコンテキスト部は空
    assert "コンテキスト:\n\n" in llm.last_system_prompt


# ── RAG-04: top_k パラメータ転送 ─────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_passes_top_k_to_vector_store():
    """RAG-04: chat に渡した top_k が VectorStore.search に正しく転送される"""
    vector_store = FakeVectorStore()
    service = RAGService(FakeEmbedder(), vector_store, FakeLLM())

    await service.chat("オフサイドとは？", None, top_k=3)

    assert vector_store.last_top_k == 3


# ── RAG-05: コンテキスト組み立て ─────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_builds_context_from_multiple_chunks():
    """RAG-05: 複数チャンクが取得された場合、全チャンクの本文と出典タイトルがプロンプトに含まれる"""
    results = [
        _make_result(title="ドキュメント A", content="Aの内容"),
        _make_result(title="ドキュメント B", content="Bの内容"),
    ]
    vector_store = FakeVectorStore(results=results)
    llm = FakeLLM()
    service = RAGService(FakeEmbedder(), vector_store, llm)

    await service.chat("テスト質問", "session-1", 5)

    assert "Aの内容" in llm.last_system_prompt
    assert "Bの内容" in llm.last_system_prompt
    assert "ドキュメント A" in llm.last_system_prompt
    assert "ドキュメント B" in llm.last_system_prompt
