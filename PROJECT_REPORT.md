# Project Report — Intelligent Software Defect Tracking System

## 1. Title
**Intelligent Software Defect Tracking System**

## 2. Problem Statement
Software teams receive defect records across releases, sprints, modules and teams. Manual tracking makes it difficult to identify critical defects, monitor resolution time, compare team performance and understand recurring root causes.

## 3. Objective
Develop an interactive analytics system that preprocesses bug records and converts them into actionable dashboards for software-quality and project-management decisions.

## 4. Main Inputs
- Bug ID
- Sprint
- Release Version
- Module
- Feature
- Component
- Priority
- Severity
- Status
- Resolution
- Root Cause
- Team
- Date Reported
- Date Closed
- Resolution Time

## 5. System Modules
### Dashboard Controls
Dataset upload and Sprint/Release filtering.

### Bug Overview
Status, severity, priority and resolution visualizations.

### Life Cycle & Trends
Weekly closure trend, resolution-time trend, current life-cycle status and root-cause analysis.

### Sprint & Module Analysis
Sprint-wise distribution, module/status distribution and module performance.

### Team Performance
Average resolution time, closure rate and KPI table.

### Defect Assistant
A data-aware chat box that answers common defect-analysis questions using the active filtered DataFrame.

### Data Explorer
Interactive record table and filtered CSV download.

## 6. Data Preprocessing
1. Normalize column names.
2. Standardize common aliases.
3. Convert dates to datetime.
4. Convert resolution time to numeric.
5. Fill missing categorical values with `Unknown`.
6. Remove duplicate Bug IDs.
7. Calculate resolution time from report/close dates when it is not supplied.

## 7. KPIs
### Closure Rate
`Closed Bugs / Total Bugs × 100`

### Average Resolution Time
Mean resolution time for resolved defects.

### Critical Bug Count
Number of records with Critical severity.

### Defect Density
A true defects/KLOC metric requires KLOC or project-size data. The application therefore avoids inventing a KLOC denominator and instead provides bug-volume/module analysis.

## 8. Technology Stack
- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenPyXL

## 9. Architecture
```text
CSV / XLSX
    ↓
Upload / Load
    ↓
Data Preprocessing
    ↓
Derived Metrics
    ↓
Filters
    ↓
┌───────────────┬────────────────┬─────────────────┐
│ KPI Dashboard │ Visualizations │ Defect Assistant│
└───────────────┴────────────────┴─────────────────┘
    ↓
Insights / CSV Export
```

## 10. Expected Benefits
- Faster defect triage
- Better sprint monitoring
- Earlier identification of high-risk modules
- Data-driven team performance evaluation
- Reduced manual reporting
- Improved release-quality decisions

## 11. Future Enhancements
- ML-based severity/priority prediction
- Duplicate-bug detection using NLP
- LLM-powered assistant with optional API integration
- Jira/GitHub/Bugzilla connectors
- Authentication and role-based access
- Automated email/Slack alerts
- True defect-density reporting using KLOC

## 12. Dataset Note
The repository includes a synthetic 200-record demo dataset so the application runs immediately. Replace it with the project's real CSV/XLSX before using the dashboard numbers in an academic submission or business report.
