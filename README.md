# Intelligent Software Defect Tracking System 🐞

An interactive Streamlit dashboard for software defect analytics, bug life-cycle monitoring, KPI reporting, sprint/module analysis, team performance and rule-based intelligent resolution assistance.

## ✨ Features

- CSV/XLSX upload
- Data preprocessing: column normalization, missing-value handling, date parsing and duplicate removal
- KPI cards:
  - Total Bugs
  - Open Bugs
  - Closed Bugs
  - Average Resolution Time
  - Critical Bugs
  - Closure Rate
- Bug Overview:
  - Status distribution
  - Severity distribution
  - Priority distribution
  - Resolution type
- Life Cycle & Trends:
  - Weekly bugs closed
  - Weekly average resolution time
  - Current life-cycle status
  - Root-cause analysis
- Sprint & Module:
  - Sprint-wise bug distribution
  - Module-wise status distribution
  - Module performance table
- Team Performance:
  - Average resolution time by team
  - Team closure rate
  - Team KPI table
- Defect Assistant 💬:
  - Ask natural-language questions about the currently filtered dataset
  - No API key required
- Data Explorer:
  - Select columns
  - Inspect filtered records
  - Download filtered data as CSV

## 📁 Project Structure

```text
intelligent_software_defect_tracking_system/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── run.bat
├── run.sh
├── data/
│   └── sample_bug_dataset.csv
├── src/
│   ├── __init__.py
│   └── data_utils.py
└── .streamlit/
    └── config.toml
```

## 🚀 Run locally

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Or double-click `run.bat`.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Or run:

```bash
bash run.sh
```

## 📊 Your Google Sheets dataset

Source sheet supplied for the project:

https://docs.google.com/spreadsheets/d/1VGvBiWbvqX7MXIC64ixXxrKt_4GhaAsKmeCQNC_yYw4/edit?usp=drivesdk

The supplied link could not be directly exported from this environment, so the repository includes a clearly labelled **sample dataset** for immediate execution. For your final project, export the Google Sheet as CSV/XLSX and upload it through the sidebar, or replace `data/sample_bug_dataset.csv` with your exact data.

Expected fields include:

`Bug ID, Sprint, Release Version, Module, Feature, Component, Priority, Severity, Status, Resolution, Root Cause, Team, Date Reported, Date Closed, Resolution Time Hours`

The app also normalizes common column-name variations such as `Bug ID` → `Bug_ID`, `Date Closed` → `Date_Closed`, and `Root Cause` → `Root_Cause`.

## 🧠 Defect Assistant

The assistant is intentionally implemented without a mandatory external AI API. It calculates answers from the active pandas DataFrame, so answers stay tied to the selected sprint/release filters.

Example questions:

- Which module has the most critical bugs?
- How many bugs are there?
- What is the average resolution time?
- Which sprint has the most bugs?
- What is the most common priority?
- Which team resolves bugs fastest?

## 📈 KPI interpretation

### Closure Rate
Closed bugs divided by total bugs × 100.

### Average Resolution Time
Average elapsed time between `Date Reported` and `Date Closed` for resolved records, or the supplied `Resolution Time Hours` field when available.

### Defect Density
The dashboard keeps the raw bug count and module-level density-ready data. A true defects/KLOC metric requires project size in KLOC; it should not be invented from a bug table alone.

## 🎯 Actionable project insights

Use the dashboard to:

1. Prioritize critical/high-severity defects.
2. Investigate modules with unusually high bug volume.
3. Identify sprints where bug inflow is increasing.
4. Compare teams using both closure rate and resolution time.
5. Track root causes to reduce recurring defects.
6. Use filters to isolate a release or sprint before making management decisions.

## ☁️ Streamlit deployment

1. Push this folder to GitHub.
2. Open Streamlit Community Cloud.
3. Select the repository and `app.py`.
4. Deploy.
5. Keep `requirements.txt` in the repository root.

## 📜 License

MIT License. See `LICENSE`.

## ⚠️ Dataset note

The included CSV is a synthetic demo dataset created to make the repository runnable and to mirror the aggregate style visible in the supplied dashboard screenshots. Replace it with your actual project dataset before submitting or publishing analytical results.
