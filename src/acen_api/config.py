"""애플리케이션 설정 정의."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """환경 변수에서 불러오는 핵심 설정."""

    app_name: str = "acen API"
    version: str = "0.1.0"
    database_url: str = "sqlite:///data/acen.db"
    log_level: str = "INFO"
    ui_enabled: bool = True
    api_key: str | None = None
    upload_max_bytes: int = 5 * 1024 * 1024
    upload_allowed_ext: str = "jpg,jpeg,png,webp"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
