# -*- coding: utf-8 -*-
# %% [markdown]
# # Observatorio de Seguridad Vial (ONSV 2021-2023)
# ## Notebook Interactivo de Consultas de Base de Datos con Pandas
# 
# Este script está estructurado utilizando celdas de código de VS Code (`# %%`). 
# Puedes ejecutar cada sección de forma independiente haciendo clic en **"Run Cell"** 
# encima de cada bloque si tienes instalada la extensión de Jupyter en tu IDE.

# %%
import os
import pandas as pd
import numpy as np

# ── 1. CARGA Y PREPARACIÓN DE DATOS ──────────────────────────────────────────
# Definir la ruta relativa al archivo Excel
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "."
file_path = os.path.join(script_dir, "BBDD ONSV - SINIESTROS 2021-2023.xlsx")

print("Cargando base de datos...")
df = pd.read_excel(file_path, sheet_name="SINIESTROS")

# Normalizar nombres de columnas para que coincidan con el dashboard
rename_map = {
    'CANTIDAD DE FALLECIDOS': 'fallecidos',
    'CANTIDAD DE LESIONADOS': 'lesionados',
    'CANTIDAD DE VEHICULOS DAADOS': 'vehiculos_danados',
    'DEPARTAMENTO': 'departamento',
    'PROVINCIA': 'provincia',
    'DISTRITO': 'distrito',
    'TIPO DE VA': 'tipo_via',
    'COD CARRETERA': 'cod_carretera',
    'FECHA SINIESTRO': 'fecha',
    'HORA SINIESTRO': 'hora',
    'CLASE SINIESTRO': 'clase',
    'CONDICIN CLIMTICA': 'clima',
    'COORDENADAS LATITUD': 'lat',
    'COORDENADAS  LONGITUD': 'lon',
    'CAUSA FACTOR PRINCIPAL': 'causa_principal'
}
df = df.rename(columns=rename_map)

# Preprocesamiento básico de fechas y normalización de textos
df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
df['year'] = df['fecha_parsed'].dt.year.fillna(2022).astype(int)
df['month'] = df['fecha_parsed'].dt.month.fillna(1).astype(int)

df['departamento'] = df['departamento'].str.upper().str.strip().fillna("DESCONOCIDO")
df['tipo_via'] = df['tipo_via'].str.upper().str.strip().fillna("OTRO")
df['clase'] = df['clase'].str.upper().str.strip().fillna("OTRO")

print(f"Base de datos cargada con éxito. Total registros: {len(df)}")


# %% [markdown]
# ## ── 2. CONSULTAS POR DEPARTAMENTO / REGION ────────────────────────────────
# Modifica la variable `mi_region` para consultar cualquier departamento (ejemplo: 'PUNO', 'AREQUIPA', 'LIMA').

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
# ## ── 3. CONSULTAS POR TIPO DE VÍA ──────────────────────────────────────────
# Modifica la variable `mi_via` para consultar clases de vía (ejemplo: 'CARRETERA', 'AVENIDA', 'CALLE', 'JARDIN').

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
# ## ── 4. CONSULTAS POR CLASE DE ACCIDENTE ────────────────────────────────────
# Modifica `mi_clase` para consultar tipos específicos de accidente (ejemplo: 'CHOQUE', 'DESPISTE', 'ATROPELLO').

# %%
mi_clase = "DESPISTE"  # <--- CAMBIA AQUÍ LA CLASE DE SINIESTRO

df_clase = df[df['clase'] == mi_clase.upper()]

print(f"=== REPORTE PARA CLASE DE SINIESTRO: {mi_clase} ===")
print(f"Total de Accidentes: {len(df_clase)}")
print(f"Total de Fallecidos: {df_clase['fallecidos'].sum()}")
print(f"Total de Lesionados: {df_clase['lesionados'].sum()}\n")

print("Principales causas de esta clase de siniestro:")
print(df_clase['causa_principal'].value_counts().head(5))


# %% [markdown]
# ## ── 5. CONSULTAS POR AÑO / PERIODO ────────────────────────────────────────
# Filtra y compara las estadísticas interanuales.

# %%
mi_ano = 2023  # <--- CAMBIA AQUÍ EL AÑO (2021, 2022, 2023)

df_ano = df[df['year'] == mi_ano]

print(f"=== REPORTE DE ACCIDENTABILIDAD - AÑO {mi_ano} ===")
print(f"Total Siniestros: {len(df_ano)}")
print(f"Total Fallecidos: {df_ano['fallecidos'].sum()}")
print(f"Tasa de Letalidad Nacional del año: {df_ano['fallecidos'].mean():.2f}\n")

# Agrupar mensualmente para ver evolución
print("Distribución mensual de siniestros fatales:")
print(df_ano.groupby('month').size().reset_index(name='siniestros'))


# %% [markdown]
# ## ── 6. CONSULTA MULTICRITERIO PERSONALIZADA ──────────────────────────────
# Combina múltiples filtros simultáneos para obtener consultas muy específicas al antojo.

# %%
# Define tus criterios de búsqueda aquí:
FILTRO_DEPARTAMENTO = "PUNO"       # Pon None para desactivar filtro
FILTRO_VIA          = "CARRETERA"   # Pon None para desactivar filtro
FILTRO_CLASE        = "CHOQUE"      # Pon None para desactivar filtro
FILTRO_ANOS         = [2022, 2023]  # Lista de años a analizar

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

# Mostrar Resultados
print("=== RESULTADOS DE CONSULTA COMBINADA A TU ANTOJO ===")
print(f"Criterios: Dept={FILTRO_DEPARTAMENTO} | Vía={FILTRO_VIA} | Clase={FILTRO_CLASE} | Años={FILTRO_ANOS}")
print(f"Registros encontrados: {len(dff_query)}")
print(f"Total Fallecidos: {dff_query['fallecidos'].sum()}")
print(f"Total Lesionados: {dff_query['lesionados'].sum()}\n")

if len(dff_query) > 0:
    print("Detalle de los primeros 5 accidentes encontrados:")
    print(dff_query[['fecha', 'provincia', 'distrito', 'fallecidos', 'causa_principal']].head(5))
else:
    print("No se encontraron registros para esta combinación de filtros.")
