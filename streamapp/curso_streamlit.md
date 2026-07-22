# Curso de Streamlit para el despliegue de modelos de Machine Learning

**Material complementario a** *F-02. Despliegue de modelos de aprendizaje automático* (IA4LEGOS)
**Versión de Streamlit de referencia:** 1.60.0
**Fecha:** julio 2026

---

## Índice

| Módulo | Contenido |
|---|---|
| 0 | El modelo mental: el ciclo de re-ejecución |
| 1 | Instalación y primera aplicación |
| 2 | Widgets de entrada |
| 3 | Elementos de salida |
| 4 | Layout: columnas, pestañas, barra lateral |
| 5 | **Caché: el concepto crítico** |
| 6 | Estado de sesión y formularios |
| 7 | De Gradio a Streamlit: equivalencias |
| 8 | **Despliegue en Streamlit Community Cloud** |
| 9 | Alternativas de despliegue |
| 10 | Buenas prácticas y errores frecuentes |
| A | Apéndice: chuleta de referencia rápida |
| B | Apéndice: comparativa Streamlit / Gradio |

---

# Módulo 0. El modelo mental

## 0.1 La idea central

Si en Gradio la abstracción era "una función con una interfaz delante", en Streamlit es otra bien distinta, y entenderla evita el 90 % de la confusión inicial:

> **Una aplicación de Streamlit es un script de Python que se vuelve a ejecutar entero, de arriba abajo, cada vez que el usuario toca algo.**

No hay funciones de *callback*. No hay eventos que conectar. No hay componentes que declarar y luego enlazar. Solo un script que se lee secuencialmente, como cualquier programa de Python.

```python
import streamlit as st

nombre = st.text_input("Tu nombre")     # dibuja la caja Y devuelve su valor
st.write(f"Hola, {nombre}")             # se ejecuta con el valor actual
```

Cuando el usuario escribe algo en la caja, Streamlit **vuelve a ejecutar el fichero entero** desde la primera línea. En esa nueva ejecución, `st.text_input` devuelve el texto que el usuario acaba de escribir, y `st.write` lo muestra.

## 0.2 Las consecuencias de este diseño

Este modelo es sorprendentemente simple, pero tiene implicaciones que hay que interiorizar:

**Los widgets devuelven valores directamente.** `st.slider(...)` no es un objeto que hay que consultar después: *es* el número que el usuario ha elegido. Se usa como cualquier variable.

**El orden del código es el orden de la pantalla.** Lo que escribes primero aparece arriba. No hay que declarar un layout aparte.

**Todo se recalcula constantemente.** Y aquí está el peligro: si tu script carga un modelo de 500 MB en la línea 10, ese modelo se cargaría **en cada interacción**. Esto es exactamente lo que resuelve el sistema de caché del módulo 5, y es la diferencia entre una aplicación usable y una inutilizable.

**No hay estado por defecto.** Cada re-ejecución empieza de cero. Si necesitas recordar algo entre interacciones, hace falta `st.session_state` (módulo 6).

## 0.3 Comparación directa con Gradio

Merece la pena verlo lado a lado, porque el mismo problema se resuelve de forma opuesta:

```python
# GRADIO: declarar componentes, conectar eventos
with gr.Blocks() as demo:
    entrada = gr.Slider(0, 10)
    salida  = gr.Textbox()
    entrada.change(fn=lambda x: x * 2, inputs=entrada, outputs=salida)

# STREAMLIT: script lineal
entrada = st.slider("Valor", 0, 10)
st.text(entrada * 2)
```

Streamlit resulta más natural para quien viene de escribir scripts de análisis. Gradio resulta más natural para quien piensa en términos de "modelo con entradas y salidas".

## 0.4 Cuándo Streamlit y cuándo Gradio

| Situación | Herramienta |
|---|---|
| Demostrar un modelo: entra un dato, sale una predicción | **Gradio** |
| Aplicación de datos con filtros, tablas y varios gráficos | **Streamlit** |
| Componentes multimedia (audio, webcam, dibujo sobre imagen) | **Gradio** |
| Varias páginas, navegación, informes | **Streamlit** |
| Necesitas una API REST además de la interfaz | **Gradio** |
| El público son analistas que quieren explorar datos | **Streamlit** |

Un criterio breve: **si el centro es el modelo, Gradio; si el centro son los datos, Streamlit.**

---

# Módulo 1. Instalación y primera aplicación

## 1.1 Instalación

```bash
pip install streamlit
```

Comprobación:

```bash
streamlit hello        # abre una app de demostración
```

## 1.2 La diferencia fundamental: cómo se ejecuta

Aquí hay una trampa que confunde a todo el mundo al principio. Una aplicación de Streamlit **no se ejecuta con `python`**:

```bash
python mi_app.py           # MAL: no hace nada útil, avisa por consola
streamlit run mi_app.py    # BIEN
```

Si lo lanzas con `python`, Streamlit imprime un aviso y el script se ejecuta como un programa normal, sin servidor y sin interfaz.

La consecuencia práctica es que **no lleva bloque `if __name__ == "__main__":`**. En Gradio ese bloque protegía la llamada a `launch()`; en Streamlit no hay nada equivalente porque el propio comando `streamlit run` es quien arranca el servidor.

