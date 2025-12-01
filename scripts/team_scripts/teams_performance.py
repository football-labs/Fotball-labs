# Importer les librairies / Importing libraries / Importar las bibliotecas
import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from scipy.stats import zscore
from scipy.stats import rankdata
from pathlib import Path
import unicodedata
import re

def _get_script_dir():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()

# Localisation des fichiers / File location / Ubicación de los archivos
script_dir = _get_script_dir()
data_team_dir = script_dir.parent.parent / "data" / "team"

team_path = data_team_dir / "fbref_analyst_joined.csv" # Chemins des fichiers / path of this files / La ruta de acceso a este archivos

out_db = data_team_dir / "database_team.csv" # Chemins de sortie / Exit paths / Salidas

team_data = pd.read_csv(team_path) # Récupération des données / Data recovery / Recuperación de datos

df = team_data # Chargement du fichier / Load file / Cargando el archivo

stat_cols = list(df.columns[8:]) # Définir la liste de colonne / Define columns / Definir la lista de columnas

# Inverser les statistiques où un chiffre élevé est une indication d'une sous-performance / Reversing statistics where a high figure is an indication of underperformance
# Invertir las estadísticas en las que una cifra elevada es indicativa de un rendimiento inferior al esperado
inverted_stats = [
    'defending_overall__goals','defending_overall__xg','defending_overall__shots','defending_overall__sot','defending_overall__xg_per_shot','defending_misc__touches_in_box',
    'defending_overall__shots_in_box_pct','defending_overall__goals_in_box_pct','defending_set_pieces__goals','defending_set_pieces__shots','defending_set_pieces__xg',
    'defending_misc__free_kicks__total','defending_misc__free_kicks__goals','defending_overall__goals_vs_xg','defending_overall__conv_pct','pressing__ppda','rank_league',
    'misc.__pens_conceded','attacking_misc__offsides','misc.__yellows','misc.__reds','misc.__fouls','misc.__errors_lead_to_shot','misc.__errors_lead_to_goal',
    'Per_90_min_Carries_Mis__poss','Per_90_min_Carries_Dis__poss']

# Normalisation / Normalization / Normalización
num = df[stat_cols].apply(pd.to_numeric, errors="coerce")
mins = num.min()
maxs = num.max()
ranges = maxs - mins
norm = (num - mins) / ranges
const_mask = (ranges == 0) | mins.isna() | maxs.isna()
if const_mask.any():
    norm.loc[:, const_mask] = 0.5
invert_cols = [c for c in stat_cols if c in inverted_stats]
if invert_cols:
    norm[invert_cols] = 1 - norm[invert_cols]
normalized_df = norm.add_suffix("_norm")
df = pd.concat([df, normalized_df], axis=1, copy=False)

