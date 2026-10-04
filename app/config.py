from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    meta_verify_token: str
    meta_app_secret: str
    page_access_token: str
    graph_api_url: str = "https://graph.facebook.com/v26.0"

    # AI provider: "claude", "openai", or "gemini"
    ai_provider: str = "claude"
    # Leave empty to use each provider's default model
    ai_model: str = ""
    ai_system_prompt: str = "You are a helpful and friendly assistant."

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""


settings = Settings()
