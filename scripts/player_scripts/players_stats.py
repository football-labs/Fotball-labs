# Importer les librairies / Importing libraries / Importar las bibliotecas
import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from scipy.stats import zscore
from scipy.stats import rankdata
from pathlib import Path
import unicodedata
import re

## Extraction des données / Data extraction / Extracción de datos
def _get_script_dir():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()

# Localisation des fichiers / File location / Ubicación de los archivos
script_dir = _get_script_dir()
data_player_dir = (script_dir.parent.parent / "data" / "player").resolve()


# Chemins des fichiers / path of this files / La ruta de acceso a este archivos
fbref_path = data_player_dir / "light2025-2026.csv"
tm_path = data_player_dir / "players_tm.csv"

# Chemins de sortie / Exit paths / Salidas
out_fbref = data_player_dir / "unmatched_fbref.csv"
out_tm = data_player_dir / "unmatched_tm.csv"
out_db = data_player_dir / "database_player.csv"

##  Pré-traitement des données / Data processing / Preprocesamiento de datos
# Récupération des données / Data recovery / Recuperación de datos
fbref_data = pd.read_csv(fbref_path)
tm_data = pd.read_csv(tm_path)

# Colonnes descriptives à conserver / Descriptive columns to be retained / Columnas descriptivas que deben conservarse
cols_fixed = ["Player", "Nation", "Age", "Born", "Comp", "Pos"]

# Colonnes numérique / Digital columns / Columnas digitales
cols_num = ["MP", "Starts", "Min", "90s", "Tkl", "Won", "Succ","Cmp", "A-xAG", "PSxG+/-","G-PK", "npxG", "AvgLen","/90", "AvgDist"]

# Colonne contenant un pourcentage / Column containing a percentage / Columna que contiene un porcentaje
cols_pct = ["G/Sh", "SoT%", "CS%", "Launch%", "Stp%", "Cmp%", "Tkl%", "Succ%", "Won%", "Save%"] 

# Colonnes à transformer en statistiques par 90 minutes / Columns to convert to per-90 stats 
# Columnas que se convertirán en estadísticas cada 90 minutos
cols_per_90 = [
    "Gls", "Ast", "G+A", "G-PK", "PK", "CrdY", "CrdR", "npxG", "xAG","PrgC", "PrgP", "PrgR", "Sh", "SoT", "Cmp","1/3", "PPA", "CrsPA","Sw", "Crs","Tkl", "Int", "Clr", "Blocks_stats_defense",
    "Err","Fld","Touches", "Succ","Carries", "Mis","Dis", "Fls", "PKwon", "PKcon", "Recov", "GA","SoTA", "Saves", "PKm", "PKsv", "Thr", "Stp", "Won", "#OPA","PSxG","G-xG"]

# Nettoyage des colonnes non présentes / Keep only available columns / Limpieza de columnas no presentes
cols_fixed = [col for col in cols_fixed if col in fbref_data.columns]
cols_num = [col for col in cols_num if col in fbref_data.columns]
cols_pct = [col for col in cols_pct if col in fbref_data.columns]
cols_per_90 = [col for col in cols_per_90 if col in fbref_data.columns]

# Conversion en numérique / Convert relevant columns to numeric / Conversión a formato digital 
for col in cols_num + cols_pct + cols_per_90:
    fbref_data[col] = pd.to_numeric(fbref_data[col], errors='coerce')

# Statistiques par 90 minutes / Compute per-90 statistics / Estadísticas por 90 minutos
per90_df = (fbref_data[cols_per_90].div(fbref_data["Min"], axis=0) * 90).add_suffix("_per90").round(2)
per90_df = per90_df.fillna(0)

# On concatène les données / We concatenate the data / Se concatenan los datos
fbref_df = pd.concat([fbref_data, per90_df], axis=1)

# Récupération de la possession moyenne par équipe / Get average team possession / Recuperar la posesión media del equipo
data_team_dir = (script_dir.parent.parent / "data" / "team").resolve()
team_path = data_team_dir / "fbref_analyst_joined.csv"
team_df = pd.read_csv(team_path)
team_df = team_df[["team_code", "passing__avg_poss"]].copy()

# Moyenne de la possession par équipe / Average possession per team / Media de posesión por equipo
team_poss = (
    team_df
    .groupby("team_code", as_index=False)["passing__avg_poss"]
    .mean()
)

# Mapping des noms d équipe / Mapping team names / Asignación de nombres de equipos
df_to_info = {
    "Sevilla": "Sevilla FC","Betis": "Real Betis","RB Leipzig": "Leipzig","Osasuna": "CA Osasuna","Nott'ham Forest": "Nott'm Forest","Newcastle Utd": "Newcastle","Milan": "AC Milan",
    "Manchester Utd": "Man Utd","Manchester City": "Man City","Mallorca": "RCD Mallorca","Mainz 05": "Mainz","Leeds United": "Leeds","Köln": "1.FC Köln","Hamburger FC": "Hamburg",
    "Gladbach": "Mönchengladbach","Elche": "Elche CF","Eint Frankfurt": "Frankfurt","Celta Vigo": "Celta de Vigo","Atlético Madrid": "Atlético"}

fbref_df["team_code"] = fbref_df["Squad"].map(df_to_info).fillna(fbref_df["Squad"]) # Création du code équipe à partir de Squad / Build team_code from Squad / Crear team_code a partir de Squad

