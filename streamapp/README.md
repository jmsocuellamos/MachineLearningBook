# Clasificador de flores Iris — Streamlit

Aplicación de demostración construida con Streamlit sobre un modelo Random Forest
entrenado con el dataset Iris de scikit-learn.

Accuracy en validación cruzada (5 folds): **0.967**

## Contenido

| Fichero | Función |
|---|---|
| `streamlit_app.py` | La aplicación completa |
| `requirements.txt` | Dependencias |
| `.streamlit/config.toml` | Tema visual (opcional) |

No hay ficheros binarios: el modelo se entrena en memoria al arrancar,
cacheado con `@st.cache_resource` para que solo ocurra una vez.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Abre `http://localhost:8501`.

> **Ojo:** no uses `python streamlit_app.py`. Las aplicaciones de Streamlit
> se lanzan siempre con `streamlit run`.

## Desplegar

1. Sube este repositorio a GitHub (público).
2. Entra en [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub.
3. **Create app** → selecciona el repositorio, rama `main`, fichero `streamlit_app.py`.
4. En **Advanced settings**, elige Python 3.11 o superior.
5. **Deploy**.

Cada `git push` posterior actualiza la aplicación automáticamente.
