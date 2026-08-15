import os
from pathlib import Path
from io import BytesIO

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ML is optional. Dashboard still works if sklearn is unavailable.
try:
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Software Defect Tracking System",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM DARK THEME
# ============================================================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: #050816;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stSidebar"] {
    background: #0b1022;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1 {
    font-size: 34px !important;
    font-weight: 800 !important;
}

h2 {
    font-weight: 750 !important;
}

h3 {
    font-weight: 700 !important;
}

.kpi-card {
    background: linear-gradient(135deg, #111a35, #0b1226);
    border: 1px solid #263557;
    border-radius: 16px;
    padding: 18px;
    min-height: 125px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-label {
    color: #94a3c7;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.section-box {
    background: #0b1226;
    border: 1px solid #202e4e;
    border-radius: 15px;
    padding: 18px;
}

.insight-box {
    background: linear-gradient(135deg, #111b38, #0c1429);
    border-left: 4px solid #ff6b6b;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.small-text {
    color: #94a3c7;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

CSV_PATH = DATA_DIR / "cleaned_bug_records.csv"
XLSX_PATH = DATA_DIR / "Bug_Life_Cycle_Managementreport.xlsx"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_mean(series):
    values = pd.to_numeric(series, errors="coerce").dropna()

    if len(values) == 0:
        return 0.0

    return float(values.mean())


def safe_percentage(numerator, denominator):
    if denominator == 0:
        return 0.0

    return (numerator / denominator) * 100


def kpi_card(label, value, icon):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div style="font-size:24px;">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name

    return None


# ============================================================
# DATA PREPROCESSING
# ============================================================

def preprocess_data(df):

    data = df.copy()

    # Remove completely empty columns
    data = data.dropna(axis=1, how="all")

    # Clean column names
    data.columns = [
        str(col).strip().replace(" ", "_")
        for col in data.columns
    ]

    # Clean text columns
    text_columns = data.select_dtypes(include=["object"]).columns

    for col in text_columns:
        data[col] = (
            data[col]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "nan": np.nan,
                    "None": np.nan,
                    "": np.nan
                }
            )
        )

    # --------------------------------------------------------
    # Date conversion
    # --------------------------------------------------------

    date_columns = [
        "Date_Reported",
        "Date_Closed"
    ]

    for col in date_columns:

        if col in data.columns:

            data[col] = pd.to_datetime(
                data[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Resolution Time
    # --------------------------------------------------------

    if "Resolution_Time_Hours" not in data.columns:

        data["Resolution_Time_Hours"] = np.nan

    data["Resolution_Time_Hours"] = pd.to_numeric(
        data["Resolution_Time_Hours"],
        errors="coerce"
    )

    if (
        "Date_Reported" in data.columns
        and "Date_Closed" in data.columns
    ):

        calculated_time = (
            data["Date_Closed"] -
            data["Date_Reported"]
        ).dt.total_seconds() / 3600

        data["Resolution_Time_Hours"] = (
            data["Resolution_Time_Hours"]
            .fillna(calculated_time)
        )

    data["Resolution_Time_Hours"] = (
        data["Resolution_Time_Hours"]
        .clip(lower=0)
        .round(2)
    )

    data["Resolution_Time_Days"] = (
        data["Resolution_Time_Hours"] / 24
    ).round(2)

    # --------------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------------

    if "duplicate" in data.columns:

        data["Is_Duplicate"] = (
            pd.to_numeric(
                data["duplicate"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

    elif "Duplicate_Of" in data.columns:

        data["Is_Duplicate"] = (
            data["Duplicate_Of"]
            .notna()
            .astype(int)
        )

    else:

        data["Is_Duplicate"] = 0

    # --------------------------------------------------------
    # Closure flag
    # --------------------------------------------------------

    if "Status" in data.columns:

        data["Closure_Flag"] = (
            data["Status"]
            .astype(str)
            .str.lower()
            .eq("closed")
            .astype(int)
        )

    else:

        data["Closure_Flag"] = 0

    return data


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_file(file_bytes=None, file_name=None):

    if file_bytes is not None:

        file_stream = BytesIO(file_bytes)

        if str(file_name).lower().endswith(".xlsx"):

            df = pd.read_excel(file_stream)

        else:

            df = pd.read_csv(file_stream)

    else:

        if CSV_PATH.exists():

            df = pd.read_csv(CSV_PATH)

        elif XLSX_PATH.exists():

            df = pd.read_excel(XLSX_PATH)

        else:

            return pd.DataFrame()

    return preprocess_data(df)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🐞 Intelligent Software Defect Tracking System"
)

st.caption(
    "Interactive bug analytics, KPI monitoring, "
    "life-cycle tracking and intelligent resolution assistance."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Bug Dataset",
    type=["csv", "xlsx"]
)


if uploaded_file:

    df = load_file(
        uploaded_file.getvalue(),
        uploaded_file.name
    )

else:

    df = load_file()


if df.empty:

    st.error(
        "Dataset not found. Please upload your CSV/XLSX file."
    )

    st.stop()


st.sidebar.success(
    "{} bug records loaded".format(len(df))
)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Filters")


def get_unique(column):

    if column not in df.columns:
        return []

    return sorted(
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


sprint_filter = st.sidebar.multiselect(
    "Sprint",
    get_unique("Sprint")
)

release_filter = st.sidebar.multiselect(
    "Release Version",
    get_unique("Release_Version")
)

module_filter = st.sidebar.multiselect(
    "Module",
    get_unique("Module")
)

feature_filter = st.sidebar.multiselect(
    "Feature",
    get_unique("Feature")
)

priority_filter = st.sidebar.multiselect(
    "Priority",
    get_unique("Priority")
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    get_unique("Severity")
)

status_filter = st.sidebar.multiselect(
    "Status",
    get_unique("Status")
)

team_filter = st.sidebar.multiselect(
    "Team",
    get_unique("Team")
)

search_text = st.sidebar.text_input(
    "🔍 Search Bug ID / Title"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


filter_values = [
    ("Sprint", sprint_filter),
    ("Release_Version", release_filter),
    ("Module", module_filter),
    ("Feature", feature_filter),
    ("Priority", priority_filter),
    ("Severity", severity_filter),
    ("Status", status_filter),
    ("Team", team_filter)
]


for column, values in filter_values:

    if values and column in filtered.columns:

        filtered = filtered[
            filtered[column]
            .astype(str)
            .isin(values)
        ]


if search_text:

    search_lower = search_text.lower()

    search_mask = pd.Series(
        False,
        index=filtered.index
    )

    if "Bug_ID" in filtered.columns:

        search_mask |= (
            filtered["Bug_ID"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False
            )
        )

    if "Bug_Title" in filtered.columns:

        search_mask |= (
            filtered["Bug_Title"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False
            )
        )

    filtered = filtered[search_mask]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_bugs = len(filtered)

if "Status" in filtered.columns:

    closed_bugs = int(
        filtered["Status"]
        .astype(str)
        .str.lower()
        .eq("closed")
        .sum()
    )

else:

    closed_bugs = 0


open_bugs = total_bugs - closed_bugs


if "Severity" in filtered.columns:

    critical_bugs = int(
        filtered["Severity"]
        .astype(str)
        .str.lower()
        .eq("critical")
        .sum()
    )

else:

    critical_bugs = 0


average_resolution = safe_mean(
    filtered["Resolution_Time_Hours"]
)


closure_rate = safe_percentage(
    closed_bugs,
    total_bugs
)


duplicate_count = int(
    filtered["Is_Duplicate"].sum()
)


duplicate_rate = safe_percentage(
    duplicate_count,
    total_bugs
)


module_count = (
    filtered["Module"].nunique()
    if "Module" in filtered.columns
    else 1
)


defect_density = (
    total_bugs / max(module_count, 1)
)


# ============================================================
# KPI CARDS
# ============================================================

st.markdown("### 📌 Project KPIs")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    kpi_card(
        "Total Bugs",
        "{:,}".format(total_bugs),
        "🐞"
    )

with k2:
    kpi_card(
        "Open Bugs",
        "{:,}".format(open_bugs),
        "⚠️"
    )

with k3:
    kpi_card(
        "Closed Bugs",
        "{:,}".format(closed_bugs),
        "✅"
    )

with k4:
    kpi_card(
        "Avg Resolution",
        "{:.1f} h".format(average_resolution),
        "⏱️"
    )

with k5:
    kpi_card(
        "Critical Bugs",
        "{:,}".format(critical_bugs),
        "🔥"
    )

with k6:
    kpi_card(
        "Closure Rate",
        "{:.1f}%".format(closure_rate),
        "📈"
    )


st.markdown("---")


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Overview",
        "🔄 Life Cycle & Trends",
        "🏃 Sprint & Module",
        "👥 Team Performance",
        "🧠 Resolution Assistance",
        "📋 Data Explorer"
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with tab1:

    st.header("📊 Bug Overview")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "Bug Status Distribution"
        )

        if "Status" in filtered.columns:

            status_data = (
                filtered["Status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = [
                "Status",
                "Count"
            ]

            fig = px.pie(
                status_data,
                names="Status",
                values="Count",
                hole=0.55,
                template="plotly_dark"
            )

            fig.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=30,
                    b=10
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "Bugs by Severity"
        )

        if "Severity" in filtered.columns:

            severity_data = (
                filtered["Severity"]
                .value_counts()
                .reset_index()
            )

            severity_data.columns = [
                "Severity",
                "Count"
            ]

            fig = px.bar(
                severity_data,
                x="Count",
                y="Severity",
                orientation="h",
                text="Count",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    col3, col4 = st.columns(2)


    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    with col3:

        st.subheader(
            "Bugs by Priority"
        )

        if "Priority" in filtered.columns:

            priority_data = (
                filtered["Priority"]
                .value_counts()
                .reset_index()
            )

            priority_data.columns = [
                "Priority",
                "Count"
            ]

            fig = px.bar(
                priority_data,
                x="Priority",
                y="Count",
                text="Count",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    with col4:

        st.subheader(
            "Resolution Type"
        )

        if "Resolution" in filtered.columns:

            resolution_data = (
                filtered["Resolution"]
                .value_counts()
                .reset_index()
            )

            resolution_data.columns = [
                "Resolution",
                "Count"
            ]

            fig = px.pie(
                resolution_data,
                names="Resolution",
                values="Count",
                hole=0.55,
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------------

    st.subheader(
        "🔬 Root Cause Analysis"
    )

    if "Root_Cause" in filtered.columns:

        root_data = (
            filtered["Root_Cause"]
            .value_counts()
            .reset_index()
        )

        root_data.columns = [
            "Root_Cause",
            "Count"
        ]

        if len(root_data) == 1:

            root_name = root_data.iloc[0]["Root_Cause"]

            st.info(
                "Current dataset contains one main root cause: **{}**. "
                "More root-cause categories can be added later."
                .format(root_name)
            )

        else:

            fig = px.bar(
                root_data,
                x="Count",
                y="Root_Cause",
                orientation="h",
                text="Count",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # --------------------------------------------------------
    # DEFECT DENSITY
    # --------------------------------------------------------

    st.subheader(
        "📐 Defect Density"
    )

    d1, d2, d3 = st.columns(3)

    with d1:

        st.metric(
            "Distinct Modules",
            module_count
        )

    with d2:

        st.metric(
            "Total Bugs",
            total_bugs
        )

    with d3:

        st.metric(
            "Bugs / Module",
            "{:.2f}".format(defect_density)
        )

    st.caption(
        "Defect density is shown as bugs per distinct module because "
        "the supplied dataset does not contain LOC or function-point data."
    )


# ============================================================
# TAB 2 - LIFE CYCLE
# ============================================================

with tab2:

    st.header(
        "🔄 Bug Life Cycle & Resolution Trends"
    )

    # --------------------------------------------------------
    # WEEKLY TREND
    # --------------------------------------------------------

    if "Date_Closed" in filtered.columns:

        closed_data = filtered.dropna(
            subset=["Date_Closed"]
        ).copy()

        if len(closed_data) > 0:

            weekly = (
                closed_data
                .set_index("Date_Closed")
                .resample("W")
                .agg(
                    Closed_Bugs=("Bug_ID", "count"),
                    Avg_Resolution_Hours=(
                        "Resolution_Time_Hours",
                        "mean"
                    )
                )
                .reset_index()
            )

            c1, c2 = st.columns(2)

            with c1:

                st.subheader(
                    "Weekly Bugs Closed"
                )

                fig = px.line(
                    weekly,
                    x="Date_Closed",
                    y="Closed_Bugs",
                    markers=True,
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with c2:

                st.subheader(
                    "Weekly Average Resolution Time"
                )

                fig = px.line(
                    weekly,
                    x="Date_Closed",
                    y="Avg_Resolution_Hours",
                    markers=True,
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        else:

            st.warning(
                "No Date Closed values available."
            )


    # --------------------------------------------------------
    # STATUS TREND
    # --------------------------------------------------------

    st.subheader(
        "Current Life Cycle Status"
    )

    if "Status" in filtered.columns:

        lifecycle = (
            filtered["Status"]
            .value_counts()
            .reset_index()
        )

        lifecycle.columns = [
            "Status",
            "Count"
        ]

        fig = px.bar(
            lifecycle,
            x="Status",
            y="Count",
            text="Count",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # DUPLICATE ANALYSIS
    # --------------------------------------------------------

    st.subheader(
        "♻️ Duplicate Bug Analysis"
    )

    duplicate_data = (
        filtered["Is_Duplicate"]
        .map(
            {
                0: "Original",
                1: "Duplicate"
            }
        )
        .value_counts()
        .reset_index()
    )

    duplicate_data.columns = [
        "Type",
        "Count"
    ]

    fig = px.pie(
        duplicate_data,
        names="Type",
        values="Count",
        hole=0.55,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Duplicate rate: {:.1f}% ({:,} duplicate records)."
        .format(
            duplicate_rate,
            duplicate_count
        )
    )


# ============================================================
# TAB 3 - SPRINT & MODULE
# ============================================================

with tab3:

    st.header(
        "🏃 Sprint-wise & Module-wise Analysis"
    )

    # --------------------------------------------------------
    # SPRINT
    # --------------------------------------------------------

    if "Sprint" in filtered.columns:

        st.subheader(
            "Sprint-wise Bug Distribution"
        )

        sprint_data = (
            filtered
            .groupby("Sprint")
            .size()
            .reset_index(
                name="Bug_Count"
            )
        )

        sprint_data["Sprint_Number"] = pd.to_numeric(
            sprint_data["Sprint"]
            .astype(str)
            .str.extract(
                r"(\d+)"
            )[0],
            errors="coerce"
        )

        sprint_data = sprint_data.sort_values(
            "Sprint_Number"
        )

        fig = px.bar(
            sprint_data,
            x="Sprint",
            y="Bug_Count",
            text="Bug_Count",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # MODULE STATUS
    # --------------------------------------------------------

    if (
        "Module" in filtered.columns
        and "Status" in filtered.columns
    ):

        st.subheader(
            "Bugs by Module & Status"
        )

        module_status = pd.crosstab(
            filtered["Module"],
            filtered["Status"]
        )

        fig = px.bar(
            module_status,
            barmode="stack",
            template="plotly_dark"
        )

        fig.update_layout(
            xaxis_title="Module",
            yaxis_title="Bug Count",
            legend_title="Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # MODULE TABLE
    # --------------------------------------------------------

    if "Module" in filtered.columns:

        st.subheader(
            "Module Performance"
        )

        module_table = (
            filtered
            .groupby("Module")
            .agg(
                Bugs=("Bug_ID", "count"),
                Avg_Resolution_Hours=(
                    "Resolution_Time_Hours",
                    "mean"
                ),
                Critical=(
                    "Severity",
                    lambda x: (
                        x.astype(str)
                        .str.lower()
                        .eq("critical")
                        .sum()
                    )
                )
            )
            .reset_index()
        )

        module_table = module_table.sort_values(
            "Bugs",
            ascending=False
        )

        st.dataframe(
            module_table.round(2),
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------------
    # RELEASE
    # --------------------------------------------------------

    if "Release_Version" in filtered.columns:

        st.subheader(
            "Release-wise Bug Distribution"
        )

        release_data = (
            filtered["Release_Version"]
            .value_counts()
            .head(15)
            .reset_index()
        )

        release_data.columns = [
            "Release_Version",
            "Bug_Count"
        ]

        fig = px.bar(
            release_data,
            x="Bug_Count",
            y="Release_Version",
            orientation="h",
            text="Bug_Count",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# TAB 4 - TEAM PERFORMANCE
# ============================================================

with tab4:

    st.header(
        "👥 Team Performance"
    )

    if "Team" in filtered.columns:

        team_data = (
            filtered
            .groupby("Team")
            .agg(
                Bugs=("Bug_ID", "count"),
                Closed=("Closure_Flag", "sum"),
                Avg_Resolution_Hours=(
                    "Resolution_Time_Hours",
                    "mean"
                ),
                Critical=(
                    "Severity",
                    lambda x: (
                        x.astype(str)
                        .str.lower()
                        .eq("critical")
                        .sum()
                    )
                )
            )
            .reset_index()
        )

        team_data["Closure_Rate_%"] = (
            team_data["Closed"]
            / team_data["Bugs"]
            * 100
        ).round(1)


        c1, c2 = st.columns(2)

        with c1:

            st.subheader(
                "Average Resolution Time by Team"
            )

            chart_data = team_data.sort_values(
                "Avg_Resolution_Hours"
            )

            fig = px.bar(
                chart_data,
                x="Team",
                y="Avg_Resolution_Hours",
                text="Avg_Resolution_Hours",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        with c2:

            st.subheader(
                "Team Closure Rate"
            )

            chart_data = team_data.sort_values(
                "Closure_Rate_%"
            )

            fig = px.bar(
                chart_data,
                x="Team",
                y="Closure_Rate_%",
                text="Closure_Rate_%",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.subheader(
            "Team KPI Table"
        )

        st.dataframe(
            team_data.round(2),
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # ACTIONABLE TEAM INSIGHTS
        # ----------------------------------------------------

        if len(team_data) > 0:

            best_team = team_data.loc[
                team_data["Closure_Rate_%"].idxmax()
            ]

            fastest_team = team_data.loc[
                team_data["Avg_Resolution_Hours"].idxmin()
            ]

            st.markdown(
                """
                <div class="insight-box">
                🏆 <b>Highest Closure Rate:</b>
                {} — {:.1f}%
                </div>
                """.format(
                    best_team["Team"],
                    best_team["Closure_Rate_%"]
                ),
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="insight-box">
                ⚡ <b>Fastest Resolution Team:</b>
                {} — {:.1f} hours average
                </div>
                """.format(
                    fastest_team["Team"],
                    fastest_team["Avg_Resolution_Hours"]
                ),
                unsafe_allow_html=True
            )


# ============================================================
# TAB 5 - INTELLIGENT RESOLUTION ASSISTANCE
# ============================================================

with tab5:

    st.header(
        "🧠 Intelligent Resolution Assistance"
    )

    st.caption(
        "The system provides rule-based recommendations and "
        "an optional Random Forest recommendation model."
    )


    # --------------------------------------------------------
    # BUG SELECTION
    # --------------------------------------------------------

    if "Bug_ID" in filtered.columns and len(filtered) > 0:

        bug_list = (
            filtered["Bug_ID"]
            .astype(str)
            .tolist()
        )

        selected_bug = st.selectbox(
            "Select a Bug ID",
            bug_list
        )

        selected_row = filtered[
            filtered["Bug_ID"]
            .astype(str)
            == selected_bug
        ].iloc[0]


        left, right = st.columns(2)


        # ----------------------------------------------------
        # BUG CONTEXT
        # ----------------------------------------------------

        with left:

            st.subheader(
                "🐞 Bug Context"
            )

            st.write(
                "**Bug ID:** {}"
                .format(
                    selected_row.get(
                        "Bug_ID",
                        "-"
                    )
                )
            )

            st.write(
                "**Title:** {}"
                .format(
                    selected_row.get(
                        "Bug_Title",
                        "-"
                    )
                )
            )

            st.write(
                "**Module:** {}"
                .format(
                    selected_row.get(
                        "Module",
                        "-"
                    )
                )
            )

            st.write(
                "**Feature:** {}"
                .format(
                    selected_row.get(
                        "Feature",
                        "-"
                    )
                )
            )

            st.write(
                "**Component:** {}"
                .format(
                    selected_row.get(
                        "Component",
                        "-"
                    )
                )
            )

            st.write(
                "**Severity:** {}"
                .format(
                    selected_row.get(
                        "Severity",
                        "-"
                    )
                )
            )

            st.write(
                "**Priority:** {}"
                .format(
                    selected_row.get(
                        "Priority",
                        "-"
                    )
                )
            )

            st.write(
                "**Status:** {}"
                .format(
                    selected_row.get(
                        "Status",
                        "-"
                    )
                )
            )

            st.write(
                "**Root Cause:** {}"
                .format(
                    selected_row.get(
                        "Root_Cause",
                        "-"
                    )
                )
            )

            st.write(
                "**Team:** {}"
                .format(
                    selected_row.get(
                        "Team",
                        "-"
                    )
                )
            )


        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        with right:

            st.subheader(
                "💡 Recommended Actions"
            )

            recommendations = []


            severity = str(
                selected_row.get(
                    "Severity",
                    ""
                )
            ).lower()

            priority = str(
                selected_row.get(
                    "Priority",
                    ""
                )
            ).upper()

            bug_type = str(
                selected_row.get(
                    "Bug_Type",
                    ""
                )
            ).lower()

            resolution = str(
                selected_row.get(
                    "Resolution",
                    ""
                )
            ).lower()

            is_duplicate = int(
                selected_row.get(
                    "Is_Duplicate",
                    0
                )
            )


            if (
                is_duplicate == 1
                or "duplicate" in resolution
            ):

                recommendations.append(
                    "♻️ Mark as duplicate and link the "
                    "defect to the master bug."
                )


            if (
                severity == "critical"
                or priority == "P1"
            ):

                recommendations.append(
                    "🔥 Escalate immediately and assign "
                    "a responsible owner."
                )


            if bug_type == "performance":

                recommendations.append(
                    "⚡ Profile the slow operation and "
                    "validate the fix using performance testing."
                )


            elif bug_type == "security":

                recommendations.append(
                    "🔐 Perform security validation and "
                    "run focused security regression tests."
                )


            elif bug_type == "database":

                recommendations.append(
                    "🗄️ Check queries, schema, transactions "
                    "and database integrity."
                )


            elif bug_type == "api":

                recommendations.append(
                    "🔗 Validate API request/response contracts, "
                    "status codes and authentication."
                )


            elif bug_type == "ui":

                recommendations.append(
                    "🖥️ Reproduce across supported browsers/devices "
                    "and add a UI regression test."
                )


            if len(recommendations) == 0:

                recommendations.append(
                    "🔎 Reproduce the issue, isolate the root cause, "
                    "implement the smallest safe fix, retest and "
                    "document the evidence."
                )


            for recommendation in recommendations:

                st.markdown(
                    """
                    <div class="insight-box">
                    {}
                    </div>
                    """.format(
                        recommendation
                    ),
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # RANDOM FOREST
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader(
            "🤖 ML Resolution Recommendation"
        )

        if SKLEARN_AVAILABLE:

            feature_columns = [
                "Module",
                "Feature",
                "Component",
                "Severity",
                "Priority",
                "Bug_Type",
                "Team"
            ]

            feature_columns = [
                col
                for col in feature_columns
                if col in filtered.columns
            ]


            if (
                "Resolution" in filtered.columns
                and len(feature_columns) > 0
            ):

                model_data = filtered[
                    feature_columns
                    + ["Resolution"]
                ].dropna()


                if (
                    len(model_data) >= 20
                    and model_data["Resolution"].nunique() >= 2
                ):

                    X = model_data[
                        feature_columns
                    ]

                    y = model_data[
                        "Resolution"
                    ]


                    preprocessor = ColumnTransformer(
                        [
                            (
                                "categorical",
                                OneHotEncoder(
                                    handle_unknown="ignore"
                                ),
                                feature_columns
                            )
                        ],
                        remainder="drop"
                    )


                    model = Pipeline(
                        [
                            (
                                "preprocessor",
                                preprocessor
                            ),
                            (
                                "classifier",
                                RandomForestClassifier(
                                    n_estimators=100,
                                    random_state=42,
                                    class_weight="balanced"
                                )
                            )
                        ]
                    )


                    try:

                        model.fit(
                            X,
                            y
                        )


                        input_data = pd.DataFrame(
                            [
                                {
                                    col:
                                    selected_row.get(
                                        col,
                                        "Unknown"
                                    )
                                    for col in feature_columns
                                }
                            ]
                        )


                        prediction = model.predict(
                            input_data
                        )[0]


                        st.success(
                            "Recommended Resolution: **{}**"
                            .format(
                                prediction
                            )
                        )

                        st.caption(
                            "Recommendation generated from "
                            "the currently filtered dataset."
                        )

                    except Exception as error:

                        st.warning(
                            "ML recommendation could not be generated: {}"
                            .format(error)
                        )

                else:

                    st.info(
                        "At least 20 labeled records with two or "
                        "more resolution classes are required."
                    )

            else:

                st.info(
                    "Required ML fields are not available."
                )

        else:

            st.warning(
                "scikit-learn is not installed. "
                "The rule-based resolution assistance above is still available."
            )


    # --------------------------------------------------------
    # PROJECT LEVEL INSIGHTS
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "📌 Actionable Project Insights"
    )


    if total_bugs > 0:

        insight_list = []


        insight_list.append(
            "Closure rate is {:.1f}%. "
            "Prioritize unresolved high-severity defects."
            .format(
                closure_rate
            )
        )


        insight_list.append(
            "Average resolution time is {:.1f} hours. "
            "Use this as the current project baseline."
            .format(
                average_resolution
            )
        )


        insight_list.append(
            "Duplicate rate is {:.1f}%. "
            "Improve duplicate detection during defect intake."
            .format(
                duplicate_rate
            )
        )


        if "Module" in filtered.columns:

            module_counts = (
                filtered["Module"]
                .value_counts()
            )

            if len(module_counts) > 0:

                top_module = module_counts.index[0]

                insight_list.append(
                    "Focus root-cause analysis on **{}**, "
                    "the module with the highest number of bugs."
                    .format(
                        top_module
                    )
                )


        if critical_bugs > 0:

            insight_list.append(
                "There are **{} critical defects**. "
                "These should receive the highest triage priority."
                .format(
                    critical_bugs
                )
            )


        for item in insight_list:

            st.markdown(
                """
                <div class="insight-box">
                📍 {}
                </div>
                """.format(
                    item
                ),
                unsafe_allow_html=True
            )


# ============================================================
# TAB 6 - DATA EXPLORER
# ============================================================

with tab6:

    st.header(
        "📋 Filtered Bug Records"
    )

    st.caption(
        "Preprocessing includes text cleaning, date conversion, "
        "resolution-time calculation, duplicate detection and closure tracking."
    )


    display_columns = [
        "Bug_ID",
        "Sprint",
        "Release_Version",
        "Module",
        "Feature",
        "Component",
        "Severity",
        "Priority",
        "Status",
        "Resolution",
        "Root_Cause",
        "Team",
        "Date_Reported",
        "Date_Closed",
        "Resolution_Time_Hours",
        "Resolution_Time_Days",
        "Is_Duplicate"
    ]


    display_columns = [
        col
        for col in display_columns
        if col in filtered.columns
    ]


    st.dataframe(
        filtered[display_columns],
        use_container_width=True,
        height=550,
        hide_index=True
    )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_data,
        file_name="filtered_bug_records.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Intelligent Software Defect Tracking System with Resolution Assistance "
    "• Interactive Analytics • KPI Monitoring • Defect Life Cycle Management"
)