fbref_df = fbref_df.merge(team_poss, on="team_code", how="left") # Jointure de la possession moyenne sur fbref_df / Merge average possession into fbref_df / Unir la posesión media en fbref_df

# Calcul des statistiques ajustées à la possession / Compute possession adjusted statistics / Calcular estadísticas ajustadas por posesión

# On évite la division par zéro pour 100 % de possession / Avoid division by zero for 100 percent possession / Evitar división por cero cuando la posesión es 100 por ciento
denom = 100 - fbref_df["passing__avg_poss"]
denom = denom.replace(0, np.nan)

facteur_possession = 50 / denom # Facteur d ajustement / Adjustment factor / Factor de ajuste

cols_def_per90 = ["Tkl_per90","Int_per90","Clr_per90","Blocks_stats_defense_per90"] # Colonnes per90 à ajuster / Per90 columns to adjust / Columnas per90 a ajustar

# Création des colonnes ajustées _Padj / Create _Padj adjusted columns / Crear columnas ajustadas _Padj
for col in cols_def_per90:
    fbref_df[col + "_Padj"] = (fbref_df[col] * facteur_possession).round(2)

# Remplacement des NaN restants par 0 / Replace remaining NaN values with 0 / Reemplazar los valores NaN restantes por 0
padj_cols = [c + "_Padj" for c in cols_def_per90]
fbref_df[padj_cols] = fbref_df[padj_cols].fillna(0)

# Remplir les % manquants par la moyenne (par ligue puis globale) / Fill missing % by mean (by league then global) / Rellenar % faltantes por la media (por liga y luego global)
pct_cols_present = [c for c in cols_pct if c in fbref_df.columns]
if pct_cols_present:
    if "Comp" in fbref_df.columns:
        fbref_df[pct_cols_present] = fbref_df[pct_cols_present].fillna(
            fbref_df.groupby("Comp")[pct_cols_present].transform("mean")
        )
    fbref_df[pct_cols_present] = fbref_df[pct_cols_present].fillna(
        fbref_df[pct_cols_present].mean(numeric_only=True)
    )
    fbref_df[pct_cols_present] = fbref_df[pct_cols_present].round(2)

# On récupère le nombre maximum de match possible par championnat / We collect the maximum number of matches possible per league
# Se recupera el máximo número de partidos posibles por campeonato
MP_max_per_league = fbref_df.assign(MP=lambda d: pd.to_numeric(d["MP"], errors="coerce"))

# On en déduit le nombre maximum de minutes possibles par championnat  / From this, we can deduce the maximum number of minutes possible per league
# De ello se deduce el número máximo de minutos posibles por campeonato
comp_max_minutes = MP_max_per_league.groupby("Comp")["MP"].max().mul(90)

# On filtre les joueurs étant en dessous du filtre des 33 % de participations des minutes de son équipe
# We filter out players who are below the 33% participation filter for their team's minutes
# Se filtran los jugadores que están por debajo del filtro del 33 % de participación en los minutos de su equipo
fbref_df = MP_max_per_league.loc[
    MP_max_per_league["MP"] >= 0.33 * MP_max_per_league.groupby("Comp")["MP"].transform("max")
].copy()

## Merging tables / Fusion des tables / Fusionar tablas

# Normaliser les noms / Normalize names / Normalizar los nombres
def normalize_name(text):
    if isinstance(text, str):
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        text = re.sub(r"[^\w\s]", "", text)
        return text.lower().strip()
    return text

# Chargement et pré-traitement / Load and preprocess / Carga y pretratamiento
fbref_df = fbref_df[fbref_df["Born"].notna()]
tm_data = tm_data[tm_data["dateOfBirth"].notna()]
fbref_df["Born_year"] = fbref_df["Born"].astype(float).astype(int)
tm_data["birth_year"] = pd.to_datetime(tm_data["dateOfBirth"], errors="coerce").dt.year
tm_data = tm_data[tm_data["birth_year"].notna()]

fbref_df["Player_clean"] = fbref_df["Player"].apply(normalize_name)
tm_data["name_clean"] = tm_data["player_name"].apply(normalize_name)

