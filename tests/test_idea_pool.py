# -*- coding: utf-8 -*-
"""IdeaPool 단위 테스트."""
from __future__ import annotations

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from idea import IdeaPool


def test_empty():
    p = IdeaPool()
    assert len(p) == 0
    assert p.pick_one() is None


def test_add_str():
    p = IdeaPool()
    p.add("아이디어 하나")
    assert len(p) == 1
    assert p.pick_one() == "아이디어 하나"


def test_from_list():
    p = IdeaPool.from_list(["a", "b", "c"])
    assert len(p) == 3
    assert p.pick_one() in ("a", "b", "c")


def test_to_list():
    p = IdeaPool(["x", "y"])
    assert p.to_list() == ["x", "y"]


def test_pick_one_max_len():
    p = IdeaPool(["ab"])
    assert p.pick_one(max_len=1) == "a..."


def test_save_load():
    p = IdeaPool(["i1", "i2"])
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        assert p.save(path) is True
        p2 = IdeaPool()
        assert p2.load(path) is True
        assert p2.to_list() == ["i1", "i2"]
    finally:
        Path(path).unlink(missing_ok=True)


# ── v0.2: pick_weighted 테스트 ──────────────────────────────────────────

def test_pick_weighted_returns_text():
    """pick_weighted가 텍스트 반환."""
    p = IdeaPool()
    p.add("idea A", confidence=0.9, feasibility=0.9, novelty=0.9)
    p.add("idea B", confidence=0.1, feasibility=0.1, novelty=0.1)
    text = p.pick_weighted()
    assert text in ("idea A", "idea B")


def test_pick_weighted_return_entry():
    """return_entry=True 이면 (text, dict) 반환."""
    p = IdeaPool()
    p.add("entry X", confidence=0.8, feasibility=0.7, novelty=0.6)
    result = p.pick_weighted(return_entry=True)
    assert isinstance(result, tuple)
    text, entry = result
    assert text == "entry X"
    assert isinstance(entry, dict)
    assert entry.get("confidence") == 0.8


def test_pick_weighted_empty_returns_none():
    """빈 풀 → None (또는 (None, None))."""
    p = IdeaPool()
    assert p.pick_weighted() is None
    assert p.pick_weighted(return_entry=True) == (None, None)


def test_pick_weighted_no_metadata_fallback():
    """메타 없는 항목도 기본 가중치(0.375)로 선택 가능."""
    p = IdeaPool(["plain text"])
    text = p.pick_weighted()
    assert text == "plain text"


def test_pick_weighted_max_len():
    """max_len 적용."""
    p = IdeaPool()
    p.add("abcde", confidence=0.9, feasibility=0.9, novelty=0.9)
    text = p.pick_weighted(max_len=3)
    assert text == "abc..."


def test_pick_weighted_high_score_preferred():
    """고신뢰 아이디어가 저신뢰 아이디어보다 더 자주 선택됨 (통계 검증)."""
    import random as _r
    _r.seed(42)
    p = IdeaPool()
    p.add("high", confidence=1.0, feasibility=1.0, novelty=1.0)   # w = 2.0
    p.add("low",  confidence=0.01, feasibility=0.01, novelty=0.01) # w ≈ 0.0001
    counts = {"high": 0, "low": 0}
    for _ in range(200):
        t = p.pick_weighted()
        counts[t] = counts.get(t, 0) + 1
    # 고신뢰가 압도적으로 더 많이 선택
    assert counts["high"] > counts["low"] * 5