## 1.3 La aplicación mínima

```python
import streamlit as st

st.title("Mi primera aplicación")

nombre = st.text_input("¿Cómo te llamas?")

if nombre:
    st.write(f"Hola, {nombre}")
```

```bash
streamlit run mi_app.py
```

Se abre en `http://localhost:8501`.

## 1.4 Configuración de la página

```python
st.set_page_config(
    page_title="Clasificador Iris",
    page_icon="🌸",
    layout="wide",              # "centered" (por defecto) o "wide"
    initial_sidebar_state="expanded",
)
```

> **Regla estricta:** `st.set_page_config()` debe ser **la primera instrucción de Streamlit** que se ejecuta en el script. Si va después de cualquier otro `st.*`, lanza una excepción. Los `import` sí pueden ir antes.

`layout="wide"` aprovecha todo el ancho de la pantalla. Para aplicaciones con gráficos y tablas suele ser lo que quieres.

---

# Módulo 2. Widgets de entrada

Todos siguen el mismo patrón: se llaman, dibujan el control y **devuelven el valor actual**.

## 2.1 Catálogo

| Widget | Devuelve | Uso típico |
|---|---|---|
| `st.text_input()` | `str` | Nombres, rutas, consultas |
| `st.text_area()` | `str` | Texto largo |
| `st.number_input()` | `int` / `float` | Valores numéricos precisos |
| `st.slider()` | `int` / `float` / tupla | Rangos acotados |
| `st.select_slider()` | valor de una lista | Escalas ordinales |
| `st.checkbox()` | `bool` | Opciones on/off |
| `st.radio()` | valor elegido | Pocas opciones exclusivas |
| `st.selectbox()` | valor elegido | Muchas opciones exclusivas |
| `st.multiselect()` | `list` | Selección múltiple |
| `st.date_input()` | `datetime.date` | Fechas |
| `st.time_input()` | `datetime.time` | Horas |
| `st.file_uploader()` | objeto tipo fichero | Subir CSV, imágenes |
| `st.color_picker()` | `str` (hex) | Colores |
| `st.button()` | `bool` | Acciones |
| `st.download_button()` | `bool` | Descargar resultados |
| `st.camera_input()` | imagen | Foto desde la webcam |

## 2.2 Ejemplos con los parámetros importantes

```python
# Slider: minimo, maximo, valor inicial, paso
edad = st.slider("Edad", min_value=0, max_value=100, value=30, step=1)

# Slider de rango: devuelve una TUPLA
rango = st.slider("Rango de precios", 0, 1000, (200, 800))
print(rango)   # (200, 800)

# Selectbox con ayuda
modelo = st.selectbox(
    "Algoritmo",
    ["Random Forest", "Regresión Logística", "SVM"],
    index=0,
    help="Random Forest suele dar mejores resultados con pocos datos",
)

# Number input con formato
umbral = st.number_input("Umbral", 0.0, 1.0, 0.5, step=0.05, format="%.2f")

# File uploader restringido
archivo = st.file_uploader("Sube un CSV", type=["csv"])
if archivo is not None:
    df = pd.read_csv(archivo)       # se lee directamente, sin .name
```

> **Diferencia con Gradio:** en Gradio, `gr.File` devolvía un objeto del que había que sacar `.name` para obtener la ruta. En Streamlit, `st.file_uploader` devuelve un objeto que `pandas` puede leer directamente.

## 2.3 El comportamiento peculiar de `st.button()`

Este merece atención especial porque es fuente constante de confusión:

```python
if st.button("Calcular"):
    st.write("Has pulsado el botón")
```

`st.button()` devuelve `True` **solo durante la re-ejecución inmediatamente posterior al clic**. En la siguiente interacción (mover un slider, por ejemplo) vuelve a ser `False` y el mensaje desaparece.

Esto rompe las expectativas de quien viene de otros frameworks. Si necesitas que algo persista tras pulsar un botón, hace falta `st.session_state` (módulo 6).

## 2.4 La clave `key`

Cuando tienes varios widgets iguales, Streamlit necesita distinguirlos:

```python
for i, columna in enumerate(df.columns):
    st.slider(f"Peso de {columna}", 0.0, 1.0, 0.5, key=f"peso_{i}")
```

Sin `key`, dos widgets con la misma etiqueta y parámetros provocan el error `DuplicateWidgetID`. Además, la `key` permite acceder al valor desde `st.session_state["peso_0"]`.

---

# Módulo 3. Elementos de salida

## 3.1 Texto y formato

```python
st.title("Título principal")
st.header("Sección")
st.subheader("Subsección")
st.markdown("Texto con **negrita**, *cursiva* y `código`")
st.caption("Texto pequeño para notas al pie")
st.code("print('hola')", language="python")
st.latex(r"\gamma(h) = c\left[1 - e^{-h/a}\right]")
st.divider()
```

`st.write()` es el comodín: detecta el tipo y lo muestra como corresponda (texto, DataFrame, figura, diccionario...). Útil para depurar, pero en código definitivo conviene usar la función específica.

## 3.2 Datos

