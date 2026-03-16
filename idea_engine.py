# -*- coding: utf-8 -*-
"""
idea_engine v0.2.0 — 궤도 이탈 판단 + 이데아 참여 엔진

【형이상학 ↔ 형이하학 구조】
  형이상학 레이어 (이데아계):  IdeaPool — 보편 형상의 저장소 (이 파일 밖)
  형이하학 레이어 (현상계):    IdeaEngine — 현상계 동역학 계산 (이 파일)
  다리:                       pick_weighted() — 참여(μέθεξις), 이데아를 현상에 끌어들임

  현상계 신호: state_vector / self_regulation / σ_q / δ_eff / orbit_mode
  이데아계→현상계: current_idea (이데아의 언어적 근사) → motor_command (행동·물질화)

v0.2 신규:
  - 양자 요동 (quantum noise): q ~ N(0, σ_q), Box-Muller 변환
      → 현상계의 불확정성 (하이젠베르크 유비)
  - 옵저버 연동: observer_verdict → σ_q 자동 결정
      HEALTHY→0.03 / STABLE→0.05 / FRAGILE→0.15 / CRITICAL→0.00 (완전 잠금)
  - orbit_mode 5단계: LOCKED / ORBIT / PRECESSION / DEVIATION / EMERGENCE
      동굴의 비유 대응:
        LOCKED     = 사슬에 묶여 그림자만 봄 (CRITICAL)
        ORBIT      = 동굴 속 그림자 세계 (현상만 처리)
        PRECESSION = 불빛 감지, 고개 돌림 (창의 전조)
        DEVIATION  = 동굴 밖으로 나가기 시작 (이데아 참여 활성)
        EMERGENCE  = 태양(선의 이데아) 목격 (창발 이벤트)
  - 창발 점수 (emergence_score):
      E = confidence × feasibility × (1 + novelty) / 2.0  ∈ [0, 1]
      emergence_event = True if E ≥ emergence_threshold (기본 0.60)
  - 불확실성 지수: U = σ_q × (1 − self_reg + |q|)
  - δ_raw (결정론적 편차), δ_eff = δ_raw + q

v0.1 하위 호환:
  orbit_deviation_active / current_idea / force_explore / idea_used_step 유지.
"""

from __future__ import annotations

import math
import random
from typing import Any, Optional, Tuple

try:
    from .idea_pool import IdeaPool
except ImportError:
    from idea.idea_pool import IdeaPool


# ── orbit_mode 상수 ────────────────────────────────────────────────────────
ORBIT_LOCKED     = "LOCKED"      # CRITICAL — 완전 잠금, 이탈 불가
ORBIT_ORBIT      = "ORBIT"       # 정상 궤도 (창의 비활성)
ORBIT_PRECESSION = "PRECESSION"  # 양자 요동 흔들림 — 창의 전조 (이탈 미만)
ORBIT_DEVIATION  = "DEVIATION"   # 궤도 이탈 — 창의 활성
ORBIT_EMERGENCE  = "EMERGENCE"   # 궤도 이탈 + 창발 이벤트 — 최고 창발

# ── observer_verdict → 양자 노이즈 스케일 σ_q ────────────────────────────
_OBSERVER_NOISE = {
    "HEALTHY":  0.03,   # 안정 궤도, 미세 요동
    "STABLE":   0.05,   # 정상 요동
    "FRAGILE":  0.15,   # 큰 요동 — 시스템이 새 궤도를 탐색
    "CRITICAL": 0.00,   # 잠금 — 자기방어, 이탈 완전 차단
}
_DEFAULT_NOISE_SCALE  = 0.05
_PRECESSION_THRESHOLD = 0.00   # δ_eff > 0 → PRECESSION 시작
_DEVIATION_THRESHOLD  = 0.15   # δ_eff > 0.15 → 완전 DEVIATION


def _float_signal(val: Any, default: float = 0.5) -> float:
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def _quantum_noise(scale: float) -> float:
    """Box-Muller 변환: N(0, scale) 샘플링."""
    if scale <= 0.0:
        return 0.0
    u1 = max(random.random(), 1e-12)
    u2 = random.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return z * scale


