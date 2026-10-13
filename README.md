# <Team name>: WACC for <Client firm>

> **CEO:** fill in every `<...>` below, then commit this file to `main`. It's the plan everyone (and every agent) works from.

## The question

What is <Client firm> (<TICKER>)'s weighted average cost of capital, and what does it mean for the hurdle rate on its new projects?

## The output (the one thing we ship)

A **WACC card**: one page, in our app, showing the WACC and every input behind it, each with its source.

`code/wacc.py` writes it as `outputs/wacc.csv`: **one row, these columns**. This is the contract between the developer and the product manager. Don't change it without telling each other.

| column | meaning |
|---|---|
| `ticker` | the client |
| `asof` | the date the returns end |
| `beta` | equity beta vs. SPY, daily returns, last 5 years |
| `rf`, `mrp` | risk-free rate, market risk premium |
| `cost_of_equity` | rf + beta × mrp |
| `rd`, `tax` | pre-tax cost of debt, tax rate |
| `w_e`, `w_d` | market-value weights of equity and debt (sum to 1) |
| `wacc` | w_e × cost_of_equity + w_d × rd × (1 − tax) |

`outputs/wacc_FAKE.csv` has the same columns with made-up numbers, so the app can be built before the real numbers exist.

## Who does what

| Role | Name | GitHub username | Branch | Owns |
|---|---|---|---|---|
| CEO | <name> | <username> | `main` (reviews and merges) | this README, reviewing every pull request |
| Developer | <name> | <username> | `dev-wacc` | `code/wacc.py` |
| Product manager | <name> | <username> | `pm-app` | `app.py` |
| Analyst | <name> | <username> | `analyst-inputs` | `inputs/assumptions.csv` (every number has a source) |

_Team of 3? The CEO is also the analyst._

## How to run it

```bash
pip install -r requirements.txt
python code/wacc.py        # writes outputs/wacc.csv
streamlit run app.py       # opens the app at localhost:8501
```

## Rules (for people and agents)

See `AGENTS.md`. Short version: work in your own branch, commit small, open a pull request, and never commit an API key.
