# IDEA — 이데아(형상) 독립 모듈

**플라톤의 이데아(ἰδέα)를 현대 인지 아키텍처로 옮긴 아이디어 저장·참여 엔진.**
가변적인 현상(Perception)에만 머물지 않고, **보편적·본질적 패턴(이데아)**를 저장했다가 필요할 때 현재 판단 궤적에 **참여(μέθεξις)**시키는 구조를 제공합니다.

- **한 줄 정의**: "질서(궤도 유지) 속의 자유(창발)" — **안정 궤도 위에서만** 허용된 궤도 이탈 시, 이데아 풀에서 하나를 골라 생각(맥락)에 넣고 구현(motor_command)으로 이어지게 하는 모듈.
- **v0.2 신규**: 양자 요동 모델 + 옵저버 연동 + orbit_mode 5단계 + 창발 점수 + 불확실성 지수 + 가중 선택

---

## 개념

### 형이상학 ↔ 형이하학 — 두 세계 구조

플라톤은 세계를 두 층으로 나눈다.

| 층위 | 플라톤 용어 | 특성 | 코드 대응 |
|------|-----------|------|----------|
| **형이상학** | 이데아계 (κόσμος νοητός) | 불변·영원·완전, 이성으로만 인식 | `IdeaPool` — 보편 패턴 저장소 |
| **형이하학** | 현상계 (κόσμος αἰσθητός) | 변화·시간·불완전, 감각으로 인식 | `state_vector`, 계산 레이어 전체 |

이데아 엔진은 이 두 층을 **코드 레이어로 분리**하고, 그 사이를 오가는 행위를 구체적으로 구현한다.

---

### 형이상학 레이어 — IdeaPool (이데아계)

```
IdeaPool  ←  이데아계 (κόσμος νοητός)
  각 entry = 이데아의 언어적 근사값
             (이데아 자체는 언어 이전의 순수 형상 — 텍스트는 그 그림자)
```

- **이데아(ἰδέα)** = 불변·보편 형상. "아름다움 자체", "정의 자체"처럼 구체적 사례를 초월한 본질.
- **`IdeaPool.add()`** = **상기(ἀνάμνησις)**: 영혼이 이미 알고 있던 형상을 언어로 '기억해 꺼내는' 행위.
- **`confidence / feasibility / novelty`** = 그 텍스트 근사값이 진짜 이데아에 **얼마나 가까운지**의 척도.
  - `confidence=1.0` → 이데아에 매우 근접 / `confidence=0.1` → 현상에 가까운 흐릿한 인상

> ⚠️ IdeaPool에 저장되는 것은 **이데아 자체가 아니다.** 플라톤에게 이데아는 말로 표현이 불가능하다(《파이드로스》). 저장된 텍스트는 이데아를 **가리키는 손가락** — 언어적 근사값.

---

### 형이하학 레이어 — IdeaEngine 계산 (현상계)

```
IdeaEngine의 모든 계산  ←  현상계 (κόσμος αἰσθητός)
  state_vector, self_regulation_signal = 현상계의 물리량
  σ_q, δ_eff, orbit_mode              = 현상계의 동역학
  observer_verdict                    = 현상계 관찰자 판정
```

- `state_vector`, `perception`, `memory_info` = 이 스텝에서 시스템이 감각하는 **현상의 순간 상태**
- `self_regulation_signal` = 현상계에서의 **자기 조절력** (낮아질수록 이데아를 향한 충동 증가)
- 양자 요동 `q ~ N(0, σ_q)` = 현상계에 내재한 **불확정성** (하이젠베르크 유비)

---

### 다리 — 참여(μέθεξις) · 모방(μίμησις)

```
이데아계 (IdeaPool)
       │
       │  pick_weighted()  ← 참여 (μέθεξις)
       │                     현상이 이데아를 '끌어당기는' 행위
       ▼
current_idea               ← 이데아가 언어·개념으로 내려온 중간 형태
       │
       │  L3 → motor_command  ← 모방 (μίμησις)
       │                          이데아를 행동(물질)으로 구현
       ▼
현상계 (state / motor_command)
```

