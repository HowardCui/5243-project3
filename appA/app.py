#!/usr/bin/env python 3.12
# -*- coding: utf-8 -*-
# time: 2026/04/10
# GA4 integration: A/B test tracking for Data Studio (Version A)

# Task: Please upload a dataset and create one visualization using the app.
# To avoid confounding effects unrelated to the experimental task,
# we removed the unrelated panel from both Version A and Version B.

import sys
from pathlib import Path
import os
import uuid
import numpy as np
import pandas as pd
import pyreadr
from shiny.express import input, render, ui
from shiny import reactive
import matplotlib.pyplot as plt

app_dir = Path(__file__).resolve().parent
app_dir = app_dir / "data"

current_df = reactive.value(pd.DataFrame())
data_source_info = reactive.value({
    "source_type": None,
    "source_name": None,
    "status": "idle",
    "message": "No data loaded yet."
})

fe_status = reactive.value({"status": "idle", "message": ""})
dropdown_choices = reactive.value({"numeric": [], "all": []})
engineered_columns = reactive.value([])

#Key
GA4_MEASUREMENT_ID = "G-CJCEK0X1HM"
AB_GROUP = "A"

ui.tags.head(
    ui.tags.script(
        src=f"https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}",
        async_=True
    ),
    ui.tags.script(f"""
        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', '{GA4_MEASUREMENT_ID}', {{
            'send_page_view': true
        }});

        // ── A/B group & session setup ──────────────────────────────────────
        // Persist user_id in sessionStorage so it survives tab refreshes
        // but resets on a new browser session (fits the experiment design).
        if (!sessionStorage.getItem('ab_user_id')) {{
            sessionStorage.setItem('ab_user_id', 'u_' + Math.random().toString(36).substr(2, 9));
            sessionStorage.setItem('ab_entry_time', Date.now());
        }}
        var AB_USER_ID   = sessionStorage.getItem('ab_user_id');
        var AB_ENTRY_TIME = parseInt(sessionStorage.getItem('ab_entry_time'));

        // ── Helper: send a GA4 custom event with shared AB dimensions ──────
        function sendABEvent(event_name, extra_params) {{
            gtag('event', event_name, Object.assign({{
                ab_group:      '{AB_GROUP}',
                user_id_custom: AB_USER_ID,
                entry_time:    AB_ENTRY_TIME
            }}, extra_params || {{}}));
        }}

        // ── Log session start ──────────────────────────────────────────────
        sendABEvent('ab_session_start');
    """)
)


def ga_event_script(event_name, extra=None) -> ui.Tag:
    """Return a <script> tag that fires one GA4 custom event."""
    params_js = ", ".join(f'"{k}": "{v}"' for k, v in (extra or {}).items())
    return ui.tags.script(f"sendABEvent('{event_name}', {{{params_js}}});")

