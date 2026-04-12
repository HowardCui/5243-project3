# GA4 Event Parameters — Data Studio A/B Test

## Shared Parameters (Included in Every Event)

All custom events automatically include the following three parameters:

| Parameter | Example Value | Description |
|---|---|---|
| `ab_group` | `"A"` / `"B"` | Identifies the experiment group. Fixed as `"A"` for Version A and `"B"` for Version B. |
| `user_id_custom` | `"u_k3x9mw2pq"` | Unique user identifier randomly generated on page load. Stored in `sessionStorage` — persists within the same browser session and resets when the browser is closed. |
| `entry_time` | `1712789423000` | Unix timestamp (milliseconds) recorded when the user first opens the page. Used to calculate time elapsed at each step. |

---

## Event Reference

### 1. `ab_session_start`

- **Trigger**: Fires once immediately after the page finishes loading
- **Additional Parameters**: None
- **Corresponding Metric**: Entry time
- **Applies to**: Version A, Version B
- **Notes**: Marks the beginning of one experiment session. Combined with `entry_time`, allows reconstruction of when each user entered the app.

---

### 2. `ab_source_selected`

- **Trigger**: Fires when the user selects a data source
  - Version A: when the radio button (`data_source`) changes
  - Version B: when the user changes the sample dropdown or interacts with the file input
- **Additional Parameters**:

| Parameter | Possible Values | Description |
|---|---|---|
| `source_type` | `"sample"` / `"upload"` | The data source type selected by the user |

- **Applies to**: Version A, Version B

---

### 3. `ab_upload_clicked`

- **Trigger**: Fires when the user expresses upload intent
  - Version A (upload path): when the file input element changes
  - Version A (sample path): when the user selects a dataset from the sample dropdown
  - Version B (upload path): when the file input element changes
  - Version B (sample path): when the user selects a dataset from the sample dropdown
- **Additional Parameters**:

| Parameter | Possible Values | Description |
|---|---|---|
| `source_type` | `"sample"` / `"upload"` | Whether the user is uploading a file or loading a sample |

- **Corresponding Metric**: Upload clicked
- **Applies to**: Version A, Version B
- **Notes**: Fires even if the user does not complete the upload. Used as the denominator when calculating upload intent-to-completion conversion rate.

---

### 4. `ab_upload_success`

- **Trigger**: Fires when a dataset or file is successfully loaded and the status UI re-renders with `"success"` state
- **Additional Parameters**:

| Parameter | Possible Values | Description |
|---|---|---|
| `source_type` | `"sample"` / `"upload"` | The data source type that was successfully loaded |
| `dataset_name` | `"penguins"` / `"mydata.csv"` etc. | The name of the sample dataset or the uploaded filename |

- **Corresponding Metric**: Upload success rate
- **Applies to**: Version A, Version B
- **Notes**: Upload success rate = users who triggered `ab_upload_success` / users who triggered `ab_upload_clicked`

---

### 5. `ab_upload_error`

- **Trigger**: Fires when data loading fails and the status UI re-renders with `"error"` state
- **Additional Parameters**: None
- **Applies to**: Version A, Version B
- **Notes**: Combined with `ab_upload_clicked`, can be used to calculate failure rate.

---

### 6. `ab_summary_viewed`

- **Trigger**: Fires when the Summary section renders with a non-empty dataframe after data is successfully loaded
- **Additional Parameters**: None
- **Corresponding Metric**: Summary viewed
- **Applies to**: Version A, Version B
- **Notes**: A mid-funnel checkpoint between "upload success" and "visualization created." Measures whether users reviewed the data overview before proceeding to plot.

---

### 7. `ab_visualization_created`

- **Trigger**: Fires when a chart is successfully validated and rendered on the EDA page (after clicking "Generate plot")
- **Additional Parameters**:

| Parameter | Possible Values | Description |
|---|---|---|
| `plot_type` | `"scatter"` / `"hist"` / `"box"` / `"bar"` / `"corr"` | The type of chart generated (`"corr"` = Correlation Heatmap, available in Version B only) |
| `x_var` | e.g. `"bill_length_mm"` | The variable selected for the X axis |

- **Corresponding Metric**: Visualization generation rate
- **Applies to**: Version A, Version B
- **Notes**: Visualization generation rate = users who triggered `ab_visualization_created` / total users. Only fires if the chart data passes validation (non-empty after dropna).

---

### 8. `ab_task_completed`

- **Trigger**: Fires once per session, immediately after `ab_visualization_created`, when a chart is successfully generated for the first time
- **Additional Parameters**:

| Parameter | Example Value | Description |
|---|---|---|
| `time_to_completion_sec` | `"47"` | Seconds from page entry to first successful chart generation. Calculated in the browser as `Math.round((Date.now() - AB_ENTRY_TIME) / 1000)`. |

- **Corresponding Metrics**: Task completion rate, Time to completion
- **Applies to**: Version A, Version B
- **Notes**: Fires only once per session (guarded by `sessionStorage` key `ab_completed`). Task completion rate = users who triggered `ab_task_completed` / total users who triggered `ab_session_start`.

---

### 9. `ab_tab_click`

- **Trigger**: Fires when the user clicks any top-level navigation tab
- **Additional Parameters**:

| Parameter | Possible Values (Version A) | Possible Values (Version B) |
|---|---|---|
| `tab_name` | `"Data Upload"` / `"Exploratory Data Analysis"` | `"User Guide"` / `"Data Upload"` / `"EDA"` / `"Export"` |

- **Applies to**: Version A, Version B
- **Notes**: Version A uses `navset_tab` (horizontal tabs); Version B uses `navset_bar` (top navbar). The JS selector covers both: `.nav-tabs .nav-link` for A and `.navbar-nav .nav-link` for B.

---

## User Behavior Funnel

```
ab_session_start
       ↓
ab_source_selected
       ↓
ab_upload_clicked
       ↓
ab_upload_success / ab_upload_error
       ↓
ab_summary_viewed
       ↓
ab_visualization_created  ──→  ab_task_completed (fires once, same trigger)
```

---

## Key Metric Formulas

| Metric | Formula |
|---|---|
| Task completion rate | `ab_task_completed` users / `ab_session_start` users |
| Upload success rate | `ab_upload_success` users / `ab_upload_clicked` users |
| Visualization generation rate | `ab_visualization_created` users / `ab_session_start` users |
| Summary view rate | `ab_summary_viewed` users / `ab_upload_success` users |
| Upload error rate | `ab_upload_error` users / `ab_upload_clicked` users |
| Avg. time to completion | Mean of `time_to_completion_sec` across `ab_task_completed` events |

