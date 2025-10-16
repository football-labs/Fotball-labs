# Import des librairies / Importing libraries / Importación de bibliotecas
import pandas as pd
from unidecode import unidecode
from pathlib import Path
import json

# Chemins / Paths / Caminos
script_dir  = Path(__file__).resolve().parents[2]
data_dir  = script_dir / "data"
team_dir  = data_dir / "team"
mapping_path = team_dir / "mapping.json"
out_path = team_dir / "fbref_analyst_joined.csv"

# Charger les fichiers csv / Load CSV files / Cargar los archivos csv
fbref = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/join_teams_salaries.csv'
)
opta = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/teams_stats.csv'
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

# Calcul des points et du classement par championnat / Calculation of points and rankings by championship / Cálculo de puntos y clasificación por campeonato

# On s'assure que les colonnes sont bien numériques / Ensure that the columns are numeric / Nos aseguramos de que las columnas sean numéricas
num_cols = [
    "Performance_W__keeper",      # victoires / wins / victorias
    "Performance_D__keeper",      # nuls / draws / empates
    "Team_Success_+/___ptime",    # différence de buts / goal average / diferencia de goles
    "Performance_Gls__std"        # buts marqués / goals scored / goles marcados
]
for c in num_cols:
    if c in opta_merged.columns:
        opta_merged[c] = pd.to_numeric(opta_merged[c], errors="coerce").fillna(0)

# Calcul du nombre de points / Calculation of the number of points / Cálculo del número de puntos
opta_merged["pts_league"] = (
    opta_merged["Performance_W__keeper"] * 3
    + opta_merged["Performance_D__keeper"]
)

# Classement / Ranking / Clasificación
def _rank_season(d: pd.DataFrame) -> pd.DataFrame:
    d = d.sort_values(
        ["pts_league", "Team_Success_+/___ptime", "Performance_Gls__std"],
        ascending=[False, False, False]
    ).copy()
    # Régle pour le classement : pts, diff, buts marqués / Ranking rules: points, goal difference, goals scored / Regla para la clasificación: puntos, diferencia, goles marcados
    d["rank_league_tmp"] = range(1, len(d) + 1)
    d["rank_league"] = d.groupby(
        ["pts_league", "Team_Success_+/___ptime", "Performance_Gls__std"]
    )["rank_league_tmp"].transform("min")
    d.drop(columns=["rank_league_tmp"], inplace=True)
    d["rank_league"] = d["rank_league"].astype(int)
    return d

# On applique la fonction pour effectuer le classement / The function is applied to perform the classification / Se aplica la función para realizar la clasificación
opta_merged = (
opta_merged
    .groupby("id_season", group_keys=False)
    .apply(_rank_season)
)

# Enregistrer le fichier csv final / Save the final merged CSV / Guardar el archivo CSV final
opta_merged.to_csv(out_path, index=False, encoding="utf-8")
