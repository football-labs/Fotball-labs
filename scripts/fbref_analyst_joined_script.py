# Import des librairies / Importing libraries / Importación de bibliotecas
import pandas as pd
from unidecode import unidecode
from pathlib import Path
import json

# Chemins / Paths / Caminos
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
mapping_path = data_dir / "mapping.json"
out_path = data_dir / "fbref_analyst_joined.csv"

# Charger les fichiers csv / Load CSV files / Cargar los archivos csv
fbref = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/join_teams_salaries.csv'
)
opta = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/teams_stats.csv'
)

# Filtrer les données des 5 grands championnats / Filter Big5 leagues / Filtrar los datos de las 5 grandes ligas
big5 = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
df_big5 = fbref[fbref['Competition'].isin(big5)]

# Charher le mapping des équipes / Load team mapping from JSON / Cargar la asignación de equipos
with open(mapping_path, "r", encoding="utf-8") as f:
    mapping = json.load(f)

# Appliquer le mapping sur les noms originaux AVANT la normalisation / Apply mapping on original names BEFORE normalization / Aplicar la asignación de nombres originales ANTES de la normalización
opta["team_code"] = opta["team_code"].replace(mapping)

# Normaliser les noms / Normalize names (remove accents, lowercase) / Normalizar los nombres
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

df_big5["Squad_clean"] = df_big5["Squad"].apply(normalize_name)
opta["team_code_clean"] = opta["team_code"].apply(normalize_name)

# Associer les colonnes entres elles / Merge using normalized columns / Asociar las columnas entre sí
opta_merged = opta.merge(
    df_big5,                   
    left_on="team_code_clean",
    right_on="Squad_clean",
    how="left"
)
# Enlever les colonnes temporaires / Drop helper columns / Eliminar las columnas temporales
opta_merged = opta_merged.drop(columns=["Squad_clean", "team_code_clean","Competition", "Squad"])

# Enregistrer le fichier csv final / Save the final merged CSV / Guardar el archivo CSV final
opta_merged.to_csv(out_path, index=False, encoding="utf-8")
