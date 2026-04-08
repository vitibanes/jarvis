from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JARVIS"
    environment: str = "development"
    database_url: str = "sqlite:///./jarvis.db"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""
    primary_model: str = "openrouter/auto"
    secondary_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    tertiary_model: str = "mistralai/mistral-7b-instruct:free"
    max_requests_per_minute: int = 20
    max_requests_per_day: int = 400
    max_retries: int = 3
    max_steps_per_task: int = 6
    max_llm_calls_per_task: int = 4
    max_planning_depth: int = 2
    request_timeout_seconds: int = 30
    command_allowlist: list[str] = Field(default_factory=lambda: ["python", "echo", "pwd", "ls"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
