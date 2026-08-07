# Evidence

Committed verification records. Each file is evidence that a specific claim was
checked on a specific commit, retained so the claim can be audited later rather
than taken on trust.

**Sanitization is mandatory.** These files are committed to a public repository.
They record *what was verified*, never *whose machine did it*. Excluded by
policy: usernames, absolute filesystem paths, credentials, tokens, device
serials, network identifiers, and any machine detail not needed to reproduce the
result. `verify_native_macos.sh` emits a sanitized report by design; the raw
run log stays untracked (`.gitignore`).

| File | Claim verified | Commit |
|---|---|---|
| `2026-08-07-native-macos-verification.md` | The pinned dependency set installs and the supported stack passes natively on macOS/arm64 with Python 3.11 | `68b8c3d` |
