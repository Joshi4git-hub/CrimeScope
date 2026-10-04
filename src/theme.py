import plotly.io as pio
import plotly.graph_objects as go

# Color Palette Constants
COLOR_BG = "#0B0B0B"
COLOR_CARD = "#141414"
COLOR_BORDER = "#262626"
COLOR_PRIMARY = "#FF5A1F"       # Orange
COLOR_SECONDARY = "#FF9A3D"     # Amber
COLOR_TERTIARY = "#FFC23D"      # Yellow
COLOR_TEXT_MAIN = "#F2F2F2"
COLOR_TEXT_MUTED = "#8A8A8A"
COLOR_GRID = "#222222"

COLORWAY = [
    "#FF5A1F", "#FF9A3D", "#FFC23D", "#00E676",
    "#29B6F6", "#E040FB", "#FF1744", "#7C4DFF",
    "#FF80AB", "#00E5FF", "#B2FF59", "#FFD700"
]

ORANGE_YELLOW_SCALE = [
    [0.0, "#FF5A1F"],
    [0.5, "#FF9A3D"],
    [1.0, "#FFC23D"]
]

def register_crimescope_template():
    """
    Registers the custom CrimeScope dark theme template for Plotly.
    """
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color=COLOR_TEXT_MAIN,
            size=12
        ),
        title=dict(
            font=dict(color=COLOR_TEXT_MAIN, size=16, family="Inter"),
            x=0.01,
            xanchor="left"
        ),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
            title=dict(font=dict(color=COLOR_TEXT_MAIN, size=12), standoff=18),
            showline=True,
            linecolor=COLOR_BORDER
        ),
        yaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
            title=dict(font=dict(color=COLOR_TEXT_MAIN, size=12)),
            showline=True,
            linecolor=COLOR_BORDER
        ),
        colorway=COLORWAY,
        colorscale=dict(
            sequential=ORANGE_YELLOW_SCALE,
            sequentialminus=ORANGE_YELLOW_SCALE,
            diverging=ORANGE_YELLOW_SCALE
        ),
        legend=dict(
            font=dict(color=COLOR_TEXT_MAIN, size=11),
            bgcolor="rgba(20,20,20,0.7)",
            bordercolor=COLOR_BORDER,
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor=COLOR_CARD,
            bordercolor=COLOR_PRIMARY,
            font=dict(color=COLOR_TEXT_MAIN, family="Inter", size=12)
        ),
        margin=dict(l=40, r=30, t=40, b=65)
    )
    
    pio.templates["crimescope_dark"] = template
    pio.templates.default = "crimescope_dark"

# Auto-register on import
register_crimescope_template()
