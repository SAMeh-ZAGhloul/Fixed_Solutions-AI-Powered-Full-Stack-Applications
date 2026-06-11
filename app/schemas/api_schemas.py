from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    display_name: str
    role: str


class CurrentUser(BaseModel):
    id: str
    username: str
    display_name: str
    role: str


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    session_id: str


class DocumentItem(BaseModel):
    id: str
    original_name: str
    file_type: str
    chunk_count: int
    status: str
    uploaded_at: int
    indexed_at: int | None


class DocumentListResponse(BaseModel):
    documents: list[DocumentItem]
    total: int


class DocumentUploadResponse(BaseModel):
    document_id: str
    original_name: str
    file_type: str
    status: str
    message: str


class HealthComponent(BaseModel):
    status: str
    collection_count: int | None = None
    vector_count: int | None = None
    ping_ms: float | None = None


class HealthResponse(BaseModel):
    status: str
    components: dict[str, HealthComponent]
    version: str
