from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    gemini_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_from: str
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()