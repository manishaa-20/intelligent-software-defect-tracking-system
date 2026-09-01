import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

from src.data_utils import (
    clean_dataset,
    add_derived_metrics,
    filter_data,
    calculate_kpis,
    answer_question,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Intelligent Software Defect Tracking System",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #070b1d;
        --panel: #0d142b;
        --card: #111a35;
        --accent: #6672f4;
        --muted: #9aa4bd;
    }

    .stApp {
        background: var(--bg);
        color: #f5f7ff;
    }

    [data-testid="stSidebar"] {
        background: #0a1024;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #111a35, #0d142b);
        border: 1px solid #202a4b;
        padding: 18px;
        border-radius: 16px;
    }

    .block-container {
        padding-top: 2rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    .assistant-box {
        border: 1px solid #2b355a;
        border-radius: 18px;
        padding: 20px;
        background: #0c1227;
    }

    .small-note {
        color: #9aa4bd;
        font-size: 0.9rem;
    }

    .success-box {
        padding: 12px;
        border-radius: 10px;
        background: #103d31;
        color: #b9f6dc;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SAMPLE DATA
# =========================================================

@st.cache_data
def load_sample():
    path = Path(__file__).parent / "data" / "sample_bug_dataset.csv"
    return pd.read_csv(path)


# =========================================================
# SAFE COLUMN HELPERS
# =========================================================

def find_column(df, possible_names):
    """
    Find a column from a list of possible column names.
    Comparison is case-insensitive and ignores spaces/underscores.
    """
    normalized = {}

    for col in df.columns:
        key = (
            str(col)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )
        normalized[key] = col

    for name in possible_names:
        key = (
            str(name)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        if key in normalized:
            return normalized[key]

    return None


def prepare_dashboard_data(raw_df):
    """
    Clean the uploaded dataset and make sure dashboard-required
    columns exist so the application does not crash when optional
    columns such as Team are missing.
    """

    df = raw_df.copy()

    # Existing project preprocessing
    try:
        df = clean_dataset(df)
    except Exception:
        # Fallback cleaning if project utility encounters an
        # unexpected column structure.
        df = df.copy()

        df.columns = [
            str(c).strip().replace(" ", "_").replace("-", "_")
            for c in df.columns
        ]

        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # -----------------------------------------------------
    # Bug ID
    # -----------------------------------------------------

    bug_col = find_column(
        df,
        [
            "Bug_ID",
            "Bug ID",
            "BugID",
            "ID",
            "Defect_ID",
            "Defect ID",
        ],
    )

    if bug_col is None:
        df["Bug_ID"] = range(1, len(df) + 1)
    elif bug_col != "Bug_ID":
        df["Bug_ID"] = df[bug_col]

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status_col = find_column(
        df,
        [
            "Status",
            "Bug_Status",
            "Bug Status",
        ],
    )

    if status_col is None:
        df["Status"] = "Unknown"
    elif status_col != "Status":
        df["Status"] = df[status_col]

    # -----------------------------------------------------
    # Severity
    # -----------------------------------------------------

    severity_col = find_column(
        df,
        [
            "Severity",
            "Bug_Severity",
            "Bug Severity",
        ],
    )

    if severity_col is None:
        df["Severity"] = "Unknown"
    elif severity_col != "Severity":
        df["Severity"] = df[severity_col]

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    priority_col = find_column(
        df,
        [
            "Priority",
            "Bug_Priority",
            "Bug Priority",
        ],
    )

    if priority_col is None:
        df["Priority"] = "Unknown"
    elif priority_col != "Priority":
        df["Priority"] = df[priority_col]

    # -----------------------------------------------------
    # Resolution
    # -----------------------------------------------------

    resolution_col = find_column(
        df,
        [
            "Resolution",
            "Bug_Resolution",
            "Bug Resolution",
        ],
    )

    if resolution_col is None:
        df["Resolution"] = "Unresolved"
    elif resolution_col != "Resolution":
        df["Resolution"] = df[resolution_col]

    # -----------------------------------------------------
    # Root Cause
    # -----------------------------------------------------

    root_col = find_column(
        df,
        [
            "Root_Cause",
            "Root Cause",
            "RootCause",
            "Cause",
        ],
    )

    if root_col is None:
        df["Root_Cause"] = "Unknown"
    elif root_col != "Root_Cause":
        df["Root_Cause"] = df[root_col]

    # -----------------------------------------------------
    # Sprint
    # -----------------------------------------------------

    sprint_col = find_column(
        df,
        [
            "Sprint",
            "Sprint_Name",
            "Sprint Name",
        ],
    )

    if sprint_col is None:
        df["Sprint"] = "Unknown"
    elif sprint_col != "Sprint":
        df["Sprint"] = df[sprint_col]

    # -----------------------------------------------------
    # Release Version
    # -----------------------------------------------------

    release_col = find_column(
        df,
        [
            "Release_Version",
            "Release Version",
            "ReleaseVersion",
            "Version",
        ],
    )

    if release_col is None:
        df["Release_Version"] = "Unknown"
    elif release_col != "Release_Version":
        df["Release_Version"] = df[release_col]

    # -----------------------------------------------------
    # Module
    # -----------------------------------------------------

    module_col = find_column(
        df,
        [
            "Module",
            "Module_Name",
            "Module Name",
        ],
    )

    if module_col is None:
        df["Module"] = "Unknown"
    elif module_col != "Module":
        df["Module"] = df[module_col]

    # -----------------------------------------------------
    # Date Closed
    # -----------------------------------------------------

    date_closed_col = find_column(
        df,
        [
            "Date_Closed",
            "Date Closed",
            "DateClosed",
            "Closed_Date",
            "Closed Date",
        ],
    )

    if date_closed_col is None:
        df["Date_Closed"] = pd.NaT
    elif date_closed_col != "Date_Closed":
        df["Date_Closed"] = pd.to_datetime(
            df[date_closed_col],
            errors="coerce",
        )

    # -----------------------------------------------------
    # TEAM FIX
    # -----------------------------------------------------

    team_col = find_column(
        df,
        [
            "Team",
            "Team_Name",
            "Team Name",
            "Assigned_Team",
            "Assigned Team",
        ],
    )

    if team_col is not None:
        if team_col != "Team":
            df["Team"] = df[team_col]

        df["Team"] = (
            df["Team"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        team_available = True

    else:
        # Do NOT fabricate a team.
        # If an Assignee/Owner exists, use it only as a fallback
        # and clearly label it as Assignee/Owner based performance.
        assignee_col = find_column(
            df,
            [
                "Assignee",
                "Assigned_To",
                "Assigned To",
                "Owner",
                "Developer",
                "Developer_Name",
                "Developer Name",
            ],
        )

        if assignee_col is not None:
            df["Team"] = (
                df[assignee_col]
                .fillna("Unassigned")
                .astype(str)
                .str.strip()
            )
            team_available = True
            st.session_state["team_label"] = "Assignee / Owner Performance"
        else:
            df["Team"] = "Team data unavailable"
            team_available = False
            st.session_state["team_label"] = "Team Performance"

    if "team_label" not in st.session_state:
        st.session_state["team_label"] = "Team Performance"

    # -----------------------------------------------------
    # Derived metrics
    # -----------------------------------------------------

    try:
        df = add_derived_metrics(df)
    except Exception:
        # Safe fallback for resolution time
        if "Resolution_Time_Hours" not in df.columns:
            df["Resolution_Time_Hours"] = np.nan

    # Make sure resolution time is numeric
    if "Resolution_Time_Hours" in df.columns:
        df["Resolution_Time_Hours"] = pd.to_numeric(
            df["Resolution_Time_Hours"],
            errors="coerce",
        )

    return df, team_available


# =========================================================
# PLOTLY THEME HELPER
# =========================================================

def style_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=40),
    )
    return fig


# =========================================================
# MAIN TITLE
# =========================================================

st.title("🐞 Intelligent Software Defect Tracking System")

st.caption(
    "Interactive bug analytics, KPI monitoring, life-cycle tracking "
    "and intelligent resolution assistance."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Dashboard Controls")

    uploaded = st.file_uploader(
        "Upload Bug Dataset",
        type=["csv", "xlsx"],
    )

    if uploaded is not None:

        try:
            if uploaded.name.lower().endswith(".xlsx"):
                raw = pd.read_excel(uploaded)
            else:
                raw = pd.read_csv(uploaded)

            st.success(
                f"{len(raw):,} bug records loaded"
            )

        except Exception as e:
            st.error(
                f"Unable to read the uploaded file: {e}"
            )
            st.stop()

    else:

        raw = load_sample()

        st.success(
            f"{len(raw):,} sample bug records loaded"
        )

    st.divider()

    st.subheader("🔎 Filters")

    sprint_options = ["All"]

    if "Sprint" in raw.columns:
        sprint_options += sorted(
            raw["Sprint"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    release_options = ["All"]

    if "Release_Version" in raw.columns:
        release_options += sorted(
            raw["Release_Version"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    sprint = st.selectbox(
        "Sprint",
        sprint_options,
    )

    release = st.selectbox(
        "Release Version",
        release_options,
    )

    st.caption(
        "Upload your Google Sheets export as CSV/XLSX "
        "to analyze your exact dataset."
    )


# =========================================================
# DATA PREPARATION
# =========================================================

df, team_available = prepare_dashboard_data(raw)

try:
    filtered = filter_data(
        df,
        sprint,
        release,
    )
except Exception:
    filtered = df.copy()

# =========================================================
# KPI CALCULATION
# =========================================================

try:
    k = calculate_kpis(filtered)
except Exception:

    total = len(filtered)

    closed = int(
        (
            filtered["Status"]
            .astype(str)
            .str.lower()
            .eq("closed")
        ).sum()
    )

    open_bugs = total - closed

    critical = int(
        (
            filtered["Severity"]
            .astype(str)
            .str.lower()
            .eq("critical")
        ).sum()
    )

    avg_resolution = (
        filtered["Resolution_Time_Hours"]
        .dropna()
        .mean()
        if "Resolution_Time_Hours" in filtered.columns
        else 0
    )

    closure_rate = (
        closed / total * 100
        if total > 0
        else 0
    )

    k = {
        "total": total,
        "open": open_bugs,
        "closed": closed,
        "avg_resolution": avg_resolution,
        "critical": critical,
        "closure_rate": closure_rate,
    }


# =========================================================
# KPI CARDS
# =========================================================

st.markdown("### 📌 Project KPIs")

c = st.columns(6)

c[0].metric(
    "Total Bugs",
    f"{k['total']:,}",
)

c[1].metric(
    "Open Bugs",
    f"{k['open']:,}",
)

c[2].metric(
    "Closed Bugs",
    f"{k['closed']:,}",
)

c[3].metric(
    "Avg Resolution",
    f"{k['avg_resolution']:.1f} h",
)

c[4].metric(
    "Critical Bugs",
    f"{k['critical']:,}",
)

c[5].metric(
    "Closure Rate",
    f"{k['closure_rate']:.1f}%",
)


# =========================================================
# TABS
# =========================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "🔄 Life Cycle & Trends",
        "🏃 Sprint & Module",
        "👥 Team Performance",
        "🧠 Resolution Assistance",
        "📋 Data Explorer",
    ]
)


# =========================================================
# TAB 1 - OVERVIEW
# =========================================================

with tabs[0]:

    st.subheader("📊 Bug Overview")

    a, b = st.columns(2)

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    with a:

        vc = (
            filtered["Status"]
            .value_counts()
            .reset_index()
        )

        vc.columns = ["Status", "Count"]

        fig = px.pie(
            vc,
            names="Status",
            values="Count",
            hole=0.45,
            title="Bug Status Distribution",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    with b:

        severity_order = [
            "High",
            "Medium",
            "Low",
            "Critical",
        ]

        vc = (
            filtered["Severity"]
            .value_counts()
            .reindex(severity_order)
            .fillna(0)
            .reset_index()
        )

        vc.columns = [
            "Severity",
            "Count",
        ]

        fig = px.bar(
            vc,
            x="Count",
            y="Severity",
            orientation="h",
            text="Count",
            title="Bugs by Severity",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------

    a, b = st.columns(2)

    with a:

        vc = (
            filtered["Priority"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        vc.columns = [
            "Priority",
            "Count",
        ]

        fig = px.bar(
            vc,
            x="Priority",
            y="Count",
            text="Count",
            title="Bugs by Priority",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # RESOLUTION
    # -----------------------------------------------------

    with b:

        vc = (
            filtered["Resolution"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        vc.columns = [
            "Resolution",
            "Count",
        ]

        fig = px.bar(
            vc,
            x="Resolution",
            y="Count",
            text="Count",
            title="Resolution Type",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )


# =========================================================
# TAB 2 - LIFE CYCLE & TRENDS
# =========================================================

with tabs[1]:

    st.subheader(
        "🔄 Bug Life Cycle & Resolution Trends"
    )

    closed = filtered.copy()

    if "Date_Closed" in closed.columns:

        closed = closed.dropna(
            subset=["Date_Closed"]
        )

    if not closed.empty:

        closed["Date_Closed"] = pd.to_datetime(
            closed["Date_Closed"],
            errors="coerce",
        )

        closed = closed.dropna(
            subset=["Date_Closed"]
        )

    if not closed.empty:

        weekly = (
            closed.assign(
                Week=closed["Date_Closed"]
                .dt.to_period("W")
                .dt.start_time
            )
            .groupby("Week")
            .agg(
                Closed_Bugs=("Bug_ID", "count"),
                Avg_Resolution_Hours=(
                    "Resolution_Time_Hours",
                    "mean",
                ),
            )
            .reset_index()
        )

        a, b = st.columns(2)

        with a:

            fig = px.line(
                weekly,
                x="Week",
                y="Closed_Bugs",
                markers=True,
                title="Weekly Bugs Closed",
            )

            st.plotly_chart(
                style_fig(fig),
                use_container_width=True,
            )

        with b:

            fig = px.line(
                weekly,
                x="Week",
                y="Avg_Resolution_Hours",
                markers=True,
                title="Weekly Average Resolution Time",
            )

            st.plotly_chart(
                style_fig(fig),
                use_container_width=True,
            )

    else:

        st.info(
            "Date Closed information is not available "
            "for the current filtered dataset."
        )

    # -----------------------------------------------------
    # CURRENT LIFE CYCLE
    # -----------------------------------------------------

    a, b = st.columns(2)

    with a:

        vc = (
            filtered["Status"]
            .value_counts()
            .reset_index()
        )

        vc.columns = [
            "Status",
            "Count",
        ]

        fig = px.bar(
            vc,
            x="Status",
            y="Count",
            text="Count",
            title="Current Life Cycle Status",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # ROOT CAUSE
    # -----------------------------------------------------

    with b:

        rc = (
            filtered["Root_Cause"]
            .value_counts()
            .head(8)
            .reset_index()
        )

        rc.columns = [
            "Root Cause",
            "Count",
        ]

        fig = px.bar(
            rc,
            x="Count",
            y="Root Cause",
            orientation="h",
            text="Count",
            title="Top Root Causes",
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )


# =========================================================
# TAB 3 - SPRINT & MODULE
# =========================================================

with tabs[2]:

    st.subheader(
        "🏃 Sprint-wise & Module-wise Analysis"
    )

    # -----------------------------------------------------
    # SPRINT DISTRIBUTION
    # -----------------------------------------------------

    sprint_counts = (
        filtered["Sprint"]
        .value_counts()
        .reset_index()
    )

    sprint_counts.columns = [
        "Sprint",
        "Bug_Count",
    ]

    fig = px.bar(
        sprint_counts,
        x="Sprint",
        y="Bug_Count",
        text="Bug_Count",
        title="Sprint-wise Bug Distribution",
    )

    st.plotly_chart(
        style_fig(fig),
        use_container_width=True,
    )

    # -----------------------------------------------------
    # MODULE & STATUS
    # -----------------------------------------------------

    module_status = pd.crosstab(
        filtered["Module"],
        filtered["Status"],
    ).reset_index()

    long_data = module_status.melt(
        id_vars="Module",
        var_name="Status",
        value_name="Bug_Count",
    )

    fig = px.bar(
        long_data,
        x="Module",
        y="Bug_Count",
        color="Status",
        title="Bugs by Module & Status",
    )

    fig.update_layout(
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        style_fig(fig),
        use_container_width=True,
    )

    # -----------------------------------------------------
    # MODULE PERFORMANCE
    # -----------------------------------------------------

    module_perf = (
        filtered
        .groupby("Module")
        .agg(
            Bugs=("Bug_ID", "count"),
            Avg_Resolution_Hours=(
                "Resolution_Time_Hours",
                "mean",
            ),
            Critical=(
                "Severity",
                lambda s: (
                    s.astype(str)
                    .str.lower()
                    .eq("critical")
                ).sum(),
            ),
        )
        .reset_index()
        .sort_values(
            "Bugs",
            ascending=False,
        )
    )

    st.markdown("### Module Performance")

    st.dataframe(
        module_perf.round(2),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# TAB 4 - TEAM PERFORMANCE
# =========================================================

with tabs[3]:

    st.subheader(
        "👥 Team Performance"
    )

    # IMPORTANT:
    # The application no longer crashes if Team is missing.
    # If Assignee/Owner exists, it is used as a fallback.
    # Otherwise a clear message is displayed.

    if team_available:

        performance_label = st.session_state.get(
            "team_label",
            "Team Performance",
        )

        st.caption(
            f"Performance analysis based on: {performance_label}"
        )

        team = (
            filtered
            .groupby("Team")
            .agg(
                Bugs=("Bug_ID", "count"),
                Avg_Resolution_Hours=(
                    "Resolution_Time_Hours",
                    "mean",
                ),
                Closed=(
                    "Status",
                    lambda s: (
                        s.astype(str)
                        .str.lower()
                        .eq("closed")
                    ).sum(),
                ),
            )
            .reset_index()
        )

        team["Closure_Rate_%"] = np.where(
            team["Bugs"] > 0,
            team["Closed"] / team["Bugs"] * 100,
            0,
        )

        a, b = st.columns(2)

        # -------------------------------------------------
        # AVERAGE RESOLUTION
        # -------------------------------------------------

        with a:

            team_sorted = team.sort_values(
                "Avg_Resolution_Hours"
            )

            fig = px.bar(
                team_sorted,
                x="Team",
                y="Avg_Resolution_Hours",
                text_auto=".1f",
                title="Average Resolution Time by Team",
            )

            st.plotly_chart(
                style_fig(fig),
                use_container_width=True,
            )

        # -------------------------------------------------
        # CLOSURE RATE
        # -------------------------------------------------

        with b:

            team_sorted = team.sort_values(
                "Closure_Rate_%"
            )

            fig = px.bar(
                team_sorted,
                x="Team",
                y="Closure_Rate_%",
                text_auto=".1f",
                title="Team Closure Rate",
            )

            st.plotly_chart(
                style_fig(fig),
                use_container_width=True,
            )

        # -------------------------------------------------
        # TEAM KPI TABLE
        # -------------------------------------------------

        st.markdown("### Team KPI Table")

        st.dataframe(
            team.round(2),
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "Action: prioritize teams/modules with high "
            "average resolution time and low closure rate."
        )

    else:

        st.warning(
            "Team information is not available in the uploaded dataset."
        )

        st.info(
            "Add a 'Team' column or an 'Assignee/Owner' column "
            "to enable team-level performance analysis."
        )

        st.markdown(
            """
            **Available analysis is still fully functional:**

            - 📊 Overall bug KPIs
            - 🔄 Life-cycle trends
            - 🏃 Sprint analysis
            - 🧩 Module analysis
            - 🎯 Severity and Priority
            - 🧠 Defect Assistant
            - 📋 Data Explorer
            """
        )


# =========================================================
# TAB 5 - DEFECT ASSISTANT
# =========================================================

with tabs[4]:

    st.subheader(
        "🧠 Defect Assistant"
    )

    st.caption(
        "Ask about bugs, sprints, resolution time, priorities, "
        "severity, teams or modules. The assistant answers from "
        "the currently filtered dataset."
    )

    st.markdown(
        '<div class="assistant-box">',
        unsafe_allow_html=True,
    )

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # Display previous messages
    for role, message in st.session_state.chat:

        if role == "user":

            st.markdown(
                f"**You:** {message}"
            )

        else:

            st.markdown(
                f"**🤖 Defect Assistant:** {message}"
            )

    with st.form(
        "assistant_form",
        clear_on_submit=True,
    ):

        question = st.text_area(
            "Ask about your defect data",
            placeholder=(
                "e.g. Which module has the most critical bugs?"
            ),
        )

        submitted = st.form_submit_button(
            "Send"
        )

    if submitted and question.strip():

        question = question.strip()

        st.session_state.chat.append(
            ("user", question)
        )

        try:

            answer = answer_question(
                question,
                filtered,
            )

        except Exception as e:

            answer = (
                "I couldn't process that question. "
                f"Please try another question. Details: {e}"
            )

        st.session_state.chat.append(
            ("assistant", answer)
        )

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# TAB 6 - DATA EXPLORER
# =========================================================

with tabs[5]:

    st.subheader(
        "📋 Data Explorer"
    )

    selected_columns = st.multiselect(
        "Columns",
        filtered.columns.tolist(),
        default=filtered.columns.tolist(),
    )

    if selected_columns:

        st.dataframe(
            filtered[selected_columns],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Select at least one column to display the data."
        )

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download filtered CSV",
        csv_data,
        "filtered_bug_dataset.csv",
        "text/csv",
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Built with Python • Streamlit • Pandas • Plotly | MIT Licensed"
)
