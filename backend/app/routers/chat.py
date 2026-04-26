from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.settings import get_settings

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    top_k = request.top_k if request.top_k is not None else get_settings().top_k_default
    return await rag_service.chat(request.query, request.session_id, top_k)

