# Machine Learning 1 — libro (Jupyter Book)

Libro de la asignatura construido con [Jupyter Book](https://jupyterbook.org). El contenido vive en cuadernos `.ipynb` y páginas `.md`, organizado en ocho bloques.

## Estructura

```
.
├── _config.yml          # título, autor, logo, tema, botones de Colab/GitHub, ejecución
├── _toc.yml             # tabla de contenidos (orden y qué entra en el libro)
├── intro.md             # portada
├── requirements.txt     # dependencias
├── bloque1/             # 1) Fundamentos de matemáticas y aprendizaje automático
│   ├── A_01_fundamentos_matematicas_ML.ipynb
│   └── A_02_introduccion_aprendizaje_automatico.ipynb
├── bloque2/ … bloque8/  # resto de bloques (con página placeholder index.md)
└── .github/workflows/deploy.yml   # publicación automática en GitHub Pages
```

## Editar el contenido (lo más habitual)

- **Cambiar texto o código:** edita el `.ipynb` correspondiente (en Colab, Jupyter o VS Code). No hay que tocar nada más.
- **Añadir un cuaderno:** copia el `.ipynb` en la carpeta del bloque (p. ej. `bloque3/`) y **añade una línea** en `_toc.yml`:
  ```yaml
      - file: bloque3/nombre_del_cuaderno   # sin la extensión .ipynb
  ```
- **Quitar un cuaderno:** borra su línea en `_toc.yml` (y, si quieres, el fichero).
- **Reordenar:** cambia el orden de las líneas en `_toc.yml`.
- **Renombrar bloques o el título:** los títulos de los bloques están en `_toc.yml` (`caption:`); el título del libro, en `_config.yml`.

## Construir y previsualizar en local

```bash
pip install -r requirements.txt        # solo la primera vez
jupyter-book build .                   # construye el sitio
```

El resultado queda en `_build/html/index.html`; ábrelo en el navegador. Para forzar una reconstrucción limpia: `jupyter-book build . --all`.

## Publicar en GitHub Pages (automático)

1. Crea un repositorio en GitHub y sube esta carpeta:
   ```bash
   git init && git add . && git commit -m "Libro ML1"
   git branch -M main
   git remote add origin https://github.com/USUARIO/ml-book.git
   git push -u origin main
   ```
2. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. En `_config.yml`, cambia `repository.url` por la URL real de tu repo (para que funcionen los botones «Open in Colab» y el enlace al repositorio).

A partir de ahí, **cada `git push` reconstruye y publica el libro** mediante la acción de `.github/workflows/deploy.yml`. La web quedará en `https://USUARIO.github.io/ml-book/`.

## Ejecución de los cuadernos

Por defecto (`execute_notebooks: "off"` en `_config.yml`) el libro **no ejecuta** los cuadernos: muestra las salidas ya guardadas en cada `.ipynb`. Es lo recomendable si dependen de datos o rutas de Colab. Si quieres que se ejecuten al construir, cambia esa opción a `"auto"` o `"force"` y asegúrate de que `requirements.txt` incluye todas las librerías necesarias.
