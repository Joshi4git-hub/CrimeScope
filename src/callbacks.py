from datetime import datetime
import zoneinfo
from dash import Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from src.data_prep import get_processed_data, get_data_summary
from src.charts import (
    build_sparkline, build_crime_trend_chart, build_crime_type_donut,
    build_hour_day_heatmap, build_multi_crime_comparison, build_seasonality_chart,
    build_hourly_profile_chart, build_chicago_map, build_top_community_areas_chart,
    build_districts_bar_chart, build_top_15_ca_chart, build_prediction_probs_chart,
    build_confusion_matrix_heatmap, build_feature_importance_chart, create_empty_figure
)
from src.ml import train_and_eval_models, predict_crime_category
from src.layout import (
    build_sidebar, build_overview_page, build_trends_page,
    build_map_page, build_districts_page, build_prediction_page,
    build_model_comparison_page, build_about_page
)

def filter_dataframe(df, filter_store):
    """
    Applies global filter settings from dcc.Store to DataFrame.
    """
    if not filter_store or df.empty:
        return df
        
    filtered_df = df.copy()
    
    # Crime Type Filter
    crimes = filter_store.get("crimes")
    if crimes:
        filtered_df = filtered_df[filtered_df["primary_type_clean"].isin(crimes)]
        
    # District Filter
    districts = filter_store.get("districts")
    if districts:
        filtered_df = filtered_df[filtered_df["district"].isin(districts)]
        
    # Year Range Filter
    years = filter_store.get("years")
    if years and len(years) == 2:
        filtered_df = filtered_df[(filtered_df["year"] >= years[0]) & (filtered_df["year"] <= years[1])]
        
    # Arrest Filter
    arrest = filter_store.get("arrest")
    if arrest == "YES":
        filtered_df = filtered_df[filtered_df["arrest"] == True]
    elif arrest == "NO":
        filtered_df = filtered_df[filtered_df["arrest"] == False]
        
    # Domestic Filter
    domestic = filter_store.get("domestic")
    if domestic == "YES":
        filtered_df = filtered_df[filtered_df["domestic"] == True]
    elif domestic == "NO":
        filtered_df = filtered_df[filtered_df["domestic"] == False]
        
    return filtered_df

