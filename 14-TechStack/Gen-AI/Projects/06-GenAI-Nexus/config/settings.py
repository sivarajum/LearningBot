"""
GenAI Nexus — Central Configuration
Uses Pydantic Settings for type-safe, env-driven config.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- LLM ---
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    default_llm: str = Field(default="openai", alias="DEFAULT_LLM")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    claude_model: str = Field(default="claude-3-haiku-20240307", alias="CLAUDE_MODEL")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    # --- App ---
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    chroma_path: str = Field(default="./data/chroma_db", alias="CHROMA_PATH")
    knowledge_base_path: str = Field(
        default="./data/knowledge_base", alias="KNOWLEDGE_BASE_PATH"
    )

    # --- Embeddings ---
    embedding_model: str = Field(default="openai", alias="EMBEDDING_MODEL")

    # --- AWS ---
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field(default="us-east-1", alias="AWS_DEFAULT_REGION")
    aws_sagemaker_role: str = Field(default="", alias="AWS_SAGEMAKER_ROLE")

    # --- Local LLM (Ollama) ---
    use_local_llm: bool = Field(default=False, alias="USE_LOCAL_LLM")
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="llama3.1:8b", alias="OLLAMA_MODEL")
    ollama_code_model: str = Field(
        default="codellama:7b", alias="OLLAMA_CODE_MODEL"
    )
    ollama_fast_model: str = Field(
        default="llama3.2:3b", alias="OLLAMA_FAST_MODEL"
    )
    ollama_embed_model: str = Field(
        default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL"
    )

    # --- Training ---
    hf_model_id: str = Field(
        default="distilbert-base-uncased", alias="HF_MODEL_ID"
    )
    peft_base_model: str = Field(
        default="meta-llama/Llama-3.2-1B", alias="PEFT_BASE_MODEL"
    )
    quantize: bool = Field(default=False, alias="QUANTIZE")

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))

    @property
    def has_anthropic(self) -> bool:
        return bool(
            self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant-")
        )

    @property
    def has_google(self) -> bool:
        return bool(self.google_api_key and len(self.google_api_key) > 10)

    @property
    def has_aws(self) -> bool:
        return bool(self.aws_access_key_id and self.aws_secret_access_key)

    @property
    def has_local_llm(self) -> bool:
        """Check if local LLM (Ollama) is configured."""
        return self.use_local_llm


settings = Settings()
