# 🚑 Emergency Room Visit Patterns Dashboard with Streamlit

🚀 **Live App:** [er-visit-patterns-dashboard.streamlit.app](https://er-visit-patterns-dashboard.streamlit.app/)

## 📌 Project Overview

This project is an interactive dashboard built in Python and Streamlit to analyze emergency room (ER) visits. It uses 600 visits from January to April 2025, with visit date, arrival hour, patient age, gender, visit reason, triage level, and wait time.

The base dashboard shows ER visits by hour of the day, the most common visit reasons, and a heatmap of ER workload by day and hour. I then expanded it to answer the questions two different audiences would ask. A clinician wants to know whether patients are seen within the target time for how sick they are. A hospital administrator wants to know when the ER is busiest, where the bottlenecks are, and how to staff for them. I added triage target tracking, chest pain and high-acuity wait reviews, daily volume trends, a wait-time bottleneck heatmap, and day vs. night shift comparisons. I also audited the data for clinical plausibility and found that **critical patients waited almost as long as low-priority patients**, the opposite of how a real ER works.

## 🎯 Key Features

✅ KPI Summary: Total visits, visits per day, median wait, % seen within target, and % Critical or High, updating with every filter.<br>
✅ Visits by Hour: Shows when patients arrive across the 24-hour day.<br>
✅ Common Visit Reasons: Ranks the reasons patients come to the ER.<br>
✅ Triage Mix and Age Groups: Shows the share of each triage level and visit reasons by age group.<br>
✅ Triage Target Tracking: Compares each triage level's wait with an editable target time.<br>
✅ Chest Pain Review: Measures how many chest pain patients were seen within 10 minutes.<br>
✅ High-Acuity Case List: Lists Critical and High patients who waited more than an hour.<br>
✅ Pediatric Visits: Shows the share and median wait of patients under 18.<br>
✅ ER Load Heatmap: Average arrivals per hour slot, per week, by day and hour.<br>
✅ Bottleneck Heatmap: Median wait time by day and hour.<br>
✅ Shift and Day Comparisons: Day vs. night shift performance and visits by day of week, with a staffing note.<br>
✅ Data Quality Tab: Flags wait times that do not match triage level and other implausible patterns.<br>
✅ Interactive Filters and Export: Filters by date, day, hour, triage level, and visit reason, with CSV download.

## 🗂️ Repository Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit app that builds the interactive dashboard |
| `emergency_room_visits.csv` | Raw dataset: 600 rows and 8 columns of ER visit records |
| `requirements.txt` | Packages used to deploy the app |

## 🧹 Data Preparation

- Loaded the data with `pd.read_csv()` using a relative file path, so the app runs on any computer and on Streamlit Cloud.
- Confirmed the dataset has no missing values.
- Converted `visit_date` to a datetime column and created a `day_of_week` column in calendar order (Monday to Sunday).
- Grouped arrivals into day shift (7am to 7pm) and night shift (7pm to 7am).
- Grouped patient age into four bands: under 18, 18 to 39, 40 to 64, and 65 and older.
- Set target wait times by triage level (Critical 10, High 30, Medium 60, and Low 120 minutes) and made them editable in the sidebar, so a hospital can apply its own standards.
- Changed the workload heatmap to show **average arrivals per hour slot, per week**, so each cell reads as the number of patients a team should expect.
- Cached the loaded data with `@st.cache_data` so filters respond quickly.
- **Flagged a clinical plausibility issue.** Critical patients waited a median of about 100 minutes, close to the 126 minutes for Low-priority patients, and waits were spread evenly from 5 to 239 minutes for every triage level and visit reason. The busiest arrival hour was 7am and the quietest was 11am, while real ERs are usually busiest from late morning to evening. These point to synthetic practice data, so the results should be read as a demonstration of the method, not as real ER performance.

## 🛠️ Skills & Tools Applied

- Language and Environment: Python, Visual Studio Code
- Libraries: pandas, Plotly Express, Streamlit
- Analysis: Grouping and aggregation, pivot tables, rolling averages, target compliance rates
- Visualization: Bar, stacked bar, donut, box, line, and heatmap charts
- App Development: Tabs, sidebar filters, editable targets, KPI metrics, data caching, CSV download
- Deployment: GitHub and Streamlit Community Cloud
- Clinical and Operational Knowledge: Triage levels and target times, chest pain evaluation, ER staffing and shift planning

## 📈 Business Questions Answered

This project provides insights into:

- When do patients arrive, and why do they come to the ER?
- Are patients seen within the target time for their triage level?
- Are chest pain and other high-acuity patients seen quickly enough?
- Which days and hours are the busiest, and where do waits build up?
- How do the day and night shifts compare?
- Is the data clinically plausible?

## 💡 Key Insights

### Overall ER Activity (600 visits)

- The ER averaged **5.1 visits per day**, ranging from 1 to 11.
- The median wait was **118 minutes**, and only **30% of patients were seen within their target time**.
- **Breathing difficulty (87), fever (85), and allergic reactions (76)** were the most common visit reasons.
- **125 visits (21%) were patients under 18**, with a median wait of 115 minutes.
- Visits were spread almost evenly across the week, from 77 on Saturdays to 92 on Tuesdays and Fridays.

### Wait Times by Triage Level

| Triage Level | Visits | Target | Median Wait | Longest Wait | Seen Within Target |
|---|---|---|---|---|---|
| Critical | 24 | 10 min | **100 min** | 233 min | **4.2%** |
| High | 117 | 30 min | 117 min | 239 min | 10.3% |
| Medium | 212 | 60 min | 110 min | 239 min | 26.4% |
| Low | 247 | 120 min | 126 min | 238 min | 45.7% |

- **Only 1 of 24 critical patients was seen within 10 minutes.** Critical patients should be seen first, but their median wait was close to that of low-priority patients.
- **102 of 141 Critical or High patients waited more than an hour**, and each one appears on the case list for quality review.
- **Only 2 of 74 chest pain patients (2.7%) were seen within 10 minutes**, the window for getting an ECG.

### Operations and Staffing

| Shift | Visits | Median Wait | Seen Within Target |
|---|---|---|---|
| Day (7am to 7pm) | 285 | **102 min** | 33.0% |
| Night (7pm to 7am) | 315 | **127 min** | 27.9% |

- **The night shift had more visits and waited 25 minutes longer** than the day shift. That points to night staffing as the first place to look.
- **The busiest arrival hours were 7am (36 visits), 9am (32), and 5am (30)**, so extra triage nurses in the early morning would cut waits the most in this data.

### Clinical Plausibility Check

| Check | Result |
|---|---|
| Median wait, Critical vs. Low | **100 vs. 126 minutes** |
| Wait range for every triage level | About 5 to 239 minutes |
| Busiest vs. quietest arrival hour | 7am vs. 11am |
| Chest pain visits for children under 5 | 5 |

- In a real ER, wait times fall sharply as triage level rises. Here they barely change, which suggests the wait times were generated at random.
- These findings are why the dashboard includes a Data Quality tab and editable targets, so the same tool could be used to check a real ER's data.

*Note: This dataset appears to be synthetic. The findings demonstrate dashboard and quality-review methods, not real ER performance.*

## 🚀 Learning Outcomes

Building this project strengthened my skills in:

📌 Building an interactive, multi-tab dashboard with Streamlit and Plotly<br>
📌 Designing one tool for two audiences: clinicians and hospital administrators<br>
📌 Measuring performance against clinical targets instead of averages alone<br>
📌 Turning arrival data into staffing insights with heatmaps and shift comparisons<br>
📌 Building editable settings so users can apply their own standards<br>
📌 Checking a dataset for clinical plausibility before trusting the results<br>
📌 Deploying a Python app to the web with GitHub and Streamlit Community Cloud

## 🔮 Next Steps

- Add door-to-provider, length-of-stay, and left-without-being-seen data for a fuller picture of ER flow.
- Forecast hourly arrivals to recommend staffing levels for each shift.
- Add the five-level Emergency Severity Index (ESI) used in most US emergency departments.
- Apply the dashboard to a larger, real-world ER dataset.

## 🙌 Acknowledgment

This project taught me that a dashboard is only as useful as the questions it answers. A chart of visits by hour is a starting point. Asking whether the sickest patients are seen first, and when the ER needs more staff, turned it into a tool both a clinician and a hospital administrator could act on.

## 👨‍💻 Author

**Omar Shazley**: Data Analyst | Python, Excel, SQL, and healthcare data analytics

💼 [LinkedIn](https://www.linkedin.com/in/omar-shazley-914a16b1/)<br>
💻 [GitHub Portfolio](https://github.com/Bromar95)<br>
📧 Email: [omarshazley@gmail.com](mailto:omarshazley@gmail.com)

✨ If you like this project, don't forget to ⭐ star the repo!
