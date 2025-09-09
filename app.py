# app.py  — Offline "Live" Airline Satisfaction Dashboard (Dash)
# Run:  python app.py
# Files expected in the SAME folder: train.csv

import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

# ============= 1) LOAD + ENRICH DATA (OFFLINE) =============
# Read your CSV (same folder as app.py)
df = pd.read_csv("train.csv")

# --- Normalize satisfaction labels to just 2 buckets ---
def normalize_satisfaction(val):
    if pd.isna(val):
        return "unknown"
    s = str(val).strip().lower()
    if "satisf" in s and "neutral" not in s and "diss" not in s:
        return "satisfied"
    if "neutral" in s or "diss" in s:
        return "neutral or dissatisfied"
    # fallback: anything else → bucket as neutral/diss
    return "neutral or dissatisfied"

df["satisfaction_norm"] = df["satisfaction"].apply(normalize_satisfaction)

# --- Simulate Airline names (expand/curate as you like) ---
airlines = [
    "Air India", "IndiGo", "SpiceJet", "Vistara", "Akasa Air", "Go First",
    "HAL", "Boeing", "Airbus", "Embraer", "Dassault Aviation", "Textron Aviation"
]
np.random.seed(42)  # keep visuals deterministic between runs
df["Airline"] = np.random.choice(airlines, size=len(df))

# --- Simulate Flight Date over ~20 years (2006–2025) ---
start_date = pd.Timestamp("2006-01-01")
end_date   = pd.Timestamp("2025-08-01")  # close to "today" feel
rand_seconds = np.random.randint(
    start_date.value // 10**9,
    end_date.value   // 10**9,
    size=len(df)
)
df["Flight Date"] = pd.to_datetime(rand_seconds, unit="s")
df["Year"] = df["Flight Date"].dt.year

# Some columns are optional in your CSV; guard missing
for col in ["Class", "Type of Travel", "Flight Distance", "Age"]:
    if col not in df.columns:
        df[col] = np.nan

# ============= 2) DASH APP SETUP =============
app = dash.Dash(__name__)
app.title = "Offline Live Airline Satisfaction"

# Slider bounds
year_min = int(df["Year"].min())
year_max = int(df["Year"].max())

def kpi_card(title, value, sub=None):
    return html.Div([
        html.Div(title, className="text-sm text-gray-500"),
        html.Div(value, className="text-2xl font-semibold"),
        html.Div(sub or "", className="text-xs text-gray-400")
    ], style={
        "padding":"16px","borderRadius":"16px","boxShadow":"0 8px 20px rgba(0,0,0,0.06)",
        "background":"white","minWidth":"200px"
    })