```python
st.dataframe(df, width="stretch", hide_index=True)   # tabla interactiva
st.table(df)                                          # tabla estática
st.metric("Accuracy", "0.967", delta="+0.02")         # KPI destacado
st.json({"clase": "setosa", "prob": 0.98})
```

`st.dataframe` permite ordenar por columnas y buscar; `st.table` no. Para resultados de modelos, `st.dataframe` casi siempre es mejor.

`st.metric` es muy útil para destacar el resultado principal:

```python
col1, col2, col3 = st.columns(3)
col1.metric("Predicción", "Setosa")
col2.metric("Confianza", "98.2%")
col3.metric("Tiempo", "12 ms", delta="-3 ms", delta_color="inverse")
```

> **Nota sobre `width`:** el parámetro `use_container_width=True` que aparece en tutoriales antiguos está **obsoleto**. Ahora se usa `width="stretch"` (ocupar todo el ancho) o `width="content"` (ajustar al contenido).

## 3.3 Gráficos

```python
# Nativos de Streamlit: rápidos, poco configurables
st.line_chart(df)
st.bar_chart(df)
st.area_chart(df)
st.scatter_chart(df, x="col_x", y="col_y")
st.map(df)                       # necesita columnas lat/lon

# Librerías externas
st.pyplot(fig)                   # matplotlib
st.plotly_chart(fig)             # plotly (interactivo)
st.altair_chart(chart)           # altair
st.graphviz_chart(dot)           # diagramas
```

Para modelos de ML, `st.pyplot` y `st.plotly_chart` cubren casi todo.

## 3.4 Mensajes al usuario

```python
st.success("Modelo entrenado correctamente")
st.info("El conjunto tiene 150 filas")
st.warning("Confianza baja: revisa los datos de entrada")
st.error("La columna 'target' no existe en el fichero")
st.exception(e)                  # muestra un traceback formateado
```

Y para detener la ejecución del script:

```python
if archivo is None:
    st.info("Sube un fichero para empezar")
    st.stop()          # nada de lo que venga después se ejecuta
```

`st.stop()` es el equivalente al `raise gr.Error(...)` de Gradio, pero más flexible: permite mostrar una interfaz parcial en lugar de solo un mensaje de error.

## 3.5 Indicadores de progreso

```python
# Spinner para operaciones cortas
with st.spinner("Entrenando el modelo..."):
    modelo.fit(X, y)

# Barra de progreso para bucles
barra = st.progress(0, text="Procesando")
for i in range(100):
    procesar(i)
    barra.progress((i + 1) / 100, text=f"Procesando {i+1}/100")
barra.empty()

# Estado expandible para procesos largos
with st.status("Ejecutando pipeline...", expanded=True) as estado:
    st.write("Cargando datos")
    cargar()
    st.write("Entrenando")
    entrenar()
    estado.update(label="Completado", state="complete")
```

---

# Módulo 4. Layout

## 4.1 Barra lateral

```python
with st.sidebar:
    st.header("Configuración")
    modelo = st.selectbox("Algoritmo", ["RF", "SVM"])
    n = st.slider("Nº de árboles", 10, 500, 100)
```

O de forma abreviada:

```python
modelo = st.sidebar.selectbox("Algoritmo", ["RF", "SVM"])
```

**Convención muy recomendable:** los controles de configuración van en la barra lateral, los resultados en el área principal. Mantiene la interfaz limpia y es lo que los usuarios esperan.

## 4.2 Columnas

```python
col1, col2 = st.columns(2)                 # dos iguales
col1, col2 = st.columns([3, 1])            # la primera, el triple de ancha
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.subheader("Gráfico")
    st.pyplot(fig)

with col2:
    st.subheader("Detalle")
    st.dataframe(df)
```

## 4.3 Pestañas

```python
tab1, tab2, tab3 = st.tabs(["Predicción", "Datos", "Sobre el modelo"])

with tab1:
    st.pyplot(fig)
with tab2:
    st.dataframe(df)
with tab3:
    st.markdown("Este modelo se entrenó con...")
```

## 4.4 Contenedores plegables

```python
with st.expander("Opciones avanzadas", expanded=False):
    semilla = st.number_input("Random seed", value=42)
    profundidad = st.slider("Profundidad máxima", 1, 20, 10)
```

## 4.5 Contenedores y huecos reservados

```python
# Contenedor: agrupa elementos
with st.container(border=True):
    st.write("Contenido dentro de un recuadro")

# Placeholder: reserva un hueco que se rellena después
hueco = st.empty()
...
hueco.success("Proceso terminado")     # sustituye el contenido del hueco
```

Los *placeholders* sirven para actualizar un elemento en su sitio, en lugar de ir añadiendo cosas al final.

## 4.6 Aplicaciones multipágina

Para aplicaciones grandes, crea una carpeta `pages/`:

```
mi_app/
├── streamlit_app.py        # página principal
└── pages/
    ├── 1_Exploración.py
    ├── 2_Modelo.py
    └── 3_Predicción.py
```

Streamlit genera automáticamente la navegación en la barra lateral. Los números fijan el orden y los guiones bajos se convierten en espacios.

---

# Módulo 5. Caché: el concepto crítico

