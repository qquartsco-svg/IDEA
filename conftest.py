# conftest.py — IDEA-repo 독립 테스트 경로 설정
# ionia.idea import 경로와 직접(로컬) import 경로 모두 지원
import sys
from pathlib import Path

# IDEA-repo 루트를 sys.path에 추가 → from idea_pool import IdeaPool 가능
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# 독립 레포에서 ionia.idea import를 지원하기 위한 가상 패키지 마운트
# IDEA-repo 루트를 'idea' 라는 이름으로 ionia 하위에 연결
try:
    import types
    ionia_mod = sys.modules.get("ionia") or types.ModuleType("ionia")
    idea_mod = types.ModuleType("ionia.idea")
    # IDEA-repo 루트의 심볼들을 ionia.idea 네임스페이스에 주입
    import idea_pool as _ip
    import idea_engine as _ie
    idea_mod.IdeaPool = _ip.IdeaPool
    idea_mod.IdeaEngine = _ie.IdeaEngine
    # adapters
    import adapters.atom_bridge as _ab
    idea_mod.update_atom_state = _ab.update_atom_state
    ionia_mod.idea = idea_mod
    sys.modules["ionia"] = ionia_mod
    sys.modules["ionia.idea"] = idea_mod
except Exception:
    pass