# ============= 3) LAYOUT =============
app.layout = html.Div([
    html.Div("Airline Customer Satisfaction — Offline Live Dashboard",
             style={"textAlign":"center","fontSize":"26px","fontWeight":"700","margin":"18px 0"}),

    # Controls Row
    html.Div([
        html.Div([
            html.Label("Airlines"),
            dcc.Dropdown(
                id="airline-dd",
                options=[{"label": a, "value": a} for a in sorted(df["Airline"].unique())],
                value=sorted(df["Airline"].unique())[:6],  # preselect a handful
                multi=True
            ),
        ], style={"width":"32%","display":"inline-block","verticalAlign":"top","paddingRight":"12px"}),

        html.Div([
            html.Label("Class"),
            dcc.Dropdown(
                id="class-dd",
                options=[{"label": c, "value": c} for c in sorted(df["Class"].dropna().unique())],
                value=sorted(df["Class"].dropna().unique()),
                multi=True
            ),
        ], style={"width":"32%","display":"inline-block","verticalAlign":"top","paddingRight":"12px"}),

        html.Div([
            html.Label("Type of Travel"),
            dcc.Dropdown(
                id="travel-dd",
                options=[{"label": t, "value": t} for t in sorted(df["Type of Travel"].dropna().unique())],
                value=sorted(df["Type of Travel"].dropna().unique()),
                multi=True
            ),
        ], style={"width":"32%","display":"inline-block","verticalAlign":"top"}),
    ], style={"width":"92%","margin":"0 auto 12px"}),

    # Live Controls
    html.Div([
        html.Div([
            html.Button("⏯ Play / Pause", id="play-btn",
                        style={"padding":"10px 14px","borderRadius":"12px","border":"1px solid #ddd","cursor":"pointer"}),
            dcc.Dropdown(
                id="speed-dd",
                options=[
                    {"label":"Slow (2s/frame)", "value":2000},
                    {"label":"Normal (1s/frame)", "value":1000},
                    {"label":"Fast (0.5s/frame)", "value":500},
                ],
                value=1000,
                clearable=False,
                style={"width":"200px","display":"inline-block","marginLeft":"12px","verticalAlign":"middle"}
            ),
        ], style={"display":"inline-block"}),

        html.Div(id="current-year-label", style={"display":"inline-block","marginLeft":"20px","fontWeight":"600"}),

    ], style={"width":"92%","margin":"10px auto"}),

    dcc.Slider(
        id="year-slider", min=year_min, max=year_max, value=year_min,
        marks={y:str(y) for y in range(year_min, year_max+1, max(1,(year_max-year_min)//10 or 1))},
        step=1, tooltip={"placement":"bottom","always_visible":True}
    ),

    # KPIs
    html.Div(id="kpi-row", style={"display":"flex","gap":"16px","flexWrap":"wrap","width":"92%","margin":"18px auto"}),

    # Graphs
    html.Div([
        dcc.Graph(id="facet-graph"),
    ], style={"width":"96%","margin":"8px auto"}),

    html.Div([
        html.Div([dcc.Graph(id="top-airlines-graph")], style={"width":"49%","display":"inline-block","verticalAlign":"top"}),
        html.Div([dcc.Graph(id="yearly-trend-graph")],  style={"width":"49%","display":"inline-block","verticalAlign":"top"}),
    ], style={"width":"96%","margin":"8px auto"}),

    html.Div([
        dcc.Graph(id="pie-graph")
    ], style={"width":"60%","margin":"12px auto"}),

    # Hidden “engine” parts
    dcc.Interval(id="tick", interval=1000, n_intervals=0, disabled=False),  # default = playing
    dcc.Store(id="play-state", data=True),    # True=playing, False=paused
], style={"fontFamily":"Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
          "background":"#f7f7fb","minHeight":"100vh"})


# ============= 4) PLAY/PAUSE & SPEED HANDLERS =============
@app.callback(
    Output("play-state", "data"),
    Input("play-btn", "n_clicks"),
    State("play-state", "data"),
    prevent_initial_call=True
)
def toggle_play(n_clicks, is_playing):
    # toggle True/False
    return not is_playing

@app.callback(
    Output("tick", "interval"),
    Input("speed-dd", "value"),
)
def set_speed(interval_ms):
    return interval_ms


# ============= 5) MAIN UPDATE LOOP =============
@app.callback(
    [
        Output("year-slider", "value"),
        Output("current-year-label", "children"),
        Output("kpi-row", "children"),
        Output("facet-graph", "figure"),
        Output("top-airlines-graph", "figure"),
        Output("yearly-trend-graph", "figure"),
        Output("pie-graph", "figure"),
        Output("tick", "disabled"),
    ],
    [
        Input("tick", "n_intervals"),
        Input("year-slider", "value"),
        Input("airline-dd", "value"),
        Input("class-dd", "value"),
        Input("travel-dd", "value"),
        Input("play-state", "data"),
    ],
)
def render(n, slider_year, airlines_sel, class_sel, travel_sel, is_playing):
    # compute current "live" year
    # when playing -> advance with n_intervals; when paused -> stick to slider year
    if is_playing:
        # loop years smoothly
        span = (year_max - year_min + 1)
        current_year = year_min + (n % span)
        slider_val = current_year
    else:
        current_year = slider_year
        slider_val = slider_year

    # filter by controls + current year (use <= to build history feel)
    mask = (
        df["Airline"].isin(airlines_sel) &
        (df["Class"].isin(class_sel) if class_sel else True) &
        (df["Type of Travel"].isin(travel_sel) if travel_sel else True) &
        (df["Year"] <= current_year)
    )
    d = df.loc[mask].copy()

    # ---- KPIs ----
    total_records = len(d)
    sat_counts = d["satisfaction_norm"].value_counts()
    sat = int(sat_counts.get("satisfied", 0))
    diss = int(sat_counts.get("neutral or dissatisfied", 0))
    sat_pct = (sat / max(1, sat + diss)) * 100
    avg_delay_dep = float(d.get("Departure Delay in Minutes", pd.Series(dtype=float)).mean()) if "Departure Delay in Minutes" in d else np.nan
    avg_delay_arr = float(d.get("Arrival Delay in Minutes", pd.Series(dtype=float)).mean()) if "Arrival Delay in Minutes" in d else np.nan

    kpis = [
        kpi_card("Total Records (≤ year)", f"{total_records:,}"),
        kpi_card("Satisfied %", f"{sat_pct:0.1f}%", f"{sat:,} sat / {diss:,} unsat"),
        kpi_card("Avg Dep Delay (min)", "-" if np.isnan(avg_delay_dep) else f"{avg_delay_dep:0.1f}"),
        kpi_card("Avg Arr Delay (min)", "-" if np.isnan(avg_delay_arr) else f"{avg_delay_arr:0.1f}"),
        kpi_card("Current Year", str(current_year)),
    ]

    # ---- Facet: Satisfaction per Class by Airline (only current year slice for clarity) ----
    d_year = d[d["Year"] == current_year]
    if d_year.empty:
        d_year = d.tail(0)  # keep schema

    facet_fig = px.histogram(
        d_year, x="Class", color="satisfaction_norm", facet_col="Airline",
        barmode="group",
        category_orders={"satisfaction_norm": ["satisfied", "neutral or dissatisfied"]},
        labels={"satisfaction_norm":"Satisfaction"},
        title=f"Satisfaction per Class — Airline Panels (Year {current_year})"
    )
    facet_fig.update_layout(margin=dict(l=20,r=20,t=60,b=20))

    # ---- Top Airlines (stacked) over history ≤ current year ----
    grp = d.groupby(["Airline","satisfaction_norm"]).size().unstack(fill_value=0)
    if "satisfied" not in grp.columns: grp["satisfied"] = 0
    if "neutral or dissatisfied" not in grp.columns: grp["neutral or dissatisfied"] = 0
    grp = grp.assign(Total=grp["satisfied"] + grp["neutral or dissatisfied"]).sort_values("Total", ascending=False)
    top_fig = px.bar(
        grp.reset_index(),
        x="Airline",
        y=["satisfied","neutral or dissatisfied"],
        barmode="stack",
        title=f"Top Airlines by Satisfaction (≤ {current_year})",
        labels={"value":"Count"}
    )
    top_fig.update_layout(margin=dict(l=20,r=20,t=60,b=20), legend_title_text="")

    # ---- Yearly Trend (history ≤ current year) ----
    year_trend = d.groupby("Year")["satisfaction_norm"].value_counts().unstack(fill_value=0).reset_index()
    if year_trend.empty:
        year_trend = pd.DataFrame({"Year":[current_year], "satisfied":[0], "neutral or dissatisfied":[0]})
    trend_fig = go.Figure()
    if "satisfied" in year_trend:
        trend_fig.add_trace(go.Scatter(x=year_trend["Year"], y=year_trend["satisfied"], mode="lines+markers", name="satisfied"))
    if "neutral or dissatisfied" in year_trend:
        trend_fig.add_trace(go.Scatter(x=year_trend["Year"], y=year_trend["neutral or dissatisfied"], mode="lines+markers", name="neutral or dissatisfied"))
    trend_fig.update_layout(
        title=f"Yearly Satisfaction Trend (≤ {current_year})",
        xaxis_title="Year", yaxis_title="Count",
        margin=dict(l=20,r=20,t=60,b=20)
    )

    # ---- Pie (current year snapshot) ----
    pie_counts = d_year["satisfaction_norm"].value_counts()
    pie_fig = px.pie(
        names=pie_counts.index, values=pie_counts.values,
        hole=0.3, title=f"Satisfaction Split — Year {current_year}"
    )

    # disable interval only if paused
    interval_disabled = not is_playing

    return (
        slider_val,
        f"Current Year: {current_year}",
        kpis,
        facet_fig,
        top_fig,
        trend_fig,
        pie_fig,
        interval_disabled
    )


# ============= 6) BOOT =============
if __name__ == "__main__":
    app.run(debug=True, port=8051)
