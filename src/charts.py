"""Gráficos Plotly con una apariencia consistente."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEAL = "#138A72"
NAVY = "#173F5F"
GOLD = "#E0A458"
PALETTE = ["#138A72", "#173F5F", "#E0A458", "#C8553D", "#6C5CE7", "#2D98DA"]


def _finish(figure: go.Figure, *, height: int = 430) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=55, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#17342F"),
        hoverlabel=dict(bgcolor="#17342F", font_color="white"),
        legend_title_text="",
    )
    figure.update_xaxes(showgrid=False, linecolor="rgba(23,52,47,.16)")
    figure.update_yaxes(gridcolor="rgba(23,52,47,.10)", zeroline=False)
    return figure


def trend_chart(frame: pd.DataFrame, indicator: str, unit: str) -> go.Figure:
    figure = px.line(
        frame,
        x="year",
        y="value",
        color="country",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"year": "Año", "value": unit, "country": "País"},
        title=f"Evolución de {indicator.lower()}",
    )
    figure.update_traces(line_width=2.6, marker_size=5)
    figure.update_layout(hovermode="x unified")
    return _finish(figure, height=500)


def ranking_chart(frame: pd.DataFrame, year: int, indicator: str, unit: str) -> go.Figure:
    snapshot = frame.loc[frame["year"].eq(year)].sort_values("value", ascending=True)
    figure = px.bar(
        snapshot,
        x="value",
        y="country",
        orientation="h",
        text_auto=".3s",
        color_discrete_sequence=[TEAL],
        labels={"value": unit, "country": ""},
        title=f"Ranking {year}: {indicator.lower()}",
    )
    figure.update_traces(textposition="outside", cliponaxis=False)
    return _finish(figure)


def map_chart(frame: pd.DataFrame, year: int, indicator: str, unit: str) -> go.Figure:
    snapshot = frame.loc[frame["year"].eq(year)]
    figure = px.choropleth(
        snapshot,
        locations="country_code",
        color="value",
        hover_name="country",
        hover_data={"country_code": False, "value": ":,.2f"},
        color_continuous_scale=["#DCEFEA", "#64B6A4", TEAL, NAVY],
        labels={"value": unit},
        title=f"Distribución regional en {year}",
    )
    figure.update_geos(
        scope="south america",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(23,52,47,.25)",
        bgcolor="rgba(0,0,0,0)",
    )
    figure.update_layout(coloraxis_colorbar=dict(title=unit, thickness=12))
    return _finish(figure)


def development_chart(snapshot: pd.DataFrame) -> go.Figure:
    year = int(snapshot["year"].iloc[0])
    figure = px.scatter(
        snapshot,
        x="NY.GDP.PCAP.CD",
        y="SP.DYN.LE00.IN",
        size="SP.POP.TOTL",
        color="IT.NET.USER.ZS",
        text="country",
        size_max=65,
        color_continuous_scale=["#DCEFEA", TEAL, NAVY],
        labels={
            "NY.GDP.PCAP.CD": "PIB per cápita (US$)",
            "SP.DYN.LE00.IN": "Esperanza de vida (años)",
            "SP.POP.TOTL": "Población",
            "IT.NET.USER.ZS": "Uso de Internet (%)",
        },
        title=f"Desarrollo, conectividad y población ({year})",
        hover_name="country",
    )
    figure.update_traces(textposition="top center", marker_line_width=1, marker_line_color="white")
    return _finish(figure, height=540)
