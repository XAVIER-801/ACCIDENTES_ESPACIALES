# ONSV · Monitoreo de Seguridad Vial (Siniestros 2021-2023)

Este es un dashboard interactivo de alta fidelidad diseñado para monitorear, geolocalizar y analizar los siniestros viales registrados en el Perú durante el período 2021-2023. La aplicación está construida sobre **Python**, utilizando **Dash** y **Plotly** para el renderizado interactivo, con un diseño premium y responsivo de tipo *Glassmorphism* (cristal neumórfico) optimizado para analistas y toma de decisiones.

## 🚀 Características Clave

* **Geolocalización en Tiempo Real:** Mapa interactivo integrado sobre Mapbox (`carto-darkmatter`) para la visualización geoespacial de accidentes según su gravedad y tipo.
* **Filtros Interactivos Avanzados (Pill-Bar style):** Filtros rápidos autogestionados de Región, Año, Tipo de Vía y Clase de Siniestro, con capacidad de búsqueda interna ultra-rápida (gracias a `clientside_callback` ejecutándose en el navegador).
* **Métricas Clave (KPIs):** Indicadores principales dinámicos (Total Siniestros, Fallecidos, Lesionados, Letalidad, Siniestros en Carretera) con diseño de bordes neón y gradientes.
* **Alertas de Accidentes Críticos:** Lista dinámica de siniestros de extrema gravedad con badges de clasificación de riesgo.
* **Análisis de Distribución Temporal y Riesgo:** Matriz de calor (horario y semanal) para identificar horas y días pico de incidentes.

## 🛠️ Tecnologías y Estructura

El proyecto sigue una estructura limpia, separando la lógica del servidor de la presentación visual para optimizar el rendimiento y evitar advertencias del linter:

```text
EstEspacial/
├── EstEspacial/
│   ├── assets/
│   │   ├── styles.css           # Estilos CSS premium (Glassmorphism, Dark Theme, Dropdowns)
│   │   └── pill_filters.js      # Interactividad nativa JS para apertura/cierre de menús
│   ├── BBDD ONSV...xlsx         # Base de datos en formato Excel
│   └── dashboard_siniestros.py  # Archivo principal de la aplicación y lógica Dash/Python
├── .gitignore                   # Exclusiones de archivos temporales
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Documentación del proyecto
```

## 💻 Instalación y Uso

### 1. Clonar el repositorio
Si ya subiste este repositorio a GitHub, clónalo localmente:
```bash
git clone <url-de-tu-repositorio>
cd EstEspacial
```

### 2. Instalar dependencias
Se recomienda utilizar un entorno virtual para correr el proyecto:
```bash
# Crear entorno virtual
python -m venv venv
# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
Para iniciar el servidor local del dashboard:
```bash
python EstEspacial/dashboard_siniestros.py
```
Abre en tu navegador la dirección que se muestra en consola (por defecto: **http://127.0.0.1:8055**).
