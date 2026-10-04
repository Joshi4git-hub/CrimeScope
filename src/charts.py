import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from src.theme import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TERTIARY,
    COLOR_BG, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLORWAY
)

def apply_dark_theme(fig, title="", xaxis_title=None, yaxis_title=None, height=None, margin=None):
    """
    Safely applies dark theme styling to any Plotly figure without duplicate kwarg errors.
    """
    fig.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT_MAIN, size=12),
        title=dict(text=title, font=dict(color=COLOR_TEXT_MAIN, size=16), x=0.01, xanchor="left") if title else None,
        margin=margin or dict(l=50, r=30, t=40, b=40)
    )
    if height:
        fig.update_layout(height=height)
        
    fig.update_xaxes(
        title_text=xaxis_title,
        gridcolor=COLOR_BORDER,
        zerolinecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_MAIN, size=12),
        showline=True,
        linecolor=COLOR_BORDER
    )
    fig.update_yaxes(
        title_text=yaxis_title,
        gridcolor=COLOR_BORDER,
        zerolinecolor=COLOR_BORDER,
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_MAIN, size=12),
        showline=True,
        linecolor=COLOR_BORDER
    )
    return fig

def create_empty_figure(title="", message="No data matches the selected filters."):
    """
    Returns a styled dark empty Plotly figure when filters yield 0 rows or data is uninitialized.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=COLOR_TEXT_MUTED)
    )
    fig.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        title=dict(text=title, font=dict(color=COLOR_TEXT_MAIN, size=15)),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# --- OVERVIEW CHARTS ---

def build_sparkline(series_data):
    """
    Builds a micro sparkline figure for KPI cards.
    """
    fig = go.Figure()
    if len(series_data) > 0:
        fig.add_trace(go.Scatter(
            y=series_data,
            mode="lines",
            line=dict(color=COLOR_PRIMARY, width=2, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(255, 90, 31, 0.15)",
            hoverinfo="none"
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=40
    )
    return fig

def build_crime_trend_chart(df, group_by="Month"):
    """
    Line/Area chart for Crime Trend grouped by Year / Month / Day of Week / Hour.
    """
    if df is None or df.empty:
        return create_empty_figure("Crime Incident Volume Trend")
        
    if group_by == "Year":
        counts = df.groupby("year").size().reset_index(name="count")
        x_col, x_title = "year", "Year"
    elif group_by == "Day of Week":
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        counts = df.groupby("day_of_week").size().reindex(days_order).fillna(0).reset_index(name="count")
        x_col, x_title = "day_of_week", "Day of Week"
    elif group_by == "Hour":
        counts = df.groupby("hour").size().reindex(range(24)).fillna(0).reset_index(name="count")
        counts["hour_label"] = counts["hour"].apply(lambda h: f"{h:02d}:00")
        x_col, x_title = "hour_label", "Hour of Day (Chicago Time - CT)"
    else:  # Month
        months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        counts = df.groupby("month_name").size().reindex(months_order).fillna(0).reset_index(name="count")
        x_col, x_title = "month_name", "Month"
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=counts[x_col],
        y=counts["count"],
        mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=3, shape="spline"),
        marker=dict(size=6, color=COLOR_SECONDARY, symbol="circle"),
        fill="tozeroy",
        fillcolor="rgba(255, 90, 31, 0.12)",
        hovertemplate="<b>%{x}</b><br>Incidents: <b>%{y:,}</b><extra></extra>"
    ))
    
    return apply_dark_theme(fig, title="Crime Incident Volume Trend", xaxis_title=x_title, yaxis_title="Total Incidents")

def build_crime_type_donut(df):
    """
    Donut chart of Crime Type Share with counts and percentages in legend.
    """
    if df is None or df.empty:
        return create_empty_figure("Crime Type Distribution")
        
    counts = df["primary_type_clean"].value_counts().reset_index()
    counts.columns = ["crime_type", "count"]
    
    total = counts["count"].sum()
    counts["percentage"] = (counts["count"] / total * 100).round(1)
    counts["label"] = counts.apply(lambda r: f"{r['crime_type']} ({r['count']:,} - {r['percentage']}%)", axis=1)
    
    fig = go.Figure(data=[go.Pie(
        labels=counts["label"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=COLORWAY),
        textinfo="percent",
        textfont=dict(color="#FFFFFF", size=11),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<extra></extra>"
    )])
    
    fig.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT_MAIN),
        title=dict(text="Crime Type Distribution", font=dict(color=COLOR_TEXT_MAIN, size=16), x=0.01, xanchor="left"),
        legend=dict(orientation="v", y=0.5, x=1.02, font=dict(color=COLOR_TEXT_MAIN, size=11), bgcolor="rgba(20,20,20,0.8)", bordercolor=COLOR_BORDER),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def build_hour_day_heatmap(df):
    """
    Heatmap of Hour x Day of Week (main 'when' insight).
    """
    if df is None or df.empty:
        return create_empty_figure("Crime Frequency Heatmap (Hour × Day of Week)")
        
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    pivot = df.pivot_table(
        index="day_of_week",
        columns="hour",
        values="year",
        aggfunc="count",
        fill_value=0
    ).reindex(days_order)
    
    for h in range(24):
        if h not in pivot.columns:
            pivot[h] = 0
    pivot = pivot[sorted(pivot.columns)]
    
    hour_labels = [f"{h:02d}:00" for h in pivot.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=hour_labels,
        y=days_order,
        colorscale=[
            [0.0, "#141414"],
            [0.2, "#3A1700"],
            [0.5, "#A83407"],
            [0.8, "#FF5A1F"],
            [1.0, "#FFC23D"]
        ],
        hovertemplate="Day: <b>%{y}</b><br>Time: <b>%{x}</b><br>Incidents: <b>%{z:,}</b><extra></extra>",
        colorbar=dict(title=dict(text="Incidents", font=dict(color=COLOR_TEXT_MAIN)), tickfont=dict(color=COLOR_TEXT_MUTED))
    ))
    
    return apply_dark_theme(fig, title="Crime Frequency Heatmap (Hour × Day of Week)", xaxis_title="Hour of Day (Chicago Time - CT)", yaxis_title="Day of Week", margin=dict(l=60, r=20, t=40, b=40))

# --- TRENDS PAGE CHARTS ---

def build_multi_crime_comparison(df, selected_crimes=None):
    """
    Multi-line chart comparing selected crime types over time.
    """
    if df is None or df.empty:
        return create_empty_figure("Monthly Trend Comparison Across Crime Categories")
        
    if not selected_crimes:
        selected_crimes = df["primary_type_clean"].value_counts().nlargest(3).index.tolist()
        
    df_filtered = df[df["primary_type_clean"].isin(selected_crimes)].copy()
    if df_filtered.empty:
        return create_empty_figure("Monthly Trend Comparison Across Crime Categories")
        
    df_filtered["year_month"] = df_filtered["date"].dt.to_period("M").astype(str)
    grouped = df_filtered.groupby(["year_month", "primary_type_clean"]).size().reset_index(name="count")
    
    fig = go.Figure()
    for i, ctype in enumerate(selected_crimes):
        c_data = grouped[grouped["primary_type_clean"] == ctype]
        fig.add_trace(go.Scatter(
            x=c_data["year_month"],
            y=c_data["count"],
            name=ctype,
            mode="lines+markers",
            line=dict(width=2.5, color=COLORWAY[i % len(COLORWAY)], shape="spline"),
            hovertemplate=f"Category: <b>{ctype}</b><br>Month: %{{x}}<br>Count: <b>%{{y:,}}</b><extra></extra>"
        ))
        
    apply_dark_theme(fig, title="Monthly Trend Comparison Across Crime Categories", xaxis_title="Year-Month", yaxis_title="Incidents", margin=dict(l=50, r=20, t=60, b=40))
    fig.update_layout(legend=dict(orientation="h", y=1.15, x=0.99, xanchor="right", font=dict(color=COLOR_TEXT_MAIN, size=11), bgcolor="rgba(20,20,20,0.8)", bordercolor=COLOR_BORDER, borderwidth=1))
    return fig

def build_seasonality_chart(df):
    """
    Monthly seasonality line/bar chart.
    """
    if df is None or df.empty:
        return create_empty_figure("Monthly Seasonality Pattern")
        
    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = df.groupby("month_name").size().reindex(months_order).fillna(0).reset_index(name="count")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month_name"],
        y=monthly["count"],
        marker=dict(
            color=monthly["count"],
            colorscale=[[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
            cornerradius=6
        ),
        hovertemplate="Month: <b>%{x}</b><br>Count: <b>%{y:,}</b><extra></extra>"
    ))
    return apply_dark_theme(fig, title="Monthly Seasonality Pattern", xaxis_title="Month", yaxis_title="Total Incidents")

def build_hourly_profile_chart(df):
    """
    Hourly profile line with smooth gradient area fill.
    """
    if df is None or df.empty:
        return create_empty_figure("24-Hour Crime Profile")
        
    hourly = df.groupby("hour").size().reindex(range(24)).fillna(0).reset_index(name="count")
    hourly["hour_str"] = hourly["hour"].apply(lambda h: f"{h:02d}:00")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly["hour_str"],
        y=hourly["count"],
        mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(255, 90, 31, 0.2)",
        hovertemplate="Time: <b>%{x}</b><br>Count: <b>%{y:,}</b><extra></extra>"
    ))
    return apply_dark_theme(fig, title="24-Hour Crime Profile", xaxis_title="Hour of Day (Chicago Time - CT)", yaxis_title="Total Incidents")

# --- MAP PAGE CHARTS ---

def build_chicago_map(df, map_mode="Heatmap"):
    """
    Builds interactive Plotly map of Chicago (Heatmap / Points / District Bubbles).
    """
    if df is None or df.empty:
        return create_empty_figure("Chicago Crime Map")
        
    center_lat = 41.8781
    center_lon = -87.6298
    
    # Check for Plotly 6+ scatter_map vs scatter_mapbox
    has_scatter_map = hasattr(px, "scatter_map")
    has_density_map = hasattr(px, "density_map")
    
    map_style_kw = "map_style" if has_scatter_map else "mapbox_style"
    
    if map_mode == "Points":
        map_df = df.sample(n=min(len(df), 20000), random_state=42) if len(df) > 20000 else df
        scatter_fn = px.scatter_map if has_scatter_map else px.scatter_mapbox
        
        kwargs = {
            "lat": "latitude",
            "lon": "longitude",
            "color": "primary_type_clean",
            "hover_name": "primary_type_clean",
            "hover_data": {
                "district": True,
                "date": "|%B %d, %Y %I:%M %p",
                "location_description": True,
                "latitude": False,
                "longitude": False
            },
            "zoom": 10,
            "center": {"lat": center_lat, "lon": center_lon},
            map_style_kw: "carto-darkmatter",
            "color_discrete_sequence": COLORWAY
        }
        fig = scatter_fn(map_df, **kwargs)
        fig.update_traces(marker=dict(size=5, opacity=0.7))
        
    elif map_mode == "District Bubbles":
        district_geo = df.groupby("district").agg(
            lat=("latitude", "mean"),
            lon=("longitude", "mean"),
            count=("primary_type_clean", "count")
        ).reset_index()
        
        scatter_fn = px.scatter_map if has_scatter_map else px.scatter_mapbox
        
        kwargs = {
            "lat": "lat",
            "lon": "lon",
            "size": "count",
            "color": "count",
            "hover_name": "district",
            "hover_data": {"count": ":,", "lat": False, "lon": False},
            "zoom": 10,
            "center": {"lat": center_lat, "lon": center_lon},
            map_style_kw: "carto-darkmatter",
            "color_continuous_scale": [[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
            "size_max": 35
        }
        fig = scatter_fn(district_geo, **kwargs)
        
    else:  # Heatmap
        map_df = df.sample(n=min(len(df), 20000), random_state=42) if len(df) > 20000 else df
        density_fn = px.density_map if has_density_map else px.density_mapbox
        
        kwargs = {
            "lat": "latitude",
            "lon": "longitude",
            "radius": 12,
            "zoom": 10,
            "center": {"lat": center_lat, "lon": center_lon},
            map_style_kw: "carto-darkmatter",
            "color_continuous_scale": [
                [0.0, "rgba(0,0,0,0)"],
                [0.2, "#3A1700"],
                [0.5, "#A83407"],
                [0.8, "#FF5A1F"],
                [1.0, "#FFC23D"]
            ]
        }
        fig = density_fn(map_df, **kwargs)
        
    layout_update = dict(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT_MAIN),
        margin=dict(l=0, r=0, t=0, b=0),
        height=580
    )
    if has_scatter_map:
        layout_update["map"] = dict(pitch=0)
    else:
        layout_update["mapbox"] = dict(pitch=0)
        
    fig.update_layout(**layout_update)
    return fig


def build_top_community_areas_chart(df):
    """
    Side panel chart for Top 10 Community Areas.
    """
    if df is None or df.empty:
        return create_empty_figure("Top 10 Community Areas")
        
    top_ca = df[df["community_area"] > 0]["community_area"].value_counts().head(10).reset_index()
    top_ca.columns = ["community_area", "count"]
    top_ca["ca_label"] = top_ca["community_area"].apply(lambda ca: f"Area #{ca}")
    
    fig = go.Figure(go.Bar(
        x=top_ca["count"],
        y=top_ca["ca_label"],
        orientation="h",
        marker=dict(
            color=top_ca["count"],
            colorscale=[[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
            cornerradius=4
        ),
        hovertemplate="<b>%{y}</b><br>Incidents: <b>%{x:,}</b><extra></extra>"
    ))
    
    apply_dark_theme(fig, title="Top 10 Community Areas", xaxis_title="Incidents", margin=dict(l=80, r=20, t=40, b=30))
    fig.update_yaxes(autorange="reversed")
    return fig

# --- DISTRICTS PAGE CHARTS ---

def build_districts_bar_chart(df):
    """
    Bar chart of all 22 Police Districts.
    """
    if df is None or df.empty:
        return create_empty_figure("Crime Incident Volume Across All Chicago Police Districts")
        
    dist_counts = df.groupby("district").size().reset_index(name="count").sort_values("count", ascending=False)
    dist_counts["district_label"] = dist_counts["district"].apply(lambda d: f"Dist {d}")
    
    fig = go.Figure(go.Bar(
        x=dist_counts["district_label"],
        y=dist_counts["count"],
        marker=dict(
            color=dist_counts["count"],
            colorscale=[[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
            cornerradius=6
        ),
        hovertemplate="<b>%{x}</b><br>Total Crimes: <b>%{y:,}</b><extra></extra>"
    ))
    
    return apply_dark_theme(fig, title="Crime Incident Volume Across All Chicago Police Districts", xaxis_title="Police District", yaxis_title="Total Incidents")

def build_top_15_ca_chart(df):
    """
    Bar chart for Top 15 Community Areas.
    """
    if df is None or df.empty:
        return create_empty_figure("Top 15 Community Areas by Volume")
        
    top15 = df[df["community_area"] > 0]["community_area"].value_counts().head(15).reset_index()
    top15.columns = ["ca", "count"]
    top15["label"] = top15["ca"].apply(lambda c: f"Area {c}")
    
    fig = go.Figure(go.Bar(
        x=top15["label"],
        y=top15["count"],
        marker=dict(color=COLOR_SECONDARY, cornerradius=4),
        hovertemplate="<b>%{x}</b><br>Incidents: <b>%{y:,}</b><extra></extra>"
    ))
    return apply_dark_theme(fig, title="Top 15 Community Areas by Volume", xaxis_title="Community Area ID", yaxis_title="Incidents")

# --- PREDICTION PAGE CHARTS ---

def build_prediction_probs_chart(top_probs):
    """
    Horizontal bar chart for top 5 predicted class probabilities.
    """
    if not top_probs:
        return create_empty_figure("Top-5 Model Class Probabilities")
        
    probs_df = pd.DataFrame(top_probs).sort_values("probability", ascending=True)
    probs_df["percentage_str"] = probs_df["probability"].apply(lambda p: f"{p*100:.1f}%")
    
    fig = go.Figure(go.Bar(
        x=probs_df["probability"],
        y=probs_df["category"],
        orientation="h",
        text=probs_df["percentage_str"],
        textposition="outside",
        textfont=dict(color=COLOR_TEXT_MAIN, size=12),
        marker=dict(
            color=probs_df["probability"],
            colorscale=[[0, COLOR_SECONDARY], [1, COLOR_PRIMARY]],
            cornerradius=4
        ),
        hovertemplate="Category: <b>%{y}</b><br>Probability: <b>%{x:.1%}</b><extra></extra>"
    ))
    
    apply_dark_theme(fig, title="Top-5 Model Class Probabilities", xaxis_title="Estimated Probability", height=320, margin=dict(l=150, r=40, t=40, b=30))
    fig.update_xaxes(range=[0, max(probs_df["probability"].max() * 1.25, 0.1)])
    return fig

# --- MODEL COMPARISON CHARTS ---

def build_confusion_matrix_heatmap(cm, classes, model_name="RandomForest"):
    """
    Confusion Matrix heatmap.
    """
    if cm is None or not len(cm):
        return create_empty_figure(f"Confusion Matrix — {model_name}")
        
    cm_array = np.array(cm)
    
    fig = go.Figure(data=go.Heatmap(
        z=cm_array,
        x=classes,
        y=classes,
        colorscale=[
            [0.0, "#141414"],
            [0.2, "#3A1700"],
            [0.5, "#A83407"],
            [1.0, "#FF5A1F"]
        ],
        hovertemplate="Actual: <b>%{y}</b><br>Predicted: <b>%{x}</b><br>Count: <b>%{z:,}</b><extra></extra>",
        colorbar=dict(title=dict(text="Count", font=dict(color=COLOR_TEXT_MAIN)), tickfont=dict(color=COLOR_TEXT_MUTED))
    ))
    
    apply_dark_theme(fig, title=f"Confusion Matrix — {model_name}", xaxis_title="Predicted Crime Category", yaxis_title="Actual Crime Category", margin=dict(l=130, r=20, t=40, b=100))
    fig.update_xaxes(tickfont=dict(size=10, color=COLOR_TEXT_MUTED), showgrid=False)
    fig.update_yaxes(tickfont=dict(size=10, color=COLOR_TEXT_MUTED), showgrid=False)
    return fig

def build_feature_importance_chart(feature_importances):
    """
    Horizontal bar chart for Random Forest Feature Importances.
    """
    if not feature_importances:
        return create_empty_figure("Random Forest Feature Importances")
        
    df_fi = pd.DataFrame(list(feature_importances.items()), columns=["feature", "importance"])
    df_fi = df_fi.sort_values("importance", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_fi["importance"],
        y=df_fi["feature"],
        orientation="h",
        marker=dict(color=COLOR_PRIMARY, cornerradius=4),
        hovertemplate="Feature: <b>%{y}</b><br>Importance: <b>%{x:.3f}</b><extra></extra>"
    ))
    
    return apply_dark_theme(fig, title="Random Forest Feature Importances", xaxis_title="Gini Feature Importance", margin=dict(l=130, r=20, t=40, b=40))
