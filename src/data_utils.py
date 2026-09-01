
import re
import pandas as pd
import numpy as np

ALIASES = {
    "Bug ID":"Bug_ID","BugID":"Bug_ID","Bug Id":"Bug_ID",
    "Release Version":"Release_Version","Release":"Release_Version",
    "Date Closed":"Date_Closed","Date Reported":"Date_Reported",
    "Root Cause":"Root_Cause","Resolution Time":"Resolution_Time_Hours",
    "Team Name":"Team"
}

def clean_dataset(df):
    df=df.copy()
    df.columns=[ALIASES.get(str(c).strip(),str(c).strip().replace(" ","_")) for c in df.columns]
    if "Bug_ID" not in df.columns:
        df["Bug_ID"]=[f"BUG-{i:04d}" for i in range(1,len(df)+1)]
    for c in ["Status","Severity","Priority","Sprint","Release_Version","Module","Feature","Component","Resolution","Root_Cause","Team"]:
        if c in df.columns:
            df[c]=df[c].astype("string").str.strip()
            df[c]=df[c].fillna("Unknown")
    for c in ["Date_Reported","Date_Closed"]:
        if c in df.columns:
            df[c]=pd.to_datetime(df[c],errors="coerce")
    if "Resolution_Time_Hours" in df.columns:
        df["Resolution_Time_Hours"]=pd.to_numeric(df["Resolution_Time_Hours"],errors="coerce")
    df=df.drop_duplicates(subset=["Bug_ID"]).reset_index(drop=True)
    return df

def add_derived_metrics(df):
    df=df.copy()
    if "Resolution_Time_Hours" not in df.columns:
        df["Resolution_Time_Hours"]=np.nan
    if {"Date_Reported","Date_Closed"}.issubset(df.columns):
        calc=(df["Date_Closed"]-df["Date_Reported"]).dt.total_seconds()/3600
        df["Resolution_Time_Hours"]=df["Resolution_Time_Hours"].fillna(calc)
    return df

def filter_data(df,sprint="All",release="All"):
    out=df
    if sprint!="All" and "Sprint" in out.columns:
        out=out[out["Sprint"].astype(str)==sprint]
    if release!="All" and "Release_Version" in out.columns:
        out=out[out["Release_Version"].astype(str)==release]
    return out.copy()

def calculate_kpis(df):
    total=len(df)
    closed=int((df["Status"].astype(str).str.lower()=="closed").sum()) if "Status" in df else 0
    open_bugs=total-closed
    avg=float(pd.to_numeric(df.get("Resolution_Time_Hours",pd.Series(dtype=float)),errors="coerce").mean() or 0)
    critical=int((df["Severity"].astype(str).str.lower()=="critical").sum()) if "Severity" in df else 0
    return {
        "total":total,"open":open_bugs,"closed":closed,"avg_resolution":avg,
        "critical":critical,"closure_rate":(closed/total*100 if total else 0)
    }

def answer_question(q,df):
    ql=q.lower()
    k=calculate_kpis(df)
    if "how many" in ql and "bug" in ql:
        return f"There are {k['total']} bugs in the current filtered dataset, with {k['closed']} closed and {k['open']} not closed."
    if "critical" in ql and "module" in ql:
        t=df[df["Severity"].astype(str).str.lower()=="critical"].groupby("Module").size().sort_values(ascending=False)
        if len(t): return f"The module with the most critical bugs is {t.index[0]} with {int(t.iloc[0])} critical bugs."
    if "critical" in ql:
        return f"There are {k['critical']} critical bugs in the current filtered dataset."
    if "resolution" in ql or "resolve" in ql:
        return f"The average resolution time is {k['avg_resolution']:.1f} hours. Focus first on teams/modules above this average."
    if "sprint" in ql and "most" in ql:
        t=df.groupby("Sprint").size().sort_values(ascending=False)
        if len(t): return f"{t.index[0]} has the highest bug count with {int(t.iloc[0])} bugs."
    if "module" in ql and ("most" in ql or "highest" in ql):
        t=df.groupby("Module").size().sort_values(ascending=False)
        if len(t): return f"{t.index[0]} has the highest bug volume with {int(t.iloc[0])} bugs."
    if "priority" in ql:
        t=df["Priority"].value_counts()
        if len(t): return f"The most common priority is {t.index[0]} with {int(t.iloc[0])} bugs."
    if "team" in ql:
        t=df.groupby("Team").agg(Bugs=("Bug_ID","count"),Avg_Hours=("Resolution_Time_Hours","mean")).sort_values("Avg_Hours")
        if len(t): return f"{t.index[0]} has the fastest average resolution time at {t.iloc[0]['Avg_Hours']:.1f} hours."
    if "status" in ql:
        t=df["Status"].value_counts()
        if len(t): return f"The most common status is {t.index[0]} with {int(t.iloc[0])} bugs."
    return ("I can answer questions about bug count, critical bugs, modules, sprints, "
            "priorities, status, teams and resolution time. Try: 'Which module has the most critical bugs?'")