# Récupération des championnats / League mapping / Recuperación de los campeonatos
club_mapping = {'Köln': '1.FC Köln','Milan': 'AC Milan','Alavés': 'Alavés','Arsenal': 'Arsenal','Aston Villa': 'Aston Villa','Atalanta': 'Atalanta','Athletic Club': 'Athletic Club',
    'Atlético Madrid': 'Atlético','Augsburg': 'Augsburg','Barcelona': 'Barcelona','Bayern Munich': 'Bayern Munich','Bologna': 'Bologna','Bournemouth': 'Bournemouth',
    'Brentford': 'Brentford','Brighton': 'Brighton','Burnley': 'Burnley','Osasuna': 'CA Osasuna','Cagliari': 'Cagliari','Celta Vigo': 'Celta de Vigo','Chelsea': 'Chelsea',
    'Como': 'Como','Cremonese': 'Cremonese','Crystal Palace': 'Crystal Palace','Dortmund': 'Dortmund','Elche': 'Elche CF','Espanyol': 'Espanyol','Everton': 'Everton',
    'Fiorentina': 'Fiorentina','Eint Frankfurt': 'Frankfurt','Freiburg': 'Freiburg','Fulham': 'Fulham','Genoa': 'Genoa','Getafe': 'Getafe','Girona': 'Girona','Hamburger SV': 'Hamburg',
    'Heidenheim': 'Heidenheim','Hellas Verona': 'Hellas Verona','Hoffenheim': 'Hoffenheim','Inter': 'Inter','Juventus': 'Juventus','Lazio': 'Lazio','Lecce': 'Lecce',
    'Leeds United': 'Leeds','RB Leipzig': 'Leipzig','Levante': 'Levante','Leverkusen': 'Leverkusen','Liverpool': 'Liverpool','Mainz 05': 'Mainz','Manchester City': 'Man City',
    'Manchester Utd': 'Man Utd','Gladbach': 'Mönchengladbach','Napoli': 'Napoli','Newcastle Utd': 'Newcastle', "Nott'ham Forest": "Nott'm Forest",'Parma': 'Parma',
    'Rayo Vallecano': 'Rayo Vallecano','Mallorca': 'RCD Mallorca','Betis': 'Real Betis','Real Madrid': 'Real Madrid','Real Sociedad': 'Real Sociedad','Roma': 'Roma',
    'Sassuolo': 'Sassuolo','Sevilla': 'Sevilla FC','St. Pauli': 'St. Pauli','Stuttgart': 'Stuttgart','Sunderland': 'Sunderland','Torino': 'Torino','Tottenham': 'Tottenham',
    'Udinese': 'Udinese','Union Berlin': 'Union Berlin','Valencia': 'Valencia','Villarreal': 'Villarreal','Werder Bremen': 'Werder Bremen','West Ham': 'West Ham',
    'Wolfsburg': 'Wolfsburg','Wolves': 'Wolves',

    # Équipe manquante pour l’instant
    'Pisa': 'Pisa Sporting Club','Oviedo': 'Real Oviedo',
    # Ligue 1
    'Paris S-G': 'Paris Saint-Germain','Marseille': 'Olympique de Marseille','Monaco': 'AS Monaco','Strasbourg': 'RC Strasbourg Alsace','Lille': 'LOSC Lille',
    'Lyon': 'Olympique Lyonnais','Nice': 'OGC Nice','Rennes': 'Stade Rennais FC','Paris FC': 'Paris FC','Lens': 'RC Lens','Toulouse': 'Toulouse FC','Brest': 'Stade Brestois 29',
    'Nantes': 'FC Nantes','Auxerre': 'AJ Auxerre','Lorient': 'FC Lorient','Metz': 'FC Metz','Le Havre': 'Le Havre AC','Angers': 'Angers SCO',
}

# Fonction pour associer les joueurs entre eux /  Function to pair players with each other / Función para asociar a los jugadores entre sí
def exact_match(fbref_df, tm_data, club_mapping):
    matches, matched_fbref, matched_tm = [], set(), set()
    for _, row in fbref_df.iterrows():
        name = row["Player_clean"]
        year = row["Born_year"]
        comp = row["Comp"]
        pos = row["Pos"]
        club = row["Squad"]

        if pd.isna(name) or pd.isna(year) or pd.isna(comp):
            continue

        club_id = club_mapping.get(club)
        if club_id is None:
            continue

        candidates = tm_data[
            (tm_data["name_clean"] == name) &
            (tm_data["birth_year"] == year) &
            (tm_data["club_name"] == club_id)
        ]

        if pos == "GK":
            candidates = candidates[candidates["position"] == "Goalkeeper"]
        else:
            candidates = candidates[candidates["position"] != "Goalkeeper"]

        if not candidates.empty:
            best_row = candidates.iloc[0]
            row_df = row.to_frame().T
            best_df = best_row.to_frame().T
            row_df["fbref_player_name"] = row["Player"]
            best_df["tm_player_name"] = best_row["player_name"]
            row_df["matching_pass"] = "exact_match"
            row_df["fuzzy_score"] = 100
            matches.append(pd.concat([row_df.reset_index(drop=True), best_df.reset_index(drop=True)], axis=1))
            matched_fbref.add(name)
            matched_tm.add(name)

    return matches, matched_fbref, matched_tm

# Fonction de l'association par ressemblance / Fuzzy match function / Función de la asociación por similitud
def fuzzy_match(fbref_subset, tm_subset, score_threshold, use_birth_year=True, label=""):
    matches, matched_fbref, matched_tm = [], set(), set()

    for _, row in fbref_subset.iterrows():
        player_name = row["Player_clean"]
        club_id = club_mapping.get(row.get("Squad"))
        born_year = row.get("Born_year")
        position = row.get("Pos")
        candidates = tm_subset.copy()

        if club_id:
            candidates = candidates[candidates["club_name"] == club_id]
        if use_birth_year:
            candidates = candidates[candidates["birth_year"] == born_year]

        if position == "GK":
            candidates = candidates[candidates["position"] == "Goalkeeper"]
        else:
            candidates = candidates[candidates["position"] != "Goalkeeper"]

        if candidates.empty:
            continue

        match = process.extractOne(
            player_name,
            candidates["name_clean"],
            scorer=fuzz.token_sort_ratio
        )

        if match and match[1] >= score_threshold:
            best_name, score = match[0], match[1]
            best_row = candidates[candidates["name_clean"] == best_name].iloc[0]

            row_df = row.to_frame().T.reset_index(drop=True)
            best_df = best_row.to_frame().T.reset_index(drop=True)

            row_df["fbref_player_name"] = row["Player"]
            best_df["tm_player_name"] = best_row["player_name"]
            row_df["matching_pass"] = label
            row_df["fuzzy_score"] = score

            matches.append(pd.concat([row_df, best_df], axis=1))

            matched_fbref.add(player_name)
            matched_tm.add(best_name)

    return matches, matched_fbref, matched_tm