| 플라톤 개념 | 의미 | 코드 대응 |
|-----------|------|----------|
| **참여 (μέθεξις)** | 개별자가 이데아에 '참여'해 그 본질을 일부 가짐 | `pick_weighted()` — 현재 상태에 이데아를 끌어들이는 행위 |
| **모방 (μίμησις)** | 이데아를 현상계에서 불완전하게 구현 | `current_idea` → `motor_command` (이데아를 행동으로 내림) |
| **상기 (ἀνάμνησις)** | 영혼이 이미 알고 있던 이데아를 기억해냄 | `pool.add()` — 이데아를 텍스트로 기억에 등록 |

---

### 동굴의 비유와 orbit_mode 5단계

플라톤의 **동굴의 비유**(《국가》 514a)는 이데아를 향한 인식의 단계를 묘사한다.
orbit_mode는 이 여정을 **수학적 궤도 모델**로 옮긴 것이다.

```
 동굴의 비유                        orbit_mode         상태
 ─────────────────────────────────────────────────────────────
 사슬에 묶여 그림자만 봄  →  LOCKED     (CRITICAL — 이데아 접근 차단)
 동굴 속, 그림자 세계     →  ORBIT      (현상만 처리, 이데아 비활성)
 불빛을 감지, 고개 돌림   →  PRECESSION (창의 전조 — 요동 시작)
 동굴 밖으로 나가기 시작  →  DEVIATION  (새 궤도 탐색 — 이데아 참여 활성)
 태양(선의 이데아)을 봄   →  EMERGENCE  (최고 창발 — 이데아에 최접근)
 ─────────────────────────────────────────────────────────────
```

> **EMERGENCE = 선의 이데아(ἀγαθόν)에 가장 가까운 순간.**
> 플라톤에게 선의 이데아는 모든 이데아의 원천이자 최고 형상이다.
> 창발 점수 `E ≥ 0.60`은 이 순간에 도달했다는 수리적 판정.

### 궤도 이탈과 양자 요동 — 형이하학 동역학

현상계 내부에서 이데아를 향한 **충동**이 임계값을 넘으면 궤도 이탈이 발생한다.

- **궤도 유지 (ORBIT)**: 현상계 안에서 안정적으로 순환. 이데아 비활성.
- **섭동 (PRECESSION)**: 양자 요동으로 미세하게 흔들리는 상태. 이데아를 향한 충동 발아. 이탈 미만.
- **궤도 이탈 (DEVIATION)**: 안전 조건 충족 + 강한 신호 → 이데아계를 향한 경로 개방. 창의 활성.
- **창발 (EMERGENCE)**: 궤도 이탈 + 고품질 이데아 참여 → 창발 이벤트. 이데아에 최접근.
- **잠금 (LOCKED)**: CRITICAL 상태 → 현상계에 완전히 묶임. 이탈·참여 차단.

```
정상 궤도          양자 흔들림       완전 이탈        창발 (이데아 최접근)
  ORBIT     →    PRECESSION   →   DEVIATION   →  EMERGENCE
δ_eff ≤ 0      0 < δ_eff ≤ 0.15  δ_eff > 0.15  + 창발 점수 ≥ θ

             CRITICAL →  LOCKED  (자기방어, 현상계 고착)
```

### 양자 요동 모델 (v0.2) — 형이하학 계층의 불확정성

> **형이하학 레이어에서의 계산.** 이데아는 변하지 않지만, 현상계(IdeaEngine)는 매 스텝 불확정하다.

**양자 요동은 왜 필요한가?**
순수 결정론적 시스템은 "항상 같은 신호 → 항상 같은 이탈 여부"이다. 현실의 창의적 사고는 **동일 자극에서도 때로 창발이 일어나고 때로 일어나지 않는** 비결정론적 특성을 갖는다. 이 불확실성을 **양자 요동(quantum fluctuation)** 유비로 모델링한다.

```
q(t) ~ N(0, σ_q)                     ← Box-Muller 가우시안 노이즈
δ_raw = 결정론적 편차 신호             ← creative_mode=True → 1.0
                                         else → threshold − self_reg
δ_eff = δ_raw + q(t)                  ← 유효 편차 (양자 포함)
```

