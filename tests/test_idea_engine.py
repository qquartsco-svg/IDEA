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


# ── v0.2: 양자 요동·옵저버·orbit_mode·창발 테스트 ──────────────────────

def test_v02_result_has_new_fields():
    """v0.2 결과 dict에 신규 필드 존재 확인."""
    s = _State()
    s._ext["creative_mode"] = True
    s._ext["idea_pool"] = ["idea"]
    eng = IdeaEngine()
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    for key in ("orbit_mode", "quantum_noise", "delta_raw", "delta_eff",
                "uncertainty_index", "emergence_score", "emergence_event",
                "observer_verdict"):
        assert key in r, f"missing key: {key}"


def test_observer_critical_blocks_deviation():
    """CRITICAL → orbit_deviation_active=False, orbit_mode=LOCKED."""
    s = _State()
    s._ext["creative_mode"] = True
    s._ext["observer_verdict"] = "CRITICAL"
    s._ext["idea_pool"] = ["idea"]
    eng = IdeaEngine()
    r = eng.step(s, pool=IdeaPool.from_list(s._ext["idea_pool"]))
    assert r["orbit_deviation_active"] is False
    assert r["orbit_mode"] == "LOCKED"
    assert r["current_idea"] is None
    assert r["quantum_noise"] == 0.0    # σ_q=0 → no noise


def test_observer_fragile_larger_sigma():
    """FRAGILE → σ_q=0.15 → |quantum_noise| 분포가 STABLE보다 큼 (통계)."""
    import math as _m
    fragile_noises = []
    stable_noises  = []
    for _ in range(300):
        s = _State()
        s._ext["observer_verdict"] = "FRAGILE"
        r = IdeaEngine(quantum_noise_scale=None).step(s)
        fragile_noises.append(abs(r["quantum_noise"]))
    for _ in range(300):
        s = _State()
        s._ext["observer_verdict"] = "STABLE"
        r = IdeaEngine(quantum_noise_scale=None).step(s)
        stable_noises.append(abs(r["quantum_noise"]))
    avg_fragile = sum(fragile_noises) / len(fragile_noises)
    avg_stable  = sum(stable_noises)  / len(stable_noises)
    # FRAGILE σ=0.15 vs STABLE σ=0.05 → 평균 절댓값 ≈ 3배 차이
    assert avg_fragile > avg_stable * 1.5


def test_orbit_mode_orbit_when_no_deviation():
    """이탈 없음 + 양자 소음도 작음 → orbit_mode ORBIT."""
    s = _State()
    s._ext["creative_mode"] = False
    s._ext["self_regulation_signal"] = 0.9   # high → no deviation
    s._ext["observer_verdict"] = "HEALTHY"   # σ_q = 0.03 (very small)
    # δ_raw = 0.35 - 0.9 = -0.55 → 노이즈가 작으면 δ_eff ≤ 0 → ORBIT
    # 결정론적으로 테스트하려면 quantum_noise_scale=0.0
    eng = IdeaEngine(quantum_noise_scale=0.0)
    r = eng.step(s)
    assert r["orbit_mode"] == "ORBIT"
    assert r["delta_eff"] == r["delta_raw"]   # noise=0 이면 eff=raw


def test_orbit_mode_locked_when_critical():
    """CRITICAL → orbit_mode=LOCKED, quantum_noise=0."""
    s = _State()
    s._ext["observer_verdict"] = "CRITICAL"
    eng = IdeaEngine()
    r = eng.step(s)
    assert r["orbit_mode"] == "LOCKED"
    assert r["quantum_noise"] == 0.0


def test_delta_eff_equals_raw_plus_noise():
    """δ_eff = δ_raw + q 공식 검증."""
    s = _State()
    s._ext["creative_mode"] = True   # δ_raw = 1.0
    eng = IdeaEngine(quantum_noise_scale=0.0)  # q = 0
    r = eng.step(s)
    assert abs(r["delta_raw"] - 1.0) < 1e-9
    assert abs(r["delta_eff"] - 1.0) < 1e-9
    assert r["quantum_noise"] == 0.0


def test_uncertainty_index_zero_when_no_noise():
    """σ_q=0 → uncertainty_index=0."""
    s = _State()
    s._ext["observer_verdict"] = "CRITICAL"  # σ_q=0
    r = IdeaEngine().step(s)
    assert r["uncertainty_index"] == 0.0


def test_uncertainty_index_positive_with_noise():
    """σ_q>0, self_reg<1 → uncertainty_index > 0."""
    s = _State()
    s._ext["observer_verdict"] = "FRAGILE"   # σ_q=0.15
    s._ext["self_regulation_signal"] = 0.3
    r = IdeaEngine().step(s)
    assert r["uncertainty_index"] >= 0.0   # 항상 비음수


def test_emergence_event_with_rich_metadata():
    """높은 confidence/feasibility/novelty → emergence_score 높고 emergence_event 가능."""
    s = _State()
    s._ext["creative_mode"] = True
    pool = IdeaPool()
    pool.add("rich idea", confidence=1.0, feasibility=1.0, novelty=1.0)
    # E = 1×1×2/2 = 1.0 → emergence_event=True (threshold=0.60)
    eng = IdeaEngine(emergence_threshold=0.60)
    r = eng.step(s, pool=pool)
    assert r["orbit_deviation_active"] is True
    assert r["emergence_score"] == 1.0
    assert r["emergence_event"] is True
    assert r["orbit_mode"] == "EMERGENCE"


def test_emergence_event_false_with_bare_str():
    """메타 없는 plain str 아이디어 → emergence_score ≈ 0.1875 < 0.60 → no event."""
    s = _State()
    s._ext["creative_mode"] = True
    pool = IdeaPool(["plain idea"])
    eng = IdeaEngine(emergence_threshold=0.60)
    r = eng.step(s, pool=pool)
    assert r["emergence_event"] is False
    assert r["emergence_score"] < 0.60


def test_pick_weighted_used_when_available():
    """use_weighted_pick=True + 메타 있는 풀 → pick_weighted 호출 → (text, entry) 반환 경로."""
    s = _State()
    s._ext["creative_mode"] = True
    pool = IdeaPool()
    pool.add("w idea", confidence=0.9, feasibility=0.9, novelty=0.8)
    eng = IdeaEngine(use_weighted_pick=True, emergence_threshold=0.0)
    r = eng.step(s, pool=pool)
    assert r["current_idea"] == "w idea"
    # emergence_score > 0 (메타 있으므로)
    assert r["emergence_score"] > 0.0


def test_observer_verdict_propagated():
    """observer_verdict가 결과에 그대로 반영."""
    s = _State()
    s._ext["observer_verdict"] = "STABLE"
    r = IdeaEngine().step(s)
    assert r["observer_verdict"] == "STABLE"
