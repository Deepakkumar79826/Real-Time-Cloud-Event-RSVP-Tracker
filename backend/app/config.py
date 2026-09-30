from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./event_tracker.db"
    jwt_secret: str = "change-this-in-local-development"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 120
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    app_env: str = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
