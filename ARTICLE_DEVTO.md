<!--
Título en Dev.to: Construí un dashboard interactivo de Sudamérica con Streamlit y datos del Banco Mundial
Descripción: Del dato público al despliegue automático: filtros, mapas y pruebas para comparar indicadores de desarrollo en Sudamérica.
Tags: python, streamlit, datavisualization, devops
Antes de publicar: subir una captura como portada y reemplazar cualquier enlace si el subdominio final cambia.
-->

# Construí un dashboard interactivo de Sudamérica con Streamlit y datos del Banco Mundial

Los datos abiertos tienen un gran potencial, pero una tabla con miles de filas no siempre permite encontrar una historia. Para esta actividad construí **Pulso de Sudamérica**, un dashboard interactivo que permite comparar indicadores económicos y sociales de doce países de la región entre los años 2000 y 2025.

La aplicación fue desarrollada con Python, Streamlit, Pandas y Plotly. El código está en un repositorio público, las pruebas se ejecutan automáticamente con GitHub Actions y la publicación se realiza en Streamlit Community Cloud.

- **Aplicación:** [Pulso de Sudamérica](https://pulso-sudamerica.streamlit.app/)
- **Código fuente:** [Repositorio público en GitHub](https://github.com/Dayan-18/pulso-sudamerica-dashboard)

> Si el enlace de la aplicación todavía muestra un error 404, significa que falta realizar el primer despliegue desde Streamlit Community Cloud. Los siguientes cambios en `main` se publicarán automáticamente.

## ¿Qué problema quería resolver?

Mi objetivo fue crear una herramienta sencilla para responder preguntas como estas:

- ¿Qué país tiene el mayor PIB per cápita en un año determinado?
- ¿Cómo evolucionó el acceso a Internet en Perú frente a otros países?
- ¿Existe una relación visible entre ingreso, conectividad y esperanza de vida?
- ¿Qué tan reciente es la información disponible para cada indicador?

En lugar de presentar gráficos estáticos, el dashboard permite seleccionar el indicador, hasta ocho países y un periodo. Así, una misma aplicación sirve para explorar diferentes preguntas sin modificar el código.

## Fuente y preparación de los datos

Utilicé **World Development Indicators**, la colección de indicadores de desarrollo del Banco Mundial. Su API V2 no necesita una clave y permite solicitar datos por país, indicador y periodo.

Los cuatro indicadores seleccionados fueron:

| Indicador | Código del Banco Mundial | Unidad |
|---|---|---|
| PIB per cápita | `NY.GDP.PCAP.CD` | US$ corrientes |
| Esperanza de vida | `SP.DYN.LE00.IN` | Años |
| Uso de Internet | `IT.NET.USER.ZS` | % de la población |
| Población total | `SP.POP.TOTL` | Personas |

El script `scripts/fetch_data.py` consulta la API, descarta observaciones sin valor, normaliza los nombres de países y guarda una extracción en CSV. Mantener una copia versionada permite que la aplicación funcione aunque la API esté temporalmente lenta o no disponible.

Una llamada tiene esta estructura:

```python
response = requests.get(
    "https://api.worldbank.org/v2/country/PER/indicator/IT.NET.USER.ZS",
    params={"format": "json", "date": "2000:2025"},
    timeout=60,
)
response.raise_for_status()
```

Además, la carga local valida el esquema, convierte años y valores a tipos numéricos y elimina duplicados usando país, año e indicador como clave.

## Diseño del dashboard

Organicé la interfaz en cuatro secciones:

1. **Panorama:** muestra indicadores principales, mapa coroplético y ranking de países.
2. **Evolución:** compara series de tiempo con líneas interactivas.
3. **Relación de desarrollo:** combina PIB per cápita, esperanza de vida, población y acceso a Internet en un gráfico de burbujas.
4. **Datos:** permite revisar y descargar la selección actual como CSV.

Los filtros están en la barra lateral. Con Pandas, el subconjunto principal se obtiene de manera directa:

```python
filtered = metric_data.loc[
    metric_data["country"].isin(selected_countries)
    & metric_data["year"].between(*selected_years)
].copy()
```

Un detalle importante fue no comparar países usando años diferentes. La función `latest_common_year` busca el año más reciente que tenga información para todos los países seleccionados. Ese año alimenta la mediana regional, el país líder, el mapa y el ranking.

```python
counts = frame.groupby("year")["country_code"].nunique()
complete = counts[counts >= expected_countries]
latest_year = int(complete.index.max())
```

Con esta decisión, los indicadores superiores son comparables y no mezclan una observación reciente de un país con una antigua de otro.

## Visualizaciones con Plotly

Elegí Plotly porque agrega interacción sin escribir JavaScript: tooltips, zoom, leyendas y mapas funcionan directamente dentro de Streamlit.

El mapa usa códigos ISO-3 para ubicar cada país. El gráfico de relación utiliza:

- Eje horizontal: PIB per cápita.
- Eje vertical: esperanza de vida.
- Tamaño de la burbuja: población.
- Color: porcentaje de personas que usan Internet.

Esta vista permite observar cuatro variables al mismo tiempo. En la extracción actual, los datos más recientes de Perú muestran aproximadamente **81.96 % de uso de Internet en 2024**, **77.94 años de esperanza de vida en 2024** y una población cercana a **34.58 millones en 2025**. Las cifras pueden cambiar cuando el Banco Mundial publique revisiones.

## Calidad del código

Separé la aplicación en componentes pequeños:

```text
streamlit_app.py       interfaz principal
src/data.py            carga y validación
src/analytics.py       métricas comparables
src/charts.py          gráficos Plotly
scripts/fetch_data.py  actualización de datos
tests/                 pruebas automáticas
```

Las pruebas verifican que:

- Existan los cuatro indicadores.
- La clave país-año-indicador sea única.
- No queden valores nulos en la medición.
- El cálculo del último año comparable sea correcto.
- La mediana, el crecimiento y el país líder se calculen correctamente.

## Automatización con GitHub Actions

El repositorio incluye el flujo `.github/workflows/ci.yml`. En cada `push` o `pull request`, GitHub crea un entorno limpio y ejecuta cuatro pasos:

```yaml
- name: Revisar estilo
  run: ruff check .

- name: Ejecutar pruebas
  run: pytest -q

- name: Probar inicio de Streamlit
  run: |
    streamlit run streamlit_app.py --server.headless true --server.port 8501 &
    curl --retry 20 --retry-delay 2 --retry-connrefused \
      http://localhost:8501/_stcore/health
```

De esta manera, un error de sintaxis, una dependencia rota o un fallo al iniciar la aplicación se detecta antes de publicar.

## Despliegue en Streamlit Community Cloud

El despliegue inicial requiere conectar una cuenta de GitHub en [Streamlit Community Cloud](https://share.streamlit.io/), elegir el repositorio, la rama `main` y el archivo `streamlit_app.py`.

Después de esa configuración, el proceso es automático: cada cambio enviado a la rama principal es detectado por Streamlit y la aplicación pública se actualiza. Esto complementa el flujo de GitHub Actions: primero se valida el proyecto y luego la plataforma publica la versión del repositorio.

La aplicación no necesita secretos ni una base de datos externa porque utiliza la extracción CSV incluida en el repositorio. Esto hace que el despliegue sea pequeño, reproducible y fácil de mantener.

## Lo que aprendí

El reto principal no fue dibujar gráficos, sino tomar decisiones que hicieran comparables los datos. Trabajar con indicadores públicos implica aceptar que cada serie puede tener un último año diferente y que el proveedor puede revisar cifras anteriores.

También comprobé que un dashboard es más útil cuando cada visualización responde una pregunta concreta. Por eso limité los indicadores, evité duplicar gráficos y agregué una descarga de datos para que el usuario pueda continuar su propio análisis.

Como siguientes mejoras me gustaría incorporar indicadores ambientales, permitir guardar una comparación mediante una URL y agregar una nota automática cuando un país tenga datos desactualizados.

## Recursos

- [Código fuente en GitHub](https://github.com/Dayan-18/pulso-sudamerica-dashboard)
- [Dashboard en Streamlit](https://pulso-sudamerica.streamlit.app/)
- [Documentación de la API del Banco Mundial](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)
- [Documentación de Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud)

Si te interesa la visualización de datos públicos, puedes clonar el repositorio y adaptar la lista de países o indicadores desde `scripts/fetch_data.py`.