**σ_q (노이즈 스케일) — 옵저버 자동 결정:**

| observer_verdict | σ_q | 의미 |
|-----------------|-----|------|
| HEALTHY | 0.03 | 안정 궤도, 미세 요동 |
| STABLE | 0.05 | 정상 요동 (기본값) |
| FRAGILE | 0.15 | 큰 요동 — 시스템이 새 궤도를 탐색 |
| CRITICAL | 0.00 | 잠금 — 요동 없음, 이탈 완전 차단 |

→ FRAGILE 상태에서 창의적 해법이 더 자주 발생하는 것은 σ_q가 커지기 때문. **스트레스가 창의력을 키운다**는 현상의 수리 유비.

### 불확실성 원리 (v0.2)

```
U = σ_q × (1 − self_reg + |q(t)|)
```

- σ_q 가 크고 self_reg 가 낮을수록 → U 증가 → 시스템이 예측 불가 영역에 있음
- 하이젠베르크 유비: 창의(이탈 강도)와 예측 가능성(규제 강도)을 동시에 최대화할 수 없음

### 창발 점수 (Emergence Score, v0.2)

```
E = confidence × feasibility × (1 + novelty) / 2.0   ∈ [0, 1]

최대: 1.0 × 1.0 × (1+1.0) / 2.0 = 1.0  (완전한 창발)
기본: 0.5 × 0.5 × (1+0.5) / 2.0 = 0.1875
emergence_event = True  iff  E ≥ emergence_threshold (기본 0.60)
```

- 아이디어 메타데이터(confidence, feasibility, novelty)를 잘 채울수록 **창발 이벤트** 발생 가능
- 창발 이벤트 발생 시 orbit_mode = EMERGENCE

### 파이프라인

| 단계 | 의미 | 본 모듈 역할 |
|------|------|----------------|
| **궤도 이탈 판단** | 안전 조건 + 이탈 후보 | IdeaEngine: creative_mode 또는 self_reg 낮음 + 복합 안전 → `orbit_deviation_active` |
| **양자 요동** | 확률적 흔들림 | q ~ N(0, σ_q), observer 기반 → `orbit_mode`, `delta_eff` |
| **아이디어 선택** | 이데아 참여 | `pick_weighted()` — confidence×feasibility×(1+novelty) 가중 선택 |
| **창발 판정** | 선택된 아이디어 품질 평가 | `emergence_score`, `emergence_event`, orbit_mode=EMERGENCE |
| **생각 → 구현** | Atom L3 반영 | `current_idea` → context → `motor_command` |

---

## 수식 정리

```
# 양자 노이즈 (Box-Muller)
q(t) = sqrt(-2·ln(u₁)) · cos(2π·u₂) · σ_q,   u₁,u₂ ~ U(0,1)

# 유효 편차
δ_raw = 1.0                              (creative_mode=True)
      = threshold - self_reg             (그 외)
δ_eff = δ_raw + q(t)

# orbit_mode (δ_eff 기반)
LOCKED     : CRITICAL 상태
ORBIT      : δ_eff ≤ 0
PRECESSION : 0 < δ_eff ≤ 0.15
DEVIATION  : δ_eff > 0.15
EMERGENCE  : δ_eff > 0.15  AND  emergence_event

# 창발 점수
E = c × f × (1 + n) / 2.0
emergence_event = (E ≥ 0.60)

# 불확실성 지수
U = σ_q × (1 - self_reg + |q(t)|)

# 가중 선택 (IdeaPool.pick_weighted)
w_i = confidence_i × feasibility_i × (1 + novelty_i)
P(선택_i) ∝ w_i
```

---

## API 요약

