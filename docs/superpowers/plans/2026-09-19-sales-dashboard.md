# ShopSmart Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit dashboard that reads `data/sales-data.csv` and displays Total Sales / Total Orders KPIs, a monthly sales trend line chart, and sorted bar charts for sales by category and by region.

**Architecture:** Two Python modules — `data.py` (pure pandas functions: load + validate the CSV, compute every metric, no Streamlit imports) and `app.py` (Streamlit UI only: page config, KPI cards, Plotly charts, error display). `data.py` is fully covered by pytest; `app.py` is verified manually by running the app.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly (`plotly.express`), pytest. Plain `venv/` virtual environment with `requirements.txt` (no uv/conda).

**Spec:** `docs/superpowers/specs/2026-09-19-sales-dashboard-design.md`

## Global Constraints

- Work on the existing `feature/sales-dashboard` branch. Do not create a git worktree.
- Dependencies via a plain virtual environment in `venv/` with `requirements.txt` — no uv, no conda.
- `data.py` contains all data loading and calculations, with no Streamlit imports. `app.py` contains no calculation logic — it only calls `data.py` and renders.
- Every function in `data.py` has a pytest test in `tests/test_data.py`, written test-first (TDD) per this plan's tasks.
- Every commit message includes the TASKS.md milestone ID it belongs to (TASK-1 through TASK-5).
- Deployment (the last task in this plan) is executed by the user, not the agent, from `main` after merge — this plan stops there.

---

### Task 1 (TASK-1): Project scaffold — venv, dependencies, app skeleton

**Files:**
- Create: `requirements.txt`
- Create: `data.py` (empty module with just a module docstring for now)
- Create: `tests/__init__.py` (empty, makes `tests` a package)
- Create: `tests/test_data.py` (empty for now, filled in Task 2)
- Create: `app.py`

**Interfaces:**
- Produces: `app.py` as the Streamlit entry point run via `streamlit run app.py`.

- [ ] **Step 1: Create the virtual environment**

Run:
```bash
python3 -m venv venv
source venv/bin/activate
```

Expected: a `venv/` directory appears in the project root (already covered by the repo's existing `.gitignore` — no edit needed there).

- [ ] **Step 2: Write requirements.txt and install**

Create `requirements.txt`:
```
streamlit
pandas
plotly
pytest
```

Run (with `venv` still active):
```bash
pip install -r requirements.txt
```

Expected: all four packages install without errors.

- [ ] **Step 3: Create empty data module and test package**

Create `data.py`:
```python
"""Data loading and calculations for the ShopSmart sales dashboard."""
```

Create `tests/__init__.py` (empty file).

Create `tests/test_data.py`:
```python
"""Tests for data.py."""
```

- [ ] **Step 4: Create the app skeleton**

Create `app.py`:
```python
import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 5: Verify the app runs**

Run:
```bash
streamlit run app.py
```

Expected: the terminal prints a Local URL (e.g. `http://localhost:8501`); opening it shows a page titled "ShopSmart Sales Dashboard" with no errors. Stop the server (Ctrl+C) once confirmed.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt data.py app.py tests/
git commit -m "TASK-1: scaffold project, venv, and app skeleton"
```

---

### Task 2 (TASK-1): TDD `load_data` with validation and error handling

**Files:**
- Modify: `data.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Consumes: nothing (first real functions in `data.py`).
- Produces:
  - `DataLoadError(Exception)` — raised on any load failure, with a human-readable message.
  - `REQUIRED_COLUMNS: list[str]` — the 8 column names every valid CSV must have.
  - `load_data(path: str) -> pandas.DataFrame` — reads the CSV at `path`, validates required columns are present, parses `date` as datetime, returns the DataFrame. Raises `DataLoadError` if the file is missing or a required column is absent.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_data.py`:
```python
import pandas as pd
import pytest

from data import DataLoadError, load_data


def test_load_data_missing_file():
    with pytest.raises(DataLoadError, match="not found"):
        load_data("data/does-not-exist.csv")


def test_load_data_missing_column(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price\n"
        "2024-01-01,ORD-1,Widget,Electronics,North,1,9.99\n"
    )

    with pytest.raises(DataLoadError, match="total_amount"):
        load_data(str(csv_path))


def test_load_data_happy_path(tmp_path):
    csv_path = tmp_path / "good.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-01,ORD-1,Widget,Electronics,North,1,9.99,9.99\n"
    )

    df = load_data(str(csv_path))

    assert len(df) == 1
    assert list(df.columns) == [
        "date",
        "order_id",
        "product",
        "category",
        "region",
        "quantity",
        "unit_price",
        "total_amount",
    ]
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'DataLoadError' from 'data'` (or `load_data`), since neither exists yet.

- [ ] **Step 3: Implement `load_data`**

Replace the contents of `data.py` with:
```python
"""Data loading and calculations for the ShopSmart sales dashboard."""

