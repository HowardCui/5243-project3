# GU5243 Project 03
### Collaborators：Haowen Cui(@HowardCui), Pengyu Chen(@Darconshal), Rui Lin(@R0R0Rui), Crystal Guo (@CrystalF042)   
---

## Project Structure

```text
5243-project3/
├── appA/
│   ├── app.py
│   ├── data/
│   │   ├── penguins.csv
│   │   ├── cars.json
│   │   └── College.rds
│   ├── requirements.txt
│   └── rsconnect-python/
│
├── appB/
│   ├── app.py
│   ├── data/
│   │   ├── penguins.csv
│   │   ├── cars.json
│   │   └── College.rds
│   ├── requirements.txt
│   └── rsconnect-python/
│
├── redirect/
│   ├── app.py
│   ├── requirements.txt
│   └── rsconnect-python/
│
├── results/
│   ├── data.csv
│   ├── versionA.png
│   └── versionB.png
│
├── Parameters.md
├── Project_3_Report_Team16.ipynb
├── Statistical Analysis.ipynb
└── README.md

The `results/` folder stores analysis outputs and report assets, including the exported funnel dataset and interface screenshots used in the report.
                  
## How to Use

### Getting Started

The app randomly assigns you to **Version A** or **Version B** upon first visit via the redirect entry point. Both versions support the same core workflow: upload or select a dataset, explore it visually, and generate charts.

---

### Step 1 — Load Your Data

**Version A**
1. Navigate to the **Data Upload** tab
2. Choose a data source:
   - **Sample dataset** — select from the dropdown (Penguins, Cars, College)
   - **Upload a file** — click the file input and select a `.csv` file from your machine
3. Wait for the status indicator to show a success state

**Version B**
1. Check the **User Guide** tab for a quick walkthrough (optional)
2. Navigate to the **Data Upload** tab
3. Select a sample dataset from the dropdown **or** upload a `.csv` file
4. Wait for the status indicator to confirm the data loaded successfully

> If loading fails, check that your file is a valid `.csv` with a header row and try again.

---

### Step 2 — Review the Data Summary

Once data is loaded, a summary table will appear automatically showing column types, basic statistics, and a preview of the dataset. Review this before proceeding to make sure the right data was loaded.

---

### Step 3 — Generate a Visualization

1. Navigate to the **Exploratory Data Analysis** (EDA) tab
2. Select a **plot type**:

   | Plot Type | Description | Available In |
   |---|---|---|
   | Scatter | X vs Y relationship | A, B |
   | Histogram | Distribution of one variable | A, B |
   | Box | Distribution by group | A, B |
   | Bar | Category counts or means | A, B |

3. Select the variable(s) for the axes
4. Click **Generate Plot**

> A plot will only render if the selected variables contain valid, non-empty data after removing missing values.

---

### Sample Datasets

| Dataset | Description |
|---|---|
| `penguins.csv` | Palmer Penguins — species, island, bill/flipper measurements |
| `cars.json` | Car attributes and performance metrics |
| `College.rds` | US College statistics (from ISLR) |

---

### Notes

- Your session is tracked anonymously for A/B testing purposes. No personally identifiable information is collected.
- Refreshing the page starts a new session. Progress is not saved between sessions.
- If you are redirected unexpectedly, return to the main entry URL to be re-assigned.
