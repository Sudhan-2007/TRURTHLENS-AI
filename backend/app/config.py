from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TruthLens AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "truthlens"
    MONGODB_PLACEHOLDER: str = "mongodb+srv://<user>:<password>@<cluster-url>"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_atlas_configured(self) -> bool:
        return "+srv://" in self.MONGODB_URI or self.MONGODB_URI == self.MONGODB_PLACEHOLDER

    @property
    def db_mode(self) -> str:
        return "atlas" if self.is_atlas_configured else "local"


settings = Settings()
