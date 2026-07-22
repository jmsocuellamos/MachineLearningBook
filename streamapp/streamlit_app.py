"""
streamlit_app.py
----------------
Clasificador de flores Iris con Streamlit.

Equivalente funcional a la version de Gradio, pero escrita de forma
idiomatica para Streamlit (no es una traduccion literal).

Ejecutar en local:
    streamlit run streamlit_app.py
"""

import matplotlib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

matplotlib.use("Agg")
from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# 1. CONFIGURACION DE LA PAGINA
#    DEBE ser la primera instruccion de Streamlit que se ejecuta.
#    Si va despues de cualquier otro st.*, lanza una excepcion.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Clasificador Iris",
    page_icon="🌸",
    layout="wide",
)

COLOR_ACTIVO = "#2563eb"
COLOR_INACTIVO = "#93c5fd"


# ---------------------------------------------------------------------------
# 2. CARGA DEL MODELO
#
#    @st.cache_resource es EL concepto clave de Streamlit.
#    El script entero se re-ejecuta de arriba abajo cada vez que el usuario
#    toca un widget. Sin cache, el modelo se reentrenaria en cada clic.
#    Con el decorador, la funcion se ejecuta UNA vez y el resultado se
#    reutiliza en todas las re-ejecuciones y para todos los usuarios.
#
#    cache_resource -> objetos no serializables y compartidos (modelos,
#                      conexiones a bases de datos).
#    cache_data     -> datos serializables (DataFrames, resultados de
#                      consultas). Devuelve una copia a cada usuario.
# ---------------------------------------------------------------------------
@st.cache_resource
def cargar_modelo():
    """Entrena el modelo una sola vez y lo deja en memoria."""
    iris = load_iris()
    X, y = iris.data, iris.target

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(modelo, X, y, cv=5)
    modelo.fit(X, y)

    metadatos = {
        "nombres_clases": [str(c) for c in iris.target_names],
        "nombres_features": [str(f) for f in iris.feature_names],
        "medias_por_clase": {
            str(nombre): X[y == i].mean(axis=0).round(3).tolist()
            for i, nombre in enumerate(iris.target_names)
        },
        "accuracy_cv": float(scores.mean()),
        "std_cv": float(scores.std()),
    }
    return modelo, metadatos


modelo, meta = cargar_modelo()
NOMBRES_CLASES = meta["nombres_clases"]
NOMBRES_FEATURES = meta["nombres_features"]


# ---------------------------------------------------------------------------
# 3. LOGICA DE NEGOCIO
#    Funciones Python normales, sin dependencia de Streamlit.
#    Se pueden testear de forma aislada.
# ---------------------------------------------------------------------------
def predecir(medidas):
    """Devuelve (indice_clase, vector_de_probabilidades)."""
    X_in = np.array([medidas])
    probs = modelo.predict_proba(X_in)[0]
    idx = int(modelo.predict(X_in)[0])
    return idx, probs


def grafico_probabilidades(probs, idx_pred):
    """Construye el grafico de barras sin usar pyplot (evita fugas de memoria)."""
    fig = Figure(figsize=(6, 3))
    ax = fig.subplots()
    colores = [COLOR_ACTIVO if i == idx_pred else COLOR_INACTIVO for i in range(len(probs))]
    barras = ax.bar(NOMBRES_CLASES, probs, color=colores, edgecolor="white", linewidth=1.5)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Probabilidad")
    for barra, p in zip(barras, probs):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.02,
            f"{p:.3f}",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def tabla_comparativa(medidas):
    """DataFrame comparando la muestra con las medias de cada especie."""
    filas = [["-> Tu muestra"] + [round(v, 2) for v in medidas]]
    for nombre, medias in meta["medias_por_clase"].items():
        filas.append([f"media {nombre}"] + medias)
    return pd.DataFrame(filas, columns=["Muestra"] + NOMBRES_FEATURES)


