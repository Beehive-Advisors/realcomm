# CLAUDE.md — realcomm repo

Guidance for Claude (Cowork / Claude Code) when working in this repository.
These rules exist because of real failures. Follow them to avoid repeating them.

## Repo facts
- Remote: `https://github.com/Beehive-Advisors/realcomm.git`
- Default branch: `master`
- Lives on Windows at `C:\Users\acocc\Downloads\realcomm`, mounted into the Linux sandbox.
- Commit author identity: **Jacob Coccari <jacob.coccari@gmail.com>**

## RULE 1 — Never run git WRITE commands against this repo from the sandbox
The repo's `.git` directory is shared between two git installations: the user's
Windows Git (MINGW64) and the sandbox's Linux git, over a virtualized mount that
does NOT sync reliably. Running `git add` / `git commit` / `git checkout` / `git reset`
from the sandbox will:
- fail to read freshly-moved/created files (stale mount cache → `open(...): No such file or directory`), and/or
- corrupt or be unable to parse `.git/index` (e.g. `fatal: unknown index entry format 0x31310000`).

Read-only checks (`git status`, `git ls-remote`, `git log`, reading `.git/config`)
are usually fine, but if any of them error with index/format/ENOENT messages, STOP
and treat it as the mount problem — do not retry or "fix" it from the sandbox.

**All staging, committing, branching, and pushing for this repo must be done by the
user on their own machine.** Claude's job is to hand the user exact, correct commands.

## RULE 2 — Pushing requires the user's machine
The sandbox has no GitHub credentials (no credential helper, no token, no `gh`).
`git push` from the sandbox fails (`could not read Username for 'https://github.com'`).
Pushes happen on the user's machine, where the Windows credential store is configured.

## RULE 3 — Verify git identity BEFORE telling the user to commit
The user's global git identity has been unset, which causes commits to fail silently:
`Author identity unknown ... fatal: unable to auto-detect email address`. When this
happens, a follow-up `git push` misleadingly prints `Everything up-to-date` because
no commit was created. Always have identity configured first:
```
git config --global user.email "jacob.coccari@gmail.com"
git config --global user.name "Jacob Coccari"
```

## RULE 4 — When a push looks like a no-op, check that the commit actually happened
"Everything up-to-date" + a prior error almost always means the commit was rejected
(usually the identity issue in Rule 3). Confirm with `git log --oneline -1` before
declaring success.

## Standard "commit & push" block to give the user (run on their machine)
```
cd "C:\Users\acocc\Downloads\realcomm"
git config --global user.email "jacob.coccari@gmail.com"
git config --global user.name "Jacob Coccari"
git add -A
git commit -m "<message>"
git push origin master
```

## Notes
- Empty directories are not tracked by git; add a `.gitkeep` if an empty folder must appear on GitHub.
- `.gitignore` ignores `*:Zone.Identifier` (Windows download-origin metadata) and `.DS_Store`.
