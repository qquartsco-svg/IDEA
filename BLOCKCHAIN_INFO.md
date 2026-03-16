# 🔗 PHAM 블록체인 서명 정보 — IDEA (이데아)

## 📋 개요

이 **IDEA (이데아)** 모듈은 **PHAM (Proof of Authorship & Merit) 블록체인 시스템**으로 서명되어 있습니다.

> 이데아(ἰδέα) — 플라톤적 형상(Form) 유비에 따른 **아이디어 저장·선택·참여** 독립 모듈.
> 궤도 이탈 → 창의력 발휘 → 아이디어 → 생각(맥락) → 구현(motor_command) 파이프라인의 **아이디어 계층**.
> Atom·Athena 등과 무의존(표준 라이브러리만 사용). 대도서관(Library)과 연동 시 idea_pool 자동 적재 가능.

---

## 🏛️ 모듈 구성

```
idea/
├── __init__.py          — IdeaPool, IdeaEngine, update_atom_state export
├── idea_pool.py         — IdeaPool: 이데아(형상) 저장소 (add/remove/pick_one, save/load JSON)
├── idea_engine.py       — IdeaEngine: 궤도 이탈 판단 + 복합 안전 조건 + pick_one
├── adapters/
│   ├── __init__.py
│   └── atom_bridge.py   — update_atom_state(state) → Atom extension 주입
├── tests/
│   ├── test_idea_pool.py   — IdeaPool 단위 테스트
│   └── test_idea_engine.py — IdeaEngine·복합 안전 조건 테스트
├── README.md            — 개념·로직·API·Atom 연동
└── BLOCKCHAIN_INFO.md   — 본 문서 (PHAM 서명)
```

---

## 🔐 핵심 계약

| 항목 | 내용 |
|------|------|
| **IdeaPool** | 항목: text, source?, type?, confidence?, feasibility?, novelty?, created_at?. 저장 규칙으로 품질 유지. |
| **IdeaEngine.step(state, pool?)** | 반환: orbit_deviation_active, current_idea, force_explore, idea_used_step. 복합 안전 조건(기본): warning/self_defense/recursion_risk 모두 낮을 때만 이탈 허용. |
| **Atom extension** | idea_pool, creative_mode, orbit_deviation_active, current_idea, force_explore, idea_used_step. |
| **테스트** | idea/tests/ — IdeaPool·IdeaEngine·복합 안전 조건 검증. |

---

## 🔄 버전 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| **v0.1.0** | 2026-03-16 | 최초 릴리즈 — IdeaPool, IdeaEngine, Atom adapter, 복합 안전 조건, idea_pool 구조화(source/type/confidence/feasibility/novelty), JSON save/load, PHAM 서명 |

---

## 💰 블록체인 기반 기여도 시스템

**라이선스**: MIT License  
**사용 제한**: 없음  
**로열티 요구**: 없음  

### ⚠️ GNJz의 기여도 원칙 (블록체인 기반)

- **상한선**: GNJz의 기여도는 블록체인 기반으로 최대 **70%** 상한
- **검증 가능성**: 블록체인으로 검증 가능한 기여도 상한선
- **투명성**: 모든 기여도 계산은 블록체인에 기록되어 검증 가능

이 원칙은 코드가 어떻게 상용화되든, 누가 상용화하든 관계없이 블록체인에 영구 기록됩니다.

---

## 📞 문의

- **GitHub**: https://github.com/qquartsco-svg/IDEA
- **Issues**: https://github.com/qquartsco-svg/IDEA/issues

---

**최초 작성일**: 2026-03-16  
**최종 갱신**: 2026-03-16  
**버전**: 0.1.0  
**작성자**: GNJz (Qquarts)
