# -*- coding: utf-8 -*-
"""
idea — 이데아(형상) 독립 모듈

플라톤적 이데아 유비: 보편 패턴(아이디어)을 저장하고, 궤도 이탈 시 하나를 골라
생각(맥락)에 참여시켜 구현(motor_command)으로 이어지게 함.

사용법:
    from ionia.idea import IdeaPool, IdeaEngine
    pool = IdeaPool(["아이디어 A", "아이디어 B"])
    engine = IdeaEngine(self_regulation_threshold=0.35)
    result = engine.step(state, pool)

    # Atom 연동 (L2와 L3 사이 레이어)
    from ionia.idea.adapters import update_atom_state
    state = update_atom_state(state)
"""
from __future__ import annotations

try:
    from .idea_pool import IdeaPool
    from .idea_engine import IdeaEngine
except ImportError:
    from idea_pool import IdeaPool   # type: ignore[no-redef]
    from idea_engine import IdeaEngine  # type: ignore[no-redef]

__version__ = "0.2.0"
__all__ = ["IdeaPool", "IdeaEngine", "update_atom_state"]


def update_atom_state(state, engine=None, pool=None):
    """Atom state에 idea 엔진 결과 주입. ionia.idea.adapters에서 re-export."""
    try:
        from .adapters.atom_bridge import update_atom_state as _update
    except ImportError:
        from adapters.atom_bridge import update_atom_state as _update  # type: ignore[no-redef]
    return _update(state, engine=engine, pool=pool)