Este es **el módulo más importante del curso**. Sin caché, una aplicación de Streamlit con un modelo real es inutilizable.

## 5.1 El problema

Recuerda el modelo mental: el script se re-ejecuta entero en cada interacción. Considera esto:

```python
import streamlit as st
import pandas as pd

df = pd.read_csv("datos_5_millones_filas.csv")     # 30 segundos
modelo = joblib.load("modelo_grande.joblib")        # 15 segundos

umbral = st.slider("Umbral", 0.0, 1.0, 0.5)
st.write(f"Predicciones por encima de {umbral}: ...")
```

Cada vez que el usuario mueve el slider un milímetro, se vuelven a leer 5 millones de filas y a cargar el modelo. **45 segundos por cada movimiento del ratón.**

## 5.2 La solución: dos decoradores

```python
@st.cache_data          # para DATOS
def cargar_datos(ruta):
    return pd.read_csv(ruta)

@st.cache_resource      # para RECURSOS
def cargar_modelo(ruta):
    return joblib.load(ruta)

df = cargar_datos("datos.csv")        # se ejecuta una vez
modelo = cargar_modelo("modelo.joblib")
```

La función se ejecuta la primera vez; después, Streamlit devuelve el resultado guardado sin volver a ejecutarla.

## 5.3 Cuál usar: la distinción importa

Esta es la duda más común, y elegir mal provoca errores sutiles.

| | `@st.cache_data` | `@st.cache_resource` |
|---|---|---|
| Para | DataFrames, listas, diccionarios, resultados de consultas | Modelos de ML, conexiones a BD, clientes de API |
| Qué devuelve | Una **copia** a cada usuario | **El mismo objeto** para todos |
| Requisito | El resultado debe ser serializable | No hace falta que lo sea |
| Riesgo si te equivocas | Copiar un modelo de 2 GB en cada sesión | Dos usuarios modifican el mismo DataFrame |

**Regla práctica:** si el objeto se puede guardar en disco con pickle y quieres que cada usuario tenga el suyo, `cache_data`. Si es un objeto pesado y compartible que nadie va a modificar, `cache_resource`.

Un modelo de scikit-learn entra siempre en `cache_resource`.

## 5.4 Parámetros útiles

```python
@st.cache_data(ttl=3600)           # caduca a la hora
def consultar_api():
    ...

@st.cache_data(max_entries=10)     # guarda como mucho 10 resultados
def procesar(parametro):
    ...

@st.cache_data(show_spinner="Cargando datos...")
def cargar():
    ...
```

## 5.5 Cómo funciona la invalidación

La caché se indexa por los **argumentos** de la función. Estas dos llamadas producen dos entradas distintas:

```python
cargar_datos("enero.csv")
cargar_datos("febrero.csv")
```

Esto tiene una consecuencia importante: si tu función depende de algo que **no** es un argumento (una variable global, un fichero que cambia), la caché no se enterará y seguirá devolviendo el valor viejo.

```python
# MAL: la cache no sabe que RUTA puede cambiar
RUTA = "datos.csv"

@st.cache_data
def cargar():
    return pd.read_csv(RUTA)

# BIEN: la ruta es un argumento
@st.cache_data
def cargar(ruta):
    return pd.read_csv(ruta)
```

Para limpiar la caché manualmente:

```python
cargar_datos.clear()      # limpia solo esta función
st.cache_data.clear()     # limpia toda la caché de datos
```

## 5.6 Argumentos que no se pueden hashear

Si un argumento no es hasheable, Streamlit da error. Se resuelve prefijando el nombre con guion bajo:

```python
@st.cache_data
def predecir_lote(_modelo, datos):     # _modelo se ignora al calcular la clave
    return _modelo.predict(datos)
```

Cuidado: al ignorarse, si cambias el modelo la caché no se invalida. Añade un argumento extra que sí identifique la versión:

```python
@st.cache_data
def predecir_lote(_modelo, datos, version_modelo):
    return _modelo.predict(datos)
```

---

# Módulo 6. Estado de sesión y formularios

## 6.1 El problema del estado

Como cada re-ejecución empieza de cero, esto no funciona:

```python
contador = 0
if st.button("Incrementar"):
    contador += 1
st.write(contador)          # siempre muestra 1, nunca 2, 3, 4...
```

## 6.2 `st.session_state`

Es un diccionario que **sobrevive a las re-ejecuciones**, individual para cada usuario:

```python
if "contador" not in st.session_state:
    st.session_state.contador = 0        # inicialización

if st.button("Incrementar"):
    st.session_state.contador += 1

st.write(st.session_state.contador)      # ahora sí: 1, 2, 3...
```

El patrón `if "clave" not in st.session_state` es obligatorio: sin él, cada re-ejecución reiniciaría el valor.

Se puede acceder de dos formas equivalentes:

```python
st.session_state.contador
st.session_state["contador"]
```

## 6.3 Usos típicos en aplicaciones de ML

```python
# Guardar el modelo entrenado por el usuario
if st.button("Entrenar"):
    st.session_state.modelo = entrenar(X, y)
    st.session_state.entrenado = True

if st.session_state.get("entrenado", False):
    st.success("Modelo listo")
    if st.button("Predecir"):
        st.write(st.session_state.modelo.predict(X_nuevo))
```

