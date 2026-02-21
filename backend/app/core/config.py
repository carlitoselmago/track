from pathlib import Path
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


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
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    server_reload: bool = False
    server_workers: int = 1
    # Legacy admin-only config file (kept for backwards compatibility)
    admin_config_file: Path = BASE_DIR / "config" / "admin.yaml"
    # Main runtime config file for admin bootstrap + smtp
    system_config_file: Path = BASE_DIR / "config" / "system.yaml"
    default_board_color: str = Field(default="#16A34A", pattern=r"^#[0-9A-Fa-f]{6}$")
    refresh_cookie_name: str = "track_refresh_token"
    admin_bootstrap_email: str = ""
    admin_bootstrap_password: str = ""
    admin_bootstrap_full_name: str = "System Admin"
    admin_reset_password_on_startup: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "noreply@track.local"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


def _apply_system_config(settings_obj: Settings) -> None:
    path = settings_obj.system_config_file
    if not path.exists():
        return
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    explicit = set(settings_obj.model_fields_set)

    admin = raw.get("admin") or {}
    if isinstance(admin, dict):
        if "admin_bootstrap_email" not in explicit and admin.get("email") is not None:
            settings_obj.admin_bootstrap_email = str(admin.get("email") or "").strip().lower()
        if "admin_bootstrap_password" not in explicit and admin.get("password") is not None:
            settings_obj.admin_bootstrap_password = str(admin.get("password") or "")
        if "admin_bootstrap_full_name" not in explicit and admin.get("full_name") is not None:
            settings_obj.admin_bootstrap_full_name = str(admin.get("full_name") or "").strip() or "System Admin"
        if "admin_reset_password_on_startup" not in explicit and admin.get("reset_password_on_startup") is not None:
            settings_obj.admin_reset_password_on_startup = bool(admin.get("reset_password_on_startup"))

    server = raw.get("server") or {}
    if isinstance(server, dict):
        if "server_host" not in explicit and server.get("host") is not None:
            settings_obj.server_host = str(server.get("host") or "").strip() or settings_obj.server_host
        if "server_port" not in explicit and server.get("port") is not None:
            settings_obj.server_port = int(server.get("port"))
        if "server_reload" not in explicit and server.get("reload") is not None:
            settings_obj.server_reload = bool(server.get("reload"))
        if "server_workers" not in explicit and server.get("workers") is not None:
            settings_obj.server_workers = int(server.get("workers"))

    smtp = raw.get("smtp") or {}
    if not isinstance(smtp, dict):
        return

    if "smtp_host" not in explicit and smtp.get("host") is not None:
        settings_obj.smtp_host = str(smtp.get("host") or "").strip()
    if "smtp_port" not in explicit and smtp.get("port") is not None:
        settings_obj.smtp_port = int(smtp.get("port"))
    if "smtp_username" not in explicit and smtp.get("username") is not None:
        settings_obj.smtp_username = str(smtp.get("username") or "").strip()
    if "smtp_password" not in explicit and smtp.get("password") is not None:
        settings_obj.smtp_password = str(smtp.get("password") or "")
    if "smtp_use_tls" not in explicit and smtp.get("use_tls") is not None:
        settings_obj.smtp_use_tls = bool(smtp.get("use_tls"))
    if "email_from" not in explicit and smtp.get("from_email") is not None:
        settings_obj.email_from = str(smtp.get("from_email") or "").strip()


def _apply_legacy_admin_config(settings_obj: Settings) -> None:
    if settings_obj.admin_bootstrap_email and settings_obj.admin_bootstrap_password:
        return

    path = settings_obj.admin_config_file
    if not path.exists():
        return

    logger = logging.getLogger("track.config")
    logger.warning(
        "Using legacy admin config file at %s. Move settings to %s.",
        path,
        settings_obj.system_config_file,
    )

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if raw.get("email") is not None:
        settings_obj.admin_bootstrap_email = str(raw.get("email") or "").strip().lower()
    if raw.get("password") is not None:
        settings_obj.admin_bootstrap_password = str(raw.get("password") or "")
    if raw.get("name") is not None:
        settings_obj.admin_bootstrap_full_name = str(raw.get("name") or "").strip() or "System Admin"
    if raw.get("reset_password_on_startup") is not None:
        settings_obj.admin_reset_password_on_startup = bool(raw.get("reset_password_on_startup"))


settings = Settings()
_apply_system_config(settings)
_apply_legacy_admin_config(settings)
