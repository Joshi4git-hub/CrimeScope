from dash import html, dcc
import dash_bootstrap_components as dbc
from src.data_prep import get_processed_data

# Navigation items configuration
NAV_ITEMS = [
    {"label": "Overview", "icon": "bi bi-grid-1x2-fill", "href": "/"},
    {"label": "Trends", "icon": "bi bi-graph-up-arrow", "href": "/trends"},
    {"label": "Map", "icon": "bi bi-map-fill", "href": "/map"},
    {"label": "Districts", "icon": "bi bi-building-fill", "href": "/districts"},
    {"label": "Prediction", "icon": "bi bi-cpu-fill", "href": "/prediction"},
    {"label": "Model Comparison", "icon": "bi bi-bar-chart-steps", "href": "/model-comparison"},
    {"label": "About & Data", "icon": "bi bi-info-circle-fill", "href": "/about"}
]

def build_sidebar(active_href="/"):
    """
    Builds persistent left sidebar.
    """
    nav_links = []
    for item in NAV_ITEMS:
        is_active = item["href"] == active_href
        active_class = " active" if is_active else ""
        nav_links.append(
            dcc.Link(
                [
                    html.I(className=item["icon"]),
                    html.Span(item["label"])
                ],
                href=item["href"],
                className=f"nav-item-link{active_class}",
                id=f"nav-link-{item['href'].replace('/', '') or 'overview'}"
            )
        )
        
    sidebar = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-shield-shaded", style={"fontSize": "26px", "color": "#FF5A1F"})
                        ],
                        className="sidebar-logo"
                    ),
                    html.H2(["Crime", html.Span("Scope")], className="sidebar-brand-title")
                ],
                className="sidebar-header"
            ),
            html.Div(nav_links, className="sidebar-nav"),
            html.Div(
                [
                    html.Small("Chicago CLEAR Dataset", style={"color": "#8A8A8A", "fontSize": "11px", "display": "block"}),
                    html.Small("v1.0 • 2020–2024 (Chicago CT)", style={"color": "#FF5A1F", "fontSize": "11px", "fontWeight": "600"})
                ],
                style={"marginTop": "auto", "padding": "16px 8px 0 8px", "borderTop": "1px solid #262626"}
            )
        ],
        className="sidebar"
    )
    return sidebar