def register_callbacks(app):
    """
    Registers all Dash callbacks for interactivity across CrimeScope.
    """
    df = get_processed_data()
    
    # 1. Routing & Layout Updates
    @app.callback(
        [
            Output("page-content", "children"),
            Output("sidebar-container", "children"),
            Output("page-section-label", "children"),
            Output("page-main-title", "children"),
            Output("page-sub-title", "children")
        ],
        [Input("url", "pathname")]
    )
    def render_page_content(pathname):
        sidebar = build_sidebar(active_href=pathname or "/")
        
        if pathname == "/trends":
            return build_trends_page(), sidebar, "TRENDS", "Temporal & Seasonal Trends", "Multi-period pattern analysis and comparative volume metrics"
        elif pathname == "/map":
            return build_map_page(), sidebar, "MAP", "Geospatial Crime Density", "Interactive spatial visualization and hot-spot analysis"
        elif pathname == "/districts":
            return build_districts_page(), sidebar, "DISTRICTS", "Police District Benchmarks", "District-level incident rates, arrest proportions, and community areas"
        elif pathname == "/prediction":
            return build_prediction_page(df), sidebar, "PREDICTION", "Crime Category Classifier", "Machine learning spatio-temporal risk estimate"
        elif pathname == "/model-comparison":
            return build_model_comparison_page(), sidebar, "MODEL COMPARISON", "Supervised ML Benchmark", "Performance comparison across classification models"
        elif pathname == "/about":
            summary_stats = get_data_summary()
            return build_about_page(summary_stats), sidebar, "ABOUT & DATA", "System Metadata & Source", "Chicago CLEAR dataset dictionary and documentation"
        else:
            return build_overview_page(), sidebar, "OVERVIEW", "Chicago Crime Analytics", "Real-time multi-dimensional exploratory dashboard"

    # 2. Toggle Offcanvas Filter Panel
    @app.callback(
        Output("offcanvas-filters", "is_open"),
        [Input("btn-open-filters", "n_clicks")],
        [State("offcanvas-filters", "is_open")]
    )
    def toggle_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # 3. Reset & Sync Global Filter Store
    @app.callback(
        [
            Output("global-filter-store", "data"),
            Output("filter-crime-type", "value"),
            Output("filter-district", "value"),
            Output("filter-year-range", "value"),
            Output("filter-arrest", "value"),
            Output("filter-domestic", "value")
        ],
        [
            Input("filter-crime-type", "value"),
            Input("filter-district", "value"),
            Input("filter-year-range", "value"),
            Input("filter-arrest", "value"),
            Input("filter-domestic", "value"),
            Input("btn-reset-filters", "n_clicks")
        ]
    )
    def update_global_filter_store(crimes, districts, years, arrest, domestic, reset_clicks):
        ctx = callback_context
        triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
        
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())
        
        if triggered == "btn-reset-filters":
            default_store = {
                "crimes": None,
                "districts": None,
                "years": [min_year, max_year],
                "arrest": "ALL",
                "domestic": "ALL"
            }
            return default_store, None, None, [min_year, max_year], "ALL", "ALL"
            
        store_data = {
            "crimes": crimes,
            "districts": districts,
            "years": years or [min_year, max_year],
            "arrest": arrest or "ALL",
            "domestic": domestic or "ALL"
        }
        return store_data, crimes, districts, years, arrest, domestic

    # 4. Overview Page Updates (KPIs, Charts, Table, Insight Banner)
    @app.callback(
        [
            Output("kpi-total-crimes", "children"),
            Output("kpi-top-crime-type", "children"),
            Output("kpi-peak-hour", "children"),
            Output("kpi-top-district", "children"),
            Output("chart-crime-trend", "figure"),
            Output("chart-crime-donut", "figure"),
            Output("chart-hour-day-heatmap", "figure"),
            Output("overview-top-districts-table", "children"),
            Output("overview-insight-text", "children")
        ],
        [
            Input("global-filter-store", "data"),
            Input("overview-trend-grouping", "value")
        ]
    )
    def update_overview_page(filter_store, trend_grouping):
        f_df = filter_dataframe(df, filter_store)
        
        total_crimes = len(f_df)
        
        try:
            ch_tz = zoneinfo.ZoneInfo("America/Chicago")
            now_ch = datetime.now(ch_tz)
        except Exception:
            now_ch = datetime.now()
            
        cur_hour = now_ch.hour
        cur_hour_str = now_ch.strftime("%I:00 %p CT")
        cur_time_str = now_ch.strftime("%I:%M %p CT")
        
        if not f_df.empty:
            top_crime = f_df["primary_type_clean"].value_counts().index[0]
            top_dist = f_df["district"].value_counts().index[0]
            
            # Live ML Risk Prediction for right now in Chicago
            live_res = predict_crime_category(
                hour=cur_hour,
                day_of_week_num=now_ch.weekday(),
                month=now_ch.month,
                district=top_dist,
                model_name="RandomForest"
            )
            live_cat = live_res["predicted_category"]
            live_prob = live_res["top_probabilities"][0]["probability"] * 100
            
            insight_msg = f"LIVE CHICAGO RISK ({cur_time_str}): Model predicts {live_cat} as top estimated crime risk right now ({live_prob:.1f}% probability in District {top_dist})."
        else:
            top_crime, top_dist = "N/A", "N/A"
            live_cat = "N/A"
            insight_msg = "No crime records match the current filter selection."
            
        # Sparklines
        m_counts = f_df.groupby("month").size().reindex(range(1, 13)).fillna(0).values if not f_df.empty else []
        spark_fig = build_sparkline(m_counts)
        
        def make_kpi_card(title, value, badge_text, badge_type="up"):
            badge_class = f"badge-delta badge-delta-{badge_type}"
            return html.Div(
                [
                    html.Div(title, className="card-title"),
                    html.Div(
                        [
                            html.Span(f"{value:,}" if isinstance(value, int) else str(value), className="card-kpi-value"),
                            html.Span(badge_text, className=badge_class)
                        ],
                        style={"display": "flex", "alignItems": "baseline", "justifyContent": "space-between", "marginBottom": "12px"}
                    ),
                    dcc.Graph(figure=spark_fig, config={"displayModeBar": False})
                ],
                className="cs-card"
            )
            
        kpi_total = make_kpi_card("Total Crimes Reported", total_crimes, f"{len(f_df):,} Rows", "up")
        kpi_type = make_kpi_card("Most Frequent Category", top_crime, "Top 1", "neutral")
        kpi_hour = make_kpi_card("Current Chicago Risk Hour", cur_hour_str, f"Pred: {live_cat}", "up")
        kpi_district = make_kpi_card("Highest Volume District", f"District {top_dist}", "Hotspot", "up")
        
        # Charts
        trend_fig = build_crime_trend_chart(f_df, group_by=trend_grouping or "Month")
        donut_fig = build_crime_type_donut(f_df)
        heatmap_fig = build_hour_day_heatmap(f_df)
        
        # Top 5 Districts Table
        if not f_df.empty:
            top5_dist = f_df["district"].value_counts().head(5).reset_index()
            top5_dist.columns = ["district", "count"]
            
            rows = []
            for rank, row in enumerate(top5_dist.itertuples(), 1):
                pct = (row.count / total_crimes) * 100
                rows.append(
                    html.Tr([
                        html.Td(f"#{rank}", style={"fontWeight": "700", "color": "#FF5A1F"}),
                        html.Td(f"District {row.district}"),
                        html.Td(f"{row.count:,}"),
                        html.Td(
                            html.Div(
                                [
                                    html.Div(
                                        html.Div(className="cs-progress-bar-fill", style={"width": f"{pct}%"}),
                                        className="cs-progress-bar-bg"
                                    ),
                                    html.Small(f"{pct:.1f}%", style={"color": "#8A8A8A", "marginLeft": "8px"})
                                ],
                                style={"display": "flex", "alignItems": "center"}
                            )
                        )
                    ])
                )
            dist_table = html.Table(
                [
                    html.Thead(html.Tr([html.Th("Rank"), html.Th("District"), html.Th("Count"), html.Th("Share")])),
                    html.Tbody(rows)
                ],
                className="cs-table"
            )
        else:
            dist_table = html.P("No data for these filters.", style={"color": "#8A8A8A"})
            
        return kpi_total, kpi_type, kpi_hour, kpi_district, trend_fig, donut_fig, heatmap_fig, dist_table, insight_msg

    # 5. Trends Page Callback
    @app.callback(
        [
            Output("trends-multi-select", "options"),
            Output("chart-trends-multi-line", "figure"),
            Output("chart-seasonality", "figure"),
            Output("chart-hourly-profile", "figure")
        ],
        [
            Input("global-filter-store", "data"),
            Input("trends-multi-select", "value")
        ]
    )
    def update_trends_page(filter_store, selected_types):
        f_df = filter_dataframe(df, filter_store)
        
        all_types = sorted(f_df["primary_type_clean"].unique().tolist()) if not f_df.empty else []
        options = [{"label": c, "value": c} for c in all_types]
        
        multi_fig = build_multi_crime_comparison(f_df, selected_crimes=selected_types)
        season_fig = build_seasonality_chart(f_df)
        hourly_fig = build_hourly_profile_chart(f_df)
        
        return options, multi_fig, season_fig, hourly_fig

    # 6. Map Page Callback
    @app.callback(
        [
            Output("chart-chicago-map", "figure"),
            Output("chart-top-community-areas", "figure")
        ],
        [
            Input("global-filter-store", "data"),
            Input("map-mode-toggle", "value")
        ]
    )
    def update_map_page(filter_store, map_mode):
        f_df = filter_dataframe(df, filter_store)
        map_fig = build_chicago_map(f_df, map_mode=map_mode or "Heatmap")
        top_ca_fig = build_top_community_areas_chart(f_df)
        return map_fig, top_ca_fig

    # 7. Districts Page Callback
    @app.callback(
        [
            Output("chart-districts-bar", "figure"),
            Output("chart-top-15-ca", "figure"),
            Output("districts-full-table", "children")
        ],
        [Input("global-filter-store", "data")]
    )
    def update_districts_page(filter_store):
        f_df = filter_dataframe(df, filter_store)
        dist_bar_fig = build_districts_bar_chart(f_df)
        ca_15_fig = build_top_15_ca_chart(f_df)
        
        if not f_df.empty:
            summary = f_df.groupby("district").agg(
                total=("date", "count"),
                arrest_cnt=("arrest", lambda x: x.sum()),
                domestic_cnt=("domestic", lambda x: x.sum())
            ).reset_index().sort_values("total", ascending=False)
            
            summary["arrest_rate"] = (summary["arrest_cnt"] / summary["total"] * 100).round(1)
            summary["domestic_share"] = (summary["domestic_cnt"] / summary["total"] * 100).round(1)
            
            rows = []
            for rank, r in enumerate(summary.itertuples(), 1):
                rows.append(html.Tr([
                    html.Td(f"#{rank}", style={"fontWeight": "700", "color": "#FF5A1F"}),
                    html.Td(f"District {r.district}"),
                    html.Td(f"{r.total:,}"),
                    html.Td(f"{r.arrest_rate}%"),
                    html.Td(f"{r.domestic_share}%")
                ]))
                
            dist_table = html.Table(
                [
                    html.Thead(html.Tr([
                        html.Th("Rank"), html.Th("District"), html.Th("Total Crimes"),
                        html.Th("Arrest Rate"), html.Th("Domestic Share")
                    ])),
                    html.Tbody(rows)
                ],
                className="cs-table"
            )
        else:
            dist_table = html.P("No data available.", style={"color": "#8A8A8A"})
            
        return dist_bar_fig, ca_15_fig, dist_table

    # 8. Prediction Page Callback
    @app.callback(
        Output("pred-hour-badge", "children"),
        [Input("pred-hour-slider", "value")]
    )
    def update_pred_hour_badge(val):
        h = val if val is not None else 18
        return f"{h:02d}:00"

    # 8a. Sync inputs with Current Chicago Time Callback
    @app.callback(
        [
            Output("pred-hour-slider", "value"),
            Output("pred-day-dropdown", "value"),
            Output("pred-month-dropdown", "value")
        ],
        [Input("btn-sync-current-time", "n_clicks")]
    )
    def sync_inputs_to_current_chicago_time(n_clicks):
        try:
            ch_tz = zoneinfo.ZoneInfo("America/Chicago")
            now_ch = datetime.now(ch_tz)
            return now_ch.hour, now_ch.weekday(), now_ch.month
        except Exception:
            return 18, 4, 7

    # 8b. Run Prediction Callback
    @app.callback(
        Output("pred-output-container", "children"),
        [
            Input("btn-run-prediction", "n_clicks"),
            Input("pred-hour-slider", "value"),
            Input("pred-day-dropdown", "value"),
            Input("pred-month-dropdown", "value"),
            Input("pred-district-dropdown", "value"),
            Input("pred-ca-dropdown", "value"),
            Input("pred-model-select", "value")
        ]
    )
    def run_prediction(n_clicks, hour, day_num, month, district, ca, model_name):
        res = predict_crime_category(
            hour=hour if hour is not None else 18,
            day_of_week_num=day_num if day_num is not None else 4,
            month=month if month is not None else 7,
            district=district if district is not None else 1,
            community_area=ca or 0,
            model_name=model_name or "RandomForest"
        )
        
        pred_cat = res["predicted_category"]
        top_probs = res["top_probabilities"]
        probs_fig = build_prediction_probs_chart(top_probs)
        
        return html.Div(
            [
                html.Div(
                    [
                        html.Span("ESTIMATED CRIME CATEGORY", style={"fontSize": "11px", "color": "#8A8A8A", "fontWeight": "700"}),
                        html.H2(pred_cat, style={"color": "#FF5A1F", "fontWeight": "800", "fontSize": "26px", "margin": "4px 0 16px 0"})
                    ]
                ),
                dcc.Graph(figure=probs_fig, config={"displayModeBar": False})
            ]
        )

    # 9. Model Comparison Page Callback
    @app.callback(
        [
            Output("ml-metrics-table-container", "children"),
            Output("chart-confusion-matrix", "figure"),
            Output("chart-feature-importance", "figure")
        ],
        [Input("cm-model-select", "value")]
    )
    def update_model_comparison(selected_model):
        metrics = train_and_eval_models()
        
        # Build benchmark comparison table
        DISPLAY_NAMES = {
            "RandomForest": "Random Forest",
            "LogisticRegression": "Logistic Regression",
            "DecisionTree": "Decision Tree"
        }
        table_rows = []
        for m_name, m_data in metrics.items():
            display_name = DISPLAY_NAMES.get(m_name, m_name)
            table_rows.append(html.Tr([
                html.Td(display_name, style={"fontWeight": "700", "color": "#F2F2F2"}),
                html.Td(f"{m_data['accuracy']*100:.2f}%"),
                html.Td(f"{m_data['precision']*100:.2f}%"),
                html.Td(f"{m_data['recall']*100:.2f}%"),
                html.Td(f"{m_data['f1_score']*100:.2f}%"),
                html.Td(f"{m_data['train_time']} s")
            ]))
            
        benchmark_table = html.Table(
            [
                html.Thead(html.Tr([
                    html.Th("Model"), html.Th("Accuracy"), html.Th("Weighted Precision"),
                    html.Th("Weighted Recall"), html.Th("Weighted F1"), html.Th("Train Time")
                ])),
                html.Tbody(table_rows)
            ],
            className="cs-table"
        )
        
        m_info = metrics.get(selected_model or "RandomForest", metrics["RandomForest"])
        cm_fig = build_confusion_matrix_heatmap(
            cm=m_info["confusion_matrix"],
            classes=m_info["classes"],
            model_name=selected_model or "RandomForest"
        )
        
        rf_info = metrics.get("RandomForest", {})
        fi_fig = build_feature_importance_chart(rf_info.get("feature_importances"))
        
        return benchmark_table, cm_fig, fi_fig

    # 10. Download Filtered CSV Callback
    @app.callback(
        Output("download-dataframe-csv", "data"),
        [Input("btn-download-csv", "n_clicks")],
        [State("global-filter-store", "data")],
        prevent_initial_call=True
    )
    def download_csv(n_clicks, filter_store):
        if n_clicks:
            f_df = filter_dataframe(df, filter_store)
            return dcc.send_data_frame(f_df.to_csv, "crimescope_filtered_crimes.csv", index=False)

    # 11. Live Chicago Time Clock Callback
    @app.callback(
        Output("live-chicago-clock", "children"),
        [Input("chicago-clock-interval", "n_intervals")]
    )
    def update_chicago_clock(n):
        try:
            ch_tz = zoneinfo.ZoneInfo("America/Chicago")
            now_ch = datetime.now(ch_tz)
        except Exception:
            now_ch = datetime.now()
        return now_ch.strftime("%b %d, %Y • %I:%M:%S %p %Z")
