"""Reciprocal Rank Fusion (RRF)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable


def reciprocal_rank_fusion(
    ranked_lists: list[list[Hashable]],
    k: int = 60,
) -> list[Hashable]:
    """
    Fuse multiple ordered candidate lists into a single ranking.
    score(d) = sum_i 1 / (k + rank_i(d)) for lists where d appears.
    """
    scores: dict[Hashable, float] = defaultdict(float)
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            scores[item] += 1.0 / (k + rank)
    return sorted(scores.keys(), key=lambda x: (-scores[x], str(x)))
