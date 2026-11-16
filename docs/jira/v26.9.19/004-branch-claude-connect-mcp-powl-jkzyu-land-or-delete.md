# pm4py: land or delete remote branch `claude/connect-mcp-powl-jkzyu`

- Standing: OPEN
- Created: 2026-09-19 (v26.9.19 gh survey wave)
- Source: remote branch `claude/connect-mcp-powl-jkzyu` — not merged into `release`, no open PR
- Evidence: `git branch -r --no-merged origin/release` lists it; absent from `gh pr list` heads

## Work to complete
- Decide: open a PR (`gh pr create -R seanchatmangpt/pm4py --head claude/connect-mcp-powl-jkzyu`) or delete (`git push origin --delete claude/connect-mcp-powl-jkzyu`).
- If superseded, delete; otherwise land through review.

## Acceptance
- After `git fetch --prune`, `git branch -r --no-merged origin/release` no longer lists `claude/connect-mcp-powl-jkzyu`.

## History
- 2026-09-19 | OPEN | survey found PR-less unmerged branch | claude/connect-mcp-powl-jkzyu | decision pending
