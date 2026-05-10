# AGENTS.md

Single-file Streamlit app (`math_tool.py`) for tracking & visualizing math wrong-question statistics. UI is Chinese.

## Quick start

```bash
source .venv/bin/activate
streamlit run math_tool.py
```

Python 3.13.11, venv at `.venv/`. Dependencies: streamlit, pandas, plotly.

## Data

- `wrong_questions.csv` — persistent data, committed to repo.
- Columns: `date`, `q_type`, `question`, `ans_wrong`, `ans_right`, `error_type`, `notes`.
- `load_data()` handles both legacy (Chinese) and current (English) column headers, and auto-initializes an empty DataFrame if the file is missing. The CSV currently has both header sets (legacy first, current second).
- In-memory state via `st.session_state.df`; every add/edit/delete saves back to CSV immediately.

## Conventions

- All UI strings are in Chinese. Data file name and column names in code are in English.
- No test, lint, typecheck config, or CI exists.