# ---------------------------------------------------------------------------
# 4. INTERFAZ
#    En Streamlit no se "declaran" componentes y luego se conectan eventos.
#    El script se lee de arriba abajo y cada widget DEVUELVE su valor actual.
# ---------------------------------------------------------------------------
st.title("🌸 Clasificador de flores Iris")
st.caption(
    f"Random Forest (100 árboles) · Accuracy en validación cruzada: "
    f"{meta['accuracy_cv']:.3f} ± {meta['std_cv']:.3f}"
)

# --- Barra lateral: entradas ---
with st.sidebar:
    st.header("Medidas de entrada")

    # Los valores por defecto viven en session_state para que el boton
    # de "Restablecer" pueda modificarlos.
    if "reset" not in st.session_state:
        st.session_state.reset = False

    ejemplos = {
        "Personalizado": None,
        "Setosa típica": [5.1, 3.5, 1.4, 0.2],
        "Versicolor típica": [6.7, 3.1, 4.7, 1.5],
        "Virginica típica": [6.3, 3.3, 6.0, 2.5],
    }
    eleccion = st.selectbox("Ejemplos predefinidos", list(ejemplos.keys()))
    base = ejemplos[eleccion] or [5.8, 3.0, 3.8, 1.2]

    sepal_l = st.slider("Sepal length (cm)", 4.0, 8.0, base[0], 0.1)
    sepal_w = st.slider("Sepal width (cm)", 2.0, 4.5, base[1], 0.1)
    petal_l = st.slider("Petal length (cm)", 1.0, 7.0, base[2], 0.1)
    petal_w = st.slider("Petal width (cm)", 0.1, 2.5, base[3], 0.1)

    st.divider()
    st.markdown(
        "**Nota:** el modelo se entrenó con solo 150 muestras. "
        "Es una demostración didáctica, no una herramienta de campo."
    )

medidas = [sepal_l, sepal_w, petal_l, petal_w]

# --- Validacion ---
if any(v <= 0 for v in medidas):
    st.error("Todas las medidas deben ser mayores que cero.")
    st.stop()          # detiene la ejecucion del script aqui

# --- Prediccion ---
idx_pred, probs = predecir(medidas)
clase_pred = NOMBRES_CLASES[idx_pred]
confianza = probs[idx_pred]

# --- Metricas destacadas ---
col1, col2, col3 = st.columns(3)
col1.metric("Predicción", clase_pred.capitalize())
col2.metric("Confianza", f"{confianza:.1%}")
col3.metric("Segunda opción", NOMBRES_CLASES[int(np.argsort(probs)[-2])])

if confianza < 0.60:
    st.warning(
        "Confianza baja. Estas medidas caen en una zona donde el modelo "
        "no distingue bien entre especies."
    )

st.divider()

# --- Resultados en dos columnas ---
izq, der = st.columns([3, 2])

with izq:
    st.subheader("Distribución de probabilidades")
    st.pyplot(grafico_probabilidades(probs, idx_pred))

with der:
    st.subheader("Detalle")
    st.dataframe(
        pd.DataFrame({"Especie": NOMBRES_CLASES, "Probabilidad": probs.round(4)}),
        hide_index=True,
        width="stretch",
    )

# --- Comparativa plegable ---
with st.expander("Comparar con las medias de cada especie"):
    st.dataframe(tabla_comparativa(medidas), hide_index=True, width="stretch")
    st.caption(
        "Compara tus medidas con el promedio de cada especie en el conjunto "
        "de entrenamiento."
    )

# --- Descarga del resultado ---
resultado = pd.DataFrame(
    {
        "variable": NOMBRES_FEATURES + ["prediccion", "confianza"],
        "valor": [str(v) for v in medidas] + [clase_pred, f"{confianza:.4f}"],
    }
)
st.download_button(
    "Descargar resultado (CSV)",
    data=resultado.to_csv(index=False).encode("utf-8"),
    file_name="prediccion_iris.csv",
    mime="text/csv",
)
