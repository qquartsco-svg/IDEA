# IDEA 모듈 — GitHub 푸시 방법

**대상 레포**: https://github.com/qquartsco-svg/IDEA

---

## 방법 1: IDEA 레포를 클론한 뒤 내용 동기화 후 푸시

```bash
# 1) IDEA 레포 클론 (한 번만)
cd /Users/jazzin/Desktop
git clone https://github.com/qquartsco-svg/IDEA.git IDEA-repo
cd IDEA-repo

# 2) 00_BRAIN/idea/ 내용을 여기로 복사 (덮어쓰기)
rsync -av --exclude='.git' /Users/jazzin/Desktop/00_BRAIN/idea/ ./
# 또는
# cp -R /Users/jazzin/Desktop/00_BRAIN/idea/* ./
# cp /Users/jazzin/Desktop/00_BRAIN/idea/.gitignore ./   # 있으면

# 3) 커밋 및 푸시
git add -A
git status
git commit -m "idea v0.1.0: IdeaPool, IdeaEngine, Atom adapter, PHAM 서명, README·BLOCKCHAIN_INFO"
git push origin main
# (기본 브랜치가 master면 git push origin master)
```

---

## 방법 2: 00_BRAIN 루트에서 subtree push (이미 remote 설정된 경우)

IDEA가 00_BRAIN 안에 있고, 별도 remote만 추가해 두었다면:

```bash
cd /Users/jazzin/Desktop/00_BRAIN
git remote add idea-repo https://github.com/qquartsco-svg/IDEA.git   # 한 번만
git subtree push --prefix=idea idea-repo main
```

---

## 푸시 전 확인

- [ ] `idea/README.md` — 개념·로직·API 설명
- [ ] `idea/BLOCKCHAIN_INFO.md` — PHAM 서명·버전·구성
- [ ] `idea/tests/` — 테스트 통과 (`pytest idea/tests/ -v`)
- [ ] `idea/__init__.py`, `idea_pool.py`, `idea_engine.py`, `adapters/` 포함