def build_top_header(section_label="OVERVIEW", title="Chicago Crime Analytics", subtitle="Real-time multi-dimensional exploratory dashboard"):
    """
    Builds persistent top header with section title, live Chicago time widget, and global filter triggers.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Div(section_label, className="section-label", id="page-section-label"),
                    html.H1(title, className="page-title", id="page-main-title"),
                    html.P(subtitle, className="page-subtitle", id="page-sub-title")
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-clock-history", style={"marginRight": "8px", "color": "#FF5A1F", "fontSize": "15px"}),
                            html.Div(
                                [
                                    html.Span("CHICAGO LOCAL TIME", style={"color": "#8A8A8A", "fontSize": "10px", "fontWeight": "700", "letterSpacing": "0.5px", "display": "block", "lineHeight": "1"}),
                                    html.Span(id="live-chicago-clock", children="Loading...", style={"color": "#F2F2F2", "fontSize": "13px", "fontWeight": "700", "fontFamily": "monospace", "lineHeight": "1.2"})
                                ]
                            )
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "backgroundColor": "#141414",
                            "border": "1px solid #262626",
                            "borderRadius": "10px",
                            "padding": "6px 14px",
                            "marginRight": "12px",
                            "boxShadow": "inset 0 0 10px rgba(0,0,0,0.5)"
                        }
                    ),
                    dbc.Button(
                        [
                            html.I(className="bi bi-funnel-fill", style={"marginRight": "8px"}),
                            "Global Filters"
                        ],
                        id="btn-open-filters",
                        className="btn-cs-primary",
                        n_clicks=0
                    )
                ],
                className="header-controls",
                style={"display": "flex", "alignItems": "center"}
            )
        ],
        className="header-container"
    )

def build_offcanvas_filters(df):
    """
    Builds global filter offcanvas panel.
    """
    all_crimes = sorted(df["primary_type_clean"].unique().tolist())
    all_districts = sorted(df["district"].unique().tolist())
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    
    panel = dbc.Offcanvas(
        [
            html.Div(
                [
                    html.Label("Crime Categories", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "marginBottom": "6px"}),
                    dcc.Dropdown(
                        id="filter-crime-type",
                        options=[{"label": c, "value": c} for c in all_crimes],
                        multi=True,
                        placeholder="All Crime Categories",
                        className="dash-dropdown"
                    )
                ],
                style={"marginBottom": "20px"}
            ),
            html.Div(
                [
                    html.Label("Police Districts", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "marginBottom": "6px"}),
                    dcc.Dropdown(
                        id="filter-district",
                        options=[{"label": f"District {d}", "value": d} for d in all_districts],
                        multi=True,
                        placeholder="All Police Districts",
                        className="dash-dropdown"
                    )
                ],
                style={"marginBottom": "20px"}
            ),
            html.Div(
                [
                    html.Label("Year Range", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "marginBottom": "6px"}),
                    dcc.RangeSlider(
                        id="filter-year-range",
                        min=min_year,
                        max=max_year,
                        step=1,
                        value=[min_year, max_year],
                        marks={y: {"label": str(y), "style": {"color": "#8A8A8A"}} for y in range(min_year, max_year + 1)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ],
                style={"marginBottom": "24px"}
            ),
            html.Div(
                [
                    html.Label("Arrest Made", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "marginBottom": "6px"}),
                    dbc.RadioItems(
                        id="filter-arrest",
                        options=[
                            {"label": "All Incidents", "value": "ALL"},
                            {"label": "Arrest Made (Yes)", "value": "YES"},
                            {"label": "No Arrest (No)", "value": "NO"}
                        ],
                        value="ALL",
                        inline=True,
                        style={"color": "#8A8A8A", "fontSize": "13px"}
                    )
                ],
                style={"marginBottom": "20px"}
            ),
            html.Div(
                [
                    html.Label("Domestic Incident", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "marginBottom": "6px"}),
                    dbc.RadioItems(
                        id="filter-domestic",
                        options=[
                            {"label": "All Incidents", "value": "ALL"},
                            {"label": "Domestic Only (Yes)", "value": "YES"},
                            {"label": "Non-Domestic (No)", "value": "NO"}
                        ],
                        value="ALL",
                        inline=True,
                        style={"color": "#8A8A8A", "fontSize": "13px"}
                    )
                ],
                style={"marginBottom": "24px"}
            ),
            html.Div(
                [
                    dbc.Button(
                        "Reset All Filters",
                        id="btn-reset-filters",
                        className="btn-cs-secondary",
                        style={"width": "100%", "justifyContent": "center"},
                        n_clicks=0
                    )
                ]
            )
        ],
        id="offcanvas-filters",
        title="Global Analysis Filters",
        is_open=False,
        placement="end"
    )
    return panel

# Page Content Constructors

def build_overview_page():
    """
    Overview page layout: KPI cards, Crime Trend, Donut share, Heatmap, Top Districts table, Insight banner.
    """
    return html.Div(
        [
            # KPI Row
            dbc.Row(
                [
                    dbc.Col(html.Div(id="kpi-total-crimes"), width=12, sm=6, lg=3, className="mb-4"),
                    dbc.Col(html.Div(id="kpi-top-crime-type"), width=12, sm=6, lg=3, className="mb-4"),
                    dbc.Col(html.Div(id="kpi-peak-hour"), width=12, sm=6, lg=3, className="mb-4"),
                    dbc.Col(html.Div(id="kpi-top-district"), width=12, sm=6, lg=3, className="mb-4"),
                ]
            ),
            
            # Trend + Donut Row
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("GROUP TREND BY: ", style={"fontSize": "11px", "color": "#8A8A8A", "fontWeight": "700", "marginRight": "8px"}),
                                        dcc.Dropdown(
                                            id="overview-trend-grouping",
                                            options=[
                                                {"label": "Month", "value": "Month"},
                                                {"label": "Year", "value": "Year"},
                                                {"label": "Day of Week", "value": "Day of Week"},
                                                {"label": "Hour", "value": "Hour"}
                                            ],
                                            value="Month",
                                            clearable=False,
                                            style={"width": "150px"},
                                            className="dash-dropdown"
                                        )
                                    ],
                                    style={"display": "flex", "alignItems": "center", "justifyContent": "flex-end", "marginBottom": "10px"}
                                ),
                                dcc.Loading(dcc.Graph(id="chart-crime-trend", config={"displayModeBar": False}))
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=7
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-crime-donut", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=5
                    )
                ]
            ),
            
            # Heatmap + Top Districts Row
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-hour-day-heatmap", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=7
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Top Districts Ranking", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "16px"}),
                                html.Div(id="overview-top-districts-table"),
                                html.Div(
                                    dcc.Link(
                                        dbc.Button("View All Districts →", className="btn-cs-secondary", style={"width": "100%", "marginTop": "16px"}),
                                        href="/districts"
                                    )
                                )
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=5
                    )
                ]
            ),
            
            # Insight Banner
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-lightbulb-fill", style={"fontSize": "22px", "color": "#FF5A1F", "marginRight": "14px"}),
                            html.Span(id="overview-insight-text", className="insight-text")
                        ],
                        style={"display": "flex", "alignItems": "center"}
                    ),
                    dcc.Link(
                        dbc.Button("Explore on Map →", className="btn-cs-primary"),
                        href="/map"
                    )
                ],
                className="insight-banner mb-4"
            )
        ]
    )

def build_trends_page():
    """
    Trends page layout.
    """
    return html.Div(
        [
            # Multi-line comparison selector row
            html.Div(
                [
                    html.Label("Compare Crime Categories Over Time:", style={"fontWeight": "700", "color": "#F2F2F2", "marginBottom": "8px"}),
                    dcc.Dropdown(
                        id="trends-multi-select",
                        multi=True,
                        placeholder="Select 2–4 crime categories to compare...",
                        className="dash-dropdown",
                        style={"marginBottom": "16px"}
                    ),
                    dcc.Loading(dcc.Graph(id="chart-trends-multi-line", config={"displayModeBar": False}))
                ],
                className="cs-card mb-4"
            ),
            
            # 2x2 Grid of Seasonality / Hourly / Weekday
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-seasonality", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, md=6
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-hourly-profile", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, md=6
                    )
                ]
            )
        ]
    )

def build_map_page():
    """
    Map page layout: interactive map + top community areas side panel.
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("MAP VIEW: ", style={"fontSize": "11px", "color": "#8A8A8A", "fontWeight": "700", "marginRight": "8px"}),
                                        dbc.RadioItems(
                                            id="map-mode-toggle",
                                            options=[
                                                {"label": "Heatmap", "value": "Heatmap"},
                                                {"label": "Points (Sampled)", "value": "Points"},
                                                {"label": "District Bubbles", "value": "District Bubbles"}
                                            ],
                                            value="Heatmap",
                                            inline=True,
                                            style={"color": "#8A8A8A", "fontSize": "13px"}
                                        )
                                    ],
                                    style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}
                                ),
                                dcc.Loading(dcc.Graph(id="chart-chicago-map", config={"displayModeBar": False}))
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=8
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-top-community-areas", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=4
                    )
                ]
            )
        ]
    )

