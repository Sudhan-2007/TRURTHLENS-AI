from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNVERIFIED = "UNVERIFIED"


class SourceType(str, Enum):
    OFFICIAL = "official"
    FACT_CHECK = "fact_check"
    REPUTABLE_NEWS = "reputable_news"


class TrustLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"


class SourceStatus(str, Enum):
    TRUSTED = "trusted"
    PENDING_REVIEW = "pending_review"
    BLOCKED = "blocked"


class VerificationMethod(str, Enum):
    MANUAL = "manual"
    DOMAIN_VERIFIED = "domain_verified"
    API = "api"


class SourceRegister(BaseModel):
    name: str
    domain: str
    category: str
    country: str = "US"
    source_type: SourceType = SourceType.OFFICIAL
    trust_level: TrustLevel = TrustLevel.HIGH
    verification_method: VerificationMethod = VerificationMethod.MANUAL

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Source name is required")
        return value

    @field_validator("domain")
    @classmethod
    def check_domain(cls, value: str) -> str:
        value = value.strip().lower()
        if not value or "." not in value:
            raise ValueError("Domain must be a valid domain such as example.gov")
        return value