# Choix des statistiques et de leurs poids associés / Choice of statistics and their associated weights / Selección de las estadísticas y sus ponderaciones asociadas
categories = {
    ## ON-BALL
    "goal_scoring_created": [(0.50, "Per_90_Minutes_npxG__std"),(0.15, "attacking_overall__shots"),(0.15, "attacking_overall__sot"),
            (0.15, "attacking_misc__touches_in_box"),(0.05, "attacking_overall__xg")],
    "finish": [(0.45, "Per_90_Minutes_G_PK__std"),(0.30, "attacking_overall__goals_vs_xg"),(0.10, "attacking_overall__conv_pct"),
            (0.10, "attacking_overall__xg_per_shot"), (0.05, "attacking_overall__goals")],
    "set_pieces_off": [(0.50, "attacking_set_pieces__goals"),(0.25, "attacking_set_pieces__xg"),(0.10, "attacking_misc__free_kicks__total"),
    (0.10, "attacking_misc__free_kicks__goals"), (0.05, "attacking_set_pieces__shots")],
    "building": [(0.20, "passing__final_third_passes__successful"), (0.25, "passing__through_balls"), (0.20, "Per_90_min_Progression_PrgP__std"),(0.15, "passing__all_passes__pct"),
        (0.10, "Per_90_min_Total_Cmp__pass"), (0.10, "Per_90_min_Receiving_PrgR__poss")],
    "projection": [(0.50, "Per_90_min_Progression_PrgC__std"),(0.30, "Per_90_min_Carries_1/3__poss"),(0.20, "Per_90_min_Carries_Carries__poss")],
    "crosses": [(0.35, "passing__crosses__total"),(0.3, "passing__crosses__pct"),(0.20, "attacking_misc__headers__goals"),
                (0.10, "attacking_misc__headers__total"),(0.05, "Per_90_min_CrsPA__pass")],
    "dribble": [(0.55, "Per_90_min_Take_Ons_Att__poss"),(0.45, "Take_Ons_Succ%__poss")],

    ## OFF-BALL
    "goal_scoring_conceded": [(0.40, "defending_overall__goals"),(0.25, "defending_overall__xg"), (0.10, "defending_overall__shots"),(0.10, "defending_overall__sot"),
          (0.05, "defending_misc__touches_in_box"),(0.05, "defending_overall__xg_per_shot"), (0.05, "defending_overall__goals_in_box_pct")],
    "defensive_actions": [(0.65, "Challenges_Tkl%__def"),(0.15, "defending_defensive_actions__interceptions_Padj"), (0.05, "defending_defensive_actions__tackles_Padj"),
        (0.05, "defending_defensive_actions__recoveries"), (0.05, "defending_defensive_actions__blocks_Padj"),(0.05, "defending_defensive_actions__clearances_Padj")],
    "set_pieces_def": [(0.50, "defending_set_pieces__goals"),(0.25, "defending_set_pieces__xg"),(0.10, "defending_misc__free_kicks__total"),
        (0.10, "defending_misc__free_kicks__goals"), (0.05, "defending_set_pieces__shots")],
    "efficiency_goalkeeper": [(0.60, "defending_overall__goals_vs_xg"),(0.35, "Performance_Save%__keeper"),(0.05, "Per_90_min_Performance_Saves__keeper")],
    "pressing": [(0.40, "pressing__ppda"),(0.30, "pressing__pressed_seqs"),(0.15, "pressing__start_distance_m"),
        (0.05, "pressing__high_turnovers__shot_ending"),(0.05, "pressing__high_turnovers__goal_ending"),
        (0.05, "pressing__high_turnovers__pct_end_in_shot")],

    ## STYLE OF PLAY
    "possession": [(0.65, "sequences__build_ups__goals"),(0.20, "sequences__build_ups__total"), (0.10, "passing__avg_poss"),(0.05, "sequences__ten_plus_passes")],
    "direct_play": [(0.65, "sequences__direct_attacks__goals"),(0.25, "sequences__direct_attacks__total"),(0.10, "Long_Att__pass_prop")], 
    "counter-attacking": [(0.65, "attacking_misc__fast_breaks__total"),(0.35, "attacking_misc__fast_breaks__goals")],

    ## OTHER
    "rank_league": [(0.50, "rank_league"),(0.40, "Team_Success_PPM__ptime"),(0.10, "Team_Success_+/_90__ptime")],
    "ground_duel": [(1.00, "defending_defensive_actions__ground_duels_won")],
    "aerial": [(0.65, "defending_defensive_actions__aerial_duels_won"),(0.35, "Per_90_min_Aerial_Duels_Won__misc")],
    "provoked_fouls": [(0.50, "misc.__fouled"),(0.20, "misc.__opp_yellows"),(0.15, "misc.__pens_won"),(0.10, "misc.__opp_reds"),
        (0.05, "defending_misc__offsides")],
    "faults_committed": [(0.50, "misc.__fouls"),(0.20, "misc.__yellows"),(0.15, "misc.__pens_conceded"),(0.10, "misc.__reds"),
        (0.05, "attacking_misc__offsides")],
    "waste": [(0.65, "misc.__errors_lead_to_goal"),(0.15, "misc.__errors_lead_to_shot"), (0.10, "Per_90_min_Carries_Mis__poss"),(0.10, "Per_90_min_Carries_Dis__poss")],
    "subs": [(0.65, "misc.__subs_goals"),(0.20, "Subs_Subs__ptime"),(0.15, "misc.__subs_used")], 
}

#  Calcul des scores par catégorie / Compute category scores / Cálculo de puntuaciones por categoría
def compute_category_score(row: pd.Series, stat_list) -> float:
    # Somme pondérée des versions normalisées (suffixe _norm), ramenée sur 100
    return 100 * sum(coef * row.get(f"{stat}_norm", 0.0) for coef, stat in stat_list)

for cat_name, stat_list in categories.items():
    df[f"score_{cat_name}_raw"] = df.apply(lambda row: compute_category_score(row, stat_list), axis=1)

# Normaliser les scores des catégories via percentiles (0-100) sur l'ensemble des équipes / Normalize category scores with percentiles (0-100) across all teams
# Normalizar las puntuaciones con percentiles (0-100) en todos los equipos
def percentile_rank(series: pd.Series):
    s = pd.to_numeric(series, errors="coerce")
    mask = s.notna()
    out = pd.Series([50.0] * len(s), index=s.index, dtype=float)
    if mask.sum() > 1:
        out.loc[mask] = 100 * (rankdata(s[mask], method="min") - 1) / (mask.sum() - 1)
    return out

