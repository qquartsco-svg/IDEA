# -*- coding: utf-8 -*-
"""
Atom state 연동: state를 넣으면 idea 엔진으로 한 스텝 돌리고
extension에 orbit_deviation_active, current_idea, force_explore, idea_used_step 기록.
"""

from __future__ import annotations
from typing import Any, Optional

from ..idea_engine import IdeaEngine
from ..idea_pool import IdeaPool


def update_atom_state(
    state: Any,
    engine: Optional[IdeaEngine] = None,
    pool: Optional[IdeaPool] = None,
) -> Any:
    """
    Atom state 한 스텝 갱신: idea 엔진으로 궤도 이탈·아이디어 선택 후
    state.set_extension(...)으로 결과 기록.

    state: AtomState 등 get_extension/set_extension 있는 객체.
    engine: None이면 IdeaEngine() 기본값.
    pool: None이면 state.get_extension("idea_pool")로 IdeaPool.from_list() 생성.
    """
    if engine is None:
        engine = IdeaEngine()
    result = engine.step(state, pool=pool)

    # ── v0.1 호환 extensions ──────────────────────────────────────────
    state.set_extension("orbit_deviation_active", result["orbit_deviation_active"])
    state.set_extension("current_idea",           result["current_idea"])
    state.set_extension("force_explore",          result["force_explore"])
    if result.get("idea_used_step") is not None:
        state.set_extension("idea_used_step", result["idea_used_step"])

    # ── v0.2 신규 extensions ──────────────────────────────────────────
    for key in (
        "orbit_mode",
        "quantum_noise",
        "delta_raw",
        "delta_eff",
        "uncertainty_index",
        "emergence_score",
        "emergence_event",
        "observer_verdict",
    ):
        if key in result:
            state.set_extension(key, result[key])

    return state
