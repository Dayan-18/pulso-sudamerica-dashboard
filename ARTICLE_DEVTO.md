<!--
DEV Community title: Building an Interactive South America Dashboard with Streamlit and World Bank Data
Description: From public data to automated deployment: filters, maps, tests, and a live dashboard for exploring development indicators across South America.
Tags: python, streamlit, datavisualization, devops
Before publishing: upload a dashboard screenshot as the cover image. Paste the article from the H1 heading downward into the Dev.to editor.
-->

# Building an Interactive South America Dashboard with Streamlit and World Bank Data

Open data has enormous potential, but a table containing thousands of rows does not always tell a clear story. For this project, I built **South America Pulse**, an interactive dashboard for comparing economic and social indicators across twelve South American countries from 2000 to 2025.

The application was created with Python, Streamlit, Pandas, and Plotly. Its source code is stored in a public repository, every change is validated automatically with GitHub Actions, and the live application is hosted on Streamlit Community Cloud.

- **Live application:** [South America Pulse](https://pulso-sudamerica.streamlit.app/)
- **Source code:** [Public GitHub repository](https://github.com/Dayan-18/pulso-sudamerica-dashboard)

## The problem I wanted to solve

My goal was to build a simple tool that could answer questions such as:

- Which country has the highest GDP per capita in a selected year?
- How has Internet adoption in Peru evolved compared with neighboring countries?
- Is there a visible relationship between income, connectivity, and life expectancy?
- How recent is the information available for each indicator?

Instead of producing a collection of static charts, the dashboard lets users select an indicator, up to eight countries, and a time range. The same application can therefore support many different comparisons without requiring any code changes.

## Data source and preparation

I used the **World Development Indicators** dataset from the World Bank. Its V2 API does not require an API key and supports requests by country, indicator, and period.

I selected four indicators:

| Indicator | World Bank code | Unit |
|---|---|---|
| GDP per capita | `NY.GDP.PCAP.CD` | Current US dollars |
| Life expectancy at birth | `SP.DYN.LE00.IN` | Years |
| Individuals using the Internet | `IT.NET.USER.ZS` | Percentage of population |
| Total population | `SP.POP.TOTL` | People |

The `scripts/fetch_data.py` script calls the API, removes observations without values, standardizes country names, and saves the result as a CSV file. Keeping a versioned local extract allows the application to continue working even if the API is temporarily slow or unavailable.

A request follows this structure:

```python
response = requests.get(
    "https://api.worldbank.org/v2/country/PER/indicator/IT.NET.USER.ZS",
    params={"format": "json", "date": "2000:2025"},
    timeout=60,
)
response.raise_for_status()
```

The local loading layer also validates the required columns, converts years and values to numeric types, and removes duplicates using country, year, and indicator as a composite key. The resulting dataset contains 1,218 observations and is small enough to load quickly on a free hosting service.

## Dashboard design

I organized the interface into four sections:

1. **Overview:** headline metrics, a choropleth map, and a country ranking.
2. **Trend:** interactive time series for the selected countries.
3. **Development relationship:** a bubble chart that combines four indicators.
4. **Data:** a searchable table and a button for downloading the current selection as CSV.

The filters are placed in the sidebar. With Pandas, the main subset can be created directly:

```python
filtered = metric_data.loc[
    metric_data["country"].isin(selected_countries)
    & metric_data["year"].between(*selected_years)
].copy()
```

One important design decision was to avoid comparing countries using different years. The `latest_common_year` function searches for the newest year that contains data for every selected country. That year is then used for the regional median, leading country, map, and ranking.

```python
counts = frame.groupby("year")["country_code"].nunique()
complete = counts[counts >= expected_countries]
latest_year = int(complete.index.max())
```

This makes the headline values comparable instead of mixing a recent observation from one country with an older observation from another.

## Interactive visualizations with Plotly

I chose Plotly because it provides useful interaction without requiring custom JavaScript. Tooltips, legends, zoom controls, and geographic maps work directly inside Streamlit.

The map uses ISO-3 country codes to locate each observation. The development relationship chart uses four visual properties at the same time:

- Horizontal axis: GDP per capita.
- Vertical axis: life expectancy.
- Bubble size: total population.
- Bubble color: percentage of people using the Internet.

This view makes it possible to compare income, health, connectivity, and population in a single chart. In the current extract, Peru has approximately **81.96% Internet usage in 2024**, **77.94 years of life expectancy in 2024**, and a population of about **34.58 million in 2025**. These values may change when the World Bank publishes revisions.

## Code organization and quality

I separated the project into small components with clear responsibilities:

```text
streamlit_app.py       main user interface
src/data.py            loading and validation
src/analytics.py       comparable metrics
src/charts.py          Plotly visualizations
scripts/fetch_data.py  data refresh process
tests/                 automated tests
```

The automated tests verify that:

- All four indicators are present.
- The country-year-indicator key is unique.
- No null measurement values remain.
- The latest comparable year is calculated correctly.
- The median, percentage change, and leading country are correct.

The project currently passes all four tests locally.

## Continuous integration with GitHub Actions

The repository includes `.github/workflows/ci.yml`. On every push or pull request, GitHub creates a clean environment and performs four checks:

```yaml
- name: Check code style
  run: ruff check .

- name: Run tests
  run: pytest -q

- name: Test the Streamlit startup
  run: |
    streamlit run streamlit_app.py --server.headless true --server.port 8501 &
    curl --retry 20 --retry-delay 2 --retry-connrefused \
      http://localhost:8501/_stcore/health
```

This workflow detects syntax errors, broken dependencies, failed tests, and application startup problems before a new version is published.

## Deployment on Streamlit Community Cloud

I deployed the application using [Streamlit Community Cloud](https://share.streamlit.io/). The initial setup only required connecting my GitHub account and selecting three values:

- Repository: `Dayan-18/pulso-sudamerica-dashboard`
- Branch: `main`
- Entry point: `streamlit_app.py`

After that initial configuration, deployment became automatic. When a validated change is pushed to the main branch, Streamlit detects the repository update and rebuilds the public application.

The dashboard does not require secrets or an external database because it reads the versioned CSV extract included in the repository. This keeps the deployment lightweight, reproducible, and suitable for a free cloud platform.

## What I learned

The main challenge was not drawing the charts; it was making responsible decisions about how the data should be compared. Public indicators do not always share the same latest year, and providers may revise previously published observations.

I also learned that a dashboard is more useful when every visualization answers a specific question. I limited the number of indicators, avoided repeating the same information in multiple charts, and included a CSV download so users can continue their own analysis.

As future improvements, I would like to add environmental indicators, allow users to save a comparison in a shareable URL, and display an automatic note whenever a country has outdated data.

## Resources

- [Public GitHub repository](https://github.com/Dayan-18/pulso-sudamerica-dashboard)
- [Live Streamlit dashboard](https://pulso-sudamerica.streamlit.app/)
- [World Bank Indicators API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)
- [Streamlit Community Cloud documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud)

If you are interested in public data visualization, you can clone the repository and adapt the country or indicator lists in `scripts/fetch_data.py`.