for cat_name in categories.keys():
    raw_col = f"score_{cat_name}_raw"
    norm_col = f"score_{cat_name}"
    df[norm_col] = percentile_rank(df[raw_col]).round(0).astype("Int64")
    df.drop(columns=raw_col, inplace=True)

# Poids associé aux catégories de statistique / Weight associated with statistical categories / Peso asociado a las categorías estadísticas
stats_weights = {
    ## ON-BALL
    "goal_scoring_created": 0.07, "finish": 0.07, "set_pieces_off": 0.03, "building": 0.03, "projection": 0.02, "crosses": 0.02, "dribble": 0.02,
    ## OFF-BALL
    "goal_scoring_conceded": 0.07, "defensive_actions": 0.03, "set_pieces_def": 0.03, "efficiency_goalkeeper": 0.07,
    ## STYLE OF PLAY
    "possession": 0.05, "direct_play": 0.05, "counter-attacking": 0.05, "pressing": 0.05,
    ## OTHER
    "rank_league": 0.20, "ground_duel": 0.03, "aerial": 0.03, "provoked_fouls": 0.02, "faults_committed": 0.02, "waste": 0.03, "subs": 0.01,
}

# Calcul de la note finale / Compute final rating / Cálculo de la nota final
def compute_rating(row: pd.Series) -> float:
    return sum(row.get(f"score_{cat}", 0.0) * w for cat, w in stats_weights.items())

df["rating"] = df.apply(compute_rating, axis=1)

# Power Ranking par championnat (source Opta Analyst) / Power Ranking by league (according to Opta Analyst) / Clasificación por campeonato (fuente: Opta Analyst)
power_ranking = {"Premier League": 92.6,"Serie A": 87.0,"LaLiga": 87.0,"Bundesliga": 86.3,"Ligue 1": 85.3,}

# Référence = Power Ranking de Premier League / Benchmark = Power Ranking de Premier League / Referencia = Clasificación de poder de Premier League
reference_ranking = power_ranking["Premier League"]

# Appliquer une pénalité relative : ratio entre ranking / référence / Apply a relative penalty: ranking/reference ratio 
# Aplicar una penalización relativa: relación entre clasificación y referencia
df["power_ranking_raw"] = df["championship_name"].map(power_ranking).fillna(85.0)
df["power_ranking_penalty"] = 1 - (1 - (df["power_ranking_raw"] / reference_ranking)) / 3

# On établit la note finale / The final grade is determined / Se establece la nota final
df["rating_raw"] = pd.to_numeric(df["rating"], errors="coerce")
df["rating_percentile"] = percentile_rank(df["rating_raw"])
df["rating_cont"] = (0.4 * pd.to_numeric(df["rating_raw"], errors="coerce")
                     + 0.6 * pd.to_numeric(df["rating_percentile"], errors="coerce")) \
                    * pd.to_numeric(df["power_ranking_penalty"], errors="coerce")
df["rating"] = df["rating_cont"].round(0).astype("Int64")

# On détermine le classement du power ranking / The power ranking is determined / Se determina la clasificación del power ranking
df["rank_big5"] = df["rating_cont"].rank(method="min", ascending=False).astype("Int64")

# Retirer les colonnes _norm et les colonnes intermédiaires inutiles / Remove the _norm columns and unnecessary intermediate columns
# Eliminar las columnas _norm y las columnas intermedias innecesarias
cols_to_drop = [c for c in df.columns if c.endswith("_norm")] + ["power_ranking_raw", "power_ranking_penalty", "rating_raw","rating_percentile", "rating_cont"]
cols_to_drop = [c for c in cols_to_drop if c in df.columns]
df = df.drop(columns=cols_to_drop)

# Liste des colonnes dans l’ordre désiré / List of column in the desired order / Lista de columnas en el orden deseado
ordered_score_cols = ["id_season", "team_id", "season_name", "country", "championship_name", "team_code", "team_logo", "rank_big5","rating","score_goal_scoring_created",
    "score_finish", "score_set_pieces_off", "score_building", "score_projection","score_crosses","score_dribble", "score_goal_scoring_conceded", "score_defensive_actions",
    "score_set_pieces_def", "score_efficiency_goalkeeper","score_pressing", "score_possession", "score_direct_play","score_counter-attacking", "score_rank_league",
    "score_ground_duel","score_aerial", "score_provoked_fouls","score_faults_committed", "score_waste", "score_subs"]

# Conserver l'ordre souhaité puis le reste / Keep desired order then others / Mantener orden deseado y el resto
exist_ordered = [c for c in ordered_score_cols if c in df.columns]
other_cols = [c for c in df.columns if c not in exist_ordered]
df = df[exist_ordered + other_cols]

df.to_csv(out_db, index=False) # Sauvegarde du dataframe final / Save final DataFrame / Guardar el marco de datos final