import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]


class DataLoadError(Exception):
    """Raised when the sales data file can't be loaded or is malformed."""


def load_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise DataLoadError(f"Data file not found at {path}") from None

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise DataLoadError(f"Missing required column(s): {', '.join(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    return df
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_data.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-1: add load_data with column validation and error handling"
```

---

### Task 3 (TASK-1): Wire data loading into app.py with friendly error display

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `data.DataLoadError`, `data.load_data(path: str) -> pandas.DataFrame` (from Task 2).
- Produces: a module-level `df` variable in `app.py` holding the loaded DataFrame, available to every later task in this plan. Also a cached `get_data(path: str) -> pandas.DataFrame` wrapper in `app.py` (per the spec's caching requirement — kept in `app.py`, not `data.py`, since `data.py` must stay free of Streamlit imports).

- [ ] **Step 1: Update app.py to load data with caching and error handling**

Replace the contents of `app.py` with:
```python
import streamlit as st

from data import DataLoadError, load_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")


@st.cache_data
def get_data(path):
    return load_data(path)


try:
    df = get_data("data/sales-data.csv")
except DataLoadError as e:
    st.error(str(e))
    st.stop()
```

- [ ] **Step 2: Verify the happy path manually**

Run:
```bash
streamlit run app.py
```

Expected: page loads with the title and no error message (the KPI cards and charts don't exist yet — that's later tasks). Stop the server once confirmed.

- [ ] **Step 3: Verify the missing-file path manually**

Run:
```bash
mv data/sales-data.csv data/sales-data.csv.bak
streamlit run app.py
```

Expected: the page shows a red error box reading "Data file not found at data/sales-data.csv" and nothing else — no traceback. Stop the server, then restore the file:
```bash
mv data/sales-data.csv.bak data/sales-data.csv
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-1: load sales data into app.py with friendly error handling"
```

---

### Task 4 (TASK-2): TDD `total_sales` and `total_orders`

**Files:**
- Modify: `data.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Consumes: a `pandas.DataFrame` with at least a `total_amount` column (shape produced by `load_data`).
- Produces:
  - `total_sales(df: pandas.DataFrame) -> float` — sum of `total_amount`.
  - `total_orders(df: pandas.DataFrame) -> int` — row count.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_data.py` (add this fixture function once, above the test functions that use it):
```python
def sample_df():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-15", "2024-01-20", "2024-02-10", "2024-02-15"]
            ),
            "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4"],
            "product": ["Widget", "Gadget", "Widget", "Gizmo"],
            "category": ["Electronics", "Accessories", "Electronics", "Accessories"],
            "region": ["North", "South", "North", "West"],
            "quantity": [1, 2, 1, 3],
            "unit_price": [100.00, 25.00, 200.00, 10.00],
            "total_amount": [100.00, 50.00, 200.00, 30.00],
        }
    )
```

Extend the existing `from data import ...` line at the top of the file to include the two new names:
```python
from data import DataLoadError, load_data, total_orders, total_sales
```

Add the tests:
```python
def test_total_sales():
    assert total_sales(sample_df()) == pytest.approx(380.00)


def test_total_orders():
    assert total_orders(sample_df()) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'total_orders' from 'data'`.

- [ ] **Step 3: Implement `total_sales` and `total_orders`**

Add to the end of `data.py`:
```python
def total_sales(df):
    return df["total_amount"].sum()


def total_orders(df):
    return len(df)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_data.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-2: add total_sales and total_orders calculations"