def build_districts_page():
    """
    Districts page layout.
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-districts-bar", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=7
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-top-15-ca", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=5
                    )
                ]
            ),
            
            # District Metrics Table
            html.Div(
                [
                    html.H4("District Detailed Breakdown", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "16px"}),
                    html.Div(id="districts-full-table")
                ],
                className="cs-card mb-4"
            )
        ]
    )

def build_prediction_page(df):
    """
    Prediction page layout.
    """
    all_districts = sorted(df["district"].unique().tolist())
    all_ca = sorted([ca for ca in df["community_area"].unique().tolist() if ca > 0])
    
    return html.Div(
        [
            dbc.Row(
                [
                    # Input Form Column
                    dbc.Col(
                        html.Div(
                            [
                                dbc.Button(
                                    [html.I(className="bi bi-clock-history", style={"marginRight": "8px"}), "Sync Inputs with Current Chicago Time"],
                                    id="btn-sync-current-time",
                                    className="btn-cs-secondary mb-3",
                                    style={"width": "100%", "justifyContent": "center", "marginBottom": "16px"},
                                    n_clicks=0
                                ),
                                html.H4("Input Spatio-Temporal Parameters", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "20px"}),
                                
                                html.Div(
                                    [
                                        html.Label("Model Selector", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2"}),
                                        dcc.Dropdown(
                                            id="pred-model-select",
                                            options=[
                                                {"label": "Random Forest Classifier (Recommended)", "value": "RandomForest"},
                                                {"label": "Logistic Regression Classifier", "value": "LogisticRegression"},
                                                {"label": "Decision Tree Classifier", "value": "DecisionTree"}
                                            ],
                                            value="RandomForest",
                                            clearable=False,
                                            className="dash-dropdown"
                                        )
                                    ],
                                    style={"marginBottom": "16px"}
                                ),
                                
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Hour of Day (0–23, Chicago Time - CT)", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2", "margin": "0"}),
                                                html.Span(id="pred-hour-badge", children="18:00", style={"color": "#FF5A1F", "fontWeight": "800", "fontSize": "14px", "backgroundColor": "#0B0B0B", "padding": "2px 8px", "borderRadius": "6px", "border": "1px solid #262626"})
                                            ],
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "8px"}
                                        ),
                                        dcc.Slider(
                                            id="pred-hour-slider",
                                            min=0, max=23, step=1, value=18,
                                            marks={h: f"{h:02d}:00" for h in range(0, 24, 4)}
                                        )
                                    ],
                                    style={"marginBottom": "20px"}
                                ),
                                
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label("Day of Week", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2"}),
                                                dcc.Dropdown(
                                                    id="pred-day-dropdown",
                                                    options=[
                                                        {"label": "Monday", "value": 0},
                                                        {"label": "Tuesday", "value": 1},
                                                        {"label": "Wednesday", "value": 2},
                                                        {"label": "Thursday", "value": 3},
                                                        {"label": "Friday", "value": 4},
                                                        {"label": "Saturday", "value": 5},
                                                        {"label": "Sunday", "value": 6}
                                                    ],
                                                    value=4,
                                                    clearable=False,
                                                    className="dash-dropdown"
                                                )
                                            ],
                                            width=6
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Month", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2"}),
                                                dcc.Dropdown(
                                                    id="pred-month-dropdown",
                                                    options=[
                                                        {"label": "January", "value": 1},
                                                        {"label": "February", "value": 2},
                                                        {"label": "March", "value": 3},
                                                        {"label": "April", "value": 4},
                                                        {"label": "May", "value": 5},
                                                        {"label": "June", "value": 6},
                                                        {"label": "July", "value": 7},
                                                        {"label": "August", "value": 8},
                                                        {"label": "September", "value": 9},
                                                        {"label": "October", "value": 10},
                                                        {"label": "November", "value": 11},
                                                        {"label": "December", "value": 12}
                                                    ],
                                                    value=7,
                                                    clearable=False,
                                                    className="dash-dropdown"
                                                )
                                            ],
                                            width=6
                                        )
                                    ],
                                    style={"marginBottom": "16px"}
                                ),
                                
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label("Police District", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2"}),
                                                dcc.Dropdown(
                                                    id="pred-district-dropdown",
                                                    options=[{"label": f"District {d}", "value": d} for d in all_districts],
                                                    value=all_districts[0] if all_districts else 1,
                                                    clearable=False,
                                                    className="dash-dropdown"
                                                )
                                            ],
                                            width=6
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Community Area (Optional)", style={"fontWeight": "600", "fontSize": "13px", "color": "#F2F2F2"}),
                                                dcc.Dropdown(
                                                    id="pred-ca-dropdown",
                                                    options=[{"label": f"Area {ca}", "value": ca} for ca in all_ca],
                                                    value=all_ca[0] if all_ca else 1,
                                                    clearable=True,
                                                    className="dash-dropdown"
                                                )
                                            ],
                                            width=6
                                        )
                                    ],
                                    style={"marginBottom": "24px"}
                                ),
                                
                                dbc.Button(
                                    [html.I(className="bi bi-lightning-charge-fill", style={"marginRight": "8px"}), "Estimate Crime Category"],
                                    id="btn-run-prediction",
                                    className="btn-cs-primary",
                                    style={"width": "100%", "justifyContent": "center"},
                                    n_clicks=0
                                )
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=5
                    ),
                    
                    # Output Column
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Prediction Output", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "20px"}),
                                html.Div(id="pred-output-container"),
                                html.Div(
                                    [
                                        html.I(className="bi bi-info-circle", style={"marginRight": "8px", "color": "#FFC23D"}),
                                        html.Span(
                                            "This is a model estimate based on historical patterns, not a certainty.",
                                            style={"fontSize": "13px", "color": "#8A8A8A", "fontStyle": "italic"}
                                        )
                                    ],
                                    style={"marginTop": "24px", "padding": "12px", "backgroundColor": "#0B0B0B", "borderRadius": "8px", "border": "1px solid #262626"}
                                )
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=7
                    )
                ]
            )
        ]
    )

def build_model_comparison_page():
    """
    Model Comparison page layout.
    """
    return html.Div(
        [
            # Metric Summary Table Card
            html.Div(
                [
                    html.H4("Supervised Classification Models Benchmark", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "16px"}),
                    html.Div(id="ml-metrics-table-container")
                ],
                className="cs-card mb-4"
            ),
            
            # Confusion Matrix + Feature Importance Row
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span("MODEL CONFUSION MATRIX: ", style={"fontSize": "11px", "color": "#8A8A8A", "fontWeight": "700", "marginRight": "8px"}),
                                        dcc.Dropdown(
                                            id="cm-model-select",
                                            options=[
                                                {"label": "Random Forest", "value": "RandomForest"},
                                                {"label": "Logistic Regression", "value": "LogisticRegression"},
                                                {"label": "Decision Tree", "value": "DecisionTree"}
                                            ],
                                            value="RandomForest",
                                            clearable=False,
                                            style={"width": "180px"},
                                            className="dash-dropdown"
                                        )
                                    ],
                                    style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}
                                ),
                                dcc.Loading(dcc.Graph(id="chart-confusion-matrix", config={"displayModeBar": False}))
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=7
                    ),
                    dbc.Col(
                        html.Div(
                            dcc.Loading(dcc.Graph(id="chart-feature-importance", config={"displayModeBar": False})),
                            className="cs-card mb-4"
                        ),
                        width=12, lg=5
                    )
                ]
            ),
            
            # Analytical Conclusions & Methodological Note
            html.Div(
                [
                    html.H4("Model Evaluation Insights & Methodological Context", style={"fontSize": "16px", "fontWeight": "700", "color": "#FF5A1F", "marginBottom": "12px"}),
                    html.P(
                        "1. Performance Ranking: The Random Forest Classifier outperforms Logistic Regression and Decision Tree across Weighted F1-Score and Accuracy. Its non-linear ensemble trees effectively capture spatial interaction boundaries between districts and peak hourly crime cycles.",
                        style={"color": "#F2F2F2", "fontSize": "14px", "marginBottom": "8px"}
                    ),
                    html.P(
                        "2. Predictive Limits Note: Predicting specific crime categories solely from spatio-temporal features (hour, day, district, location coordinates) is an inherently difficult task, so moderate predictive accuracy is expected due to high variance and overlapping spatial-temporal patterns across crime types.",
                        style={"color": "#8A8A8A", "fontSize": "13px", "fontStyle": "italic", "marginTop": "12px"}
                    )
                ],
                className="cs-card mb-4"
            )
        ]
    )

def build_about_page(summary_stats):
    """
    About & Data page layout.
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Dataset Source & Citation", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "12px"}),
                                html.P(
                                    "Source: City of Chicago Data Portal — 'Crimes - 2001 to Present' (Dataset ID: ijzp-q8t2). Published by the Chicago Police Department's Citizen Law Enforcement Analysis and Reporting (CLEAR) system.",
                                    style={"color": "#8A8A8A", "fontSize": "14px"}
                                ),
                                html.H5("Timezone Standardization", style={"fontSize": "14px", "fontWeight": "700", "color": "#FF5A1F", "marginTop": "16px", "marginBottom": "6px"}),
                                html.P(
                                    "All crime incident timestamps, hourly distributions, peak crime windows, and spatio-temporal ML features are recorded and evaluated in Chicago Local Time (Central Standard Time / Central Daylight Time - US/Central) as reported by the Chicago Police Department CLEAR system.",
                                    style={"color": "#8A8A8A", "fontSize": "13px"}
                                ),
                                html.H5("Disclaimer", style={"fontSize": "14px", "fontWeight": "700", "color": "#FFC23D", "marginTop": "16px", "marginBottom": "6px"}),
                                html.P(
                                    "These records are preliminary, unverified reports of crime incidents subject to change upon further police investigation. Geographic location coordinates are anonymized at the block level for privacy compliance.",
                                    style={"color": "#8A8A8A", "fontSize": "13px"}
                                )
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=6
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H4("Data Preprocessing Summary", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "12px"}),
                                html.Ul(
                                    [
                                        html.Li(f"Raw Row Count: {summary_stats.get('initial_rows', 0):,}"),
                                        html.Li(f"Cleaned Row Count: {summary_stats.get('processed_rows', 0):,}"),
                                        html.Li(f"Excluded Invalid Rows: {summary_stats.get('removed_rows', 0):,}"),
                                        html.Li(f"Coverage Period: {summary_stats.get('date_min', '')} to {summary_stats.get('date_max', '')}"),
                                        html.Li("Grouping: Crime categories outside top 12 mapped to 'OTHER'.")
                                    ],
                                    style={"color": "#8A8A8A", "fontSize": "14px"}
                                ),
                                dbc.Button(
                                    [html.I(className="bi bi-download", style={"marginRight": "8px"}), "Download Filtered Data as CSV"],
                                    id="btn-download-csv",
                                    className="btn-cs-primary",
                                    style={"marginTop": "12px"},
                                    n_clicks=0
                                ),
                                dcc.Download(id="download-dataframe-csv")
                            ],
                            className="cs-card mb-4"
                        ),
                        width=12, lg=6
                    )
                ]
            ),
            
            # Data Dictionary & Tech Stack Row
            html.Div(
                [
                    html.H4("Column Dictionary", style={"fontSize": "16px", "fontWeight": "700", "color": "#F2F2F2", "marginBottom": "16px"}),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr([
                                    html.Th("Column"),
                                    html.Th("Data Type"),
                                    html.Th("Description")
                                ])
                            ),
                            html.Tbody([
                                html.Tr([html.Td("date"), html.Td("datetime64"), html.Td("Timestamp when the crime incident occurred.")]),
                                html.Tr([html.Td("primary_type"), html.Td("string"), html.Td("Primary classification category assigned by CPD.")]),
                                html.Tr([html.Td("primary_type_clean"), html.Td("string"), html.Td("Cleaned category (Top 12 categories + OTHER).")]),
                                html.Tr([html.Td("description"), html.Td("string"), html.Td("Sub-classification detail of the incident.")]),
                                html.Tr([html.Td("location_description"), html.Td("string"), html.Td("Location type (e.g. STREET, RESIDENCE).")]),
                                html.Tr([html.Td("district"), html.Td("int32"), html.Td("Chicago Police Department district code (1–25).")]),
                                html.Tr([html.Td("community_area"), html.Td("int32"), html.Td("Chicago official community area code (1–77).")]),
                                html.Tr([html.Td("arrest"), html.Td("boolean"), html.Td("Indicates whether an arrest was executed.")]),
                                html.Tr([html.Td("domestic"), html.Td("boolean"), html.Td("Indicates whether the incident is domestic-related.")]),
                                html.Tr([html.Td("latitude / longitude"), html.Td("float64"), html.Td("Anonymized geographic coordinates.")])
                            ])
                        ],
                        className="cs-table"
                    )
                ],
                className="cs-card mb-4"
            )
        ]
    )
