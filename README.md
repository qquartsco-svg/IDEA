# IDEA — 이데아(형상) 독립 모듈

**플라톤의 이데아(ἰδέα)를 현대 인지 아키텍처로 옮긴 아이디어 저장·참여 엔진.**  
가변적인 현상(Perception)에만 머물지 않고, **보편적·본질적 패턴(이데아)**를 저장했다가 필요할 때 현재 판단 궤적에 **참여(μέθεξις)**시키는 구조를 제공합니다.

- **한 줄 정의**: "질서(궤도 유지) 속의 자유(창발)" — **안정 궤도 위에서만** 허용된 궤도 이탈 시, 이데아 풀에서 하나를 골라 생각(맥락)에 넣고 구현(motor_command)으로 이어지게 하는 모듈.
- **역할**: IdeaPool(저장소) + IdeaEngine(궤도 이탈 판단·복합 안전 조건·선택) + Atom 어댑터. 표준 라이브러리만 사용해 Atom·Observer·Library에 **무의존**으로 동작.

---

## 개념

### 플라톤의 이데아(ἰδέα)와의 연결

- **이데아** = 영어 "idea"의 어원. **불변·보편·이성적** 형상(Form). 개별 사물은 이데아에 **참여**함으로써 그 본질을 일부 갖는다.
- **우리 매핑**:
  - **이데아(형상)** ↔ `IdeaPool`에 저장되는 문장·요약 (보편 패턴)
  - **개별자(현상)** ↔ `state_vector`, `perception`, `memory_info` (한 스텝의 구체적 상태)
  - **참여(μέθεξις)** ↔ `IdeaPool.pick_one()`으로 하나를 골라 현재 맥락에 넣는 행위 → `current_idea` → L3 맥락 → `motor_command`

즉, 이 모듈은 "이데아가 다뤄지는 층" — **형이상학적 유비** 위에 구현된 창의·창발 계층입니다.

### 궤도 이탈과 창발

- **궤도 유지**: 목표·제약을 지키며 예측 가능하게 동작 (기본).
- **궤도 이탈**: 안정 궤도에서 잠시 벗어나 **새 경로·새 조합**을 시도하는 것. 창발·창의는 이 "가끔의 이탈"과 연결됩니다.
- **제어된 이탈**: 단순 "랜덤"이 아니라, **복합 안전 조건**을 만족할 때만 이탈을 허용합니다.

### 파이프라인: 궤도 이탈 → 창의력 → 아이디어 → 생각 → 구현

| 단계 | 의미 | 본 모듈 역할 |
|------|------|----------------|
| **궤도 이탈** | 이탈 허용 조건 충족 | IdeaEngine: creative_mode 또는 self_regulation 낮음 + **복합 안전**(warning/self_defense/recursion_risk 낮음) → `orbit_deviation_active` |
| **창의력 발휘** | 이탈 시 탐색·이데아 참여 허용 | pool에서 하나 선택 → `current_idea`, `force_explore=True` |
| **아이디어** | 보편 패턴이 "지금"에 참여 | `current_idea` (문자열) |
| **생각** | 의사결정 맥락에 반영 | Atom L3가 context에 current_idea 포함, force_explore면 action=explore |
| **구현** | 행동으로의 귀결 | `motor_command` (Atom L3 출력) |

---

## 로직

### IdeaPool — 이데아 저장소

- **저장 단위**: 문자열 또는 dict. **저장 규칙** 권장으로 품질 유지.
  - `text`: 본문 (필수)
  - `source`: library | recall | observer-trigger
  - `type`: metaphor | solution | experiment | question
  - `confidence`, `feasibility`, `novelty`: 0~1 (선택)
  - `created_at`: ISO 타임스탬프 (선택)
- **연산**: `add`, `remove`, `pick_one(max_len=None)`, `to_list()`, `save(path)`, `load(path)`, `IdeaPool.from_list(raw)`.

### IdeaEngine — 궤도 이탈 판단 + 선택

