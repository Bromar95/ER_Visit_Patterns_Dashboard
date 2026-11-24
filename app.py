import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ER Visit Patterns Dashboard", page_icon="🚑", layout="wide")


# Full-width charts and tables on both newer and older Streamlit versions
def show_chart(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def show_table(data):
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(data, use_container_width=True, hide_index=True)


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TRIAGE_ORDER = ["Critical", "High", "Medium", "Low"]
TRIAGE_COLORS = {"Critical": "#D62728", "High": "#FF7F0E", "Medium": "#F2C14E", "Low": "#2CA02C"}


# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("emergency_room_visits.csv")
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    # Create day of week column
    df["day_of_week"] = pd.Categorical(df["visit_date"].dt.day_name(), categories=DAY_ORDER, ordered=True)
    df["shift"] = df["visit_time_hour"].apply(lambda h: "Day (7am to 7pm)" if 7 <= h < 19 else "Night (7pm to 7am)")
    df["age_group"] = pd.cut(df["patient_age"], bins=[-1, 17, 39, 64, 120],
                             labels=["Under 18", "18 to 39", "40 to 64", "65 and older"])
    return df


df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")

min_date, max_date = df["visit_date"].min().date(), df["visit_date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)

# Day-of-week filter (in calendar order)
selected_day = st.sidebar.selectbox("Select Day of Week", ["All"] + DAY_ORDER)

# Time slider (hour of day)
hour_range = st.sidebar.slider("Select Hour Range", min_value=0, max_value=23, value=(0, 23))

selected_triage = st.sidebar.multiselect("Triage level", TRIAGE_ORDER, default=TRIAGE_ORDER)
reasons = sorted(df["visit_reason"].unique().tolist())
selected_reasons = st.sidebar.multiselect("Visit reason", reasons, default=reasons)

# Target wait times by triage level (editable so the hospital can use its own standards)
with st.sidebar.expander("Target wait times (minutes)"):
    st.caption("Example targets based on common five-level triage scales. Adjust to match your hospital's standards.")
    targets = {
        "Critical": st.number_input("Critical", 0, 240, 10),
        "High": st.number_input("High", 0, 240, 30),
        "Medium": st.number_input("Medium", 0, 240, 60),
        "Low": st.number_input("Low", 0, 240, 120),
    }

# Apply filters
filtered_df = df[(df["visit_time_hour"] >= hour_range[0]) & (df["visit_time_hour"] <= hour_range[1])]
if selected_day != "All":
    filtered_df = filtered_df[filtered_df["day_of_week"] == selected_day]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["visit_date"] >= start) & (filtered_df["visit_date"] <= end)]
filtered_df = filtered_df[filtered_df["triage_level"].isin(selected_triage)
                          & filtered_df["visit_reason"].isin(selected_reasons)].copy()
filtered_df["target_minutes"] = filtered_df["triage_level"].map(targets)
filtered_df["met_target"] = filtered_df["wait_time_minutes"] <= filtered_df["target_minutes"]

# Dashboard Title
st.title("🚑 Emergency Room Visit Patterns Dashboard")
st.write(f"Showing **{len(filtered_df)}** of {len(df)} ER visits")

if filtered_df.empty:
    st.warning("No visits match these filters. Try widening the date range or selecting more options.")
    st.stop()

# KPI Row
days_in_view = filtered_df["visit_date"].nunique()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total visits", f"{len(filtered_df):,}")
k2.metric("Visits per day", f"{len(filtered_df) / max(days_in_view, 1):.1f}")
k3.metric("Median wait", f"{filtered_df['wait_time_minutes'].median():.0f} min")
k4.metric("Seen within target", f"{filtered_df['met_target'].mean():.0%}")
k5.metric("Critical or High", f"{filtered_df['triage_level'].isin(['Critical', 'High']).mean():.0%}")

tab_overview, tab_clinical, tab_ops, tab_quality = st.tabs(
    ["📊 Visit Patterns", "🩺 Clinical Quality", "🏥 Operations & Staffing", "🔍 Data Quality"]
)

