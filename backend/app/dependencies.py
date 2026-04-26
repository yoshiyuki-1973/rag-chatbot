from fastapi import Request

from app.adapters.vector_store.supabase import SupabaseVectorStore
from app.services.rag_service import RAGService


def get_rag_service(request: Request) -> RAGService:
    return RAGService(
        embedder=request.app.state.embedder,
        vector_store=SupabaseVectorStore(request.app.state.db_pool),
        llm=request.app.state.llm,
    )
