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
