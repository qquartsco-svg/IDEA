# tests/conftest.py — IDEA-repo 독립 테스트: ionia.idea import 지원
import sys
import types
from pathlib import Path

# IDEA-repo 루트
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# ionia.idea 가상 패키지 마운트 (독립 레포에서 from ionia.idea import ... 지원)
if "ionia.idea" not in sys.modules:
    import idea_pool as _ip
    import idea_engine as _ie

    ionia_mod = sys.modules.get("ionia") or types.ModuleType("ionia")
    idea_mod = types.ModuleType("ionia.idea")
    idea_mod.IdeaPool = _ip.IdeaPool
    idea_mod.IdeaEngine = _ie.IdeaEngine

    try:
        sys.path.insert(0, str(_repo_root))
        import adapters.atom_bridge as _ab
        idea_mod.update_atom_state = _ab.update_atom_state
    except Exception:
        pass

    ionia_mod.idea = idea_mod
    sys.modules.setdefault("ionia", ionia_mod)
    sys.modules["ionia.idea"] = idea_mod