# Liste des phases de matching / List of matching phases / Lista de fases de emparejamiento
matches_name, matched_fbref_name, matched_tm_name = exact_match(fbref_df, tm_data, club_mapping)
remaining_fbref = fbref_df[~fbref_df["Player_clean"].isin(matched_fbref_name)]
remaining_tm = tm_data[~tm_data["name_clean"].isin(matched_tm_name)]

matches_90, matched_fbref_90, matched_tm_90 = fuzzy_match(remaining_fbref, remaining_tm, 90, True, "90%_year")
remaining_fbref = remaining_fbref[~remaining_fbref["Player_clean"].isin(matched_fbref_90)]
remaining_tm = remaining_tm[~remaining_tm["name_clean"].isin(matched_tm_90)]

matches_75, matched_fbref_75, matched_tm_75 = fuzzy_match(remaining_fbref, remaining_tm, 75, True, "75%_year")
remaining_fbref = remaining_fbref[~remaining_fbref["Player_clean"].isin(matched_fbref_75)]
remaining_tm = remaining_tm[~remaining_tm["name_clean"].isin(matched_tm_75)]

matches_90noyear, matched_fbref_90noyear, matched_tm_90noyear = fuzzy_match(remaining_fbref, remaining_tm, 90, False, "90%_no_year")


matches_65, matched_fbref_65, matched_tm_65 = fuzzy_match(remaining_fbref, remaining_tm, 65, True, "65%_year")
remaining_fbref = remaining_fbref[~remaining_fbref["Player_clean"].isin(matched_fbref_65)]
remaining_tm = remaining_tm[~remaining_tm["name_clean"].isin(matched_tm_65)]

matches_80noyear, matched_fbref_80noyear, matched_tm_80noyear = fuzzy_match(remaining_fbref, remaining_tm, 80, False, "80%_no_year")

matches_60, matched_fbref_60, matched_tm_60 = fuzzy_match(remaining_fbref, remaining_tm, 60, True, "60%_year")

remaining_fbref = remaining_fbref[~remaining_fbref["Player_clean"].isin(matched_fbref_60)]
remaining_tm = remaining_tm[~remaining_tm["name_clean"].isin(matched_tm_60)]


manual_links = {
    "cucho": "cucho hernandez",
    "raul": "raul garcia",
    "đorđe petrovic": "djordje petrovic",
    "kike": "kike garcia",
    "toti gomes": "toti",
    "catena": "alejandro catena",
    "łukasz skorupski": "lukasz skorupski",
    "peque": "peque fernandez",
    "obite ndicka": "evan ndicka",
    "carmona": "jose angel carmona",
    "alfon": "alfon gonzalez",
    "andrefrank zambo anguissa": "frank anguissa",
    "jose luis garcia vaya": "pepelu",
    "ezequiel avila": "chimy avila",
    "milan đuric": "milan djuric",
    "jofre": "jofre carreras",
    "abel": "abel bretones",
    "musa altaamari": "mousa tamari",
    "souleymane toure": "isaak toure",
    
    "abdoul coulibaly" : "karim coulibaly",
    "chema" : "chema andres",
    "alexandre alemao" : "alemao",
    "brugui" : "roger brugue",
    "almoatasem al musrati" : "moatasem almusrati",
    "djene" : "dakonam djene",
    "jonny castro" : "jonny otto",
}

manual_matches = []
manual_matched_fbref, manual_matched_tm = set(), set()

for fbref_name, tm_name in manual_links.items():
    fbref_row = remaining_fbref[remaining_fbref["Player_clean"] == fbref_name]
    tm_row = remaining_tm[remaining_tm["name_clean"] == tm_name]

    if not fbref_row.empty and not tm_row.empty:
        fbref_row = fbref_row.iloc[0:1].copy()
        tm_row = tm_row.iloc[0:1].copy()
        fbref_row["fbref_player_name"] = fbref_row["Player"]
        tm_row["tm_player_name"] = tm_row["player_name"]
        fbref_row["matching_pass"] = "manual"
        fbref_row["fuzzy_score"] = 100
        combined = pd.concat([fbref_row.reset_index(drop=True), tm_row.reset_index(drop=True)], axis=1)
        manual_matches.append(combined)

        manual_matched_fbref.add(fbref_name)
        manual_matched_tm.add(tm_name)

# Supprimer ces joueurs des restants / Remove these players from the remainder / Eliminar estos jugadores de los restantes
remaining_fbref = remaining_fbref[~remaining_fbref["Player_clean"].isin(manual_matched_fbref)]
remaining_tm = remaining_tm[~remaining_tm["name_clean"].isin(manual_matched_tm)]

# Combiner tous les matchs / Combine all matches / Combinar todos los partidos
all_matches = pd.concat(matches_name + matches_90 + matches_75 + matches_90noyear + matches_65 +
                        matches_80noyear + matches_60 + manual_matches, ignore_index=True)

#all_matches = pd.concat(matches_name + matches_90 + matches_75 + matches_90noyear + manual_matches, ignore_index=True)

# Enlever les colonnes inutiles / Drop unwanted columns / Eliminar columnas no deseadas
cols_to_remove = [
    "Player", "Nation", "date_of_birth", "Player_clean", "name_clean", "name_lower", "match_score", "match_pass", "Born_year","birth_year","fbref_player_name",
    "matching_pass","fuzzy_score","dateOfBirth","age","tm_player_name", "club_id", "Unnamed: 0","Rk","Pos","Squad"]