Sin `session_state`, el modelo entrenado se perdería en cuanto el usuario tocase cualquier otro widget.

```python
# Historial de predicciones
if "historial" not in st.session_state:
    st.session_state.historial = []

if st.button("Predecir"):
    resultado = modelo.predict(entrada)
    st.session_state.historial.append(resultado)

st.dataframe(pd.DataFrame(st.session_state.historial))
```

## 6.4 Widgets y `session_state`

Un widget con `key` guarda automáticamente su valor en `session_state`:

```python
st.slider("Umbral", 0.0, 1.0, 0.5, key="umbral")
st.write(st.session_state.umbral)     # mismo valor
```

Esto permite modificar un widget desde código:

```python
if st.button("Restablecer"):
    st.session_state.umbral = 0.5
    st.rerun()          # fuerza una re-ejecución inmediata
```

## 6.5 Formularios: agrupar entradas

Un formulario evita que el script se re-ejecute con cada tecla. Todo se envía de golpe:

```python
with st.form("mi_formulario"):
    nombre = st.text_input("Nombre")
    edad = st.number_input("Edad", 0, 120)
    enviar = st.form_submit_button("Enviar")

if enviar:
    st.write(f"{nombre}, {edad} años")
```

Muy recomendable cuando hay muchos campos o cuando el procesamiento es costoso: sin formulario, cada campo dispararía una re-ejecución completa.

## 6.6 Callbacks

Aunque el modelo es de re-ejecución, existen callbacks para casos concretos:

```python
def al_cambiar():
    st.session_state.historial.append(st.session_state.seleccion)

st.selectbox("Opción", ["a", "b"], key="seleccion", on_change=al_cambiar)
```

El callback se ejecuta **antes** de la re-ejecución del script. Se usa poco, pero es útil para registrar acciones.

## 6.7 Fragmentos: re-ejecutar solo una parte

Una función decorada con `@st.fragment` se re-ejecuta sola, sin relanzar el script entero:

```python
@st.fragment
def panel_grafico():
    tipo = st.radio("Tipo", ["Barras", "Líneas"], horizontal=True)
    st.pyplot(dibujar(tipo))

panel_grafico()
```

Muy útil cuando el resto de la aplicación es lento y solo quieres refrescar un panel.

---

# Módulo 7. De Gradio a Streamlit: equivalencias

## 7.1 Tabla de traducción

| Gradio | Streamlit |
|---|---|
| `gr.Textbox()` | `st.text_input()` / `st.text_area()` |
| `gr.Number()` | `st.number_input()` |
| `gr.Slider()` | `st.slider()` |
| `gr.Checkbox()` | `st.checkbox()` |
| `gr.Radio()` | `st.radio()` |
| `gr.Dropdown()` | `st.selectbox()` / `st.multiselect()` |
| `gr.File()` | `st.file_uploader()` |
| `gr.Dataframe()` | `st.dataframe()` |
| `gr.Label()` | `st.metric()` + `st.dataframe()` |
| `gr.Plot()` | `st.pyplot()` / `st.plotly_chart()` |
| `gr.Markdown()` | `st.markdown()` |
| `gr.Button()` | `st.button()` |
| `gr.Row()` | `st.columns()` |
| `gr.Column()` | `with col:` |
| `gr.Tab()` | `st.tabs()` |
| `gr.Accordion()` | `st.expander()` |
| `gr.State()` | `st.session_state` |
| `raise gr.Error()` | `st.error()` + `st.stop()` |
| `gr.Warning()` | `st.warning()` |
| `gr.Info()` | `st.info()` |
| `gr.Progress()` | `st.progress()` / `st.spinner()` |
| `gr.Examples()` | `st.selectbox()` con valores predefinidos |
| carga fuera de la función | `@st.cache_resource` |
| `demo.launch()` | `streamlit run app.py` |

## 7.2 El cambio estructural

No basta con sustituir nombres. La reorganización es esta:

```python
# GRADIO
def predecir(a, b):
    return modelo.predict([[a, b]])[0]

with gr.Blocks() as demo:
    x = gr.Slider(0, 10)
    y = gr.Slider(0, 10)
    salida = gr.Label()
    btn = gr.Button("Predecir")
    btn.click(predecir, inputs=[x, y], outputs=salida)

demo.launch()
```

```python
# STREAMLIT
@st.cache_resource
def cargar_modelo():
    return joblib.load("modelo.joblib")

modelo = cargar_modelo()

x = st.slider("X", 0, 10)
y = st.slider("Y", 0, 10)
resultado = modelo.predict([[x, y]])[0]
st.metric("Predicción", resultado)
```

Observa qué desaparece: el bloque `with`, el botón, la conexión de eventos, la función envoltorio. Y qué aparece: el decorador de caché.

## 7.3 Detalles que cambian en la práctica

**Ficheros subidos.** En Gradio había que usar `archivo.name`; en Streamlit el objeto se pasa directamente a pandas:

```python
# Gradio
df = pd.read_csv(archivo.name)

# Streamlit
df = pd.read_csv(archivo)
```