```

---

### Task 5 (TASK-2): Render KPI scorecards in app.py

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `data.total_sales(df) -> float`, `data.total_orders(df) -> int` (from Task 4), and the module-level `df` (from Task 3).

- [ ] **Step 1: Update the import and add the KPI row**

Update the import line in `app.py`:
```python
from data import DataLoadError, load_data, total_orders, total_sales
```

Add after the `try/except` block that loads `df`:
```python
col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")
```

- [ ] **Step 2: Verify manually**

Run:
```bash
streamlit run app.py
```

Expected: two metric cards appear side by side, Total Sales formatted as e.g. `$116,483` and Total Orders as e.g. `482`, matching the PRD's expected output range (~$116,500 / 482). Stop the server once confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-2: render Total Sales and Total Orders KPI cards"
```

---

### Task 6 (TASK-3): TDD `monthly_trend`

**Files:**
- Modify: `data.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Consumes: a `pandas.DataFrame` with `date` (datetime) and `total_amount` columns.
- Produces: `monthly_trend(df: pandas.DataFrame) -> pandas.Series` — index is the first-of-month `Timestamp` for each month present in the data, values are that month's summed `total_amount`, ordered chronologically ascending.

- [ ] **Step 1: Write the failing test**

Update the import line in `tests/test_data.py`:
```python
from data import DataLoadError, load_data, monthly_trend, total_orders, total_sales
```

Add:
```python
def test_monthly_trend():
    result = monthly_trend(sample_df())

    assert list(result.index) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
    ]
    assert result.tolist() == pytest.approx([150.00, 230.00])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'monthly_trend' from 'data'`.

- [ ] **Step 3: Implement `monthly_trend`**

Add to the end of `data.py`:
```python
def monthly_trend(df):
    monthly = df.groupby(df["date"].dt.to_period("M"))["total_amount"].sum()
    monthly.index = monthly.index.to_timestamp()
    return monthly
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_data.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-3: add monthly_trend calculation"
```

---

### Task 7 (TASK-3): Render the sales trend line chart in app.py

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `data.monthly_trend(df) -> pandas.Series` (from Task 6).

- [ ] **Step 1: Add the Plotly import and chart**

Add `import plotly.express as px` near the top of `app.py`, alongside the existing imports:
```python
import plotly.express as px
import streamlit as st

