from legal_rag.rag.citations import validate_citations


def test_validate_citations_good() -> None:
    ok, bad = validate_citations("Held that X applies [abc12345-1].", {"abc12345-1"})
    assert ok and not bad


def test_validate_citations_bad() -> None:
    ok, bad = validate_citations("Claim [fake-99].", {"real-1"})
    assert not ok and bad == {"fake-99"}
