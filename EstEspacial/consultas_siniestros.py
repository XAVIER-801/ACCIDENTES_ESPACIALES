# -*- coding: utf-8 -*-
# %% [markdown]
# # Observatorio de Seguridad Vial (ONSV 2021-2023)
# ## Notebook Interactivo de Consultas de Base de Datos con Pandas
# 
# Este script está estructurado utilizando celdas de código de VS Code (`# %%`).
# Cada sección tiene una explicación en Markdown (`# %% [markdown]`) y una celda de código ejecutable.
# Puedes ejecutar cada sección individualmente haciendo clic en **"Run Cell"** (Ejecutar Celda) en tu IDE.

# %%
import os
import pandas as pd
import numpy as np

# %% [markdown]
# ### ── 1. Carga y Normalización Robusta de Datos ──
# En esta celda cargamos la base de datos de siniestros desde el archivo Excel.
# Para evitar errores por tildes o caracteres especiales en las columnas (como `VÍA` o `COD CARRETERA`),
# utilizamos una búsqueda parcial de nombres de columnas (insensible a mayúsculas y minúsculas).

# %%
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "."
file_path = os.path.join(script_dir, "BBDD ONSV - SINIESTROS 2021-2023.xlsx")

print("Cargando base de datos...")
df = pd.read_excel(file_path, sheet_name="SINIESTROS")

# Normalizar y limpiar nombres de columnas de forma robusta
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
    elif "CAUSA FACTOR" in col_upper or "CAUSA_FACTOR" in col_upper:
        rename_map[col] = "causa_principal"

df = df.rename(columns=rename_map)

# Preprocesamiento de variables temporales
df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
df['year'] = df['fecha_parsed'].dt.year.fillna(2022).astype(int)
df['month'] = df['fecha_parsed'].dt.month.fillna(1).astype(int)

df['departamento'] = df['departamento'].str.upper().str.strip().fillna("DESCONOCIDO")
df['tipo_via'] = df['tipo_via'].str.upper().str.strip().fillna("OTRO")
df['clase'] = df['clase'].str.upper().str.strip().fillna("OTRO")

print(f"Base de datos cargada y normalizada con éxito. Total registros: {len(df)}")


# %% [markdown]
# ### ── 2. Consulta y Estadísticas de una Región específica ──
# Modifica la variable `mi_region` para filtrar por cualquier departamento del Perú.
# Por defecto se establece en **PUNO**.

# %%
mi_region = "PUNO"  # <--- CAMBIA AQUÍ EL DEPARTAMENTO

# Filtrar datos de la región elegida
df_region = df[df['departamento'] == mi_region.upper()]

print(f"=== REPORTE PARA LA REGIÓN: {mi_region} ===")
print(f"Total de Siniestros Fatales: {len(df_region)}")
print(f"Total de Víctimas Mortales: {df_region['fallecidos'].sum()}")
print(f"Total de Lesionados: {df_region['lesionados'].sum()}")
print(f"Tasa de Letalidad Promedio: {df_region['fallecidos'].mean():.2f} muertes/accidente\n")

print("Top 5 Clases de Siniestro en esta región:")
print(df_region['clase'].value_counts().head(5))


# %% [markdown]
# ### ── 3. Consulta de Siniestros por Tipo de Vía ──
# Filtra y analiza la peligrosidad según el tipo de infraestructura vial.
# Modifica la variable `mi_via` (por ejemplo: 'CARRETERA', 'AVENIDA', 'CALLE').

# %%
mi_via = "CARRETERA"  # <--- CAMBIA AQUÍ EL TIPO DE VÍA

# Filtrar datos de la vía elegida
df_via = df[df['tipo_via'] == mi_via.upper()]

print(f"=== REPORTE PARA TIPO DE VÍA: {mi_via} ===")
print(f"Total de Accidentes: {len(df_via)}")
print(f"Total de Fallecidos: {df_via['fallecidos'].sum()}")
print(f"Tasa de Letalidad Promedio: {df_via['fallecidos'].mean():.2f} muertes/accidente\n")

print("Top 5 Provincias con más siniestros en este tipo de vía:")
print(df_via.groupby(['departamento', 'provincia']).size().reset_index(name='siniestros').sort_values(by='siniestros', ascending=False).head(5))


# %% [markdown]
# ### ── 4. Consulta por Clase de Accidente ──
# Analiza cuáles son los motivos que causan cada clase de accidente.
# Modifica `mi_clase` (por ejemplo: 'CHOQUE', 'DESPISTE', 'ATROPELLO').

# %%
mi_clase = "DESPISTE"  # <--- CAMBIA AQUÍ LA CLASE DE SINIESTRO

df_clase = df[df['clase'] == mi_clase.upper()]

print(f"=== REPORTE PARA CLASE: {mi_clase} ===")
print(f"Total de Accidentes: {len(df_clase)}")
print(f"Total de Fallecidos: {df_clase['fallecidos'].sum()}")
print(f"Total de Lesionados: {df_clase['lesionados'].sum()}\n")

print("Principales causas de esta clase de siniestro:")
print(df_clase['causa_principal'].value_counts().head(5))


# %% [markdown]
# ### ── 5. Consulta Avanzada Combinada (Multicriterio) ──
# Esta celda te permite cruzar múltiples filtros de manera simultánea. 
# Puedes configurar cada variable a tu gusto. Si pones `None`, ese filtro no se aplicará.

# %%
# Configura tus criterios de búsqueda
FILTRO_DEPARTAMENTO = "PUNO"       # Ej: "PUNO", "LIMA", "AREQUIPA" o None
FILTRO_VIA          = "CARRETERA"   # Ej: "CARRETERA", "AVENIDA", "CALLE" o None
FILTRO_CLASE        = "DESPISTE"    # Ej: "DESPISTE", "CHOQUE", "ATROPELLO" o None
FILTRO_ANOS         = [2022, 2023]  # Años seleccionados (ej: [2021, 2022, 2023])

# Aplicar filtros dinámicos secuenciales
dff_query = df.copy()

if FILTRO_DEPARTAMENTO:
    dff_query = dff_query[dff_query['departamento'] == FILTRO_DEPARTAMENTO.upper()]
if FILTRO_VIA:
    dff_query = dff_query[dff_query['tipo_via'] == FILTRO_VIA.upper()]
if FILTRO_CLASE:
    dff_query = dff_query[dff_query['clase'] == FILTRO_CLASE.upper()]
if FILTRO_ANOS:
    dff_query = dff_query[dff_query['year'].isin(FILTRO_ANOS)]

# Mostrar Resultados de la Búsqueda Avanzada
print("=== RESULTADOS DE LA CONSULTA COMBINADA ===")
print(f"Criterios activos: Dept={FILTRO_DEPARTAMENTO} | Vía={FILTRO_VIA} | Clase={FILTRO_CLASE} | Años={FILTRO_ANOS}")
print(f"Registros coincidentes: {len(dff_query)}")
print(f"Total de Fallecidos: {dff_query['fallecidos'].sum()}")
print(f"Total de Lesionados: {dff_query['lesionados'].sum()}\n")

if len(dff_query) > 0:
    print("Detalle de los primeros 10 accidentes coincidentes:")
    print(dff_query[['fecha', 'provincia', 'distrito', 'fallecidos', 'causa_principal']].head(10))
else:
    print("No se encontraron registros para la combinación de filtros seleccionada.")