all_matches.drop(columns=[col for col in cols_to_remove if col in all_matches.columns], inplace=True)

# Réarrangement des colonnes / Rearrange columns / Reordenación de columnas
final_column_order = [
    #"Player", "Nation", "date_of_birth", "Player_clean", "name_clean", "name_lower", "match_score", "match_pass", "Born_year", "birth_year",
    #"fbref_player_name",tm_player_name","matching_pass","fuzzy_score",
    "player_name", "player_id", "nationality", "Age", "Born", "position", "position_other", "height","foot","shirtNumber","joinedOn", "contract", "Comp","club_name","marketValue",
    "imageUrl","agent_name", "outfitter","status","MP","Starts","Min", "90s", "Gls_per90", "Ast_per90", "G+A_per90", "G-PK", "G-PK_per90", "G-xG_per90","PK_per90","npxG", "npxG_per90",
    "xAG_per90","PrgC_per90","G-xG", "A-xAG", "Sh_per90", "SoT_per90", "G/Sh", "SoT%","PrgP_per90","PrgR_per90", "Cmp","Cmp_per90", "Cmp%", "1/3_per90","PPA_per90","CrsPA_per90",
    "AvgDist","Sw_per90","Crs_per90", "Tkl_per90_Padj","Int_per90_Padj","Clr_per90_Padj","Blocks_stats_defense_per90_Padj","Tkl","Tkl_per90","Int_per90","Clr_per90",
    "Blocks_stats_defense_per90","Err_per90","Fld_per90", "Touches_per90","Succ","Succ_per90","Carries_per90", "Mis_per90","Dis_per90", "Fls_per90","PKwon_per90","PKcon_per90",
    "Recov_per90","Tkl%", "Succ%","Won", "Won_per90", "Won%", "CrdY_per90", "CrdR_per90","GA_per90","SoTA_per90", "Saves_per90", "PSxG_per90", "PSxG+/-","/90","PKm_per90","PKsv_per90",
    "Thr_per90", "Stp_per90","Save%","CS%","AvgLen", "Launch%", "Stp%", "#OPA_per90"
]
               
if 'player_name' in all_matches.columns and 'MP' in all_matches.columns:
    all_matches = all_matches.sort_values('MP', ascending=False)
    all_matches = all_matches.drop_duplicates(subset='player_name', keep='first')

existing_cols_ordered = [col for col in final_column_order if col in all_matches.columns]
remaining_cols = [col for col in all_matches.columns if col not in existing_cols_ordered]
all_matches = all_matches[existing_cols_ordered + remaining_cols]

# Sauvegarde des joueurs non associées / Save unmatched / Guardar jugadores no asociados
all_matched_fbref = matched_fbref_name.union(
    matched_fbref_90, matched_fbref_75, matched_fbref_90noyear, matched_fbref_65, matched_fbref_80noyear,
    matched_fbref_60, manual_matched_fbref
)
all_matched_tm = matched_tm_name.union(
    matched_tm_90, matched_tm_75, matched_tm_90noyear, matched_tm_65, matched_tm_80noyear,
    matched_tm_60, manual_matched_tm
)

#all_matched_fbref = matched_fbref_name.union(matched_fbref_90, matched_fbref_75, matched_fbref_90noyear, manual_matched_fbref)
#all_matched_tm = matched_tm_name.union(matched_tm_90, matched_tm_75, matched_tm_90noyear, manual_matched_tm)

unmatched_fbref_final = fbref_df[~fbref_df["Player_clean"].isin(all_matched_fbref)]
unmatched_tm_final = tm_data[~tm_data["name_clean"].isin(all_matched_tm)]

unmatched_fbref_final.to_csv(out_fbref, index=False)
unmatched_tm_final.to_csv(out_tm, index=False)


# Résumé / Summary / Resumen
print(f"Noms identique (même année, ligue, poste gardien) : {len(matches_name)}")
print(f"Matches à 90% (même année, ligue, poste gardien) : {len(matches_90)}")
print(f"Matches à 75% (même année, ligue, poste gardien) : {len(matches_75)}")
print(f"Matches à 90% (même ligue, poste gardien) : {len(matches_90noyear)}")
print(f"Matches à 65% (même année, ligue, poste gardien) : {len(matches_65)}")
print(f"Matches à 80% (même ligue, poste gardien) : {len(matches_80noyear)}")
print(f"Matches à 60% (même année, ligue, poste gardien) : {len(matches_60)}")
print(f"Matches manuels ajoutés : {len(manual_matches)}")
print(f"Total appariés : {len(all_matches)}")
print(f"Non appariés (fbref) : {len(unmatched_fbref_final)}")
print(f"Non appariés (tm) : {len(unmatched_tm_final)}")

## Rating / Notation

df = all_matches # Chargement du fichier / Load file / Cargando el archivo

stat_cols = df.columns[23:] # Définir la liste de colonne / Define columns / Definir la lista de columnas

# Inverser les statistiques où un chiffre élevé est une indication d'une sous-performance / Reversing statistics where a high figure is an indication of underperformance
# Invertir las estadísticas en las que una cifra elevada es indicativa de un rendimiento inferior al esperado
inverted_stats = ['Err_per90', 'PKcon_per90', 'CrdR_per90', 'CrdY_per90', 'Fls_per90', 'Mis_per90', 'Dis_per90',
                  'GA_per90', 'SoTA_per90', 'PSxG/SoT', 'PKm_per90','PSxG_per_90','PSxG', 'Pkm_per90']

