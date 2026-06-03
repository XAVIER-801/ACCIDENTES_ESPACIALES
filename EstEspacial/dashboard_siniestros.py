# -*- coding: utf-8 -*-
# Refrescando linter de la IDE
"""
Dashboard de Seguridad Vial - ONSV (Siniestros 2021-2023)
Diseño de Alta Fidelidad y UI/UX Premium (Inspiración en Supply Chain Route Planner)
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, dash_table
import warnings
warnings.filterwarnings('ignore')

# ── 1. CARGA Y PREPROCESAMIENTO DE DATOS ──────────────────────────────────────
print("Iniciando carga de datos...")
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "BBDD ONSV - SINIESTROS 2021-2023.xlsx")

if not os.path.exists(file_path):
    print(f"Error crítico: Archivo no encontrado en {file_path}")
    sys.exit(1)

# Cargar base de datos
try:
    df = pd.read_excel(file_path, sheet_name="SINIESTROS")
    print(f"Cargados exitosamente {len(df)} registros.")
except Exception as e:
    print(f"Error al leer el archivo Excel: {e}")
    sys.exit(1)

# Normalizar y limpiar nombres de columnas para evitar problemas de codificación
rename_map = {}
for col in df.columns:
    col_upper = col.upper()
    if "CDIGO" in col_upper or "CODIGO" in col_upper or "C\u00d3DIGO" in col_upper:
        rename_map[col] = "codigo"
    elif "FECHA" in col_upper:
        rename_map[col] = "fecha"
    elif "HORA" in col_upper:
        rename_map[col] = "hora"
    elif "CLASE" in col_upper:
        rename_map[col] = "clase"
    elif "FALLECIDOS" in col_upper:
        rename_map[col] = "fallecidos"
    elif "LESIONADOS" in col_upper:
        rename_map[col] = "lesionados"
    elif "VEHICULOS" in col_upper or "VEHCULOS" in col_upper or "VEHICULO" in col_upper:
        rename_map[col] = "vehiculos_danados"
    elif "DEPARTAMENTO" in col_upper:
        rename_map[col] = "departamento"
    elif "PROVINCIA" in col_upper:
        rename_map[col] = "provincia"
    elif "DISTRITO" in col_upper:
        rename_map[col] = "distrito"
    elif "ZONA" in col_upper:
        rename_map[col] = "zona"
    elif "TIPO DE" in col_upper or "TIPO_DE" in col_upper:
        rename_map[col] = "tipo_via"
    elif "RED VIAL" in col_upper or "RED_VIAL" in col_upper:
        rename_map[col] = "red_vial"
    elif "COD CARRETERA" in col_upper:
        rename_map[col] = "cod_carretera"
    elif "CICLOV" in col_upper:
        rename_map[col] = "existe_ciclovia"
    elif "LATITUD" in col_upper:
        rename_map[col] = "lat"
    elif "LONGITUD" in col_upper and "LONGITUDINAL" not in col_upper:
        rename_map[col] = "lon"
    elif "CLIM" in col_upper:
        rename_map[col] = "clima"
    elif "ZONIFICAC" in col_upper:
        rename_map[col] = "zonificacion"
    elif "CARACTER" in col_upper:
        rename_map[col] = "caracteristicas_via"
    elif "PERFIL" in col_upper:
        rename_map[col] = "perfil_longitudinal"
    elif "SUPERFICIE" in col_upper:
        rename_map[col] = "superficie_calzada"
    elif "SEAL VERTICAL" in col_upper or "SEÑAL VERTICAL" in col_upper or "SENAL VERTICAL" in col_upper:
        if "1" in col_upper:
            rename_map[col] = "senal_vertical_1"
        elif "2" in col_upper:
            rename_map[col] = "senal_vertical_2"
        else:
            rename_map[col] = "existe_senal_vertical"
    elif "SEAL HORIZONTAL" in col_upper or "SEÑAL HORIZONTAL" in col_upper or "SENAL HORIZONTAL" in col_upper:
        rename_map[col] = "existe_senal_horizontal"
    elif "CAUSA FACTOR" in col_upper or "CAUSA_FACTOR" in col_upper:
        rename_map[col] = "causa_principal"
    elif "CAUSA ESPEC" in col_upper or "CAUSA_ESPEC" in col_upper:
        rename_map[col] = "causa_especifica"

df = df.rename(columns=rename_map)

# Preprocesamiento de variables temporales
df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
df['year'] = df['fecha_parsed'].dt.year.fillna(2022).astype(int)
df['month'] = df['fecha_parsed'].dt.month.fillna(1).astype(int)
df['month_name'] = df['fecha_parsed'].dt.strftime('%b')
df['day_name'] = df['fecha_parsed'].dt.day_name()
df['day_of_week'] = df['fecha_parsed'].dt.dayofweek.fillna(0).astype(int)

# Corregir horas
def extract_hour(x):
    try:
        val = str(x).strip()
        if ':' in val:
            return int(val.split(':')[0])
        else:
            # Intentar convertir número flotante
            return int(float(val))
    except:
        return 12 # Mediodía por defecto si hay error

df['hour'] = df['hora'].apply(extract_hour)

# Normalizar cadenas de texto importantes para visualización
df['clase'] = df['clase'].str.upper().str.strip().fillna("OTRO")
df['departamento'] = df['departamento'].str.upper().str.strip().fillna("DESCONOCIDO")
df['zona'] = df['zona'].str.upper().str.strip().fillna("RURAL")
df['tipo_via'] = df['tipo_via'].str.upper().str.strip().fillna("CARRETERA")
df['causa_principal'] = df['causa_principal'].str.upper().str.strip().fillna("NO IDENTIFICA LA CAUSA")
df['clima'] = df['clima'].str.upper().str.strip().fillna("DESPEJADO")

# Limpiar valores nulos en fallecidos y lesionados
df['fallecidos'] = df['fallecidos'].fillna(1).astype(int)
df['lesionados'] = df['lesionados'].fillna(0).astype(int)
df['vehiculos_danados'] = df['vehiculos_danados'].fillna(1).astype(int)

# Convertir coordenadas a numérico de forma segura y filtrar nulos
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
df = df.dropna(subset=['lat', 'lon'])

# Bounding box para Perú
df = df[(df['lat'] >= -19) & (df['lat'] <= -3) & (df['lon'] >= -82) & (df['lon'] <= -68)]

# Listas de filtros únicos
DEPARTAMENTOS = sorted(df['departamento'].unique().tolist())
ANOS = sorted(df['year'].unique().tolist())
CLASES = sorted(df['clase'].unique().tolist())
VIAS = sorted(df['tipo_via'].unique().tolist())

DAYS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
DAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAY_MAP = dict(zip(DAYS_EN, DAYS_ES))
df['day_es'] = df['day_name'].map(DAY_MAP).fillna('Lunes')

print("Preprocesamiento completado con éxito.")

# ── 2. CONSTANTES DE DISEÑO PREMIUM (PALETA DE LA IMAGEN) ────────────────────
DARK_BG = "#080b11"       # Azul ultra-oscuro de fondo general
CARD_BG = "#111622"       # Fondo de las tarjetas con opacidad
CARD_BORDER = "#1f2937"   # Borde gris oscuro
TEXT_COLOR = "#f1f5f9"    # Blanco/Gris brillante para texto
LABEL_COLOR = "#94a3b8"   # Slate grisáceo para etiquetas

# Paleta Neón / Resplandor
CYAN_ACCENT = "#38bdf8"    # Azul cian brillante (Métricas de siniestros, botones)
CORAL_ACCENT = "#ff7a45"   # Naranja/Coral neón (Métricas de fallecidos, zonas de alto riesgo)
EMERALD_ACCENT = "#059669" # Verde esmeralda (Lesionados, estado estable)
AMBER_ACCENT = "#d97706"   # Amarillo/Dorado (Letalidad e infraestructura)
PURPLE_ACCENT = "#c084fc"  # Púrpura (Carreteras)

# Mapa de colores para Clase de Siniestro
CLASE_COLORS = {
    'CHOQUE': CYAN_ACCENT,
    'DESPISTE': CORAL_ACCENT,
    'ATROPELLO': PURPLE_ACCENT,
    'ATROPELLO FUGA': AMBER_ACCENT,
    'VOLCADURA': "#10b981",
    'CHOQUE FUGA': "#ec4899",
    'CHOQUE CON OBJETO FIJO': "#a855f7",
    'CAÍDA DE PASAJERO': "#f43f5e",
    'ESPECIAL': "#64748b",
    'FERROVIARIO': "#e2e8f0"
}

# Configuración base de gráficos Plotly
PLOTLY_THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_COLOR, family="Segoe UI, system-ui, sans-serif"),
    margin=dict(l=40, r=20, t=30, b=40),
    legend=dict(
        bgcolor="rgba(17, 22, 34, 0.8)",
        font=dict(size=10, color=TEXT_COLOR)
    ),
    xaxis=dict(
        gridcolor="#1e293b",
        linecolor="#1e293b",
        zerolinecolor="#1e293b",
        tickfont=dict(color=LABEL_COLOR, size=10)
    ),
    yaxis=dict(
        gridcolor="#1e293b",
        linecolor="#1e293b",
        zerolinecolor="#1e293b",
        tickfont=dict(color=LABEL_COLOR, size=10)
    ),
)

# ── 3. ESTRUCTURACIÓN DE COMPONENTES REUTILIZABLES ───────────────────────────
def create_kpi_card(title, value_id, sub_id, icon, glow_color):
    """Crea una tarjeta de KPI dinámica con borde neón y resplandor de color."""
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "24px", "color": glow_color, "marginRight": "12px"}),
                html.Div([
                    html.Div(title, style={"color": LABEL_COLOR, "fontSize": "11px", "fontWeight": "700", "textTransform": "uppercase", "letterSpacing": "1.5px"}),
                    html.Div(id=value_id, style={"color": TEXT_COLOR, "fontSize": "26px", "fontWeight": "800", "marginTop": "2px"}),
                ])
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(id=sub_id, style={
                "fontSize": "11px",
                "color": glow_color,
                "fontWeight": "600",
                "background": f"{glow_color}15",
                "padding": "3px 8px",
                "borderRadius": "20px",
                "border": f"1px solid {glow_color}30",
                "marginTop": "4px",
                "alignSelf": "flex-start"
            })
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "width": "100%"})
    ], className="card-kpi", style={
        "borderLeft": f"4px solid {glow_color}",
        "boxShadow": f"0 4px 20px {glow_color}0d",
        "flex": "1",
        "minWidth": "200px"
    })

# ── 4. APLICACIÓN DASH ────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Portal ONSV — Observatorio de Seguridad Vial")
app.config.suppress_callback_exceptions = True

# Enrutamiento de excepciones a stdout para visibilidad de logs en segundo plano
import sys
import traceback
@app.server.errorhandler(Exception)
def handle_exception(e):
    print("\n--- EXCEPCION CRITICA EN EL SERVIDOR ---", file=sys.stdout)
    traceback.print_exc(file=sys.stdout)
    sys.stdout.flush()
    return "Internal Server Error", 500

app.layout = html.Div([
    
    # HEADER (Estilo de la imagen con barra de estado y título elegante)
    html.Div([
        html.Div([
            html.Div(style={
                "width": "5px", "height": "32px", "background": CYAN_ACCENT, 
                "borderRadius": "3px", "marginRight": "12px", 
                "boxShadow": f"0 0 10px {CYAN_ACCENT}"
            }),
            html.Div([
                html.H1("MONITOREO DE SEGURIDAD VIAL · ONSV",
                    style={"color": TEXT_COLOR, "fontSize": "20px", "fontWeight": "900", "margin": "0", "letterSpacing": "1.5px"}),
                html.Div("Plataforma Inteligente de Siniestros Fatales y Análisis de Vías · 2021–2023",
                    style={"color": LABEL_COLOR, "fontSize": "11px", "marginTop": "2px", "fontWeight": "600", "letterSpacing": "0.5px"}),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),
        
        # Estado de conexión de datos
        html.Div([
            html.Div("BASE DE DATOS ONSV ACTIVA", style={
                "background": "rgba(5, 150, 105, 0.15)", "color": "#10b981", 
                "borderRadius": "20px", "border": "1px solid rgba(16, 185, 129, 0.3)",
                "padding": "6px 14px", "fontSize": "10px", "fontWeight": "800", 
                "marginRight": "12px", "letterSpacing": "1px",
                "boxShadow": "0 0 10px rgba(16, 185, 129, 0.15)"
            }),
            html.Div(f"{len(df):,} REGISTROS", style={
                "background": "rgba(56, 189, 248, 0.15)", "color": CYAN_ACCENT, 
                "borderRadius": "20px", "border": f"1px solid {CYAN_ACCENT}30",
                "padding": "6px 14px", "fontSize": "10px", "fontWeight": "800",
                "letterSpacing": "1px"
            }),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={
        "background": f"linear-gradient(90deg, {CARD_BG} 0%, rgba(17,22,34,0.3) 100%)",
        "padding": "16px 30px", "borderBottom": f"1px solid {CARD_BORDER}",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "boxShadow": "0 4px 30px rgba(0,0,0,0.5)"
    }),

    # FILA DE KPIs (5 Tarjetas horizontales de alta fidelidad)
    html.Div([
        create_kpi_card("Siniestros Fatales", "kpi-siniestros", "kpi-siniestros-sub", "", CYAN_ACCENT),
        create_kpi_card("Total Fallecidos", "kpi-fallecidos", "kpi-fallecidos-sub", "", CORAL_ACCENT),
        create_kpi_card("Total Lesionados", "kpi-lesionados", "kpi-lesionados-sub", "", EMERALD_ACCENT),
        create_kpi_card("Índice de Letalidad", "kpi-letalidad", "kpi-letalidad-sub", "", AMBER_ACCENT),
        create_kpi_card("Zonas de Carretera", "kpi-carreteras", "kpi-carreteras-sub", "", PURPLE_ACCENT),
    ], style={
        "display": "flex", "gap": "14px", "padding": "16px 30px 10px 30px", 
        "flexWrap": "wrap", "background": DARK_BG
    }),

    # ── BARRA HORIZONTAL DE FILTROS (estilo boceto: pill-chips + badge + chevron) ──
    html.Div([
        # HIDDEN dropdowns (Dash callbacks los leen)
        html.Div([
            dcc.Dropdown(id="filter-depts",  options=[{"label": d, "value": d} for d in DEPARTAMENTOS], value=None, multi=True),
            dcc.Dropdown(id="filter-years",  options=[{"label": str(y), "value": y} for y in ANOS],       value=None, multi=True),
            dcc.Dropdown(id="filter-vias",   options=[{"label": v, "value": v} for v in VIAS],             value=None, multi=True),
            dcc.Dropdown(id="filter-clases", options=[{"label": c, "value": c} for c in CLASES],           value=None, multi=True),
            # Stores para el estado de cada filtro
            dcc.Store(id="store-depts",  data=None),
            dcc.Store(id="store-years",  data=None),
            dcc.Store(id="store-vias",   data=None),
            dcc.Store(id="store-clases", data=None),
            # Stores con opciones COMPLETAS (para poder restaurar al limpiar el buscador)
            dcc.Store(id="all-opts-depts",  data=[{"label": d, "value": d} for d in DEPARTAMENTOS]),
            dcc.Store(id="all-opts-years",  data=[{"label": str(y), "value": y} for y in ANOS]),
            dcc.Store(id="all-opts-vias",   data=[{"label": v, "value": v} for v in VIAS]),
            dcc.Store(id="all-opts-clases", data=[{"label": c, "value": c} for c in CLASES]),
        ], style={"display": "none"}),

        # Etiqueta
        html.Div("FILTROS", style={
            "color": LABEL_COLOR, "fontSize": "10px", "fontWeight": "800",
            "letterSpacing": "1.5px", "whiteSpace": "nowrap", "alignSelf": "center",
            "paddingRight": "12px"
        }),

        # Separador vertical izquierdo
        html.Div(style={"width": "1px", "height": "34px", "background": "rgba(255,255,255,0.08)", "flexShrink": "0"}),

        # ── FILTRO 1: REGIONES ──────────────────────────────────────────────────
        html.Div([
            html.Div(id="pill-bar-depts", className="pill-filter-bar", **{"data-filter": "depts"}, children=[
                html.Span("REGIONES", className="pill-filter-label"),
                html.Div(style={"width": "1px", "height": "18px", "background": "rgba(255,255,255,0.12)", "flexShrink": "0"}),
                html.Div(id="pill-chips-depts", className="pill-chips-zone"),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("✕", id="pill-clear-depts", className="pill-clear-btn", n_clicks=0),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("▾", id="pill-chevron-depts", className="pill-chevron"),
            ]),
            # Panel flotante de opciones
            html.Div(id="pill-panel-depts", className="pill-panel", style={"display": "none"}, children=[
                html.Div([
                    dcc.Input(id="pill-search-depts", type="text", placeholder="Buscar región...", className="pill-search", debounce=False),
                    html.Div([
                        html.Button("Todo",  id="pill-all-depts",   n_clicks=0, className="pill-action-btn"),
                        html.Button("Ninguno", id="pill-none-depts", n_clicks=0, className="pill-action-btn pill-action-none"),
                    ], style={"display": "flex", "gap": "6px", "padding": "6px 10px"}),
                    html.Div(
                        dcc.Checklist(
                            id="chklist-depts",
                            options=[{"label": d, "value": d} for d in DEPARTAMENTOS],
                            value=[],
                            className="pill-checklist",
                            inputClassName="pill-chk",
                            labelClassName="pill-chk-label",
                            inputStyle={"accentColor": CYAN_ACCENT},
                            labelStyle={"color": TEXT_COLOR, "fontSize": "12px", "cursor": "pointer"}
                        ),
                        className="pill-options-list custom-scrollbar", id="pill-opts-depts"
                    )
                ])
            ])
        ], style={"position": "relative", "flex": "1", "minWidth": "0"}),

        # Separador
        html.Div(style={"width": "1px", "height": "34px", "background": "rgba(255,255,255,0.08)", "flexShrink": "0"}),

        # ── FILTRO 2: AÑO ──────────────────────────────────────────────────────
        html.Div([
            html.Div(id="pill-bar-years", className="pill-filter-bar", **{"data-filter": "years"}, children=[
                html.Span("AÑO", className="pill-filter-label"),
                html.Div(style={"width": "1px", "height": "18px", "background": "rgba(255,255,255,0.12)", "flexShrink": "0"}),
                html.Div(id="pill-chips-years", className="pill-chips-zone"),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("✕", id="pill-clear-years", className="pill-clear-btn", n_clicks=0),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("▾", id="pill-chevron-years", className="pill-chevron"),
            ]),
            html.Div(id="pill-panel-years", className="pill-panel", style={"display": "none"}, children=[
                html.Div([
                    dcc.Input(id="pill-search-years", type="text", placeholder="Buscar año...", className="pill-search", debounce=False),
                    html.Div([
                        html.Button("Todo",  id="pill-all-years",   n_clicks=0, className="pill-action-btn"),
                        html.Button("Ninguno", id="pill-none-years", n_clicks=0, className="pill-action-btn pill-action-none"),
                    ], style={"display": "flex", "gap": "6px", "padding": "6px 10px"}),
                    html.Div(
                        dcc.Checklist(
                            id="chklist-years",
                            options=[{"label": str(y), "value": y} for y in ANOS],
                            value=[],
                            className="pill-checklist",
                            inputClassName="pill-chk",
                            labelClassName="pill-chk-label",
                            inputStyle={"accentColor": CYAN_ACCENT},
                            labelStyle={"color": TEXT_COLOR, "fontSize": "12px", "cursor": "pointer"}
                        ),
                        className="pill-options-list custom-scrollbar", id="pill-opts-years"
                    )
                ])
            ])
        ], style={"position": "relative", "flex": "1", "minWidth": "0"}),

        # Separador
        html.Div(style={"width": "1px", "height": "34px", "background": "rgba(255,255,255,0.08)", "flexShrink": "0"}),

        # ── FILTRO 3: TIPO VÍA ─────────────────────────────────────────────────
        html.Div([
            html.Div(id="pill-bar-vias", className="pill-filter-bar", **{"data-filter": "vias"}, children=[
                html.Span("TIPO VÍA", className="pill-filter-label"),
                html.Div(style={"width": "1px", "height": "18px", "background": "rgba(255,255,255,0.12)", "flexShrink": "0"}),
                html.Div(id="pill-chips-vias", className="pill-chips-zone"),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("✕", id="pill-clear-vias", className="pill-clear-btn", n_clicks=0),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("▾", id="pill-chevron-vias", className="pill-chevron"),
            ]),
            html.Div(id="pill-panel-vias", className="pill-panel", style={"display": "none"}, children=[
                html.Div([
                    dcc.Input(id="pill-search-vias", type="text", placeholder="Buscar tipo de vía...", className="pill-search", debounce=False),
                    html.Div([
                        html.Button("Todo",  id="pill-all-vias",   n_clicks=0, className="pill-action-btn"),
                        html.Button("Ninguno", id="pill-none-vias", n_clicks=0, className="pill-action-btn pill-action-none"),
                    ], style={"display": "flex", "gap": "6px", "padding": "6px 10px"}),
                    html.Div(
                        dcc.Checklist(
                            id="chklist-vias",
                            options=[{"label": v, "value": v} for v in VIAS],
                            value=[],
                            className="pill-checklist",
                            inputClassName="pill-chk",
                            labelClassName="pill-chk-label",
                            inputStyle={"accentColor": CYAN_ACCENT},
                            labelStyle={"color": TEXT_COLOR, "fontSize": "12px", "cursor": "pointer"}
                        ),
                        className="pill-options-list custom-scrollbar", id="pill-opts-vias"
                    )
                ])
            ])
        ], style={"position": "relative", "flex": "1", "minWidth": "0"}),

        # Separador
        html.Div(style={"width": "1px", "height": "34px", "background": "rgba(255,255,255,0.08)", "flexShrink": "0"}),

        # ── FILTRO 4: CLASE SINIESTRO ──────────────────────────────────────────
        html.Div([
            html.Div(id="pill-bar-clases", className="pill-filter-bar", **{"data-filter": "clases"}, children=[
                html.Span("CLASE", className="pill-filter-label"),
                html.Div(style={"width": "1px", "height": "18px", "background": "rgba(255,255,255,0.12)", "flexShrink": "0"}),
                html.Div(id="pill-chips-clases", className="pill-chips-zone"),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("✕", id="pill-clear-clases", className="pill-clear-btn", n_clicks=0),
                html.Div(style={"width": "1px", "height": "22px", "background": "rgba(255,255,255,0.15)", "flexShrink": "0"}),
                html.Span("▾", id="pill-chevron-clases", className="pill-chevron"),
            ]),
            html.Div(id="pill-panel-clases", className="pill-panel", style={"display": "none"}, children=[
                html.Div([
                    dcc.Input(id="pill-search-clases", type="text", placeholder="Buscar clase...", className="pill-search", debounce=False),
                    html.Div([
                        html.Button("Todo",  id="pill-all-clases",   n_clicks=0, className="pill-action-btn"),
                        html.Button("Ninguno", id="pill-none-clases", n_clicks=0, className="pill-action-btn pill-action-none"),
                    ], style={"display": "flex", "gap": "6px", "padding": "6px 10px"}),
                    html.Div(
                        dcc.Checklist(
                            id="chklist-clases",
                            options=[{"label": c, "value": c} for c in CLASES],
                            value=[],
                            className="pill-checklist",
                            inputClassName="pill-chk",
                            labelClassName="pill-chk-label",
                            inputStyle={"accentColor": CYAN_ACCENT},
                            labelStyle={"color": TEXT_COLOR, "fontSize": "12px", "cursor": "pointer"}
                        ),
                        className="pill-options-list custom-scrollbar", id="pill-opts-clases"
                    )
                ])
            ])
        ], style={"position": "relative", "flex": "1", "minWidth": "0"}),

    ], style={
        "display": "flex", "alignItems": "center", "gap": "10px",
        "padding": "10px 30px", "background": CARD_BG,
        "borderBottom": f"1px solid {CARD_BORDER}",
        "borderTop": f"1px solid {CARD_BORDER}",
        "overflowX": "visible", "overflowY": "visible", "flexWrap": "nowrap",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.3)",
        "position": "relative", "zIndex": "9999"
    }),

    # AREA PRINCIPAL DE REJILLA (Dashboard Grid)
    html.Div([
        
        # COLUMNA IZQUIERDA: Alertas de Accidentes Críticos
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(style={"width": "3px", "height": "14px", "background": CORAL_ACCENT, "marginRight": "8px"}),
                        html.Div("ALERTAS DE ACCIDENTES CRÍTICOS", style={"color": TEXT_COLOR, "fontSize": "13px", "fontWeight": "800", "letterSpacing": "1px"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Div(id="alerts-count-badge", className="neon-badge-red")
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"}),
                
                # Lista de alertas con scroll cuando desborda
                html.Div(
                    id="alerts-list-container",
                    className="custom-scrollbar",
                    style={"overflowY": "auto", "flex": "1", "display": "flex", "flexDirection": "column", "gap": "10px", "minHeight": "0"}
                )
                
            ], className="card-glass", style={
                "padding": "20px",
                "border": f"1px solid {CORAL_ACCENT}30",
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
            })

        ], style={
            "minWidth": "280px", "maxWidth": "320px",
            "display": "flex", "flexDirection": "column",
            "alignSelf": "flex-start",
            "height": "830px",
        }),
        
        # COLUMNA CENTRAL: Gran Mapa y Tendencias Temporales
        html.Div([
            
            # Panel del Mapa Geoespacial (Inspiración "Route Map")
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(style={"width": "3px", "height": "14px", "background": CYAN_ACCENT, "marginRight": "8px"}),
                        html.Div("GEOLOCALIZACIÓN DE ACCIDENTES EN TIEMPO REAL", style={"color": TEXT_COLOR, "fontSize": "13px", "fontWeight": "800", "letterSpacing": "1px"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Div("Interactúe con el mapa para ver la gravedad exacta", style={"color": LABEL_COLOR, "fontSize": "10px", "fontWeight": "600"})
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "12px"}),
                
                # Gráfico del Mapa
                dcc.Graph(
                    id="geo-map",
                    style={"height": "460px", "borderRadius": "12px", "overflow": "hidden"},
                    config={"displayModeBar": True, "scrollZoom": True}
                )
            ], className="card-glass", style={"padding": "20px", "marginBottom": "16px"}),
            
            # Fila de Gráficos de Tendencias y Severidad (Línea + Barras)
            html.Div([
                # Gráfico de Línea Temporal (Inspiración "Lead Time Trend")
                html.Div([
                    html.Div([
                        html.Div(style={"width": "3px", "height": "12px", "background": CYAN_ACCENT, "marginRight": "6px"}),
                        html.Div("EVOLUCIÓN MENSUAL", style={"color": TEXT_COLOR, "fontSize": "12px", "fontWeight": "800", "letterSpacing": "0.5px"}),
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                    dcc.Graph(id="time-trend-chart", style={"height": "220px"}, config={"displayModeBar": False})
                ], className="card-glass", style={"flex": "1.2", "padding": "16px", "marginRight": "14px", "minWidth": "280px"}),
                
                # Gráfico de Letalidad por Vía (Inspiración "Cost Comparison")
                html.Div([
                    html.Div([
                        html.Div(style={"width": "3px", "height": "12px", "background": AMBER_ACCENT, "marginRight": "6px"}),
                        html.Div("LETALIDAD POR INFRAESTRUCTURA", style={"color": TEXT_COLOR, "fontSize": "12px", "fontWeight": "800", "letterSpacing": "0.5px"}),
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                    dcc.Graph(id="infrastructure-chart", style={"height": "220px"}, config={"displayModeBar": False})
                ], className="card-glass", style={"flex": "1", "padding": "16px", "minWidth": "240px"})
            ], style={"display": "flex", "flexWrap": "wrap"})

        ], style={"flex": "2.2", "display": "flex", "flexDirection": "column", "minWidth": "500px"}),

        # COLUMNA DERECHA: Alertas de Incidentes Críticos & Distribución Temporal
        html.Div([
            
            # Panel de Regiones Más Críticas
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(style={"width": "3px", "height": "14px", "background": CYAN_ACCENT, "marginRight": "8px"}),
                        html.Div("REGIONES MÁS CRÍTICAS", style={"color": TEXT_COLOR, "fontSize": "13px", "fontWeight": "800", "letterSpacing": "1px"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"}),
                
                # Lista de regiones críticas
                html.Div(
                    id="top-regions-list",
                    className="custom-scrollbar",
                    style={"overflowY": "auto", "maxHeight": "240px", "display": "flex", "flexDirection": "column", "gap": "10px"}
                )
                
            ], className="card-glass", style={"padding": "20px", "marginBottom": "16px", "border": f"1px solid {CYAN_ACCENT}30"}),
            
            # Panel de Factores de Riesgo e Impacto
            html.Div([
                html.Div([
                    html.Div(style={"width": "3px", "height": "14px", "background": PURPLE_ACCENT, "marginRight": "8px"}),
                    html.Div("MATRIZ DE RIESGO HORARIO Y SEMANAL", style={"color": TEXT_COLOR, "fontSize": "13px", "fontWeight": "800", "letterSpacing": "1px"}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px"}),
                
                dcc.Graph(id="heatmap-chart", style={"height": "395px"}, config={"displayModeBar": False})
                
            ], className="card-glass", style={"padding": "20px", "flex": "1"})

        ], style={"flex": "1.1", "minWidth": "300px", "maxWidth": "380px", "display": "flex", "flexDirection": "column"}),

    ], style={
        "display": "flex", "flexWrap": "wrap", "gap": "16px", 
        "padding": "16px 30px 30px 30px", "background": DARK_BG, "minHeight": "80vh",
        "position": "relative", "zIndex": "1"
    }),

], style={"background": DARK_BG, "minHeight": "100vh", "fontFamily": "'Segoe UI', system-ui, sans-serif"})


# ── 5. INTERACTIVIDAD Y CALLBACKS ─────────────────────────────────────────────

# Sync checklists → hidden dropdowns (directo, sin store intermedio)
@app.callback(
    Output("filter-depts", "value"),
    Input("chklist-depts", "value"),
    prevent_initial_call=False
)
def sync_filter_depts(val):
    return val or []

@app.callback(
    Output("filter-years", "value"),
    Input("chklist-years", "value"),
    prevent_initial_call=False
)
def sync_filter_years(val):
    return val or []

@app.callback(
    Output("filter-vias", "value"),
    Input("chklist-vias", "value"),
    prevent_initial_call=False
)
def sync_filter_vias(val):
    return val or []

@app.callback(
    Output("filter-clases", "value"),
    Input("chklist-clases", "value"),
    prevent_initial_call=False
)
def sync_filter_clases(val):
    return val or []


# ── BÚSQUEDA EN TIEMPO REAL (clientside callbacks — 100% en el navegador) ──────
# Filtra las opciones del checklist al escribir en el buscador.
# Al borrar el texto, restaura la lista completa desde el Store.
_SEARCH_JS = """
function(query, allOpts) {
    var q = (query || '').toLowerCase().trim();
    if (!q) return allOpts;
    return allOpts.filter(function(o) {
        return String(o.label || '').toLowerCase().indexOf(q) !== -1;
    });
}
"""

app.clientside_callback(
    _SEARCH_JS,
    Output("chklist-depts",  "options"),
    Input("pill-search-depts",  "value"),
    dash.dependencies.State("all-opts-depts",  "data"),
)
app.clientside_callback(
    _SEARCH_JS,
    Output("chklist-years",  "options"),
    Input("pill-search-years",  "value"),
    dash.dependencies.State("all-opts-years",  "data"),
)
app.clientside_callback(
    _SEARCH_JS,
    Output("chklist-vias",   "options"),
    Input("pill-search-vias",   "value"),
    dash.dependencies.State("all-opts-vias",   "data"),
)
app.clientside_callback(
    _SEARCH_JS,
    Output("chklist-clases", "options"),
    Input("pill-search-clases", "value"),
    dash.dependencies.State("all-opts-clases", "data"),
)

# Pill-bar chip display callbacks (update visual chips from checklist values)
@app.callback(
    Output("pill-chips-depts", "children"),
    Input("chklist-depts", "value")
)
def update_chips_depts(val):
    return _make_chips(val, DEPARTAMENTOS)

@app.callback(
    Output("pill-chips-years", "children"),
    Input("chklist-years", "value")
)
def update_chips_years(val):
    return _make_chips([str(v) for v in (val or [])], [str(y) for y in ANOS])

@app.callback(
    Output("pill-chips-vias", "children"),
    Input("chklist-vias", "value")
)
def update_chips_vias(val):
    return _make_chips(val, VIAS)

@app.callback(
    Output("pill-chips-clases", "children"),
    Input("chklist-clases", "value")
)
def update_chips_clases(val):
    return _make_chips(val, CLASES)

def _make_chips(selected, all_vals):
    """Build chip/badge children for the pill-bar chips zone."""
    selected = selected or []
    total = len(all_vals)
    if len(selected) == 0:
        return [html.Span("Todos (sin filtro)", className="pill-count-badge")]
    if len(selected) == total:
        return [html.Span(f"Todos ({total})", className="pill-count-badge")]
    MAX_VIS = 2
    chips = [html.Span(v, className="pill-chip") for v in selected[:MAX_VIS]]
    if len(selected) > MAX_VIS:
        chips.append(html.Span(f"{len(selected)} Seleccionados", className="pill-count-badge"))
    return chips

# Pill clear / select all / none callbacks
@app.callback(
    Output("chklist-depts", "value"),
    Input("pill-all-depts", "n_clicks"),
    Input("pill-none-depts", "n_clicks"),
    Input("pill-clear-depts", "n_clicks"),
    prevent_initial_call=True
)
def ctrl_depts(all_c, none_c, clear_c):
    from dash import ctx
    tid = ctx.triggered_id
    if tid == "pill-all-depts": return DEPARTAMENTOS
    if tid in ("pill-none-depts", "pill-clear-depts"): return []
    return []

@app.callback(
    Output("chklist-years", "value"),
    Input("pill-all-years", "n_clicks"),
    Input("pill-none-years", "n_clicks"),
    Input("pill-clear-years", "n_clicks"),
    prevent_initial_call=True
)
def ctrl_years(all_c, none_c, clear_c):
    from dash import ctx
    tid = ctx.triggered_id
    if tid == "pill-all-years": return ANOS
    if tid in ("pill-none-years", "pill-clear-years"): return []
    return []

@app.callback(
    Output("chklist-vias", "value"),
    Input("pill-all-vias", "n_clicks"),
    Input("pill-none-vias", "n_clicks"),
    Input("pill-clear-vias", "n_clicks"),
    prevent_initial_call=True
)
def ctrl_vias(all_c, none_c, clear_c):
    from dash import ctx
    tid = ctx.triggered_id
    if tid == "pill-all-vias": return VIAS
    if tid in ("pill-none-vias", "pill-clear-vias"): return []
    return []

@app.callback(
    Output("chklist-clases", "value"),
    Input("pill-all-clases", "n_clicks"),
    Input("pill-none-clases", "n_clicks"),
    Input("pill-clear-clases", "n_clicks"),
    prevent_initial_call=True
)
def ctrl_clases(all_c, none_c, clear_c):
    from dash import ctx
    tid = ctx.triggered_id
    if tid == "pill-all-clases": return CLASES
    if tid in ("pill-none-clases", "pill-clear-clases"): return []
    return []


def filter_data(depts, years, vias, clases):
    """Filtra el DataFrame según las opciones seleccionadas.
    Lista vacía = sin filtro (muestra todos los valores de esa dimensión).
    """
    mask = pd.Series([True] * len(df), index=df.index)
    if depts:
        mask &= df['departamento'].isin(depts)
    if years:
        mask &= df['year'].isin(years)
    if vias:
        mask &= df['tipo_via'].isin(vias)
    if clases:
        mask &= df['clase'].isin(clases)
    return df[mask]


def log_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(script_dir, "error_log.txt")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n--- EXCEPCION EN CALLBACK UPDATE_DASHBOARD ---\n")
                traceback.print_exc(file=f)
            raise e
    return wrapper

@app.callback(
    # KPIs
    Output("kpi-siniestros", "children"),
    Output("kpi-siniestros-sub", "children"),
    Output("kpi-fallecidos", "children"),
    Output("kpi-fallecidos-sub", "children"),
    Output("kpi-lesionados", "children"),
    Output("kpi-lesionados-sub", "children"),
    Output("kpi-letalidad", "children"),
    Output("kpi-letalidad-sub", "children"),
    Output("kpi-carreteras", "children"),
    Output("kpi-carreteras-sub", "children"),
    # Lista de Regiones Críticas (Supplier Cards style)
    Output("top-regions-list", "children"),
    # Mapa
    Output("geo-map", "figure"),
    # Gráficos Inferiores
    Output("time-trend-chart", "figure"),
    Output("infrastructure-chart", "figure"),
    # Columna Derecha
    Output("alerts-count-badge", "children"),
    Output("alerts-list-container", "children"),
    Output("heatmap-chart", "figure"),
    # Filtros
    Input("filter-depts", "value"),
    Input("filter-years", "value"),
    Input("filter-vias", "value"),
    Input("filter-clases", "value"),
)
def update_dashboard(selected_depts, selected_years, selected_vias, selected_clases):
    try:
        return run_dashboard_logic(selected_depts, selected_years, selected_vias, selected_clases)
    except Exception as e:
        import traceback
        log_path = r"C:\Users\Alessandro\.gemini\antigravity\brain\398c6553-a285-4768-bb08-b9fb63b1a256\error_log.txt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n--- EXCEPCION EN CALLBACK UPDATE_DASHBOARD ---\n")
            traceback.print_exc(file=f)
        raise e

def run_dashboard_logic(selected_depts, selected_years, selected_vias, selected_clases):
    # Normalizar a lista (None → [])
    selected_depts  = selected_depts  or []
    selected_years  = selected_years  or []
    selected_vias   = selected_vias   or []
    selected_clases = selected_clases or []

    dff = filter_data(selected_depts, selected_years, selected_vias, selected_clases)
    
    # ── 1. CÁLCULO DE KPIs ────────────────────────────────────────────────────
    total_siniestros = len(dff)
    total_fallecidos = dff['fallecidos'].sum()
    total_lesionados = dff['lesionados'].sum()
    
    avg_letalidad = total_fallecidos / total_siniestros if total_siniestros > 0 else 0
    
    crashes_on_carretera = len(dff[dff['tipo_via'] == 'CARRETERA'])
    pct_carreteras = (crashes_on_carretera / total_siniestros * 100) if total_siniestros > 0 else 0

    # Sub-indicadores de tendencias
    if len(selected_years) == 0:
        sub_siniestros = "Todos los años"
    elif len(selected_years) > 1:
        sub_siniestros = f"{min(selected_years)} - {max(selected_years)}"
    else:
        sub_siniestros = f"Año {selected_years[0]}"
    max_deadly_accident = dff['fallecidos'].max() if len(dff) > 0 else 0
    sub_fallecidos = f"Máx: {max_deadly_accident} en 1 accidente"
    sub_lesionados = f"Promedio: {(total_lesionados/total_siniestros):.1f} lesionados/ac." if total_siniestros > 0 else "0.0/ac."
    sub_letalidad = "Riesgo Muy Alto " if avg_letalidad > 1.2 else "Riesgo Moderado "
    sub_carreteras = f"{crashes_on_carretera:,} siniestros fatales"

    # Formatear strings
    kpi_sin_str = f"{total_siniestros:,}"
    kpi_fall_str = f"{total_fallecidos:,}"
    kpi_les_str = f"{total_lesionados:,}"
    kpi_let_str = f"{avg_letalidad:.2f}"
    kpi_carr_str = f"{pct_carreteras:.1f}%"

    # ── 2. LISTA DE REGIONES CRÍTICAS (SUPPLIER CARDS STYLE) ──────────────────
    top_depts_dff = dff.groupby('departamento').agg(
        siniestros=('codigo', 'count'),
        fallecidos=('fallecidos', 'sum')
    ).reset_index().sort_values(by='siniestros', ascending=False).head(5)
    
    top_regions_cards = []
    
    max_sin_top = top_depts_dff['siniestros'].max() if len(top_depts_dff) > 0 else 1
    
    for _, row in top_depts_dff.iterrows():
        dept_name = row['departamento']
        dept_sin = row['siniestros']
        dept_fall = row['fallecidos']
        
        # Calcular porcentaje para la barra de progreso
        progress_pct = (dept_sin / max_sin_top) * 100
        
        # Determinar nivel de riesgo
        if dept_fall > 400:
            badge_text = "Riesgo Crítico "
            badge_color = CORAL_ACCENT
        elif dept_fall > 150:
            badge_text = "Riesgo Alto "
            badge_color = AMBER_ACCENT
        else:
            badge_text = "Riesgo Moderado "
            badge_color = CYAN_ACCENT

        card_element = html.Div([
            html.Div([
                html.Div([
                    html.Div(dept_name, style={"color": TEXT_COLOR, "fontWeight": "800", "fontSize": "13px"}),
                    html.Div(f"{dept_sin:,} siniestros · {dept_fall:,} fallecidos", style={"color": LABEL_COLOR, "fontSize": "11px", "marginTop": "2px"})
                ]),
                html.Div(badge_text, style={
                    "color": badge_color, "fontSize": "9px", "fontWeight": "800",
                    "background": f"{badge_color}15", "border": f"1px solid {badge_color}35",
                    "padding": "3px 8px", "borderRadius": "20px", "letterSpacing": "0.5px"
                })
            ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "6px"}),
            # Barra de Progreso Neón
            html.Div([
                html.Div(style={
                    "width": f"{progress_pct}%", "height": "4px", 
                    "background": f"linear-gradient(90deg, {CYAN_ACCENT} 0%, {badge_color} 100%)",
                    "borderRadius": "2px", "boxShadow": f"0 0 8px {badge_color}50"
                })
            ], style={"width": "100%", "height": "4px", "background": "#1e293b", "borderRadius": "2px"})
        ], style={
            "background": "#161d30", "padding": "12px 14px", "borderRadius": "10px", 
            "border": "1px solid rgba(255, 255, 255, 0.03)", "display": "flex", 
            "flexDirection": "column", "justifyContent": "center"
        })
        top_regions_cards.append(card_element)

    if not top_regions_cards:
        top_regions_cards = html.Div("No hay datos disponibles", style={"color": LABEL_COLOR, "textAlign": "center", "marginTop": "20px"})

    # ── 3. MAPA GEOESPACIAL INTERACTIVO ───────────────────────────────────────
    # Submuestreo inteligente para evitar lag en renderizado del mapa si son demasiados puntos
    map_dff = dff.copy()
    
    # Mapear colores de clase
    map_dff['marker_color'] = map_dff['clase'].map(CLASE_COLORS).fillna("#cccccc")
    
    # Crear hover template personalizado
    hover_tmpl = (
        "<b> Región: %{customdata[0]}</b><br>" +
        " Vía: %{customdata[1]} (%{customdata[2]})<br>" +
        " Clase: %{customdata[3]}<br>" +
        " Fecha/Hora: %{customdata[4]} a las %{customdata[5]}:00 h<br>" +
        " Fallecidos: <b>%{customdata[6]}</b>  |   Lesionados: %{customdata[7]}<br>" +
        " Causa: <i>%{customdata[8]}</i>" +
        "<extra></extra>"
    )
    
    if map_dff.empty:
        # Si está vacío, creamos un Scattermapbox vacío con coordenadas vacías pero configuramos el mapa Mapbox
        # para evitar que se ponga de color blanco (comportamiento cartesiano por defecto de Plotly sin datos).
        fig_map = go.Figure(go.Scattermapbox(lat=[], lon=[]))
        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                zoom=5.3,
                center={"lat": -9.8, "lon": -74.9}
            )
        )
    else:
        fig_map = px.scatter_mapbox(
            map_dff,
            lat="lat",
            lon="lon",
            color="clase",
            color_discrete_map=CLASE_COLORS,
            size="fallecidos",
            size_max=32,
            custom_data=["departamento", "tipo_via", "cod_carretera", "clase", "fecha", "hour", "fallecidos", "lesionados", "causa_principal"],
            zoom=5.3,
            center={"lat": -9.8, "lon": -74.9}  # Centro de Perú
        )
        fig_map.update_traces(
            hovertemplate=hover_tmpl,
            marker=dict(opacity=0.75)
        )

        # ── DIBUJAR CARRETERAS ENCIMA DEL MAPA (DYNAMIC HIGHWAYS TRACING) ──
        # Filtrar registros que tengan código de carretera válido
        highway_dff = map_dff[
            (map_dff['cod_carretera'].notnull()) & 
            (map_dff['cod_carretera'] != "") & 
            (~map_dff['cod_carretera'].isin(["NO CORRESPONDE", "SIN CLASIFICAR"]))
        ]
        
        line_traces = []
        if not highway_dff.empty:
            # Agrupar por carretera para dibujar sus líneas
            for h in highway_dff['cod_carretera'].unique():
                df_h = highway_dff[highway_dff['cod_carretera'] == h]
                # Necesitamos al menos 2 puntos para dibujar una línea
                if len(df_h) < 2:
                    continue
                
                # Heurística de ordenamiento: si la carretera es más "horizontal" o "vertical"
                lat_range = df_h['lat'].max() - df_h['lat'].min()
                lon_range = df_h['lon'].max() - df_h['lon'].min()
                if lon_range > lat_range:
                    df_h = df_h.sort_values(by='lon')
                else:
                    df_h = df_h.sort_values(by='lat')
                
                # Calcular total de siniestros en esta carretera bajo el filtro actual
                total_h_siniestros = len(df_h)
                total_h_fallecidos = df_h['fallecidos'].sum()
                
                # Determinar grosor y color según peligrosidad (siniestros)
                if total_h_siniestros >= 50:
                    line_color = "#ef4444"  # Rojo brillante neón
                    line_width = 4.5
                elif total_h_siniestros >= 15:
                    line_color = "#f97316"  # Naranja
                    line_width = 3.0
                else:
                    line_color = "#eab308"  # Amarillo
                    line_width = 1.5
                
                # Crear la traza de la línea
                line_trace = go.Scattermapbox(
                    lat=df_h['lat'],
                    lon=df_h['lon'],
                    mode='lines',
                    line=dict(width=line_width, color=line_color),
                    name=f"Carretera {h}",
                    hoverinfo='text',
                    hovertext=f"<b>Carretera: {h}</b><br>Siniestros en tramo: {total_h_siniestros}<br>Fallecidos: {total_h_fallecidos}",
                    showlegend=False
                )
                line_traces.append(line_trace)
            
            # Insertar las líneas al principio para que se rendericen DEBAJO de los puntos (scatter)
            if line_traces:
                fig_map.data = tuple(line_traces) + fig_map.data
    
    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        hoverlabel=dict(
            bgcolor="#0d1117",
            font=dict(color=TEXT_COLOR, size=12, family="Segoe UI, system-ui, sans-serif"),
            namelength=-1,
        ),
        legend=dict(
            title=dict(
                text="<b>Clase Siniestro</b>",
                font=dict(color=TEXT_COLOR, size=12)
            ),
            bgcolor="rgba(10, 14, 23, 0.92)",
            borderwidth=1,
            font=dict(size=12, color=TEXT_COLOR),
            orientation="v",
            yanchor="top", y=0.98,
            xanchor="left", x=0.02,
            itemsizing="constant",
            itemwidth=30,
        ),
        coloraxis_showscale=False
    )

    # ── 4. GRÁFICO DE TENDENCIA MENSUAL (LÍNEA TIPO LEAD TIME) ─────────────────
    trend_dff = dff.groupby(['year', 'month', 'month_name']).agg(
        siniestros=('codigo', 'count'),
        fallecidos=('fallecidos', 'sum')
    ).reset_index().sort_values(by=['year', 'month'])
    
    trend_dff['periodo'] = trend_dff['month_name'].astype(str) + " " + trend_dff['year'].astype(str)
    
    fig_trend = go.Figure()
    
    # Línea de Siniestros
    fig_trend.add_trace(go.Scatter(
        x=trend_dff['periodo'], y=trend_dff['siniestros'],
        name="Siniestros Fatales",
        mode="lines+markers",
        line=dict(color=CYAN_ACCENT, width=3, shape="spline"),
        marker=dict(size=6, color=CYAN_ACCENT, symbol="circle-open-dot"),
        hovertemplate="Período: %{x}<br>Siniestros: %{y}<extra></extra>"
    ))
    
    # Línea de Fallecidos
    fig_trend.add_trace(go.Scatter(
        x=trend_dff['periodo'], y=trend_dff['fallecidos'],
        name="Víctimas Mortales",
        mode="lines+markers",
        line=dict(color=CORAL_ACCENT, width=2, dash="dash", shape="spline"),
        marker=dict(size=5, color=CORAL_ACCENT),
        hovertemplate="Período: %{x}<br>Fallecidos: %{y}<extra></extra>"
    ))
    
    layout_trend = dict(**PLOTLY_THEME_LAYOUT)
    layout_trend["margin"] = dict(l=30, r=10, t=10, b=30)
    layout_trend["hovermode"] = "x unified"
    layout_trend["hoverlabel"] = dict(
        bgcolor="#0d1117",
        font=dict(color=TEXT_COLOR, size=12, family="Segoe UI, system-ui, sans-serif"),
        namelength=-1,
    )
    layout_trend["xaxis"] = dict(
        gridcolor="#1e293b",
        linecolor="#1e293b",
        tickfont=dict(color=LABEL_COLOR, size=8),
        nticks=12
    )
    fig_trend.update_layout(**layout_trend)

    # ── 5. LETALIDAD POR INFRAESTRUCTURA (BARRAS DOBLES TIPO COST COMPARISON) ──
    infra_dff = dff.groupby('tipo_via').agg(
        siniestros=('codigo', 'count'),
        avg_letalidad=('fallecidos', 'mean')
    ).reset_index().sort_values(by='siniestros', ascending=False).head(5)
    
    fig_infra = go.Figure()
    
    # Barras de Siniestros
    fig_infra.add_trace(go.Bar(
        x=infra_dff['tipo_via'], y=infra_dff['siniestros'],
        name="Total Siniestros",
        marker_color=CYAN_ACCENT,
        marker_opacity=0.8,
        yaxis="y1",
        hovertemplate="Vía: %{x}<br>Siniestros: %{y}<extra></extra>"
    ))
    
    # Línea de Letalidad Promedio (eje secundario)
    fig_infra.add_trace(go.Scatter(
        x=infra_dff['tipo_via'], y=infra_dff['avg_letalidad'],
        name="Letalidad Promedio",
        mode="lines+markers",
        line=dict(color=AMBER_ACCENT, width=3),
        marker=dict(size=8, color=AMBER_ACCENT),
        yaxis="y2",
        hovertemplate="Vía: %{x}<br>Letalidad: %{y:.2f} muertes/ac.<extra></extra>"
    ))
    
    layout_infra = dict(**PLOTLY_THEME_LAYOUT)
    layout_infra["margin"] = dict(l=40, r=40, t=10, b=30)
    layout_infra["xaxis"] = dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=LABEL_COLOR, size=9))
    layout_infra["yaxis"] = dict(
        title=dict(text="Total Siniestros", font=dict(color=CYAN_ACCENT, size=10)),
        gridcolor="#1e293b"
    )
    layout_infra["yaxis2"] = dict(
        title=dict(text="Letalidad (Muertes/Accidente)", font=dict(color=AMBER_ACCENT, size=10)),
        overlaying="y",
        side="right",
        gridcolor="rgba(0,0,0,0)"
    )
    layout_infra["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    layout_infra["hoverlabel"] = dict(
        bgcolor="#0d1117",
        font=dict(color=TEXT_COLOR, size=12, family="Segoe UI, system-ui, sans-serif"),
        namelength=-1,
    )
    fig_infra.update_layout(**layout_infra)

    # ── 6. ALERTAS DE ACCIDENTES CRÍTICOS (COLUMNA DERECHA) ───────────────────
    critical_crashes = dff[dff['fallecidos'] >= 4].sort_values(by='fallecidos', ascending=False).head(15)
    
    alerts_count_badge_text = f"{len(critical_crashes):,} ALERTAS"
    
    alerts_list = []
    
    for _, row in critical_crashes.iterrows():
        dept = row['departamento']
        fallecidos = row['fallecidos']
        lesionados = row['lesionados']
        clase = row['clase']
        via = row['tipo_via']
        fecha = row['fecha']
        cod_carretera = row['cod_carretera']
        causa = row['causa_principal']
        
        via_label = f"{via} ({cod_carretera})" if pd.notnull(cod_carretera) and str(cod_carretera).strip() != "" else via
        
        # Color del badge según letalidad extrema
        if fallecidos >= 10:
            glow_col = CORAL_ACCENT
            alert_badge = "CRÍTICO "
        else:
            glow_col = AMBER_ACCENT
            alert_badge = "EXTREMO "

        alert_item = html.Div([
            html.Div([
                html.Div([
                    html.Span(" ", style={"fontSize": "14px"}),
                    html.Strong(f"{dept} · {fecha}", style={"color": TEXT_COLOR, "fontSize": "11px"})
                ]),
                html.Div(alert_badge, style={
                    "color": glow_col, "fontSize": "8px", "fontWeight": "900",
                    "background": f"{glow_col}15", "border": f"1px solid {glow_col}40",
                    "padding": "2px 6px", "borderRadius": "12px", "letterSpacing": "0.5px"
                })
            ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "6px"}),
            html.Div(f"{clase} en {via_label}", style={"color": LABEL_COLOR, "fontSize": "11px", "fontWeight": "600"}),
            html.Div([
                html.Div([
                    html.Span(" ", style={"color": CORAL_ACCENT}),
                    html.Span(f"{fallecidos} Fallecidos", style={"color": TEXT_COLOR, "fontWeight": "700", "fontSize": "11px"}),
                    html.Span("  |   ", style={"color": EMERALD_ACCENT}),
                    html.Span(f"{lesionados} Lesionados", style={"color": LABEL_COLOR, "fontSize": "11px"})
                ]),
                html.Div(causa.replace("NO IDENTIFICA LA CAUSA", "CAUSA EN INVESTIGACIÓN").title(), 
                         style={"color": LABEL_COLOR, "fontSize": "9px", "fontStyle": "italic", "marginTop": "2px", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"})
            ])
        ], style={
            "background": "#161d30", 
            "padding": "10px 12px", 
            "borderRadius": "8px", 
            "border": f"1px solid {glow_col}25",
            "boxShadow": f"0 2px 10px {glow_col}05"
        })
        alerts_list.append(alert_item)
        
    if not alerts_list:
        alerts_list = html.Div("No hay accidentes de extrema gravedad registrados con los filtros actuales.", 
                               style={"color": LABEL_COLOR, "textAlign": "center", "fontSize": "12px", "padding": "20px"})

    # ── 7. MATRIZ DE RIESGO HORARIO Y SEMANAL (HEATMAP) ───────────────────────
    # Agrupar por día de la semana y por hora
    heatmap_data = dff.groupby(['day_of_week', 'day_es', 'hour']).size().reset_index(name='siniestros')
    
    # Crear pivote para el mapa de calor
    pivot_df = pd.DataFrame(0, index=range(24), columns=DAYS_ES)
    for _, row in heatmap_data.iterrows():
        pivot_df.at[int(row['hour']), row['day_es']] = int(row['siniestros'])
        
    # Reordenar columnas para que empiece en lunes
    pivot_df = pivot_df[DAYS_ES]
    
    fig_heat = go.Figure(go.Heatmap(
        z=pivot_df.values.tolist(),
        x=DAYS_ES,
        y=[f"{h:02d}:00" for h in range(24)],
        colorscale=[
            [0.0, "rgba(56, 189, 248, 0.0)"],    # Cyan invisible en mínimo
            [0.2, "rgba(56, 189, 248, 0.3)"],    # Cyan suave
            [0.5, "rgba(217, 119, 6, 0.6)"],     # Dorado medio
            [0.8, "rgba(255, 122, 69, 0.85)"],   # Coral fuerte
            [1.0, "rgba(255, 122, 69, 1.0)"]      # Coral neón intenso
        ],
        text=pivot_df.values.tolist(),
        texttemplate="%{text}",
        textfont={"size": 8, "color": TEXT_COLOR, "family": "Segoe UI"},
        hovertemplate="Día: %{x}<br>Hora: %{y}<br>Siniestros: <b>%{z}</b><extra></extra>",
        colorbar=dict(
            tickfont=dict(color=LABEL_COLOR, size=8),
            title=dict(text="Accidentes", font=dict(color=TEXT_COLOR, size=9))
        )
    ))
    
    layout_heat = dict(**PLOTLY_THEME_LAYOUT)
    layout_heat["margin"] = dict(l=45, r=10, t=10, b=30)
    layout_heat["yaxis"] = dict(
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(color=LABEL_COLOR, size=8),
        dtick=3,  # Mostrar cada 3 horas
        autorange="reversed" # Poner el inicio (00:00) arriba
    )
    layout_heat["xaxis"] = dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=LABEL_COLOR, size=9))
    layout_heat["hoverlabel"] = dict(
        bgcolor="#0d1117",
        bordercolor=PURPLE_ACCENT,
        font=dict(color=TEXT_COLOR, size=12, family="Segoe UI, system-ui, sans-serif"),
        namelength=-1,
    )
    fig_heat.update_layout(**layout_heat)

    return (
        kpi_sin_str, sub_siniestros,
        kpi_fall_str, sub_fallecidos,
        kpi_les_str, sub_lesionados,
        kpi_let_str, sub_letalidad,
        kpi_carr_str, sub_carreteras,
        top_regions_cards,
        fig_map,
        fig_trend,
        fig_infra,
        alerts_count_badge_text,
        alerts_list,
        fig_heat
    )
# ── 6. CSS PERSONALIZADO E INTERFAZ PREMIUM (EXTRACTED TO ASSETS) ──────────────
# Note: CSS and JavaScript are now loaded automatically from the assets/ folder
# (assets/styles.css and assets/pill_filters.js) to keep Python file clean and fix linter issues.




# ── 7. INICIO DEL SERVIDOR ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Usar puerto 8055 para evitar conflictos con otros servidores abiertos
    port = 8055
    print("=====================================================================")
    print("INICIANDO PORTAL DE SEGURIDAD VIAL ONSV EN MODO DE ALTA FIDELIDAD")
    print(f"Acceda de inmediato en su navegador: http://127.0.0.1:{port}")
    print("=====================================================================")
    app.run(debug=False, host="127.0.0.1", port=port)
