from legal_rag.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_deterministic() -> None:
    a = ["x", "y", "z"]
    b = ["y", "z", "w"]
    fused = reciprocal_rank_fusion([a, b], k=60)
    fused2 = reciprocal_rank_fusion([a, b], k=60)
    assert fused == fused2
    assert set(fused) == {"x", "y", "z", "w"}
