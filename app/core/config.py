from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mail Registry MVP"
    database_url: str = "sqlite:///./mail_registry.db"
    api_prefix: str = "/api/v1"
    poll_interval_minutes: int = 5

    nextcloud_root: str = "/Документооборот/Реестр писем"
    nextcloud_webdav_url: str = "http://nextcloud/remote.php/dav/files/service"
    nextcloud_username: str = "service"
    nextcloud_password: str = "service"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
