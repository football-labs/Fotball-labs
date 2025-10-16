import pandas as pd
from pathlib import Path
from unidecode import unidecode


# Load input data | Charger les données d'entrée | Cargar los datos de entrada
df_salaries = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/teams_salaries.csv'
)
df_all_teams_stats = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/grouped_stats.csv'
)

# Define columns of interest | Colonnes d'intérêt | Columnas de interés
weekly_col = 'Weekly Wages'
annual_col = 'Annual Wages'
estimated_col = '% Estimated'

# Normalize team names (remove accents, lowercase) | Normaliser les noms d'équipes (supprimer accents, minuscules) | Normalizar los nombres de los equipos (eliminar acentos, minúsculas)
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

df_all_teams_stats["Squad_norm_left"] = df_all_teams_stats["Squad"].apply(normalize_name)
df_salaries["Squad_norm_right"] = df_salaries["Squad"].apply(normalize_name)

# Select columns to keep from salary data | Sélectionner les colonnes à conserver depuis salaires | Seleccionar las columnas que se desean conservar de los salarios
cols_keep = ["Squad_norm_right", weekly_col, annual_col, estimated_col]

# Merge salary data into stats | Fusionner les salaires avec les statistiques | Fusionar los salarios con las estadísticas
df_all_teams_stats = df_all_teams_stats.merge(
    df_salaries[cols_keep],
    left_on="Squad_norm_left",
    right_on="Squad_norm_right",
    how="left",
    suffixes=("", "_sal")
)

# Drop helper normalization columns | Supprimer les colonnes auxiliaires de normalisation | Eliminar las columnas auxiliares de normalización
df_all_teams_stats = df_all_teams_stats.drop(columns=["Squad_norm_left", "Squad_norm_right"])

# Save output CSV | Enregistrer le CSV de sortie | Guardar el CSV de salida
script_dir  = Path(__file__).resolve().parents[2]
data_dir  = script_dir / "data"
team_dir  = data_dir / "team"
out_path = team_dir / "join_teams_salaries.csv"
df_all_teams_stats.to_csv(out_path, index=False, encoding="utf-8")