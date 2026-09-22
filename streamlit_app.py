"""Pulso de Sudamérica: dashboard interactivo con datos del Banco Mundial."""

import pandas as pd
import streamlit as st

from src.analytics import build_summary, development_snapshot
from src.charts import development_chart, map_chart, ranking_chart, trend_chart
from src.data import INDICATORS, indicator_frame, load_data

st.set_page_config(
    page_title="Pulso de Sudamérica",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f3f8f6 0%, #ffffff 34%); }
    [data-testid="stMetric"] {
        background: rgba(255,255,255,.82);
        border: 1px solid rgba(19,138,114,.15);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(23,63,95,.06);
    }
    [data-testid="stMetricLabel"] { color: #52706a; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(19,138,114,.12); }
    div[data-testid="stDownloadButton"] button { width: 100%; }
    .hero-kicker { color:#138a72; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    .hero-copy { color:#52706a; max-width:780px; font-size:1.06rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data()


def format_value(value: float, indicator: str) -> str:
    if indicator == "PIB per cápita":
        return f"US$ {value:,.0f}"
    if indicator == "Esperanza de vida":
        return f"{value:.1f} años"
    if indicator == "Uso de Internet":
        return f"{value:.1f}%"
    if indicator == "Población":
        return f"{value / 1_000_000:.1f} M"
    return f"{value:,.2f}"


data = get_data()
all_countries = sorted(data["country"].unique())
all_years = sorted(data["year"].unique())

with st.sidebar:
    st.header("Explorar datos")
    selected_indicator = st.selectbox("Indicador", list(INDICATORS), index=0)
    selected_countries = st.multiselect(
        "Países",
        all_countries,
        default=["Perú", "Chile", "Colombia", "Argentina", "Brasil"],
        max_selections=8,
    )
    selected_years = st.slider(
        "Periodo",
        min_value=min(all_years),
        max_value=max(all_years),
        value=(2005, max(all_years)),
    )
    st.caption("Fuente: World Development Indicators, Banco Mundial.")

st.markdown('<p class="hero-kicker">World Development Indicators</p>', unsafe_allow_html=True)
st.title("Pulso de Sudamérica")
st.markdown(
    '<p class="hero-copy">Compara crecimiento, bienestar, conectividad y población mediante '
    "indicadores oficiales. Ajusta los filtros y descubre cómo cambió la región desde el año "
    "2000.</p>",
    unsafe_allow_html=True,
)

if not selected_countries:
    st.warning("Selecciona al menos un país para construir el análisis.")
    st.stop()

metric_data = indicator_frame(data, selected_indicator)
filtered = metric_data.loc[
    metric_data["country"].isin(selected_countries)
    & metric_data["year"].between(*selected_years)
].copy()

if filtered.empty:
    st.warning("No hay observaciones para los filtros seleccionados.")
    st.stop()

summary = build_summary(filtered, len(selected_countries))
meta = INDICATORS[selected_indicator]
delta = (
    None
    if summary.change_pct is None
    else f"{summary.change_pct:+.1f}% desde {summary.first_year}"
)

metric_1, metric_2 = st.columns(2)
metric_1.metric(
    f"Mediana regional · {summary.year}",
    format_value(summary.median, selected_indicator),
    delta,
)
metric_2.metric(
    "País líder",
    summary.leader,
    format_value(summary.leader_value, selected_indicator),
)
metric_3, metric_4 = st.columns(2)
metric_3.metric("Países comparados", summary.countries)
metric_4.metric("Último año comparable", summary.year)

overview_tab, trend_tab, relation_tab, data_tab = st.tabs(
    ["Panorama", "Evolución", "Relación de desarrollo", "Datos"]
)

with overview_tab:
    map_column, ranking_column = st.columns([1.1, 1])
    with map_column:
        st.plotly_chart(
            map_chart(filtered, summary.year, selected_indicator, meta["unit"]),
            width="stretch",
            config={"displayModeBar": False},
        )
    with ranking_column:
        st.plotly_chart(
            ranking_chart(filtered, summary.year, selected_indicator, meta["unit"]),
            width="stretch",
            config={"displayModeBar": False},
        )
    st.info(meta["description"], icon="💡")

with trend_tab:
    st.plotly_chart(
        trend_chart(filtered, selected_indicator, meta["unit"]),
        width="stretch",
        config={"displayModeBar": False},
    )

with relation_tab:
    relation = development_snapshot(data, selected_countries, selected_years[1])
    if relation.empty:
        st.info("No hay un año con los cuatro indicadores disponibles para esta selección.")
    else:
        st.plotly_chart(
            development_chart(relation),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.caption(
            "El tamaño representa la población y el color el porcentaje de personas que "
            "usan Internet."
        )

with data_tab:
    display = filtered[["country", "country_code", "year", "indicator", "unit", "value"]].copy()
    display.columns = ["País", "Código", "Año", "Indicador", "Unidad", "Valor"]
    st.dataframe(display, width="stretch", hide_index=True)
    st.download_button(
        "Descargar selección en CSV",
        data=display.to_csv(index=False).encode("utf-8"),
        file_name="pulso_sudamerica.csv",
        mime="text/csv",
    )

with st.expander("Metodología y fuente"):
    st.markdown(
        "Los datos provienen de la API pública de World Development Indicators del Banco Mundial. "
        "El dashboard conserva únicamente observaciones publicadas y calcula la mediana sobre los "
        "países seleccionados. Para comparaciones transversales utiliza el año más reciente con "
        "cobertura para todos los países elegidos. Los datos pueden contener revisiones del "
        "proveedor."
    )

st.caption("Construido por Dayan Elvis Jahuira Pilco · Actividad Grupal 01 · SI885")
