#!/usr/bin/env python 3.12
# -*- coding: utf-8 -*-
# time: 2026/04/10
# GA4 integration: A/B test tracking for Data Studio (Version B)

# Task: Please upload a dataset and create one visualization using the app.
# To avoid confounding effects unrelated to the experimental task,
# we removed the unrelated panel from both Version A and Version B.

from pathlib import Path
import os
import numpy as np
import pandas as pd
import pyreadr
import matplotlib.pyplot as plt
from shiny import reactive
from shiny import ui as ui_core
from shiny.express import input, render, ui


GA4_MEASUREMENT_ID = "G-CJCEK0X1HM"
AB_GROUP = "B"

ui.tags.head(
    ui.tags.script(
        src=f"https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}",
        async_=True
    ),
    ui.tags.script(f"""
        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', '{GA4_MEASUREMENT_ID}', {{ 'send_page_view': true }});

        if (!sessionStorage.getItem('ab_user_id')) {{
            sessionStorage.setItem('ab_user_id', 'u_' + Math.random().toString(36).substr(2, 9));
            sessionStorage.setItem('ab_entry_time', Date.now());
        }}
        var AB_USER_ID    = sessionStorage.getItem('ab_user_id');
        var AB_ENTRY_TIME = parseInt(sessionStorage.getItem('ab_entry_time'));

        function sendABEvent(event_name, extra_params) {{
            gtag('event', event_name, Object.assign({{
                ab_group:       '{AB_GROUP}',
                user_id_custom: AB_USER_ID,
                entry_time:     AB_ENTRY_TIME
            }}, extra_params || {{}}));
        }}

        sendABEvent('ab_session_start');

        // Track navbar tab clicks
        document.addEventListener('DOMContentLoaded', function() {{
            var tabs = document.querySelectorAll('.nav-tabs .nav-link, .navbar-nav .nav-link');
            tabs.forEach(function(tab) {{
                tab.addEventListener('click', function() {{
                    sendABEvent('ab_tab_click', {{ tab_name: this.textContent.trim() }});
                }});
            }});
        }});
    """)
)


def ga_event_script(event_name: str, extra: dict | None = None) -> ui.Tag:
    params_js = ", ".join(f'"{k}": "{v}"' for k, v in (extra or {}).items())
    return ui.tags.script(f"sendABEvent('{event_name}', {{{params_js}}});")