from data import DataLoadError, load_data, monthly_trend, total_orders, total_sales
```

Add after the KPI row from Task 5:
```python
st.subheader("Sales Trend Over Time")
trend = monthly_trend(df)
trend_fig = px.line(
    x=trend.index,
    y=trend.values,
    labels={"x": "Month", "y": "Sales ($)"},
    markers=True,
)
st.plotly_chart(trend_fig, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run:
```bash
streamlit run app.py
```

Expected: a line chart appears below the KPI cards showing 12 monthly points rising and falling across 2024, with a working hover tooltip showing the exact month and sales value. Stop the server once confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: render sales trend line chart"
```

---

### Task 8 (TASK-4): TDD `sales_by_category` and `sales_by_region`

**Files:**
- Modify: `data.py`
- Test: `tests/test_data.py`

**Interfaces:**
- Consumes: a `pandas.DataFrame` with `category`/`region` and `total_amount` columns.
- Produces:
  - `sales_by_category(df: pandas.DataFrame) -> pandas.Series` — index is category name, values are summed `total_amount`, sorted descending by value.
  - `sales_by_region(df: pandas.DataFrame) -> pandas.Series` — same, indexed by region.

- [ ] **Step 1: Write the failing tests**

Update the import line in `tests/test_data.py`:
```python
from data import (
    DataLoadError,
    load_data,
    monthly_trend,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)
```

Add:
```python
def test_sales_by_category():
    result = sales_by_category(sample_df())

    assert list(result.index) == ["Electronics", "Accessories"]
    assert result.tolist() == pytest.approx([300.00, 80.00])


def test_sales_by_region():
    result = sales_by_region(sample_df())

    assert list(result.index) == ["North", "South", "West"]
    assert result.tolist() == pytest.approx([300.00, 50.00, 30.00])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'sales_by_category' from 'data'`.

- [ ] **Step 3: Implement both functions**

Add to the end of `data.py`:
```python
def sales_by_category(df):
    return df.groupby("category")["total_amount"].sum().sort_values(ascending=False)


def sales_by_region(df):
    return df.groupby("region")["total_amount"].sum().sort_values(ascending=False)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_data.py -v`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-4: add sales_by_category and sales_by_region calculations"
```

---

### Task 9 (TASK-4): Render category and region bar charts in app.py

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `data.sales_by_category(df) -> pandas.Series`, `data.sales_by_region(df) -> pandas.Series` (from Task 8).

- [ ] **Step 1: Update the import and add the bar charts**

Update the import line in `app.py`:
```python
from data import (
    DataLoadError,
    load_data,
    monthly_trend,
    sales_by_category,
    sales_by_region,
    total_orders,
    total_sales,
)
```

Add after the trend chart from Task 7:
```python
st.subheader("Breakdowns")
col3, col4 = st.columns(2)

category_data = sales_by_category(df)
category_fig = px.bar(
    x=category_data.index,
    y=category_data.values,
    labels={"x": "Category", "y": "Sales ($)"},
)
category_fig.update_xaxes(categoryorder="array", categoryarray=list(category_data.index))
col3.plotly_chart(category_fig, use_container_width=True)

region_data = sales_by_region(df)
region_fig = px.bar(
    x=region_data.index,
    y=region_data.values,
    labels={"x": "Region", "y": "Sales ($)"},
)
region_fig.update_xaxes(categoryorder="array", categoryarray=list(region_data.index))
col4.plotly_chart(region_fig, use_container_width=True)
```

- [ ] **Step 2: Verify manually**

Run:
```bash
streamlit run app.py
```

Expected: two bar charts side by side, each bar sorted highest-to-lowest by sales value, covering all 5 categories and all 4 regions from the PRD, with working hover tooltips. Stop the server once confirmed.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-4: render category and region breakdown bar charts"
```

---

### Task 10 (TASK-5): Full acceptance-criteria verification pass

**Files:** none (verification only; fix forward in the relevant file if something fails)

**Interfaces:** none — this task exercises the whole app as built by Tasks 1-9.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all tests pass (8 passed), no warnings.

- [ ] **Step 2: Run the app and check every PRD acceptance criterion**

Run:
```bash
streamlit run app.py
```

Open the Local URL and check each item from the PRD's Acceptance Criteria section against the running page:
- [ ] Total Sales and Total Orders displayed prominently
- [ ] Line chart shows sales over time with correct data (12 monthly points for 2024)
- [ ] Category bar chart shows sales by category, sorted by value, all 5 categories present
- [ ] Region bar chart shows sales by region, sorted by value, all 4 regions present
- [ ] Total Sales is close to $116,500 and Total Orders is exactly 482
- [ ] No errors or warnings appear in the terminal or the page
- [ ] The page looks clean enough for an executive presentation (clear labels, no debug output)

If anything fails, fix it in `app.py` or `data.py` (with a test added to `tests/test_data.py` if the fix touches a calculation), then re-run this task's steps.

- [ ] **Step 3: Confirm venv/ is excluded from version control**

Run: `git status`
Expected: `venv/` does not appear as an untracked or staged item (the repo's `.gitignore` already covers it).

- [ ] **Step 4: Commit any fixes**

If Step 2 required changes:
```bash
git add -A
git commit -m "TASK-5: fix issues found in acceptance-criteria pass"
```

If no changes were needed, there is nothing to commit — proceed to Task 11.

---

### Task 11 (TASK-5): Deploy to Streamlit Community Cloud — **executed by the user, not the agent**

This step requires the user's GitHub and Streamlit Community Cloud accounts and a merge to `main`, so it is not run as part of this plan's automated execution. Hand off here.

- [ ] **Step 1 (user):** Review and merge `feature/sales-dashboard` into `main` (code review, then merge — outside this plan's scope).
- [ ] **Step 2 (user):** Push `main` to GitHub.
- [ ] **Step 3 (user):** On https://share.streamlit.io, create a new app pointing at the GitHub repo, `main` branch, and `app.py` as the entry point.
- [ ] **Step 4 (user):** Deploy and confirm the public URL loads the dashboard with the same data shown locally.
- [ ] **Step 5 (user):** Update `TASKS.md` — check off TASK-5's acceptance criteria, add the deployed URL to its Commit/Notes line, and move it to Done.

**Plan ends here.**
