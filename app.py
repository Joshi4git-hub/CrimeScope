import os
import sys
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_prep import get_processed_data
from src.layout import build_sidebar, build_top_header, build_offcanvas_filters
from src.callbacks import register_callbacks

# Bootstrap Icons & Custom CSS
BOOTSTRAP_ICONS = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
GOOGLE_FONTS = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, BOOTSTRAP_ICONS, GOOGLE_FONTS],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

app.title = "CrimeScope — Chicago Crime Analytics & Prediction"
server = app.server

# Load cached dataset
df = get_processed_data()

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="global-filter-store"),
        dcc.Interval(id="chicago-clock-interval", interval=1000, n_intervals=0),
        
        # Offcanvas filter panel container
        build_offcanvas_filters(df),
        
        html.Div(
            [
                html.Div(id="sidebar-container"),
                html.Div(
                    [
                        build_top_header(),
                        html.Div(id="page-content")
                    ],
                    className="main-content"
                )
            ],
            className="app-container"
        )
    ]
)

register_callbacks(app)

if __name__ == "__main__":
    print("Starting CrimeScope dashboard on http://127.0.0.1:8050")
    app.run(debug=False, host="127.0.0.1", port=8050)
