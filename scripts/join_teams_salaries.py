import pandas as pd
from pathlib import Path
from unidecode import unidecode

# Leer datos | Lire les données | Read data
df_salaries = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/teams_salaries.csv'
)
df_all_teams_stats = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/grouped_stats.csv'
)

# Columnas de interés | Colonnes d'intérêt | Columns of interest
weekly_col = 'Weekly Wages' if 'Weekly Wages' in df_salaries.columns else 'Weekly Wages'
annual_col = 'Annual Wages' if 'Annual Wages' in df_salaries.columns else 'Annual Wages'
estimated_col = '% Estimated' if '% Estimated' in df_salaries.columns else '% Estimated'

# Función para normalizar nombres (quitar acentos, espacios y pasar a minúsculas)
# Fonction pour normaliser les noms (supprimer accents, espaces, minuscules)
# Function to normalize names (remove accents, strip spaces, lowercase)
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

# Crear columnas normalizadas con nombres distintos
# Créer des colonnes normalisées avec des noms différents
# Create normalized columns with different names
df_all_teams_stats["Squad_norm_left"] = df_all_teams_stats["Squad"].apply(normalize_name)
df_salaries["Squad_norm_right"] = df_salaries["Squad"].apply(normalize_name)

# Seleccionar columnas a mantener de salarios
# Sélectionner les colonnes à conserver depuis salaires
# Select columns to keep from salaries
cols_keep = ["Squad_norm_right", weekly_col, annual_col, estimated_col]

# Merge LEFT: mantener todo de stats y añadir salarios
# Jointure LEFT : garder tout de stats et ajouter salaires
# LEFT merge: keep all from stats and add salaries
df_all_teams_stats = df_all_teams_stats.merge(
    df_salaries[cols_keep],
    left_on="Squad_norm_left",
    right_on="Squad_norm_right",
    how="left",
    suffixes=("", "_sal")
)

# Eliminar columnas auxiliares de normalización
# Supprimer les colonnes auxiliaires de normalisation
# Drop helper normalization columns
df_all_teams_stats = df_all_teams_stats.drop(columns=["Squad_norm_left", "Squad_norm_right"])

# Guardar CSV de salida
# Enregistrer le CSV de sortie
# Save output CSV
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
out_path = data_dir / "join_teams_salaries.csv"
df_all_teams_stats.to_csv(out_path, index=False, encoding="utf-8")