# ---------------- Visit Patterns tab ----------------
with tab_overview:
    # ER Visits by Hour
    st.subheader("⏰ ER Visits by Hour of the Day")
    hourly_visits = filtered_df.groupby("visit_time_hour").size().reset_index(name="visit_count")
    fig_hour = px.bar(hourly_visits, x="visit_time_hour", y="visit_count",
                      labels={"visit_time_hour": "Hour of Day", "visit_count": "Number of Visits"},
                      title="ER Visits by Hour")
    fig_hour.update_xaxes(dtick=1)
    show_chart(fig_hour)

    col1, col2 = st.columns(2)

    # Common Visit Reasons
    with col1:
        st.subheader("🩺 Common ER Visit Reasons")
        reason_counts = filtered_df["visit_reason"].value_counts().reset_index()
        reason_counts.columns = ["visit_reason", "count"]
        fig_reason = px.bar(reason_counts, x="count", y="visit_reason", orientation="h", text="count",
                            title="Most Common ER Visit Reasons",
                            labels={"visit_reason": "", "count": "Visits"})
        fig_reason.update_yaxes(categoryorder="total ascending")
        show_chart(fig_reason)

    # Triage mix
    with col2:
        st.subheader("🚦 Triage Mix")
        triage_counts = filtered_df["triage_level"].value_counts().reindex(TRIAGE_ORDER, fill_value=0).reset_index()
        triage_counts.columns = ["triage_level", "visits"]
        fig_triage = px.pie(triage_counts, names="triage_level", values="visits", hole=0.45,
                            color="triage_level", color_discrete_map=TRIAGE_COLORS,
                            title="Share of Visits by Triage Level")
        show_chart(fig_triage)

    # Visit reason by age group
    by_age = filtered_df.groupby(["age_group", "visit_reason"], observed=True).size().reset_index(name="visits")
    fig_age = px.bar(by_age, x="age_group", y="visits", color="visit_reason",
                     title="Visit Reasons by Age Group",
                     labels={"age_group": "Age group", "visits": "Visits", "visit_reason": "Reason"})
    show_chart(fig_age)

# ---------------- Clinical Quality tab ----------------
with tab_clinical:
    st.subheader("⏱️ Are Patients Seen Within the Target Time for Their Triage Level?")

    triage_summary = (filtered_df.groupby("triage_level")
                      .agg(visits=("visit_id", "size"),
                           median_wait=("wait_time_minutes", "median"),
                           longest_wait=("wait_time_minutes", "max"),
                           met_target=("met_target", "mean"))
                      .reindex([t for t in TRIAGE_ORDER if t in filtered_df["triage_level"].unique()])
                      .reset_index())
    triage_summary["target"] = triage_summary["triage_level"].map(targets)
    triage_summary["met_target"] = (triage_summary["met_target"] * 100).round(1)
    triage_summary = triage_summary[["triage_level", "visits", "target", "median_wait", "longest_wait", "met_target"]]
    triage_summary.columns = ["Triage level", "Visits", "Target (min)", "Median wait (min)",
                              "Longest wait (min)", "Seen within target (%)"]
    show_table(triage_summary)

    fig_wait = px.box(filtered_df, x="triage_level", y="wait_time_minutes", color="triage_level",
                      category_orders={"triage_level": TRIAGE_ORDER}, color_discrete_map=TRIAGE_COLORS,
                      title="Wait Time by Triage Level (sicker patients should wait less)",
                      labels={"triage_level": "Triage level", "wait_time_minutes": "Wait (minutes)"})
    fig_wait.update_layout(showlegend=False)
    show_chart(fig_wait)

    c1, c2 = st.columns(2)

    # Chest pain: ECG is expected within about 10 minutes of arrival
    with c1:
        st.subheader("❤️ Chest Pain")
        chest = filtered_df[filtered_df["visit_reason"] == "Chest Pain"]
        if chest.empty:
            st.write("No chest pain visits in the current filters.")
        else:
            m1, m2 = st.columns(2)
            m1.metric("Chest pain visits", len(chest))
            m2.metric("Seen within 10 min", f"{(chest['wait_time_minutes'] <= 10).mean():.0%}")
            st.caption("Guidelines call for an ECG within about 10 minutes of arrival for chest pain, "
                       "because a heart attack can be ruled in or out quickly.")

    # Pediatric share
    with c2:
        st.subheader("🧒 Pediatric Visits")
        peds = filtered_df[filtered_df["patient_age"] < 18]
        m1, m2 = st.columns(2)
        m1.metric("Patients under 18", f"{len(peds)} ({len(peds) / len(filtered_df):.0%})")
        m2.metric("Median pediatric wait", f"{peds['wait_time_minutes'].median():.0f} min" if len(peds) else "n/a")
        st.caption("Pediatric volume helps decide whether a separate pediatric area or staff is needed.")

    # High-acuity patients who waited too long
    st.subheader("🚨 High-Acuity Patients Who Waited More Than 60 Minutes")
    long_waits = filtered_df[filtered_df["triage_level"].isin(["Critical", "High"])
                             & (filtered_df["wait_time_minutes"] > 60)].sort_values("wait_time_minutes", ascending=False)
    st.write(f"**{len(long_waits)}** Critical or High patients waited more than an hour. "
             "Each one is a case a quality team would review.")
    show_table(long_waits[["visit_id", "visit_date", "visit_time_hour", "patient_age", "gender",
                           "visit_reason", "triage_level", "wait_time_minutes"]]
               .assign(visit_date=lambda d: d["visit_date"].dt.date))

