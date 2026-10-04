from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    meta_verify_token: str
    meta_app_secret: str
    page_access_token: str
    graph_api_url: str = "https://graph.facebook.com/v26.0"


settings = Settings()
