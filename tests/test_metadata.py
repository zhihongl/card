from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from legal_rag.metadata import Governed, touch, utc_now
from legal_rag.models import ManifestEntry


def test_governed_requires_system_user() -> None:
    with pytest.raises(ValidationError):
        Governed(system_user="")  # type: ignore[arg-type]


def test_manifest_entry_has_governance_fields() -> None:
    m = ManifestEntry(
        system_user="test:unit",
        source_url="https://www.supremecourt.vic.gov.au/areas/case-summaries/judgments",
        status="pending",
    )
    assert m.system_user == "test:unit"
    assert m.update_time.tzinfo is not None


def test_touch_updates_fields() -> None:
    past = datetime(2020, 1, 1, tzinfo=UTC)
    g = Governed(system_user="a", update_time=past)
    touch(g, "b")
    assert g.system_user == "b"
    assert g.update_time > past


def test_utc_now_is_aware() -> None:
    assert utc_now().tzinfo is not None