- **이탈 후보 조건**: `creative_mode=True` **또는** `self_regulation_signal < self_regulation_threshold`(기본 0.35).
- **복합 안전 조건**(기본 켜짐): 위가 참이어도 **warning_signal**, **self_defense_signal**, **recursion_risk_signal**이 모두 `safe_signal_threshold`(기본 0.5) **미만**일 때만 `orbit_deviation_active=True`.  
  → 단일 신호만 보면 위험 구간에서도 탐색을 키울 수 있으므로, 복합 조건으로 "안전한 궤도 이탈"만 허용.
- **선택**: 이탈 시 `pool.pick_one(max_idea_len)` → `current_idea`, `force_explore=True`.
- **입력**: state(get_extension 지원), pool(생략 시 state의 idea_pool로 IdeaPool.from_list).
- **출력**: `{ orbit_deviation_active, current_idea, force_explore, idea_used_step }`.

### Atom 연동

- **update_atom_state(state, engine=None, pool=None)**: IdeaEngine 한 스텝 실행 후 state에 `orbit_deviation_active`, `current_idea`, `force_explore`, `idea_used_step` 설정.
- Atom의 **CreativeIdeaBridgeLayer**는 이 함수를 호출합니다 (idea 모듈 설치 시).

---

## 설치·의존성

- **Python**: 3.8+
- **의존성**: 표준 라이브러리만 사용 (json, random, pathlib, typing, datetime). 별도 패키지 없음.

```bash
git clone https://github.com/qquartsco-svg/IDEA.git
cd IDEA
# 사용 시 프로젝트 루트에서 sys.path에 IDEA 상위 경로 추가 후: from idea import IdeaPool, IdeaEngine, update_atom_state
```

---

## API 요약

```python
from idea import IdeaPool, IdeaEngine, update_atom_state

# 풀 생성·추가
pool = IdeaPool()
pool.add("경계를 넘어보면 새 해법이 보인다.", source="library", type_="metaphor")
pool.add({"text": "두 대립을 제3의 관점으로 묶는다.", "type": "solution"})

# 엔진 한 스텝 (state는 get_extension/set_extension 있는 객체)
engine = IdeaEngine(self_regulation_threshold=0.35, use_composite_safety=True)
result = engine.step(state, pool=pool)
# result["orbit_deviation_active"], result["current_idea"], result["force_explore"]

# Atom state 갱신 (extensions에 결과 기록)
state = update_atom_state(state, engine=engine, pool=pool)
```

---

## Atom 계약 (extension 키)

| 키 | 쓰기 | 설명 |
|----|------|------|
| `idea_pool` | 러너/외부 | IdeaPool.to_list() 또는 list of str/dict |
| `creative_mode` | 러너/외부 | True면 이탈 후보 |
| `self_regulation_signal` | Observer 등 | 낮을수록 이탈 후보 |
| `warning_signal`, `self_defense_signal`, `recursion_risk_signal` | Observer 등 | 복합 안전 조건 (낮을 때만 이탈 허용) |
| `orbit_deviation_active` | idea | 이번 스텝 이탈 여부 |
| `current_idea` | idea | 선택된 아이디어 텍스트 |
| `force_explore` | idea | L3가 explore로 구현할지 |
| `idea_used_step` | idea | 아이디어 사용 스텝 |

---

## 테스트

```bash
# 00_BRAIN 루트에서 (idea가 path에 있도록)
python -m pytest idea/tests/ -v
```

- `test_idea_pool.py`: IdeaPool add/remove/pick_one/to_list/save/load, from_list
- `test_idea_engine.py`: 궤도 이탈 조건, 복합 안전 조건(경고 높으면 이탈 비허용, 전부 낮으면 허용)

---

## 버전·문서

- **버전**: 0.1.0
- **PHAM 블록체인 서명**: [BLOCKCHAIN_INFO.md](./BLOCKCHAIN_INFO.md)
- **상위 설계**: 00_BRAIN 문서 `ATOM_개인로봇_창의_창발_설계_분석.md` (이데아·형이상학 연결, 복합 안전 조건, L9 의미/구조 구분, idea_pool 구조화, novelty×feasibility)

---

**이데아의 빛이 아톰의 판단을 더욱 찬란하게 만듭니다.**
