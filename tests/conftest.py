import pytest

from legal_rag.retrieval import hybrid


@pytest.fixture(autouse=True)
def _clear_vec_cache() -> None:
    hybrid._CHUNK_VEC_CACHE.clear()
    yield
    hybrid._CHUNK_VEC_CACHE.clear()
