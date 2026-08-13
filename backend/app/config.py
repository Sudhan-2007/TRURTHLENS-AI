from typing import Literal

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_ENVIRONMENTS = ("development", "testing", "production")

ENVIRONMENT_DEFAULTS: dict[str, bool] = {
    "development": True,
    "testing": True,
    "production": False,
}


class Settings(BaseSettings):
    APP_NAME: str = "TruthLens AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool | None = None

    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        validation_alias=AliasChoices("MONGODB_URI", "DATABASE_URL"),
    )
    MONGODB_DB: str = "truthlens"
    MONGODB_PLACEHOLDER: str = "mongodb+srv://<user>:<password>@<cluster-url>"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:5173"

    AI_MODEL_PATH: str | None = None
    SOURCE_API_KEYS: str = ""

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

    @property
    def debug(self) -> bool:
        if self.DEBUG is not None:
            return self.DEBUG
        return ENVIRONMENT_DEFAULTS.get(self.ENVIRONMENT, True)

    @model_validator(mode="after")
    def _validate_environment(self) -> "Settings":
        if self.ENVIRONMENT not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                f"ENVIRONMENT must be one of {', '.join(ALLOWED_ENVIRONMENTS)}"
            )
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET == "change-me" or len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "JWT_SECRET must be set to a strong random value (>=32 chars) "
                    "in production"
                )
            if self.MONGODB_URI in ("", self.MONGODB_PLACEHOLDER, "mongodb://localhost:27017"):
                raise ValueError(
                    "DATABASE_URL must point at a real production database, not "
                    "a placeholder or a local instance"
                )
        return self

    @model_validator(mode="after")
    def _require_strong_secret_outside_debug(self) -> "Settings":
        if not self.debug and (
            self.JWT_SECRET == "change-me" or len(self.JWT_SECRET) < 32
        ):
            raise ValueError(
                "JWT_SECRET must be set to a strong random value (>=32 chars) "
                "when DEBUG is false"
            )
        return self


settings = Settings()
