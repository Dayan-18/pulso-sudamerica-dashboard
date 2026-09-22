# Pulso de Sudamérica

Dashboard interactivo creado con Streamlit y Plotly para comparar indicadores de desarrollo de doce países sudamericanos entre 2000 y 2025.

## Indicadores

- PIB per cápita en dólares corrientes.
- Esperanza de vida al nacer.
- Personas que usan Internet.
- Población total.

Los datos provienen de [World Development Indicators](https://databank.worldbank.org/source/world-development-indicators), mediante la [API pública del Banco Mundial](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation).

## Funciones

- Filtros por indicador, países y periodo.
- Indicadores clave calculados sobre años comparables.
- Mapa coroplético y ranking regional.
- Evolución histórica de hasta ocho países.
- Comparación entre PIB, esperanza de vida, conectividad y población.
- Tabla navegable y descarga de la selección en CSV.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

En Windows, la activación del entorno es `.venv\Scripts\activate`.

## Actualizar los datos

```bash
python scripts/fetch_data.py
```

El dashboard funciona sin conexión a la API porque conserva una extracción versionada dentro de `data/`.

## Pruebas y automatización

Cada `push` y `pull request` ejecuta GitHub Actions para:

1. Instalar las dependencias.
2. Revisar el código con Ruff.
3. Ejecutar las pruebas con Pytest.
4. Iniciar Streamlit y consultar su endpoint de salud.

Streamlit Community Cloud queda conectado a la rama `main`; después del primer despliegue, cada cambio aprobado y enviado a GitHub se publica automáticamente.

## Publicar en Streamlit Community Cloud

1. Crear un repositorio público llamado `pulso-sudamerica-dashboard` y subir este proyecto.
2. Ingresar a [share.streamlit.io](https://share.streamlit.io/) con GitHub.
3. Seleccionar el repositorio, la rama `main` y `streamlit_app.py` como archivo principal.
4. Elegir, si está disponible, el subdominio `pulso-sudamerica` y presionar **Deploy**.

## Enlaces

- Repositorio previsto: <https://github.com/Dayan-18/pulso-sudamerica-dashboard>
- Aplicación prevista: <https://pulso-sudamerica.streamlit.app/>
- Artículo: pendiente de publicación.
- Video: pendiente de publicación.

## Autor

Dayan Elvis Jahuira Pilco — SI885.