#
# UI Styles
#
ui.tags.style("""
:root{
  --cds-blue: #B9D9EB;
  --cds-blue-soft: #EEF7FC;
  --cds-blue-deep: #89BDD8;
  --cds-text: #0F172A;
  --cds-muted: #475569;
  --cds-border: #D8E6EF;
  --cds-success-bg: #EAF7EE;
  --cds-success-text: #1E7A39;
  --cds-error-bg: #FDECEC;
  --cds-error-text: #B42318;
}

body {
  background: #F8FBFD;
  color: var(--cds-text);
  font-size: 16px;
}

.container-fluid, .container-xxl {
  max-width: 100% !important;
}

.product-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 10px 22px 10px;
  margin-bottom: 18px;
  border-bottom: 2px solid #E5EDF3;
}

.product-title {
  font-size: 48px;
  font-weight: 900;
  color: #000000;
  line-height: 1.05;
  letter-spacing: 0.2px;
}

.function-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.function-item {
  font-size: 24px;
  font-weight: 700;
  color: #334155;
  padding: 8px 14px;
}

.function-divider {
  width: 1px;
  height: 28px;
  background: #B8C2CC;
}

.nav-tabs .nav-link {
  font-size: 20px !important;
  font-weight: 600 !important;
  padding: 10px 16px !important;
}

.card, .upload-card, .status-card, .content-card {
  border: 1.5px solid var(--cds-border) !important;
  border-radius: 22px !important;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  padding: 12px;
}

.upload-title {
  font-size: 28px;
  font-weight: 400;
  color: #16324F;
  margin-bottom: 6px;
}

.upload-subtitle {
  font-size: 22px;
  color: var(--cds-muted);
  margin-bottom: 14px;
  line-height: 1.5;
}

.section-label {
  font-size: 22px;
  font-weight: 600;
  color: #1D4E89;
  margin-bottom: 10px;
}

.decor-block {
  background: linear-gradient(90deg, var(--cds-blue-soft), #ffffff);
  border-left: 7px solid var(--cds-blue-deep);
  padding: 12px 16px;
  border-radius: 16px;
  margin-bottom: 14px;
}

.status-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1F2937;
}

.status-box {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.status-idle {
  background: #F1F5F9;
  color: #5B6470;
}

.status-success {
  background: var(--cds-success-bg);
  color: var(--cds-success-text);
}

.status-error {
  background: var(--cds-error-bg);
  color: var(--cds-error-text);
}

.form-label, .control-label {
  font-size: 24px !important;
  font-weight: 800 !important;
  color: #0F3D5E !important;
}

.shiny-input-container {
  margin-bottom: 18px !important;
}

.form-select, .form-control {
  font-size: 16px !important;
  min-height: 56px !important;
  border-radius: 14px !important;
}

.form-check-label {
  font-size: 22px !important;
  font-weight: 600 !important;
}

.form-check-input {
  transform: scale(1.35);
  margin-top: 0.35em;
}

.btn, .btn-default {
  font-size: 20px !important;
  border-radius: 14px !important;
  padding: 10px 18px !important;
}

.table {
  font-size: 20px !important;
}

.table th {
  font-size: 21px !important;
  font-weight: 800 !important;
}

.table td {
  font-size: 19px !important;
}

.bslib-gap-spacing {
  gap: 28px !important;
}
              .summary-table {
  width: 340px;
  border-collapse: collapse;
  font-size: 19px;
}
.summary-table th {
  font-size: 21px !important;
  font-weight: 800 !important;
  text-align: left !important;
  padding: 6px 16px 6px 4px;
  border-bottom: 2px solid #CBD5E1;
}
.summary-table td {
  text-align: left !important;
  padding: 5px 16px 5px 4px;
  border-bottom: 1px solid #E2EAF0;
}
""")

with ui.div(class_="product-bar"):
    ui.div("Data Studio", class_="product-title")


#
# functions
#
def load_sample_dataset(name: str) -> pd.DataFrame:
    if name == "penguins":
        return pd.read_csv(app_dir / "penguins.csv")
    elif name == "cars":
        return pd.read_json(app_dir / "cars.json")
    elif name == "College":
        result = pyreadr.read_r(app_dir / "College.rds")
        first_key = list(result.keys())[0]
        obj = result[first_key]
        return obj if isinstance(obj, pd.DataFrame) else pd.DataFrame(obj)
    else:
        raise ValueError(f"Unknown sample dataset: {name}")


def read_uploaded_file(fileinfo) -> pd.DataFrame:
    path = fileinfo["datapath"]
    name = fileinfo["name"]
    ext = os.path.splitext(name)[1].lower()

    if ext == ".csv":
        return pd.read_csv(path)
    elif ext == ".xlsx":
        return pd.read_excel(path, engine="openpyxl")
    elif ext == ".json":
        return pd.read_json(path)
    elif ext == ".rds":
        result = pyreadr.read_r(path)
        first_key = list(result.keys())[0]
        obj = result[first_key]
        return obj if isinstance(obj, pd.DataFrame) else pd.DataFrame(obj)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


#
# UI
#

# GA4: Track tab clicks — registered at top level to catch all tabs
ui.tags.script("""
    document.addEventListener('DOMContentLoaded', function() {
        var tabs = document.querySelectorAll('.nav-tabs .nav-link');
        tabs.forEach(function(tab) {
            tab.addEventListener('click', function() {
                sendABEvent('ab_tab_click', { tab_name: this.textContent.trim() });
            });
        });
    });
""")