#
# UI Styles
#
ui.tags.style(
    """
    :root {
      --ts-bg-app: #e9e9e9;
      --ts-bg-panel: #ffffff;
      --ts-bg-rail: #f3f3f3;
      --ts-border: #c9c9c9;
      --ts-border-soft: #e0e0e0;
      --ts-text: #333333;
      --ts-text-muted: #6f6f6f;
      --ts-accent: #2f6ab0;
      --ts-accent-deep: #24578f;
      --ts-orange: #e8762d;
      --ts-radius: 3px;
      --ts-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --columbia-blue: #b9d9eb;
      --columbia-deep: #7fb9d6;
      --columbia-navy: #0f3d5e;
      --card-border: #d4e6f1;
      --text-main: var(--ts-text);
      --text-muted: var(--ts-text-muted);
    }

    body {
      font-family: var(--ts-font);
      -webkit-font-smoothing: antialiased;
      background: var(--ts-bg-app);
      color: var(--ts-text);
      font-size: 14px;
    }

    .navbar ~ .container-fluid {
      padding-left: 0 !important;
      max-width: 100%;
    }

    .navbar {
      background: var(--ts-bg-panel) !important;
      border: none !important;
      border-bottom: 1px solid var(--ts-border) !important;
      border-radius: 0 !important;
      margin-bottom: 0 !important;
      padding-top: 0 !important;
      padding-bottom: 0 !important;
      box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
    }

    .navbar .container-fluid {
      padding-top: 6px;
      padding-bottom: 6px;
    }

    .navbar-brand {
      color: var(--ts-text) !important;
      font-size: 18px !important;
      font-weight: 600 !important;
      letter-spacing: -0.02em;
      padding-right: 1rem !important;
      border-right: 1px solid var(--ts-border-soft);
      margin-right: 0.75rem !important;
    }

    .navbar-brand::after {
      content: "";
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 1px;
      background: var(--ts-orange);
      margin-left: 8px;
      vertical-align: middle;
      opacity: 0.9;
    }

    .nav-tabs {
      border-bottom: none !important;
      gap: 2px;
    }

    .nav-tabs .nav-link {
      font-size: 13px !important;
      font-weight: 500 !important;
      color: var(--ts-text-muted) !important;
      border: none !important;
      border-radius: var(--ts-radius) var(--ts-radius) 0 0 !important;
      padding: 0.45rem 0.65rem !important;
      margin-bottom: 0 !important;
    }

    .nav-tabs .nav-link:hover {
      color: var(--ts-text) !important;
      background: rgba(0, 0, 0, 0.03) !important;
    }

    .nav-tabs .nav-link.active {
      color: var(--ts-accent) !important;
      background: var(--ts-bg-app) !important;
      border: 1px solid var(--ts-border) !important;
      border-bottom-color: var(--ts-bg-app) !important;
      font-weight: 600 !important;
    }

    .card {
      border: 1px solid var(--ts-border-soft) !important;
      border-radius: var(--ts-radius) !important;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06) !important;
      background: var(--ts-bg-panel) !important;
      padding: 10px 12px !important;
    }

    .left-tools.card {
      background: var(--ts-bg-rail) !important;
      border-color: var(--ts-border) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
    }

    .section-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--ts-text);
      margin-bottom: 6px;
      letter-spacing: -0.01em;
    }

    .section-subtitle {
      font-size: 13px;
      color: var(--ts-text-muted);
      margin-bottom: 6px;
    }

    .group-title {
      font-size: 12px;
      font-weight: 600;
      color: var(--ts-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-top: 8px;
      margin-bottom: 4px;
    }

    .feature-block {
      background: var(--ts-bg-panel);
      border: 1px solid var(--ts-border-soft);
      border-radius: var(--ts-radius);
      padding: 8px 10px;
      margin-bottom: 8px;
    }

    hr {
      margin-top: 8px !important;
      margin-bottom: 8px !important;
    }

    .mode-switch .form-check {
      display: inline-block;
      margin-right: 10px;
      margin-bottom: 8px;
    }

    .mode-switch .form-check-input {
      display: none;
    }

    .mode-switch .form-check-label {
      border: 1px solid transparent;
      border-radius: var(--ts-radius);
      padding: 5px 10px;
      background: rgba(255, 255, 255, 0.55);
      color: var(--ts-text-muted);
      cursor: pointer;
      font-size: 12px !important;
      font-weight: 500 !important;
    }

    .mode-switch .form-check-input:checked + .form-check-label {
      background: var(--ts-bg-panel);
      border-color: var(--ts-border);
      color: var(--ts-accent);
      font-weight: 600 !important;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    .mode-content {
      min-height: 0;
      overflow: visible;
      border: none;
      border-radius: 0;
      padding: 8px 0;
      background: transparent;
    }

    .user-guide-page {
      background: var(--ts-bg-panel);
      min-height: 0;
      border: 1px solid var(--ts-border-soft);
      border-radius: var(--ts-radius);
      padding: 16px 20px;
      max-width: 52rem;
      margin: 12px 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.07);
    }

    .user-guide-page p,
    .user-guide-page li {
      line-height: 1.85;
    }

    .compact-feedback {
      padding-top: 6px !important;
      padding-bottom: 6px !important;
      min-height: 64px;
    }

    .small-card {
      padding-top: 2px !important;
      padding-bottom: 2px !important;
      min-height: 58px;
    }

    .small-card .section-title,
    .small-empty .section-title {
      margin-bottom: 2px;
      font-size: 16px;
      font-weight: 600;
    }

    .small-card .alert {
      margin-bottom: 0 !important;
      padding-top: 4px;
      padding-bottom: 4px;
      min-height: 24px;
    }

    .small-empty .alert {
      margin-bottom: 0 !important;
      padding-top: 4px;
      padding-bottom: 4px;
      min-height: 24px;
    }

    .small-empty {
      padding-top: 2px !important;
      padding-bottom: 2px !important;
      min-height: 58px;
    }

    .data-preview-card {
      min-height: 0;
    }

    .dense-grid {
      max-height: none;
      overflow: visible;
    }

    .eda-plot-card {
      min-height: 0;
    }

    .eda-plot-card img, .eda-plot-card canvas {
      max-height: 280px !important;
      width: auto !important;
    }

    .left-tools .section-title {
      font-size: 15px !important;
      font-weight: 600 !important;
      margin-bottom: 4px !important;
      color: var(--ts-text) !important;
    }

    .left-tools .group-title {
      font-size: 11px !important;
      font-weight: 600 !important;
      margin-top: 4px !important;
      margin-bottom: 2px !important;
      color: var(--ts-text-muted) !important;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .left-tools .form-label,
    .left-tools .control-label {
      font-size: 12px !important;
      font-weight: 500 !important;
      margin-bottom: 2px !important;
      color: var(--ts-text) !important;
    }

    .left-tools .form-check-label {
      font-size: 12px !important;
      font-weight: 500 !important;
    }

    .left-tools .form-select,
    .left-tools .form-control {
      font-size: 13px !important;
      min-height: 30px !important;
      padding: 4px 8px !important;
      border-radius: var(--ts-radius) !important;
      border-color: #b3b3b3 !important;
    }

    .left-tools .btn,
    .left-tools .btn-default {
      font-size: 12px !important;
      font-weight: 600 !important;
      padding: 5px 12px !important;
      border-radius: var(--ts-radius) !important;
      background: var(--ts-accent) !important;
      border: 1px solid var(--ts-accent-deep) !important;
      color: #fff !important;
    }

    .left-tools .btn:hover,
    .left-tools .btn-default:hover {
      background: var(--ts-accent-deep) !important;
      border-color: #1a4675 !important;
      color: #fff !important;
    }

    .left-tools .shiny-input-container {
      margin-bottom: 5px !important;
    }

    .left-tools .feature-block {
      padding: 5px 7px !important;
      margin-bottom: 4px !important;
    }

    .left-tools .mode-content {
      min-height: 0;
      padding: 5px;
    }

    .eda-viz-panel .section-title {
      margin-bottom: 2px !important;
    }

    .eda-viz-columns {
      margin-bottom: 4px !important;
    }

    .eda-viz-columns > [class*="col-"] {
      min-width: 0;
    }

    .eda-viz-panel .selectize-control {
      max-width: 100% !important;
    }

    .eda-viz-panel .shiny-input-container .irs {
      width: 100% !important;
      max-width: 100% !important;
    }

    .eda-viz-panel .irs {
      margin-top: 2px !important;
      margin-bottom: 2px !important;
    }

    .eda-viz-generate {
      margin-top: 2px !important;
      margin-bottom: 0 !important;
    }

    .eda-viz-generate .shiny-input-container {
      margin-bottom: 0 !important;
    }

    .eda-viz-panel .form-group,
    .eda-viz-panel .mb-3 {
      margin-bottom: 6px !important;
    }

    .eda-viz-panel.card {
      padding-bottom: 8px !important;
    }

    .left-tools .selectize-input {
      min-height: 30px !important;
      padding: 4px 8px !important;
      font-size: 13px !important;
      border-radius: var(--ts-radius) !important;
    }

    .tab-content {
      background: var(--ts-bg-app);
      border: none !important;
      padding-top: 8px !important;
    }

    .tab-pane {
      background: transparent !important;
    }

    input[type="radio"],
    input[type="checkbox"] {
      accent-color: var(--ts-accent);
    }

    .form-label, .control-label {
      font-size: 13px !important;
      font-weight: 500 !important;
      color: var(--ts-text) !important;
      margin-bottom: 4px !important;
    }

    .shiny-input-container {
      margin-bottom: 10px !important;
    }

    .btn, .btn-default {
      font-size: 13px !important;
      font-weight: 500 !important;
      border-radius: var(--ts-radius) !important;
      border: 1px solid #a8a8a8 !important;
      background: linear-gradient(180deg, #ffffff 0%, #f0f0f0 100%) !important;
      color: var(--ts-text) !important;
      box-shadow: none !important;
    }

    .btn:hover, .btn-default:hover {
      background: linear-gradient(180deg, #f5f5f5 0%, #e5e5e5 100%) !important;
      border-color: #8c8c8c !important;
      color: #000 !important;
    }

    .alert {
      border-radius: var(--ts-radius);
      font-size: 13px;
      font-weight: 500;
      border: 1px solid var(--ts-border-soft);
    }

    .alert-success {
      background: #e8f4ea;
      border-color: #a3c9a8;
      color: #1b5e20;
    }

    .alert-danger {
      background: #fce8e6;
      border-color: #e0a19c;
      color: #8b1a12;
    }

    .alert-secondary {
      background: #f0f0f0;
      border-color: #c9c9c9;
      color: #505050;
    }

    .summary-table, .history-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    .summary-table th, .history-table th {
      text-align: left;
      color: var(--ts-text);
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      border-bottom: 2px solid var(--ts-border);
      padding: 8px 10px;
      background: #fafafa;
    }

    .summary-table td, .history-table td {
      border-bottom: 1px solid var(--ts-border-soft);
      padding: 8px 10px;
    }

    .summary-table td:last-child, .summary-table th:last-child {
      width: 150px;
      text-align: right;
      font-weight: 700;
    }
    """
)

