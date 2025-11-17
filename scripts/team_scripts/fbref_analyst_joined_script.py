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
fbref = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/join_teams_salaries.csv')
opta = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/teams_stats.csv')

# Filtrer les données des 5 grands championnats / Filter Big5 leagues / Filtrar los datos de las 5 grandes ligas
big5 = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
df_big5 = fbref[fbref['Competition'].isin(big5)]

# Charher le mapping des équipes / Load team mapping from JSON / Cargar la asignación de equipos
with open(mapping_path, "r", encoding="utf-8") as f:
    mapping = json.load(f)

opta["team_code"] = opta["team_code"].replace(mapping) # Appliquer le mapping sur les noms originaux / Apply mapping on original names / Aplicar la asignación de nombres originales

# Normaliser les noms / Normalize names (remove accents, lowercase) / Normalizar los nombres
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

df_big5["Squad_clean"] = df_big5["Squad"].apply(normalize_name)
opta["team_code_clean"] = opta["team_code"].apply(normalize_name)

# Associer les colonnes entres elles / Merge using normalized columns / Asociar las columnas entre sí
opta_merged = opta.merge(df_big5,left_on="team_code_clean",right_on="Squad_clean",how="left")

# Enlever les colonnes temporaires / Drop helper columns / Eliminar las columnas temporales
opta_merged = opta_merged.drop(columns=["Squad_clean", "team_code_clean","Competition", "Squad"])

# Calcul du nombre de points / Calculation of the number of points / Cálculo del número de puntos
opta_merged["pts_league"] = (opta_merged["Performance_W__keeper"] * 3 + opta_merged["Performance_D__keeper"])

# Classement / Ranking / Clasificación
def _rank_season(d: pd.DataFrame) -> pd.DataFrame:
    d = d.sort_values(["pts_league", "Team_Success_+/___ptime", "Performance_Gls__std"],ascending=[False, False, False]).copy()
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

# Dénominateur du total des passes / Denominator of total passes / Denominador del total de pases
den = (opta_merged["Long_Att__pass"] + opta_merged["Medium_Att__pass"] + opta_merged["Short_Att__pass"])

# Proportion de passes longues / Proportion of long passes / Proporción de pases largos
opta_merged["Long_Att__pass_prop"] = ((opta_merged["Long_Att__pass"] / den).where(den > 0, 0))
opta_merged["Long_Att__pass_prop"] = (opta_merged["Long_Att__pass_prop"] * 100).round(2)

# Dénominateur du total d'attaque / Denominator of total attack / Denominador del ataque total
den_attack = (opta_merged["sequences__direct_attacks__total"] + opta_merged["sequences__build_ups__total"] + opta_merged["attacking_misc__fast_breaks__total"])

# Proportion d'attaque directe / Proportion of direct attack / Proporción de ataque directo
opta_merged["direct_attack_prop"] = ((opta_merged["sequences__direct_attacks__total"] / den_attack).where(den_attack > 0, 0))
opta_merged["direct_attack_prop"] = (opta_merged["direct_attack_prop"] * 100).round(2)

# Proportion d'attaque placée / Proportion of build ups / Proporción de ataque colocado
opta_merged["build_ups_prop"] = ((opta_merged["sequences__build_ups__total"] / den_attack).where(den_attack > 0, 0))
opta_merged["build_ups_prop"] = (opta_merged["build_ups_prop"] * 100).round(2)

# Proportion de contre-attaque / Proportion of fast break / Proporción de contraataques
opta_merged["fast_break_prop"] = ((opta_merged["attacking_misc__fast_breaks__total"] / den_attack).where(den_attack > 0, 0))
opta_merged["fast_break_prop"] = (opta_merged["fast_break_prop"] * 100).round(2)

# On passe cette liste de statistiques brutes par 90 minutes / We run this list of raw statistics through 90 minutes / Pasamos esta lista de estadísticas brutas por 90 minutos
minutes_col = "Playing_Time_Min__ptime"
per90_cols = ["CrsPA__pass","Progression_PrgP__std","Progression_PrgC__std","Carries_Carries__poss","Carries_1/3__poss","Take_Ons_Att__poss","Take_Ons_Succ__poss",
    "Performance_Saves__keeper","Aerial_Duels_Won__misc","Receiving_PrgR__poss","Total_Cmp__pass","Carries_Mis__poss","Carries_Dis__poss",]
factor = 90.0 / opta_merged[minutes_col]
per90_df = opta_merged[per90_cols].apply(pd.to_numeric, errors="coerce").mul(factor, axis=0)
per90_df.columns = [f"Per_90_min_{c}" for c in per90_df.columns]
opta_merged[per90_df.columns] = per90_df.round(2)

# Liste des colonnes à ajuster / List of columns to adjust / Lista de columnas que hay que ajustar
cols_to_adjust = ["pressing__pressed_seqs","defending_defensive_actions__tackles","defending_defensive_actions__interceptions",
    "defending_defensive_actions__blocks","defending_defensive_actions__clearances"]

# Boucle pour créer les colonnes ajustées / Loop to create the adjusted columns / Bucle para crear columnas ajustadas
for col in cols_to_adjust:
    new_col = f"{col}_Padj"
    opta_merged[new_col] = (opta_merged[col] * (50 / (100 - opta_merged["passing__avg_poss"]))).round(2)

opta_merged.to_csv(out_path, index=False, encoding="utf-8") # Enregistrer le fichier csv final / Save the final merged CSV / Guardar el archivo CSV final