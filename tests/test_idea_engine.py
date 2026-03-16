# -*- coding: utf-8 -*-
"""IdeaEngine 단위 테스트."""
from __future__ import annotations


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from idea import IdeaPool, IdeaEngine


class _State:
    def __init__(self):
        self.step = 0
        self._ext = {}
    def get_extension(self, k, default=None):
        return self._ext.get(k, default)
    def set_extension(self, k, v):
        self._ext[k] = v


def test_orbit_deviation_creative_mode():
    s = _State()
    s._ext["creative_mode"] = True
    s._ext["idea_pool"] = ["idea A", "idea B"]
    eng = IdeaEngine(0.35, True)
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is True
    assert r["current_idea"] in ("idea A", "idea B")
    assert r["force_explore"] is True


def test_orbit_hold_high_regulation():
    s = _State()
    s._ext["creative_mode"] = False
    s._ext["self_regulation_signal"] = 0.8
    s._ext["idea_pool"] = ["x"]
    eng = IdeaEngine(0.35, True)
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is False
    assert r["current_idea"] is None
    assert r["force_explore"] is False


def test_orbit_deviation_low_regulation():
    s = _State()
    s._ext["self_regulation_signal"] = 0.2
    s._ext["idea_pool"] = ["only one"]
    eng = IdeaEngine(0.35, True)
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is True
    assert r["current_idea"] == "only one"
    assert r["force_explore"] is True


def test_composite_safety_blocks_when_warning_high():
    """복합 안전 조건: creative_mode 켜져도 warning_signal 높으면 이탈 비허용."""
    s = _State()
    s._ext["creative_mode"] = True
    s._ext["idea_pool"] = ["x"]
    s._ext["warning_signal"] = 0.9
    eng = IdeaEngine(0.35, True, use_composite_safety=True, safe_signal_threshold=0.5)
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is False
    assert r["current_idea"] is None
    assert r["force_explore"] is False


def test_composite_safety_allows_when_all_low():
    """복합 안전 조건: 모든 신호 낮으면 이탈 허용."""
    s = _State()
    s._ext["creative_mode"] = True
    s._ext["idea_pool"] = ["y"]
    s._ext["warning_signal"] = 0.2
    s._ext["self_defense_signal"] = 0.2
    s._ext["recursion_risk_signal"] = 0.2
    eng = IdeaEngine(0.35, True, use_composite_safety=True, safe_signal_threshold=0.5)
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is True
    assert r["current_idea"] == "y"
    assert r["force_explore"] is True