app_dir = Path(__file__).resolve().parent / "data"

current_df = reactive.value(pd.DataFrame())
original_df = reactive.value(pd.DataFrame())
operation_log = reactive.value([])

upload_status = reactive.value({"status": "idle", "message": "No data loaded yet."})
cleaning_status = reactive.value({"status": "idle", "message": ""})
fe_status = reactive.value({"status": "idle", "message": ""})
eda_status = reactive.value({"status": "idle", "message": ""})
dropdown_choices = reactive.value({"numeric": [], "all": [], "categorical": []})
engineered_columns = reactive.value([])

#
# functions
#
def add_log(action: str) -> None:
    operation_log.set(operation_log.get() + [action])


def status_box(info: dict):
    status = info.get("status", "idle")
    if status == "success":
        cls = "alert alert-success"
    elif status == "error":
        cls = "alert alert-danger"
    else:
        cls = "alert alert-secondary"
    return ui.div(info.get("message", ""), class_=cls)


def _read_rds(path: str) -> pd.DataFrame:
    result = pyreadr.read_r(path)
    if not result:
        return pd.DataFrame()
    first_key = next(iter(result.keys()))
    obj = result[first_key]
    return obj if isinstance(obj, pd.DataFrame) else pd.DataFrame(obj)


def read_uploaded_file(fileinfo: dict) -> pd.DataFrame:
    path = fileinfo["datapath"]
    name = fileinfo["name"]
    ext = os.path.splitext(name)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".xlsx":
        return pd.read_excel(path, engine="openpyxl")
    if ext == ".json":
        return pd.read_json(path)
    if ext == ".rds":
        return _read_rds(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file format: {ext}")


def load_sample_dataset(name: str) -> pd.DataFrame:
    if name == "penguins":
        return pd.read_csv(app_dir / "penguins.csv")
    if name == "cars":
        return pd.read_json(app_dir / "cars.json")
    if name == "College":
        return _read_rds(str(app_dir / "College.rds"))
    raise ValueError(f"Unknown sample dataset: {name}")


def summary_html(df: pd.DataFrame):
    if df.empty:
        return ui.div("No data loaded", class_="alert alert-secondary")
    rows_data = [
        ("Rows", int(df.shape[0])),
        ("Columns", int(df.shape[1])),
        ("Missing Cells", int(df.isna().sum().sum())),
        ("Duplicate Rows", int(df.duplicated().sum())),
        ("Numeric Columns", int(df.select_dtypes(include="number").shape[1])),
        ("Categorical Columns", int(df.select_dtypes(exclude="number").shape[1])),
    ]
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows_data)
    return ui.HTML(
        f"""
        <table class="summary-table">
          <thead><tr><th>Metric</th><th>Value</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """
    )


