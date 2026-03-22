"""Mandatory governance fields for persisted records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class Governed(BaseModel):
    """Every created/updated governed row must carry these fields."""

    system_user: str = Field(..., min_length=1, description="Service principal or operator id")
    update_time: datetime = Field(default_factory=utc_now)

    @field_validator("update_time", mode="before")
    @classmethod
    def ensure_tz(cls, v: Any) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v


def touch(record: Governed, system_user: str) -> None:
    """Update audit fields for an in-memory model before persistence."""
    record.system_user = system_user
    record.update_time = utc_now()
