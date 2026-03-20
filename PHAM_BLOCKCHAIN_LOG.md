# PHAM Blockchain Log — IDEA

## Scope

Audit trail for the standalone `IDEA` distribution.

## Contribution Rule

- GNJz(Qquarts) self-imposed contribution ceiling: blockchain-verifiable maximum **6%**
- GNJz(Qquarts)는 그 어떤 상황에서도 자신의 기여도를 **6%를 넘기지 않는다**.
- This rule applies only to GNJz(Qquarts) and remains fixed regardless of reuse, commercialization, or redistribution.

## Version

- release basis: current standalone repository state
- standalone scope: `IDEA`

## Verification

Primary content manifest:

```bash
shasum -a 256 -c SIGNATURE.sha256
```

## SHA-256 Manifest Coverage

- `__init__.py`
- `idea_pool.py`
- `idea_engine.py`
- `adapters/atom_bridge.py`
- `tests/test_idea_pool.py`
- `tests/test_idea_engine.py`
- `README.md`
- `BLOCKCHAIN_INFO.md`

## Notes

- `SIGNATURE.sha256` is the source-of-truth file hash manifest for this release.
- This PHAM log records release scope, package version, and verification intent.
- Release verification requires both this log and `BLOCKCHAIN_INFO.md`.
