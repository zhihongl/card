from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "legal-rag"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    opensearch_url: str | None = Field(default=None, alias="OPENSEARCH_URL")
    opensearch_index: str = Field(default="legal_chunks", alias="OPENSEARCH_INDEX")

    data_dir: str = Field(default="data", alias="LEGAL_RAG_DATA_DIR")
    rrf_k: int = Field(default=60, alias="RRF_K")
    top_k_semantic: int = Field(default=8, alias="TOP_K_SEMANTIC")
    top_k_keyword: int = Field(default=8, alias="TOP_K_KEYWORD")
    embedding_dimensions: int = Field(default=8, alias="LEGAL_RAG_MOCK_EMBEDDING_DIM")

    judgments_list_url: str = Field(
        default="https://www.supremecourt.vic.gov.au/areas/case-summaries/judgments",
        alias="JUDGMENTS_LIST_URL",
    )
    max_ingest_documents: int = Field(default=50, alias="MAX_INGEST_DOCUMENTS")
    max_listing_pages: int = Field(default=15, alias="MAX_LISTING_PAGES")


@lru_cache
def get_settings() -> Settings:
    return Settings()
