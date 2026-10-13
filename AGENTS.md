# Rules for this repo (humans and coding agents)

Coding agents (Codex, Claude Code, Copilot) read this file before they work. Humans should too.

## The project

`README.md` is the plan. Read it first. The output contract is the table of columns for `outputs/wacc.csv`. Don't change those columns unless the README changes first.

## Git

- **Never commit directly to `main`.** Work in your own branch (see the README's roles table), then open a pull request.
- **Never force-push** (`git push --force`) and never rewrite shared history (`git reset --hard` on a pushed branch, `git rebase` of a shared branch) without a human's OK. Those can erase a teammate's work.
- Commit small, logical steps with messages that say what changed ("Estimate beta from 5y daily returns", not "update").
- Before you start work each session: `git switch main`, `git pull`, then `git switch <your-branch>` and `git merge main`.
- Only edit the files your role owns. If you need a change in someone else's file, ask them (or open an issue).

## Code

- Relative paths only (`inputs/assumptions.csv`), never `C:/Users/...`.
- In `inputs/assumptions.csv`, keep every `source` in double quotes. Sources often contain commas, and an unquoted comma breaks the file for `wacc.py` and the app.
- Run everything from the repo root.
- Keep `app.py` light: it only reads files from `outputs/` and `inputs/`. No downloads and no model estimation inside the app.
- Add checks (`assert`) for things that would silently break the answer: missing returns, weights that don't sum to 1, a WACC outside 0–25%.

## Secrets

- **Never commit an API key.** Keys go in `.env` (already in `.gitignore`) or in Streamlit's secrets. This project shouldn't need any.
