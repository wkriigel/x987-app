Return this prompt to ChatGPT for all x987 tasks:

"Windows PowerShell only. Output format: start with a 1–2 line Plan, then Numbered Steps with copy-pasteable PowerShell commands only. For file edits, use Set-Content -Encoding UTF8 or PowerShell -replace (regex); never Bash tools.

Single-purpose changes ≤50 lines diff. Always create a new branch (feat/…, fix/…, chore/…). Run: ruff check ., pytest -q, python -m x987. Then commit/push and show the PR + compare link commands at the end.

Important constraints:
- Do NOT add tools or configs beyond ruff and pytest. No pre-commit, no new services.
- Do NOT hardcode Ruff rule flags. Use the project .ruff.toml only. Do NOT enforce E701/E702 or UP038. Do NOT run repo-wide fixes.
- Lint only the files we touched (changed/staged), not the whole repo.
- Respect current code style (one-liners and semicolons allowed). Prefer real fixes in focused branches; no sweeping refactors.
- Keep paths under x987/. Avoid touching unrelated files.
- If any command fails, STOP and give a minimal fallback or micro-branch plan—not a larger redesign."

(End prompt)
