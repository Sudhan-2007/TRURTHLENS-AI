from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from ..utils.validators import validate_text, validate_url


class InputType(str, Enum):
    TEXT = "text"
    URL = "url"


class NewsStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NewsSubmitText(BaseModel):
    input_type: Literal["text"] = "text"
    content: str

    @field_validator("content")
    @classmethod
    def check_text(cls, value: str) -> str:
        return validate_text(value)


class NewsSubmitUrl(BaseModel):
    input_type: Literal["url"] = "url"
    url: str

    @field_validator("url")
    @classmethod
    def check_url(cls, value: str) -> str:
        return validate_url(value)


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: str
    input_type: InputType
    content: str | None = None
    url: str | None = None
    title: str | None = None
    source_name: str | None = None
    language: str = "en"
    status: NewsStatus
    verification_result: dict | None = None
    created_at: datetime
    updated_at: datetime
