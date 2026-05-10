# AGENTS.md

Single-file Streamlit app (`math_tool.py`) for tracking & visualizing math wrong-question statistics. UI is Chinese.

## Quick start

```bash
source .venv/bin/activate
streamlit run math_tool.py
```

Python 3.13.11, venv at `.venv/`. Dependencies: streamlit, pandas, plotly, PyGithub.

## Data

- `wrong_questions.csv` — persistent data, committed to repo.
- Columns: `date`, `q_type`, `question`, `ans_wrong`, `ans_right`, `error_type`, `notes`.
- `load_data()` handles both legacy (Chinese) and current (English) column headers, and auto-initializes an empty DataFrame if the file is missing. The CSV currently has both header sets (legacy first, current second).
- In-memory state via `st.session_state.df`; every add/edit/delete saves back to CSV immediately.

## Streamlit Cloud 部署

- 仓库：`zcchm/math-wrong-questions`
- 依赖写于 `requirements.txt` ，入口文件自动识别为 `math_tool.py`
- 持久化策略：每次修改通过 PyGithub 将 CSV 提交回仓库
- 需在 Streamlit Secrets 中设置 `GITHUB_TOKEN`（classic token，scope: `repo`）
- 本地开发时也可在 `.streamlit/secrets.toml` 中设置同名字段
- 若没有 token，自动回退到本地 CSV 读写

## Conventions

- All UI strings are in Chinese. Data file name and column names in code are in English.
- No test, lint, typecheck config, or CI exists.
