# -*- coding: utf-8 -*-
"""
idea_engine — 궤도 이탈 판단 + 이데아 선택 엔진

복합 안전 조건: creative_mode 또는 (self_regulation 낮음) 일 때만 이탈 허용하고,
warning_signal / self_defense_signal / recursion_risk_signal 이 모두 낮을 때만
exploration 상향(orbit_deviation_active). 단일 신호 역전은 위험 구간에서도
탐색을 키울 수 있으므로 복합 조건 사용.
"""

from __future__ import annotations
from typing import Any, Optional

try:
    from .idea_pool import IdeaPool
except ImportError:
    from idea.idea_pool import IdeaPool


def _float_signal(val: Any, default: float = 0.5) -> float:
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


class IdeaEngine:
    """
    궤도 이탈 시 아이디어 하나를 골라 "생각(맥락)"으로 쓸 수 있게 하는 엔진.

    - 궤도 이탈 후보: creative_mode=True 또는 self_regulation_signal < threshold
    - 복합 안전 조건: 위 + (warning_signal, self_defense_signal, recursion_risk_signal 모두 < safe_threshold)일 때만 orbit_deviation_active=True. 없으면 기존처럼 단일 조건.
    - 이탈 시: pool.pick_one() → current_idea, force_explore=True
    """

    def __init__(
        self,
        self_regulation_threshold: float = 0.35,
        force_explore_when_deviation: bool = True,
        max_idea_len: int = 500,
        use_composite_safety: bool = True,
        safe_signal_threshold: float = 0.5,
    ):
        self.self_regulation_threshold = self_regulation_threshold
        self.force_explore_when_deviation = force_explore_when_deviation
        self.max_idea_len = max_idea_len
        self.use_composite_safety = use_composite_safety
        self.safe_signal_threshold = safe_signal_threshold

    def step(
        self,
        state: Any,
        pool: Optional[IdeaPool] = None,
    ) -> dict:
        """
        한 스텝: state에서 신호 읽기 → 복합 안전 조건으로 궤도 이탈 여부 → 풀에서 선택 → 결과 dict.
        """
        def get_ext(key: str, default: Any = None):
            if hasattr(state, "get_extension"):
                return state.get_extension(key, default)
            if hasattr(state, "extensions") and isinstance(state.extensions, dict):
                return state.extensions.get(key, default)
            return default

        creative_mode = get_ext("creative_mode") is True
        self_reg = _float_signal(get_ext("self_regulation_signal"), 0.5)
        low_regulation = self_reg < self.self_regulation_threshold
        deviation_candidate = creative_mode or low_regulation

        if self.use_composite_safety and deviation_candidate:
            warn = _float_signal(get_ext("warning_signal"), 0.0)
            defense = _float_signal(get_ext("self_defense_signal"), 0.0)
            recur = _float_signal(get_ext("recursion_risk_signal"), 0.0)
            all_safe = (warn < self.safe_signal_threshold and
                        defense < self.safe_signal_threshold and
                        recur < self.safe_signal_threshold)
            orbit_deviation_active = deviation_candidate and all_safe
        else:
            orbit_deviation_active = deviation_candidate

        current_idea = None
        idea_used_step = None
        force_explore = False

        if pool is None:
            pool = IdeaPool.from_list(get_ext("idea_pool"))

        if orbit_deviation_active and pool:
            current_idea = pool.pick_one(max_len=self.max_idea_len)
            step_val = get_ext("step", 0)
            try:
                idea_used_step = int(step_val)
            except (TypeError, ValueError):
                idea_used_step = 0
            force_explore = self.force_explore_when_deviation
        elif orbit_deviation_active:
            force_explore = self.force_explore_when_deviation

        return {
            "orbit_deviation_active": orbit_deviation_active,
            "current_idea": current_idea,
            "force_explore": force_explore,
            "idea_used_step": idea_used_step,
        }
