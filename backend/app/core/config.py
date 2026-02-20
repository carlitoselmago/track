from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="TRACK_",
        case_sensitive=False,
    )

    app_name: str = "Track API"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 1
    database_url: str = "sqlite:///./data/track.db"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: Path = BASE_DIR / "data" / "uploads" / "cards"
    admin_config_file: Path = BASE_DIR / "config" / "admin.yaml"
    default_board_color: str = Field(default="#16A34A", pattern=r"^#[0-9A-Fa-f]{6}$")
    refresh_cookie_name: str = "track_refresh_token"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