**Errores.** En Gradio se lanzaba una excepción; en Streamlit se muestra y se detiene:

```python
# Gradio
raise gr.Error("Falta el fichero")

# Streamlit
st.error("Falta el fichero")
st.stop()
```

**Reactividad.** En Gradio había que conectar `.change()` explícitamente para que los sliders recalcularan. En Streamlit **es el comportamiento por defecto**: cualquier cambio re-ejecuta el script.

**Gráficos de matplotlib.** El mismo consejo vale para ambos: usa la clase `Figure` en lugar de `pyplot` para evitar acumulación de figuras en memoria.

```python
from matplotlib.figure import Figure

fig = Figure(figsize=(6, 3))
ax = fig.subplots()
ax.bar(nombres, valores)
st.pyplot(fig)
```

---

# Módulo 8. Despliegue en Streamlit Community Cloud

Aquí está la diferencia práctica más importante frente a Hugging Face Spaces: **Streamlit Community Cloud despliega desde GitHub**, no desde su propio repositorio.

## 8.1 Cómo funciona

Streamlit Community Cloud permite crear, desplegar y gestionar aplicaciones **de forma gratuita**, conectando la cuenta directamente a repositorios de GitHub, públicos o privados. La plataforma se encarga de la contenerización, y la mayoría de aplicaciones arrancan en pocos minutos.

El flujo es:

```
Tu código  →  repositorio de GitHub  →  Streamlit Cloud  →  URL pública
                      ↑                        │
                      └── cada push redespliega automáticamente
```

## 8.2 Requisitos previos

1. Una cuenta de **GitHub** (gratuita).
2. Una cuenta en **share.streamlit.io** (se crea con la de GitHub).
3. Un repositorio con, como mínimo, dos ficheros:
   - `streamlit_app.py` — la aplicación
   - `requirements.txt` — las dependencias

## 8.3 Estructura del repositorio

```
mi-app-streamlit/
├── streamlit_app.py         # la aplicación (nombre por convención)
├── requirements.txt         # dependencias
├── README.md                # opcional, documentación normal
└── .streamlit/
    └── config.toml          # opcional, tema y configuración
```

A diferencia de Hugging Face, **el `README.md` no lleva cabecera YAML**: aquí es documentación normal. Toda la configuración va en `.streamlit/config.toml` o se define en el propio panel de Streamlit.

## 8.4 El fichero `requirements.txt`

Todo paquete que importes debe estar listado. Streamlit trae algunos por defecto, pero conviene ser explícito:

```
streamlit>=1.40
scikit-learn>=1.4
numpy>=1.26
pandas>=2.2
matplotlib>=3.8
```

**Un consejo que evita muchos problemas:** aquí uso `>=` en lugar de `==`. La razón es que esta aplicación entrena el modelo en memoria, así que no hay ningún fichero serializado atado a una versión concreta de scikit-learn. Eso elimina de raíz toda una clase de errores de compatibilidad.

Si en cambio cargas un `.joblib`, entonces **sí** debes fijar la versión exacta con `==`, y asegurarte de que coincide con la que usaste al entrenar.

## 8.5 Fichero de configuración opcional

`.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2563eb"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f1f5f9"
textColor = "#0f172a"
font = "sans serif"

[server]
maxUploadSize = 50        # MB, por defecto 200
```

## 8.6 Paso a paso del despliegue

**Paso 1: crear el repositorio en GitHub**

