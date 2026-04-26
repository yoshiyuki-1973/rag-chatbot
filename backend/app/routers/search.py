from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.models.schemas import SearchRequest, SearchResponse
from app.services.rag_service import RAGService
from app.settings import get_settings

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    top_k = request.top_k if request.top_k is not None else get_settings().top_k_default
    return await rag_service.search(
        query=request.query,
        top_k=top_k,
        min_similarity=request.min_similarity,
        min_authority_score=request.min_authority_score,
    )

