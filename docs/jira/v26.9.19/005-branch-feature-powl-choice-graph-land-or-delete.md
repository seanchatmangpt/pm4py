# pm4py: land or delete remote branch `feature/powl-choice-graph`

- Standing: OPEN
- Created: 2026-09-19 (v26.9.19 gh survey wave)
- Source: remote branch `feature/powl-choice-graph` — not merged into `release`, no open PR
- Evidence: `git branch -r --no-merged origin/release` lists it; absent from `gh pr list` heads

## Work to complete
- Decide: open a PR (`gh pr create -R seanchatmangpt/pm4py --head feature/powl-choice-graph`) or delete (`git push origin --delete feature/powl-choice-graph`).
- If superseded, delete; otherwise land through review.

## Acceptance
- After `git fetch --prune`, `git branch -r --no-merged origin/release` no longer lists `feature/powl-choice-graph`.

## History
- 2026-09-19 | OPEN | survey found PR-less unmerged branch | feature/powl-choice-graph | decision pending
