from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str
    title: str
    source_url: str
    organization: str | None = None
    authority_score: float = Field(ge=0, le=1)
    chunk_index: int = Field(ge=0)
    similarity: float = Field(ge=-1, le=1)


class SearchResult(Source):
    content: str


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    session_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    session_id: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int | None = Field(default=None, ge=1, le=20)
    min_similarity: float = Field(default=0.0, ge=-1, le=1)
    min_authority_score: float = Field(default=0.0, ge=0, le=1)


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]

