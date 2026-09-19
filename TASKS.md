# Sales Dashboard: Tasks

This file tracks all work for the e-commerce sales dashboard.
Each milestone moves through To Do -> In Progress -> Done.

## Definition of Done (must hold before any milestone moves to Done)
- Acceptance criteria met
- App runs locally with `streamlit run app.py`
- Changes committed with the milestone ID in the message

## To Do
- [ ] **TASK-4: Category and region breakdowns**
  - [ ] Bar chart of sales by category, sorted highest to lowest, all categories shown
  - [ ] Bar chart of sales by region, sorted highest to lowest, all regions shown
  - Commit:
- [ ] **TASK-5: Test and deploy**
  - [ ] Dashboard runs without errors or warnings against the full dataset
  - [ ] All PRD acceptance criteria verified against expected output (~$116,500 total sales, 482 orders)
  - [ ] Deployed to Streamlit Community Cloud with a public URL
  - Commit:

## In Progress
- [ ] **TASK-3: Sales trend chart**
  - [ ] Line chart shows sales over time with correct data
  - [ ] Interactive tooltips show exact values
  - Commit:

## Done
- [x] **TASK-2: KPI scorecards**
  - [x] Total Sales displayed as formatted currency (e.g. $116,500)
  - [x] Total Orders displayed as a formatted count (e.g. 482)
  - Commit: 6724a2a
  - Notes: clean.
- [x] **TASK-1: Project setup and data loading**
  - [x] App runs with `streamlit run app.py` and shows a title
  - [x] Loads `data/sales-data.csv`; handles date, numeric, and categorical columns per the data spec
  - Commit: 74e4e68
  - Notes: first `streamlit run` hung on an interactive first-run onboarding prompt (asking for an email); fixed by pre-setting `~/.streamlit/credentials.toml` with a blank email, a one-time machine setting outside the repo. No code changes needed beyond the plan.
