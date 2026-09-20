# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a student-facing tutorial (see `README.md`) that teaches a professional AI-assisted development workflow: PRD → `TASKS.md` → brainstorming → writing-plans → executing-plans → commit → push → review/merge → deploy, using Superpowers skills for Claude Code. The tutorial's build target is a small Streamlit sales dashboard, built under that workflow on the `feature/sales-dashboard` branch.

## Commands

```bash
source venv/bin/activate                        # activate the venv (plain venv, no uv/conda)
pip install -r requirements.txt                 # install dependencies (streamlit, pandas, plotly, pytest)
streamlit run app.py                            # run the dashboard locally at http://localhost:8501
pytest                                           # run the full test suite
pytest tests/test_data.py -v                     # run the data-layer tests, verbose
pytest tests/test_data.py::test_monthly_trend    # run a single test
```

No lint/build step is configured for this project.

## Architecture

The dashboard is split into two modules, per the design doc (`docs/superpowers/specs/2026-09-19-sales-dashboard-design.md`) and plan (`docs/superpowers/plans/2026-09-19-sales-dashboard.md`):

- **`data.py`** — pure pandas: `load_data`, `total_sales`, `total_orders`, `monthly_trend`, `sales_by_category`, `sales_by_region`. No Streamlit imports, ever — that's what makes it unit-testable without a server. Every function here has a pytest test in `tests/test_data.py`, using a small hand-built fixture DataFrame (not the real CSV), so expected values are hand-calculable.
- **`app.py`** — Streamlit UI only: page config, `@st.cache_data`-wrapped data loading, `st.metric` KPI cards, Plotly (`plotly.express`) charts. Contains no calculation logic — it only calls into `data.py` and formats/renders the result. Not unit tested; verified by running the app and checking the page.

**Error handling:** `data.py` raises one custom exception, `DataLoadError`, for any load failure (missing file, missing required column) with a human-readable message — it never imports or talks to Streamlit. `app.py` catches it once at load time, calls `st.error(str(e))` then `st.stop()`, so the user sees one readable message instead of a traceback. No other error handling is planned: the dataset is fixed and the aggregations can't throw once required columns are validated.

**Data contract:** `data/sales-data.csv` must have exactly the 8 columns in `data.REQUIRED_COLUMNS`: `date, order_id, product, category, region, quantity, unit_price, total_amount`. Full spec in `prd/ecommerce-analytics.md`.

## Task tracking workflow

Work is tracked in `TASKS.md`, a Markdown kanban board (`To Do` / `In Progress` / `Done` sections) with milestone IDs `TASK-1` through `TASK-5`. Conventions this repo follows:

- Every commit message is prefixed with the milestone ID it belongs to, e.g. `TASK-2: add total_sales and total_orders calculations`.
- Moving a milestone between board sections is its own commit (e.g. `TASK-3: move to In Progress on task board`), separate from the code commits implementing it.
- A milestone only moves to `Done` once its acceptance-criteria checkboxes are checked, the app runs locally, and everything is committed with its ID — see the `Definition of Done` at the top of `TASKS.md`.
- Each `Done` entry records the hash of its last *code* commit (not a board-move commit) and a `Notes:` line.
- TASK-5's final acceptance criterion — deployment to Streamlit Community Cloud — is explicitly the user's step to run from `main` after merge, not something to do as part of implementing the plan (see the plan's Task 11).

The implementation plan and design doc under `docs/superpowers/` are the source of truth for what each `TASK-N` covers and its step-by-step build order; check them before starting a new milestone.

## Lessons

- Before running `streamlit run` on a new machine, pre-set `~/.streamlit/credentials.toml` with a blank email. Otherwise the first run hangs on an interactive onboarding prompt asking for an email — a one-time machine setting outside this repo, not a code fix (from `TASKS.md`'s TASK-1 notes).