# ---------------- Operations & Staffing tab ----------------
with tab_ops:
    # Daily volume trend
    st.subheader("📅 Daily Visit Volume")
    daily = filtered_df.groupby("visit_date").size().reset_index(name="visits")
    daily["7-day average"] = daily["visits"].rolling(7, min_periods=1).mean()
    fig_daily = px.line(daily, x="visit_date", y=["visits", "7-day average"],
                        labels={"visit_date": "Date", "value": "Visits", "variable": ""},
                        title="Visits per Day with 7-Day Average")
    show_chart(fig_daily)

    # ER Load Heatmap: average arrivals per hour, so busy slots are easy to staff
    st.subheader("🔥 ER Load Heatmap (Day vs Hour)")
    weeks = max(filtered_df["visit_date"].dt.isocalendar().week.nunique(), 1)
    heatmap_df = (filtered_df.groupby(["day_of_week", "visit_time_hour"], observed=False).size()
                  .unstack(fill_value=0).reindex(index=DAY_ORDER, columns=range(24), fill_value=0))
    fig_heatmap = px.imshow(heatmap_df / weeks, aspect="auto", color_continuous_scale="Reds",
                            labels={"x": "Hour of Day", "y": "Day of Week", "color": "Avg arrivals"},
                            title="Average Arrivals per Hour Slot (per week)")
    fig_heatmap.update_xaxes(dtick=1)
    show_chart(fig_heatmap)

    # Wait-time heatmap: where the bottlenecks are
    wait_heat = (filtered_df.pivot_table(index="day_of_week", columns="visit_time_hour",
                                         values="wait_time_minutes", aggfunc="median", observed=False)
                 .reindex(index=DAY_ORDER, columns=range(24)))
    fig_waitheat = px.imshow(wait_heat, aspect="auto", color_continuous_scale="Purples",
                             labels={"x": "Hour of Day", "y": "Day of Week", "color": "Median wait (min)"},
                             title="Median Wait Time by Day and Hour (bottlenecks)")
    fig_waitheat.update_xaxes(dtick=1)
    show_chart(fig_waitheat)

    c1, c2 = st.columns(2)

    # Day vs night shift
    with c1:
        st.subheader("🌗 Day vs Night Shift")
        shift = (filtered_df.groupby("shift")
                 .agg(visits=("visit_id", "size"), median_wait=("wait_time_minutes", "median"),
                      met_target=("met_target", "mean"))
                 .reset_index())
        shift["met_target"] = (shift["met_target"] * 100).round(1)
        shift.columns = ["Shift", "Visits", "Median wait (min)", "Seen within target (%)"]
        show_table(shift)

    # Weekday vs weekend
    with c2:
        st.subheader("📆 Busiest Days")
        by_day = filtered_df.groupby("day_of_week", observed=False).size().reset_index(name="visits")
        fig_days = px.bar(by_day, x="day_of_week", y="visits", text="visits",
                          labels={"day_of_week": "", "visits": "Visits"}, title="Visits by Day of Week")
        show_chart(fig_days)

    # Peak hours for staffing
    top_hours = hourly_visits.sort_values("visit_count", ascending=False).head(3)["visit_time_hour"].tolist()
    st.info(f"**Staffing note:** the busiest arrival hours in the current view are "
            f"**{', '.join(f'{h}:00' for h in top_hours)}**. Those are the hours where extra triage "
            "nurses would cut waits the most.")

    st.download_button("⬇️ Download filtered data (CSV)",
                       filtered_df.drop(columns=["target_minutes"]).to_csv(index=False),
                       file_name="filtered_er_visits.csv", mime="text/csv")

# ---------------- Data Quality tab ----------------
with tab_quality:
    st.subheader("🔍 Clinical Data Quality Checks")

    all_targets = df["triage_level"].map(targets)
    crit = df[df["triage_level"] == "Critical"]
    low = df[df["triage_level"] == "Low"]
    young_chest = df[(df["visit_reason"] == "Chest Pain") & (df["patient_age"] < 5)]
    hour_counts = df.groupby("visit_time_hour").size()

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Median wait: Critical", f"{crit['wait_time_minutes'].median():.0f} min")
    q2.metric("Median wait: Low", f"{low['wait_time_minutes'].median():.0f} min")
    q3.metric("Seen within target (all)", f"{(df['wait_time_minutes'] <= all_targets).mean():.0%}")
    q4.metric("Chest pain under age 5", len(young_chest))

    st.markdown(
        f"""
- **Triage level does not change the wait.** Critical patients waited a median of
  {crit['wait_time_minutes'].median():.0f} minutes, close to the {low['wait_time_minutes'].median():.0f} minutes
  for Low-priority patients. In a real ER, critical patients are seen right away.
- **Wait times are spread evenly from about 5 to 240 minutes** for every triage level and every visit reason,
  which looks like random numbers rather than a real queue.
- **The busiest hour is {hour_counts.idxmax()}:00 and the quietest is {hour_counts.idxmin()}:00.** Real ERs are
  usually busiest from late morning to evening and quietest overnight.
- **{len(young_chest)} chest pain visits are for children under 5**, which is unusual as a main complaint.
- There are no missing values, and visits are spread almost evenly across all seven days.

Together these suggest the dataset is synthetic. The dashboard methods are sound, but the results should be
read as a demonstration, not as real ER performance.
"""
    )

st.info("Use the filters on the left to explore ER visit patterns by time and day.")