from legal_rag.ingestion.discover import extract_judgment_urls


def test_extract_judgment_urls_from_fixture() -> None:
    html = """
    <html><body>
    <a href="/areas/case-summaries/judgments/foo-v-bar-2024-vsc-1">Case</a>
    <a href="https://www.supremecourt.vic.gov.au/sites/default/files/2024-06/judgment-summary.pdf">PDF</a>
    <a href="https://evil.example.com/steal">bad</a>
    </body></html>
    """
    base = "https://www.supremecourt.vic.gov.au/areas/case-summaries/judgments"
    urls = extract_judgment_urls(html, base)
    assert any("foo-v-bar" in u for u in urls)
    assert any(u.endswith(".pdf") for u in urls)
    assert not any("evil.example" in u for u in urls)
