# -*- coding: utf-8 -*-
"""
idea_pool — 이데아계(형이상학) 저장소

【플라톤 개념 정확 대응】
  IdeaPool 전체  = 이데아계 (κόσμος νοητός) — 보편·불변 형상들의 저장소
  각 entry       = 이데아의 언어적 근사값 (이데아 자체는 언어 이전의 순수 형상)
  add()          = 상기(ἀνάμνησις) — 이데아를 텍스트로 '기억에 등록'
  pick_weighted()= 참여(μέθεξις)   — 현상계(IdeaEngine)가 이데아를 끌어당기는 행위
  confidence     = 그 텍스트 근사값이 이데아에 얼마나 가까운지의 척도

저장 단위: str 또는 dict. dict 권장 필드:
  text, source (library|recall|observer-trigger), type (metaphor|solution|experiment|question),
  confidence, feasibility, novelty (선택), created_at.
"""

from __future__ import annotations
import json
import random
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union


def _float_val(val: Any, default: float = 0.5) -> float:
    """None-safe float 변환."""
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default

# 항목 타입/소스 상수 (저장 규칙)
SOURCE_LIBRARY = "library"
SOURCE_RECALL = "recall"
SOURCE_OBSERVER_TRIGGER = "observer-trigger"
TYPE_METAPHOR = "metaphor"
TYPE_SOLUTION = "solution"
TYPE_EXPERIMENT = "experiment"
TYPE_QUESTION = "question"


def _to_entry(x: Union[str, dict]) -> dict:
    """단일 항목을 {text, source?, type?, confidence?, feasibility?, novelty?, created_at?} 형태로."""
    if isinstance(x, str):
        return {"text": x, "source": None, "type": None, "confidence": None, "feasibility": None, "novelty": None, "created_at": None}
    if isinstance(x, dict) and x:
        text = x.get("text", x.get("digest", str(next(iter(x.values())))))
        return {
            "text": text,
            "source": x.get("source"),
            "type": x.get("type"),
            "confidence": x.get("confidence"),
            "feasibility": x.get("feasibility"),
            "novelty": x.get("novelty"),
            "created_at": x.get("created_at"),
        }
    return {"text": str(x), "source": None, "type": None, "confidence": None, "feasibility": None, "novelty": None, "created_at": None}


class IdeaPool:
    """
    이데아 풀: 보편 패턴(아이디어) 목록. 추가·삭제·선택·영속화.

    플라톤적 해석: 이데아(형상)의 저장소. 개별 state가 여기서 하나를 골라
    "참여(μέθεξις)"할 때 current_idea가 됨.
    """

    def __init__(self, items: Optional[List[Union[str, dict]]] = None):
        self._entries: List[dict] = []
        if items:
            for x in items:
                self.add(x)

    def add(
        self,
        text_or_dict: Union[str, dict],
        source: Optional[str] = None,
        type_: Optional[str] = None,
        confidence: Optional[float] = None,
        feasibility: Optional[float] = None,
        novelty: Optional[float] = None,
    ) -> None:
        """항목 추가. dict면 text/source/type/confidence/feasibility/novelty 추출."""
        if isinstance(text_or_dict, str):
            self._entries.append({
                "text": text_or_dict,
                "source": source,
                "type": type_,
                "confidence": confidence,
                "feasibility": feasibility,
                "novelty": novelty,
                "created_at": _iso_now(),
            })
        else:
            e = _to_entry(text_or_dict)
            if not e.get("created_at"):
                e["created_at"] = _iso_now()
            if source is not None:
                e["source"] = source
            if type_ is not None:
                e["type"] = type_
            if confidence is not None:
                e["confidence"] = confidence
            if feasibility is not None:
                e["feasibility"] = feasibility
            if novelty is not None:
                e["novelty"] = novelty
            self._entries.append(e)

    def remove(self, index: int) -> Optional[dict]:
        """인덱스로 삭제. 반환: 삭제된 항목."""
        if 0 <= index < len(self._entries):
            return self._entries.pop(index)
        return None

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return len(self._entries) > 0

    def pick_one(self, max_len: Optional[int] = None) -> Optional[str]:
        """
        풀에서 하나를 무작위로 선택해 텍스트만 반환 (uniform random).
        max_len 넘으면 잘라서 반환.
        """
        if not self._entries:
            return None
        e = random.choice(self._entries)
        text = e.get("text", "")
        if max_len is not None and len(text) > max_len:
            text = text[:max_len].rstrip() + "..."
        return text

    def pick_weighted(
        self,
        max_len: Optional[int] = None,
        return_entry: bool = False,
    ) -> "Union[Optional[str], Tuple[Optional[str], Optional[dict]]]":
        """
        가중 무작위 선택: w = confidence × feasibility × (1 + novelty).

        메타데이터 없는 항목 기본 가중치:
            0.5 × 0.5 × (1 + 0.5) = 0.375

        return_entry=True 이면 (text, entry_dict) 튜플 반환.
        풀이 비어 있으면 (None, None) 또는 None 반환.

        v0.2.0 신규 — 창발 점수 계산에 활용됨.
        """
        if not self._entries:
            return (None, None) if return_entry else None

        # 가중치 계산
        weights: List[float] = []
        for e in self._entries:
            c = _float_val(e.get("confidence"),  0.5)
            f = _float_val(e.get("feasibility"), 0.5)
            n = _float_val(e.get("novelty"),      0.5)
            w = c * f * (1.0 + n)
            weights.append(max(w, 1e-6))

        # 가중 누적합으로 선택
        total  = sum(weights)
        r      = random.random() * total
        cumsum = 0.0
        selected = self._entries[-1]
        for entry, w in zip(self._entries, weights):
            cumsum += w
            if r <= cumsum:
                selected = entry
                break

        text = selected.get("text", "")
        if max_len is not None and len(text) > max_len:
            text = text[:max_len].rstrip() + "..."

        if return_entry:
            return (text, selected)
        return text

    def to_list(self) -> List[Union[str, dict]]:
        """state extension 호환: 문자열 리스트 또는 dict 리스트."""
        return [e["text"] for e in self._entries]

    def to_list_with_meta(self) -> List[dict]:
        """메타 포함 리스트."""
        return list(self._entries)

    @classmethod
    def from_list(cls, raw: Any) -> "IdeaPool":
        """state.get_extension('idea_pool') 같은 list/dict에서 생성."""
        if raw is None:
            return cls()
        if isinstance(raw, IdeaPool):
            return cls(raw.to_list())
        if isinstance(raw, list):
            return cls(raw)
        if isinstance(raw, str):
            return cls([raw])
        return cls()

    def save(self, path: Union[str, Path]) -> bool:
        """JSON으로 저장."""
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load(self, path: Union[str, Path]) -> bool:
        """JSON에서 로드. 기존 항목에 추가."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for e in data:
                    if isinstance(e, dict):
                        self._entries.append(e)
                    else:
                        self._entries.append(_to_entry(str(e)))
            return True
        except Exception:
            return False


def _iso_now() -> str:
    try:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