with ui.navset_tab():

    # Tab 1: Data Upload
    with ui.nav_panel("Data"):

        with ui.layout_columns(col_widths=(5, 7)):
            with ui.card(class_="upload-card"):
                ui.div("Data", class_="upload-title")
                

                with ui.div(class_="decor-block"):
                    ui.div("Choose source", class_="section-label")

                    # GA4: Track radio button change via JS
                    ui.tags.script("""
                        document.addEventListener('change', function(e) {
                            if (e.target && e.target.name === 'data_source') {
                                sendABEvent('ab_source_selected', {
                                    source_type: e.target.value
                                });
                            }
                        });
                    """)

                    ui.input_radio_buttons(
                        "data_source",
                        None,
                        choices={
                            "sample": "Sample dataset",
                            "upload": "Upload file"
                        },
                        selected=None
                    )

                with ui.panel_conditional("input.data_source == 'sample'"):
                    with ui.div(class_="decor-block"):
                        ui.div("Sample dataset", class_="section-label")
                        # GA4: track upload_clicked when user selects a sample dataset
                        ui.tags.script("""
                            document.addEventListener('change', function(e) {
                                if (e.target && e.target.id === 'sample_dataset' && e.target.value !== '') {
                                    sendABEvent('ab_upload_clicked', { source_type: 'sample' });
                                }
                            });
                        """)
                        ui.input_select(
                            "sample_dataset",
                            None,
                            choices={
                                "": "Please select a dataset",
                                "penguins": "Penguins (.csv)",
                                "cars": "cars (.json)",
                                "College": "College (.rds)"
                            },
                            selected=""
                        )

                with ui.panel_conditional("input.data_source == 'upload'"):
                    with ui.div(class_="decor-block"):
                        ui.div("Upload file", class_="section-label")
                        ui.input_file(
                            "file_upload",
                            None,
                            accept=[".csv", ".xlsx", ".json", ".rds"],
                            multiple=False
                        )

                        ui.tags.script("""
                            document.addEventListener('change', function(e) {
                                if (e.target && e.target.id === 'file_upload') {
                                    sendABEvent('ab_upload_clicked', { source_type: 'upload' });
                                }
                            });
                        """)

            with ui.div():
                with ui.card(class_="status-card"):
                    ui.div("Status", class_="status-title")

                    @render.ui
                    def status_ui():
                        info = data_source_info.get()
                        status = info["status"]
                        msg = info["message"]

                        if status == "success":
                            cls = "status-box status-success"
                        elif status == "error":
                            cls = "status-box status-error"
                        else:
                            cls = "status-box status-idle"

                        # GA4: emit upload_success / upload_error
                        # Attach a script tag alongside the status div so the
                        # event fires every time status changes to success/error.
                        ga_script = ui.div()   # default: no event
                        if status == "success":
                            source = info.get("source_type", "unknown")
                            name = info.get("source_name", "unknown")
                            ga_script = ga_event_script(
                                "ab_upload_success",
                                {"source_type": source, "dataset_name": name}
                            )
                        elif status == "error":
                            ga_script = ga_event_script("ab_upload_error")

                        return ui.div(
                            ui.div(msg, class_=cls),
                            ga_script
                        )

                ui.div(style="height: 4px;")

                with ui.card(class_="content-card"):
                    with ui.navset_tab():
                        with ui.nav_panel("Summary"):
                            @render.table
                            def summary_table():
                                df = current_df.get()
                                if df.empty:
                                    return pd.DataFrame({"Message": ["No data loaded"]})
                                return pd.DataFrame({
                                    "Metric": ["Rows", "Columns"],
                                    "Value": [df.shape[0], df.shape[1]]
                                })

                            # GA4: Track "summary_viewed" — fires once per session
                            @render.ui
                            def summary_viewed_tracker():
                                df = current_df.get()
                                if df.empty:
                                    return ui.div()
                                return ui.tags.script("""
                                    if (!sessionStorage.getItem('ab_summary_viewed')) {
                                        sessionStorage.setItem('ab_summary_viewed', '1');
                                        sendABEvent('ab_summary_viewed');
                                    }
                                """)

                        with ui.nav_panel("Preview"):
                            @render.data_frame
                            def preview_table():
                                df = current_df.get()
                                if df.empty:
                                    return render.DataGrid(
                                        pd.DataFrame({"Message": ["No data loaded"]}),
                                        width="100%"
                                    )
                                return render.DataGrid(df.head(10), width="100%")

                        with ui.nav_panel("Columns"):
                            @render.table
                            def column_info():
                                df = current_df.get()
                                if df.empty:
                                    return pd.DataFrame({"Message": ["No data loaded"]})
                                return pd.DataFrame({
                                    "Column": df.columns,
                                    "Type": [str(dtype) for dtype in df.dtypes]
                                })

                        with ui.nav_panel("Structure"):
                            @render.table
                            def structure_table():
                                df = current_df.get()
                                if df.empty:
                                    return pd.DataFrame({"Message": ["No data loaded"]})
                                return pd.DataFrame({
                                    "Column": df.columns,
                                    "Missing": [int(df[col].isna().sum()) for col in df.columns],
                                    "Unique": [int(df[col].nunique(dropna=True)) for col in df.columns]
                                })

    # Tab 2: EDA
    with ui.nav_panel("EDA"):

        # Block 1: Dataset Summary
        with ui.card(class_="content-card"):
            ui.div("Dataset Summary", class_="status-title")

            @render.ui
            def dataset_summary_table():
                df = current_df.get()

                if df.empty:
                    return ui.div("No data loaded", class_="status-box status-idle")

                n_rows, n_cols = df.shape
                missing_cells = int(df.isna().sum().sum())
                duplicate_rows = int(df.duplicated().sum())
                numeric_cols = int(df.select_dtypes(include="number").shape[1])
                categorical_cols = int(df.select_dtypes(exclude="number").shape[1])

                rows_data = [
                    ("Rows", n_rows),
                    ("Columns", n_cols),
                    ("Missing Cells", missing_cells),
                    ("Duplicate Rows", duplicate_rows),
                    ("Numeric Columns", numeric_cols),
                    ("Categorical Columns", categorical_cols),
                ]

                table_rows = "".join(
                    f"<tr><td>{metric}</td><td>{value}</td></tr>"
                    for metric, value in rows_data
                )

                html = f"""
                <table class="summary-table">
                  <thead>
                    <tr><th>Metric</th><th>Value</th></tr>
                  </thead>
                  <tbody>
                    {table_rows}
                  </tbody>
                </table>
                """
                return ui.HTML(html)

        ui.br()

        # Block 1a: Feature Engineering
        with ui.card(class_="content-card"):
            ui.div("Feature Engineering", class_="status-title")

            with ui.layout_columns(col_widths=(4, 4, 4)):
                ui.input_select("fe_column", "Select column", choices={})
                ui.input_select(
                    "fe_transformation",
                    "Transformation",
                    choices={
                        "log": "Log Transform",
                        "square": "Square",
                        "bin": "Binning",
                        "standardize": "Standardize (Z-score)",
                        "scale": "Scale (Min-Max)"}
                )
                ui.input_slider(
                    "fe_bins",
                    "Bins for binning",
                    min=2, max=10, value=3
                )
            ui.input_action_button("apply_fe", "Apply")

            @render.ui
            def fe_status_ui():
                info = fe_status.get()
                if info["status"] == "idle" or not info["message"]:
                    return ui.div()
                cls = "status-box status-success" if info["status"] == "success" else "status-box status-error"
                return ui.div(info["message"], class_=cls, style="margin-top: 10px;")

            @render.ui
            def engineered_columns_ui():
                cols = engineered_columns.get()
                if not cols:
                    return ui.div()

                rows = "".join(
                    f"<tr><td>{c['name']}</td><td>{c['derived_from']}</td><td>{c['transformation']}</td></tr>"
                    for c in cols
                )
                html = f"""
                <div style="margin-top:16px;">
                  <div class="section-label">Engineered Variables</div>
                  <table class="table table-sm table-bordered" style="margin-top:8px;">
                    <thead><tr><th>New Column</th><th>Derived From</th><th>Transformation</th></tr></thead>
                    <tbody>{rows}</tbody>
                  </table>
                </div>
                """
                return ui.HTML(html)

        # Block 2: Plot Controls
        with ui.card(class_="content-card"):
            ui.div("Visualization Controls", class_="status-title")

            with ui.layout_columns(col_widths=(4, 4, 4)):
                ui.input_select(
                    "plot_type",
                    "Choose plot type",
                    choices={
                        "scatter": "Scatter Plot",
                        "hist": "Histogram",
                        "box": "Box Plot",
                        "bar": "Bar Chart"
                    },
                    selected="scatter"
                )

                @render.ui
                def x_var_ui():
                    choices=dropdown_choices.get()
                    plot_type=input.plot_type()
                    cols=choices["all"] if plot_type=="bar" else choices["numeric"]
                    if not cols:
                        return ui.input_select("x_var", "X variable", choices={"": "No data loaded"}, selected="")
                    try:
                        current_x=input.x_var()
                        selected_x=current_x if current_x in cols else cols[0]
                    except:
                        selected_x=cols[0]
                    return ui.input_select("x_var", "X variable", choices={c: c for c in cols}, selected=selected_x)


                @render.ui
                def y_var_ui():
                    choices=dropdown_choices.get()
                    cols=choices["numeric"]
                    if not cols:
                        return ui.input_select("y_var", "Y variable", choices={"": "No data loaded"}, selected="")
                    try:
                        current_y=input.y_var()
                        selected_y=current_y if current_y in cols else cols[0]
                    except:
                        selected_y=cols[0]
                    return ui.input_select("y_var", "Y variable", choices={c: c for c in cols}, selected=selected_y)

            ui.input_action_button("generate_plot", "Generate plot")

        ui.br()

        # Block 3: Plot Output
        with ui.card(class_="content-card"):
            ui.div("Plot Output", class_="status-title")


            @render.plot
            @reactive.event(lambda: input.generate_plot())
            def eda_plot():
                df=current_df.get()
                fig, ax=plt.subplots(figsize=(8, 5))

                if df.empty:
                    ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
                    ax.axis("off")
                    return fig

                plot_type=input.plot_type()
                x_var=input.x_var()

                try:
                    if plot_type=="scatter":
                        y_var=input.y_var()
                        if x_var not in df.columns or y_var not in df.columns:
                            ax.text(0.5, 0.5, "Please select valid X and Y variables.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        plot_df=df[[x_var, y_var]].dropna()
                        if plot_df.empty:
                            ax.text(0.5, 0.5, "No valid data to plot.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        ax.scatter(plot_df[x_var], plot_df[y_var])
                        ax.set_xlabel(x_var)
                        ax.set_ylabel(y_var)
                        ax.set_title(f"{y_var} vs {x_var}")

                    elif plot_type=="hist":
                        if x_var not in df.columns:
                            ax.text(0.5, 0.5, "Please select a valid variable.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        series=df[x_var].dropna()
                        if series.empty:
                            ax.text(0.5, 0.5, "No valid data to plot.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        ax.hist(series, bins=20)
                        ax.set_xlabel(x_var)
                        ax.set_title(f"Histogram of {x_var}")

                    elif plot_type=="box":
                        if x_var not in df.columns:
                            ax.text(0.5, 0.5, "Please select a valid variable.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        series=df[x_var].dropna()
                        if series.empty:
                            ax.text(0.5, 0.5, "No valid data to plot.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        ax.boxplot(series)
                        ax.set_title(f"Box Plot of {x_var}")
                        ax.set_xticklabels([x_var])

                    elif plot_type=="bar":
                        if x_var not in df.columns:
                            ax.text(0.5, 0.5, "Please select a valid variable.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        counts=df[x_var].astype(str).value_counts(dropna=False).head(10)
                        if counts.empty:
                            ax.text(0.5, 0.5, "No valid data to plot.", ha="center", va="center")
                            ax.axis("off")
                            return fig
                        ax.bar(counts.index, counts.values)
                        ax.set_title(f"Bar Chart of {x_var}")
                        ax.tick_params(axis="x", rotation=45)

                except Exception as e:
                    ax.clear()
                    ax.text(0.5, 0.5, f"Plot error: {e}", ha="center", va="center")
                    ax.axis("off")

                return fig


            @render.ui
            @reactive.event(lambda: input.generate_plot())
            def viz_and_completion_tracker():
                df=current_df.get()
                if df.empty:
                    return ui.div()

                try:
                    plot_type=input.plot_type()
                    x_var=input.x_var()
                except:
                    return ui.div()

                ok=False

                try:
                    if plot_type=="scatter":
                        y_var=input.y_var()
                        if x_var in df.columns and y_var in df.columns:
                            plot_df=df[[x_var, y_var]].dropna()
                            ok=not plot_df.empty

                    elif plot_type in ["hist", "box"]:
                        if x_var in df.columns:
                            series=df[x_var].dropna()
                            ok=not series.empty

                    elif plot_type=="bar":
                        if x_var in df.columns:
                            counts=df[x_var].astype(str).value_counts(dropna=False).head(10)
                            ok=not counts.empty

                except:
                    ok=False

                if not ok:
                    return ui.div()

                return ui.div(
                    ga_event_script(
                        "ab_visualization_created",
                        {"plot_type": plot_type, "x_var": x_var}
                    ),
                    ui.tags.script("""
                        (function() {
                            if (!sessionStorage.getItem('ab_completed')) {
                                sessionStorage.setItem('ab_completed', '1');
                                var elapsed = Math.round((Date.now() - AB_ENTRY_TIME) / 1000);
                                sendABEvent('ab_task_completed', {
                                    time_to_completion_sec: elapsed
                                });
                            }
                        })();
                    """)
                )

        ui.br()

        # Block 4: Correlation Controls
        with ui.card(class_="content-card"):
            ui.div("Correlation Analysis", class_="status-title")

            @render.ui
            def corr_vars_ui():
                df = current_df.get()
                if df.empty:
                    return ui.div("No data loaded")
                numeric_cols = df.select_dtypes(include="number").columns.tolist()
                if len(numeric_cols) < 2:
                    return ui.div("Need at least 2 numeric columns for correlation analysis")
                return ui.input_selectize(
                    "corr_vars",
                    "Select numeric variables",
                    choices=numeric_cols,
                    selected=numeric_cols[:4],
                    multiple=True
                )

        ui.br()

        # Block 5: Correlation Output
        with ui.card(class_="content-card"):
            ui.div("Correlation Heatmap", class_="status-title")

            @render.plot
            def correlation_heatmap():
                df = current_df.get()
                fig, ax = plt.subplots(figsize=(8, 6))

                if df.empty:
                    ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
                    ax.axis("off")
                    return fig

                numeric_df = df.select_dtypes(include="number")
                if numeric_df.empty:
                    ax.text(0.5, 0.5, "No numeric columns available", ha="center", va="center")
                    ax.axis("off")
                    return fig

                selected_vars = input.corr_vars()
                if not selected_vars or len(selected_vars) < 2:
                    ax.text(0.5, 0.5, "Please select at least 2 numeric variables.", ha="center", va="center")
                    ax.axis("off")
                    return fig

                corr_df = numeric_df[list(selected_vars)].dropna()
                if corr_df.empty:
                    ax.text(0.5, 0.5, "No valid data for correlation.", ha="center", va="center")
                    ax.axis("off")
                    return fig

                corr_matrix = corr_df.corr()
                im = ax.imshow(corr_matrix, aspect="auto")
                ax.set_xticks(range(len(corr_matrix.columns)))
                ax.set_yticks(range(len(corr_matrix.columns)))
                ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right")
                ax.set_yticklabels(corr_matrix.columns)
                ax.set_title("Correlation Heatmap")

                for i in range(len(corr_matrix)):
                    for j in range(len(corr_matrix)):
                        ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha="center", va="center")

                fig.colorbar(im, ax=ax)
                return fig

        ui.br()


#
# Reactive effects
#
@reactive.effect
@reactive.event(lambda: input.data_source(),lambda: input.sample_dataset())
def _load_sample():
    if input.data_source() != "sample":
        return
    selected_dataset = input.sample_dataset()
    if not selected_dataset:
        current_df.set(pd.DataFrame())
        data_source_info.set({
            "source_type": "sample",
            "source_name": None,
            "status": "idle",
            "message": "Please select a sample dataset."
        })
        return
    try:
        df = load_sample_dataset(selected_dataset)
        current_df.set(df)
        fe_status.set({"status": "idle", "message": ""})
        engineered_columns.set([])
        data_source_info.set({
            "source_type": "sample",
            "source_name": selected_dataset,
            "status": "success",
            "message": f"Loaded successfully | {selected_dataset} | {df.shape[0]} rows × {df.shape[1]} columns"
        })
    except Exception as e:
        current_df.set(pd.DataFrame())
        data_source_info.set({
            "source_type": "sample",
            "source_name": selected_dataset,
            "status": "error",
            "message": f"Failed to load sample dataset: {e}"
        })


@reactive.effect
@reactive.event(lambda: input.file_upload(),lambda: input.data_source())
def _load_upload():
    if input.data_source() != "upload":
        return
    files = input.file_upload()
    if not files:
        current_df.set(pd.DataFrame())
        data_source_info.set({
            "source_type": "upload",
            "source_name": None,
            "status": "idle",
            "message": "Please upload a file."
        })
        return
    fileinfo = files[0]
    try:
        df = read_uploaded_file(fileinfo)
        current_df.set(df)
        fe_status.set({"status": "idle", "message": ""})
        engineered_columns.set([])
        data_source_info.set({
            "source_type": "upload",
            "source_name": fileinfo["name"],
            "status": "success",
            "message": f"Loaded successfully | {fileinfo['name']} | {df.shape[0]} rows × {df.shape[1]} columns"
        })
    except Exception as e:
        current_df.set(pd.DataFrame())
        data_source_info.set({
            "source_type": "upload",
            "source_name": fileinfo["name"],
            "status": "error",
            "message": f"Upload failed: {e}"
        })


@reactive.effect
@reactive.event(lambda: input.apply_fe())
def apply_feature_engineering():
    df = current_df.get()
    if df.empty:
        return
    col = input.fe_column()
    if col not in df.columns:
        return
    new_df = df.copy()
    try:
        transformation = input.fe_transformation()
        if transformation == "log":
            new_col = f"log_{col}"
            new_df[new_col] = np.log(new_df[col] + 1)
        elif transformation == "square":
            new_col = f"sq_{col}"
            new_df[new_col] = new_df[col] ** 2
        elif transformation == "bin":
            new_col = f"bin_{col}"
            new_df[new_col] = pd.cut(new_df[col], bins=input.fe_bins(), labels=False).astype(float)
        elif transformation == "standardize":
            new_col = f"std_{col}"
            col_std = new_df[col].std()
            if col_std == 0:
                raise ValueError("Column has zero variance: standardization not possible.")
            new_df[new_col] = (new_df[col] - new_df[col].mean()) / col_std
        elif transformation == "scale":
            new_col = f"scaled_{col}"
            col_min = new_df[col].min()
            col_max = new_df[col].max()
            if col_min == col_max:
                raise ValueError("Column is constant: min-max scaling not possible.")
            new_df[new_col] = (new_df[col] - col_min) / (col_max - col_min)

        current_df.set(new_df)
        transformation_label = {
            "log": "Log transform",
            "square": "Square",
            "bin": "Binning",
            "standardize": "Standardize (Z-score)",
            "scale": "Scale (Min-Max)"
        }.get(transformation, transformation)
        fe_status.set({
            "status": "success",
            "message": f"✓ {transformation_label} applied — new variable '{new_col}' is now available in the Visualization Controls."
        })
        existing = engineered_columns.get()
        already_exists = any(e["name"] == new_col for e in existing)
        if not already_exists:
            engineered_columns.set(existing + [{
                "name": new_col,
                "derived_from": col,
                "transformation": transformation_label
            }])
    except Exception as e:
        fe_status.set({
            "status": "error",
            "message": f"Error applying transformation: {e}. Please choose a different column or transformation."
        })
        print("Feature engineering error:", e)


@reactive.effect
def update_fe_columns():
    df = current_df.get()
    if not df.empty:
        numeric = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()
        ui.update_select("fe_column", choices={c: c for c in numeric})
        dropdown_choices.set({"numeric": numeric, "all": all_cols})