#
# UI
#
with ui.navset_bar(
    title="Data Studio",
    padding=[12, 16, 12, 0],
):
    # User Guide
    with ui.nav_panel("User Guide"):
        with ui.div(class_="user-guide-page"):
            ui.div("User Guide", class_="section-title")
            ui.markdown(
                """
                1. **Data Upload**: Load a sample dataset or upload your own file.
                2. **EDA**: Select a plot type and variables, then click **Generate plot** to create a visualization.
                3. **Export**: Download the processed dataset when you are done.
                """
            )

    # Data Upload
    with ui.nav_panel("Data Upload"):
        with ui.layout_columns(col_widths=(4, 8)):
            with ui.card(class_="left-tools"):
                ui.div("Data Upload", class_="section-title")
                with ui.div(class_="feature-block"):
                    ui.div("Upload Dataset", class_="group-title")
                    ui.input_file(
                        "file_upload",
                        "Choose a file",
                        accept=[".csv", ".xlsx", ".json", ".rds", ".parquet"],
                        multiple=False,
                    )
                with ui.div(class_="feature-block"):
                    ui.div("Load Sample Dataset", class_="group-title")
                    # GA4: track source_selected and upload_clicked for sample path
                    ui.tags.script("""
                        document.addEventListener('change', function(e) {
                            if (e.target && e.target.id === 'sample_dataset' && e.target.value !== '') {
                                sendABEvent('ab_source_selected', { source_type: 'sample' });
                                sendABEvent('ab_upload_clicked', { source_type: 'sample' });
                            }
                        });
                        document.addEventListener('change', function(e) {
                            if (e.target && e.target.id === 'file_upload') {
                                sendABEvent('ab_source_selected', { source_type: 'upload' });
                            }
                        });
                    """)
                    ui.input_select(
                        "sample_dataset",
                        "Sample data",
                        choices={"": "Select sample", "penguins": "Penguins", "cars": "Cars", "College": "College"},
                        selected="",
                    )
                    ui.input_action_button("load_sample_btn", "Load selected sample")

            with ui.div():
                with ui.card(class_="compact-feedback"):
                    ui.div("Current Data State", class_="section-title")

                    @render.ui
                    def upload_status_ui():
                        info = upload_status.get()
                        status = info.get("status", "idle")

                        # ── GA4: upload_success / upload_error ─────────────
                        ga_script = ui.div()
                        if status == "success":
                            ga_script = ga_event_script(
                                "ab_upload_success",
                                {"source_type": info.get("source_type", "unknown"),
                                 "dataset_name": info.get("dataset_name", "unknown")}
                            )
                        elif status == "error":
                            ga_script = ga_event_script("ab_upload_error")

                        return ui.div(status_box(info), ga_script)

                with ui.card(class_="data-preview-card"):
                    with ui.layout_columns(col_widths=(4, 8)):
                        with ui.div():
                            ui.div("Summary", class_="group-title")

                            @render.ui
                            def upload_summary_ui():
                                df = current_df.get()
                                result = summary_html(df)
                                # ── GA4: summary_viewed ────────────────────
                                if not df.empty:
                                    return ui.div(result, ga_event_script("ab_summary_viewed"))
                                return result

                        with ui.div(class_="dense-grid"):
                            ui.div("Preview", class_="group-title")

                            @render.data_frame
                            def upload_preview():
                                df = current_df.get()
                                if df.empty:
                                    return render.DataGrid(pd.DataFrame({"Message": ["No data loaded"]}), width="100%", height="220px")
                                return render.DataGrid(df.head(15), width="100%", height="220px")

    with ui.nav_panel("EDA"):
        with ui.layout_columns(col_widths=(4, 8)):
            with ui.card(class_="left-tools eda-viz-panel"):
                ui.div("Visualization", class_="section-title")
                ui_core.row(
                    ui_core.column(
                        6,
                        ui.div("Plot", class_="group-title"),
                        ui.input_select(
                            "plot_type",
                            "Plot Type",
                            {
                                "hist": "Histogram",
                                "box": "Box Plot",
                                "bar": "Bar Chart",
                                "scatter": "Scatter Plot",
                                "corr": "Correlation Heatmap",
                            },
                            selected="hist",
                        ),
                        ui.input_select("x_var", "X Axis", choices={}),
                        ui.input_select("y_var", "Y Axis", choices={}),
                        ui.input_select("color_var", "Color (optional)", choices={"": "None"}),
                    ),
                    ui_core.column(
                        6,
                        ui.div("Filters", class_="group-title"),
                        ui.input_select("num_filter_col", "Numeric filter", choices={"": "None"}),
                        ui.input_slider("num_filter_range", "Range", min=0.0, max=1.0, value=[0.0, 1.0]),
                        ui.input_select("cat_filter_col", "Category filter", choices={"": "None"}),
                        ui.input_selectize("cat_filter_vals", "Category values", choices=[], multiple=True),
                    ),
                    class_="g-2 eda-viz-columns",
                )
                with ui.div(class_="eda-viz-generate"):
                    ui.input_action_button("generate_plot", "Generate plot")

            with ui.div():
                with ui.card(class_="eda-plot-card"):
                    ui.div("Plot Output", class_="section-title")

                    @render.plot
                    @reactive.event(input.generate_plot)
                    def eda_plot():
                        df = current_df.get()
                        fig, ax = plt.subplots(figsize=(6.5, 3.2))
                        if df.empty:
                            ax.text(0.5, 0.5, "No data loaded", ha="center", va="center")
                            ax.axis("off")
                            return fig

                        plot_df = df.copy()
                        n_col = input.num_filter_col()
                        if n_col and n_col in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df[n_col]):
                            rmin, rmax = input.num_filter_range()
                            plot_df = plot_df[(plot_df[n_col] >= rmin) & (plot_df[n_col] <= rmax)]

                        c_col = input.cat_filter_col()
                        c_vals = input.cat_filter_vals() or []
                        if c_col and c_col in plot_df.columns and c_vals:
                            plot_df = plot_df[plot_df[c_col].astype(str).isin(c_vals)]

                        if plot_df.empty:
                            eda_status.set({"status": "error", "message": "No rows available after filters."})
                            ax.text(0.5, 0.5, "No rows available after filters", ha="center", va="center")
                            ax.axis("off")
                            return fig

                        p = input.plot_type()
                        x = input.x_var()
                        y = input.y_var()
                        color = input.color_var()

                        try:
                            if p == "hist":
                                ax.hist(plot_df[x].dropna(), bins=20)
                                ax.set_title(f"Histogram of {x}")
                            elif p == "box":
                                ax.boxplot(plot_df[x].dropna())
                                ax.set_xticklabels([x])
                                ax.set_title(f"Box Plot of {x}")
                            elif p == "bar":
                                counts = plot_df[x].astype(str).value_counts().head(15)
                                ax.bar(counts.index, counts.values)
                                ax.tick_params(axis="x", rotation=45)
                                ax.set_title(f"Bar Chart of {x}")
                            elif p == "scatter":
                                if color and color in plot_df.columns:
                                    for name, g in plot_df.groupby(color):
                                        ax.scatter(g[x], g[y], label=str(name), alpha=0.7)
                                    ax.legend()
                                else:
                                    ax.scatter(plot_df[x], plot_df[y], alpha=0.7)
                                ax.set_xlabel(x)
                                ax.set_ylabel(y)
                                ax.set_title(f"{y} vs {x}")
                            else:
                                num = plot_df.select_dtypes(include="number")
                                corr = num.corr()
                                im = ax.imshow(corr, aspect="auto")
                                ax.set_xticks(range(len(corr.columns)))
                                ax.set_yticks(range(len(corr.columns)))
                                ax.set_xticklabels(corr.columns, rotation=45, ha="right")
                                ax.set_yticklabels(corr.columns)
                                ax.set_title("Correlation Heatmap")
                                fig.colorbar(im, ax=ax)
                            eda_status.set({"status": "success", "message": f"Plot generated with {len(plot_df)} rows after filters."})
                        except Exception as e:
                            eda_status.set({"status": "error", "message": f"Plot generation failed: {e}"})
                            ax.clear()
                            ax.text(0.5, 0.5, f"Plot error: {e}", ha="center", va="center")
                            ax.axis("off")
                        return fig

                    # ── GA4: visualization_created + task_completed ─────────
                    @render.ui
                    @reactive.event(input.generate_plot)
                    def viz_tracker():
                        df = current_df.get()
                        if df.empty:
                            return ui.div()
                        info = eda_status.get()
                        if info.get("status") != "success":
                            return ui.div()
                        try:
                            plot_type = input.plot_type()
                            x_var = input.x_var()
                        except:
                            return ui.div()

                        return ui.div(
                            ga_event_script(
                                "ab_visualization_created",
                                {"plot_type": plot_type, "x_var": x_var}
                            ),
                            # task_completed: fires once per session
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

                with ui.card(class_="compact-feedback"):
                    ui.div("EDA Feedback", class_="section-title")
                    @render.ui
                    def eda_feedback_ui():
                        info = eda_status.get()
                        msg = (info.get("message") or "").strip()
                        if info.get("status", "idle") == "idle" and not msg:
                            info = {**info, "message": "Ready when you generate a plot."}
                        return status_box(info)

    # Export
    with ui.nav_panel("Export"):
        with ui.layout_columns(col_widths=(3, 9)):
            with ui.card(class_="left-tools"):
                ui.div("Export", class_="section-title")
                @render.download(filename="processed_data.csv")
                def download_processed_data():
                    df = current_df.get()
                    if df.empty:
                        yield "No data available.\n"
                    else:
                        yield df.to_csv(index=False)

            with ui.card(class_="dense-grid"):
                ui.div("Preview", class_="section-title")
                @render.data_frame
                def export_preview():
                    df = current_df.get()
                    if df.empty:
                        return render.DataGrid(pd.DataFrame({"Message": ["No data loaded"]}), width="100%", height="220px")
                    return render.DataGrid(df.head(15), width="100%", height="220px")


#
# Reactive effects
#
def _after_data_loaded(df: pd.DataFrame, source: str, source_type: str = "unknown", dataset_name: str = "unknown") -> None:
    current_df.set(df.copy())
    original_df.set(df.copy())
    operation_log.set([f"Loaded dataset from {source}"])
    engineered_columns.set([])
    cleaning_status.set({"status": "idle", "message": ""})
    fe_status.set({"status": "idle", "message": ""})
    eda_status.set({"status": "idle", "message": ""})
    upload_status.set({
        "status": "success",
        "message": f"Loaded {source}: {df.shape[0]} rows x {df.shape[1]} columns.",
        "source_type": source_type,
        "dataset_name": dataset_name
    })


@reactive.effect
@reactive.event(input.load_sample_btn)
def _load_sample():
    selected = input.sample_dataset()
    if not selected:
        upload_status.set({"status": "error", "message": "Please select a sample dataset first."})
        return
    # GA4: track upload_clicked for sample
    try:
        df = load_sample_dataset(selected)
        _after_data_loaded(df, f"sample '{selected}'", source_type="sample", dataset_name=selected)
    except Exception as e:
        upload_status.set({"status": "error", "message": f"Failed to load sample: {e}"})


@reactive.effect
@reactive.event(input.file_upload)
def _load_upload():
    files = input.file_upload()
    if not files:
        return
    fileinfo = files[0]
    try:
        df = read_uploaded_file(fileinfo)
        _after_data_loaded(df, f"file '{fileinfo['name']}'", source_type="upload", dataset_name=fileinfo["name"])
    except Exception as e:
        upload_status.set({"status": "error", "message": f"Upload failed: {e}"})


@reactive.effect
def _update_dynamic_choices():
    df = current_df.get()
    all_cols = df.columns.tolist() if not df.empty else []
    numeric_cols = df.select_dtypes(include="number").columns.tolist() if not df.empty else []
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist() if not df.empty else []
    dropdown_choices.set({"numeric": numeric_cols, "all": all_cols, "categorical": categorical_cols})

    # EDA dropdowns
    ui.update_select("x_var", choices={c: c for c in all_cols})
    ui.update_select("y_var", choices={c: c for c in numeric_cols})
    ui.update_select("color_var", choices={"": "None", **{c: c for c in categorical_cols}})
    ui.update_select("num_filter_col", choices={"": "None", **{c: c for c in numeric_cols}})
    ui.update_select("cat_filter_col", choices={"": "None", **{c: c for c in categorical_cols}})

    cat_col = input.cat_filter_col() if hasattr(input, "cat_filter_col") else ""
    if cat_col and cat_col in df.columns:
        values = sorted(df[cat_col].dropna().astype(str).unique().tolist())
        ui.update_selectize("cat_filter_vals", choices=values, selected=[])
    else:
        ui.update_selectize("cat_filter_vals", choices=[], selected=[])

    num_col = input.num_filter_col() if hasattr(input, "num_filter_col") else ""
    if num_col and num_col in df.columns and pd.api.types.is_numeric_dtype(df[num_col]):
        values = df[num_col].dropna()
        if not values.empty:
            low = float(values.min())
            high = float(values.max())
            if low == high:
                high = low + 1.0
            ui.update_slider("num_filter_range", min=low, max=high, value=[low, high])