Por la web: entra en [github.com/new](https://github.com/new), ponle un nombre, márcalo **Public**, y créalo. Después usa **Add file → Upload files** para subir `streamlit_app.py` y `requirements.txt`.

O por línea de comandos:

```bash
mkdir mi-app-streamlit && cd mi-app-streamlit
# copia aquí streamlit_app.py y requirements.txt

git init
git add .
git commit -m "Primera versión"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/mi-app-streamlit.git
git push -u origin main
```

**Paso 2: conectar Streamlit Cloud**

1. Entra en [share.streamlit.io](https://share.streamlit.io).
2. Pulsa **Sign in with GitHub** y autoriza el acceso.
3. Pulsa **Create app** (o **New app**).
4. Elige **Deploy a public app from GitHub**.

**Paso 3: configurar el despliegue**

Rellena tres campos:

- **Repository**: `TU_USUARIO/mi-app-streamlit`
- **Branch**: `main`
- **Main file path**: `streamlit_app.py`

Y opcionalmente el **App URL**, que puede contener letras, números y guiones. Si no lo pones, Streamlit genera uno automáticamente.

**Paso 4: elegir la versión de Python (importante)**

Despliega **Advanced settings** y selecciona la versión de Python.

> Este paso merece atención. Si tu código depende de una versión concreta de alguna librería, aquí es donde se decide la compatibilidad. Y hay un detalle crítico: **la versión de Python no se puede cambiar una vez desplegada la aplicación**. Para modificarla habría que borrar la app y volver a desplegarla. Elige bien a la primera.

**Paso 5: desplegar**

Pulsa **Deploy**. Verás el log de construcción en tiempo real. En unos minutos la aplicación estará en:

```
https://NOMBRE-ELEGIDO.streamlit.app
```

Esa URL es pública y permanente.

## 8.7 Actualizar la aplicación

No hay que hacer nada especial: **cada `git push` a la rama desplegada actualiza la aplicación automáticamente.** La mayoría de cambios aparecen de inmediato.

Un límite a tener en cuenta: Community Cloud limita las actualizaciones desde GitHub a un máximo de cinco por minuto.

```bash
# flujo de trabajo habitual
streamlit run streamlit_app.py     # probar en local
git add . && git commit -m "Mejora el gráfico"
git push                            # se despliega solo
```

## 8.8 Secretos

Nunca escribas claves en el código. En el panel de la aplicación: **Settings → Secrets**, con formato TOML:

```toml
API_KEY = "abc123"

[base_datos]
usuario = "admin"
password = "xxx"
```

Y en el código:

```python
clave = st.secrets["API_KEY"]
usuario = st.secrets["base_datos"]["usuario"]
```

Para desarrollo local, crea `.streamlit/secrets.toml` con el mismo contenido **y añádelo a `.gitignore`**.

## 8.9 Límites de la capa gratuita

Conviene conocerlos antes de diseñar:

| Aspecto | Límite |
|---|---|
| Coste | Gratuito |
| Memoria por aplicación | En torno a 1 GB de RAM |
| Repositorio | GitHub, público o privado |
| Hibernación | Las aplicaciones sin visitas se duermen y despiertan al recibir una |
| Actualizaciones | Máximo 5 por minuto |
| Sistema | Debian Linux |

El límite de memoria es el que más suele doler: **1 GB es poco** para modelos de deep learning. Para scikit-learn con datasets moderados es suficiente.

## 8.10 Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError` | Falta el paquete en `requirements.txt` | Añádelo y haz push |
| `Error installing requirements` | Versión inexistente para ese Python | Revisa el log; ajusta versión o Python |
| La app se queda "en el horno" | Suele ser falta de memoria | Reduce el modelo o los datos |
| `StreamlitAPIException: set_page_config()` | No es la primera instrucción `st.*` | Muévela justo tras los imports |
| `DuplicateWidgetID` | Dos widgets idénticos sin `key` | Añade `key="algo_unico"` |
| La app va lentísima | Falta caché | Añade `@st.cache_data` / `@st.cache_resource` |
| Los cambios no aparecen | Push a otra rama | Verifica la rama desplegada |
| `use_container_width` obsoleto | Parámetro retirado | Usa `width="stretch"` |

**Cómo depurar.** En el panel de la aplicación, abajo a la derecha, hay un botón **Manage app** que despliega los logs en vivo. Es el equivalente a los *Container logs* de Hugging Face.

Y como siempre: prueba primero en local con un entorno limpio.

```bash
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Si funciona así, funcionará desplegado.

---

# Módulo 9. Alternativas de despliegue

| Plataforma | Gratis | Complejidad | Cuándo elegirla |
|---|---|---|---|
| **Streamlit Community Cloud** | Sí | Muy baja | Opción por defecto para Streamlit |
| **Hugging Face Spaces** | Depende del plan | Baja | Si ya estás en el ecosistema HF |
| **Render** | Capa gratuita | Baja | Si necesitas más control |
| **Railway** | Crédito mensual | Baja | Con base de datos asociada |
| **Google Cloud Run** | Capa gratuita | Media | Producción, escalado automático |
| **Docker + VPS** | No | Alta | Datos sensibles, control total |

## 9.1 Streamlit en Hugging Face Spaces

Es posible, con la cabecera YAML correspondiente en el `README.md`:

```yaml
---
title: Clasificador Iris
emoji: 🌸
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.60.0
app_file: streamlit_app.py
pinned: false
---
```

Ten en cuenta que las condiciones del plan gratuito de Hugging Face para Spaces que consumen cómputo han cambiado y conviene verificarlas antes de contar con ello.

## 9.2 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 0.0.0.0 es imprescindible dentro de un contenedor
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t mi-app-streamlit .
docker run -p 8501:8501 mi-app-streamlit
```

La ruta `/_stcore/health` es el punto de comprobación de salud que expone Streamlit: devuelve `ok` si el servidor responde. Sirve tanto para Docker como para balanceadores de carga.

---

# Módulo 10. Buenas prácticas y errores frecuentes

## 10.1 Estructura del código

**Separa la lógica de la interfaz.** Igual que en Gradio: las funciones que calculan no deberían importar Streamlit.

```python
# logica.py
def predecir(modelo, medidas):
    return modelo.predict([medidas])[0]

# streamlit_app.py
from logica import predecir
```

Así puedes escribir tests con pytest sin arrancar ningún servidor.

**Cachea todo lo caro.** Es la optimización con mayor retorno en Streamlit. Si algo tarda más de un segundo y no depende de la interacción, va cacheado.

**Usa `st.stop()` en lugar de anidar `if`.** Hace el código mucho más legible:

```python
# En lugar de esto
if archivo is not None:
    if columna in df.columns:
        if len(df) > 10:
            procesar()

# Esto
if archivo is None:
    st.info("Sube un fichero")
    st.stop()
if columna not in df.columns:
    st.error(f"No existe la columna '{columna}'")
    st.stop()
procesar()
```

## 10.2 Rendimiento

- **Cachea la carga de modelos y datos** (módulo 5).
- **Usa formularios** cuando haya muchos campos: evita re-ejecuciones por cada tecla.
- **Usa `@st.fragment`** para paneles que se refrescan solos sin relanzar todo.
- **No cargues DataFrames enormes en memoria.** Con 1 GB de límite, filtra antes.
- **Evita `pyplot` global**: usa la clase `Figure` para no acumular figuras.

## 10.3 Experiencia de usuario

- Controles en la **barra lateral**, resultados en el área principal.
- `st.metric` para el resultado principal: destaca visualmente.
- `help="..."` en los widgets para explicar qué hace cada uno.
- Avisa de las **limitaciones del modelo** con `st.caption` o `st.info`.
- `st.spinner` en toda operación que tarde más de un segundo.
- Ofrece **descarga de resultados** con `st.download_button`.

## 10.4 Los cinco errores que más tiempo cuestan

1. **Olvidar la caché.** La aplicación funciona pero es insoportablemente lenta.
2. **`st.set_page_config()` en el sitio equivocado.** Debe ser la primera llamada `st.*`.
3. **Esperar que `st.button()` recuerde su estado.** Solo es `True` en la re-ejecución inmediata; para persistir, `session_state`.
4. **Ejecutar con `python` en vez de `streamlit run`.** No da error claro, simplemente no funciona.
5. **Elegir mal la versión de Python al desplegar.** No se puede cambiar después.

---

# Apéndice A. Chuleta de referencia rápida

## Esqueleto de una aplicación

```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mi app", layout="wide")   # SIEMPRE primero

@st.cache_resource
def cargar_modelo():
    return joblib.load("modelo.joblib")

modelo = cargar_modelo()

with st.sidebar:
    parametro = st.slider("Parámetro", 0, 100, 50)

st.title("Mi aplicación")
resultado = modelo.predict([[parametro]])[0]
st.metric("Resultado", resultado)
```

## Entradas

```python
st.text_input()      st.number_input()    st.slider()
st.checkbox()        st.radio()           st.selectbox()
st.multiselect()     st.file_uploader()   st.date_input()
st.button()          st.download_button() st.camera_input()
```

## Salidas

```python
st.write()           st.markdown()        st.dataframe()
st.metric()          st.pyplot()          st.plotly_chart()
st.json()            st.code()            st.latex()
st.success()         st.info()            st.warning()      st.error()
```

## Layout

```python
with st.sidebar: ...
col1, col2 = st.columns([2, 1])
tab1, tab2 = st.tabs(["A", "B"])
with st.expander("Más"): ...
with st.container(border=True): ...
hueco = st.empty()
```

## Caché

```python
@st.cache_data          # DataFrames, listas, dicts (copia por usuario)
@st.cache_resource      # modelos, conexiones (objeto compartido)

mi_funcion.clear()      # invalidar
```

## Estado

```python
if "clave" not in st.session_state:
    st.session_state.clave = valor_inicial

st.session_state.clave = nuevo_valor
st.rerun()              # forzar re-ejecución
st.stop()               # detener el script aquí
```

## Ejecución

```bash
streamlit run app.py
streamlit run app.py --server.port 8502
streamlit run app.py --server.address 0.0.0.0
```

---

# Apéndice B. Comparativa Streamlit / Gradio

| Aspecto | Streamlit | Gradio |
|---|---|---|
| Modelo mental | Script que se re-ejecuta | Función con interfaz |
| Reactividad | Automática, siempre | Hay que conectar eventos |
| Ejecución | `streamlit run app.py` | `python app.py` |
| Fichero de entrada | `streamlit_app.py` | `app.py` |
| Caché | Imprescindible (`@st.cache_*`) | Basta con cargar fuera de la función |
| Estado | `st.session_state` | `gr.State` |
| Despliegue gratuito | Community Cloud (vía GitHub) | HF Spaces (verificar plan) |
| Configuración del despliegue | Panel web + `config.toml` | Cabecera YAML del README |
| Memoria en capa gratuita | ~1 GB | 16 GB en CPU Basic |
| Multimedia | Correcto | Excelente |
| API REST automática | No | Sí |
| Multipágina | Nativo (carpeta `pages/`) | Manual |
| Personalización visual | Media (tema + CSS) | Media (temas + CSS) |

## Qué elegir para este proyecto

Para el clasificador de Iris, **ambos sirven igual de bien**. La decisión aquí ha sido práctica: Streamlit Community Cloud ofrece un despliegue gratuito claro y estable vía GitHub, mientras que las condiciones del plan gratuito de Hugging Face para Spaces con cómputo han cambiado.

Para un proyecto con imágenes, audio o vídeo —como el clasificador de enfermedades de plantas—, Gradio seguiría siendo preferible por sus componentes multimedia y por su API automática.

---

## Recursos

- Documentación oficial: `docs.streamlit.io`
- Referencia de la API: `docs.streamlit.io/develop/api-reference`
- Galería de ejemplos: `streamlit.io/gallery`
- Community Cloud: `share.streamlit.io`
- Foro: `discuss.streamlit.io`
- Estado del servicio: `streamlitstatus.com`
