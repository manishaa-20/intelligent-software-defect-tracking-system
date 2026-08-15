## 🚀 Live Dashboard

[👉 Open Intelligent Software Defect Tracking Dashboard](https://intelligent-software-defect-tracking-system-6sza9fe4hup6daf5xj.streamlit.app)# Intelligent Software Defect Tracking System with Resolution Assistance 🐞

An interactive Streamlit dashboard for software defect analytics, KPI monitoring, bug life-cycle analysis, and resolution assistance.

## Project task coverage

- Interactive bug dashboard using Bug ID, Sprint, Release Version, Module, Feature, Component, Priority, Resolution, Root Cause and Date Closed
- Data preprocessing and cleaning
- Bug status and severity distribution
- Resolution trends and weekly closure analysis
- Sprint-wise and module-wise bug distribution
- KPI reporting for resolution time, defect density and team performance
- Duplicate-defect monitoring
- Rule-based resolution assistance
- Optional Random Forest resolution recommendation trained on the current dataset
- Filtered data export

## Tech stack

Python, Streamlit, Pandas, Plotly, Scikit-learn, OpenPyXL

## Run in VS Code

### 1. Open the project folder

Open this folder in VS Code.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install packages

```powershell
pip install -r requirements.txt
```

### 4. Start the dashboard

```powershell
streamlit run app.py
```

The terminal will show the local dashboard URL, normally `http://localhost:8501`.

## Dataset

The supplied Excel dataset is stored in `data/Bug_Life_Cycle_Managementreport.xlsx`.

A cleaned CSV is also included as `data/cleaned_bug_records.csv`.

The dashboard can additionally accept a new CSV/XLSX from the sidebar.

## Repository structure

```text
Intelligent_Software_Defect_Tracking_System/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── data/
│   ├── Bug_Life_Cycle_Managementreport.xlsx
│   └── cleaned_bug_records.csv
└── screenshots/
```

## KPI definitions

- **Average Resolution Time:** mean `Resolution_Time_Hours`
- **Closure Rate:** closed bugs / total filtered bugs × 100
- **Duplicate Rate:** duplicate bugs / total filtered bugs × 100
- **Defect Density:** bugs / distinct module (proxy metric because the supplied dataset has no LOC/function-point measure)

## Notes about the supplied dataset

The current dataset contains 200 records. It has one populated root-cause category (`Code defect`) and the lifecycle-stage field is currently `Open` for all records. The dashboard therefore displays those facts instead of inventing additional categories.

## GitHub

Recommended repository name:

`intelligent-software-defect-tracking-system`

Suggested topics:

`software-defect-tracking`, `bug-tracking`, `streamlit`, `python`, `plotly`, `software-quality`, `dashboard`, `machine-learning`

This repository includes an MIT license. Replace `Project Author` in `LICENSE` with the copyright holder's name before publishing.

## License

MIT License. See `LICENSE`.

## Disclaimer

The resolution assistance is an analytics/triage aid. It should not be treated as an autonomous engineering decision-maker.
