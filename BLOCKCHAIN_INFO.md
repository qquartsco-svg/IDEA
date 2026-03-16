# 🔗 PHAM 블록체인 서명 정보 — IDEA (이데아)

## 📋 개요

이 **IDEA (이데아)** 모듈은 **PHAM (Proof of Authorship & Merit) 블록체인 시스템**으로 서명되어 있습니다.

> 이데아(ἰδέα) — 플라톤적 형상(Form) 유비에 따른 **아이디어 저장·선택·참여** 독립 모듈.
> 궤도 이탈 → 창의력 발휘 → 아이디어 → 생각(맥락) → 구현(motor_command) 파이프라인의 **아이디어 계층**.
> v0.2: **양자 요동 모델** + **옵저버 연동** + **orbit_mode 5단계** + **창발 점수** + **불확실성 지수**.

---

## 🏛️ 모듈 구성

```
idea/
├── __init__.py          — IdeaPool, IdeaEngine, update_atom_state export (v0.2.0)
├── idea_pool.py         — IdeaPool: add/remove/pick_one/pick_weighted/save/load JSON
├── idea_engine.py       — IdeaEngine: 양자 요동 + 옵저버 + orbit_mode + 창발 점수
├── adapters/
│   ├── __init__.py
│   └── atom_bridge.py   — update_atom_state(state) → v0.1+v0.2 extensions 주입
├── tests/
│   ├── test_idea_pool.py   — 12개 단위 테스트
│   └── test_idea_engine.py — 17개 단위 테스트
├── README.md            — 개념·수식·API·Atom 연동
└── BLOCKCHAIN_INFO.md   — 본 문서 (PHAM 서명)
```

---

## 🔐 핵심 계약

| 항목 | 내용 |
|------|------|
| **IdeaPool** | text, source?, type?, confidence?, feasibility?, novelty?. `pick_weighted()` 가중 선택 (v0.2). |
| **IdeaEngine.step()** | 반환: orbit_deviation_active, current_idea, force_explore, idea_used_step (v0.1) + orbit_mode, quantum_noise, delta_eff, uncertainty_index, emergence_score, emergence_event (v0.2). |
| **orbit_mode** | LOCKED / ORBIT / PRECESSION / DEVIATION / EMERGENCE |
| **양자 요동** | q ~ N(0, σ_q), σ_q = observer_verdict 기반 (HEALTHY→0.03, STABLE→0.05, FRAGILE→0.15, CRITICAL→0.00) |
| **창발 점수** | E = confidence × feasibility × (1+novelty) / 2.0 ∈ [0,1] |
| **불확실성 지수** | U = σ_q × (1 − self_reg + &#124;q&#124;) |
| **테스트** | 총 29개 (pool 12 + engine 17), 전체 PASS |

---

## 🔄 버전 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| **v0.2.0** | 2026-03-16 | 양자 요동(Box-Muller), 옵저버 연동(σ_q 자동), orbit_mode 5단계, 창발 점수, 불확실성 지수, pick_weighted(), atom_bridge v0.2 extensions, 테스트 29개 |
| **v0.1.0** | 2026-03-16 | 최초 릴리즈 — IdeaPool, IdeaEngine, Atom adapter, 복합 안전 조건, JSON save/load, PHAM 서명 |

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
**버전**: 0.2.0
**작성자**: GNJz (Qquarts)
