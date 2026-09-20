from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BuildSure AI"
    database_url: str = "sqlite:///./buildsure.db"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email_to: str = ""
    teams_webhook_url: str = ""
    slack_webhook_url: str = ""
    sms_api_key: str = ""

    critical_risk_score: int = 75
    escalation_severity: str = "critical"


@lru_cache
def get_settings() -> Settings:
    return Settings()