# Catégorie des postes / Position categories / Categoría de puestos
position_category = {
    "Goalkeeper": "Goalkeepers","Centre-Back": "Central Defenders","Right-Back": "Fullbacks","Left-Back": "Fullbacks","Left Midfield": "Midfielders","Right Midfield": "Midfielders",
    "Central Midfield": "Midfielders","Defensive Midfield": "Midfielders","Attacking Midfield": "Attacking Midfielders / Wingers","Right Winger": "Attacking Midfielders / Wingers",
    "Left Winger": "Attacking Midfielders / Wingers","Second Striker": "Forwards","Centre-Forward": "Forwards"
}
df["position_group"] = df["position"].map(position_category)

# Fonction de normalisation / Normalization function / Función de normalización
def min_max_normalize(series, inverse=False):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series), index=series.index)
    norm = (series - min_val) / (max_val - min_val)
    return 1 - norm if inverse else norm

# Application de la normalisation par groupe selon le poste / Apply normalization per position group
# Aplicación de la normalización por grupo según el puesto
normalized_df = (
    df.groupby("position_group")[stat_cols]
      .transform(lambda s: min_max_normalize(s, inverse=(s.name in inverted_stats)))
      .add_suffix("_norm")
)
df = pd.concat([df, normalized_df], axis=1, copy=False)

# Choix des statistiques et de leurs poids associés / Choice of statistics and their associated weights / Selección de las estadísticas y sus ponderaciones asociadas
categories = {
    "goal_scoring_created": [(0.6, "npxG"),  (0.3, "npxG_per90"), (0.05, "SoT_per90"), (0.05, "Sh_per90")],
    "finish": [(0.5, "G-PK"), (0.2, "G-PK_per90"), (0.2, "G-xG"), (0.05, "G-xG_per90"),  (0.03, "G/Sh"), (0.02, "SoT%")],
    "building": [(0.4, "PrgP_per90"), (0.25, "Cmp_per90"), (0.15, "PrgR_per90"), (0.15, "Cmp%"), (0.025, "Sw_per90"), (0.025, "Crs_per90")],
    "creation": [(0.8, "xAG_per90"), (0.12, "Ast_per90"), (0.02, "1/3_per90"), (0.02, "PPA_per90"),
                 (0.02, "CrsPA_per90"), (0.02, "A-xAG")],
    "dribble": [(0.7, "Succ_per90"), (0.3, "Succ%")],
    "projection": [(0.6, "PrgC_per90"), (0.4, "Carries_per90")],
    "provoked_fouls": [(0.8, "Fld_per90"), (0.2, "PKwon_per90")],
    "waste": [(0.7, "Err_per90"), (0.15, "Mis_per90"), (0.15, "Dis_per90")],
    "defensive_actions": [(0.6, "Tkl%"), (0.15, "Int_per90_Padj"), (0.10, "Tkl_per90_Padj"), (0.05, "Recov_per90"), (0.05, "Clr_per90_Padj"),  (0.05, "Blocks_stats_defense_per90_Padj")], 
    "faults_committed": [(0.4, "CrdY_per90"), (0.3, "CrdR_per90"),  (0.2, "Fls_per90"), (0.1, "PKcon_per90")],
    "aerial": [(0.7, "Won_per90"), (0.3, "Won%")]
}
goalkeeper_categories = {
    "goal_scoring_conceded": [(0.45, "GA_per90"), (0.25, "PSxG_per90"), (0.15, "PSxG"), (0.05, "SoTA_per90"), (0.05, "PSxG/SoT"), (0.05, "PKm_per90")],
    "efficiency": [(0.45, "/90"), (0.25, "Save%"), (0.15, "PSxG+/-"), (0.05, "Saves_per90"), (0.05, "PKsv_per90"), (0.05, "CS%")],
    "error_fouls": [(0.6, "Err_per90"), (0.2, "PKcon_per90"), (0.1, "CrdR_per90"), (0.05, "CrdY_per90"), (0.05, "Fls_per90")],
    "short_clearance": [(1.0, "Launch%")],
    "long_clearance": [(0.5, "AvgLen"), (0.3, "Cmp%"), (0.1, "PrgP_per90"), (0.1, "xAG_per90")],
    "positioning": [(0.7, "AvgDist"), (0.3, "#OPA_per90")],
    "aerial_defense": [(0.6, "Stp%"), (0.2, "Won%"), (0.1, "Stp_per90"), (0.1, "Won_per90")]

}

#  Calcul des scores par catégorie / Compute category scores / Cálculo de puntuaciones por categoría
def compute_category_score(row, stat_list):
    return 100 * sum(coef * row.get(f"{stat}_norm", 0) for coef, stat in stat_list)

for cat_name, stat_list in {**categories, **goalkeeper_categories}.items():
    df[f"score_{cat_name}_raw"] = df.apply(lambda row: compute_category_score(row, stat_list), axis=1)

# Normaliser les scores des catégories par groupe de postes en utilisant les percentiles (0-100) / Normalize category scores per position_group using percentiles (0-100)
# Normalizar las puntuaciones de las categorías por grupo de puestos utilizando percentiles (0-100)
def percentile_rank(series):
    return 100 * (rankdata(series, method="min") - 1) / (len(series) - 1) if len(series) > 1 else pd.Series([50.0] * len(series), index=series.index)