def _emergence_score(entry: Optional[dict]) -> float:
    """
    창발 점수 = confidence × feasibility × (1 + novelty) / 2.0  ∈ [0, 1]

    최대값: 1.0 × 1.0 × (1 + 1.0) / 2.0 = 1.0
    메타 없으면: 0.5 × 0.5 × 1.5 / 2.0 = 0.1875
    """
    if entry is None:
        return 0.0
    c   = _float_signal(entry.get("confidence"),  0.5)
    f   = _float_signal(entry.get("feasibility"), 0.5)
    n   = _float_signal(entry.get("novelty"),      0.5)
    raw = c * f * (1.0 + n)
    return min(raw / 2.0, 1.0)


class IdeaEngine:
    """
    궤도 이탈 시 아이디어를 골라 "생각(맥락)"으로 쓸 수 있게 하는 엔진.

    ── v0.1 결정론적 ─────────────────────────────────────────────────────
    이탈 후보 : creative_mode=True  or  self_regulation < threshold
    복합 안전  : warning / self_defense / recursion_risk 모두 낮아야 허용

    ── v0.2 양자 요동 ────────────────────────────────────────────────────
    q ~ N(0, σ_q),   σ_q = observer_verdict 기반 자동 결정
    δ_raw = 결정론적 편차 신호
    δ_eff = δ_raw + q

    orbit_mode (δ_eff 기반):
      LOCKED     → CRITICAL 상태
      ORBIT      → δ_eff ≤ 0
      PRECESSION → 0 < δ_eff ≤ 0.15  (양자 요동 흔들림)
      DEVIATION  → δ_eff > 0.15
      EMERGENCE  → DEVIATION + emergence_event

    orbit_deviation_active : v0.1 결정론적 조건 유지 (하위 호환)
    """

    def __init__(
        self,
        self_regulation_threshold:  float = 0.35,
        force_explore_when_deviation: bool = True,
        max_idea_len:               int   = 500,
        use_composite_safety:       bool  = True,
        safe_signal_threshold:      float = 0.5,
        quantum_noise_scale:        Optional[float] = None,   # None → observer 자동
        emergence_threshold:        float = 0.60,
        use_weighted_pick:          bool  = True,
    ):
        self.self_regulation_threshold   = self_regulation_threshold
        self.force_explore_when_deviation = force_explore_when_deviation
        self.max_idea_len                = max_idea_len
        self.use_composite_safety        = use_composite_safety
        self.safe_signal_threshold       = safe_signal_threshold
        self.quantum_noise_scale         = quantum_noise_scale
        self.emergence_threshold         = emergence_threshold
        self.use_weighted_pick           = use_weighted_pick

    # ── 내부 ────────────────────────────────────────────────────────────

    def _sigma(self, observer_verdict: Optional[str]) -> float:
        """σ_q: 고정값 or observer_verdict 자동."""
        if self.quantum_noise_scale is not None:
            return self.quantum_noise_scale
        if observer_verdict is None:
            return _DEFAULT_NOISE_SCALE
        return _OBSERVER_NOISE.get(observer_verdict, _DEFAULT_NOISE_SCALE)

    def _orbit_mode(
        self,
        delta_eff: float,
        blocked: bool,
        emergence_event: bool,
    ) -> str:
        if blocked:
            return ORBIT_LOCKED
        if delta_eff <= _PRECESSION_THRESHOLD:
            return ORBIT_ORBIT
        if delta_eff <= _DEVIATION_THRESHOLD:
            return ORBIT_PRECESSION
        if emergence_event:
            return ORBIT_EMERGENCE
        return ORBIT_DEVIATION

    # ── 공개 ────────────────────────────────────────────────────────────

    def step(
        self,
        state: Any,
        pool: Optional[IdeaPool] = None,
    ) -> dict:
        """
        한 스텝:
          ① state 신호 읽기
          ② 결정론적 궤도 이탈 판단 (orbit_deviation_active — v0.1 호환)
          ③ 양자 요동 계산 → δ_eff, orbit_mode, uncertainty_index
          ④ 아이디어 선택 (pick_weighted → 창발 점수)
          ⑤ 결과 dict 반환
        """
        def get_ext(key: str, default: Any = None):
            if hasattr(state, "get_extension"):
                return state.get_extension(key, default)
            if hasattr(state, "extensions") and isinstance(state.extensions, dict):
                return state.extensions.get(key, default)
            return default

        # ① 신호 읽기
        creative_mode    = get_ext("creative_mode") is True
        self_reg         = _float_signal(get_ext("self_regulation_signal"), 0.5)
        observer_verdict = get_ext("observer_verdict", None)
        if isinstance(observer_verdict, str):
            observer_verdict = observer_verdict.upper()

        # ② 결정론적 이탈 판단 (v0.1 호환)
        low_regulation      = self_reg < self.self_regulation_threshold
        deviation_candidate = creative_mode or low_regulation
        blocked             = (observer_verdict == "CRITICAL")

        if blocked:
            orbit_deviation_active = False
        elif self.use_composite_safety and deviation_candidate:
            warn    = _float_signal(get_ext("warning_signal"),       0.0)
            defense = _float_signal(get_ext("self_defense_signal"),   0.0)
            recur   = _float_signal(get_ext("recursion_risk_signal"), 0.0)
            all_safe = (
                warn    < self.safe_signal_threshold and
                defense < self.safe_signal_threshold and
                recur   < self.safe_signal_threshold
            )
            orbit_deviation_active = deviation_candidate and all_safe
        else:
            orbit_deviation_active = deviation_candidate

        # ③ 양자 요동 계산 (v0.2 신규)
        sigma   = self._sigma(observer_verdict)
        q_noise = _quantum_noise(sigma)

        # δ_raw: 결정론적 이탈 "강도"
        #   creative_mode=True → δ_raw = 1.0 (항상 이탈 방향)
        #   else              → δ_raw = threshold − self_reg (양수면 이탈 방향)
        if creative_mode:
            delta_raw = 1.0
        else:
            delta_raw = self.self_regulation_threshold - self_reg

        delta_eff         = delta_raw + q_noise
        uncertainty_index = sigma * (1.0 - self_reg + abs(q_noise))

        # ④ 아이디어 선택
        if pool is None:
            pool = IdeaPool.from_list(get_ext("idea_pool"))

        current_idea    = None
        idea_used_step  = None
        selected_entry  = None
        force_explore   = False
        emergence_score = 0.0
        emergence_event = False

        if orbit_deviation_active and pool:
            # 가중 선택 우선 (confidence × feasibility × (1+novelty))
            if self.use_weighted_pick and hasattr(pool, "pick_weighted"):
                picked = pool.pick_weighted(
                    max_len=self.max_idea_len, return_entry=True
                )
                if isinstance(picked, tuple):
                    current_idea, selected_entry = picked
                else:
                    current_idea = picked

            # 가중 선택 실패 시 uniform fallback
            if current_idea is None:
                current_idea = pool.pick_one(max_len=self.max_idea_len)
                selected_entry = None

            step_val = get_ext("step", 0)
            try:
                idea_used_step = int(step_val)
            except (TypeError, ValueError):
                idea_used_step = 0

            force_explore   = self.force_explore_when_deviation
            emergence_score = _emergence_score(selected_entry)
            emergence_event = (emergence_score >= self.emergence_threshold)

        elif orbit_deviation_active:
            force_explore = self.force_explore_when_deviation

        # ⑤ orbit_mode (δ_eff 기반 5단계)
        orbit_mode = self._orbit_mode(delta_eff, blocked, emergence_event)

        return {
            # ── v0.1 호환 ──────────────────────────────────────────────
            "orbit_deviation_active": orbit_deviation_active,
            "current_idea":           current_idea,
            "force_explore":          force_explore,
            "idea_used_step":         idea_used_step,
            # ── v0.2 신규 ──────────────────────────────────────────────
            "orbit_mode":             orbit_mode,
            "quantum_noise":          q_noise,
            "delta_raw":              delta_raw,
            "delta_eff":              delta_eff,
            "uncertainty_index":      uncertainty_index,
            "emergence_score":        emergence_score,
            "emergence_event":        emergence_event,
            "observer_verdict":       observer_verdict,
        }