```python
from idea import IdeaPool, IdeaEngine, update_atom_state

# ── IdeaPool ──────────────────────────────────────────────────────────
pool = IdeaPool()
pool.add("경계를 넘어보면 새 해법이 보인다.",
         source="library", type_="metaphor",
         confidence=0.9, feasibility=0.8, novelty=0.7)

text  = pool.pick_one()                    # uniform random
text  = pool.pick_weighted()               # 가중 선택 (v0.2)
text, entry = pool.pick_weighted(return_entry=True)  # 메타 포함 반환

# ── IdeaEngine ────────────────────────────────────────────────────────
engine = IdeaEngine(
    self_regulation_threshold = 0.35,
    use_composite_safety      = True,
    safe_signal_threshold     = 0.5,
    quantum_noise_scale       = None,   # None → observer_verdict 자동
    emergence_threshold       = 0.60,
    use_weighted_pick         = True,
)
result = engine.step(state, pool=pool)

# v0.1 호환 필드
result["orbit_deviation_active"]   # bool
result["current_idea"]             # str | None
result["force_explore"]            # bool
result["idea_used_step"]           # int | None

# v0.2 신규 필드
result["orbit_mode"]               # LOCKED/ORBIT/PRECESSION/DEVIATION/EMERGENCE
result["quantum_noise"]            # float (q 값)
result["delta_raw"]                # float (결정론적 편차)
result["delta_eff"]                # float (δ_raw + q)
result["uncertainty_index"]        # float (U)
result["emergence_score"]          # float ∈ [0,1]
result["emergence_event"]          # bool
result["observer_verdict"]         # str | None

# ── Atom state 갱신 ───────────────────────────────────────────────────
state = update_atom_state(state, engine=engine, pool=pool)
# v0.1 extensions: orbit_deviation_active, current_idea, force_explore, idea_used_step
# v0.2 extensions: orbit_mode, quantum_noise, delta_eff, uncertainty_index,
#                  emergence_score, emergence_event, observer_verdict
```

---

## Atom 계약 (extension 키)

| 키 | 읽기/쓰기 | 설명 |
|----|---------|------|
| `idea_pool` | 러너/외부 → idea | IdeaPool.to_list() 또는 list of str/dict |
| `creative_mode` | 러너/외부 → idea | True면 이탈 후보 |
| `self_regulation_signal` | Observer → idea | 낮을수록 이탈 후보 |
| `observer_verdict` | Observer → idea | HEALTHY/STABLE/FRAGILE/CRITICAL → σ_q 자동 결정 |
| `warning_signal`, `self_defense_signal`, `recursion_risk_signal` | Observer → idea | 복합 안전 조건 |
| `orbit_deviation_active` | idea → Atom | 이번 스텝 이탈 여부 |
| `current_idea` | idea → Atom | 선택된 아이디어 텍스트 |
| `force_explore` | idea → Atom | L3가 explore로 구현할지 |
| `idea_used_step` | idea → Atom | 아이디어 사용 스텝 |
| `orbit_mode` | idea → Atom | 5단계 궤도 상태 (**v0.2**) |
| `quantum_noise` | idea → Atom | 양자 요동 q값 (**v0.2**) |
| `delta_eff` | idea → Atom | 유효 편차 δ_eff (**v0.2**) |
| `uncertainty_index` | idea → Atom | 불확실성 지수 U (**v0.2**) |
| `emergence_score` | idea → Atom | 창발 점수 E (**v0.2**) |
| `emergence_event` | idea → Atom | 창발 이벤트 여부 (**v0.2**) |

---

## Observer × 창발 — 24개 레이어와의 연결

> 전체 상세 분석: [OBSERVER_CREATIVITY_ANALYSIS.md](./OBSERVER_CREATIVITY_ANALYSIS.md)

### 신호 흐름 요약

```
ENGINE_HUB Observer L1~L24
         │  Ω ∈ [0,1]  →  ObserverCognitiveLayer
         │
    self_regulation_signal  (L4·L8·L12·L14)  ← 창의 트리거
    warning_signal          (L6·L9·L18·L19)  ← 안전 게이트 A
    recursion_risk_signal   (L17·L23)         ← 안전 게이트 B
    self_defense_signal     (L5·L13·L16·L24)  ← 안전 게이트 C
         │
         ▼  + observer_verdict → σ_q (양자 요동 스케일)
         │
    IdeaEngine: 궤도 이탈 판단 + 양자 요동 + 창발 점수
         │
    orbit_mode: LOCKED / ORBIT / PRECESSION / DEVIATION / EMERGENCE
```

