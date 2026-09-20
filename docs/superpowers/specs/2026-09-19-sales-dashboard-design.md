# Design: ShopSmart Sales Dashboard

**Status:** Approved for planning
**Source PRD:** `prd/ecommerce-analytics.md`
**Milestones:** `TASKS.md` (TASK-1 through TASK-5)

## Summary

A single-page Streamlit dashboard that reads `data/sales-data.csv` and
shows two KPI cards (Total Sales, Total Orders), a monthly sales trend
line chart, and two sorted bar charts (sales by category, sales by
region). Built as two Python modules: a UI module and a data module,
with the data module fully covered by pytest.

## Decisions from clarifying questions

| Question | Decision |
|---|---|
| Trend chart granularity | Monthly (12 points from 482 transactions reads cleanly; PRD left this open) |
| Missing data file behavior | Friendly in-app error via `st.error` + `st.stop()`, not a raw traceback |
| Code structure | Two files: `app.py` (UI) + `data.py` (data/calculations), not a third `charts.py` |
| Dashboard title | "ShopSmart Sales Dashboard" (PRD text says ShopSmart; the ASCII mockup's "SHOPMART" header is treated as a typo) |
| Data module shape | Plain functions over a shared DataFrame, not a wrapper class — simpler and directly testable |
| CSV validation depth | Check the 8 required columns are present after load; no general-purpose schema validation |

## Architecture & components

```
app.py                 Streamlit UI: page config, title, KPI cards, charts, layout
data.py                load_data(), total_sales(), total_orders(),
                        sales_by_category(), sales_by_region(), monthly_trend()
tests/test_data.py     pytest tests for every function in data.py
data/sales-data.csv    (existing) source data
requirements.txt       streamlit, pandas, plotly, pytest
venv/                  local virtual environment (gitignored)
```

`app.py` calls into `data.py` for every number and every chart's
underlying data, then hands that to Plotly/Streamlit for rendering.
`data.py` has no Streamlit imports — it only knows about pandas —
which is what makes it testable without starting a server.

**Layout** (top to bottom, matching the PRD mockup): title → two KPI
metric cards side by side (Total Sales, Total Orders) → monthly trend
line chart (full width) → category bar chart and region bar chart side
by side, both sorted highest-to-lowest.

## Data flow & caching

1. `app.py` calls `data.load_data("data/sales-data.csv")` once at the
   top of the script.
2. `load_data` reads the CSV with pandas, parses `date` as a datetime
   column, checks the 8 required columns are present, and returns the
   DataFrame. Wrapped in `@st.cache_data` so Streamlit's rerun-the-
   whole-script-on-every-interaction model doesn't re-read the file
   from disk each time.
3. Everything downstream (`total_sales(df)`, `sales_by_category(df)`,
   etc.) takes that same DataFrame and returns a plain value (float,
   int) or a small aggregated DataFrame/Series, already sorted where
   the PRD asks for sorting.
4. `app.py` passes those results straight into `st.metric(...)` and
   `px.line(...)` / `px.bar(...)` calls. No calculation logic lives in
   `app.py` — it only formats and renders.

## Error handling

- **Missing/unparseable file:** `load_data` catches the file-not-found
  and parse-failure cases and raises a single custom exception,
  `DataLoadError`, with a clear message (e.g. `"Data file not found at
  data/sales-data.csv"` or `"Missing required column(s): ..."`).
  `data.py` never talks to Streamlit — it just raises.
- **In `app.py`:** the `load_data` call is wrapped in
  `try/except DataLoadError as e`, which calls `st.error(str(e))` then
  `st.stop()` to halt rendering the rest of the page. The user sees
  one readable message instead of a traceback.
- **No other error handling is planned.** The dataset is fixed and the
  calculations are simple aggregations that can't throw once the
  required columns are confirmed present.

## Testing

Every function in `data.py` gets a pytest test in `tests/test_data.py`,
using a small hand-built DataFrame fixture (a handful of rows spanning
2+ categories, regions, and months), not the real 482-row CSV, so
expected values are easy to hand-calculate and tests don't depend on
the data file changing later.

Planned tests:
- `test_total_sales` — sums `total_amount` correctly
- `test_total_orders` — counts rows correctly
- `test_sales_by_category` — aggregates and sorts descending by value
- `test_sales_by_region` — same, for region
- `test_monthly_trend` — aggregates `total_amount` by calendar month
- `test_load_data_missing_file` — raises `DataLoadError` for a
  nonexistent path
- `test_load_data_missing_column` — raises `DataLoadError` when a
  required column is absent

Chart rendering (`app.py`) is not unit tested — Streamlit/Plotly
components aren't meaningfully testable that way. Manual "run it and
look" checkpoints cover that instead.

## Milestone mapping

| TASKS.md milestone | Covered by |
|---|---|
| TASK-1: Project setup and data loading | `requirements.txt`, `venv/`, `app.py` skeleton + title, `load_data` + validation + error handling, its tests |
| TASK-2: KPI scorecards | `total_sales`, `total_orders` + tests; `st.metric` cards in `app.py` |
| TASK-3: Sales trend chart | `monthly_trend` + test; Plotly line chart in `app.py` |
| TASK-4: Category and region breakdowns | `sales_by_category`, `sales_by_region` + tests; two Plotly bar charts |
| TASK-5: Test and deploy | Full manual acceptance-criteria pass, `.gitignore` for `venv/`, deployment (marked as the user's to execute, from `main`, after merge) |

## Out of scope (per PRD Phase 2)

Authentication, real-time database integration, export, alerts,
filtering/date ranges, drill-down, mobile-responsive design.

## Ground rules for implementation

- Work on the existing `feature/sales-dashboard` branch; no git worktree.
- Plain Python virtual environment in `venv/` with `requirements.txt`
  (no uv or conda).
- Deployment is the plan's final step, marked as the user's to execute
  from `main` after merge — the plan stops there.