for cat_name in categories.keys() | goalkeeper_categories.keys():
    raw_col = f"score_{cat_name}_raw"
    norm_col = f"score_{cat_name}"
    df[norm_col] = df.groupby("position_group")[raw_col].transform(percentile_rank).round(0).astype("Int64")
    df.drop(columns=raw_col, inplace=True)


# Poids associé aux catégories de statistique selon le poste du joueur / Weight associated with statistical categories by player position
# Peso asociado a las categorías estadísticas según la posición del jugador
position_weights = {
    "Centre-Back": {
        "goal_scoring_created": 0.06, "finish": 0.03, "building": 0.13, "creation": 0.06,"dribble": 0.02, "projection": 0.12, 
        "provoked_fouls": 0.03, "waste": 0.05,"defensive_actions": 0.2, "faults_committed": 0.2, "aerial": 0.1
    },
    "Right-Back": {
        "goal_scoring_created": 0.14, "finish": 0.07, "building": 0.12, "creation": 0.09,"dribble": 0.02, "projection": 0.10,
        "provoked_fouls": 0.04, "waste": 0.05,"defensive_actions": 0.17, "faults_committed": 0.17, "aerial": 0.03
    },
    "Left-Back": {
        "goal_scoring_created": 0.14, "finish": 0.07, "building": 0.12, "creation": 0.09,"dribble": 0.02, "projection": 0.10,
        "provoked_fouls": 0.04, "waste": 0.05,"defensive_actions": 0.17, "faults_committed": 0.17, "aerial": 0.03
    },
    "Right Midfield": {
        "goal_scoring_created": 0.16, "finish": 0.08, "building": 0.12, "creation": 0.10,"dribble": 0.02, "projection": 0.12,
        "provoked_fouls": 0.05, "waste": 0.05,"defensive_actions": 0.125, "faults_committed": 0.125, "aerial": 0.05
    },
    "Left Midfield": {
        "goal_scoring_created": 0.16, "finish": 0.08, "building": 0.12, "creation": 0.10,"dribble": 0.02, "projection": 0.12,
        "provoked_fouls": 0.05, "waste": 0.05,"defensive_actions": 0.125, "faults_committed": 0.125, "aerial": 0.05
    },
    "Defensive Midfield": {
        "goal_scoring_created": 0.1, "finish": 0.05, "building": 0.14, "creation": 0.09,"dribble": 0.02, "projection": 0.13,
        "provoked_fouls": 0.05, "waste": 0.05,"defensive_actions": 0.16, "faults_committed": 0.16, "aerial": 0.06
    },
    "Central Midfield": {
        "goal_scoring_created": 0.2, "finish": 0.1, "building": 0.10, "creation": 0.10,"dribble": 0.02, "projection": 0.10,
        "provoked_fouls": 0.04, "waste": 0.04,"defensive_actions": 0.125, "faults_committed": 0.125, "aerial": 0.05
    },
    "Attacking Midfield": {
        "goal_scoring_created": 0.35, "finish": 0.15, "building": 0.08, "creation": 0.12,"dribble": 0.04, "projection": 0.08,
        "provoked_fouls": 0.06, "waste": 0.05,"defensive_actions": 0.03, "faults_committed": 0.03, "aerial": 0.01
    },
    "Right Winger": {
        "goal_scoring_created": 0.35, "finish": 0.15, "building": 0.06, "creation": 0.10,"dribble": 0.10, "projection": 0.06,
        "provoked_fouls": 0.06, "waste": 0.05,"defensive_actions": 0.03, "faults_committed": 0.03, "aerial": 0.01
    },
    "Left Winger": {
        "goal_scoring_created": 0.35, "finish": 0.15, "building": 0.06, "creation": 0.10,"dribble": 0.10, "projection": 0.06,
        "provoked_fouls": 0.06, "waste": 0.05,"defensive_actions": 0.03, "faults_committed": 0.03, "aerial": 0.01
    },
    "Second Striker": {
        "goal_scoring_created": 0.4, "finish": 0.15, "building": 0.08, "creation": 0.13,"dribble": 0.03, "projection": 0.08,
        "provoked_fouls": 0.04, "waste": 0.03,"defensive_actions": 0.025, "faults_committed": 0.025, "aerial": 0.01
    },
    "Centre-Forward": {
        "goal_scoring_created": 0.5, "finish": 0.2, "building": 0.03, "creation": 0.08,"dribble": 0.03, "projection": 0.03,
        "provoked_fouls": 0.04, "waste": 0.03,"defensive_actions": 0.025, "faults_committed": 0.025, "aerial": 0.01
    }
}

goalkeeper_weights = {
    "goal_scoring_conceded": 0.01, "efficiency": 0.74, "error_fouls": 0.18, "short_clearance": 0.01,"long_clearance": 0.01, "positioning": 0.01, "aerial_defense": 0.02}

# Calcul de la note finale / Compute final rating / Cálculo de la nota final
def compute_rating(row):
    if row["position"] == "Goalkeeper":
        return sum(row[f"score_{cat}"] * weight for cat, weight in goalkeeper_weights.items())
    weights = position_weights.get(row["position"])
    if not weights:
        return None
    return sum(row[f"score_{cat}"] * weight for cat, weight in weights.items())