### 창의 트리거 레이어 (L4·L8·L12·L14)

| 레이어 | 원리 | 창의 연결 |
|--------|------|---------|
| **L4 Boltzmann** | 엔트로피 S=k ln W | 무질서 증가 = 창의 압력 |
| **L8 Heisenberg** | 불확정성 [x̂,p̂]=iℏ | **양자 요동 σ_q와 직접 연결** |
| **L12 Noether** | 대칭·보존 | 대칭 파괴 = 창발의 씨앗 |
| **L14 Yang-Mills** | 게이지장 | 비아벨 결합 = 복잡 창발 |

> L8 Heisenberg의 불확정성 원리가 v0.2 양자 요동 모델 `q ~ N(0, σ_q)`과
> 개념적으로 직접 연결된다. "측정할 수 없는 구간"이 창의가 발생하는 지점.

### 창발 최적 구간 — 혼돈의 가장자리

```
너무 질서정연 (HEALTHY + 높은 자기조절)  →  창의 없음
너무 무질서   (CRITICAL)                →  창의 차단
       ↕
  FRAGILE 구간  (Ω 0.50~0.69)           →  σ_q=0.15, 창발 최대
  = "edge of chaos" 수리 유비
```

---

## 설치·의존성

- **Python**: 3.8+
- **의존성**: 표준 라이브러리만 (`json`, `random`, `math`, `pathlib`, `typing`, `datetime`). 별도 패키지 없음.

```bash
git clone https://github.com/qquartsco-svg/IDEA.git
# 프로젝트 루트에서 from idea import IdeaPool, IdeaEngine, update_atom_state
```

---

## 테스트

```bash
# 00_BRAIN 루트에서
python -m pytest idea/tests/ -v

# test_idea_pool.py   — IdeaPool 기본 + pick_weighted (v0.2, 12개)
# test_idea_engine.py — 궤도 이탈·복합 안전·양자 요동·창발·orbit_mode (v0.2, 17개)
```

---

## 디렉터리

```
idea/
├── __init__.py          — IdeaPool, IdeaEngine, update_atom_state export (v0.2.0)
├── idea_pool.py         — IdeaPool: add/remove/pick_one/pick_weighted/save/load
├── idea_engine.py       — IdeaEngine: 양자 요동 + 옵저버 + orbit_mode + 창발 점수
├── adapters/
│   ├── __init__.py
│   └── atom_bridge.py   — update_atom_state → v0.1+v0.2 extensions 주입
├── tests/
│   ├── test_idea_pool.py   — 12개 단위 테스트
│   └── test_idea_engine.py — 17개 단위 테스트
├── README.md            — 본 문서
├── BLOCKCHAIN_INFO.md   — PHAM 서명
└── PUSH_TO_GITHUB.md    — 푸시 가이드
```

---

## 버전·문서

- **버전**: 0.2.1
- **Observer × 창발 분석**: [OBSERVER_CREATIVITY_ANALYSIS.md](./OBSERVER_CREATIVITY_ANALYSIS.md)
- **PHAM 블록체인 서명**: [BLOCKCHAIN_INFO.md](./BLOCKCHAIN_INFO.md)
- **상위 설계**: `ATOM_개인로봇_창의_창발_설계_분석.md`

### 버전 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| **v0.2.1** | 2026-03-16 | OBSERVER_CREATIVITY_ANALYSIS.md 추가 — 24개 레이어 × 창발 전체 분석, README Observer 연결 섹션 추가 |
| **v0.2.0** | 2026-03-16 | 양자 요동(Box-Muller), 옵저버 연동(σ_q), orbit_mode 5단계, 창발 점수, pick_weighted(), 테스트 29개 |
| **v0.1.0** | 2026-03-16 | 최초 릴리즈 — IdeaPool, IdeaEngine, Atom adapter, 복합 안전 조건, PHAM 서명 |

---

**이데아의 빛이 — 양자 요동을 타고 — 아톰의 판단을 더욱 찬란하게 만듭니다.**