df["rating"] = df.apply(compute_rating, axis=1)

df["rating_raw"] = df["rating"]

# Équilibrer la note selon la position du joueur / Balance the rating according to the player's position / Equilibrar la nota según la posición del intérprete
df["rating_raw"] = pd.to_numeric(df["rating"], errors="coerce")
df["rating_percentile"] = df.groupby("position_group")["rating_raw"].transform(percentile_rank)
df["rating"] = (0.4 * df["rating_raw"] + 0.6 * df["rating_percentile"]).round(0).astype("Int64")

# Arrondir les scores et la note / Round scores and rating / Redondear las puntuaciones y la nota
score_cols = [col for col in df.columns if col.startswith("score_")]
df[score_cols + ["rating"]] = df[score_cols + ["rating"]].round(0).astype("Int64")

# Power Ranking par championnat (source Opta Analyst) / Power Ranking by league (according to Opta Analyst) / Clasificación por campeonato (fuente: Opta Analyst)
power_ranking = {"GB1": 92.6,"IT1": 87,"ES1": 87,"L1": 86.3,"FR1": 85.3}

reference_ranking = power_ranking["GB1"] # Référence = Power Ranking de GB1 / Benchmark = Power Ranking de GB1 / Referencia = Clasificación de poder de GB1

# Appliquer une pénalité relative : ratio entre ranking / référence (max 1) / Apply a relative penalty: ranking/reference ratio (max 1)
# Aplicar una penalización relativa: relación entre clasificación y referencia (máximo 1).
df["power_ranking_raw"] = df["Comp"].map(power_ranking).fillna(85)
#df["power_ranking_penalty"] = df["power_ranking_raw"] / reference_ranking
df["power_ranking_penalty"] = 1 - (1 - (df["power_ranking_raw"] / reference_ranking)) / 3

comp_to_max_minutes = comp_max_minutes.astype(float).to_dict() # Maximum de minutes selon la ligue / Maximum minutes depending on the league / Máximo de minutos según la liga

# Calcule du % de minutes jouées / Calculation of the % of minutes played / Cálculo del porcentaje de minutos jugados
df = df.copy()
df["Min"] = pd.to_numeric(df["Min"], errors="coerce")

# Calcule du nombre de minutes jouées par championnat / Calculate the number of minutes played per championship / Cálculo del número de minutos jugados por campeonato
df["max_minute_season"] = df["Comp"].map(comp_to_max_minutes)

# Calcule du ratio du minutes jouées par joueur / Calculation of the ratio of minutes played per player / Cálculo del ratio de minutos jugados por jugador
df["minute_ratio"] = df["Min"] / df["max_minute_season"]

# Pénalité logistique graduelle : pas de pénalité si ratio ≥ 0.6, max 0.8 si ratio ≤ 0.15 / Graduated logistical penalty: no penalty if ratio ≥ 0.6, max 0.8 if ratio ≤ 0.15
# Penalización logística gradual: sin penalización si la ratio es ≥ 0,6, máximo 0,8 si la ratio es ≤ 0,15
def compute_minutes_penalty(ratio):
    if ratio >= 0.6:
        return 1.0
    elif ratio <= 0.33:
        return 0.85
    else:
        return 0.85 + 0.15 * (ratio - 0.33) / (0.6 - 0.33)

df["minutes_penalty"] = df["minute_ratio"].apply(compute_minutes_penalty)

df["rating"] = (df["rating"] * df["power_ranking_penalty"] * df["minutes_penalty"]).round(0).astype("Int64")


# Sauvegarde du dataframe final / Save final DataFrame / Guardar el marco de datos final
df = df[[col for col in df.columns if not col.endswith('_norm') and col != "position_group"]]
df.drop(columns=["power_ranking_raw", "power_ranking_penalty", "max_minute_season", "minute_ratio","minutes_penalty", "rating_raw", "rating_percentile"  ], inplace=True)

# Liste des colonnes dans l’ordre désiré / List of column in the desired order / Lista de columnas en el orden deseado
ordered_score_cols = [
    "player_name", "player_id", "nationality", "Age", "Born", "position", "position_other", "height","foot","shirtNumber","joinedOn", "contract", "Comp","club_name",
    "marketValue", "imageUrl","agent_name", "outfitter","status","rating","score_goal_scoring_created","score_finish", "score_building", "score_creation","score_dribble",
    "score_projection","score_defensive_actions", "score_waste", "score_faults_committed", "score_provoked_fouls","score_aerial","score_goal_scoring_conceded", "score_efficiency",
    "score_error_fouls","score_short_clearance","score_long_clearance","score_positioning", "score_aerial_defense"
]

other_cols = [col for col in df.columns if col not in ordered_score_cols and not col.endswith('_norm') and col != "position_group"]
df = df[ordered_score_cols + other_cols]

# Supprime les ellipses finales ("...", "…"), espaces adjacents, normalise les espaces / Removes trailing ellipses (‘...’, ‘…’), adjacent spaces, normalises spaces
# Elimina los puntos suspensivos finales («...», «…»), los espacios adyacentes y normaliza los espacios
df["agent_name"] = (
    df["agent_name"]
      .astype("string")
      .str.replace(r"\s*(?:\u2026|\.{3,})\s*$", "", regex=True)
      .str.replace("\u00A0", " ", regex=False)
      .str.replace(r"\s+", " ", regex=True)
      .str.strip()
)

df.to_csv(out_db, index=False)

print("Fichier mis à jour")