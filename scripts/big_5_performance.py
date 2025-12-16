"""

Ceci est la page principale du projet, veuillez trouver ci dessous une brève présentation du projet, ainsi que le code associé.
This is the main page of the project, please find below a brief presentation of the project, as well as the associated code.
Esta es la página principal del proyecto. A continuación encontrará una breve presentación del proyecto, así como el código asociado
"""

# Import des librairies / Importing libraries
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import os
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from mplsoccer import PyPizza, FontManager
from matplotlib.patches import Patch
import base64
import re
from itertools import chain

# Affichage du titre et du logo de l'application web / Display of web application title and logo / Visualización del título y el logotipo de la aplicación web
st.set_page_config(page_title="Big 5 Performance 25/26 ⚽ ", page_icon="💯", layout="centered")

# Langue dans session_state / Language in session_state / Idioma en session_state
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

lang = st.sidebar.selectbox(
    "Choisissez votre langue / Choose your language / Elige tu idioma", ["Français", "English", "Español"]
)
st.session_state["lang"] = lang

### Fonction pour la partie Joueur / Function for the Player part / Función para la parte Jugador

# Affichage de la valeur du joueur / Player value display / Visualización del valor del jugador
def format_market_value(eur):
    if pd.isna(eur):
        return "-"
    if eur >= 1_000_000:
        return f"{eur / 1_000_000:.1f}M €"
    elif eur >= 1_000:
        return f"{eur / 1_000:.0f}K €"
    else:
        return f"{int(eur)} €"

# Dictionnaire de traduction des postes de joueurs et de leur pays / Translation dictionary for player positions and his country / Diccionario de traducción de posiciones de jugadores y sus países
position_translation = {
    "fr": {
        "Second Striker": "Second Attaquant","Centre-Forward": "Attaquant-Centre","Right-Back": "Défenseur Droit","Left-Back": "Défenseur Gauche","Right Winger": "Ailier Droit",
        "Left Winger": "Ailier Gauche","Right Midfield": "Milieu Droit","Left Midfield": "Milieu Gauche","Attacking Midfield": "Milieu Attaquant","Goalkeeper": "Gardien",
        "Defensive Midfield": "Milieu Défensif","Central Midfield": "Milieu Central","Centre-Back": "Défenseur Central",
    },
    "es": {
        "Second Striker": "Segundo delantero","Centre-Forward": "Delantero centro","Right-Back": "Lateral derecho","Left-Back": "Lateral izquierdo","Right Winger": "Extremo derecho",
        "Left Winger": "Extremo izquierdo","Right Midfield": "Centrocampista derecho","Left Midfield": "Centrocampista izquierdo","Attacking Midfield": "Mediapunta",
        "Goalkeeper": "Portero","Defensive Midfield": "Mediocentro defensivo","Central Midfield": "Mediocentro","Centre-Back": "Defensa central",
    }
}

country_translation = {
    "fr": {
        "Germany": "Allemagne","Spain": "Espagne","Italy": "Italie","England": "Angleterre","Netherlands": "Pays-Bas","Brazil": "Brésil","Argentina": "Argentine","Belgium": "Belgique",
        "Croatia": "Croatie","Switzerland": "Suisse","Senegal": "Sénégal","Cameroon": "Cameroun","Morocco": "Maroc","Albania": "Albanie","Algeria": "Algérie","Andorra": "Andorre",
        "Armenia": "Arménie","Australia": "Australie","Austria": "Autriche","Bosnia-Herzegovina": "Bosnie-Herzégovine","Cape Verde": "Cap-Vert",
        "Central African Republic": "République centrafricaine","Chile": "Chili","Colombia": "Colombie","Czech Republic": "Tchéquie","Denmark": "Danemark",
        "DR Congo": "République démocratique du Congo","Ecuador": "Équateur","Egypt": "Égypte","Equatorial Guinea": "Guinée équatoriale","Estonia": "Estonie","Finland": "Finlande",
        "French Guiana": "Guyane française","Georgia": "Géorgie","Greece": "Grèce","Guinea": "Guinée","Guinea-Bissau": "Guinée-Bissau","Hungary": "Hongrie","Iceland": "Islande",
        "Indonesia": "Indonésie","Ireland": "Irlande","Jamaica": "Jamaïque","Japan": "Japon","Jordan": "Jordanie","Korea, South": "Corée du Sud","Libya": "Libye","Lithuania": "Lituanie",
        "Malta": "Malte","Mexico": "Mexique","New Zealand": "Nouvelle-Zélande","North Macedonia": "Macédoine du Nord","Northern Ireland": "Irlande du Nord","Norway": "Norvège",
        "Peru": "Pérou","Poland": "Pologne","Romania": "Roumanie","Russia": "Russie","Scotland": "Écosse","Serbia": "Serbie","Slovakia": "Slovaquie","Slovenia": "Slovénie",
        "Sweden": "Suède","Syria": "Syrie","The Gambia": "Gambie","Tunisia": "Tunisie","Türkiye": "Turquie","United States": "États-Unis","Uzbekistan": "Ouzbékistan",
        "Wales": "Pays de Galles","Zambia": "Zambie",
    },
    "es": {
        "France": "Francia","Canada": "Canadá","Germany": "Alemania","Spain": "España","Italy": "Italia","England": "Inglaterra","Netherlands": "Países Bajos","Brazil": "Brasil",
        "Argentina": "Argentina","Belgium": "Bélgica","Croatia": "Croacia","Switzerland": "Suiza","Senegal": "Senegal","Cameroon": "Camerún","Morocco": "Marruecos","Albania": "Albania",
        "Algeria": "Argelia","Andorra": "Andorra","Armenia": "Armenia","Australia": "Australia","Austria": "Austria","Bosnia-Herzegovina": "Bosnia y Herzegovina","Cape Verde": "Cabo Verde","Central African Republic": "República Centroafricana","Chile": "Chile",
        "Colombia": "Colombia","Czech Republic": "Chequia","Denmark": "Dinamarca","DR Congo": "República Democrática del Congo","Ecuador": "Ecuador","Egypt": "Egipto",
        "Equatorial Guinea": "Guinea Ecuatorial","Estonia": "Estonia","Finland": "Finlandia","French Guiana": "Guayana Francesa","Georgia": "Georgia","Greece": "Grecia","Guinea": "Guinea",
        "Guinea-Bissau": "Guinea-Bisáu","Hungary": "Hungría","Iceland": "Islandia","Indonesia": "Indonesia","Ireland": "Irlanda","Jamaica": "Jamaica","Japan": "Japón","Jordan": "Jordania",
        "Korea, South": "Corea del Sur","Libya": "Libia","Lithuania": "Lituania","Malta": "Malta","Mexico": "México","New Zealand": "Nueva Zelanda","North Macedonia": "Macedonia del Norte",
        "Northern Ireland": "Irlanda del Norte","Norway": "Noruega","Peru": "Perú","Poland": "Polonia","Romania": "Rumanía","Russia": "Rusia","Scotland": "Escocia","Serbia": "Serbia",
        "Slovakia": "Eslovaquia","Slovenia": "Eslovenia","Sweden": "Suecia","Syria": "Siria","The Gambia": "Gambia","Tunisia": "Túnez","Türkiye": "Turquía","United States": "Estados Unidos",
        "Ukraine": "Ucrania","Uzbekistan": "Uzbekistán","Wales": "Gales","Zambia": "Zambia","Zimbabwe": "Zimbabue","Panama": "Panamá","Haiti": "Haití","Guadeloupe": "Guadalupe",
        "Gabon": "Gabón","Cote d'Ivoire": "Costa de Marfil",
    }
}

base_stat_translation = {
    "fr": {
        # Joueurs
        "goal_scoring_created": "Création de buts","goal_scoring_conceded": "Occasions concédées","efficiency": "Efficacité","error_fouls": "Erreurs et fautes",
        "short_clearance": "Relance courte","long_clearance": "Relance longue","positioning": "Positionnement","aerial_defense": "Jeu aérien défensif","finish": "Finition",
        "building": "Construction du jeu","creation": "Création d'occasions","dribble": "Dribbles","projection": "Projection","defensive_actions": "Actions défensives",
        "waste": "Pertes de balle","faults_committed": "Fautes commises","provoked_fouls": "Fautes provoquées","aerial": "Jeu aérien",
        # Équipes
        "set_pieces_off": "CPA offensifs","crosses": "Centres","set_pieces_def": "CPA défensifs","efficiency_goalkeeper": "Efficacité du gardien","pressing": "Pressing",
        "possession": "Jeu de possession","direct_play": "Jeu direct","counter-attacking": "Jeu en contre-attaque","rank_league": "Performance en championnat",
        "ground_duel": "Duels au sol","subs": "Remplacements",
    },
    "es": {
        # Jugadores
        "goal_scoring_created": "Creación de goles","goal_scoring_conceded": "Ocasiones concedidas","efficiency": "Eficiencia","error_fouls": "Errores y faltas",
        "short_clearance": "Salida en corto","long_clearance": "Salida en largo","positioning": "Posicionamiento","aerial_defense": "Juego aéreo defensivo","finish": "Finalización",
        "building": "Construcción del juego","creation": "Creación de ocasiones","dribble": "Regates","projection": "Proyección","defensive_actions": "Acciones defensivas",
        "waste": "Pérdidas de balón","faults_committed": "Faltas cometidas","provoked_fouls": "Faltas provocadas","aerial": "Juego aéreo",
        # Equipos
        "set_pieces_off": "Balones parados ofensivos","crosses": "Centros","set_pieces_def": "Balones parados defensivos","efficiency_goalkeeper": "Eficiencia del portero",
        "pressing": "Presión","possession": "Juego de posesión","direct_play": "Juego directo","counter-attacking": "Juego de contraataque","rank_league": "Rendimiento en el campeonato",
        "ground_duel": "Duelos en el suelo","subs": "Sustituciones",
    },
    "eng": {
        # Players
        "goal_scoring_created": "Goal creation","goal_scoring_conceded": "Chances conceded","efficiency": "Efficiency","error_fouls": "Errors and fouls",
        "short_clearance": "Short clearance","long_clearance": "Long clearance","positioning": "Positioning","aerial_defense": "Aerial defense","finish": "Finishing",
        "building": "Build-up play","creation": "Chance creation","dribble": "Dribbling","projection": "Projection","defensive_actions": "Defensive actions",
        "waste": "Ball losses","faults_committed": "Fouls committed","provoked_fouls": "Fouls won","aerial": "Aerial play",
        # Teams
        "set_pieces_off": "Offensive set-pieces","crosses": "Crosses","set_pieces_def": "Defensive set-pieces","efficiency_goalkeeper": "Goalkeeper efficiency","pressing": "Pressing",
        "possession": "Possession play","direct_play": "Direct play","counter-attacking": "Counter-attacking play","rank_league": "League performance",
        "ground_duel": "Ground duels","subs": "Substitutions",
    },
}

foot_translation = {
    "fr": {"right": "Droit", "left": "Gaucher", "both": "Ambidextre"}, "es": {"right": "Diestro", "left": "Zurdo", "both": "Ambidiestro"},
}

foot_en_pretty = {"right": "Right", "left": "Left", "both": "Both"}

style_translation = {
    "fr": {
        "Direct Play": "Jeu direct","Possession Play": "Jeu de possession","Counter-Attacking": "Jeu de contre-attaque","Mixed": "Jeu mixte",
        "High Press": "Pressing haut","Low Block": "Bloc bas","Mid Block": "Bloc médian",
    },
    "es": {
        "Direct Play": "Juego directo", "Possession Play": "Juego de posesión","Counter-Attacking": "Juego de contraataque", "Mixed": "Juego mixto",
        "High Press": "Presión alta", "Low Block": "Bloque bajo","Mid Block": "Bloque medio",
    },
}

categories_stats_translation = {
    "fr": {
        "Offensive": "Jeu avec ballon","Set-Pieces (Offensive)": "Coup de pied arrêtés (Offensif)","Style of play" : "Style de jeu","Passing" : "Jeu de passe","Pressing": "Pressing",
        "Defending": "Jeu sans ballon","Set-Pieces (Defensive)": "Coup de pied arrêtés (Défensif)","Penalties": "Penalties", "Foul": "Faute", "Duel": "Duel", "Take-ons": "Dribble", 
        "Results": "Résultats", "Miscellaneous": "Autre", 
    },
    "es": {
        "Offensive": "Juego con balón","Set-Pieces (Offensive)": "Jugadas a balón parado (Ofensivas)","Style of play": "Estilo de juego","Passing": "Juego de pases",
        "Pressing": "Presión","Defending": "Juego sin balón","Set-Pieces (Defensive)": "Jugadas a balón parado (Defensivas)","Penalties": "Penaltis","Foul": "Faltas",
        "Duel": "Duelo","Take-ons": "Regate","Results": "Resultados","Miscellaneous": "Otros",
    }
}

# Utilise la traduction si besoin selon la langue de l'application / Use translation if necessary depending on the language of the application
# Utiliza la traducción si es necesario según el idioma de la aplicación
def translate_position(sub_position: str, lang: str = "fr") -> str:
    return position_translation.get(lang, {}).get(sub_position, sub_position)

def translate_country(country_en: str, lang: str = "fr") -> str:
    lang_map = country_translation.get(lang, {})
    if country_en in lang_map:
        return lang_map[country_en]
    return country_translation.get("fr", {}).get(country_en, country_en)

def translate_base_stat(key: str, lang: str = "fr") -> str:
    if key in base_stat_translation.get(lang, {}):
        return base_stat_translation[lang][key]
    if key in base_stat_translation.get("fr", {}):
        return base_stat_translation["fr"][key]
    return key.replace("_", " ").capitalize()

def translate_foot(foot_raw: str | None, lang: str = "fr") -> str | None:
    if foot_raw is None:
        return None
    s = str(foot_raw).strip()
    if s == "" or (isinstance(foot_raw, float) and pd.isna(foot_raw)):
        return None
    key = s.lower()
    if lang in foot_translation:
        return foot_translation[lang].get(key, s)
    return foot_en_pretty.get(key, s)

def translate_position_list(pos_str: str | None, lang: str = "fr") -> str | None:
    if pos_str is None or (isinstance(pos_str, float) and pd.isna(pos_str)):
        return None
    s = str(pos_str).strip()
    if not s:
        return None
    items = [p.strip() for p in s.split(",") if p.strip()]
    if not items:
        return None
    translated = [translate_position(p, lang=lang) for p in items]
    return ", ".join(translated) if translated else None

def translate_style(style_en: str, lang: str = "fr") -> str:
    if not isinstance(style_en, str):
        return style_en
    lang_map = style_translation.get(lang, {})
    if style_en in lang_map:
        return lang_map[style_en]
    return style_translation.get("fr", {}).get(style_en, style_en)

def translate_categories_stats(name_en: str, lang: str = "fr") -> str:
    if not isinstance(name_en, str):
        return name_en
    lang_map = categories_stats_translation.get(lang, {})
    return lang_map.get(name_en, name_en)

# Mapping des noms d'équipe  / Mapping of teams name  / Asignación de nombres de equipos
df_to_info = {
    "Sevilla": "Sevilla FC","Betis": "Real Betis","RB Leipzig": "Leipzig","Osasuna": "CA Osasuna","Nott'ham Forest": "Nott'm Forest","Newcastle Utd": "Newcastle","Milan": "AC Milan",
    "Manchester Utd": "Man Utd","Manchester City": "Man City","Mallorca": "RCD Mallorca","Mainz 05": "Mainz","Leeds United": "Leeds","Köln": "1.FC Köln","Hamburger FC": "Hamburg",
    "Gladbach": "Mönchengladbach","Elche": "Elche CF","Eint Frankfurt": "Frankfurt","Celta Vigo": "Celta de Vigo","Atlético Madrid": "Atlético", 'Oviedo': 'Real Oviedo',
    "Paris S-G" : "PSG",'Strasbourg': 'R. Strasbourg','Rennes': 'Stade Rennais','Brest': 'Stade Brestois','Nantes': 'FC Nantes','Auxerre': 'AJ Auxerre','Lorient': 'FC Lorient',
    'Metz': 'FC Metz','Le Havre': 'Le Havre AC','Angers': 'Angers SCO',
}

# Catégorie des postes pour le radar / Position category for the radar plot / Categoría de posiciones para el radar plot
position_category = {
    "Goalkeeper": "Gardiens de but","Centre-Back": "Défenseurs centraux","Right-Back": "Défenseurs latéraux","Left-Back": "Défenseurs latéraux","Left Midfield": "Milieux de terrain",
    "Right Midfield": "Milieux de terrain","Central Midfield": "Milieux de terrain","Defensive Midfield": "Milieux de terrain","Attacking Midfield": "Milieux offensifs / Ailiers",
    "Right Winger": "Milieux offensifs / Ailiers","Left Winger": "Milieux offensifs / Ailiers","Second Striker": "Attaquants","Centre-Forward": "Attaquants"
}

# Statistiques par catégorie pour le radar / Statistics by categorie for the radar plot / Estadísticas por categoría para el radar plot
category_stats_player = {
    "Gardiens de but": ["GA_per90", "PSxG_per90", "/90", "Save%", "PSxG+/-", "Err_per90","Launch%", "AvgLen", "Cmp%", "AvgDist", "#OPA_per90", "Stp%"],
    "Défenseurs centraux": ["G-PK_per90", "PrgP_per90","Cmp%","xAG_per90","PrgC_per90","Err_per90","Tkl%","Int_per90_Padj","Tkl_per90_Padj","CrdY_per90","Won_per90","Won%" ],
    "Défenseurs latéraux": ["G-PK_per90", "PrgP_per90", "Cmp%", "xAG_per90", "Succ_per90", "PrgC_per90", "Err_per90", "Tkl%", "Int_per90_Padj", "Tkl_per90_Padj", "CrdY_per90", "Won%"],
    "Milieux de terrain": ["G-PK_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "PrgC_per90", "Fld_per90", "Err_per90", "Tkl%", "Int_per90_Padj", "CrdY_per90", "Won%"],
    "Milieux offensifs / Ailiers": ["npxG_per90","G-PK_per90", "G-xG_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "Succ_per90", "Succ%", "PrgC_per90", "Fld_per90", "Dis_per90"],
    "Attaquants": ["npxG_per90","Sh_per90", "G-PK_per90", "G-xG_per90", "G/Sh", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90","Succ_per90", "PrgC_per90", "Dis_per90"    ]
}

invert_stats = {"GA_per90", "PSxG_per90","Err_per90", "CrdY_per90", "Dis_per90"}

stats_team = {
    "Offensive": [
        "attacking_overall__goals","attacking_overall__xg","attacking_overall__goals_vs_xg","attacking_overall__shots","attacking_overall__sot","attacking_overall__conv_pct",
	    "attacking_overall__xg_per_shot","attacking_misc__touches_in_box","attacking_misc__hit_post","attacking_misc__offsides", "attacking_misc__headers__total",
        "attacking_misc__headers__goals", "performance_gls","performance_g_minus_pk", "expected_xg","expected_npxg", "per90_g_minus_pk","per90_npxg","shooting_sh",
        "shooting_sot","shooting_dist",
    ],
    "Set-Pieces (Offensive)": [
        "attacking_set_pieces__goals","attacking_set_pieces__shots","attacking_set_pieces__xg","attacking_set_pieces__goal_pct","attacking_set_pieces__shot_pct",
        "attacking_set_pieces__xg_pct", "attacking_misc__free_kicks__total","attacking_misc__free_kicks__goals",
    ],
    "Style of play": [
        "attacking_misc__fast_breaks__total","attacking_misc__fast_breaks__goals","sequences__ten_plus_passes","sequences__direct_speed","sequences__passes_per_seq",
        "sequences__sequence_time","sequences__build_ups__total","sequences__build_ups__goals","sequences__direct_attacks__total","sequences__direct_attacks__goals",
        "direct_attack_prop","build_ups_prop","fast_break_prop",
    ],
    "Passing": [
        "passing__avg_poss","passing__all_passes__pct","passing__final_third_passes__successful","passing__final_third_passes__pct","passing__pass_direction__fwd",
        "passing__pass_direction__bwd","passing__pass_direction__left","passing__pass_direction__right","passing__crosses__total","passing__crosses__successful",
        "passing__crosses__pct","passing__through_balls", "progression_prgc","progression_prgp", "carries_total", "carries_final_third","carries_mis","carries_dis",
        "receiving_prgr", "performance_crs", "passing_cmp","short_cmp","short_cmp_pct","medium_cmp","medium_cmp", "long_cmp","long_cmp_pct", "passing_ppa","passing_crspa",
        "passing_prgp", "Long_Att__pass_prop", "Per_90_min_passing_crspa","Per_90_min_passing_prgp","Per_90_min_progression_prgc","Per_90_min_carries_total",
        "Per_90_min_carries_final_third","Per_90_min_receiving_prgr","Per_90_min_passing_cmp","Per_90_min_carries_mis","Per_90_min_carries_dis"
    ],
    "Pressing": [
        "pressing__pressed_seqs","pressing__pressed_seqs_Padj","pressing__ppda","pressing__start_distance_m", "pressing__high_turnovers__shot_ending",
        "pressing__high_turnovers__goal_ending","pressing__high_turnovers__pct_end_in_shot",
    ],
    "Defending": [
        "defending_overall__goals","defending_overall__xg","defending_overall__goals_vs_xg","defending_overall__shots","defending_overall__sot",
        "defending_overall__conv_pct","defending_overall__xg_per_shot","defending_overall__shots_in_box_pct","defending_overall__goals_in_box_pct",
        "defending_misc__touches_in_box","defending_misc__hit_post","defending_misc__offsides","defending_misc__headers__total","defending_misc__headers__goals",
        "defending_misc__fast_breaks__total","defending_misc__fast_breaks__goals", "performance_cs","performance_cs_pct", "performance_int","performance_tklw","performance_recov",
        "tackles_tkl","blocks_blocks","blocks_clr", "defending_defensive_actions__tackles","defending_defensive_actions__interceptions", "defending_defensive_actions__recoveries",
        "defending_defensive_actions__blocks","defending_defensive_actions__clearances","defending_defensive_actions__tackles_Padj","defending_defensive_actions__interceptions_Padj",
        "defending_defensive_actions__blocks_Padj","defending_defensive_actions__clearances_Padj"
    ],
    "Set-Pieces (Defensive)": [
        "defending_set_pieces__goals","defending_set_pieces__shots","defending_set_pieces__xg","defending_set_pieces__goal_pct","defending_set_pieces__shot_pct",
        "defending_set_pieces__xg_pct", "defending_misc__free_kicks__total","defending_misc__free_kicks__goals",
    ],
    "Penalties": [
        "attacking_misc__penalties__total","attacking_misc__penalties__goals", "misc.__pens_conceded", "performance_pk","performance_pkatt",
    ],
    "Foul": [
        "misc.__fouled","misc.__yellows","misc.__reds","misc.__fouls","misc.__opp_yellows","misc.__opp_reds", "performance_crdy","performance_crdr","performance_fls","performance_fld", 
    ],
    "Duel": [
        "defending_defensive_actions__ground_duels_won","defending_defensive_actions__aerial_duels_won", "aerial_won","aerial_lost","Per_90_min_aerial_won",
    ],
    "Take-ons": [
        "takeons_att", "takeons_succ", "takeons_succ_pct", "Per_90_min_takeons_att","Per_90_min_takeons_succ",
    ],
    "Results": [
        "performance_w", "performance_d","performance_l", "team_success_ppm", "team_success_plus_minus","team_success_plus_minus_per90",
    ],
    "Miscellaneous": [
        "misc.__subs_used","misc.__subs_goals","subs_min_per_sub", "misc.__errors_lead_to_shot","misc.__errors_lead_to_goal", "blocks_err", 
    ],
}

# Glossaire multilingue
glossary = {
    "fr": {
        # JEU AVEC BALLON
        "attacking_overall__goals": "Nombre de buts inscrits par 90 minutes","attacking_overall__xg": "Nombre de buts attendus par 90 minutes",
        "attacking_overall__goals_vs_xg": "Différence entre les buts inscrits et les buts attendus par 90 minutes","attacking_overall__shots": "Nombre de tirs réalisés par 90 minutes",
        "attacking_overall__sot": "Nombre de tirs cadrés réalisés par 90 minutes","attacking_overall__conv_pct": "Pourcentage de buts inscrits par tir réalisé",
        "attacking_overall__xg_per_shot": "Nombre de buts attendus par tir réalisé","attacking_misc__touches_in_box": "Nombre de touches dans la surface adverse effectués par 90 minutes",
        "attacking_misc__hit_post": "Nombre de poteaux/transversales effectués par 90 minutes","attacking_misc__offsides": "Nombre de hors-jeu commis par 90 minutes",
        "attacking_misc__headers__total": "Nombre de tirs de tête réalisés par 90 minutes","attacking_misc__headers__goals": "Nombre de buts de tête réalisés par 90 minutes",
        "performance_gls": "Nombre de buts inscrits","performance_g_minus_pk": "Nombre de buts inscrits moins les penalties marqués",
        "expected_xg": "Nombre de buts attendus","expected_npxg": "Nombre de buts attendus (hors penalties)",
        "per90_g_minus_pk": "Nombre de buts inscrits moins les penalties marqués par 90 minutes","per90_npxg": "Nombre de buts attendus réalisés par 90 minutes",
        "shooting_sh": "Nombre de tirs réalisés","shooting_sot": "Nombre de tirs cadrés réalisés","shooting_dist": "Distance moyenne par tir réalisé",

        # COUP DE PIED ARRÊTÉS (OFFENSIF)
        "attacking_set_pieces__goals": "Nombre de buts inscrits sur coup de pied arrêté par 90 minutes","attacking_set_pieces__shots": "Nombre de tirs sur coup de pied arrêté par 90 minutes",
        "attacking_set_pieces__xg": "Nombre de buts attendus sur coup de pied arrêté par 90 minutes","attacking_set_pieces__goal_pct": "Pourcentage de buts inscrits sur coup de pied arrêté",
        "attacking_set_pieces__shot_pct": "Pourcentage de tirs sur coup de pied arrêté","attacking_set_pieces__xg_pct": "Pourcentage de buts attendus sur coup de pied arrêté",
        "attacking_misc__free_kicks__total": "Nombre de coups francs directs tentés par 90 minutes","attacking_misc__free_kicks__goals": "Nombre de buts sur coups francs directs par 90 minutes",

        # STYLE DE JEU
        "attacking_misc__fast_breaks__total": "Nombre de contre-attaques réalisées par 90 minutes","attacking_misc__fast_breaks__goals": "Nombre de buts sur contre-attaques par 90 minutes",
        "sequences__ten_plus_passes": "Nombre de séquences de plus de 10 passes par 90 minutes","sequences__direct_speed": "Vitesse moyenne de progression des séquences",
        "sequences__passes_per_seq": "Nombre de passes par séquence","sequences__sequence_time": "Temps moyen d'une séquence de jeu",
        "sequences__build_ups__total": "Nombre d'attaques placées par 90 minutes","sequences__build_ups__goals": "Nombre de buts sur attaques placées par 90 minutes",
        "sequences__direct_attacks__total": "Nombre d'actions en jeu direct par 90 minutes","sequences__direct_attacks__goals": "Nombre de buts sur actions en jeu direct par 90 minutes",
        "direct_attack_prop": "Proportion d'actions en jeu direct","build_ups_prop": "Proportion d'attaques placées","fast_break_prop": "Proportion de contre-attaques",

        # JEU DE PASSE
        "passing__avg_poss": "Possession moyenne","passing__all_passes__pct": "Pourcentage de passes réussies",
        "passing__final_third_passes__successful": "Nombre de passes réussies dans le dernier tiers par 90 minutes",
        "passing__final_third_passes__pct": "Pourcentage de passes réussies dans le dernier tiers","passing__pass_direction__fwd": "Pourcentage de passes vers l'avant",
        "passing__pass_direction__bwd": "Pourcentage de passes vers l'arrière","passing__pass_direction__left": "Pourcentage de passes vers la gauche",
        "passing__pass_direction__right": "Pourcentage de passes vers la droite","passing__crosses__total": "Nombre de centres réalisés par 90 minutes",
        "passing__crosses__successful": "Nombre de centres réussis par 90 minutes","passing__crosses__pct": "Pourcentage de centres réussis",
        "passing__through_balls": "Nombre de passes en profondeur par 90 minutes","progression_prgc": "Nombre de portées de balle progressives",
        "progression_prgp": "Nombre de passes progressives","carries_total": "Nombre de portées de balle",
        "carries_final_third": "Nombre de portées de balle dans le dernier tiers adverse","carries_mis": "Nombre de contrôles manqués",
        "carries_dis": "Nombre de pertes de balle sur portées","receiving_prgr": "Nombre de réceptions progressives","performance_crs": "Nombre de centres réalisés",
        "passing_cmp": "Nombre de passes réussies","short_cmp": "Nombre de passes courtes réussies",
        "short_cmp_pct": "Pourcentage de passes courtes réussies","medium_cmp": "Nombre de passes moyennes réussies","medium_cmp_pct": "Pourcentage de passes moyennes réussies",
        "long_cmp": "Nombre de passes longues réussies","long_cmp_pct": "Pourcentage de passes longues réussies","passing_ppa": "Nombre de passes réussies dans la surface",
        "passing_crspa": "Nombre de centres dans la surface réalisés","passing_prgp": "Nombre de passes progressives réalisées","Long_Att__pass_prop": "Pourcentage de passes longues tentées",
        "Per_90_min_passing_crspa": "Nombre de centres dans la surface réalisés par 90 minutes","Per_90_min_passing_prgp": "Nombre de passes progressives par 90 minutes",
        "Per_90_min_progression_prgc": "Nombre de portées de balle progressives par 90 minutes","Per_90_min_carries_total": "Nombre de portées de balle par 90 minutes",
        "Per_90_min_carries_final_third": "Nombre de portées de balle dans le dernier tiers par 90 minutes","Per_90_min_receiving_prgr": "Nombre de réceptions progressives par 90 minutes",
        "Per_90_min_passing_cmp": "Nombre de passes réussies par 90 minutes","Per_90_min_carries_mis": "Nombre de contrôles manqués par 90 minutes",
        "Per_90_min_carries_dis": "Nombre de pertes de balle sur portées par 90 minutes",

        # PRESSING
        "pressing__pressed_seqs": "Nombre de séquences de pressing par 90 minutes", "pressing__pressed_seqs_Padj": "Nombre de séquences de pressing par 90 minutes ajustées à la possession",
        "pressing__ppda": "Passes permises par action défensive dans les deux tiers défensifs","pressing__start_distance_m": "Distance moyenne de début du pressing",
        "pressing__high_turnovers__shot_ending": "Pressings hauts menant à un tir par 90 minutes","pressing__high_turnovers__goal_ending": "Pressings hauts menant à un but par 90 minutes",
        "pressing__high_turnovers__pct_end_in_shot": "Pourcentage de pressings hauts débouchant sur un tir",

        # JEU SANS BALLON
        "defending_overall__goals": "Nombre de buts encaissés par 90 minutes","defending_overall__xg": "Nombre de buts attendus concédés par 90 minutes",
        "defending_overall__goals_vs_xg": "Différence entre buts encaissés et xG concédés par 90 minutes","defending_overall__shots": "Nombre de tirs concédés par 90 minutes",
        "defending_overall__sot": "Nombre de tirs cadrés concédés par 90 minutes","defending_overall__conv_pct": "Pourcentage de tirs concédés se terminant en but",
        "defending_overall__xg_per_shot": "Buts attendus concédés par tir","defending_overall__shots_in_box_pct": "Pourcentage de tirs concédés dans la surface",
        "defending_overall__goals_in_box_pct": "Pourcentage de buts concédés dans la surface","defending_misc__touches_in_box": "Touches concédées dans la surface par 90 minutes",
        "defending_misc__hit_post": "Poteaux/transversales concédés par 90 minutes","defending_misc__offsides": "Hors-jeu sifflés contre l'adversaire par 90 minutes",
        "defending_misc__headers__total": "Tirs de tête concédés par 90 minutes","defending_misc__headers__goals": "Buts de tête concédés par 90 minutes",
        "defending_misc__fast_breaks__total": "Contre-attaques subies par 90 minutes","defending_misc__fast_breaks__goals": "Buts encaissés sur contre-attaques par 90 minutes",
        "performance_cs": "Matchs sans encaisser de buts","performance_cs_pct": "Pourcentage de clean sheets","performance_int": "Interceptions","performance_tklw": "Tacles gagnés",
        "performance_recov": "Récupérations de balle","tackles_tkl": "Tacles effectués","blocks_blocks": "Nombre de blocs","blocks_clr": "Dégagements",
        "defending_defensive_actions__tackles": "Tacles par 90 minutes","defending_defensive_actions__interceptions": "Interceptions par 90 minutes",
        "defending_defensive_actions__recoveries": "Récupérations par 90 minutes","defending_defensive_actions__blocks": "Blocs par 90 minutes",
        "defending_defensive_actions__clearances": "Dégagements par 90 minutes", "defending_defensive_actions__tackles_Padj": "Tacles par 90 minutes ajustées à la possession",
        "defending_defensive_actions__interceptions_Padj": "Interceptions par 90 minutes ajustées à la possession",
        "defending_defensive_actions__blocks_Padj": "Blocs par 90 minutes ajustées à la possession",
        "defending_defensive_actions__clearances_Padj": "Dégagements par 90 minutes ajustées à la possession",

        # COUP DE PIED ARRÊTÉS (DEFENSIF)
        "defending_set_pieces__goals": "Buts concédés sur coup de pied arrêté par 90 minutes","defending_set_pieces__shots": "Tirs concédés sur coup de pied arrêté par 90 minutes",
        "defending_set_pieces__xg": "xG concédés sur coup de pied arrêté par 90 minutes","defending_set_pieces__goal_pct": "Pourcentage de buts concédés sur coup de pied arrêté",
        "defending_set_pieces__shot_pct": "Pourcentage de tirs concédés sur coup de pied arrêté","defending_set_pieces__xg_pct": "Pourcentage de xG concédés sur coup de pied arrêté",
        "defending_misc__free_kicks__total": "Coups francs directs concédés par 90 minutes","defending_misc__free_kicks__goals": "Buts concédés sur coups francs directs par 90 minutes",

        # PENALTIES
        "attacking_misc__penalties__total": "Penalties obtenus par 90 minutes","attacking_misc__penalties__goals": "Penalties marqués par 90 minutes",
        "misc.__pens_conceded": "Penalties concédés par 90 minutes","performance_pk": "Penalties marqués","performance_pkatt": "Penalties obtenus",

        # FAUTES
        "misc.__fouled": "Fautes subies par 90 minutes","misc.__yellows": "Cartons jaunes reçus par 90 minutes","misc.__reds": "Cartons rouges reçus par 90 minutes",
        "misc.__fouls": "Fautes commises par 90 minutes","misc.__opp_yellows": "Cartons jaunes reçus par l'adversaire par 90 minutes",
        "misc.__opp_reds": "Cartons rouges reçus par l'adversaire par 90 minutes","performance_crdy": "Cartons jaunes","performance_crdr": "Cartons rouges",
        "performance_fls": "Fautes commises","performance_fld": "Fautes subies",

        # DUELS
        "defending_defensive_actions__ground_duels_won": "Pourcentage de duels au sol gagnés","defending_defensive_actions__aerial_duels_won": "Pourcentage de duels aériens gagnés",
        "aerial_won": "Duels aériens gagnés","aerial_lost": "Duels aériens perdus","Per_90_min_aerial_won": "Duels aériens gagnés par 90 minutes",

        # DRIBBLES
        "takeons_att": "Dribbles tentés","takeons_succ": "Dribbles réussis","takeons_succ_pct": "Pourcentage de dribbles réussis",
        "Per_90_min_takeons_att": "Dribbles tentés par 90 minutes","Per_90_min_takeons_succ": "Dribbles réussis par 90 minutes",

        # RÉSULTATS
        "performance_w": "Victoires","performance_d": "Nuls","performance_l": "Défaites","team_success_ppm": "Points par match",
        "team_success_plus_minus": "Différentiel buts pour/contre","team_success_plus_minus_per90": "Différentiel buts pour/contre par 90 minutes",

        # AUTRES
        "misc.__subs_used": "Remplaçants utilisés par 90 minutes","misc.__subs_goals": "Buts marqués par des remplaçants par 90 minutes",
        "subs_min_per_sub": "Temps de jeu moyen des remplaçants","misc.__errors_lead_to_shot": "Erreurs menant à un tir adverse par 90 minutes",
        "misc.__errors_lead_to_goal": "Erreurs menant à un but adverse par 90 minutes","blocks_err": "Erreurs défensives"
    },

    "es": {
        # CON BALÓN
        "attacking_overall__goals": "Goles por 90 minutos","attacking_overall__xg": "Goles esperados por 90 minutos",
        "attacking_overall__goals_vs_xg": "Diferencia entre goles y xG por 90 minutos","attacking_overall__shots": "Tiros por 90 minutos",
        "attacking_overall__sot": "Tiros a puerta por 90 minutos","attacking_overall__conv_pct": "Porcentaje de tiros que terminan en gol",
        "attacking_overall__xg_per_shot": "xG por tiro","attacking_misc__touches_in_box": "Toques en el área rival por 90 minutos",
        "attacking_misc__hit_post": "Tiros al poste/travesaño por 90 minutos","attacking_misc__offsides": "Fueras de juego cometidos por 90 minutos",
        "attacking_misc__headers__total": "Remates de cabeza por 90 minutos","attacking_misc__headers__goals": "Goles de cabeza por 90 minutos",
        "performance_gls": "Goles","performance_g_minus_pk": "Goles sin penaltis convertidos","expected_xg": "Goles esperados",
        "expected_npxg": "Goles esperados sin penaltis","per90_g_minus_pk": "Goles sin penaltis por 90 minutos","per90_npxg": "xG sin penaltis por 90 minutos",
        "shooting_sh": "Tiros","shooting_sot": "Tiros a puerta","shooting_dist": "Distancia media por tiro",

        # A BALÓN PARADO (OFENSIVO)
        "attacking_set_pieces__goals": "Goles a balón parado por 90 minutos","attacking_set_pieces__shots": "Tiros a balón parado por 90 minutos",
        "attacking_set_pieces__xg": "xG a balón parado por 90 minutos","attacking_set_pieces__goal_pct": "Porcentaje de goles a balón parado",
        "attacking_set_pieces__shot_pct": "Porcentaje de tiros a balón parado","attacking_set_pieces__xg_pct": "Porcentaje de xG a balón parado",
        "attacking_misc__free_kicks__total": "Faltas directas intentadas por 90 minutos","attacking_misc__free_kicks__goals": "Goles de falta directa por 90 minutos",

        # ESTILO DE JUEGO
        "attacking_misc__fast_breaks__total": "Contraataques por 90 minutos","attacking_misc__fast_breaks__goals": "Goles en contraataques por 90 minutos",
        "sequences__ten_plus_passes": "Secuencias de 10+ pases por 90 minutos","sequences__direct_speed": "Velocidad media de progresión",
        "sequences__passes_per_seq": "Pases por secuencia","sequences__sequence_time": "Duración media de una secuencia",
        "sequences__build_ups__total": "Ataques elaborados por 90 minutos","sequences__build_ups__goals": "Goles en ataques elaborados por 90 minutos",
        "sequences__direct_attacks__total": "Ataques directos por 90 minutos","sequences__direct_attacks__goals": "Goles en ataques directos por 90 minutos",
        "direct_attack_prop": "Proporción de ataque directo","build_ups_prop": "Proporción de ataque elaborado","fast_break_prop": "Proporción de contraataque",

        # PASE
        "passing__avg_poss": "Posesión media","passing__all_passes__pct": "Porcentaje de pases completados",
        "passing__final_third_passes__successful": "Pases completados en el último tercio por 90 minutos","passing__final_third_passes__pct": "Porcentaje de acierto en el último tercio",
        "passing__pass_direction__fwd": "Porcentaje de pases hacia adelante","passing__pass_direction__bwd": "Porcentaje de pases hacia atrás",
        "passing__pass_direction__left": "Porcentaje de pases a la izquierda","passing__pass_direction__right": "Porcentaje de pases a la derecha",
        "passing__crosses__total": "Centros por 90 minutos","passing__crosses__successful": "Centros completados por 90 minutos",
        "passing__crosses__pct": "Porcentaje de centros completados","passing__through_balls": "Pases al hueco por 90 minutos",
        "progression_prgc": "Conducciones progresivas","progression_prgp": "Pases progresivos","carries_total": "Conducciones",
        "carries_final_third": "Conducciones en el último tercio","carries_mis": "Controles fallidos","carries_dis": "Pérdidas en conducción",
        "receiving_prgr": "Recepciones progresivas","performance_crs": "Centros","passing_cmp": "Pases completados","short_cmp": "Pases cortos completados",
        "short_cmp_pct": "Porcentaje de pases cortos completados","medium_cmp": "Pases medios completados","medium_cmp_pct": "Porcentaje de pases medios completados",
        "long_cmp": "Pases largos completados","long_cmp_pct": "Porcentaje de pases largos completados","passing_ppa": "Pases completados al área","passing_crspa": "Centros al área",
        "passing_prgp": "Pases progresivos","Long_Att__pass_prop": "Porcentaje de pases largos intentados","Per_90_min_passing_crspa": "Centros al área por 90 minutos",
        "Per_90_min_passing_prgp": "Pases progresivos por 90 minutos","Per_90_min_progression_prgc": "Conducciones progresivas por 90 minutos",
        "Per_90_min_carries_total": "Conducciones por 90 minutos","Per_90_min_carries_final_third": "Conducciones en el último tercio por 90 minutos",
        "Per_90_min_receiving_prgr": "Recepciones progresivas por 90 minutos","Per_90_min_passing_cmp": "Pases completados por 90 minutos",
        "Per_90_min_carries_mis": "Controles fallidos por 90 minutos","Per_90_min_carries_dis": "Pérdidas en conducción por 90 minutos",

        # PRESIÓN
        "pressing__pressed_seqs": "Secuencias de presión por 90 minutos", "pressing__pressed_seqs_Padj": "Número de secuencias de presión por 90 minutos ajustadas a la posesión",
        "pressing__ppda": "Pases permitidos por acción defensiva en dos tercios defensivos","pressing__start_distance_m": "Distancia media de inicio de la presión",
        "pressing__high_turnovers__shot_ending": "Recuperaciones altas que acaban en tiro por 90 minutos",
        "pressing__high_turnovers__goal_ending": "Recuperaciones altas que acaban en gol por 90 minutos",
        "pressing__high_turnovers__pct_end_in_shot": "Porcentaje de presiones altas que acaban en tiro",

        # SIN BALÓN
        "defending_overall__goals": "Goles encajados por 90 minutos","defending_overall__xg": "xG concedidos por 90 minutos",
        "defending_overall__goals_vs_xg": "Diferencia entre goles encajados y xG concedidos por 90 minutos","defending_overall__shots": "Tiros concedidos por 90 minutos",
        "defending_overall__sot": "Tiros a puerta concedidos por 90 minutos","defending_overall__conv_pct": "Porcentaje de tiros concedidos que acaban en gol",
        "defending_overall__xg_per_shot": "xG concedidos por tiro","defending_overall__shots_in_box_pct": "Porcentaje de tiros concedidos en el área",
        "defending_overall__goals_in_box_pct": "Porcentaje de goles encajados en el área","defending_misc__touches_in_box": "Toques concedidos en el área por 90 minutos",
        "defending_misc__hit_post": "Postes/travesaños concedidos por 90 minutos","defending_misc__offsides": "Fueras de juego del rival por 90 minutos",
        "defending_misc__headers__total": "Remates de cabeza concedidos por 90 minutos","defending_misc__headers__goals": "Goles de cabeza encajados por 90 minutos",
        "defending_misc__fast_breaks__total": "Contraataques sufridos por 90 minutos","defending_misc__fast_breaks__goals": "Goles encajados en contraataques por 90 minutos",
        "performance_cs": "Partidos con portería a cero","performance_cs_pct": "Porcentaje de porterías a cero","performance_int": "Intercepciones","performance_tklw": "Entradas ganadas",
        "performance_recov": "Recuperaciones","tackles_tkl": "Entradas realizadas","blocks_blocks": "Bloqueos","blocks_clr": "Despejes",
        "defending_defensive_actions__tackles": "Entradas por 90 minutos","defending_defensive_actions__interceptions": "Intercepciones por 90 minutos",
        "defending_defensive_actions__recoveries": "Recuperaciones por 90 minutos","defending_defensive_actions__blocks": "Bloqueos por 90 minutos",
        "defending_defensive_actions__clearances": "Despejes por 90 minutos", "defending_defensive_actions__tackles_Padj": "Entradas por 90 minutos ajustadas a la posesión",
        "defending_defensive_actions__interceptions_Padj": "Intercepciones por 90 minutos ajustadas a la posesión",
        "defending_defensive_actions__blocks_Padj": "Bloqueos por cada 90 minutos ajustados a la posesión",
        "defending_defensive_actions__clearances_Padj": "Despejes por cada 90 minutos ajustados a la posesión",

        # A BALÓN PARADO (DEFENSIVO)
        "defending_set_pieces__goals": "Goles encajados a balón parado por 90 minutos","defending_set_pieces__shots": "Tiros concedidos a balón parado por 90 minutos",
        "defending_set_pieces__xg": "xG concedidos a balón parado por 90 minutos","defending_set_pieces__goal_pct": "Porcentaje de goles encajados a balón parado",
        "defending_set_pieces__shot_pct": "Porcentaje de tiros concedidos a balón parado","defending_set_pieces__xg_pct": "Porcentaje de xG concedidos a balón parado",
        "defending_misc__free_kicks__total": "Faltas directas concedidas por 90 minutos","defending_misc__free_kicks__goals": "Goles encajados de falta directa por 90 minutos",

        # PENALTIS
        "attacking_misc__penalties__total": "Penaltis a favor por 90 minutos","attacking_misc__penalties__goals": "Penaltis convertidos por 90 minutos",
        "misc.__pens_conceded": "Penaltis en contra por 90 minutos","performance_pk": "Penaltis convertidos","performance_pkatt": "Penaltis a favor",

        # FALTAS
        "misc.__fouled": "Faltas recibidas por 90 minutos","misc.__yellows": "Tarjetas amarillas recibidas por 90 minutos","misc.__reds": "Tarjetas rojas recibidas por 90 minutos",
        "misc.__fouls": "Faltas cometidas por 90 minutos","misc.__opp_yellows": "Amarillas del rival por 90 minutos","misc.__opp_reds": "Rojas del rival por 90 minutos",
        "performance_crdy": "Tarjetas amarillas","performance_crdr": "Tarjetas rojas","performance_fls": "Faltas cometidas","performance_fld": "Faltas recibidas",

        # DUELOS
        "defending_defensive_actions__ground_duels_won": "Porcentaje de duelos terrestres ganados","defending_defensive_actions__aerial_duels_won": "Porcentaje de duelos aéreos ganados",
        "aerial_won": "Duelos aéreos ganados","aerial_lost": "Duelos aéreos perdidos","Per_90_min_aerial_won": "Duelos aéreos ganados por 90 minutos",

        # REGATES
        "takeons_att": "Regates intentados","takeons_succ": "Regates completados","takeons_succ_pct": "Porcentaje de regates completados",
        "Per_90_min_takeons_att": "Regates intentados por 90 minutos","Per_90_min_takeons_succ": "Regates completados por 90 minutos",

        # RESULTADOS
        "performance_w": "Victorias","performance_d": "Empates","performance_l": "Derrotas","team_success_ppm": "Puntos por partido",
        "team_success_plus_minus": "Diferencial de goles a favor/en contra","team_success_plus_minus_per90": "Diferencial de goles por 90 minutos",

        # OTROS
        "misc.__subs_used": "Suplentes utilizados por 90 minutos","misc.__subs_goals": "Goles de suplentes por 90 minutos","subs_min_per_sub": "Tiempo medio de juego de suplentes",
        "misc.__errors_lead_to_shot": "Errores que acaban en tiro rival por 90 minutos","misc.__errors_lead_to_goal": "Errores que acaban en gol rival por 90 minutos",
        "blocks_err": "Errores defensivos"
    },

    "eng": {
        # ON-BALL
        "attacking_overall__goals": "Goals per 90 minutes","attacking_overall__xg": "Expected goals per 90 minutes",
        "attacking_overall__goals_vs_xg": "Difference between goals and xG per 90 minutes","attacking_overall__shots": "Shots per 90 minutes",
        "attacking_overall__sot": "Shots on target per 90 minutes","attacking_overall__conv_pct": "Share of shots that become goals",
        "attacking_overall__xg_per_shot": "xG per shot","attacking_misc__touches_in_box": "Touches in opponent box per 90 minutes",
        "attacking_misc__hit_post": "Shots off post/crossbar per 90 minutes","attacking_misc__offsides": "Offsides committed per 90 minutes",
        "attacking_misc__headers__total": "Header shots per 90 minutes","attacking_misc__headers__goals": "Headed goals per 90 minutes","performance_gls": "Goals",
        "performance_g_minus_pk": "Goals excluding penalties scored","expected_xg": "Expected goals","expected_npxg": "Non-penalty expected goals",
        "per90_g_minus_pk": "Goals excluding penalties per 90 minutes","per90_npxg": "Non-penalty xG per 90 minutes","shooting_sh": "Shots",
        "shooting_sot": "Shots on target","shooting_dist": "Average shot distance",

        # SET-PIECES (OFFENSE)
        "attacking_set_pieces__goals": "Set-piece goals per 90 minutes","attacking_set_pieces__shots": "Set-piece shots per 90 minutes",
        "attacking_set_pieces__xg": "Set-piece xG per 90 minutes","attacking_set_pieces__goal_pct": "Share of goals from set-pieces",
        "attacking_set_pieces__shot_pct": "Share of shots from set-pieces","attacking_set_pieces__xg_pct": "Share of xG from set-pieces",
        "attacking_misc__free_kicks__total": "Direct free kicks attempted per 90 minutes","attacking_misc__free_kicks__goals": "Direct free kick goals per 90 minutes",

        # STYLE OF PLAY
        "attacking_misc__fast_breaks__total": "Counter-attacks per 90 minutes","attacking_misc__fast_breaks__goals": "Counter-attack goals per 90 minutes",
        "sequences__ten_plus_passes": "10+ pass sequences per 90 minutes","sequences__direct_speed": "Average direct speed of possession",
        "sequences__passes_per_seq": "Passes per sequence","sequences__sequence_time": "Average sequence duration",
        "sequences__build_ups__total": "Possession attacks per 90 minutes","sequences__build_ups__goals": "Goals from possession attacks per 90 minutes",
        "sequences__direct_attacks__total": "Direct attacks per 90 minutes","sequences__direct_attacks__goals": "Goals from direct attacks per 90 minutes",
        "direct_attack_prop": "Share of direct attacks","build_ups_prop": "Share of possession attacks","fast_break_prop": "Share of counter-attacks",

        # PASSING
        "passing__avg_poss": "Average possession","passing__all_passes__pct": "Pass completion percentage",
        "passing__final_third_passes__successful": "Completed passes in final third per 90 minutes","passing__final_third_passes__pct": "Completion rate in final third",
        "passing__pass_direction__fwd": "Share of forward passes","passing__pass_direction__bwd": "Share of backward passes","passing__pass_direction__left": "Share of leftward passes",
        "passing__pass_direction__right": "Share of rightward passes","passing__crosses__total": "Crosses per 90 minutes","passing__crosses__successful": "Completed crosses per 90 minutes",
        "passing__crosses__pct": "Cross completion percentage","passing__through_balls": "Through balls per 90 minutes","progression_prgc": "Progressive carries",
        "progression_prgp": "Progressive passes","carries_total": "Carries","carries_final_third": "Carries in final third","carries_mis": "Miscontrols",
        "carries_dis": "Dispossessions on carries","receiving_prgr": "Progressive receptions","performance_crs": "Crosses","passing_cmp": "Completed passes",
        "short_cmp": "Completed short passes","short_cmp_pct": "Short pass completion percentage","medium_cmp": "Completed medium passes",
        "medium_cmp_pct": "Medium pass completion percentage","long_cmp": "Completed long passes","long_cmp_pct": "Long pass completion percentage",
        "passing_ppa": "Completed passes into the penalty area","passing_crspa": "Crosses into the penalty area","passing_prgp": "Progressive passes",
        "Long_Att__pass_prop": "Share of long passes attempted","Per_90_min_passing_crspa": "Crosses into the penalty area per 90 minutes",
        "Per_90_min_passing_prgp": "Progressive passes per 90 minutes","Per_90_min_progression_prgc": "Progressive carries per 90 minutes",
        "Per_90_min_carries_total": "Carries per 90 minutes","Per_90_min_carries_final_third": "Carries in final third per 90 minutes",
        "Per_90_min_receiving_prgr": "Progressive receptions per 90 minutes","Per_90_min_passing_cmp": "Completed passes per 90 minutes",
        "Per_90_min_carries_mis": "Miscontrols per 90 minutes","Per_90_min_carries_dis": "Dispossessions on carries per 90 minutes",

        # PRESSING
        "pressing__pressed_seqs": "Pressing sequences per 90 minutes","pressing__pressed_seqs_Padj": "Number of pressing sequences per 90 minutes adjusted for possession",
        "pressing__ppda": "Passes allowed per defensive action in defensive two-thirds","pressing__start_distance_m": "Average pressing start distance",
        "pressing__high_turnovers__shot_ending": "High turnovers leading to a shot per 90 minutes",
        "pressing__high_turnovers__goal_ending": "High turnovers leading to a goal per 90 minutes","pressing__high_turnovers__pct_end_in_shot": "Share of high turnovers ending in a shot",

        # OFF-BALL
        "defending_overall__goals": "Goals conceded per 90 minutes","defending_overall__xg": "Expected goals conceded per 90 minutes",
        "defending_overall__goals_vs_xg": "Difference between goals conceded and xG conceded per 90 minutes","defending_overall__shots": "Shots conceded per 90 minutes",
        "defending_overall__sot": "Shots on target conceded per 90 minutes","defending_overall__conv_pct": "Share of shots conceded that become goals",
        "defending_overall__xg_per_shot": "xG conceded per shot","defending_overall__shots_in_box_pct": "Share of shots conceded in the box",
        "defending_overall__goals_in_box_pct": "Share of goals conceded in the box","defending_misc__touches_in_box": "Touches conceded in the box per 90 minutes",
        "defending_misc__hit_post": "Posts/crossbars conceded per 90 minutes","defending_misc__offsides": "Offsides by opponent per 90 minutes",
        "defending_misc__headers__total": "Header shots conceded per 90 minutes","defending_misc__headers__goals": "Headed goals conceded per 90 minutes",
        "defending_misc__fast_breaks__total": "Counter-attacks faced per 90 minutes","defending_misc__fast_breaks__goals": "Counter-attack goals conceded per 90 minutes",
        "performance_cs": "Clean sheets","performance_cs_pct": "Clean sheet percentage","performance_int": "Interceptions","performance_tklw": "Tackles won",
        "performance_recov": "Ball recoveries","tackles_tkl": "Tackles made","blocks_blocks": "Blocks","blocks_clr": "Clearances",
        "defending_defensive_actions__tackles": "Tackles per 90 minutes","defending_defensive_actions__interceptions": "Interceptions per 90 minutes",
        "defending_defensive_actions__recoveries": "Recoveries per 90 minutes","defending_defensive_actions__blocks": "Blocks per 90 minutes",
        "defending_defensive_actions__clearances": "Clearances per 90 minute", "defending_defensive_actions__tackles_Padj": "Tackles per 90 minutes adjusted for possession",
        "defending_defensive_actions__interceptions_Padj": "Interceptions per 90 minutes adjusted for possession",
        "defending_defensive_actions__blocks_Padj": "Blocks per 90 minutes adjusted for possession",
        "defending_defensive_actions__clearances_Padj": "Clearances per 90 minutes adjusted for possession",

        # SET-PIECES (DEFENSE)
        "defending_set_pieces__goals": "Set-piece goals conceded per 90 minutes","defending_set_pieces__shots": "Set-piece shots conceded per 90 minutes",
        "defending_set_pieces__xg": "Set-piece xG conceded per 90 minutes","defending_set_pieces__goal_pct": "Share of goals conceded from set-pieces",
        "defending_set_pieces__shot_pct": "Share of shots conceded from set-pieces","defending_set_pieces__xg_pct": "Share of xG conceded from set-pieces",
        "defending_misc__free_kicks__total": "Direct free kicks conceded per 90 minutes","defending_misc__free_kicks__goals": "Direct free kick goals conceded per 90 minutes",

        # PENALTIES
        "attacking_misc__penalties__total": "Penalties won per 90 minutes","attacking_misc__penalties__goals": "Penalties scored per 90 minutes",
        "misc.__pens_conceded": "Penalties conceded per 90 minutes","performance_pk": "Penalties scored","performance_pkatt": "Penalties won",

        # FOULS
        "misc.__fouled": "Fouls suffered per 90 minutes","misc.__yellows": "Yellow cards received per 90 minutes","misc.__reds": "Red cards received per 90 minutes",
        "misc.__fouls": "Fouls committed per 90 minutes","misc.__opp_yellows": "Opponent yellow cards per 90 minutes","misc.__opp_reds": "Opponent red cards per 90 minutes",
        "performance_crdy": "Yellow cards","performance_crdr": "Red cards","performance_fls": "Fouls committed","performance_fld": "Fouls suffered",

        # DUELS
        "defending_defensive_actions__ground_duels_won": "Ground duels won percentage","defending_defensive_actions__aerial_duels_won": "Aerial duels won percentage",
        "aerial_won": "Aerial duels won","aerial_lost": "Aerial duels lost","Per_90_min_aerial_won": "Aerial duels won per 90 minutes",

        # DRIBBLES
        "takeons_att": "Dribbles attempted","takeons_succ": "Dribbles completed","takeons_succ_pct": "Dribble success rate",
        "Per_90_min_takeons_att": "Dribbles attempted per 90 minutes","Per_90_min_takeons_succ": "Dribbles completed per 90 minutes",

        # RESULTS
        "performance_w": "Wins","performance_d": "Draws","performance_l": "Losses","team_success_ppm": "Points per match",
        "team_success_plus_minus": "Goal difference for/against","team_success_plus_minus_per90": "Goal difference per 90 minutes",

        # OTHER
        "misc.__subs_used": "Substitutions used per 90 minutes","misc.__subs_goals": "Goals by substitutes per 90 minutes","subs_min_per_sub": "Average minutes for substitutes",
        "misc.__errors_lead_to_shot": "Errors leading to an opponent shot per 90 minutes","misc.__errors_lead_to_goal": "Errors leading to an opponent goal per 90 minutes",
        "blocks_err": "Defensive errors"
    }
}

stat_display_names = {
    # JEU AVEC BALLON
    "attacking_overall__goals": "goals_per90","attacking_overall__xg": "xG_per90","attacking_overall__goals_vs_xg": "goals-xG_per90","attacking_overall__shots": "shots_per90",
    "attacking_overall__sot": "shots_on_target_per90","attacking_overall__conv_pct": "goal/shot","attacking_overall__xg_per_shot": "xG_per_shot",
    "attacking_misc__touches_in_box": "touches_in_box_per90","attacking_misc__hit_post": "hit_post_per90","attacking_misc__offsides": "offsides_off_per90",
    "attacking_misc__headers__total": "shots_headers_per90","attacking_misc__headers__goals": "goals_headers_per90","performance_gls": "goals",
    "performance_g_minus_pk": "goals-penalties","expected_xg": "expected_xG","expected_npxg": "expected_npxG","per90_g_minus_pk": "goals-penalties_per90",
    "per90_npxg": "expected_npxG_per90","shooting_sh": "shots","shooting_sot": "shots_on_target","shooting_dist": "distance_per_shot",

    # COUP DE PIED ARRÊTÉS (OFFENSIF)
    "attacking_set_pieces__goals": "goals_set_pieces_per90","attacking_set_pieces__shots": "shots_set_pieces_per90","attacking_set_pieces__xg": "xG_set_pieces_per90",
    "attacking_set_pieces__goal_pct": "goal_pct_set_pieces","attacking_set_pieces__shot_pct": "shot_pct_set_pieces","attacking_set_pieces__xg_pct": "xG_pct_set_pieces",
    "attacking_misc__free_kicks__total": "shots_free_kicks_per90","attacking_misc__free_kicks__goals": "goals_free_kicks_per90",

    # STYLE DE JEU
    "attacking_misc__fast_breaks__total": "fast_breaks_per90","attacking_misc__fast_breaks__goals": "goals_fast_breaks_per90","sequences__ten_plus_passes": "seq_ten_plus_passes_per90",
    "sequences__direct_speed": "direct_speed","sequences__passes_per_seq": "passes_per_seq","sequences__sequence_time": "sequence_time","sequences__build_ups__total": "build_ups_per90",
    "sequences__build_ups__goals": "goals_build_ups_per90","sequences__direct_attacks__total": "direct_attacks_per90","sequences__direct_attacks__goals": "goals_direct_attacks_per90",
    "direct_attack_prop": "direct_attack_pct","build_ups_prop": "build_ups_pct","fast_break_prop": "fast_break_pct",

    # JEU DE PASSE
    "passing__avg_poss": "avg_poss","passing__all_passes__pct": "passes__pct","passing__final_third_passes__successful": "final_third_passes_succ_per90",
    "passing__final_third_passes__pct": "final_third_passes__pct","passing__pass_direction__fwd": "pass_direction_fwd","passing__pass_direction__bwd": "pass_direction_bwd",
    "passing__pass_direction__left": "pass_direction_left","passing__pass_direction__right": "pass_direction_right","passing__crosses__total": "crosses_per90",
    "passing__crosses__successful": "crosses_succ_per90","passing__crosses__pct": "crosses_pct","passing__through_balls": "through_balls_per90","progression_prgc": "prg_carries",
    "progression_prgp": "prg_passes","carries_total": "carries","carries_final_third": "carries_in_1/3","carries_mis": "miscontrols","carries_dis": "dispossessed",
    "receiving_prgr": "prg_received","performance_crs": "crosses","passing_cmp": "passes_succ","short_cmp": "short_passes_succ","short_cmp_pct": "short_passes_pct",
    "medium_cmp": "medium_passes_succ","medium_cmp_pct": "medium_passes_pct","long_cmp": "long_passes_succ","long_cmp_pct": "long_passes_pct","passing_ppa": "passes_in_box",
    "passing_crspa": "crosses_in_box","passing_prgp": "prgP__pass","Long_Att__pass_prop": "long_pass_att_pct","Per_90_min_passing_crspa": "crosses_in_box_per90",
    "Per_90_min_passing_prgp": "prg_passes_per90","Per_90_min_progression_prgc": "prg_carries_per90","Per_90_min_carries_total": "carries_per90",
    "Per_90_min_carries_final_third": "carries_in_1/3_per90","Per_90_min_receiving_prgr": "prg_received_per90","Per_90_min_passing_cmp": "pass_succ_per90",
    "Per_90_min_carries_mis": "miscontrols_per90","Per_90_min_carries_dis": "dispossessed_per90",

    # PRESSING
    "pressing__pressed_seqs": "pressed_seq_per90", "pressing__pressed_seqs_Padj": "pressed_seq_per90_Padj", "pressing__ppda": "ppda",
    "pressing__start_distance_m": "pressing_start_distance_m","pressing__high_turnovers__shot_ending": "pressing_shot_endings",
    "pressing__high_turnovers__goal_ending": "pressing_goal_ending","pressing__high_turnovers__pct_end_in_shot": "pressing_pct_end_in_shot",

    # JEU SANS BALLON
    "defending_overall__goals": "goals_conceded_per90","defending_overall__xg": "xG_conceded_per90","defending_overall__goals_vs_xg": "goals-xG_conceded_per90",
    "defending_overall__shots": "shots_conceded_per90","defending_overall__sot": "shots_on_target_conceded_per90","defending_overall__conv_pct": "goal/shot_conceded",
    "defending_overall__xg_per_shot": "xG_per_shot_conceded","defending_overall__shots_in_box_pct": "shots_in_box_pct_conceded",
    "defending_overall__goals_in_box_pct": "goals_in_box_pct_conceded","defending_misc__touches_in_box": "touches_in_box_conceded_per90",
    "defending_misc__hit_post": "hit_post_conceded_per90","defending_misc__offsides": "offsides_committed_per90","defending_misc__headers__total": "headers_conceded_per90",
    "defending_misc__headers__goals": "goals_headers_conceded_per90","defending_misc__fast_breaks__total": "fast_breaks_conceded_per90",
    "defending_misc__fast_breaks__goals": "goals_fast_breaks_conceded_per90","performance_cs": "clean_sheet","performance_cs_pct": "clean_sheet_pct",
    "performance_int": "interceptions","performance_tklw": "tackles_won","performance_recov": "recoveries","tackles_tkl": "tackles","blocks_blocks": "blocks",
    "blocks_clr": "clearance","defending_defensive_actions__tackles": "tackles_per90","defending_defensive_actions__interceptions": "interceptions_per90",
    "defending_defensive_actions__recoveries": "recoveries_per90","defending_defensive_actions__blocks": "blocks_per90","defending_defensive_actions__clearances": "clearances_per90",
    "defending_defensive_actions__tackles_Padj": "tackles_per90_Padj","defending_defensive_actions__interceptions_Padj": "interceptions_per90_Padj",
    "defending_defensive_actions__blocks_Padj": "blocks_per90_Padj","defending_defensive_actions__clearances_Padj": "clearances_per90_Padj",

    # COUP DE PIED ARRÊTÉS (DEFENSIF)
    "defending_set_pieces__goals": "goals_set_pieces_conceded_per90","defending_set_pieces__shots": "shots_set_pieces_conceded_per90",
    "defending_set_pieces__xg": "xG_set_pieces_conceded_per90","defending_set_pieces__goal_pct": "goals_set_pieces_pct_conceded",
    "defending_set_pieces__shot_pct": "shots_set_pieces_pct_conceded","defending_set_pieces__xg_pct": "xG_set_pieces_pct_conceded",
    "defending_misc__free_kicks__total": "free_kicks_conceded_per90","defending_misc__free_kicks__goals": "goals_free_kicks_conceded_per90",

    # PENALTIES
    "attacking_misc__penalties__total": "penalties_won_per90","attacking_misc__penalties__goals": "goals_penalties_won_per90",
    "misc.__pens_conceded": "penalties_conceded_per90","performance_pk": "penalties_scored","performance_pkatt": "penalties_won",

    # FAUTES
    "misc.__fouled": "fouled_per90","misc.__yellows": "yellows_per90","misc.__reds": "reds_per90","misc.__fouls": "fouls_per90","misc.__opp_yellows": "opp_yellows_per90",
    "misc.__opp_reds": "opp_reds_per90","performance_crdy": "yellows","performance_crdr": "reds","performance_fls": "fouls","performance_fld": "fouled",

    # DUELS
    "defending_defensive_actions__ground_duels_won": "ground_duels_won_pct","defending_defensive_actions__aerial_duels_won": "aerial_duels_won_pct",
    "aerial_won": "aerial_duels_won","aerial_lost": "aerial_duels_lost","Per_90_min_aerial_won": "aerial_duels_won_per90",

    # DRIBBLES
    "takeons_att": "take_ons_att","takeons_succ": "take_ons_succ","takeons_succ_pct": "take_ons_succ_pct",
    "Per_90_min_takeons_att": "take_ons_att_per90","Per_90_min_takeons_succ": "take_ons_succ_per90",

    # RÉSULTATS
    "performance_w": "wins","performance_d": "draws","performance_l": "looses","team_success_ppm": "points_per_match",
    "team_success_plus_minus": "goals_scored-conceded","team_success_plus_minus_per90": "goals_scored-conceded_per90",

    # AUTRES
    "misc.__subs_used": "subs_used_per90","misc.__subs_goals": "subs_goals_per90","subs_min_per_sub": "subs_mean_time",
    "misc.__errors_lead_to_shot": "errors_lead_to_shot_per90","misc.__errors_lead_to_goal": "errors_lead_to_goal_per90","blocks_err": "errors",
}

# Fonctions pour récupérer la définition de chaque statistique / Functions to retrieve the definition of each statistic + Funciones para recuperar la definición de cada estadística
def get_definition(stat_key: str, lang: str = "fr") -> str:
    lang_key = lang.lower() if lang else "fr"
    if lang_key not in ("fr", "eng", "es"):
        lang_key = "fr"

    return (
        glossary.get(lang_key, {}).get(stat_key)
        or glossary.get("fr", {}).get(stat_key)
        or "Définition à ajouter."
    )

# Renommage des noms des statistiques / Renaming statistics names / Renombrar los nombres de las estadísticas
def get_stat_display_name(stat_key: str) -> str:
    return stat_display_names.get(stat_key, stat_key)

# Fonction pour renommer les noms des catégories / Function for renaming category names / Función para renombrar los nombres de las categorías
def format_stat_name(stat):
    if stat.startswith("score_"):
        return stat.replace("score_", "").replace("_", " ").capitalize()
    return stat.capitalize() if stat == "rating" else stat

# Fonction pour effectuer un radar plot avec les données / Radar plot function with data / Función para realizar un radar plot con los datos
def plot_pizza_radar(labels, data_values, median_values, title="Radar",legend_labels=("Player/Team", "Médiane")):
    # Paramètres de la pizza plot / Parameters of the pizza plot
    pizza = PyPizza(
        params=labels,background_color="#EFF0D1",straight_line_color="#000000",straight_line_lw=1,last_circle_lw=1,
        last_circle_color="#000000",other_circle_ls="--",other_circle_color="#000000",other_circle_lw=0.5
    )
    
    # Mise des couleurs et valeurs sur la pizza plot / Dislay colors and values on the pizza plot / Colores y valores en la pizza plot
    fig, ax = pizza.make_pizza(
        values=[round(v) for v in data_values], 
        compare_values=[round(v) for v in median_values],
        figsize=(8, 8),
        kwargs_slices=dict(
            facecolor="#7FBFFF", edgecolor="#000000", zorder=2, linewidth=1
        ),
        kwargs_compare=dict(
            facecolor="#e63946", edgecolor="#000000", zorder=1, linewidth=1
        ),
        kwargs_params=dict(
            color="#000000", fontsize=11, va="center"
        ),
        kwargs_values=dict(
            color="#000000", fontsize=11, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#7FBFFF", boxstyle="round,pad=0.2", lw=1)
        ),
        kwargs_compare_values=dict(
            color="#000000", fontsize=11, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#f08080", boxstyle="round,pad=0.2", lw=1)
        )
    )

    # Ajustement si valeurs proches / Adjustment if values are close / Ajuste si los valores son cercanos
    threshold = 10
    params_offset = [abs(p - m) < threshold for p, m in zip(data_values, median_values)]
    pizza.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)

    fig.text(0.5, 1.00, title,ha="center", fontsize=14, fontweight="bold", color="#000000") # Titre du radar / Radar title / Título del radar

    # Légende personnalisée / Custom legend / Légende personnalisée
    legend_elements = [Patch(facecolor="#7FBFFF", edgecolor='black', label=legend_labels[0]),Patch(facecolor="#e63946", edgecolor='black', label=legend_labels[1])]
    ax.legend(handles=legend_elements,loc='lower center', bbox_to_anchor=(0.5, -0.15),ncol=2, fontsize=10, frameon=False)

    return fig

# Fonction pour trouver les joueurs similaires / Function to find similar players / Función para encontrar jugadores similares
def find_similar_players(selected_player_name, df, filter_type=None, top_n=5):
    # Informations du joueur sélectionné / Selected player information / Información del jugador seleccionado
    try:
        selected_player_row = df[df['player_name'] == selected_player_name].iloc[0]
    except IndexError:
        return pd.DataFrame()

    sub_position = selected_player_row['position']
    age = selected_player_row['Age']
    competition = selected_player_row['Comp']
    country = selected_player_row['nationality']

    candidates_df = df[df['position'] == sub_position].copy() # Candidats = tous les joueurs du même poste / Candidates = all players in the same position / Candidatos = todos los jugadores en la misma posición

    candidates_df = candidates_df[candidates_df['player_name'] != selected_player_name] # Retirer le joueur lui-même du calcul / Remove the player himself from the calculation / Eliminar al jugador mismo del cálculo

    # Colonnes de stats à comparer (sauf les informations de base) / Columns of statistics to compare (except base informations) / Columnas de estadísticas para comparar (excepto información base)
    stats_cols = df.columns[14:]
    stats_df = candidates_df[stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Ajouter le joueur sélectionné au début pour calculer les similarités / Add the player selected at the beginning to calculate similarities
    # Añadir el jugador seleccionado al principio para calcular las similitudes
    selected_stats = df[df['player_name'] == selected_player_name][stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    full_stats = pd.concat([selected_stats, stats_df], ignore_index=True)

    # Normalisation / Standardisation / Normalización
    scaler = StandardScaler()
    stats_scaled = scaler.fit_transform(full_stats)

    similarities = cosine_similarity(stats_scaled)[0][1:] # Calcul de similarité / Similarity calculation / Cálculo de similitud

    # Ajouter les scores à candidates_df / Add scores to candidates_df / Añadir los scores a candidates_df
    candidates_df = candidates_df.reset_index(drop=True)
    candidates_df['percentage_similarity'] = [round(s * 100, 2) for s in similarities]

    # Appliquer un filtre si spécifié / Apply a filter if specified / Aplicar un filtro si especificado
    if filter_type == "championnat":
        candidates_df = candidates_df[candidates_df['Comp'] == competition]
    elif filter_type == "pays":
        candidates_df = candidates_df[candidates_df['nationality'] == country]
    elif filter_type == "tranche_age":
        if pd.isna(age):
            pass
        elif age < 23:
            candidates_df = candidates_df[candidates_df['Age'] < 23]
        elif 24 <= age <= 29:
            candidates_df = candidates_df[candidates_df['Age'].between(24, 29)]
        else:
            candidates_df = candidates_df[candidates_df['Age'] >= 30]

    candidates_df = candidates_df.sort_values(by='percentage_similarity', ascending=False) # Trier par similarité / Sort by similarity / Ordenar por similitud
    
    candidates_df['marketValue'] = candidates_df['marketValue'].apply(format_market_value) # Formater la colonne de valeur marchande / Formatting market value column / Formatar la columna de valor de mercado

    final_cols = ['player_name', 'percentage_similarity', 'Age', 'nationality',  'club_name', 'marketValue', 'contract'] # Colonnes à afficher / Columns to display / Columnas a mostrar

    # Traduction du pays du joueur / Translation of the player's country / Traducción del país del jugador
    if lang == "Français":
        candidates_df['nationality'] = candidates_df['nationality'].apply(lambda x: translate_country(x, lang="fr"))
    elif lang == "Español":
        candidates_df['nationality'] = candidates_df['nationality'].apply(lambda x: translate_country(x, lang="es"))

    # Renommage des colonnes selon la langue / Renaming columns according to language / Renombrar las columnas según el idioma
    col_labels = {
        "Français": {"player_name": "Joueur","percentage_similarity": "Similarité (%)","Age": "Âge","nationality": "Nationalité","club_name": "Club","marketValue": "Valeur marchande",
            "contract": "Contrat"},
        "Español": {"player_name": "Jugador","percentage_similarity": "Similitud (%)","Age": "Edad","nationality": "Nacionalidad","club_name": "Club","marketValue": "Valor de mercado",
            "contract": "Contrato"},
        "English": {"player_name": "Player","percentage_similarity": "Similarity (%)","Age": "Age","nationality": "Country","club_name": "Club","marketValue": "Market value",
            "contract": "Contract"}}

    out = candidates_df[final_cols].head(top_n).copy()
    out = out.rename(columns=col_labels.get(lang, col_labels["English"]))
    return out

# Fonction pour trouver les équipes similaires / Function to find similar teams / Función para encontrar equipos similares
def find_similar_teams(selected_team_name, df, filter_type=None, top_n=5):
    # Informations de l'équipe sélectionné / Selected team information / Información del equipo seleccionado
    try:
        selected_team_row = df[df['team_code'] == selected_team_name].iloc[0]
    except IndexError:
        return pd.DataFrame()

    competition = selected_team_row['championship_name'] 

    candidates_df = df[df['team_code'] != selected_team_name] # Retirer l'équipe lui-même du calcul / Remove the team himself from the calculation / Eliminar al equipo mismo del cálculo

    # Colonnes de stats à comparer / Columns of statistics to compare  / Columnas de estadísticas para comparar
    stats_cols = [col for col in [
        "attacking_set_pieces__xg_pct","passing__avg_poss","passing__pass_direction__fwd","passing__pass_direction__left","passing__pass_direction__right","passing__crosses__pct",
        "pressing__pressed_seqs_Padj","pressing__ppda","pressing__start_distance_m","sequences__ten_plus_passes","sequences__direct_speed","sequences__passes_per_seq",
        "sequences__sequence_time","sequences__build_ups__total","sequences__direct_attacks__total", "attacking_misc__fast_breaks__total","misc.__fouled","misc.__fouls",
        "defending_set_pieces__xg_pct","defending_defensive_actions__clearancess_Padj","defending_defensive_actions__ground_duels_won","defending_defensive_actions__aerial_duels_won",
        "defending_misc__offsides","Long_Att__pass_prop","direct_attack_prop","build_ups_prop","fast_break_prop"
    ] if col in df.columns]

    stats_df = candidates_df[stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Ajouter l'équipe sélectionné au début pour calculer les similarités / Add the team selected at the beginning to calculate similarities
    # Añadir el equipo seleccionado al principio para calcular las similitudes
    selected_stats = df[df['team_code'] == selected_team_name][stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    full_stats = pd.concat([selected_stats, stats_df], ignore_index=True)

    # Normalisation / Standardisation / Normalización
    scaler = StandardScaler()
    stats_scaled = scaler.fit_transform(full_stats)

    similarities = cosine_similarity(stats_scaled)[0][1:] # Calcul de similarité / Similarity calculation / Cálculo de similitud

    # Ajouter les scores à candidates_df / Add scores to candidates_df / Añadir los scores a candidates_df
    candidates_df = candidates_df.reset_index(drop=True)
    candidates_df['percentage_similarity'] = [round(s * 100, 2) for s in similarities]

    # Appliquer un filtre si spécifié / Apply a filter if specified / Aplicar un filtro si especificado
    if filter_type == "championnat":
        candidates_df = candidates_df[candidates_df['championship_name'] == competition]

    candidates_df = candidates_df.sort_values(by='percentage_similarity', ascending=False) # Trier par similarité / Sort by similarity / Ordenar por similitud
    
    final_cols = ['team_code', 'percentage_similarity', 'championship_name', 'country'] # Colonnes à afficher / Columns to display / Columnas a mostrar
    # Traduction du pays du joueur / Translation of the player's country / Traducción del país del jugador
    if lang == "Français":
        candidates_df['country'] = candidates_df['country'].apply(lambda x: translate_country(x, lang="fr"))
    elif lang == "Español":
        candidates_df['country'] = candidates_df['country'].apply(lambda x: translate_country(x, lang="es"))

    # Renommage des colonnes selon la langue / Renaming columns according to language / Renombrar las columnas según el idioma
    col_labels = {
        "Français": {"team_code": "Équipe","percentage_similarity": "Similarité (%)","championship_name": "Championnat","country": "Pays",},
        "Español": {"team_code": "Equipo","percentage_similarity": "Similitud (%)","championship_name": "Liga","country": "País",},
        "English": {"team_code": "Team","percentage_similarity": "Similarity (%)","championship_name": "League","country": "Country"}}

    out = candidates_df[final_cols].head(top_n).copy()
    out = out.rename(columns=col_labels.get(lang, col_labels["English"]))
    return out

# Fonction pour estimer le style de jeu offensif et défensif d'une équipe / Function to estimate a team's offensive and defensive playing style
# Función para estimar el estilo de juego ofensivo y defensivo de un equipo
def estimate_team_styles(team_row_or_series):
    # Normaliser l'entrée / Normalise input / Normalizar la entrada
    if isinstance(team_row_or_series, pd.Series):
        row = team_row_or_series
    else:
        row = pd.Series(team_row_or_series)

    # Règles / Rules / Reglas
    direct_rules = [
        ("sequences__direct_attacks__total", ">", 1.75),("direct_attack_prop", ">", 40),("Long_Att__pass_prop", ">", 20),
        ("sequences__sequence_time", "<", 10)
    ]
    possession_rules = [
        ("passing__avg_poss", ">", 55),("sequences__build_ups__total", ">", 3),("build_ups_prop", ">", 55),
        ("sequences__sequence_time", ">", 10),("sequences__passes_per_seq", ">", 4),("sequences__ten_plus_passes", ">", 13),
    ]
    counter_rules = [
        ("attacking_misc__fast_breaks__total", ">", 1.25),("fast_break_prop", ">", 25), ("sequences__sequence_time", "<", 10)
    ]
    high_press_rules = [
        ("pressing__pressed_seqs_Padj", ">", 15),("pressing__ppda", "<", 10),("pressing__start_distance_m", ">", 45),
    ]
    low_block_rules = [
        ("pressing__pressed_seqs_Padj", "<", 8),("pressing__ppda", ">", 15),("pressing__start_distance_m", "<", 40),
    ]

    # Fonction pour déterminer le style / Function to determine style / Función para determinar el estilo
    def score_style(rules):
        ok = 0
        seen = 0
        dist_sum = 0.0
        for col, op, thr in rules:
            if col in row and pd.notna(row[col]):
                try:
                    val = float(row[col])
                except Exception:
                    continue
                seen += 1
                if (op == ">" and val > thr) or (op == "<" and val < thr):
                    ok += 1
                    base = abs(thr) if thr != 0 else 1.0
                    dist_sum += (val - thr) / base if op == ">" else (thr - val) / base
        ratio = ok / seen if seen > 0 else 0.0
        return ratio, dist_sum, seen

    # Offensif / Offensive / Ofensivo
    direct = score_style(direct_rules)
    counter = score_style(counter_rules)
    possession = score_style(possession_rules)

    # On cherche le score maximum obtenu entre le style en Jeu direct et Contre-attaque / We are looking for the highest score achieved between the Direct Play and Counterattack styles
    # Se busca la puntuación máxima obtenida entre el estilo de juego directo y el contraataque
    transition_label, transition = max([("Direct Play", direct), ("Counter-Attacking", counter)],key=lambda kv: (kv[1][0], kv[1][1]))
    poss_ratio, poss_dist, poss_seen = possession
    tran_ratio,  tran_dist,  tran_seen  = transition

    # "Mixed" si les deux style de Possession et de Transition sont simultanément faibles ou forts / ‘Mixed’ if both Possession and Transition styles are simultaneously weak or strong
    # «Mixto» si los dos estilos de posesión y transición son simultáneamente débiles o fuertes
    if (poss_seen > 0 and tran_seen > 0) and (
        (poss_ratio < 0.33 and tran_ratio < 0.33) or (poss_ratio >= 0.66 and tran_ratio >= 0.66)
    ):
        offensive_style = "Mixed"
    else:
        # Sinon on choisit le style le plus élevé / Otherwise, we choose the highest style / Si no, se elige el estilo más elevado.
        if (poss_ratio, poss_dist) >= (tran_ratio, tran_dist):
            offensive_style = "Possession Play"
        else:
            offensive_style = transition_label

    # Défensif / Defensive / Defensivo
    hp = score_style(high_press_rules)
    lb = score_style(low_block_rules)
    # Mid Block si aucun extrême ne domine clairement (les deux < 0.5) ou les deux >= 0.5 / Mid Block if neither extreme clearly dominates (both < 0.5) or both >= 0.5
    # Mid Block si ningún extremo predomina claramente (ambos < 0,5) o ambos >= 0,5
    if (hp[2] > 0 and lb[2] > 0) and ((hp[0] < 0.5 and lb[0] < 0.5) or (hp[0] >= 0.5 and lb[0] >= 0.5)):
        defensive_style = "Mid Block"
    else:
        defensive_style = "High Press" if (hp[0], hp[1]) >= (lb[0], lb[1]) else "Low Block"

    return {"offensive_style": offensive_style, "defensive_style": defensive_style}

# Sélecteur de MODE (Équipes / Joueurs) / Selector of MODE (Teams / Players) / Selector de MODE (Equipos / Jugadores)
mode_label = {"Français": "Type d'analyse","English": "Analysis type","Español": "Tipo de análisis",}[lang]
mode_options = {"Français": ["Équipes", "Joueurs"],"English": ["Teams", "Players"],"Español": ["Equipos", "Jugadores"],}[lang]
mode = option_menu(menu_title=None,options=mode_options,icons=["shield", "person-lines-fill"], orientation="horizontal")

# Menus selon le MODE / Menus according to MODE /Menús según el MODO
if (mode in ["Équipes", "Teams", "Equipos"]):
    # MENU ÉQUIPE / MENU TEAM / MENU EQUIPO
    if lang == "Français":
        menu_labels = ["Menu", "Équipe", "Duel", "Stats +", "Stats", "Top"]
    elif lang == "English":
        menu_labels = ["Home", "Team", "F2F", "Stats +", "Stats", "Top"]
    else:
        menu_labels = ["Inicio", "Equipo", "Duelo", "Stats +", "Stats", "Top"]

    selected = option_menu(menu_title=None,options=menu_labels,icons=["house", "people", "crosshair", "trophy", "list-ol", "award"],orientation="horizontal")

    # Code de la partie Équipe / Code of the Team part / Código de la parte Equipo
    if selected in ["Menu", "Home", "Inicio"]:
        if lang == "Français":
            st.markdown("<h3 style='text-align: center;'>Visualisation des performances des équipes sur la saison 25/26</h3>", unsafe_allow_html=True) # Titre de la page
            
            # Utilisation de la 1er bannière en image
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_team_performance.jpg")
            st.image(image_path)

            st.markdown("<h4 style='text-align: center;'>Présentation</h4>", unsafe_allow_html=True) # Sous-titre

            # Description du projet
            st.markdown(
                """
                <p style="text-align: justify;">
                L'objectif est de <strong>visualiser les performances des équipes sur la saison 25/26</strong>.
                Les données des joueurs proviennent de Opta The Analyst, Fbref et Transfermarkt.
                </p>

                <p style="text-align: justify;">
                Ainsi, l'analyse portera sur la saison 25/26 pour les compétitions suivantes :
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Analyse d'un équipes</strong> : Analyse de l'équipe de votre choix à travers plusieurs statistiques</li>
                    <li><strong>🥊 Comparaison entre Équipes</strong> : Analyse comparative entre deux équipes</li>
                    <li><strong>🏆 Classement des équipes (Stats Aggrégées par Catégorie) </strong> : Classement des équipes par performance selon une statistique aggrégée par catégorie choisie</li>
                    <li><strong>🥇 Classement des équipes (Stats Brutes) </strong> : Classement des équipes par performance selon une statistique brute choisie</li>
                    <li><strong>⭐ Top </strong> : Établissement d'une classement des équipes à partir des statistiques</li>
                </ul>

                <br>

                Pour plus de détails sur ce projet, vous avez à votre disposition :
                <ul>
                    <li><a href="https://github.com/football-labs/Fotball-labs/blob/main/documentation/Documentation_FR.pdf" target="_blank">La documentation du projet</a></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">Le code associé à l'application</a></li>
                </ul>
                """,
                unsafe_allow_html=True
            )

        elif lang == "English":
            st.markdown("<h3 style='text-align: center;'>Visualization of team performance over the 25/26 season</h3>", unsafe_allow_html=True) # Page title
            
            # Using the 1st image banner
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_team_performance.jpg")
            st.image(image_path)

            st.markdown("<h4 style='text-align: center;'>Presentation</h4>", unsafe_allow_html=True) # Subtitle

            # Project description
            st.markdown(
                """
                <p style="text-align: justify;">
                The goal is to <strong>visualize team performances during the 25/26 season</strong>.
                The data of players comes from Opta The Analyst, Fbref and Transfermarkt.
                </p>
                <p style="text-align: justify;">
                The analysis will cover the 25/26 season for the following competitions:
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Team Analysis</strong>: Analyze the team of your choice through various statistics</li>
                    <li><strong>🥊 Team Comparison</strong>: Compare two teams</li>
                    <li><strong>🏆 Team Ranking (Aggregate Statistics by Category) </strong>: Rank teams based on a chosen aggregate statistic by category according to their position</li>
                    <li><strong>🥇 Team Ranking (Raw Statistics) </strong>: Rank teams based on a chosen raw statistic</li>
                    <li><strong>⭐ Top </strong> : Establishing a ranking of teams based on statistics</li>
                </ul>

                <br>

                For more details about this project, you can refer to:
                <ul>
                    <li><a href="https://github.com/football-labs/Fotball-labs/blob/main/documentation/Documentation_ENG.pdf" target="_blank">The project documentation</a></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">The code used to build the application</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
        else :
            st.markdown("<h3 style='text-align: center;'>Visualización del rendimiento de los equipos durante la temporada 25/26</h3>", unsafe_allow_html=True) # Título de la página

            # Usando el primer banner de imagen
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_team_performance.jpg")
            st.image(image_path)

            st.markdown("<h4 style='text-align: center;'>Presentación</h4>", unsafe_allow_html=True) # Subtítulo

            # Descripción del proyecto
            st.markdown(
                """
                <p style="text-align: justify;">
                El objetivo es <strong>visualizar el rendimiento de los equipos durante la temporada 25/26</strong>.
                Los datos de los jugadores provienen de Opta The Analyst, Fbref y Transfermarkt.
                </p>
                <p style="text-align: justify;">
                El análisis abarcará la temporada 25/26 para las siguientes competiciones:
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Análisis de equipos</strong>: Analizar el equipo de tu elección a través de varias estadísticas</li>
                    <li><strong>🥊 Comparación de equipos</strong>: Comparar dos equipos</li>
                    <li><strong>🏆 Clasificación de equipos (Estadísticas agregadas por categoría) </strong>: Clasificar a los equipos según una estadística agregada por categoría de acuerdo con su posición</li>
                    <li><strong>🥇 Clasificación de equipos (Estadísticas brutas) </strong>: Clasificar a los equipos según una estadística bruta elegida</li>
                    <li><strong>⭐ Top </strong>: Establecer una clasificación de equipos basada en estadísticas</li>
                </ul>

                <br>

                Para más detalles sobre este proyecto, puedes consultar:
                <ul>
                    <li><a href="https://github.com/football-labs/Fotball-labs/blob/main/documentation/Documentation_ES.pdf" target="_blank">La documentación del proyecto</a></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">El código utilizado para construir la aplicación</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
                    
    elif selected in ["Équipe", "Team", "Equipo"]:
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>📊 Analyse d'une équipe</h4>", unsafe_allow_html=True) # Afficher le titre
            # Charger les données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            championship_names = [''] + sorted(info_team['championship_name'].dropna().unique().tolist()) # Extraire la liste des championnats

            selected_championship = st.sidebar.selectbox("Choisissez un championnat :", championship_names) # Sélection de championnat

            championship_data = info_team[info_team['championship_name'] == selected_championship]
                    
            teams_names = [''] + sorted(championship_data['team_code'].dropna().unique().tolist()) # Extraire la liste des équipes dans le championnat choisi

            selected_team = st.sidebar.selectbox("Choisissez une équipe :", teams_names) # Sélection de l'équipe

            # Si un championnat est sélectionné, on cache l’image   
            if not selected_championship or not selected_team:
                # Aucun championnat sélectionné, on affiche l'image d'intro
                # Utilisation de la 1er bannière en image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "championship_analysis.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour choisir la langue et le championnat à analyser")
            else:
                team_data = info_team[info_team['team_code'] == selected_team].iloc[0] # Filtrer le DataFrame pour l'équipe sélectionnée
                pays = translate_country(team_data['country'], lang="fr") # On traduit le nom du pays
                
                # On indique le noms des colonnes utilisées
                df_team_col = "team_code"     # dans info_team
                club_col = "club_name"     # dans info_player
                value_col = "marketValue"  # dans info_player
                name_col = "player_name"      # dans info_player
                rating_col = "rating"         # dans info_player

                team_df_name = str(team_data[df_team_col]) # Nom de club côté info_player après mapping
                team_info_name = df_to_info.get(team_df_name, team_df_name)

                subset = info_player[info_player[club_col] == team_info_name].copy() # Filtrer les joueurs du club sélectionné

                # Calculer total et moyenne des valeurs sur le marché des joueurs par équipe
                if subset.empty:
                    valeur_effectif_fmt = "Non connu"
                    valeur_par_joueur_fmt = "Non connu"
                else:
                    total_value = subset[value_col].sum(min_count=1)
                    n_players = len(subset)

                    if pd.isna(total_value) or n_players == 0:
                        valeur_effectif_fmt = "Non connu"
                        valeur_par_joueur_fmt = "Non connu"
                    else:
                        valeur_effectif_fmt = format_market_value(total_value)
                        valeur_par_joueur_fmt = format_market_value(total_value / n_players)

                # On estime le style de jeu offensif et défensif de l'équipe
                styles = estimate_team_styles(team_data) 
                off_label = translate_style(styles["offensive_style"], lang="fr")
                def_label = translate_style(styles["defensive_style"], lang="fr")

                # Équipe (image à gauche, infos à droite)
                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{team_data['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 180px;">
                    <p><strong>Nom :</strong> {team_data['team_code']}</p>
                    <p><strong>Saison :</strong> {team_data['season_name']}</p>
                    <p><strong>Ligue :</strong> {team_data['championship_name']}</p>
                    <p><strong>Pays :</strong> {pays}</p>
                    <p><strong>Power Ranking :</strong> {team_data['rank_big5']}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Classement :</strong> {team_data['rank_league']}</p>
                    <p><strong>Pts :</strong> {int(team_data['pts_league'])}</p>
                    <p><strong>Différence de buts :</strong> {int(team_data['team_success_plus_minus'])}</p>
                    <p><strong>Style de jeu Offensif :</strong> {off_label}</p>
                    <p><strong>Style de jeu Défensif :</strong> {def_label}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Âge moyen :</strong> {team_data['age']}</p>
                    <p><strong>Taille effectif :</strong> {int(team_data['players']) if pd.notna(team_data['players']) else "-"}</p>
                    <p><strong>Valeur effectif :</strong> {valeur_effectif_fmt}</p>
                    <p><strong>Valeur par joueur :</strong> {valeur_par_joueur_fmt}</p>
                    <p><strong>Salaire annuel :</strong> {format_market_value(team_data['Annual Wages'])}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

                # On définit par défaut les Top 5
                top5_rating_list = ["Non disponible"]
                top5_valued_list = ["Non disponible"]

                # On calcule le Top 5 joueurs de la saison (par rating) et le Top 5 joueurs les plus valorisés (par marketValue)
                if not subset.empty and {name_col, rating_col, value_col}.issubset(subset.columns):
                    df_tmp = subset.copy()

                    # Top 5 joueurs de la saison (par rating)
                    df_tmp["rating_num"] = pd.to_numeric(df_tmp[rating_col], errors="coerce")
                    top_rating_df = (
                        df_tmp.dropna(subset=["rating_num"])
                            .sort_values("rating_num", ascending=False)
                            .head(5)
                    )
                    if not top_rating_df.empty:
                        # Arrondi à l'entier
                        top5_rating_list = [
                            f"{row[name_col]} ({int(round(row['rating_num']))})"
                            for _, row in top_rating_df.iterrows()
                        ]

                    # Top 5 joueurs les plus valorisés (par marketValue)
                    df_tmp["mv_num"] = pd.to_numeric(df_tmp[value_col], errors="coerce")
                    if df_tmp["mv_num"].notna().any():
                        top_valued_df = df_tmp.sort_values("mv_num", ascending=False).head(5)
                        items = []
                        for _, row in top_valued_df.iterrows():
                            if pd.notna(row["mv_num"]):
                                s = format_market_value(int(round(row["mv_num"])))
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)  # On enlève les .0M € dans l'affichage
                                items.append(f"{row[name_col]} ({s})")
                        top5_valued_list = items if items else ["Non disponible"]
                    else:
                        top_valued_df = df_tmp.sort_values(value_col, ascending=False).head(5)
                        if not top_valued_df.empty:
                            items = []
                            for _, row in top_valued_df.iterrows():
                                s = format_market_value(row[value_col])
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)
                                items.append(f"{row[name_col]} ({s})")
                            top5_valued_list = items
                        else:
                            top5_valued_list = ["Non disponible"]

                # On affiche les tops
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("<h5>🏅 Top 5 joueurs de la saison</h5>", unsafe_allow_html=True)
                    if top5_rating_list == ["Non disponible"]:
                        st.write("Non disponible")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_rating_list]))

                with col2:
                    st.markdown("<h5>💎 Top 5 joueurs les plus valorisés</h5>", unsafe_allow_html=True)
                    if top5_valued_list == ["Non disponible"]:
                        st.write("Non disponible")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_valued_list]))

                # Filtre
                st.markdown("<p style='text-align:center; margin-bottom:0'>En comparaison avec :</p>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1.6, 2, 1])
                with c2:
                    comparison_filter = st.radio(label="En comparaison avec",options=["Big 5", "Championnat"],index=0,
                        horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

                filter_arg = {"Big 5": None, "Championnat": "championnat"}[comparison_filter]

                # Groupe filtré selon le filtre sélectionné 
                if filter_arg is None:
                    group_df = info_team  # Pas de filtre
                else:  # "championnat"
                    group_df = info_team[info_team['championship_name'] == team_data['championship_name']]

                # Colonnes par catégorie
                pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                # On construit le radar
                def build_radar(cols, title):
                    use_cols = [c for c in cols if (c in team_data.index) and (c in group_df.columns)]
                    if not use_cols:
                        return None
                    labels = [translate_base_stat(c.replace("score_", ""), lang="fr") for c in use_cols]
                    team_vals = [team_data[c] for c in use_cols]
                    group_meds = group_df[use_cols].median(numeric_only=True).tolist()

                    team_scaled = [0 if pd.isna(v) else v for v in team_vals]
                    median_scaled = [0 if pd.isna(v) else round(v) for v in group_meds]

                    fig = plot_pizza_radar(labels=labels,data_values=team_scaled,median_values=median_scaled,
                        title=f"{title} de {team_data['team_code']} vs Médiane",legend_labels=(team_data["team_code"], "Médiane"))
                    return fig

                # Construit les 4 radars
                fig_pizza_stat_off    = build_radar(pizza_cols_off, "Statistiques offensives")
                fig_pizza_stat_def    = build_radar(pizza_cols_def, "Statistiques défensives")
                fig_pizza_stat_style  = build_radar(pizza_cols_style_of_play, "Performance selon le style de jeu")
                fig_pizza_stat_others = build_radar(pizza_cols_other, "Autres statistiques")

                # Affichage 2 x 2
                col1, col2 = st.columns(2)
                with col1:
                    if fig_pizza_stat_off is not None:
                        st.pyplot(fig_pizza_stat_off)
                with col2:
                    if fig_pizza_stat_def is not None:
                        st.pyplot(fig_pizza_stat_def)

                col3, col4 = st.columns(2)
                with col3:
                    if fig_pizza_stat_style is not None:
                        st.pyplot(fig_pizza_stat_style)
                with col4:
                    if fig_pizza_stat_others is not None:
                        st.pyplot(fig_pizza_stat_others)

                # Construction du tableau des Équipes similaires
                similar_df = find_similar_teams(selected_team, info_team, filter_type=filter_arg)
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align:center;'>Équipes similaires à {team_data['team_code']}</h4>", unsafe_allow_html=True)
                    d1, d2, d3 = st.columns([0.1, 0.8, 0.1])
                    with d2:
                        st.dataframe(similar_df, use_container_width=True)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>📊 Team analysis</h4>", unsafe_allow_html=True) # Display title
            # Load data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            championship_names = [''] + sorted(info_team['championship_name'].dropna().unique().tolist()) # Extract championship list

            selected_championship = st.sidebar.selectbox("Choose a league :", championship_names) # Selection of the championship

            championship_data = info_team[info_team['championship_name'] == selected_championship]
                    
            teams_names = [''] + sorted(championship_data['team_code'].dropna().unique().tolist()) # Extract the list of teams in the selected league

            selected_team = st.sidebar.selectbox("Choose a team :", teams_names) # Selection of the team

            # If a championship is selected, the image is hidden.   
            if not selected_championship or not selected_team:
                # No league selected, intro image displayed
                # Use of the first banner in image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "championship_analysis.jpg")
                st.image(image_path)
                st.info("Expand the sidebar to select the language and league to analyze")
            else:
                team_data = info_team[info_team['team_code'] == selected_team].iloc[0] # Filter the DataFrame for the selected team
                
                # The names of the columns used are indicated
                df_team_col = "team_code"     # in info_team
                club_col = "club_name"     # in info_player
                value_col = "marketValue"  # in info_player
                name_col = "player_name"      # in info_player
                rating_col = "rating"         # in info_player

                team_df_name = str(team_data[df_team_col]) # Club name listed under info_player after map
                team_info_name = df_to_info.get(team_df_name, team_df_name)

                subset = info_player[info_player[club_col] == team_info_name].copy() # Filter players from the selected club

                # Calculate total and average market values of players per team
                if subset.empty:
                    valeur_effectif_fmt = "Unknown"
                    valeur_par_joueur_fmt = "Unknown"
                else:
                    total_value = subset[value_col].sum(min_count=1)
                    n_players = len(subset)

                    if pd.isna(total_value) or n_players == 0:
                        valeur_effectif_fmt = "Unknown"
                        valeur_par_joueur_fmt = "Unknown"
                    else:
                        valeur_effectif_fmt = format_market_value(total_value)
                        valeur_par_joueur_fmt = format_market_value(total_value / n_players)

                # The team's offensive and defensive style of play is highly regarded.
                styles = estimate_team_styles(team_data) 
                off_label = styles["offensive_style"]
                def_label = styles["defensive_style"]

                # Team (image on the left, information on the right)
                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{team_data['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 180px;">
                    <p><strong>Name :</strong> {team_data['team_code']}</p>
                    <p><strong>Season :</strong> {team_data['season_name']}</p>
                    <p><strong>League :</strong> {team_data['championship_name']}</p>
                    <p><strong>Country :</strong> {team_data['country']}</p>
                    <p><strong>Power Ranking :</strong> {team_data['rank_big5']}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Ranking :</strong> {team_data['rank_league']}</p>
                    <p><strong>Pts :</strong> {int(team_data['pts_league'])}</p>
                    <p><strong>Goal average :</strong> {int(team_data['team_success_plus_minus'])}</p>
                    <p><strong>Offensive playing style :</strong> {off_label}</p>
                    <p><strong>Defensive playing style :</strong> {def_label}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Average age :</strong> {team_data['age']}</p>
                    <p><strong>Effective size :</strong> {int(team_data['players']) if pd.notna(team_data['players']) else "-"}</p>
                    <p><strong>Value of squad :</strong> {valeur_effectif_fmt}</p>
                    <p><strong>Value per player :</strong> {valeur_par_joueur_fmt}</p>
                    <p><strong>Annual salary :</strong> {format_market_value(team_data['Annual Wages'])}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

                # The Top 5 are defined by default
                top5_rating_list = ["Not available"]
                top5_valued_list = ["Not available"]

                # We calculate the Top 5 players of the season (by rating) and the Top 5 most valuable players (by market value).
                if not subset.empty and {name_col, rating_col, value_col}.issubset(subset.columns):
                    df_tmp = subset.copy()

                    # Top 5 players of the season (by rating)
                    df_tmp["rating_num"] = pd.to_numeric(df_tmp[rating_col], errors="coerce")
                    top_rating_df = (
                        df_tmp.dropna(subset=["rating_num"])
                            .sort_values("rating_num", ascending=False)
                            .head(5)
                    )
                    if not top_rating_df.empty:
                        # Rounded to the nearest whole number
                        top5_rating_list = [
                            f"{row[name_col]} ({int(round(row['rating_num']))})"
                            for _, row in top_rating_df.iterrows()
                        ]

                    # Top 5 most valuable players (by market value)
                    df_tmp["mv_num"] = pd.to_numeric(df_tmp[value_col], errors="coerce")
                    if df_tmp["mv_num"].notna().any():
                        top_valued_df = df_tmp.sort_values("mv_num", ascending=False).head(5)
                        items = []
                        for _, row in top_valued_df.iterrows():
                            if pd.notna(row["mv_num"]):
                                s = format_market_value(int(round(row["mv_num"])))
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)  # Remove the .0M € from the display.
                                items.append(f"{row[name_col]} ({s})")
                        top5_valued_list = items if items else ["Not available"]
                    else:
                        top_valued_df = df_tmp.sort_values(value_col, ascending=False).head(5)
                        if not top_valued_df.empty:
                            items = []
                            for _, row in top_valued_df.iterrows():
                                s = format_market_value(row[value_col])
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)
                                items.append(f"{row[name_col]} ({s})")
                            top5_valued_list = items
                        else:
                            top5_valued_list = ["Not available"]

                # The top rankings are displayed
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("<h5>🏅 Top 5 players of the season</h5>", unsafe_allow_html=True)
                    if top5_rating_list == ["Not available"]:
                        st.write("Not available")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_rating_list]))

                with col2:
                    st.markdown("<h5>💎 Top 5 most valuable players</h5>", unsafe_allow_html=True)
                    if top5_valued_list == ["Not available"]:
                        st.write("Not available")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_valued_list]))

                # Filter
                st.markdown("<p style='text-align:center; margin-bottom:0'>Compared to :</p>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1.6, 2, 1])
                with c2:
                    comparison_filter = st.radio(label="Compared",options=["Big 5", "Championship"],index=0,
                        horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

                filter_arg = {"Big 5": None, "Championship": "championnat"}[comparison_filter]

                # Group filtered according to the selected filter 
                if filter_arg is None:
                    group_df = info_team  # No filter
                else:  # "championship"
                    group_df = info_team[info_team['championship_name'] == team_data['championship_name']]

                # Columns by category
                pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                # We are building the radar.
                def build_radar(cols, title):
                    use_cols = [c for c in cols if (c in team_data.index) and (c in group_df.columns)]
                    if not use_cols:
                        return None
                    labels = [translate_base_stat(c.replace("score_", ""), lang="eng") for c in use_cols]
                    team_vals = [team_data[c] for c in use_cols]
                    group_meds = group_df[use_cols].median(numeric_only=True).tolist()

                    team_scaled = [0 if pd.isna(v) else v for v in team_vals]
                    median_scaled = [0 if pd.isna(v) else round(v) for v in group_meds]

                    fig = plot_pizza_radar(labels=labels,data_values=team_scaled,median_values=median_scaled,
                        title=f"{title} de {team_data['team_code']} vs Median",legend_labels=(team_data["team_code"], "Median"))
                    return fig

                # Builds the 4 radars
                fig_pizza_stat_off    = build_radar(pizza_cols_off, "Offensive statistics")
                fig_pizza_stat_def    = build_radar(pizza_cols_def, "Defensive statistics")
                fig_pizza_stat_style  = build_radar(pizza_cols_style_of_play, "Performance based on playing style")
                fig_pizza_stat_others = build_radar(pizza_cols_other, "Other statistics")

                # 2 x 2 display
                col1, col2 = st.columns(2)
                with col1:
                    if fig_pizza_stat_off is not None:
                        st.pyplot(fig_pizza_stat_off)
                with col2:
                    if fig_pizza_stat_def is not None:
                        st.pyplot(fig_pizza_stat_def)

                col3, col4 = st.columns(2)
                with col3:
                    if fig_pizza_stat_style is not None:
                        st.pyplot(fig_pizza_stat_style)
                with col4:
                    if fig_pizza_stat_others is not None:
                        st.pyplot(fig_pizza_stat_others)

                # Construction of the Similar Teams table
                similar_df = find_similar_teams(selected_team, info_team, filter_type=filter_arg)
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align:center;'>Teams similar to {team_data['team_code']}</h4>", unsafe_allow_html=True)
                    d1, d2, d3 = st.columns([0.1, 0.8, 0.1])
                    with d2:
                        st.dataframe(similar_df, use_container_width=True)

        else:
            st.markdown("<h4 style='text-align: center;'>📊 Análisis de un equipo</h4>", unsafe_allow_html=True) # Mostrar título
            # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            championship_names = [''] + sorted(info_team['championship_name'].dropna().unique().tolist()) # Extraer la lista de campeonatos

            selected_championship = st.sidebar.selectbox("Elige una liga :", championship_names) # Selección del campeonato

            championship_data = info_team[info_team['championship_name'] == selected_championship]
                    
            teams_names = [''] + sorted(championship_data['team_code'].dropna().unique().tolist()) # Extraer la lista de equipos de la liga seleccionada

            selected_team = st.sidebar.selectbox("Elige un equipo :", teams_names) # Selección del equipo

            # Si se selecciona un campeonato, se oculta la imagen.     
            if not selected_championship or not selected_team:
                # No se ha seleccionado ningún campeonato, se muestra la imagen de introducción.
                # Uso del primer banner en imagen
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "championship_analysis.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma y la liga que deseas analizar.")
            else:
                team_data = info_team[info_team['team_code'] == selected_team].iloc[0] # Filtrar el DataFrame para el equipo seleccionado
                pays = translate_country(team_data['country'], lang="es") # Se traduce el nombre del país.
                
                # Se indican los nombres de las columnas utilizadas
                df_team_col = "team_code"     # en info_team
                club_col = "club_name"     # en info_player
                value_col = "marketValue"  # en info_player
                name_col = "player_name"      # en info_player
                rating_col = "rating"         # en info_player

                team_df_name = str(team_data[df_team_col]) # Nombre del club junto a info_player después del mapeo
                team_info_name = df_to_info.get(team_df_name, team_df_name)

                subset = info_player[info_player[club_col] == team_info_name].copy() # Filtrar los jugadores del club seleccionado

                # Calcular el total y la media de los valores en el mercado de los jugadores por equipo.
                if subset.empty:
                    valeur_effectif_fmt = "Desconocido"
                    valeur_par_joueur_fmt = "Desconocido"
                else:
                    total_value = subset[value_col].sum(min_count=1)
                    n_players = len(subset)

                    if pd.isna(total_value) or n_players == 0:
                        valeur_effectif_fmt = "Desconocido"
                        valeur_par_joueur_fmt = "Desconocido"
                    else:
                        valeur_effectif_fmt = format_market_value(total_value)
                        valeur_par_joueur_fmt = format_market_value(total_value / n_players)

                #  Se valora el estilo de juego ofensivo y defensivo del equipo
                styles = estimate_team_styles(team_data) 
                off_label = translate_style(styles["offensive_style"], lang="es")
                def_label = translate_style(styles["defensive_style"], lang="es")

                # Equipo (imagen a la izquierda, información a la derecha)
                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{team_data['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 180px;">
                    <p><strong>Nombre :</strong> {team_data['team_code']}</p>
                    <p><strong>Temporada :</strong> {team_data['season_name']}</p>
                    <p><strong>Liga :</strong> {team_data['championship_name']}</p>
                    <p><strong>País :</strong> {pays}</p>
                    <p><strong>Power Ranking :</strong> {team_data['rank_big5']}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Clasificación :</strong> {team_data['rank_league']}</p>
                    <p><strong>Pts :</strong> {int(team_data['pts_league'])}</p>
                    <p><strong>Diferencia de goles :</strong> {int(team_data['team_success_plus_minus'])}</p>
                    <p><strong>Estilo de juego Ofensivo :</strong> {off_label}</p>
                    <p><strong>Estilo de juego Defensivo :</strong> {def_label}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Edad media :</strong> {team_data['age']}</p>
                    <p><strong>Tamaño efectivo :</strong> {int(team_data['players']) if pd.notna(team_data['players']) else "-"}</p>
                    <p><strong>Valor efectivo :</strong> {valeur_effectif_fmt}</p>
                    <p><strong>Valor por jugador :</strong> {valeur_par_joueur_fmt}</p>
                    <p><strong>Salario anual :</strong> {format_market_value(team_data['Annual Wages'])}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

                # Se definen por defecto los Top 5
                top5_rating_list = ["No disponible"]
                top5_valued_list = ["No disponible"]

                # Se calculan los 5 mejores jugadores de la temporada (por clasificación) y los 5 jugadores más valorados (por valor de mercado).
                if not subset.empty and {name_col, rating_col, value_col}.issubset(subset.columns):
                    df_tmp = subset.copy()

                    # Los 5 mejores jugadores de la temporada (por clasificación)
                    df_tmp["rating_num"] = pd.to_numeric(df_tmp[rating_col], errors="coerce")
                    top_rating_df = (
                        df_tmp.dropna(subset=["rating_num"])
                            .sort_values("rating_num", ascending=False)
                            .head(5)
                    )
                    if not top_rating_df.empty:
                        # Redondeado al entero
                        top5_rating_list = [
                            f"{row[name_col]} ({int(round(row['rating_num']))})"
                            for _, row in top_rating_df.iterrows()
                        ]

                    # Los 5 jugadores más valorados (por marketValue)
                    df_tmp["mv_num"] = pd.to_numeric(df_tmp[value_col], errors="coerce")
                    if df_tmp["mv_num"].notna().any():
                        top_valued_df = df_tmp.sort_values("mv_num", ascending=False).head(5)
                        items = []
                        for _, row in top_valued_df.iterrows():
                            if pd.notna(row["mv_num"]):
                                s = format_market_value(int(round(row["mv_num"])))
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)  # Se eliminan los 0,0 millones de euros de la visualización.
                                items.append(f"{row[name_col]} ({s})")
                        top5_valued_list = items if items else ["No disponible"]
                    else:
                        top_valued_df = df_tmp.sort_values(value_col, ascending=False).head(5)
                        if not top_valued_df.empty:
                            items = []
                            for _, row in top_valued_df.iterrows():
                                s = format_market_value(row[value_col])
                                s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z])', r'\1', s)
                                items.append(f"{row[name_col]} ({s})")
                            top5_valued_list = items
                        else:
                            top5_valued_list = ["No disponible"]

                # Se muestran los tops
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("<h5>🏅 Los 5 mejores jugadores de la temporada</h5>", unsafe_allow_html=True)
                    if top5_rating_list == ["No disponible"]:
                        st.write("No disponible")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_rating_list]))

                with col2:
                    st.markdown("<h5>💎 Los 5 jugadores más valorados</h5>", unsafe_allow_html=True)
                    if top5_valued_list == ["No disponible"]:
                        st.write("No disponible")
                    else:
                        st.write("\n".join([f"- {x}" for x in top5_valued_list]))

                # Filtro
                st.markdown("<p style='text-align:center; margin-bottom:0'>En comparación con :</p>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1.6, 2, 1])
                with c2:
                    comparison_filter = st.radio(label="En comparación con",options=["Big 5", "Liga"],index=0,
                        horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

                filter_arg = {"Big 5": None, "Liga": "championnat"}[comparison_filter]

                # Grupo filtrado según el filtro seleccionado 
                if filter_arg is None:
                    group_df = info_team  # No filtro
                else:  # "liga"
                    group_df = info_team[info_team['championship_name'] == team_data['championship_name']]

                # Columnas por categoría
                pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                # Se construye el radar
                def build_radar(cols, title):
                    use_cols = [c for c in cols if (c in team_data.index) and (c in group_df.columns)]
                    if not use_cols:
                        return None
                    labels = [translate_base_stat(c.replace("score_", ""), lang="es") for c in use_cols]
                    team_vals = [team_data[c] for c in use_cols]
                    group_meds = group_df[use_cols].median(numeric_only=True).tolist()

                    team_scaled = [0 if pd.isna(v) else v for v in team_vals]
                    median_scaled = [0 if pd.isna(v) else round(v) for v in group_meds]

                    fig = plot_pizza_radar(labels=labels,data_values=team_scaled,median_values=median_scaled,
                        title=f"{title} de {team_data['team_code']} vs Mediana",legend_labels=(team_data["team_code"], "Mediana"))
                    return fig

                # Construye los 4 radares.
                fig_pizza_stat_off    = build_radar(pizza_cols_off, "Estadísticas ofensivas")
                fig_pizza_stat_def    = build_radar(pizza_cols_def, "Estadísticas defensivas")
                fig_pizza_stat_style  = build_radar(pizza_cols_style_of_play, "Rendimiento según el estilo de juego")
                fig_pizza_stat_others = build_radar(pizza_cols_other, "Otras estadísticas")

                # Pantalla 2 x 2
                col1, col2 = st.columns(2)
                with col1:
                    if fig_pizza_stat_off is not None:
                        st.pyplot(fig_pizza_stat_off)
                with col2:
                    if fig_pizza_stat_def is not None:
                        st.pyplot(fig_pizza_stat_def)

                col3, col4 = st.columns(2)
                with col3:
                    if fig_pizza_stat_style is not None:
                        st.pyplot(fig_pizza_stat_style)
                with col4:
                    if fig_pizza_stat_others is not None:
                        st.pyplot(fig_pizza_stat_others)

                # Creación de la tabla de equipos similares
                similar_df = find_similar_teams(selected_team, info_team, filter_type=filter_arg)
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align:center;'>Equipos similares a {team_data['team_code']}</h4>", unsafe_allow_html=True)
                    d1, d2, d3 = st.columns([0.1, 0.8, 0.1])
                    with d2:
                        st.dataframe(similar_df, use_container_width=True)

    elif selected in ["Duel", "F2F", "Duelo"]:
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🥊 Comparaison de deux équipes</h4>", unsafe_allow_html=True) # Affichage du titre
            
            # Charger les données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            teams_names = [''] + sorted(info_team['team_code'].dropna().unique().tolist()) # Extraire la liste des équipes dans le championnat choisi

            team1 = st.sidebar.selectbox("Première équipe :", [''] + teams_names, key="team1") # Sélection de la 1ère équipe

            if not team1:
                # Aucune équipe sélectionnée → afficher l'image d'intro
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour choisir la langue et les équipes à analyser")

            if team1:
                # Nous stockons les informations de la 1ère équipe
                team1_data = info_team[info_team['team_code'] == team1].iloc[0] # Récupération des informations de la 1ère équipe

                team2_names = sorted(info_team['team_code'].dropna().unique().tolist())
                team2_names = [t for t in team2_names if t != team1]

                team2 = st.sidebar.selectbox("Seconde équipe :", [''] + team2_names, key="team2") # Sélection de la 2ème équipe
                
                if not team2:
                    # Aucune équipe sélectionnée → afficher l'image d'intro
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                    st.image(image_path)
                    st.info("Dérouler la barre latérale pour choisir la langue et les équipes à analyser")

                if team2:
                    team2_data = info_team[info_team['team_code'] == team2].iloc[0] # Récupération des informations de la 2ème équipe
                    
                    st.markdown("<h5 style='text-align: center;'>Présentations des équipes</h4>", unsafe_allow_html=True) # On affiche le profil des équipes

                    # Colonnes
                    df_team_col = "team_code"
                    club_col    = "club_name"
                    value_col   = "marketValue"
                    name_col    = "player_name"
                    rating_col  = "rating"

                    # Regrouper les deux équipes
                    team_datas = [team1_data, team2_data]
                    team_codes = [str(td[df_team_col]) for td in team_datas]
                    team_names = [df_to_info.get(code, code) for code in team_codes]

                    both_teams_players = info_player[info_player[club_col].isin(team_names)].copy() # Joueurs des deux équipes

                    # Agrégats par club
                    if both_teams_players.empty:
                        vals_by_team = {name: {"valeur_effectif_fmt": "Non connu", "valeur_par_joueur_fmt": "Non connu"}
                                        for name in team_names}
                    else:
                        tmp = (
                            both_teams_players.groupby(club_col, dropna=False)
                            .agg(total_value=(value_col, "sum"), n_players=(value_col, "size"))
                            .reset_index()
                        )
                        def fmt_or_unknown(v):
                            return "Non connu" if pd.isna(v) else format_market_value(v)
                        tmp["valeur_effectif_fmt"]   = tmp["total_value"].apply(fmt_or_unknown)
                        tmp["valeur_par_joueur_fmt"] = (tmp["total_value"] / tmp["n_players"]).apply(
                            lambda v: "Non connu" if not np.isfinite(v) else format_market_value(v)
                        )
                        vals_by_team = {
                            row[club_col]: {
                                "valeur_effectif_fmt": row["valeur_effectif_fmt"],
                                "valeur_par_joueur_fmt": row["valeur_par_joueur_fmt"],
                            } for _, row in tmp.iterrows()
                        }
                        for name in team_names:
                            vals_by_team.setdefault(name, {"valeur_effectif_fmt": "Non connu", "valeur_par_joueur_fmt": "Non connu"})

                    # Styles par équipe
                    styles_by_team = {}
                    for td, club_name in zip(team_datas, team_names):
                        style_dict = estimate_team_styles(td)
                        styles_by_team[club_name] = {
                            "off": translate_style(style_dict["offensive_style"], lang="fr"),
                            "def": translate_style(style_dict["defensive_style"], lang="fr"),
                        }

                    # Affichage
                    for td in team_datas:
                        key = str(td[df_team_col])

                        pays = translate_country(td["country"], lang="fr")
                        club_name = df_to_info.get(key, key)

                        valeur_par_joueur_fmt = vals_by_team.get(club_name, {}).get("valeur_par_joueur_fmt", "Non connu")
                        off_label = styles_by_team.get(club_name, {}).get("off", "Non connu")
                        def_label = styles_by_team.get(club_name, {}).get("def", "Non connu")

                        pts_league = int(td["pts_league"]) if pd.notna(td["pts_league"]) else "-"
                        taille_effectif = int(td["players"]) if pd.notna(td["players"]) else "-"
                        salaire_annuel = format_market_value(td["Annual Wages"]) if "Annual Wages" in td else "Non connu"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{td['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Nom :</strong> {td['team_code']}</p>
                            <p><strong>Championnat :</strong> {td['championship_name']}</p>
                            <p><strong>Pays :</strong> {pays}</p>
                            <p><strong>Power Ranking :</strong> {td['rank_big5']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Classement :</strong> {td['rank_league']}</p>
                            <p><strong>Pts :</strong> {pts_league}</p>
                            <p><strong>Style de jeu Offensif :</strong> {off_label}</p>
                            <p><strong>Style de jeu Défensif :</strong> {def_label}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Âge moyen :</strong> {td['age']}</p>
                            <p><strong>Taille effectif :</strong> {taille_effectif}</p>
                            <p><strong>Valeur par joueur :</strong> {valeur_par_joueur_fmt}</p>
                            <p><strong>Salaire annuel :</strong> {salaire_annuel}</p>
                        </div>

                        </div>
                        """, unsafe_allow_html=True)

                    # Construction des tops par équipe
                    results_by_team = {}

                    for td, club_map_name in zip(team_datas, team_names):
                        # Nom affiché et clé de filtre
                        team_code = str(td[df_team_col])
                        club_name = df_to_info.get(team_code, team_code)

                        # Par défaut
                        top5_rating = ["Non disponible"]
                        top5_value  = ["Non disponible"]

                        df_team = both_teams_players[both_teams_players[club_col] == club_name].copy()
                        if not df_team.empty and {name_col, rating_col, value_col}.issubset(df_team.columns):

                            # Top 5 rating
                            df_team["rating_num"] = pd.to_numeric(df_team[rating_col], errors="coerce")
                            top_rating_df = (
                                df_team.dropna(subset=["rating_num"])
                                    .sort_values("rating_num", ascending=False)
                                    .head(5)
                            )
                            if not top_rating_df.empty:
                                top5_rating = [
                                    f"{row[name_col]} ({int(round(row['rating_num']))})"
                                    for _, row in top_rating_df.iterrows()
                                ]

                            # Top 5 valeur sur le marché
                            df_team["mv_num"] = pd.to_numeric(df_team[value_col], errors="coerce")
                            if df_team["mv_num"].notna().any():
                                top_value_df = (
                                    df_team.dropna(subset=["mv_num"])
                                        .sort_values("mv_num", ascending=False)
                                        .head(5)
                                )
                                items = []
                                for _, row in top_value_df.iterrows():
                                    s = format_market_value(int(round(row["mv_num"])))
                                    s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                    items.append(f"{row[name_col]} ({s})")
                                top5_value = items if items else ["Non disponible"]
                            else:
                                top_value_df = df_team.sort_values(value_col, ascending=False).head(5)
                                if not top_value_df.empty:
                                    items = []
                                    for _, row in top_value_df.iterrows():
                                        s = format_market_value(row[value_col])
                                        s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                        items.append(f"{row[name_col]} ({s})")
                                    top5_value = items

                        results_by_team[club_name] = {"display_name": team_code,"top_rating": top5_rating,"top_value": top5_value}

                    col_left, col_right = st.columns(2) # Affichage comparatif côte à côte

                    # Top 5 joueurs de la saison
                    st.markdown("""<h5 style='text-align:center;'>🏅 Top 5 joueurs de la saison</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        club1_display = results_by_team[team_names[0]]["display_name"]
                        items = results_by_team[team_names[0]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["Non disponible"]:
                            st.markdown("<p style='text-align:center;'>Non disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        club2_display = results_by_team[team_names[1]]["display_name"]
                        items = results_by_team[team_names[1]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["Non disponible"]:
                            st.markdown("<p style='text-align:center;'>Non disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # Top 5 joueurs les plus valorisés
                    st.markdown("""<h5 style='text-align:center;'>💎 Top 5 joueurs les plus valorisés</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        items = results_by_team[team_names[0]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["Non disponible"]:
                            st.markdown("<p style='text-align:center;'>Non disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        items = results_by_team[team_names[1]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["Non disponible"]:
                            st.markdown("<p style='text-align:center;'>Non disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    # Colonnes par catégorie
                    pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                    pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                    pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                    pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                    def build_radar_vs_team(cols, title, team1_s, team2_s):
                        use_cols = [c for c in cols if (c in team1_s.index) and (c in team2_s.index)]
                        if not use_cols:
                            return None

                        labels = [translate_base_stat(c.replace("score_", ""), lang="fr") for c in use_cols]

                        t1_vals = pd.to_numeric(team1_s[use_cols], errors="coerce").tolist()
                        t2_vals = pd.to_numeric(team2_s[use_cols], errors="coerce").tolist()

                        t1_vals = [0 if pd.isna(v) else float(v) for v in t1_vals]
                        t2_vals = [0 if pd.isna(v) else float(v) for v in t2_vals]

                        t1_code = str(team1_s["team_code"])
                        t2_code = str(team2_s["team_code"])

                        fig = plot_pizza_radar(labels=labels,data_values=t1_vals,median_values=t2_vals,
                            title=f"{title}: {t1_code} vs {t2_code}",legend_labels=(t1_code, t2_code))
                        return fig

                    # Constructions des 4 radars
                    fig_pizza_stat_off    = build_radar_vs_team(pizza_cols_off, "Statistiques offensives", team1_data, team2_data)
                    fig_pizza_stat_def    = build_radar_vs_team(pizza_cols_def, "Statistiques defensives", team1_data, team2_data)
                    fig_pizza_stat_style  = build_radar_vs_team(pizza_cols_style_of_play, "Performance selon le style de jeu", team1_data, team2_data)
                    fig_pizza_stat_others = build_radar_vs_team(pizza_cols_other, "Autres statistiques", team1_data, team2_data)

                    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align:center;'>Comparaison graphique</h4>", unsafe_allow_html=True)

                    # Affichage 2 x 2
                    col1, col2 = st.columns(2)
                    with col1:
                        if fig_pizza_stat_off is not None:
                            st.pyplot(fig_pizza_stat_off)
                    with col2:
                        if fig_pizza_stat_def is not None:
                            st.pyplot(fig_pizza_stat_def)

                    col3, col4 = st.columns(2)
                    with col3:
                        if fig_pizza_stat_style is not None:
                            st.pyplot(fig_pizza_stat_style)
                    with col4:
                        if fig_pizza_stat_others is not None:
                            st.pyplot(fig_pizza_stat_others)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🥊 Comparison of two teams</h4>", unsafe_allow_html=True) # Display title
            
            # Load the data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            teams_names = [''] + sorted(info_team['team_code'].dropna().unique().tolist()) # Extract the list of teams in the selected league

            team1 = st.sidebar.selectbox("First team :", [''] + teams_names, key="team1") # Selection of the 1st team

            if not team1:
                # No team selected → display intro image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                st.image(image_path)
                st.info("Expand the sidebar to select the language and teams to analyse")

            if team1:
                # We store information about the first team
                team1_data = info_team[info_team['team_code'] == team1].iloc[0] # Retrieving information from the first team

                team2_names = sorted(info_team['team_code'].dropna().unique().tolist())
                team2_names = [t for t in team2_names if t != team1]

                team2 = st.sidebar.selectbox("Second team :", [''] + team2_names, key="team2") # Selection of the 2nd team
                
                if not team2:
                    # No team selected → display intro image
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                    st.image(image_path)
                    st.info("Expand the sidebar to select the language and teams to analyse.")

                if team2:
                    team2_data = info_team[info_team['team_code'] == team2].iloc[0] # Retrieving information from the second team
                    
                    st.markdown("<h5 style='text-align: center;'>Team presentations</h4>", unsafe_allow_html=True) # The teams' profiles are displayed

                    # Column
                    df_team_col = "team_code"
                    club_col    = "club_name"
                    value_col   = "marketValue"
                    name_col    = "player_name"
                    rating_col  = "rating"

                    # Bring the two teams together
                    team_datas = [team1_data, team2_data]
                    team_codes = [str(td[df_team_col]) for td in team_datas]
                    team_names = [df_to_info.get(code, code) for code in team_codes]

                    both_teams_players = info_player[info_player[club_col].isin(team_names)].copy() # Players from both teams

                    # Aggregates by club
                    if both_teams_players.empty:
                        vals_by_team = {name: {"valeur_effectif_fmt": "Unknown", "valeur_par_joueur_fmt": "Unknown"}
                                        for name in team_names}
                    else:
                        tmp = (
                            both_teams_players.groupby(club_col, dropna=False)
                            .agg(total_value=(value_col, "sum"), n_players=(value_col, "size"))
                            .reset_index()
                        )
                        def fmt_or_unknown(v):
                            return "Unknown" if pd.isna(v) else format_market_value(v)
                        tmp["valeur_effectif_fmt"]   = tmp["total_value"].apply(fmt_or_unknown)
                        tmp["valeur_par_joueur_fmt"] = (tmp["total_value"] / tmp["n_players"]).apply(
                            lambda v: "Unknown" if not np.isfinite(v) else format_market_value(v)
                        )
                        vals_by_team = {
                            row[club_col]: {
                                "valeur_effectif_fmt": row["valeur_effectif_fmt"],
                                "valeur_par_joueur_fmt": row["valeur_par_joueur_fmt"],
                            } for _, row in tmp.iterrows()
                        }
                        for name in team_names:
                            vals_by_team.setdefault(name, {"valeur_effectif_fmt": "Unknown", "valeur_par_joueur_fmt": "Unknown"})

                    # Styles by team
                    styles_by_team = {}
                    for td, club_name in zip(team_datas, team_names):
                        style_dict = estimate_team_styles(td)
                        styles_by_team[club_name] = {
                            "off": style_dict["offensive_style"],
                            "def": style_dict["defensive_style"],
                        }

                    # Displaying
                    for td in team_datas:
                        key = str(td[df_team_col])

                        club_name = df_to_info.get(key, key)

                        valeur_par_joueur_fmt = vals_by_team.get(club_name, {}).get("valeur_par_joueur_fmt", "Unknown")
                        off_label = styles_by_team.get(club_name, {}).get("off", "Unknown")
                        def_label = styles_by_team.get(club_name, {}).get("def", "Unknown")

                        pts_league = int(td["pts_league"]) if pd.notna(td["pts_league"]) else "-"
                        taille_effectif = int(td["players"]) if pd.notna(td["players"]) else "-"
                        salaire_annuel = format_market_value(td["Annual Wages"]) if "Annual Wages" in td else "Unknown"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{td['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Name :</strong> {td['team_code']}</p>
                            <p><strong>League :</strong> {td['championship_name']}</p>
                            <p><strong>Country :</strong> {td["country"]}</p>
                            <p><strong>Power Ranking :</strong> {td['rank_big5']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Ranking :</strong> {td['rank_league']}</p>
                            <p><strong>Pts :</strong> {pts_league}</p>
                            <p><strong>Offensive playing style :</strong> {off_label}</p>
                            <p><strong>Defensive playing style :</strong> {def_label}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Average age :</strong> {td['age']}</p>
                            <p><strong>Effective size :</strong> {taille_effectif}</p>
                            <p><strong>Value of squad :</strong> {valeur_par_joueur_fmt}</p>
                            <p><strong>Annual salary :</strong> {salaire_annuel}</p>
                        </div>

                        </div>
                        """, unsafe_allow_html=True)

                    # Team-based construction of tops
                    results_by_team = {}

                    for td, club_map_name in zip(team_datas, team_names):
                        # Display name and filter key
                        team_code = str(td[df_team_col])
                        club_name = df_to_info.get(team_code, team_code)

                        # By default
                        top5_rating = ["Not available"]
                        top5_value  = ["Not available"]

                        df_team = both_teams_players[both_teams_players[club_col] == club_name].copy()
                        if not df_team.empty and {name_col, rating_col, value_col}.issubset(df_team.columns):

                            # Top 5 rating
                            df_team["rating_num"] = pd.to_numeric(df_team[rating_col], errors="coerce")
                            top_rating_df = (
                                df_team.dropna(subset=["rating_num"])
                                    .sort_values("rating_num", ascending=False)
                                    .head(5)
                            )
                            if not top_rating_df.empty:
                                top5_rating = [
                                    f"{row[name_col]} ({int(round(row['rating_num']))})"
                                    for _, row in top_rating_df.iterrows()
                                ]

                            # Top 5 value on the market
                            df_team["mv_num"] = pd.to_numeric(df_team[value_col], errors="coerce")
                            if df_team["mv_num"].notna().any():
                                top_value_df = (
                                    df_team.dropna(subset=["mv_num"])
                                        .sort_values("mv_num", ascending=False)
                                        .head(5)
                                )
                                items = []
                                for _, row in top_value_df.iterrows():
                                    s = format_market_value(int(round(row["mv_num"])))
                                    s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                    items.append(f"{row[name_col]} ({s})")
                                top5_value = items if items else ["Not available"]
                            else:
                                top_value_df = df_team.sort_values(value_col, ascending=False).head(5)
                                if not top_value_df.empty:
                                    items = []
                                    for _, row in top_value_df.iterrows():
                                        s = format_market_value(row[value_col])
                                        s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                        items.append(f"{row[name_col]} ({s})")
                                    top5_value = items

                        results_by_team[club_name] = {"display_name": team_code,"top_rating": top5_rating,"top_value": top5_value}

                    col_left, col_right = st.columns(2) # Side-by-side comparison display

                    # Top 5 players of the season
                    st.markdown("""<h5 style='text-align:center;'>🏅 Top 5 players of the season</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        club1_display = results_by_team[team_names[0]]["display_name"]
                        items = results_by_team[team_names[0]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["Not available"]:
                            st.markdown("<p style='text-align:center;'>Not available</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        club2_display = results_by_team[team_names[1]]["display_name"]
                        items = results_by_team[team_names[1]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["Not available"]:
                            st.markdown("<p style='text-align:center;'>Not available</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # Top 5 most valuable players
                    st.markdown("""<h5 style='text-align:center;'>💎 Top 5 most valuable players</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        items = results_by_team[team_names[0]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["Not available"]:
                            st.markdown("<p style='text-align:center;'>Not available</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        items = results_by_team[team_names[1]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["Not available"]:
                            st.markdown("<p style='text-align:center;'>Not available</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    # Columns by category
                    pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                    pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                    pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                    pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                    def build_radar_vs_team(cols, title, team1_s, team2_s):
                        use_cols = [c for c in cols if (c in team1_s.index) and (c in team2_s.index)]
                        if not use_cols:
                            return None

                        labels = [translate_base_stat(c.replace("score_", ""), lang="eng") for c in use_cols]

                        t1_vals = pd.to_numeric(team1_s[use_cols], errors="coerce").tolist()
                        t2_vals = pd.to_numeric(team2_s[use_cols], errors="coerce").tolist()

                        t1_vals = [0 if pd.isna(v) else float(v) for v in t1_vals]
                        t2_vals = [0 if pd.isna(v) else float(v) for v in t2_vals]

                        t1_code = str(team1_s["team_code"])
                        t2_code = str(team2_s["team_code"])

                        fig = plot_pizza_radar(labels=labels,data_values=t1_vals,median_values=t2_vals,
                            title=f"{title}: {t1_code} vs {t2_code}",legend_labels=(t1_code, t2_code))
                        return fig

                    # Construction of the four radars
                    fig_pizza_stat_off    = build_radar_vs_team(pizza_cols_off, "Offensive statistics", team1_data, team2_data)
                    fig_pizza_stat_def    = build_radar_vs_team(pizza_cols_def, "Defensive statistics", team1_data, team2_data)
                    fig_pizza_stat_style  = build_radar_vs_team(pizza_cols_style_of_play, "Performance according to playing style", team1_data, team2_data)
                    fig_pizza_stat_others = build_radar_vs_team(pizza_cols_other, "Other statistics", team1_data, team2_data)

                    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align:center;'>Graphical comparison</h4>", unsafe_allow_html=True)

                    # 2 x 2 display
                    col1, col2 = st.columns(2)
                    with col1:
                        if fig_pizza_stat_off is not None:
                            st.pyplot(fig_pizza_stat_off)
                    with col2:
                        if fig_pizza_stat_def is not None:
                            st.pyplot(fig_pizza_stat_def)

                    col3, col4 = st.columns(2)
                    with col3:
                        if fig_pizza_stat_style is not None:
                            st.pyplot(fig_pizza_stat_style)
                    with col4:
                        if fig_pizza_stat_others is not None:
                            st.pyplot(fig_pizza_stat_others)

        else:
            st.markdown("<h4 style='text-align: center;'>🥊 Comparación entre dos equipos</h4>", unsafe_allow_html=True) # Visualización del título
            
            # Cargar los datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            info_player = pd.read_csv(player_path)
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            teams_names = [''] + sorted(info_team['team_code'].dropna().unique().tolist()) # Extraer la lista de equipos de la liga seleccionada

            team1 = st.sidebar.selectbox("Primer equipo :", [''] + teams_names, key="team1") # Selección del primer equipo
            if not team1:
                # No hay ningún equipo seleccionado → mostrar la imagen de introducción
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma y los equipos que deseas analizar")

            if team1:
                # Almacenamos la información del primer equipo
                team1_data = info_team[info_team['team_code'] == team1].iloc[0] # Recopilación de información del primer equipo

                team2_names = sorted(info_team['team_code'].dropna().unique().tolist())
                team2_names = [t for t in team2_names if t != team1]

                team2 = st.sidebar.selectbox("Segundo equipo :", [''] + team2_names, key="team2") # Selección del segundo equipo
                
                if not team2:
                    # No hay ningún equipo seleccionado → mostrar la imagen de introducción
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_comparison.jpg")
                    st.image(image_path)
                    st.info("Despliega la barra lateral para seleccionar el idioma y los equipos que deseas analizar")

                if team2:
                    team2_data = info_team[info_team['team_code'] == team2].iloc[0] # Recopilación de información del segundo equipo
                    
                    st.markdown("<h5 style='text-align: center;'>Team presentations</h4>", unsafe_allow_html=True) # Se muestra el perfil de los equipos

                    # Columnas
                    df_team_col = "team_code"
                    club_col    = "club_name"
                    value_col   = "marketValue"
                    name_col    = "player_name"
                    rating_col  = "rating"

                    # Reunir a los dos equipos
                    team_datas = [team1_data, team2_data]
                    team_codes = [str(td[df_team_col]) for td in team_datas]
                    team_names = [df_to_info.get(code, code) for code in team_codes]

                    both_teams_players = info_player[info_player[club_col].isin(team_names)].copy() # Jugadores de ambos equipos

                    # Agregados por club
                    if both_teams_players.empty:
                        vals_by_team = {name: {"valeur_effectif_fmt": "Desconocido", "valeur_par_joueur_fmt": "Desconocido"}
                                        for name in team_names}
                    else:
                        tmp = (
                            both_teams_players.groupby(club_col, dropna=False)
                            .agg(total_value=(value_col, "sum"), n_players=(value_col, "size"))
                            .reset_index()
                        )
                        def fmt_or_unknown(v):
                            return "Desconocido" if pd.isna(v) else format_market_value(v)
                        tmp["valeur_effectif_fmt"]   = tmp["total_value"].apply(fmt_or_unknown)
                        tmp["valeur_par_joueur_fmt"] = (tmp["total_value"] / tmp["n_players"]).apply(
                            lambda v: "Desconocido" if not np.isfinite(v) else format_market_value(v)
                        )
                        vals_by_team = {
                            row[club_col]: {
                                "valeur_effectif_fmt": row["valeur_effectif_fmt"],
                                "valeur_par_joueur_fmt": row["valeur_par_joueur_fmt"],
                            } for _, row in tmp.iterrows()
                        }
                        for name in team_names:
                            vals_by_team.setdefault(name, {"valeur_effectif_fmt": "Desconocido", "valeur_par_joueur_fmt": "Desconocido"})

                    # Estilos por equipo
                    styles_by_team = {}
                    for td, club_name in zip(team_datas, team_names):
                        style_dict = estimate_team_styles(td)
                        styles_by_team[club_name] = {
                            "off": translate_style(style_dict["offensive_style"], lang="es"),
                            "def": translate_style(style_dict["defensive_style"], lang="es"),
                        }

                    # Visualización
                    for td in team_datas:
                        key = str(td[df_team_col])

                        pays = translate_country(td["country"], lang="es")
                        club_name = df_to_info.get(key, key)

                        valeur_par_joueur_fmt = vals_by_team.get(club_name, {}).get("valeur_par_joueur_fmt", "Desconocido")
                        off_label = styles_by_team.get(club_name, {}).get("off", "Desconocido")
                        def_label = styles_by_team.get(club_name, {}).get("def", "Desconocido")

                        pts_league = int(td["pts_league"]) if pd.notna(td["pts_league"]) else "-"
                        taille_effectif = int(td["players"]) if pd.notna(td["players"]) else "-"
                        salaire_annuel = format_market_value(td["Annual Wages"]) if "Annual Wages" in td else "Desconocido"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{td['team_logo']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Nombre :</strong> {td['team_code']}</p>
                            <p><strong>Liga :</strong> {td['championship_name']}</p>
                            <p><strong>País :</strong> {pays}</p>
                            <p><strong>Power Ranking :</strong> {td['rank_big5']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Clasificación :</strong> {td['rank_league']}</p>
                            <p><strong>Pts :</strong> {pts_league}</p>
                            <p><strong>Estilo de juego Ofensivo :</strong> {off_label}</p>
                            <p><strong>Estilo de juego Defensivo :</strong> {def_label}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Edad media :</strong> {td['age']}</p>
                            <p><strong>Tamaño efectivo :</strong> {taille_effectif}</p>
                            <p><strong>Valor por jugador :</strong> {valeur_par_joueur_fmt}</p>
                            <p><strong>Salario anual :</strong> {salaire_annuel}</p>
                        </div>

                        </div>
                        """, unsafe_allow_html=True)

                    # Construcción de los tops por equipos
                    results_by_team = {}

                    for td, club_map_name in zip(team_datas, team_names):
                        # Nombre mostrado y clave de filtro
                        team_code = str(td[df_team_col])
                        club_name = df_to_info.get(team_code, team_code)

                        # Por defecto
                        top5_rating = ["No disponible"]
                        top5_value  = ["No disponible"]

                        df_team = both_teams_players[both_teams_players[club_col] == club_name].copy()
                        if not df_team.empty and {name_col, rating_col, value_col}.issubset(df_team.columns):

                            # Top 5 rating
                            df_team["rating_num"] = pd.to_numeric(df_team[rating_col], errors="coerce")
                            top_rating_df = (
                                df_team.dropna(subset=["rating_num"])
                                    .sort_values("rating_num", ascending=False)
                                    .head(5)
                            )
                            if not top_rating_df.empty:
                                top5_rating = [
                                    f"{row[name_col]} ({int(round(row['rating_num']))})"
                                    for _, row in top_rating_df.iterrows()
                                ]

                            # Top 5 valor en el mercado
                            df_team["mv_num"] = pd.to_numeric(df_team[value_col], errors="coerce")
                            if df_team["mv_num"].notna().any():
                                top_value_df = (
                                    df_team.dropna(subset=["mv_num"])
                                        .sort_values("mv_num", ascending=False)
                                        .head(5)
                                )
                                items = []
                                for _, row in top_value_df.iterrows():
                                    s = format_market_value(int(round(row["mv_num"])))
                                    s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                    items.append(f"{row[name_col]} ({s})")
                                top5_value = items if items else ["No disponible"]
                            else:
                                top_value_df = df_team.sort_values(value_col, ascending=False).head(5)
                                if not top_value_df.empty:
                                    items = []
                                    for _, row in top_value_df.iterrows():
                                        s = format_market_value(row[value_col])
                                        s = re.sub(r'(\d+)\.0(?=\s*[A-Za-z€])', r'\1', s)
                                        items.append(f"{row[name_col]} ({s})")
                                    top5_value = items

                        results_by_team[club_name] = {"display_name": team_code,"top_rating": top5_rating,"top_value": top5_value}

                    col_left, col_right = st.columns(2) # Visualización comparativa en paralelo

                    # Los 5 mejores jugadores de la temporada
                    st.markdown("""<h5 style='text-align:center;'>🏅 Los 5 mejores jugadores de la temporada</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        club1_display = results_by_team[team_names[0]]["display_name"]
                        items = results_by_team[team_names[0]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["No disponible"]:
                            st.markdown("<p style='text-align:center;'>No disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        club2_display = results_by_team[team_names[1]]["display_name"]
                        items = results_by_team[team_names[1]]["top_rating"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["No disponible"]:
                            st.markdown("<p style='text-align:center;'>No disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # Los 5 jugadores más valorados
                    st.markdown("""<h5 style='text-align:center;'>💎 Los 5 jugadores más valorados</h5>""", unsafe_allow_html=True)

                    col_left, col_right = st.columns(2)

                    with col_left:
                        items = results_by_team[team_names[0]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club1_display}</h6>", unsafe_allow_html=True)
                        if items == ["No disponible"]:
                            st.markdown("<p style='text-align:center;'>No disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    with col_right:
                        items = results_by_team[team_names[1]]["top_value"]
                        st.markdown(f"<h6 style='text-align:center;'>{club2_display}</h6>", unsafe_allow_html=True)
                        if items == ["No disponible"]:
                            st.markdown("<p style='text-align:center;'>No disponible</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='text-align:center;'>" + "<br>".join([f"• {x}" for x in items]) + "</div>",
                                unsafe_allow_html=True
                            )

                    # Columnas por categoría
                    pizza_cols_off = ["score_goal_scoring_created", "score_finish", "score_set_pieces_off","score_building", "score_projection", "score_crosses", "score_dribble"]
                    pizza_cols_def = ["score_goal_scoring_conceded", "score_defensive_actions","score_set_pieces_def", "score_efficiency_goalkeeper"]
                    pizza_cols_style_of_play = ["score_possession", "score_direct_play", "score_counter-attacking","score_pressing"]
                    pizza_cols_other = ["score_rank_league", "score_ground_duel", "score_aerial","score_provoked_fouls", "score_faults_committed", "score_waste", "score_subs"]

                    def build_radar_vs_team(cols, title, team1_s, team2_s):
                        use_cols = [c for c in cols if (c in team1_s.index) and (c in team2_s.index)]
                        if not use_cols:
                            return None

                        labels = [translate_base_stat(c.replace("score_", ""), lang="es") for c in use_cols]

                        t1_vals = pd.to_numeric(team1_s[use_cols], errors="coerce").tolist()
                        t2_vals = pd.to_numeric(team2_s[use_cols], errors="coerce").tolist()

                        t1_vals = [0 if pd.isna(v) else float(v) for v in t1_vals]
                        t2_vals = [0 if pd.isna(v) else float(v) for v in t2_vals]

                        t1_code = str(team1_s["team_code"])
                        t2_code = str(team2_s["team_code"])

                        fig = plot_pizza_radar(labels=labels,data_values=t1_vals,median_values=t2_vals,
                            title=f"{title}: {t1_code} vs {t2_code}",legend_labels=(t1_code, t2_code))
                        return fig

                    # Construcción de los 4 radares
                    fig_pizza_stat_off    = build_radar_vs_team(pizza_cols_off, "Estadísticas ofensivas", team1_data, team2_data)
                    fig_pizza_stat_def    = build_radar_vs_team(pizza_cols_def, "Estadísticas defensivas", team1_data, team2_data)
                    fig_pizza_stat_style  = build_radar_vs_team(pizza_cols_style_of_play, "Rendimiento según el estilo de juego", team1_data, team2_data)
                    fig_pizza_stat_others = build_radar_vs_team(pizza_cols_other, "Otras estadísticas", team1_data, team2_data)

                    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align:center;'>Comparación gráfica</h4>", unsafe_allow_html=True)

                    #  Pantalla 2 x 2
                    col1, col2 = st.columns(2)
                    with col1:
                        if fig_pizza_stat_off is not None:
                            st.pyplot(fig_pizza_stat_off)
                    with col2:
                        if fig_pizza_stat_def is not None:
                            st.pyplot(fig_pizza_stat_def)

                    col3, col4 = st.columns(2)
                    with col3:
                        if fig_pizza_stat_style is not None:
                            st.pyplot(fig_pizza_stat_style)
                    with col4:
                        if fig_pizza_stat_others is not None:
                            st.pyplot(fig_pizza_stat_others)

    elif selected == "Stats +":
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏅 Classement des équipes (0-100) pour les statistiques aggrégées par catégorie </h4>", unsafe_allow_html=True) # Affichage du titre de la page
            # Récupération des données
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)
            # Récupération des colonnes "score_" + "rating"
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            fr_map = base_stat_translation.get("fr", {}) # Traduction pour l'affichage

            translated_stats = [
                "Note" if col == "rating"
                else fr_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))
            
            selected_stat_display = st.sidebar.selectbox("Choisissez une statistique :", [""] + translated_stats) # Demande à l'utilisateur du choix de statistique
            
            selected_stat = stat_name_mapping.get(selected_stat_display, None)

            if not selected_stat:
                # Si la métrique est selectionné, nous cachons l'image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking_basis.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")
                    
            if selected_stat:
                # Début de la sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filtres")
                    
                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                    filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                    # Filtre Championnat
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("Championnat", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filtre Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # Liste de colonnes
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])

                df_stat['country'] = df_stat['country'].apply(lambda x: translate_country(x, lang="fr")) # Traduction du pays de l'équipe dans la table
                
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Ordonner les données du plus grand au plus petit

                top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

                # Ordre podium et médailles
                podium_order = [0, 1, 2]
                medals = ["🥇","🥈", "🥉"]

                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        stat = round(team[selected_stat]) if pd.notna(team[selected_stat]) else "-"
                        image_url = team['team_logo']
                        image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                        team_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                            "</div>"
                        )
                        podium_html += team_html

                podium_html += "</div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # Choix des colonnes dans la table
                final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
                final_df = final_df[['team_code', 'Statistique', 'championship_name', 'country', 'rank_big5', 'rank_league']]

                # Traduction des colonnes en français
                col_labels_fr = {"team_code": "Équipe","Statistique": "Statistique","championship_name": "Championnat",
                "country": "Pays","rank_big5": "Power Ranking","rank_league": "Classement (Championnat)"}
                final_df = final_df.rename(columns=col_labels_fr)

                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🏅 Team rankings (0-100) for aggregated statistics by category </h4>", unsafe_allow_html=True) # Displaying the page title
            # Load the data
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)
            # Retrieval of the ‘score_’ + ‘rating’ columns
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            fr_map = base_stat_translation.get("eng", {}) # Translation for display

            translated_stats = [
                "Rating" if col == "rating"
                else fr_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))
            
            selected_stat_display = st.sidebar.selectbox("Select a statistic :", [""] + translated_stats) # Ask the user to choose statistics
            
            selected_stat = stat_name_mapping.get(selected_stat_display, None)

            if not selected_stat:
                # If the metric is selected, we hide the image.
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking_basis.jpg")
                st.image(image_path)
                st.info("Expand the sidebar to select your preferred language, metric, and filters")
                    
            if selected_stat:
                # Start of sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filters")
                    
                    df_with_stat = df.dropna(subset=[selected_stat]) # Filter according to the selected statistic

                    filtered_df = df_with_stat.copy()  # Starting point for filters

                    # Filter League
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("League", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filter Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # List of columns
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])
                
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Sort data from largest to smallest

                top3 = df_stat.head(3).reset_index(drop=True) # Podium display

                # Podium order and medals
                podium_order = [0, 1, 2]
                medals = ["🥇","🥈", "🥉"]

                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        stat = round(team[selected_stat]) if pd.notna(team[selected_stat]) else "-"
                        image_url = team['team_logo']
                        image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                        team_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                            "</div>"
                        )
                        podium_html += team_html

                podium_html += "</div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # Choosing columns in the table
                final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
                final_df = final_df[['team_code', 'Statistic', 'championship_name', 'country', 'rank_big5', 'rank_league']]
                col_labels_en = {"team_code": "Team","Statistic": "Statistic","championship_name": "League","country": "Country","rank_big5": "Power Ranking","rank_league": "League Standing"}
                final_df = final_df.rename(columns=col_labels_en)

                st.dataframe(final_df, use_container_width=True)

        else:
            st.markdown("<h4 style='text-align: center;'>🏅 Clasificación de equipos (0-100) para estadísticas agregadas por categoría </h4>", unsafe_allow_html=True) # Mostrar el título de la página
            # Recuperación de datos
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)
            # Recuperación de las columnas «score_» + «rating»
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            fr_map = base_stat_translation.get("es", {}) # Traducción para visualización

            translated_stats = [
                "Nota" if col == "rating"
                else fr_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))
            
            selected_stat_display = st.sidebar.selectbox("Elija una estadística :", [""] + translated_stats) # Solicita al usuario la elección de estadísticas
            
            selected_stat = stat_name_mapping.get(selected_stat_display, None)

            if not selected_stat:
                # Si se selecciona la métrica, ocultamos la imagen.
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking_basis.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma, la métrica y los filtros que desees")
                    
            if selected_stat:
                # Inicio de la barra lateral
                with st.sidebar:
                    st.markdown("### 🎯 Filtros")
                    
                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtrar según la estadística seleccionada

                    filtered_df = df_with_stat.copy()  # Punto de partida para los filtros

                    # Filtro Liga
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("Liga", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filtro Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # Lista de columnas
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])

                df_stat['country'] = df_stat['country'].apply(lambda x: translate_country(x, lang="es")) # Traducción del país del equipo en la tabla
                
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Ordenar los datos de mayor a menor

                top3 = df_stat.head(3).reset_index(drop=True) # Visualización del podio

                # Orden del podio y medallas
                podium_order = [0, 1, 2]
                medals = ["🥇","🥈", "🥉"]

                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        stat = round(team[selected_stat]) if pd.notna(team[selected_stat]) else "-"
                        image_url = team['team_logo']
                        image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                        team_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                            "</div>"
                        )
                        podium_html += team_html

                podium_html += "</div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # Selección de columnas en la tabla
                final_df = df_stat.rename(columns={selected_stat: 'Estadística'})
                final_df = final_df[['team_code', 'Estadística', 'championship_name', 'country', 'rank_big5', 'rank_league']]
                col_labels_es = {"team_code": "Equipo","Estadística": "Estadística","championship_name": "Liga","country": "País","rank_big5": "Power Ranking","rank_league": "Clasificación (Liga)"}
                final_df = final_df.rename(columns=col_labels_es)
                st.dataframe(final_df, use_container_width=True)

    elif selected == "Stats":
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏆 Classement des équipes pour les statistiques brutes</h4>", unsafe_allow_html=True) # Affichage du titre de la page
            # Récupération des données
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)

            categories_en = list(stats_team.keys()) # Catégories
            categories_fr = [translate_categories_stats(c, "fr") for c in categories_en] # Libellés FR affichés
            cat_display_to_key = dict(zip(categories_fr, categories_en))
            display_options = [""] + categories_fr + ["Toutes les catégories"]

            selected_category_display = st.sidebar.selectbox("Choisissez une catégorie :", display_options) # On choisit la catégorie de son choix

            # Choix de la catégorie
            if selected_category_display == "":
                available_stats = []
            elif selected_category_display == "Toutes les catégories":
                available_stats = sorted({s for stats in stats_team.values() for s in stats if s in df.columns})
            else:
                selected_key = cat_display_to_key[selected_category_display]
                available_stats = sorted([s for s in stats_team[selected_key] if s in df.columns])

            if available_stats:
                options = [""] + [get_stat_display_name(s) for s in available_stats]
                selected_label = st.sidebar.selectbox("Choisissez une statistique :", options)

                if selected_label:
                    label_to_key = {get_stat_display_name(s): s for s in available_stats}
                    selected_stat = label_to_key[selected_label]
                else:
                    selected_stat = ""
            else:
                selected_stat = ""

            if not selected_stat:
                # Si la métrique est selectionné, nous cachons l'image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")
                    
            if selected_stat:
                # Début de la sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filtres")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                    filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                    # Filtre Championnat
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("Championnat", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filtre Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # Déterminer les catégories à afficher dans le glossaire
                if selected_category_display == "":
                    cats_to_show = []
                elif selected_category_display == "Toutes les catégories":
                    cats_to_show = list(stats_team.keys())
                else:
                    cats_to_show = [cat_display_to_key[selected_category_display]]

                # Affichage du glossaire
                with st.sidebar.expander("Glossaire des statistiques"):
                    if selected_category_display == "":
                        st.markdown("Sélectionnez une catégorie pour afficher le glossaire correspondant")
                    else:
                        cats_to_show = (
                            list(stats_team.keys())
                            if selected_category_display == "Toutes les catégories"
                            else [cat_display_to_key[selected_category_display]]
                        )

                        for cat_key in cats_to_show:
                            cat_title_fr = translate_categories_stats(cat_key, "fr").upper() # Titre de catégorie en FR
                            st.markdown(f"### {cat_title_fr}")

                            stats_in_cat = [s for s in stats_team[cat_key] if s in df.columns] # Stats présentes dans le dataframe
                            if not stats_in_cat:
                                st.markdown("Aucune statistique disponible pour cette catégorie dans les données chargées.")
                                continue

                            # Liste des définitions en FR
                            lines = []
                            for s in stats_in_cat:
                                label = get_stat_display_name(s)
                                definition = get_definition(s, "fr")
                                lines.append(f"- **{label}** : {definition}")

                            st.markdown("\n".join(lines))

                # Liste de colonnes
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])

                df_stat['country'] = df_stat['country'].apply(lambda x: translate_country(x, lang="fr")) # Traduction du pays dans la table

                # Métriques à trier du plus petit au plus grand
                ascending_metrics = {
                    "carries_dis","carries_mis","Per_90_min_carries_dis","Per_90_min_carries_mis","pressing__ppda","defending_set_pieces__goals","defending_set_pieces__shots",
                    "defending_set_pieces__xg","misc.__pens_conceded","performance_crdr","performance_crdy","performance_fls","misc.__fouls","misc.__reds","misc.__yellows",
                    "performance_l","blocks_err","misc.__errors_lead_to_goal","misc.__errors_lead_to_shot","defending_misc__fast_breaks__goals","defending_misc__fast_breaks__total",
                    "defending_misc__headers__goals","defending_misc__headers__total","hit_post_conceded_per90","defending_misc__offsides","defending_misc__touches_in_box",
                    "defending_overall__conv_pct","defending_overall__goals","defending_overall__goals_vs_xg","defending_overall__shots","defending_overall__sot","defending_overall__xg",
                    "defending_overall__xg_per_shot",
                }

                ascending = selected_stat in ascending_metrics
                df_stat = df_stat.sort_values(by=selected_stat, ascending=ascending)

                top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        image_url = team['team_logo']
                        stat_val = round(team[selected_stat], 2) if pd.notna(team[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        team_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'></strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += team_html

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                stat_col_label = get_stat_display_name(selected_stat) # Choix des colonnes dans la table

                final_df = df_stat.rename(columns={selected_stat: stat_col_label})
                final_df = final_df[['team_code', stat_col_label, 'championship_name', 'country', 'rank_big5', 'rank_league']]

                # Traduction des colonnes en français
                col_labels_fr = {"team_code": "Équipe","championship_name": "Championnat","country": "Pays","rank_big5": "Power Ranking","rank_league": "Classement (Championnat)"}
                final_df = final_df.rename(columns=col_labels_fr)
                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🏆 Team rankings for raw statistics</h4>", unsafe_allow_html=True) # Displaying the page title
            # Data recovery
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)

            categories_en = list(stats_team.keys()) # Category
            cat_display_to_key = dict(zip(categories_en, categories_en))
            display_options = [""] + categories_en + ["All categories"]

            selected_category_display = st.sidebar.selectbox("Select a category :", display_options) # You choose the category of your choice.

            # Category selection
            if selected_category_display == "":
                available_stats = []
            elif selected_category_display == "All categories":
                available_stats = sorted({s for stats in stats_team.values() for s in stats if s in df.columns})
            else:
                selected_key = cat_display_to_key[selected_category_display]
                available_stats = sorted([s for s in stats_team[selected_key] if s in df.columns])

            if available_stats:
                options = [""] + [get_stat_display_name(s) for s in available_stats]
                selected_label = st.sidebar.selectbox("Select a statistic :", options)

                if selected_label:
                    label_to_key = {get_stat_display_name(s): s for s in available_stats}
                    selected_stat = label_to_key[selected_label]
                else:
                    selected_stat = ""
            else:
                selected_stat = ""

            if not selected_stat:
                # If the metric is selected, we hide the image.
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking.jpg")
                st.image(image_path)
                st.info("Expand the sidebar to select your preferred language, metric, and filters.")
                    
            if selected_stat:
                # Start of sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filters")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filter according to the selected statistic

                    filtered_df = df_with_stat.copy()  # Starting point for filters

                    # Filter League
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("League", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filter Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # Determine which categories to display in the glossary
                if selected_category_display == "":
                    cats_to_show = []
                elif selected_category_display == "All categories":
                    cats_to_show = list(stats_team.keys())
                else:
                    cats_to_show = [cat_display_to_key[selected_category_display]]

                # Displaying the glossary
                with st.sidebar.expander("Glossary of statistics"):
                    if selected_category_display == "":
                        st.markdown("Select a category to display the corresponding glossary")
                    else:
                        cats_to_show = (
                            list(stats_team.keys())
                            if selected_category_display == "All categories"
                            else [cat_display_to_key[selected_category_display]]
                        )

                        for cat_key in cats_to_show:
                            st.markdown(f"### {cat_key}") # Category title in English

                            stats_in_cat = [s for s in stats_team[cat_key] if s in df.columns] # Stats present in the dataframe
                            if not stats_in_cat:
                                st.markdown("No statistics available for this category in the loaded data.")
                                continue

                            # List of definitions in English
                            lines = []
                            for s in stats_in_cat:
                                label = get_stat_display_name(s)
                                definition = get_definition(s, "eng")
                                lines.append(f"- **{label}** : {definition}")

                            st.markdown("\n".join(lines))

                # List of columns
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])

                # Metrics to sort from smallest to largest
                ascending_metrics = {
                    "carries_dis","carries_mis","Per_90_min_carries_dis","Per_90_min_carries_mis","pressing__ppda","defending_set_pieces__goals","defending_set_pieces__shots",
                    "defending_set_pieces__xg","misc.__pens_conceded","performance_crdr","performance_crdy","performance_fls","misc.__fouls","misc.__reds","misc.__yellows",
                    "performance_l","blocks_err","misc.__errors_lead_to_goal","misc.__errors_lead_to_shot","defending_misc__fast_breaks__goals","defending_misc__fast_breaks__total",
                    "defending_misc__headers__goals","defending_misc__headers__total","hit_post_conceded_per90","defending_misc__offsides","defending_misc__touches_in_box",
                    "defending_overall__conv_pct","defending_overall__goals","defending_overall__goals_vs_xg","defending_overall__shots","defending_overall__sot","defending_overall__xg",
                    "defending_overall__xg_per_shot",
                }

                ascending = selected_stat in ascending_metrics
                df_stat = df_stat.sort_values(by=selected_stat, ascending=ascending)

                top3 = df_stat.head(3).reset_index(drop=True) # Podium display

                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        image_url = team['team_logo']
                        stat_val = round(team[selected_stat], 2) if pd.notna(team[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        team_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'></strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += team_html

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                stat_col_label = get_stat_display_name(selected_stat) # Choosing columns in the table

                final_df = df_stat.rename(columns={selected_stat: stat_col_label})
                final_df = final_df[['team_code', stat_col_label, 'championship_name', 'country', 'rank_big5', 'rank_league']] # Translation of columns into English
                col_labels_eng = {"team_code": "Team","championship_name": "League","country": "Country","rank_big5": "Power Ranking","rank_league": "League Standing"}
                final_df = final_df.rename(columns=col_labels_eng)
                st.dataframe(final_df, use_container_width=True)

        else:
            st.markdown("<h4 style='text-align: center;'>🏆 Clasificación de equipos según estadísticas brutas</h4>", unsafe_allow_html=True) # Mostrar el título de la página
            # Recuperación de datos
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            df = pd.read_csv(team_path)

            categories_en = list(stats_team.keys()) # Categorías
            categories_es = [translate_categories_stats(c, "es") for c in categories_en] # Etiquetas ES mostradas
            cat_display_to_key = dict(zip(categories_es, categories_en))
            display_options = [""] + categories_es + ["Todas las categorías"]

            selected_category_display = st.sidebar.selectbox("Elige una categoría :", display_options) # Se elige la categoría que se desee.

            # Selección de categoría
            if selected_category_display == "":
                available_stats = []
            elif selected_category_display == "Todas las categorías":
                available_stats = sorted({s for stats in stats_team.values() for s in stats if s in df.columns})
            else:
                selected_key = cat_display_to_key[selected_category_display]
                available_stats = sorted([s for s in stats_team[selected_key] if s in df.columns])

            if available_stats:
                options = [""] + [get_stat_display_name(s) for s in available_stats]
                selected_label = st.sidebar.selectbox("Elige una estadística :", options)

                if selected_label:
                    label_to_key = {get_stat_display_name(s): s for s in available_stats}
                    selected_stat = label_to_key[selected_label]
                else:
                    selected_stat = ""
            else:
                selected_stat = ""

            if not selected_stat:
                # Si se selecciona la métrica, ocultamos la imagen.
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "team_ranking.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma, la métrica y los filtros que desees")
                    
            if selected_stat:
                # Inicio de la barra lateral
                with st.sidebar:
                    st.markdown("### 🎯 Filtros")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtrar según la estadística seleccionada

                    filtered_df = df_with_stat.copy()  # Punto de partida para los filtros

                    # Filtro Liga
                    championnat_options = sorted(filtered_df["championship_name"].dropna().unique())
                    championnat = st.selectbox("Liga", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["championship_name"] == championnat]

                    # Filtro Club
                    club_options = sorted(filtered_df["team_code"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["team_code"] == club]

                # Determinar las categorías que se mostrarán en el glosario
                if selected_category_display == "":
                    cats_to_show = []
                elif selected_category_display == "Todas las categorías":
                    cats_to_show = list(stats_team.keys())
                else:
                    cats_to_show = [cat_display_to_key[selected_category_display]]

                # Visualización del glosario
                with st.sidebar.expander("Glosario de estadísticas"):
                    if selected_category_display == "":
                        st.markdown("Seleccione una categoría para ver el glosario correspondiente")
                    else:
                        cats_to_show = (
                            list(stats_team.keys())
                            if selected_category_display == "Todas las categorías"
                            else [cat_display_to_key[selected_category_display]]
                        )

                        for cat_key in cats_to_show:
                            cat_title_es = translate_categories_stats(cat_key, "es").upper() # Título de categoría en ES
                            st.markdown(f"### {cat_title_es}")

                            stats_in_cat = [s for s in stats_team[cat_key] if s in df.columns] # Estadísticas presentes en el marco de datos
                            if not stats_in_cat:
                                st.markdown("No hay estadísticas disponibles para esta categoría en los datos cargados.")
                                continue

                            # Lista de definiciones en español
                            lines = []
                            for s in stats_in_cat:
                                label = get_stat_display_name(s)
                                definition = get_definition(s, "es")
                                lines.append(f"- **{label}** : {definition}")

                            st.markdown("\n".join(lines))

                # Lista de columnas
                df_stat = filtered_df[['team_code', 'team_logo', 'championship_name', 'country','rank_big5', 'rank_league', selected_stat]].dropna(subset=[selected_stat])

                df_stat['country'] = df_stat['country'].apply(lambda x: translate_country(x, lang="es")) # Traducción del país en la tabla

                # Métricas ordenadas de menor a mayor
                ascending_metrics = {
                    "carries_dis","carries_mis","Per_90_min_carries_dis","Per_90_min_carries_mis","pressing__ppda","defending_set_pieces__goals","defending_set_pieces__shots",
                    "defending_set_pieces__xg","misc.__pens_conceded","performance_crdr","performance_crdy","performance_fls","misc.__fouls","misc.__reds","misc.__yellows",
                    "performance_l","blocks_err","misc.__errors_lead_to_goal","misc.__errors_lead_to_shot","defending_misc__fast_breaks__goals","defending_misc__fast_breaks__total",
                    "defending_misc__headers__goals","defending_misc__headers__total","hit_post_conceded_per90","defending_misc__offsides","defending_misc__touches_in_box",
                    "defending_overall__conv_pct","defending_overall__goals","defending_overall__goals_vs_xg","defending_overall__shots","defending_overall__sot","defending_overall__xg",
                    "defending_overall__xg_per_shot",
                }

                ascending = selected_stat in ascending_metrics
                df_stat = df_stat.sort_values(by=selected_stat, ascending=ascending)

                top3 = df_stat.head(3).reset_index(drop=True) # Visualización del podio

                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        team = top3.loc[i]
                        name = team['team_code']
                        image_url = team['team_logo']
                        stat_val = round(team[selected_stat], 2) if pd.notna(team[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        team_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'></strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += team_html

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                stat_col_label = get_stat_display_name(selected_stat) # Selección de columnas en la tabla

                final_df = df_stat.rename(columns={selected_stat: stat_col_label})
                final_df = final_df[['team_code', stat_col_label, 'championship_name', 'country', 'rank_big5', 'rank_league']]
                # Traducción de columnas al español
                col_labels_es = {"team_code": "Equipo","championship_name": "Liga","country": "País","rank_big5": "Power Ranking","rank_league": "Clasificación (Liga)"}
                final_df = final_df.rename(columns=col_labels_es)
                st.dataframe(final_df, use_container_width=True)

    elif selected in ["Top"]:
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏅 Power Ranking</h4>", unsafe_allow_html=True) # Afficher le titre

            # Chargement
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            st.markdown("<p style='text-align:center; margin-bottom:0'>En comparaison avec :</p>", unsafe_allow_html=True) # Filtre selon le Big 5 ou un championnat spécifique
            c1, c2, c3 = st.columns([1.6, 2, 1])
            with c2:
                comparison_filter = st.radio(label="En comparaison avec",options=["Big 5", "Championnat"],index=0,horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

            if comparison_filter == "Championnat":  # Filtre championnat
                champs = info_team["championship_name"].dropna().drop_duplicates().sort_values().tolist()
                selected_champ = st.selectbox("Sélectionnez un championnat", champs, index=0)
                group_df = info_team[info_team["championship_name"] == selected_champ].copy()
            else:
                group_df = info_team.copy()  # Pas de filtre

            group_df["Pays"] = group_df["country"].map(lambda x: translate_country(x, lang="fr")) # Traduction du pays

            # Estimation du style de jeu Offensif et Défensif pour chaque équipe
            def _compute_styles_labels(row):
                styles = estimate_team_styles(row)
                off_label_fr = translate_style(styles.get("offensive_style", ""), lang="fr")
                def_label_fr = translate_style(styles.get("defensive_style", ""), lang="fr")
                return pd.Series({"Style offensif": off_label_fr, "Style défensif": def_label_fr})

            style_cols = group_df.apply(_compute_styles_labels, axis=1)
            group_df = pd.concat([group_df, style_cols], axis=1)

            # Colonnes de score : renommage en français
            score_cols = [c for c in group_df.columns if c.startswith("score_")]
            translated_score_map = {c: translate_base_stat(c.replace("score_", ""), lang="fr") for c in score_cols}
            group_df = group_df.rename(columns=translated_score_map)
            translated_score_cols = [translated_score_map[c] for c in score_cols]

            # Liste des colonnes à afficher
            preferred_cols = ["rank_big5","team_logo","team_code","championship_name","Pays","rank_league","rating","Style offensif","Style défensif"] + translated_score_cols
            df_display = group_df[preferred_cols].copy()

            df_display = df_display.sort_values(by="rank_big5", ascending=True) # Tri : uniquement par rank_big5 (ascendant)

            # Configuration d'affichage
            col_config = {"team_logo": st.column_config.ImageColumn("Logo", help="Logo du club", width="small"),"rank_big5": st.column_config.NumberColumn("Rang Big 5", format="%d"),
                        "team_code": "Équipe","championship_name": "Championnat","rank_league": st.column_config.NumberColumn("Rang Ligue", format="%d"),
                        "rating": st.column_config.NumberColumn("Note", format="%.0f")}

            st.dataframe(df_display.reset_index(drop=True),hide_index=True,use_container_width=True,column_config=col_config) # Affichage du tableau

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🏅 Power Ranking</h4>", unsafe_allow_html=True) # Title display

            # Loading
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            st.markdown("<p style='text-align:center; margin-bottom:0'>Compared to :</p>", unsafe_allow_html=True) # Filter by the Big 5 or a specific championship
            c1, c2, c3 = st.columns([1.6, 2, 1])
            with c2:
                comparison_filter = st.radio(label="Compared to",options=["Big 5", "League"],index=0,horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

            if comparison_filter == "League":  # Filter League
                champs = info_team["championship_name"].dropna().drop_duplicates().sort_values().tolist()
                selected_champ = st.selectbox("Select a league", champs, index=0)
                group_df = info_team[info_team["championship_name"] == selected_champ].copy()
            else:
                group_df = info_team.copy()  # No filter

            # Estimation of each team's offensive and defensive playing style
            def _compute_styles_labels(row):
                styles = estimate_team_styles(row)
                off_label = styles.get("offensive_style", "")
                def_label = styles.get("defensive_style", "")
                return pd.Series({"Offensive style": off_label, "Defensive style": def_label})

            style_cols = group_df.apply(_compute_styles_labels, axis=1)
            group_df = pd.concat([group_df, style_cols], axis=1)

            # Score columns: renaming in English
            score_cols = [c for c in group_df.columns if c.startswith("score_")]
            translated_score_map = {c: translate_base_stat(c.replace("score_", ""), lang="eng") for c in score_cols}
            group_df = group_df.rename(columns=translated_score_map)
            translated_score_cols = [translated_score_map[c] for c in score_cols]

            # List of columns to display
            preferred_cols = ["rank_big5","team_logo","team_code","championship_name","country","rank_league","rating","Offensive style","Defensive style"] + translated_score_cols
            df_display = group_df[preferred_cols].copy()

            df_display = df_display.sort_values(by="rank_big5", ascending=True) # Sort: only by rank_big5 (ascending)

            # Display configuration
            col_config = {"team_logo": st.column_config.ImageColumn("Logo", help="Club logo", width="small"),"rank_big5": st.column_config.NumberColumn("Big 5 ranking", format="%d"),
                        "team_code": "Team","championship_name": "League","rank_league": st.column_config.NumberColumn("League ranking", format="%d"),
                        "rating": st.column_config.NumberColumn("Rating", format="%.0f")}

            st.dataframe(df_display.reset_index(drop=True),hide_index=True,use_container_width=True,column_config=col_config) # Displaying the table

        else:
            st.markdown("<h4 style='text-align: center;'>🏅 Power Ranking</h4>", unsafe_allow_html=True) # Visualización del título

            # Cargando
            team_path = os.path.join(os.path.dirname(__file__), "..", "data", "team", "database_team.csv")
            info_team = pd.read_csv(team_path)

            st.markdown("<p style='text-align:center; margin-bottom:0'>En comparación con :</p>", unsafe_allow_html=True) # Filtrar según los Big 5 o una liga específica
            c1, c2, c3 = st.columns([1.6, 2, 1])
            with c2:
                comparison_filter = st.radio(label="En comparación con",options=["Big 5", "Liga"],index=0,horizontal=True,label_visibility="collapsed",key="comparison_filter_radio")

            if comparison_filter == "Liga":  # Filtro liga
                champs = info_team["championship_name"].dropna().drop_duplicates().sort_values().tolist()
                selected_champ = st.selectbox("Elige a liga", champs, index=0)
                group_df = info_team[info_team["championship_name"] == selected_champ].copy()
            else:
                group_df = info_team.copy()  # No filtro

            group_df["País"] = group_df["country"].map(lambda x: translate_country(x, lang="es")) # Traducción del país

            # Estimación del estilo de juego ofensivo y defensivo de cada equipo
            def _compute_styles_labels(row):
                styles = estimate_team_styles(row)
                off_label_es = translate_style(styles.get("offensive_style", ""), lang="es")
                def_label_es = translate_style(styles.get("defensive_style", ""), lang="es")
                return pd.Series({"Estilo ofensivo": off_label_es, "Estilo defensivo": def_label_es})

            style_cols = group_df.apply(_compute_styles_labels, axis=1)
            group_df = pd.concat([group_df, style_cols], axis=1)

            # Columnas de score: cambio de nombre al español
            score_cols = [c for c in group_df.columns if c.startswith("score_")]
            translated_score_map = {c: translate_base_stat(c.replace("score_", ""), lang="es") for c in score_cols}
            group_df = group_df.rename(columns=translated_score_map)
            translated_score_cols = [translated_score_map[c] for c in score_cols]

            # Lista de columnas que se mostrarán
            preferred_cols = ["rank_big5","team_logo","team_code","championship_name","País","rank_league","rating","Estilo ofensivo","Estilo defensivo"] + translated_score_cols
            df_display = group_df[preferred_cols].copy()

            df_display = df_display.sort_values(by="rank_big5", ascending=True) # Ordenar: solo por rank_big5 (ascendente)

            # Configuración de pantalla
            col_config = {"team_logo": st.column_config.ImageColumn("Logo", help="Logotipo del club", width="small"),"rank_big5": st.column_config.NumberColumn("Clasificación Big 5", format="%d"),
                        "team_code": "Equipo","championship_name": "Liga","rank_league": st.column_config.NumberColumn("Puesto Liga", format="%d"),
                        "rating": st.column_config.NumberColumn("Nota", format="%.0f")}

            st.dataframe(df_display.reset_index(drop=True),hide_index=True,use_container_width=True,column_config=col_config) # Visualización de la tabla

else:
    # MENU JOUEURS
    if lang == "Français":
        menu_labels = ["Menu", "Joueur", "Duel", "Stats +", "Stats", "Scout"]
    elif lang == "English":
        menu_labels = ["Home", "Player", "F2F", "Stats +", "Stats", "Scout"]
    else:
        menu_labels = ["Inicio", "Atleta", "Duelo", "Stats +", "Stats", "Scout"]

    selected = option_menu(menu_title=None,options=menu_labels,icons=["house", "person", "crosshair", "trophy", "list-ol", "binoculars"],orientation="horizontal")

    # Code de la partie Joueur / Code of the Player part / Código de la parte Jugador
    if selected in ["Menu", "Home", "Inicio"]:
        if lang == "Français":
            st.markdown("<h3 style='text-align: center;'>Visualisation des performances des joueurs sur la saison 25/26</h3>", unsafe_allow_html=True) # Titre de la page
            # Utilisation de la 1er bannière en image
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_player_performance.jpg")
            st.image(image_path)

            st.markdown("<h4 style='text-align: center;'>Présentation</h4>", unsafe_allow_html=True) # Sous-titre

            # Description du projet
            st.markdown(
                """
                <p style="text-align: justify;">
                L'objectif est de <strong>visualiser les performances des joueurs sur la saison 25/26</strong>.
                Les données des joueurs proviennent de Fbref et Transfermarkt.
                </p>

                <p style="text-align: justify;">
                Ainsi, l'analyse portera sur la saison 25/26 pour les compétitions suivantes :
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Analyse d'un Joueur</strong> : Analyse du joueur de votre choix à travers plusieurs statistiques</li>
                    <li><strong>🥊 Comparaison entre Joueurs</strong> : Analyse comparative entre deux joueurs du même poste</li>
                    <li><strong>🏆 Classement des joueurs (Stats Aggrégées par Catégorie) </strong> : Classement des joueurs par performance selon une statistique aggrégée par catégorie choisie</li>
                    <li><strong>🥇 Classement des joueurs (Stats Brutes) </strong> : Classement des joueurs par performance selon une statistique brute choisie</li>
                    <li><strong>🔎 Scouting </strong> : Établissement d'une liste de joueurs collant aux critères choisis</li>
                </ul>

                <br>

                Pour plus de détails sur ce projet, vous avez à votre disposition :
                <ul>
                    <li><em>La documentation du projet</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">Le code associé à l'application</a></li>
                </ul>
                """,
                unsafe_allow_html=True
            )

        elif lang == "English":
            st.markdown("<h3 style='text-align: center;'>Visualization of player performance over the 25/26 season</h3>", unsafe_allow_html=True) # Page title

            # Using the 1st image banner
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_player_performance.jpg")
            st.image(image_path)
            st.markdown("<h4 style='text-align: center;'>Presentation</h4>", unsafe_allow_html=True) # Subtitle

            # Project description
            st.markdown(
                """
                <p style="text-align: justify;">
                The goal is to <strong>visualize player performances during the 25/26 season</strong>.
                The data of players comes from Fbref and Transfermarkt.
                </p>
                <p style="text-align: justify;">
                The analysis will cover the 25/26 season for the following competitions:
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Player Analysis</strong>: Analyze the player of your choice through various statistics</li>
                    <li><strong>🥊 Player Comparison</strong>: Compare two players who play in the same position</li>
                    <li><strong>🏆 Player Ranking (Aggregate Statistics by Category) </strong>: Rank players based on a chosen aggregate statistic by category according to their position</li>
                    <li><strong>🥇 Player Ranking (Raw Statistics) </strong>: Rank players based on a chosen raw statistic</li>
                    <li><strong>🔎 Scouting </strong> : Drawing up a list of players matching the chosen criteria</li>
                </ul>

                <br>

                For more details about this project, you can refer to:
                <ul>
                    <li><em>The project documentation</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">The code used to build the application</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown("<h3 style='text-align: center;'>Visualización del rendimiento de los jugadores durante la temporada 25/26</h3>", unsafe_allow_html=True) # Título de la página

            # Usando el primer banner de imagen
            image_path = os.path.join(os.path.dirname(__file__), "..", "image", "logo_player_performance.jpg")
            st.image(image_path)

            st.markdown("<h4 style='text-align: center;'>Presentación</h4>", unsafe_allow_html=True) # Subtítulo

            # Descripción del proyecto
            st.markdown(
                """
                <p style="text-align: justify;">
                El objetivo es <strong>visualizar el rendimiento de los jugadores durante la temporada 25/26</strong>.
                Los datos de los jugadores provienen de Fbref y Transfermarkt.
                </p>
                <p style="text-align: justify;">
                El análisis abarcará la temporada 25/26 para las siguientes competiciones:
                <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
                </p>

                <br>

                <ul>
                    <li><strong>📊 Análisis de jugadores</strong>: Analizar al jugador de tu elección a través de varias estadísticas</li>
                    <li><strong>🥊 Comparación de jugadores</strong>: Comparar dos jugadores que juegan en la misma posición</li>
                    <li><strong>🏆 Clasificación de jugadores (Estadísticas agregadas por categoría) </strong>: Clasificar a los jugadores según una estadística agregada por categoría de acuerdo con su posición</li>
                    <li><strong>🥇 Clasificación de jugadores (Estadísticas brutas) </strong>: Clasificar a los jugadores según una estadística bruta elegida</li>
                    <li><strong>🔎 Scouting </strong>: Elaborar una lista de jugadores que cumplan con los criterios seleccionados</li>
                </ul>

                <br>

                Para más detalles sobre este proyecto, puedes consultar:
                <ul>
                    <li><em>La documentación del proyecto</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">El código utilizado para construir la aplicación</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
      

    elif selected in ["Joueur", "Player", "Atleta"]:
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>📊 Analyse d'un joueur</h4>", unsafe_allow_html=True) # Afficher le titre

            # Charger les données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist()) # Extraire la liste des joueurs

            selected_player = st.sidebar.selectbox("Choisissez un joueur :", player_names) # Sélection de joueur

            # Si un joueur est sélectionnée, on cache l’image   
            if not selected_player:
                # Aucun joueur sélectionné → afficher l'image d'intro
                # Utilisation de la 1er bannière en image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_analysis.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour choisir la langue et le joueur à analyser")
            else:
                player_data = df[df['player_name'] == selected_player].iloc[0] # Filtrer le DataFrame pour le joueur sélectionné

                # Récupération des informations et traductions associées en français si besoin
                pays = translate_country(player_data['nationality'], lang="fr")
                poste = translate_position(player_data['position'], lang="fr")

                shirt_raw = player_data.get("shirtNumber")
                if shirt_raw is not None and not (isinstance(shirt_raw, float) and pd.isna(shirt_raw)):
                    digits = re.sub(r"\D+", "", str(shirt_raw))
                    shirt_num = digits if digits else None
                else:
                    shirt_num = None

                foot_lbl = translate_foot(player_data.get("foot"), lang="fr")
                position_other_translated = translate_position_list(player_data.get("position_other"), lang="fr")
                agent_name = player_data.get("agent_name")
                agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                outfitter = player_data.get("outfitter")
                outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                shirt_num = shirt_num if shirt_num is not None else "Non connu"
                foot_lbl = foot_lbl if foot_lbl is not None else "Non connu"
                position_other = position_other_translated if position_other_translated is not None else "Aucun"
                agent_name = agent_name if agent_name is not None else "Non connu"
                outfitter = outfitter if outfitter is not None else "Non connu"

                st.markdown("<h4 style='text-align: center;'>Profil du joueur</h4>", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{player_data['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Nom :</strong> {player_data['player_name']}</p>
                    <p><strong>Âge :</strong> {int(player_data['Age']) if pd.notna(player_data['Age']) else "-"}</p>
                    <p><strong>Pays :</strong> {pays}</p>
                    <p><strong>Club :</strong> {player_data['club_name']}</p>
                    <p><strong>Poste :</strong> {poste}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Taille :</strong> {int(player_data['height']) if pd.notna(player_data['height']) else "-" } cm</p>
                    <p><strong>Valeur marchande :</strong> {format_market_value(player_data['marketValue'])}</p>
                    <p><strong>Fin de contrat :</strong> {player_data['contract'] if pd.notna(player_data['contract']) else "-"}</p>
                    <p><strong>Matches joués :</strong> {int(player_data['MP']) if pd.notna(player_data['MP']) else "-"}</p>
                    <p><strong>Minutes jouées :</strong> {int(player_data['Min']) if pd.notna(player_data['Min']) else "-"}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Numéro :</strong> {shirt_num}</p>
                    <p><strong>Pied fort :</strong> {foot_lbl}</p>
                    <p><strong>Autre(s) poste(s) :</strong> {position_other}</p>
                    <p><strong>Agent :</strong> {agent_name}</p>
                    <p><strong>Équipementier :</strong> {outfitter}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

                # Filtre unique pour radar + similarité
                comparison_filter = st.radio("En comparaison à son poste : ",options=["Vue globale","Championnat","Tranche d’âge","Pays"],index=0,horizontal=True)

                filter_arg = {"Vue globale": None,"Championnat": "championnat","Tranche d’âge": "tranche_age","Pays": "pays"}[comparison_filter]

                poste_cat = position_category.get(player_data['position'], None)

                # Glossaire des statistiques associées
                with st.expander(" Glossaire des statistiques"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90** : Buts encaissés par 90 minutes 
                            - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                            - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                            - **Save%** : Pourcentage d’arrêts effectués  
                            - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                            - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                            - **Launch%** : Pourcentage de passes longues  
                            - **AvgLen** : Longueur moyenne des passes (en yards)  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **AvgDist** : Distance moyenne des passes (en yards)  
                            - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                            - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués
                            - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                            - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won_per90** : Duels aériens gagnés par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués 
                            - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                            - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won_per90** : Duels aériens gagnés par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés 
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Fld_per90** : Fautes subies par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués 
                            - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés 
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **G-xG_per90** : Expected Goals par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **Succ_per90** : Dribbles réussis par 90 minutes
                            - **Succ%** : Pourcentage de dribbles réussis
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Fld_per90** : Fautes subies par 90 minutes
                            - **Dis_per90** : Ballons perdus par 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                            - **Sh_per90** : Tirs tentés par 90 minutes
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **G-xG_per90** : Expected Goals par 90 minutes
                            - **G/Sh** : Buts par tir  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **Succ_per_90** : Dribbles réussis par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **Dis_per90** : Ballons perdus par 90 minutes  
                            """)

                if poste_cat and poste_cat in category_stats_player:
                    stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]
                    player_rating = player_data.get("rating", None)

                    # Groupe filtré selon le filtre sélectionné par l'utilisateur
                    if filter_arg is None:
                        group_df = df[df['position'].map(position_category.get) == poste_cat]
                    elif filter_arg == "championnat":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['Comp'] == player_data['Comp'])
                        ]
                    elif filter_arg == "pays":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['nationality'] == player_data['nationality'])
                        ]
                    elif filter_arg == "tranche_age":
                        age = player_data['Age']
                        if pd.isna(age):
                            group_df = df[df['position'].map(position_category.get) == poste_cat]
                        elif age < 23:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] < 23)]
                        elif 24 <= age <= 29:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'].between(24, 29))]
                        else:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] >= 30)]

                    nb_players = len(group_df) # Calculer le nombre de joueur dans le groupe filtré

                    # Si il y a moins de 5 joueurs, on n'affiche pas de radar pour le groupe associé
                    if nb_players >= 5:
                        radar_df = group_df[['player_name'] + stats_cols].dropna(subset=stats_cols).copy()
                        radar_df = radar_df.set_index('player_name')

                        # On s'assure que le joueur est présent dans la catégorie de poste
                        if player_data['player_name'] not in radar_df.index:
                            radar_df.loc[player_data['player_name']] = pd.Series(player_data).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        # On établit le rang en percentile par catégorie pour chaque joueur (0 = plus faible, 1 = plus élevé)
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        # On inverse les métriques où "plus petit = mieux"
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0) # On normalise le profil du joueur en percentiles

                        # On calcule la médiane selon la catégorie de poste
                        group_median = (
                            rank_pct.drop(index=player_data['player_name'], errors='ignore')
                                    .median()
                                    .reindex(stats_cols)
                                    .fillna(0)
                        )

                        rating_text = f" - Note : {round(player_rating, 2)}" if player_rating is not None else "" # Calcul de la note si elle existe

                        # Affichage du titre avec note
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar de performance de {player_data['player_name']} vs {nb_players} joueurs dans sa catégorie {rating_text}</h4>",
                            unsafe_allow_html=True
                        )

                        # Construction de la pizza plot (joueur-médiane à son poste) pour les statistiques avancées
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player_norm * 100,median_values=group_median * 100,
                            title=f"Statistiques avancées de {player_data['player_name']} de vs Médiane à son poste",
                            legend_labels=(player_data['player_name'], "Médiane poste")
                        )

                        # Liste des colonnes à afficher selon le poste
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble", "score_projection",
                                "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

                        # On garde uniquement les colonnes présentes
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [translate_base_stat(col.replace("score_", ""), lang="fr") for col in pizza_cols]
                        # Vérifie que toutes les colonnes existent pour le joueur
                        if all(col in player_data for col in pizza_cols):

                            player_values = [player_data[col] for col in pizza_cols]

                            # Calcul des valeurs médianes sur le groupe filtré
                            group_df_scores = group_df[pizza_cols].dropna()
                            if len(group_df_scores) >= 5:
                                group_median = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median]

                                # Construction de la pizza plot (joueur-médiane) pour les statistiques de base
                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,data_values=player_scaled,median_values=median_scaled,
                                    title=f"Statistiques de base de {player_data['player_name']} vs Médiane à son poste",
                                    legend_labels=(player_data['player_name'], "Médiane poste")
                                )

                                # Affichage dans Streamlit
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.pyplot(fig_pizza_stat_basis)
                                with col2:
                                    st.pyplot(fig_pizza_stat_adv)

                        else:
                            st.info("Pas assez de joueurs dans ce groupe pour générer un radar (minimum requis : 5).")

                similar_df = find_similar_players(selected_player, df, filter_type=filter_arg) # Recherche des joueurs similaires avec le même filtre utilisé
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align: center;'>Joueurs similaires à {player_data['player_name']}</h4>",unsafe_allow_html=True) # Affichage du titre
                    st.dataframe(similar_df)
                else:
                    st.info("Aucun joueur similaire trouvé avec les critères sélectionnés.")

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>📊 Player analysis</h4>", unsafe_allow_html=True) # Display the title

            # Collect the data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)

            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist()) # Extract the list of players

            selected_player = st.sidebar.selectbox("Select a player :", player_names) # Select a player

            # If a player is selected, the image is hidden.   
            if not selected_player:
                # No player selected → show intro image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_analysis.jpg")
                st.image(image_path)
                st.info("Scroll down the sidebar to select the language and the player you wish to analyze")
            else:
                player_data = df[df['player_name'] == selected_player].iloc[0] # Filter the DataFrame for the selected player

                # Récupération des informations
                shirt_raw = player_data.get("shirtNumber")
                if shirt_raw is not None and not (isinstance(shirt_raw, float) and pd.isna(shirt_raw)):
                    digits = re.sub(r"\D+", "", str(shirt_raw))
                    shirt_num = digits if digits else None
                else:
                    shirt_num = None

                foot_lbl = translate_foot(player_data.get("foot"), lang="eng")
                position_other_translated = translate_position_list(player_data.get("position_other"), lang="eng")
                agent_name = player_data.get("agent_name")
                agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                outfitter = player_data.get("outfitter")
                outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                shirt_num = shirt_num if shirt_num is not None else "Not known"
                foot_lbl = foot_lbl if foot_lbl is not None else "Not known"
                position_other = position_other_translated if position_other_translated is not None else "None"
                agent_name = agent_name if agent_name is not None else "Not known"
                outfitter = outfitter if outfitter is not None else "Not known"

                # Player profile (image on left, info on right)
                st.markdown(f"<h4 style='text-align: center;'>Player profile</h4>",unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{player_data['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Name :</strong> {player_data['player_name']}</p>
                    <p><strong>Age :</strong> {int(player_data['Age']) if pd.notna(player_data['Age']) else "-"}</p>
                    <p><strong>Country :</strong> {player_data['nationality']}</p>
                    <p><strong>Club :</strong> {player_data['club_name']}</p>
                    <p><strong>Position :</strong> {player_data['position']}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Height :</strong> {int(player_data['height']) if pd.notna(player_data['height']) else "-" } cm</p>
                    <p><strong>Market Value :</strong> {format_market_value(player_data['marketValue'])}</p>
                    <p><strong>Contract :</strong> {player_data['contract'] if pd.notna(player_data['contract']) else "-"}</p>
                    <p><strong>Matches Played :</strong> {int(player_data['MP']) if pd.notna(player_data['MP']) else "-"}</p>
                    <p><strong>Minutes Played :</strong> {int(player_data['Min']) if pd.notna(player_data['Min']) else "-"}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Number :</strong> {shirt_num}</p>
                    <p><strong>Strong foot :</strong> {foot_lbl}</p>
                    <p><strong>Other(s) position(s) :</strong> {position_other_translated}</p>
                    <p><strong>Agent :</strong> {agent_name}</p>
                    <p><strong>Outfitter :</strong> {outfitter}</p>
                </div>
                </div>
                """, unsafe_allow_html=True)

                # Single filter for radar + similarity
                comparison_filter = st.radio("Compared to his position :",options=["Overview","Championship","Age group","Country"],index=0,horizontal=True)

                filter_arg = {"Overview": None,"Championship": "championnat","Age group": "tranche_age","Country": "pays"}[comparison_filter]

                poste_cat = position_category.get(player_data['position'], None)

                # Glossary of Statistics associated
                with st.expander("Glossary of Statistics"):
                    if poste_cat:
                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90**: Goals conceded per 90 minutes  
                            - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                            - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                            - **Save%**: Save percentage  
                            - **PSxG+/-**: Difference between PSxG and goals conceded  
                            - **Err_per90**: Errors leading to a shot per 90 minutes  
                            - **Launch%**: Percentage of long passes  
                            - **AvgLen**: Average pass length (in yards)  
                            - **Cmp%**: Pass completion percentage  
                            - **AvgDist**: Average pass distance (in yards)  
                            - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                            - **Stp%**: Percentage of crosses stopped inside the box 
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                            - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won_per90**: Aerial duels won per 90 minutes  
                            - **Won%**: Aerial duel success rate  
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                            - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won_per90**: Aerial duels won per 90 minutes  
                            - **Won%**: Aerial duel success rate  
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Fld_per90**: Fouls drawn per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won%**: Aerial duel success rate 
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **Succ_per90**: Successful dribbles per 90 minutes  
                            - **Succ%**: Dribble success rate  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Fld_per90**: Fouls drawn per 90 minutes  
                            - **Dis_per90**: Dispossessions per 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                            - **Sh_per90**: Shots attempted per 90 minutes  
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                            - **G/Sh**: Goals per shot  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **Succ_per_90**: Successful dribbles per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Dis_per90**: Dispossessions per 90 minutes 
                            """)

                if poste_cat and poste_cat in category_stats_player:
                    stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]
                    player_rating = player_data.get("rating", None)

                    # Group filtered according to the selected filter by the user
                    if filter_arg is None:
                        group_df = df[df['position'].map(position_category.get) == poste_cat]
                    elif filter_arg == "championnat":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['Comp'] == player_data['Comp'])
                        ]
                    elif filter_arg == "pays":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['nationality'] == player_data['nationality'])
                        ]
                    elif filter_arg == "tranche_age":
                        age = player_data['Age']
                        if pd.isna(age):
                            group_df = df[df['position'].map(position_category.get) == poste_cat]
                        elif age < 23:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] < 23)]
                        elif 24 <= age <= 29:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'].between(24, 29))]
                        else:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] >= 30)]

                    nb_players = len(group_df) # Calculation of the length of the group

                    # If the group is less than 5, we don't build the radar
                    if nb_players >= 5:
                        radar_df = group_df[['player_name'] + stats_cols].dropna(subset=stats_cols).copy()
                        radar_df = radar_df.set_index('player_name')

                        # We ensure that the player is present in the position category.
                        if player_data['player_name'] not in radar_df.index:
                            radar_df.loc[player_data['player_name']] = pd.Series(player_data).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True) # The percentile rank is established for each player by category (0 = lowest, 1 = highest)

                        # We are reversing the metrics where ‘smaller = better’
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0) # The player's profile is standardised in percentiles

                        # The median is calculated according to position category.
                        group_median = (
                            rank_pct.drop(index=player_data['player_name'], errors='ignore')
                                    .median()
                                    .reindex(stats_cols)
                                    .fillna(0)
                        )
                        rating_text = f" - Rating : {round(player_rating, 2)}" if player_rating is not None else "" # Rating calculation if available

                        # Title display with note
                        st.markdown(f"<h4 style='text-align: center;'>Performance radar from {player_data['player_name']} vs {nb_players} players in his category {rating_text}</h4>",
                            unsafe_allow_html=True)
                        
                        # Bulding the pizza plot (player-median) for the advanced statistics
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player_norm * 100,median_values=group_median * 100,
                            title=f"Advanced statistics of {player_data['player_name']} vs. median at the same position",
                            legend_labels=(player_data['player_name'], "Median position")
                        )

                        # List of columns to be displayed by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls","score_short_clearance",
                             "score_long_clearance","score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble",
                             "score_projection", "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        # We keep only the columns present
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                        # Checks that all columns exist for the player
                        if all(col in player_data for col in pizza_cols):
                            player_values = [player_data[col] for col in pizza_cols]

                            group_df_scores = group_df[pizza_cols].dropna() # Calculation of median values on the filtered group
                            if len(group_df_scores) >= 5:
                                group_median = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median]

                                # Bulding the pizza plot (player-median) for the basic statistics
                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,data_values=player_scaled,median_values=median_scaled,
                                    title=f"Basic statistics of {player_data['player_name']} vs. median at the same position",
                                    legend_labels=(player_data['player_name'], "Median position")
                                )

                        # List of columns to be displayed by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble",
                             "score_projection", "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        # We keep only the columns present
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                        # Checks that all columns exist for the player
                        if all(col in player_data for col in pizza_cols):
                            player_values = [player_data[col] for col in pizza_cols]

                            group_df_scores = group_df[pizza_cols].dropna() # Calculation of median values on the filtered group
                            if len(group_df_scores) >= 5:
                                group_median = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median]

                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,data_values=player_scaled,median_values=median_scaled,
                                    title="Basic statistics vs. median at the same position",
                                    legend_labels=(player_data['player_name'], "Median position")
                                )

                                # Display in Streamlit
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.pyplot(fig_pizza_stat_basis)
                                with col2:
                                    st.pyplot(fig_pizza_stat_adv)
                    else:
                        st.info("Not enough players in this group to generate a radar (minimum requirement: 5).")

                similar_df = find_similar_players(selected_player, df, filter_type=filter_arg) # Search for similar players using the same filter
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align: center;'>Players similar to {player_data['player_name']}</h4>",unsafe_allow_html=True) # Display the title
                    st.dataframe(similar_df)
                else:
                    st.info("Not enough players in this group to generate a radar (minimum requirement: 5).")
        else:
            st.markdown("<h4 style='text-align: center;'>📊 Análisis de un jugador</h4>", unsafe_allow_html=True) # Título

            # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)

            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist())  # Lista de jugadores

            selected_player = st.sidebar.selectbox("Elige un jugador:", player_names)  # Selección de jugador

            # Si no hay jugador seleccionado → mostrar imagen de introducción
            if not selected_player:
                # Banner de introducción
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_analysis.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para elegir el idioma y el jugador a analizar")
            else:
                player_data = df[df['player_name'] == selected_player].iloc[0]  # Fila del jugador

                # Recuperación de la información y traducciones asociadas, si es necesario
                pais = translate_country(player_data['nationality'], lang="es")
                puesto = translate_position(player_data['position'], lang="es")

                shirt_raw = player_data.get("shirtNumber")
                if shirt_raw is not None and not (isinstance(shirt_raw, float) and pd.isna(shirt_raw)):
                    digits = re.sub(r"\D+", "", str(shirt_raw))
                    shirt_num = digits if digits else None
                else:
                    shirt_num = None

                foot_lbl = translate_foot(player_data.get("foot"), lang="es")
                position_other_translated = translate_position_list(player_data.get("position_other"), lang="es")
                agent_name = player_data.get("agent_name")
                agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                outfitter = player_data.get("outfitter")
                outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                shirt_num = shirt_num if shirt_num is not None else "Desconocido"
                foot_lbl = foot_lbl if foot_lbl is not None else "Desconocido"
                position_other = position_other_translated if position_other_translated is not None else "Ninguno"
                agent_name = agent_name if agent_name is not None else "Desconocido"
                outfitter = outfitter if outfitter is not None else "Desconocido"

                # Perfil del jugador (imagen a la izquierda, info a la derecha)
                st.markdown("<h4 style='text-align: center;'>Perfil del jugador</h4>", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

                <div style="flex: 1; text-align: center; min-width: 180px;">
                    <img src="{player_data['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Nombre:</strong> {player_data['player_name']}</p>
                    <p><strong>Edad:</strong> {int(player_data['Age']) if pd.notna(player_data['Age']) else "-"}</p>
                    <p><strong>País:</strong> {pais}</p>
                    <p><strong>Club:</strong> {player_data['club_name']}</p>
                    <p><strong>Posición:</strong> {puesto}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Altura:</strong> {int(player_data['height']) if pd.notna(player_data['height']) else "-" } cm</p>
                    <p><strong>Valor de mercado:</strong> {format_market_value(player_data['marketValue'])}</p>
                    <p><strong>Fin de contrato:</strong> {player_data['contract'] if pd.notna(player_data['contract']) else "-"}</p>
                    <p><strong>Partidos jugados:</strong> {int(player_data['MP']) if pd.notna(player_data['MP']) else "-"}</p>
                    <p><strong>Minutos jugados:</strong> {int(player_data['Min']) if pd.notna(player_data['Min']) else "-"}</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Número :</strong> {shirt_num}</p>
                    <p><strong>Pie fuerte :</strong> {foot_lbl}</p>
                    <p><strong>Otro(s) puesto(s) :</strong> {position_other_translated}</p>
                    <p><strong>Agente :</strong> {agent_name}</p>
                    <p><strong>Fabricante de equipos :</strong> {outfitter}</p>
                </div>
                </div>
                """, unsafe_allow_html=True)

                # Filtro único para radar + similitud
                comparison_filter = st.radio("En comparación con su posición:",options=["Vista general","Liga","Tramo de edad","País"],index=0,horizontal=True)

                # Mapeo de la opción de UI (ES) a las claves internas usadas en tu lógica
                filter_arg = {"Vista general": None,"Liga": "championnat","Tramo de edad": "tranche_age","País": "pays"}[comparison_filter]

                poste_cat = position_category.get(player_data['position'], None) # Categoría del puesto

                # Glosario de estadísticas (poste_cat en francés)
                with st.expander(" Glosario de estadísticas"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90**: Goles encajados por 90 minutos  
                            - **PSxG_per90**: Post-Shot Expected Goals por 90 minutos  
                            - **/90 (PSxG-GA/90)**: Diferencia entre PSxG y goles encajados por 90 minutos  
                            - **Save%**: Porcentaje de paradas  
                            - **PSxG+/-**: Diferencia entre PSxG (xG post-tiro) y goles encajados  
                            - **Err_per90**: Errores que conducen a un tiro rival por 90 minutos  
                            - **Launch%**: Porcentaje de pases largos  
                            - **AvgLen**: Longitud media de pase (yardas)  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **AvgDist**: Distancia media de pase (yardas)  
                            - **#OPA_per90**: Acciones defensivas fuera del área por 90 minutos  
                            - **Stp%**: Porcentaje de centros detenidos dentro del área  
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                            - **PrgP_per90**: Pases progresivos por 90 minutos  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                            - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                            - **Err_per90**: Errores que conducen a un tiro rival  
                            - **Tkl%**: Porcentaje de éxito en entradas  
                            - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                            - **Tkl_per90_Padj**: Entradas por 90 minutos ajustadas a la posesión
                            - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                            - **Won_per90**: Duelos aéreos ganados por 90 minutos  
                            - **Won%**: Porcentaje de duelos aéreos ganados  
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                            - **PrgP_per90**: Pases progresivos por 90 minutos  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                            - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                            - **Err_per90**: Errores que conducen a un tiro rival  
                            - **Tkl%**: Porcentaje de éxito en entradas  
                            - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                            - **Tkl_per90_Padj**: Entradas por 90 minutos ajustadas a la posesión
                            - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                            - **Won_per90**: Duelos aéreos ganados por 90 minutos  
                            - **Won%**: Porcentaje de duelos aéreos ganados  
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                            - **PrgP_per90**: Pases progresivos por 90 minutos  
                            - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                            - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                            - **Fld_per90**: Faltas recibidas por 90 minutos  
                            - **Err_per90**: Errores que conducen a un tiro rival  
                            - **Tkl%**: Porcentaje de éxito en entradas  
                            - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                            - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                            - **Won%**: Porcentaje de duelos aéreos ganados  
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **npxG_per90**: xG sin penaltis por 90 minutos  
                            - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                            - **G-xG_per90**: G - xG por 90 minutos  
                            - **PrgP_per90**: Pases progresivos por 90 minutos  
                            - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                            - **Succ_per90**: Regates exitosos por 90 minutos  
                            - **Succ%**: Porcentaje de regates exitosos  
                            - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                            - **Fld_per90**: Faltas recibidas por 90 minutos  
                            - **Dis_per90**: Balones perdidos por 90 minutos  
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **npxG_per90**: xG sin penaltis por 90 minutos  
                            - **Sh_per90**: Tiros por 90 minutos  
                            - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                            - **G-xG_per90**: G - xG por 90 minutos  
                            - **G/Sh**: Goles por tiro  
                            - **PrgP_per90**: Pases progresivos por 90 minutos  
                            - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                            - **Cmp%**: Porcentaje de pases completados  
                            - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                            - **Succ_per_90**: Regates exitosos por 90 minutos  
                            - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                            - **Dis_per90**: Balones perdidos por 90 minutos  
                            """)

                if poste_cat and poste_cat in category_stats_player:
                    stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]
                    player_rating = player_data.get("rating", None)

                    # Grupo filtrado según el filtro seleccionado
                    if filter_arg is None:
                        group_df = df[df['position'].map(position_category.get) == poste_cat]
                    elif filter_arg == "championnat":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['Comp'] == player_data['Comp'])
                        ]
                    elif filter_arg == "pays":
                        group_df = df[
                            (df['position'] == player_data['position']) &
                            (df['nationality'] == player_data['nationality'])
                        ]
                    elif filter_arg == "tranche_age":
                        age = player_data['Age']
                        if pd.isna(age):
                            group_df = df[df['position'].map(position_category.get) == poste_cat]
                        elif age < 23:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] < 23)]
                        elif 24 <= age <= 29:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'].between(24, 29))]
                        else:
                            group_df = df[(df['position'] == player_data['position']) & (df['Age'] >= 30)]

                    nb_players = len(group_df)  # Número de jugadores en el grupo

                    # Si hay menos de 5 jugadores, no mostramos radar del grupo
                    if nb_players >= 5:
                        radar_df = group_df[['player_name'] + stats_cols].dropna(subset=stats_cols).copy()
                        radar_df = radar_df.set_index('player_name')

                        # Asegurar que el jugador esté presente
                        if player_data['player_name'] not in radar_df.index:
                            radar_df.loc[player_data['player_name']] = pd.Series(player_data).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True) # Percentiles por categoría (0 = peor, 1 = mejor)

                        # Invertir métricas donde "más pequeño = mejor"
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0) # Perfil del jugador normalizado (percentiles)

                        # Mediana del grupo (sin el propio jugador)
                        group_median = (
                            rank_pct
                            .drop(index=player_data['player_name'], errors='ignore')
                            .median()
                            .reindex(stats_cols)
                            .fillna(0)
                        )

                        rating_text = f" - Nota: {round(player_rating, 2)}" if player_rating is not None else "" # Nota si existe

                        # Título con nota
                        st.markdown(f"<h4 style='text-align: center;'>Radar de rendimiento de {player_data['player_name']} frente a {nb_players} jugadores de su categoría{rating_text}</h4>",
                            unsafe_allow_html=True)

                        # Radar (avanzadas)
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player_norm * 100,median_values=group_median * 100,
                            title=f"Estadísticas avanzadas de {player_data['player_name']} vs Mediana del puesto",
                            legend_labels=(player_data['player_name'], "Mediana del puesto")
                        )

                        # Columnas para el radar (básicas)
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls","score_short_clearance",
                             "score_long_clearance", "score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble", "score_projection",
                             "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        pizza_cols = [col for col in pizza_cols if col in df.columns] # Mantener solo las columnas presentes
                        pizza_labels = [translate_base_stat(col.replace("score_", ""), lang="es") for col in pizza_cols] # Etiquetas en español

                        # Verificar que el jugador tenga todas las columnas
                        if all(col in player_data for col in pizza_cols):
                            player_values = [player_data[col] for col in pizza_cols]

                            group_df_scores = group_df[pizza_cols].dropna() # Mediana del grupo para estas columnas
                            if len(group_df_scores) >= 5:
                                group_median_list = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median_list]

                                # Radar (básicas)
                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,data_values=player_scaled,median_values=median_scaled,
                                    title=f"Estadísticas básicas de {player_data['player_name']} vs Mediana del puesto",
                                    legend_labels=(player_data['player_name'], "Mediana del puesto")
                                )

                                # Mostrar en Streamlit
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.pyplot(fig_pizza_stat_basis)
                                with col2:
                                    st.pyplot(fig_pizza_stat_adv)
                    else:
                        st.info("No hay suficientes jugadores en este grupo para generar un radar (mínimo requerido: 5).")

                similar_df = find_similar_players(selected_player, df, filter_type=filter_arg) # Jugadores similares (mismo filtro)
                if not similar_df.empty:
                    st.markdown(f"<h4 style='text-align: center;'>Jugadores similares a {player_data['player_name']}</h4>",unsafe_allow_html=True)
                    st.dataframe(similar_df)
                else:
                    st.info("No se encontraron jugadores similares con los criterios seleccionados.")
            

    elif selected in ["Duel", "F2F", "Duelo"]:
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🥊 Comparaison de deux joueurs</h4>", unsafe_allow_html=True) # Affichage du titre
            # Récupérer les données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            player_names = sorted(df['player_name'].dropna().unique().tolist()) # Ordonner par le nom du joueur

            st.sidebar.markdown("### Sélection des joueurs") # Sélection dans la sidebar

            player1 = st.sidebar.selectbox("Premier joueur :", [''] + player_names, key="player1") # Sélection du 1er joueur
            
            if not player1:
                # Aucun joueur sélectionné → afficher l'image d'intro
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")

            if player1:
                # Nous stockons les informations du 1er joueur
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None)

                sub_positions_same_cat = [pos for pos, cat in position_category.items() if cat == poste_cat] # Tous les position de la même catégorie

                # On filtre tous les joueurs ayant un poste dans cette catégorie
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]

                player2 = st.sidebar.selectbox("Second joueur (même poste) :", [''] + player2_names, key="player2") # Sélection du 2nd joueur
                
                if not player2:
                    # Aucun joueur sélectionné → afficher l'image d'intro
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                    st.image(image_path)
                    st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")

                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0] # Récupération du nom du 2nd joueur
                    
                    st.markdown("<h4 style='text-align: center;'>Profils des joueurs</h4>", unsafe_allow_html=True) # On affiche le profil des joueurs

                    for pdata in [player1_data, player2_data]:
                        # Traductions et affichage propre des informations
                        pays = translate_country(pdata['nationality'], lang="fr")
                        poste = translate_position(pdata['position'], lang="fr")

                        foot_lbl = translate_foot(pdata.get("foot"), lang="fr")
                        position_other_translated = translate_position_list(pdata.get("position_other"), lang="fr")
                        agent_name = pdata.get("agent_name")
                        agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                        outfitter = pdata.get("outfitter")
                        outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                        foot_lbl = foot_lbl if foot_lbl is not None else "Non connu"
                        position_other = position_other_translated if position_other_translated is not None else "Aucun"
                        agent_name = agent_name if agent_name is not None else "Non connu"
                        outfitter = outfitter if outfitter is not None else "Non connu"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{pdata['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Nom :</strong> {pdata['player_name']}</p>
                            <p><strong>Âge :</strong> {int(pdata['Age']) if pd.notna(pdata['Age']) else "-"}</p>
                            <p><strong>Pays :</strong> {pays}</p>
                            <p><strong>Club :</strong> {pdata['club_name']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Poste :</strong> {poste}</p>
                            <p><strong>Taille :</strong> {int(pdata['height']) if pd.notna(pdata['height']) else "-" } cm</p>
                            <p><strong>Valeur marchande :</strong> {format_market_value(pdata['marketValue'])}</p>
                            <p><strong>Fin de contrat :</strong> {pdata['contract'] if pd.notna(pdata['contract']) else "-"}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Pied fort :</strong> {foot_lbl}</p>
                            <p><strong>Autre(s) poste(s) :</strong> {position_other_translated}</p>
                            <p><strong>Agent :</strong> {agent_name}</p>
                            <p><strong>Équipementier :</strong> {outfitter}</p>
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Glossaire des statistiques associées
                    with st.expander(" Glossaire des statistiques"):
                        if poste_cat:

                            if poste_cat == "Gardiens de but":
                                st.markdown("""
                                - **GA_per90** : Buts encaissés par 90 minutes 
                                - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                                - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                                - **Save%** : Pourcentage d’arrêts effectués  
                                - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                                - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                                - **Launch%** : Pourcentage de passes longues  
                                - **AvgLen** : Longueur moyenne des passes (en yards)  
                                - **Cmp%** : Pourcentage de passes réussies  
                                - **AvgDist** : Distance moyenne des passes (en yards)  
                                - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                                - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                                """)

                            elif poste_cat == "Défenseurs centraux":
                                st.markdown("""
                                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                                - **PrgP_per90** : Passes progressives par 90 minutes
                                - **Cmp%** : Pourcentage de passes réussies
                                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                                - **PrgC_per90** : Conduites progressives par 90 minutes
                                - **Err_per90** : Erreurs menant à un tir adverse
                                - **Tkl%** : Pourcentage de tacles effectués
                                - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                                - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                                - **CrdY_per90** : Cartons jaunes par 90 minutes
                                - **Won_per90** : Duels aériens gagnés par 90 minutes
                                - **Won%** : Pourcentage de duels aériens gagnés
                                """)

                            elif poste_cat == "Défenseurs latéraux":
                                st.markdown("""
                                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                                - **PrgP_per90** : Passes progressives par 90 minutes
                                - **Cmp%** : Pourcentage de passes réussies
                                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                                - **PrgC_per90** : Conduites progressives par 90 minutes
                                - **Err_per90** : Erreurs menant à un tir adverse
                                - **Tkl%** : Pourcentage de tacles effectués 
                                - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                                - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                                - **CrdY_per90** : Cartons jaunes par 90 minutes
                                - **Won_per90** : Duels aériens gagnés par 90 minutes
                                - **Won%** : Pourcentage de duels aériens gagnés 
                                """)

                            elif poste_cat == "Milieux de terrain":
                                st.markdown("""
                                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                                - **PrgP_per90** : Passes progressives par 90 minutes
                                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                                - **Cmp%** : Pourcentage de passes réussies
                                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                                - **PrgC_per90** : Conduites progressives par 90 minutes
                                - **Fld_per90** : Fautes subies par 90 minutes
                                - **Err_per90** : Erreurs menant à un tir adverse
                                - **Tkl%** : Pourcentage de tacles effectués 
                                - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                                - **CrdY_per90** : Cartons jaunes par 90 minutes
                                - **Won%** : Pourcentage de duels aériens gagnés 
                                """)

                            elif poste_cat == "Milieux offensifs / Ailiers":
                                st.markdown("""
                                - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                                - **G-xG_per90** : Expected Goals par 90 minutes
                                - **PrgP_per90** : Passes progressives par 90 minutes
                                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                                - **Cmp%** : Pourcentage de passes réussies
                                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                                - **Succ_per90** : Dribbles réussis par 90 minutes
                                - **Succ%** : Pourcentage de dribbles réussis
                                - **PrgC_per90** : Conduites progressives par 90 minutes
                                - **Fld_per90** : Fautes subies par 90 minutes
                                - **Dis_per90** : Ballons perdus par 90 minutes
                                """)

                            elif poste_cat == "Attaquants":
                                st.markdown("""
                                - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                                - **Sh_per90** : Tirs tentés par 90 minutes
                                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                                - **G-xG_per90** : Expected Goals par 90 minutes
                                - **G/Sh** : Buts par tir  
                                - **PrgP_per90** : Passes progressives par 90 minutes  
                                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                                - **Cmp%** : Pourcentage de passes réussies
                                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                                - **Succ_per_90** : Dribbles réussis par 90 minutes  
                                - **PrgC_per90** : Conduites progressives par 90 minutes  
                                - **Dis_per90** : Ballons perdus par 90 minutes  
                                """)

                    # Génération du radar
                    if poste_cat and poste_cat in category_stats_player:
                        stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]  # On récupère la catégories de stats selon le poste

                        # Filtrer les statistiques des joueurs selon la catégorie de poste
                        if 'poste_cat' not in df.columns:
                            df = df.copy()
                            df['poste_cat'] = df['position'].map(position_category)

                        radar_df = df[df['poste_cat'] == poste_cat][['player_name'] + stats_cols].copy()
                        radar_df = radar_df.dropna(subset=stats_cols).set_index('player_name')

                        # On s'assure que les 2 joueurs comparés sont inclus dans la référence
                        for p, pdata in [(player1, player1_data), (player2, player2_data)]:
                            if p not in radar_df.index:
                                radar_df.loc[p] = pd.Series(pdata).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        # On évalue chaque statistique selon sa position au regard des autres joueurs ayant la même position
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        # On inverse les métriques où "plus petit = mieux"
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        # On normalise les valeurs par rang pour le radar
                        player1_norm = rank_pct.loc[player1].reindex(stats_cols).fillna(0)
                        player2_norm = rank_pct.loc[player2].reindex(stats_cols).fillna(0)
                        
                        player1_rating = player1_data.get("rating", None)
                        player2_rating = player2_data.get("rating", None)

                        # Calcul de la note si elle existe
                        rating1_text = f"Note : {round(player1_rating)}" if player1_rating is not None else ""
                        rating2_text = f"Note : {round(player2_rating)}" if player2_rating is not None else ""
                        
                        # Affichage du titre et du radar
                        st.markdown(f"<h4 style='text-align: center;'>Radar comparatif : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",unsafe_allow_html=True)
                        
                        # Création de la la pizza plot des statistiques avancées
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player1_norm * 100,median_values=player2_norm * 100,
                            title=f"Statistiques avancées de {player1} vs {player2}",legend_labels=(player1, player2)
                        )

                        # Liste de colonnes de score par poste
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls","score_short_clearance",
                             "score_long_clearance", "score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble", "score_projection",
                             "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        # Nous ne gardons uniquement les colonnes d'interêt pour le poste
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [translate_base_stat(col.replace("score_", ""), lang="fr") for col in pizza_cols]

                        # Vérification si ces colonnes existent pour les deux joueurs
                        if all((col in player1_data) and (col in player2_data) for col in pizza_cols):

                            player1_values = [player1_data[col] for col in pizza_cols]
                            player2_values = [player2_data[col] for col in pizza_cols]

                            # Vérifie que les données sont valides pour les deux joueurs
                            player1_scaled = [v if pd.notna(v) else 0 for v in player1_values]
                            player2_scaled = [v if pd.notna(v) else 0 for v in player2_values]

                            # Création du radar comparatif (pizza plot) pour les statistiques de base
                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,data_values=player1_scaled,median_values=player2_scaled,
                                title=f"Statistiques de base de {player1} vs {player2}",legend_labels=(player1, player2)
                            )

                        # Affichage dans Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🥊 Player Comparison</h4>", unsafe_allow_html=True) # Display the title
            # Recover the data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            player_names = sorted(df['player_name'].dropna().unique().tolist()) # Order by data 

            st.sidebar.markdown("### Player selection") # Selection in the sidebar

            player1 = st.sidebar.selectbox("First player :", [''] + player_names, key="player1") # Select the first player
            
            if not player1:
                # If the player is selected, we hide the image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                st.image(image_path)
                st.info("Scroll down the sidebar to select the language and players for analysis")

            if player1:
                # Collecting the data for the players
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None)

                sub_positions_same_cat = [pos for pos, cat in position_category.items() if cat == poste_cat] # All positions in the same category

                # We filter all players with a position in this category
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]

                player2 = st.sidebar.selectbox("Second player (same position) :", [''] + player2_names, key="player2") # Select the 2nd player
                
                if not player2:
                    # If the player is selected, we hide the image
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                    st.image(image_path)
                    st.info("Scroll down the sidebar to select the language and players for analysis")
                        
                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0] # Collecting the name of the player 2
                    
                    st.markdown("<h4 style='text-align: center;'>Players profile</h4>", unsafe_allow_html=True) # We display players profiles

                    for pdata in [player1_data, player2_data]:
                        
                        # Recovery of the data
                        foot_lbl = translate_foot(pdata.get("foot"), lang="eng")
                        position_other_translated = translate_position_list(pdata.get("position_other"), lang="eng")
                        agent_name = pdata.get("agent_name")
                        agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                        outfitter = pdata.get("outfitter")
                        outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                        foot_lbl = foot_lbl if foot_lbl is not None else "Not known"
                        position_other = position_other_translated if position_other_translated is not None else "None"
                        agent_name = agent_name if agent_name is not None else "Not known"
                        outfitter = outfitter if outfitter is not None else "Not known"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{pdata['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Name:</strong> {pdata['player_name']}</p>
                            <p><strong>Age:</strong> {int(pdata['Age']) if pd.notna(pdata['Age']) else "-"}</p>
                            <p><strong>Country:</strong> {pdata['nationality']}</p>
                            <p><strong>Club:</strong> {pdata['club_name']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Position:</strong> {pdata['position']}</p>
                            <p><strong>Height:</strong> {int(pdata['height']) if pd.notna(pdata['height']) else "-"} cm</p>
                            <p><strong>Market Value:</strong> {format_market_value(pdata['marketValue'])}</p>
                            <p><strong>Contract:</strong> {pdata['contract'] if pd.notna(pdata['contract']) else "-"}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Strong foot :</strong> {foot_lbl}</p>
                            <p><strong>Other(s) position(s) :</strong> {position_other_translated}</p>
                            <p><strong>Agent :</strong> {agent_name}</p>
                            <p><strong>Outfitter :</strong> {outfitter}</p>
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Glossary of Statistics associated
                    with st.expander("Glossary of Statistics"):
                        if poste_cat:

                            if poste_cat == "Gardiens de but":
                                st.markdown("""
                                - **GA_per90**: Goals conceded per 90 minutes  
                                - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                                - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                                - **Save%**: Save percentage  
                                - **PSxG+/-**: Difference between PSxG and goals conceded  
                                - **Err_per90**: Errors leading to a shot per 90 minutes  
                                - **Launch%**: Percentage of long passes  
                                - **AvgLen**: Average pass length (in yards)  
                                - **Cmp%**: Pass completion percentage  
                                - **AvgDist**: Average pass distance (in yards)  
                                - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                                - **Stp%**: Percentage of crosses stopped inside the box 
                                """)

                            elif poste_cat == "Défenseurs centraux":
                                st.markdown("""
                                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                                - **PrgP_per90**: Progressive passes per 90 minutes  
                                - **Cmp%**: Pass completion percentage  
                                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                                - **PrgC_per90**: Progressive carries per 90 minutes  
                                - **Err_per90**: Errors leading to a shot  
                                - **Tkl%**: Tackle success rate  
                                - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                                - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                                - **CrdY_per90**: Yellow cards per 90 minutes  
                                - **Won_per90**: Aerial duels won per 90 minutes  
                                - **Won%**: Aerial duel success rate  
                                """)

                            elif poste_cat == "Défenseurs latéraux":
                                st.markdown("""
                                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                                - **PrgP_per90**: Progressive passes per 90 minutes  
                                - **Cmp%**: Pass completion percentage  
                                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                                - **PrgC_per90**: Progressive carries per 90 minutes  
                                - **Err_per90**: Errors leading to a shot  
                                - **Tkl%**: Tackle success rate  
                                - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                                - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                                - **CrdY_per90**: Yellow cards per 90 minutes  
                                - **Won_per90**: Aerial duels won per 90 minutes  
                                - **Won%**: Aerial duel success rate  
                                """)

                            elif poste_cat == "Milieux de terrain":
                                st.markdown("""
                                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                                - **PrgP_per90**: Progressive passes per 90 minutes  
                                - **PrgR_per90**: Progressive passes received per 90 minutes  
                                - **Cmp%**: Pass completion percentage  
                                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                                - **PrgC_per90**: Progressive carries per 90 minutes  
                                - **Fld_per90**: Fouls drawn per 90 minutes  
                                - **Err_per90**: Errors leading to a shot  
                                - **Tkl%**: Tackle success rate  
                                - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                                - **CrdY_per90**: Yellow cards per 90 minutes  
                                - **Won%**: Aerial duel success rate
                                """)

                            elif poste_cat == "Milieux offensifs / Ailiers":
                                st.markdown("""
                                - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                                - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                                - **PrgP_per90**: Progressive passes per 90 minutes  
                                - **PrgR_per90**: Progressive passes received per 90 minutes  
                                - **Cmp%**: Pass completion percentage  
                                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                                - **Succ_per90**: Successful dribbles per 90 minutes  
                                - **Succ%**: Dribble success rate  
                                - **PrgC_per90**: Progressive carries per 90 minutes  
                                - **Fld_per90**: Fouls drawn per 90 minutes  
                                - **Dis_per90**: Dispossessions per 90 minutes
                                """)

                            elif poste_cat == "Attaquants":
                                st.markdown("""
                                - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                                - **Sh_per90**: Shots attempted per 90 minutes  
                                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                                - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                                - **G/Sh**: Goals per shot  
                                - **PrgP_per90**: Progressive passes per 90 minutes  
                                - **PrgR_per90**: Progressive passes received per 90 minutes  
                                - **Cmp%**: Pass completion percentage  
                                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                                - **Succ_per_90**: Successful dribbles per 90 minutes  
                                - **PrgC_per90**: Progressive carries per 90 minutes  
                                - **Dis_per90**: Dispossessions per 90 minutes 
                                """)

                    # Radar generation
                    if poste_cat and poste_cat in category_stats_player:
                        stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]  # We retrieve the stat categories according to position.

                        # Filter player statistics by position category
                        if 'poste_cat' not in df.columns:
                            df = df.copy()
                            df['poste_cat'] = df['position'].map(position_category)

                        radar_df = df[df['poste_cat'] == poste_cat][['player_name'] + stats_cols].copy()
                        radar_df = radar_df.dropna(subset=stats_cols).set_index('player_name')

                        # We ensure that the two players being compared are included in the reference
                        for p, pdata in [(player1, player1_data), (player2, player2_data)]:
                            if p not in radar_df.index:
                                radar_df.loc[p] = pd.Series(pdata).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        # Each statistic is evaluated according to its position relative to other players in the same position
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        invert_stats = globals().get("invert_stats", set()) # We are reversing the metrics where ‘smaller = better’
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        # We normalise the values by rank for the radar.
                        player1_norm = rank_pct.loc[player1].reindex(stats_cols).fillna(0)
                        player2_norm = rank_pct.loc[player2].reindex(stats_cols).fillna(0)

                        player1_rating = player1_data.get("rating", None)
                        player2_rating = player2_data.get("rating", None)

                        # Rating calculation if available
                        rating1_text = f"Rating : {round(player1_rating)}" if player1_rating is not None else ""
                        rating2_text = f"Rating : {round(player2_rating)}" if player2_rating is not None else ""
                        
                        # Title and radar display
                        st.markdown(f"<h4 style='text-align: center;'>Radar comparison : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",unsafe_allow_html=True)
                        
                        # Creating the advanced statistics pizza plot
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player1_norm * 100,median_values=player2_norm * 100,
                            title=f"Advanced statistics of {player1} vs {player2}",legend_labels=(player1, player2)
                        )

                        # List of score columns by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls","score_short_clearance",
                             "score_long_clearance", "score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble", "score_projection",
                             "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        # We keep only the columns of interest for the post
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                        # Check if these columns exist for both players
                        if all((col in player1_data) and (col in player2_data) for col in pizza_cols):

                            player1_values = [player1_data[col] for col in pizza_cols]
                            player2_values = [player2_data[col] for col in pizza_cols]

                            # Checks that data is valid for both players
                            player1_scaled = [v if pd.notna(v) else 0 for v in player1_values]
                            player2_scaled = [v if pd.notna(v) else 0 for v in player2_values]

                            # Creation of comparative radar (pizza plot) for the basic statistics
                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,data_values=player1_scaled,median_values=player2_scaled,
                                title=f"Basic statistics of {player1} vs {player2}",legend_labels=(player1, player2)
                            )

                        # Display in Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)
        
        else:
            st.markdown("<h4 style='text-align: center;'>🥊 Comparación de dos jugadores</h4>", unsafe_allow_html=True)
            # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            player_names = sorted(df['player_name'].dropna().unique().tolist())  # Ordenar por nombre

            st.sidebar.markdown("### Selección de jugadores")  # Selección en la barra lateral

            player1 = st.sidebar.selectbox("Primer jugador:", [''] + player_names, key="player1")  # Jugador 1

            if not player1:
                # Sin selección → imagen de intro
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para elegir el idioma y los jugadores a analizar")

            if player1:
                # Datos del primer jugador
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None) 

                sub_positions_same_cat = [pos for pos, cat in position_category.items() if cat == poste_cat] # Todas las position de la misma categoría

                # Filtrar jugadores de la misma categoría
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]

                player2 = st.sidebar.selectbox("Segundo jugador (misma posición):", [''] + player2_names, key="player2")  # Jugador 2

                if not player2:
                    image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_comparison.jpg")
                    st.image(image_path)
                    st.info("Despliega la barra lateral para elegir el idioma y los jugadores a analizar")

                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0]  # Datos del segundo jugador

                    st.markdown("<h4 style='text-align: center;'>Perfiles de los jugadores</h4>", unsafe_allow_html=True) # Perfiles de los jugadores

                    for pdata in [player1_data, player2_data]:
                        # Traducciones mostradas en ES y recuperación de datos
                        pais = translate_country(pdata['nationality'], lang="es")
                        puesto = translate_position(pdata['position'], lang="es")
                        foot_lbl = translate_foot(pdata.get("foot"), lang="es")
                        position_other_translated = translate_position_list(pdata.get("position_other"), lang="es")
                        agent_name = pdata.get("agent_name")
                        agent_name = None if (agent_name is None or (isinstance(agent_name, float) and pd.isna(agent_name)) or str(agent_name).strip() == "") else str(agent_name).strip()
                        outfitter = pdata.get("outfitter")
                        outfitter = None if (outfitter is None or (isinstance(outfitter, float) and pd.isna(outfitter)) or str(outfitter).strip() == "") else str(outfitter).strip()

                        foot_lbl = foot_lbl if foot_lbl is not None else "Desconocido"
                        position_other = position_other_translated if position_other_translated is not None else "Ninguno"
                        agent_name = agent_name if agent_name is not None else "Desconocido"
                        outfitter = outfitter if outfitter is not None else "Desconocido"

                        st.markdown(f"""
                        <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                        <div style="flex: 1; text-align: center; min-width: 180px;">
                            <img src="{pdata['imageUrl']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Nombre:</strong> {pdata['player_name']}</p>
                            <p><strong>Edad:</strong> {int(pdata['Age']) if pd.notna(pdata['Age']) else "-"}</p>
                            <p><strong>País:</strong> {pais}</p>
                            <p><strong>Club:</strong> {pdata['club_name']}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Posición:</strong> {puesto}</p>
                            <p><strong>Altura:</strong> {int(pdata['height']) if pd.notna(pdata['height']) else "-" } cm</p>
                            <p><strong>Valor de mercado:</strong> {format_market_value(pdata['marketValue'])}</p>
                            <p><strong>Fin de contrato:</strong> {pdata['contract'] if pd.notna(pdata['contract']) else "-"}</p>
                        </div>

                        <div style="flex: 2; min-width: 280px;">
                            <p><strong>Pie fuerte :</strong> {foot_lbl}</p>
                            <p><strong>Otro(s) puesto(s) :</strong> {position_other_translated}</p>
                            <p><strong>Agente :</strong> {agent_name}</p>
                            <p><strong>Fabricante de equipos :</strong> {outfitter}</p>
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Glosario
                    with st.expander(" Glosario de estadísticas"):
                        if poste_cat:

                            if poste_cat == "Gardiens de but":
                                st.markdown("""
                                - **GA_per90**: Goles encajados por 90 minutos 
                                - **PSxG_per90**: Post-Shot Expected Goals por 90 minutos
                                - **/90 (PSxG-GA/90)**: Diferencia entre PSxG y goles encajados por 90 minutos
                                - **Save%**: Porcentaje de paradas  
                                - **PSxG+/-**: Diferencia entre PSxG (xG post-tiro) y goles encajados  
                                - **Err_per90**: Errores que conducen a un tiro rival por 90 minutos
                                - **Launch%**: Porcentaje de pases largos  
                                - **AvgLen**: Longitud media de pase (yardas)  
                                - **Cmp%**: Porcentaje de pases completados  
                                - **AvgDist**: Distancia media de pase (yardas)  
                                - **#OPA_per90**: Acciones defensivas fuera del área por 90 minutos  
                                - **Stp%**: Porcentaje de centros detenidos dentro del área  
                                """)

                            elif poste_cat == "Défenseurs centraux":
                                st.markdown("""
                                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                                - **PrgP_per90**: Pases progresivos por 90 minutos
                                - **Cmp%**: Porcentaje de pases completados
                                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                                - **PrgC_per90**: Conducciones progresivas por 90 minutos
                                - **Err_per90**: Errores que conducen a un tiro rival
                                - **Tkl%**: Porcentaje de éxito en entradas
                                - **Int_per90**: Intercepciones por 90 minutos
                                - **Tkl_per90**: Entradas por 90 minutos
                                - **CrdY_per90**: Tarjetas amarillas por 90 minutos
                                - **Won_per90**: Duelos aéreos ganados por 90 minutos
                                - **Won%**: Porcentaje de duelos aéreos ganados
                                """)

                            elif poste_cat == "Défenseurs latéraux":
                                st.markdown("""
                                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                                - **PrgP_per90**: Pases progresivos por 90 minutos
                                - **Cmp%**: Porcentaje de pases completados
                                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                                - **PrgC_per90**: Conducciones progresivas por 90 minutos
                                - **Err_per90**: Errores que conducen a un tiro rival
                                - **Tkl%**: Porcentaje de éxito en entradas 
                                - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                                - **Tkl_per90_Padj**: Entradas por 90 minutos ajustadas a la posesión
                                - **CrdY_per90**: Tarjetas amarillas por 90 minutos
                                - **Won_per90**: Duelos aéreos ganados por 90 minutos
                                - **Won%**: Porcentaje de duelos aéreos ganados 
                                """)

                            elif poste_cat == "Milieux de terrain":
                                st.markdown("""
                                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                                - **PrgP_per90**: Pases progresivos por 90 minutos
                                - **PrgR_per90**: Recepciones progresivas por 90 minutos
                                - **Cmp%**: Porcentaje de pases completados
                                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                                - **PrgC_per90**: Conducciones progresivas por 90 minutos
                                - **Fld_per90**: Faltas recibidas por 90 minutos
                                - **Err_per90**: Errores que conducen a un tiro rival
                                - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                                - **CrdY_per90**: Tarjetas amarillas por 90 minutos
                                - **Won%**: Porcentaje de duelos aéreos ganados 
                                """)

                            elif poste_cat == "Milieux offensifs / Ailiers":
                                st.markdown("""
                                - **npxG_per90**: xG sin penaltis por 90 minutos
                                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                                - **G-xG_per90**: G - xG por 90 minutos
                                - **PrgP_per90**: Pases progresivos por 90 minutos
                                - **PrgR_per90**: Recepciones progresivas por 90 minutos
                                - **Cmp%**: Porcentaje de pases completados
                                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                                - **Succ_per90**: Regates exitosos por 90 minutos
                                - **Succ%**: Porcentaje de regates exitosos
                                - **PrgC_per90**: Conducciones progresivas por 90 minutos
                                - **Fld_per90**: Faltas recibidas por 90 minutos
                                - **Dis_per90**: Balones perdidos por 90 minutos
                                """)

                            elif poste_cat == "Attaquants":
                                st.markdown("""
                                - **npxG_per90**: xG sin penaltis por 90 minutos
                                - **Sh_per90**: Tiros por 90 minutos
                                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                                - **G-xG_per90**: G - xG por 90 minutos
                                - **G/Sh**: Goles por tiro  
                                - **PrgP_per90**: Pases progresivos por 90 minutos  
                                - **PrgR_per90**: Recepciones progresivas por 90 minutos
                                - **Cmp%**: Porcentaje de pases completados
                                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                                - **Succ_per_90**: Regates exitosos por 90 minutos  
                                - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                                - **Dis_per90**: Balones perdidos por 90 minutos  
                                """)

                    # Radar comparativo
                    if poste_cat and poste_cat in category_stats_player:
                        stats_cols = [col for col in category_stats_player[poste_cat] if col in df.columns]

                        # Añadir columna poste_cat si no existe
                        if 'poste_cat' not in df.columns:
                            df = df.copy()
                            df['poste_cat'] = df['position'].map(position_category)

                        radar_df = df[df['poste_cat'] == poste_cat][['player_name'] + stats_cols].copy()
                        radar_df = radar_df.dropna(subset=stats_cols).set_index('player_name')

                        # Asegurar que ambos jugadores estén presentes
                        for p, pdata in [(player1, player1_data), (player2, player2_data)]:
                            if p not in radar_df.index:
                                radar_df.loc[p] = pd.Series(pdata).reindex(stats_cols)

                        radar_vals = radar_df[stats_cols].apply(pd.to_numeric, errors='coerce')

                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True) # Percentiles (0 = peor, 1 = mejor)

                        invert_stats = globals().get("invert_stats", set()) # Invertir métricas donde "más pequeño = mejor"
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        # Valores normalizados
                        player1_norm = rank_pct.loc[player1].reindex(stats_cols).fillna(0)
                        player2_norm = rank_pct.loc[player2].reindex(stats_cols).fillna(0)

                        # Notas (si existen)
                        player1_rating = player1_data.get("rating", None)
                        player2_rating = player2_data.get("rating", None)
                        rating1_text = f"Nota: {round(player1_rating)}" if player1_rating is not None else ""
                        rating2_text = f"Nota: {round(player2_rating)}" if player2_rating is not None else ""

                        # Título
                        st.markdown(f"<h4 style='text-align: center;'>Radar comparativo: {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",unsafe_allow_html=True)

                        # Radar de estadísticas avanzadas
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,data_values=player1_norm * 100,median_values=player2_norm * 100,
                            title=f"Estadísticas avanzadas de {player1} vs {player2}",legend_labels=(player1, {player2})
                        )

                        # Columnas de puntuación por puesto
                        if poste_cat == "Gardiens de but":
                            pizza_cols = ["score_goal_scoring_conceded", "score_efficiency", "score_error_fouls","score_short_clearance",
                             "score_long_clearance", "score_positioning", "score_aerial_defense"]
                        else:
                            pizza_cols = ["score_goal_scoring_created", "score_finish", "score_building", "score_creation","score_dribble", "score_projection",
                             "score_defensive_actions", "score_waste","score_faults_committed", "score_provoked_fouls", "score_aerial"]

                        # Mantener solo columnas presentes
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [translate_base_stat(col.replace("score_", ""), lang="es") for col in pizza_cols]

                        # Verificar columnas para ambos jugadores
                        if all((col in player1_data) and (col in player2_data) for col in pizza_cols):
                            player1_values = [player1_data[col] for col in pizza_cols]
                            player2_values = [player2_data[col] for col in pizza_cols]

                            player1_scaled = [v if pd.notna(v) else 0 for v in player1_values]
                            player2_scaled = [v if pd.notna(v) else 0 for v in player2_values]

                            # Radar de estadísticas básicas
                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,data_values=player1_scaled,median_values=player2_scaled,
                                title=f"Estadísticas básicas de {player1} vs {player2}",legend_labels=(player1, player2)
                            )

                        # Mostrar en Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)

    elif selected == "Stats +":
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏅 Classement des joueurs (0-100) pour les statistiques aggrégées par catégorie selon leur poste</h4>", unsafe_allow_html=True) # Affichage du titre de la page
            # Récupération des données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # Récupération des colonnes "score_" + "rating"
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            fr_map = base_stat_translation.get("fr", {}) # Traduction pour l'affichage

            translated_stats = [
                "Note" if col == "rating"
                else fr_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))
            
            selected_stat_display = st.sidebar.selectbox("Choisissez une statistique :", [""] + translated_stats) # Demande à l'utilisateur du choix de statistique
            
            selected_stat = stat_name_mapping.get(selected_stat_display, None)

            if not selected_stat:
                # Si la métrique est selectionné, nous cachons l'image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking_basis.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")

                    
            if selected_stat:
                # Début de la sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filtres")
                    
                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                    filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                    # Filtre Poste
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options_fr = [""] + [translate_position(p, lang="fr") for p in poste_options_raw]
                    poste_fr = st.selectbox("Poste", poste_options_fr)

                    if poste_fr:
                        idx = poste_options_fr.index(poste_fr) - 1
                        poste_en = poste_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["position"] == poste_en]

                    # Filtre Championnat
                    championnat_options = sorted(filtered_df["Comp"].dropna().unique())
                    championnat = st.selectbox("Championnat", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["Comp"] == championnat]

                    # Filtre Club
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Filtre Pays
                    pays_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pays_options_fr = [""] + [translate_country(p, lang="fr") for p in pays_options_raw]
                    pays_fr = st.selectbox("Pays", pays_options_fr, placeholder="")

                    if pays_fr:
                        idx = pays_options_fr.index(pays_fr) - 1  # -1 à cause de l'option vide
                        pays_en = pays_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["nationality"] == pays_en]

                    # Filtre Tranche d’âge (création dynamiquement des tranches d'âge disponibles)
                    tranche_options = [""]

                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 ans")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 ans")
                    if any(ages >= 30):
                        tranche_options.append("30 ans et +")

                    age_group = st.selectbox("Tranche d'âge", tranche_options) # Sélecteur de la trancge d'âge

                    # Appliquer le filtre si sélectionné
                    if age_group:
                        if age_group == "< 23 ans":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 ans":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 ans et +":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Filtre de valeur marchande
                    valeur_min_possible = 0
                    valeur_max_possible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valeur_max = st.slider("Valeur marchande maximum (€)",valeur_min_possible,valeur_max_possible,valeur_max_possible,step=100000,format="%d")

                    st.markdown(f"Valeur maximum sélectionné : **{format_market_value(valeur_max)}**") # Affichage du choix de l'utilisateur
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]

                # Définir les statistiques spécifiques aux gardiens
                goalkeeper_stats = ["goal_scoring_conceded", "efficiency", "error_fouls","short_clearance", "long_clearance", "positioning", "aerial_defense"]

                # Liste de colonnes
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue','contract','position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Filtrage conditionnel selon la statistique sélectionnée
                if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                else:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="fr"))

                # Traduction du pays du joueur dans la table
                df_stat['nationality'] = df_stat['nationality'].apply(lambda x: translate_country(x, lang="fr"))
                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value) # Utilisation du format de market_value
                
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Ordonner les données du plus grand au plus petit

                top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

                # Ordre podium et médailles
                podium_order = [0, 1, 2]
                medals = ["🥇","🥈", "🥉"]

                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        stat = round(player[selected_stat]) if pd.notna(player[selected_stat]) else "-"
                        image_url = player['imageUrl']
                        image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                        player_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                            "</div>"
                        )
                        podium_html += player_html

                podium_html += "</div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # Choix des colonnes dans la table
                final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
                final_df = final_df[['player_name', 'Statistique', 'Age', 'nationality', 'club_name', 'position','marketValue', 'contract']]

                # Traduction des colonnes en français
                col_labels_fr = {"player_name": "Joueur","Statistique": "Statistique","Age": "Âge","nationality": "Nationalité","club_name": "Club",
                    "position": "Poste","marketValue": "Valeur marchande","contract": "Contrat"}
                final_df = final_df.rename(columns=col_labels_fr)

                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":

            st.markdown("<h4 style='text-align: center;'>🏅 Player rankings (0-100) for aggregate statistics by category according to their position</h4>", unsafe_allow_html=True) # Display title
            # Collect the data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # Retrieve “score_” + “rating” columns
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            translated_stats = [format_stat_name(col) for col in all_stats_raw] # Apply format to names for display

            stat_name_mapping = dict(zip(translated_stats, all_stats_raw)) # Create display mapping → real name

            selected_stat_display = st.sidebar.selectbox("Select a statistic :", [""] + translated_stats) # Selector in the sidebar

            selected_stat = stat_name_mapping.get(selected_stat_display, None) # Recover the real name of the column

            if not selected_stat:
                # If the metric is selected, we hide the image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking_basis.jpg")
                st.image(image_path)
                st.info("Scroll down the sidebar to select the language, metric and filters of your choice")
                    
                    
            if selected_stat:
                # Top of the sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filters")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filter by selected statistic

                    filtered_df = df_with_stat.copy()  # Starting point for filters

                    # Position filter
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options = st.selectbox("Position", [""] + poste_options_raw )

                    if poste_options:
                        filtered_df = filtered_df[filtered_df["position"] == poste_options]

                    # League filter
                    championnat_options = sorted(filtered_df["Comp"].dropna().unique())
                    championnat = st.selectbox("League", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["Comp"] == championnat]

                    # Club filter
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Country filter
                    pays_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pays_options = st.selectbox("Country", [""] + pays_options_raw )

                    if pays_options:
                        filtered_df = filtered_df[filtered_df["nationality"] == pays_options]

                    # Age group filter (dynamically create the age ranges available)
                    tranche_options = [""]
                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 yrs")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 yrs")
                    if any(ages >= 30):
                        tranche_options.append("30 yrs and +")

                    age_group = st.selectbox("Age group", tranche_options) # Selector

                    # Apply filter if selected
                    if age_group:
                        if age_group == "< 23 yrs":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 yrs":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 yrs abd +":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Market value filter
                    valeur_min_possible = 0
                    valeur_max_possible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valeur_max = st.slider("Maximum market value (€)",valeur_min_possible,valeur_max_possible,valeur_max_possible,step=100000,format="%d")

                    st.markdown(f"Maximum value selected: **{format_market_value(valeur_max)}**") # Display the choice of the user
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]
            
                # Define statistics specific to goalkeepers
                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]
                # Selecting columns
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','position','Comp', 'marketValue','contract', selected_stat]
                ].dropna(subset=[selected_stat])

                # Conditional filtering by selected statistic
                if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                else:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value) # Format market value
                    
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Order data from largest to smallest

                top3 = df_stat.head(3).reset_index(drop=True) # Displaying podium

                podium_order = [0, 1, 2]  # 1st, 2nd, 3rd
                medals = ["🥇", "🥈", "🥉"]

                # Start of scrollable container
                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                # Creating player blocks
                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        image_url = player['imageUrl']
                        stat_val = round(player[selected_stat]) if pd.notna(player[selected_stat]) else "-"
                        stat_label = format_stat_name(selected_stat)

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{stat_label}:</strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += player_html

                podium_html += "</div>" # Closing the container

                st.markdown(podium_html, unsafe_allow_html=True) # Final display

                # We display the table with the columns desired
                final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
                final_df = final_df[['player_name', 'Statistic', 'Age', 'nationality', 'club_name', 'position', 'marketValue', 'contract']]

                # We clean all the columns
                col_labels_en = {"player_name": "Player","Statistic": "Statistic","Age": "Age","nationality": "Country","club_name": "Club",
                    "position": "Position","marketValue": "Market value","contract": "Contract"}
                final_df = final_df.rename(columns=col_labels_en)

                st.dataframe(final_df, use_container_width=True)
        
        else:
            # Página en español
            st.markdown("<h4 style='text-align: center;'>🏅 Clasificación de jugadores (0-100) para estadísticas agregadas por categoría según su posición</h4>", unsafe_allow_html=True)
            # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # Columnas "score_" + "rating"
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            # Traducción para la visualización
            es_map = base_stat_translation.get("es", {})
            translated_stats = [
                "Nota" if col == "rating"
                else es_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

            selected_stat_display = st.sidebar.selectbox("Elige una estadística:", [""] + translated_stats)
            selected_stat = stat_name_mapping.get(selected_stat_display, None)

            if not selected_stat:
                # Imagen e info si no hay métrica seleccionada
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking_basis.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma, la métrica y los filtros que quieras")

            if selected_stat:
                # Sidebar de filtros
                with st.sidebar:
                    st.markdown("### 🎯 Filtros")

                    df_with_stat = df.dropna(subset=[selected_stat])  # Filtrar por la estadística seleccionada
                    filtered_df = df_with_stat.copy()

                    # Filtro Posición
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options_es = [""] + [translate_position(p, lang="es") for p in poste_options_raw]
                    poste_es = st.selectbox("Posición", poste_options_es)

                    if poste_es:
                        idx = poste_options_es.index(poste_es) - 1
                        poste_en = poste_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["position"] == poste_en]

                    # Filtro Liga
                    campeonato_options = sorted(filtered_df["Comp"].dropna().unique())
                    campeonato = st.selectbox("Liga", [""] + campeonato_options)
                    if campeonato:
                        filtered_df = filtered_df[filtered_df["Comp"] == campeonato]

                    # Filtro Club
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)
                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Filtro País
                    pays_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pays_options_es = [""] + [translate_country(p, lang="es") for p in pays_options_raw]
                    pais_es = st.selectbox("País", pays_options_es, placeholder="")
                    if pais_es:
                        idx = pays_options_es.index(pais_es) - 1  # -1 por la opción vacía
                        pais_en = pays_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["nationality"] == pais_en]

                    # Filtro Tramo de edad (dinámico)
                    tranche_options = [""]
                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 años")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 años")
                    if any(ages >= 30):
                        tranche_options.append("30 años o más")

                    age_group = st.selectbox("Tramo de edad", tranche_options)

                    # Aplicar filtro de edad
                    if age_group:
                        if age_group == "< 23 años":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 años":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 años o más":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Filtro de valor de mercado
                    valor_min_posible = 0
                    valor_max_posible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valor_max = st.slider("Valor de mercado máximo (€)",valor_min_posible,valor_max_posible,valor_max_posible,step=100000,format="%d")

                    st.markdown(f"Valor máximo seleccionado: **{format_market_value(valor_max)}**")
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valor_max]

                # Stats específicas de porteros
                goalkeeper_stats = ["goal_scoring_conceded", "efficiency", "error_fouls","short_clearance", "long_clearance", "positioning", "aerial_defense"]

                # Subconjunto de columnas
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue', 'contract','position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Filtrado condicional según la estadística seleccionada
                if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                else:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                # Posición en ES (solo visual)
                df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="es"))

                # País en ES (solo visual)
                df_stat['nationality'] = df_stat['nationality'].apply(lambda x: translate_country(x, lang="es"))

                # Formato del valor de mercado
                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value)

                # Ordenar de mayor a menor
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

                # Top 3 (podio)
                top3 = df_stat.head(3).reset_index(drop=True)
                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        stat = round(player[selected_stat]) if pd.notna(player[selected_stat]) else "-"
                        image_url = player['imageUrl']
                        image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                        player_html = (
                            "<div style='min-width: 200px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                            "</div>"
                        )
                        podium_html += player_html

                podium_html += "</div>"
                st.markdown(podium_html, unsafe_allow_html=True)

                # Tabla final (renombrar solo la columna de la métrica)
                final_df = df_stat.rename(columns={selected_stat: 'Estadística'})
                final_df = final_df[['player_name', 'Estadística', 'Age', 'nationality', 'club_name','position', 'marketValue', 'contract']]

                # Traducción de las columnas al español
                col_labels_es = {"player_name": "Jugador","Estadística": "Estadística","Age": "Edad","nationality": "Nacionalidad","club_name": "Club",
                    "position": "Posición","marketValue": "Valor de mercado","contract": "Contrato",}
                final_df = final_df.rename(columns=col_labels_es)

                st.dataframe(final_df, use_container_width=True)

    elif selected == "Stats":
        # Page en français
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏆 Classement des joueurs pour les statistiques brutes</h4>", unsafe_allow_html=True) # Affichage du titre de la page
            # Récupération des données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            all_stats = sorted(set(stat for stats in category_stats_player.values() for stat in stats if stat in df.columns)) # Liste des statistiques disponibles

            selected_stat = st.sidebar.selectbox("Choisissez une statistique :", [""] + all_stats) # Choix de la statistique dans la sidebar
            
            if not selected_stat:
                # Si la métrique est selectionné, nous cachons l'image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking.jpg")
                st.image(image_path)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")
                    
            if selected_stat:
                # Début de la sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filtres")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                    filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                    # Filtre Poste
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options_fr = [""] + [translate_position(p, lang="fr") for p in poste_options_raw]
                    poste_fr = st.selectbox("Poste", poste_options_fr)

                    if poste_fr:
                        idx = poste_options_fr.index(poste_fr) - 1
                        poste_en = poste_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["position"] == poste_en]

                    # Filtre Championnat
                    championnat_options = sorted(filtered_df["Comp"].dropna().unique())
                    championnat = st.selectbox("Championnat", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["Comp"] == championnat]

                    # Filtre Club
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Filtre Pays
                    pays_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pays_options_fr = [""] + [translate_country(p, lang="fr") for p in pays_options_raw]
                    pays_fr = st.selectbox("Pays", pays_options_fr, placeholder="")

                    if pays_fr:
                        idx = pays_options_fr.index(pays_fr) - 1  # -1 à cause de l'option vide
                        pays_en = pays_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["nationality"] == pays_en]

                    # Filtre Tranche d’âge (créer dynamiquement les tranches d'âge disponibles)
                    tranche_options = [""]
                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 ans")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 ans")
                    if any(ages >= 30):
                        tranche_options.append("30 ans et +")

                    age_group = st.selectbox("Tranche d'âge", tranche_options) # Sélecteur

                    # Appliquer le filtre si sélectionné
                    if age_group:
                        if age_group == "< 23 ans":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 ans":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 ans et +":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Filtre de valeur marchande
                    valeur_min_possible = 0
                    valeur_max_possible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valeur_max = st.slider("Valeur marchande maximum (€)",valeur_min_possible,valeur_max_possible,valeur_max_possible,step=100000,format="%d")

                    st.markdown(f"Valeur maximum sélectionné : **{format_market_value(valeur_max)}**") # Affichage du choix de l'utilisateur
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]

                # Placement du glossaire en sidebar
                with st.sidebar.expander("Glossaire des statistiques"):
                    st.markdown("""
                    ### Gardien de but :
                    - **GA_per90** : Buts encaissés par 90 minutes 
                    - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                    - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                    - **Save%** : Pourcentage d’arrêts effectués  
                    - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                    - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                    - **Launch%** : Pourcentage de passes longues  
                    - **AvgLen** : Longueur moyenne des passes (en yards)  
                    - **Cmp%** : Pourcentage de passes réussies  
                    - **AvgDist** : Distance moyenne des passes (en yards)  
                    - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                    - **Stp%** : Pourcentage de centres arrêtés dans la surface  

                    ### Défenseurs centraux :
                    - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                    - **PrgP_per90** : Passes progressives par 90 minutes
                    - **Cmp%** : Pourcentage de passes réussies
                    - **xAG_per90** : Expected Assisted Goals par 90 minutes
                    - **PrgC_per90** : Conduites progressives par 90 minutes
                    - **Err_per90** : Erreurs menant à un tir adverse
                    - **Tkl%** : Pourcentage de tacles effectués
                    - **Int_per90** : Interceptions par 90 minutes
                    - **Tkl_per90** : Tacles par 90 minutes
                    - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                    - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                    - **CrdY_per90** : Cartons jaunes par 90 minutes
                    - **Won_per90** : Duels aériens gagnés par 90 minutes
                    - **Won%** : Pourcentage de duels aériens gagnés

                    ### Défenseurs latéraux :
                    - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                    - **PrgP_per90** : Passes progressives par 90 minutes
                    - **Cmp%** : Pourcentage de passes réussies
                    - **xAG_per90** : Expected Assisted Goals par 90 minutes
                    - **PrgC_per90** : Conduites progressives par 90 minutes
                    - **Err_per90** : Erreurs menant à un tir adverse
                    - **Tkl%** : Pourcentage de tacles effectués
                    - **Int_per90** : Interceptions par 90 minutes
                    - **Tkl_per90** : Tacles par 90 minutes
                    - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                    - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                    - **CrdY_per90** : Cartons jaunes par 90 minutes
                    - **Won_per90** : Duels aériens gagnés par 90 minutes
                    - **Won%** : Pourcentage de duels aériens gagnés 

                    ### Milieux de terrain :
                    - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                    - **PrgP_per90** : Passes progressives par 90 minutes
                    - **PrgR_per90** : Passes progressives reçues par 90 minutes
                    - **Cmp%** : Pourcentage de passes réussies
                    - **xAG_per90** : Expected Assisted Goals par 90 minutes
                    - **PrgC_per90** : Conduites progressives par 90 minutes
                    - **Fld_per90** : Fautes subies par 90 minutes
                    - **Err_per90** : Erreurs menant à un tir adverse
                    - **Tkl%** : Pourcentage de tacles effectués
                    - **Int_per90** : Interceptions par 90 minutes
                    - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                    - **CrdY_per90** : Cartons jaunes par 90 minutes
                    - **Won%** : Pourcentage de duels aériens gagnés 

                    ### Milieux offensifs / Ailiers :
                    - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                    - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                    - **G-xG_per90** : Expected Goals par 90 minutes
                    - **PrgP_per90** : Passes progressives par 90 minutes
                    - **PrgR_per90** : Passes progressives reçues par 90 minutes
                    - **Cmp%** : Pourcentage de passes réussies
                    - **xAG_per90** : Expected Assisted Goals par 90 minutes
                    - **Succ_per90** : Dribbles réussis par 90 minutes
                    - **Succ%** : Pourcentage de dribbles réussis
                    - **PrgC_per90** : Conduites progressives par 90 minutes
                    - **Fld_per90** : Fautes subies par 90 minutes
                    - **Dis_per90** : Ballons perdus par 90 minutes

                    ### Attaquants :
                    - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                    - **Sh_per90** : Tirs tentés par 90 minutes
                    - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                    - **G-xG_per90** : Expected Goals par 90 minutes
                    - **G/Sh** : Buts par tir  
                    - **PrgP_per90** : Passes progressives par 90 minutes  
                    - **PrgR_per90** : Passes progressives reçues par 90 minutes
                    - **Cmp%** : Pourcentage de passes réussies
                    - **xAG_per90** : Expected Assisted Goals par 90 minutes
                    - **Succ_per_90** : Dribbles réussis par 90 minutes  
                    - **PrgC_per90** : Conduites progressives par 90 minutes  
                    - **Dis_per90** : Ballons perdus par 90 minutes  
                    """)

                # Appliquer des conditions minimales sur les métriques spécifiques
                thresholds = {'Cmp%': ('Cmp', 50),'Tkl%': ('Tkl', 7),'Won%': ('Won', 6),'Succ%': ('Succ', 6)}

                if selected_stat in thresholds:
                    col, min_value = thresholds[selected_stat]
                    
                    # S'assurer que la colonne existe et que les valeurs sont numériques
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                        st.markdown(f"<small><strong>Filtre : {col} > {min_value}</strong></small>", unsafe_allow_html=True)

                # Liste de colonnes
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue','contract','position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Traduction du pays du joueur dans la table
                df_stat['nationality'] = df_stat['nationality'].apply(lambda x: translate_country(x, lang="fr"))
                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value) # Utilisation du format de market_value

                # Filtrage spécial si la statistique sélectionnée est reservée aux gardiens
                if selected_stat in ['Saves_per90', 'Save%', '/90', 'PSxG+/-','AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%']:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
        
                # Filtrage spécial si la statistique sélectionnée est GA_per90
                if selected_stat == 'GA_per90':
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
                else:
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

                # Cas particuliers : exclusion des gardiens pour certaines statistiques
                if selected_stat in ['Won%', 'Tkl%','Succ%']:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="fr"))
                top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        image_url = player['imageUrl']
                        stat_val = round(player[selected_stat], 2) if pd.notna(player[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat}:</strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += player_html

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # Choix des colonnes dans la table
                final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
                final_df = final_df[['player_name', 'Statistique', 'Age', 'nationality', 'club_name', 'position','marketValue', 'contract']]

                # Traduction des colonnes en français
                col_labels_fr = {"player_name": "Joueur","Statistique": "Statistique","Age": "Âge","nationality": "Nationalité","club_name": "Club",
                    "position": "Poste","marketValue": "Valeur marchande","contract": "Contrat"}
                final_df = final_df.rename(columns=col_labels_fr)

                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🏆 Player rankings for raw statistics</h4>", unsafe_allow_html=True) # Display the title
            
            # Recovering data
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)

            all_stats = sorted(set(stat for stats in category_stats_player.values() for stat in stats if stat in df.columns)) # List of available statistics

            selected_stat = st.sidebar.selectbox("Choose a metric :", [""] + all_stats) # Choice of statistics in the sidebar
            
            if not selected_stat:
                # If the metric is selected, we hide the image
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking.jpg")
                st.image(image_path)
                st.info("Scroll down the sidebar to select the language, metric and filters of your choice")
                    
            if selected_stat:
                # Top of the sidebar
                with st.sidebar:
                    st.markdown("### 🎯 Filters")

                    df_with_stat = df.dropna(subset=[selected_stat]) # Filter by selected statistic

                    filtered_df = df_with_stat.copy()  # Starting point for filters

                    # Position filter
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options = st.selectbox("Position", [""] + poste_options_raw )

                    if poste_options:
                        filtered_df = filtered_df[filtered_df["position"] == poste_options]

                    # League filter
                    championnat_options = sorted(filtered_df["Comp"].dropna().unique())
                    championnat = st.selectbox("League", [""] + championnat_options)

                    if championnat:
                        filtered_df = filtered_df[filtered_df["Comp"] == championnat]

                    # Club filter
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)

                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Country filter
                    pays_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pays_options = st.selectbox("Country", [""] + pays_options_raw )

                    if pays_options:
                        filtered_df = filtered_df[filtered_df["nationality"] == pays_options]

                    # Age group filter (dynamically create the age ranges available)
                    tranche_options = [""]
                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 yrs")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 yrs")
                    if any(ages >= 30):
                        tranche_options.append("30 yrs and +")

                    age_group = st.selectbox("Age group", tranche_options) # Selector

                    # Apply filter if selected
                    if age_group:
                        if age_group == "< 23 yrs":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 yrs":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 yrs abd +":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Market value filter
                    valeur_min_possible = 0
                    valeur_max_possible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valeur_max = st.slider("Maximum market value (€)",valeur_min_possible,valeur_max_possible,valeur_max_possible,step=100000,format="%d")

                    st.markdown(f"Maximum value selected: **{format_market_value(valeur_max)}**") # Display the choice of the user
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]

                # Statistics glossary in the sidebar
                with st.sidebar.expander("Statistics glossary"):
                    st.markdown("""
                    ### Goalkeeper :
                    - **GA_per90**: Goals conceded per 90 minutes  
                    - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                    - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                    - **Save%**: Save percentage  
                    - **PSxG+/-**: Difference between PSxG and goals conceded  
                    - **Err_per90**: Errors leading to a shot per 90 minutes  
                    - **Launch%**: Percentage of long passes  
                    - **AvgLen**: Average pass length (in yards)  
                    - **Cmp%**: Pass completion percentage  
                    - **AvgDist**: Average pass distance (in yards)  
                    - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                    - **Stp%**: Percentage of crosses stopped inside the box 

                    ### Center Back :
                    - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                    - **PrgP_per90**: Progressive passes per 90 minutes  
                    - **Cmp%**: Pass completion percentage  
                    - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                    - **PrgC_per90**: Progressive carries per 90 minutes  
                    - **Err_per90**: Errors leading to a shot  
                    - **Tkl%**: Tackle success rate
                    - **Int_per90**: Interceptions per 90 minutes
                    - **Tkl_per90**: Tackles per 90 minutes
                    - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                    - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                    - **CrdY_per90**: Yellow cards per 90 minutes  
                    - **Won_per90**: Aerial duels won per 90 minutes  
                    - **Won%**: Aerial duel success rate  

                    ### Full-backs :
                    - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                    - **PrgP_per90**: Progressive passes per 90 minutes  
                    - **Cmp%**: Pass completion percentage  
                    - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                    - **PrgC_per90**: Progressive carries per 90 minutes  
                    - **Err_per90**: Errors leading to a shot  
                    - **Tkl%**: Tackle success rate  
                    - **Int_per90**: Interceptions per 90 minutes  
                    - **Tkl_per90**: Tackles per 90 minutes
                    - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                    - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                    - **CrdY_per90**: Yellow cards per 90 minutes  
                    - **Won_per90**: Aerial duels won per 90 minutes  
                    - **Won%**: Aerial duel success rate  

                    ### Midfielders :
                    - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                    - **PrgP_per90**: Progressive passes per 90 minutes  
                    - **PrgR_per90**: Progressive passes received per 90 minutes  
                    - **Cmp%**: Pass completion percentage  
                    - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                    - **PrgC_per90**: Progressive carries per 90 minutes  
                    - **Fld_per90**: Fouls drawn per 90 minutes  
                    - **Err_per90**: Errors leading to a shot  
                    - **Tkl%**: Tackle success rate  
                    - **Int_per90**: Interceptions per 90 minutes
                    - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                    - **CrdY_per90**: Yellow cards per 90 minutes  
                    - **Won%**: Aerial duel success rate

                    ### Attacking midfielders / Wingers :
                    - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                    - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                    - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                    - **PrgP_per90**: Progressive passes per 90 minutes  
                    - **PrgR_per90**: Progressive passes received per 90 minutes  
                    - **Cmp%**: Pass completion percentage  
                    - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                    - **Succ_per90**: Successful dribbles per 90 minutes  
                    - **Succ%**: Dribble success rate  
                    - **PrgC_per90**: Progressive carries per 90 minutes  
                    - **Fld_per90**: Fouls drawn per 90 minutes  
                    - **Dis_per90**: Dispossessions per 90 minutes

                    ### Forwards :
                    - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                    - **Sh_per90**: Shots attempted per 90 minutes  
                    - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                    - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                    - **G/Sh**: Goals per shot  
                    - **PrgP_per90**: Progressive passes per 90 minutes  
                    - **PrgR_per90**: Progressive passes received per 90 minutes  
                    - **Cmp%**: Pass completion percentage  
                    - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                    - **Succ_per_90**: Successful dribbles per 90 minutes  
                    - **PrgC_per90**: Progressive carries per 90 minutes  
                    - **Dis_per90**: Dispossessions per 90 minutes 
                    """)

                # Apply minimum conditions to specific metrics
                thresholds = {
                    'Cmp%': ('Cmp', 50),
                    'Tkl%': ('Tkl', 7),
                    'Won%': ('Won', 6),
                    'Succ%': ('Succ', 6)
                }

                if selected_stat in thresholds:
                    col, min_value = thresholds[selected_stat]
                    
                    # Check that the column exists and that the values are numeric
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                        st.markdown(f"<small><strong>Filter : {col} > {min_value}</strong></small>", unsafe_allow_html=True)

                # Selecting columns
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue','contract','position', selected_stat]
                ].dropna(subset=[selected_stat])

                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value) # Format market value

                # Special filtering if the selected statistic is reserved for goalkeepers
                if selected_stat in ['Saves_per90', 'Save%', '/90', 'PSxG+/-','AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%']:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                    
                # Special filtering if the selected statistic is GA_per90
                if selected_stat == 'GA_per90':
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
                else:
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

                # Special cases: exclusion of goalkeepers for certain statistics
                if selected_stat in ['Won%', 'Tkl%','Succ%']:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                top3 = df_stat.head(3).reset_index(drop=True) # Displaying podium

                # Display the podium
                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        image_url = player['imageUrl']
                        stat_val = round(player[selected_stat], 2) if pd.notna(player[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat}:</strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += player_html

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                # We display the table with the columns desired
                final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
                final_df = final_df[['player_name', 'Statistic', 'Age', 'nationality', 'club_name', 'marketValue', 'contract']]

                # We clean all the columns
                col_labels_en = {"player_name": "Player","Statistic": "Statistic","Age": "Age","nationality": "Country","club_name": "Club",
                    "position": "Position","marketValue": "Market value","contract": "Contract"}
                final_df = final_df.rename(columns=col_labels_en)

                st.dataframe(final_df, use_container_width=True)
        else:
            # Página en español
            st.markdown("<h4 style='text-align: center;'>🏆 Clasificación de jugadores por estadísticas brutas</h4>", unsafe_allow_html=True)
             # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # Lista de estadísticas disponibles
            all_stats = sorted(set(stat for stats in category_stats_player.values() for stat in stats if stat in df.columns))

            # Selección de la estadística en la barra lateral
            selected_stat = st.sidebar.selectbox("Elige una estadística:", [""] + all_stats)

            if not selected_stat:
                image_path = os.path.join(os.path.dirname(__file__), "..", "image", "player_ranking.jpg")
                st.image(image_path)
                st.info("Despliega la barra lateral para seleccionar el idioma, la métrica y los filtros que quieras")

            if selected_stat:
                # Filtros en la barra lateral
                with st.sidebar:
                    st.markdown("### 🎯 Filtros")

                    df_with_stat = df.dropna(subset=[selected_stat])  # Filtrar por la estadística seleccionada
                    filtered_df = df_with_stat.copy()

                    # Filtro Posición
                    poste_options_raw = sorted(filtered_df["position"].dropna().unique())
                    poste_options_es = [""] + [translate_position(p, lang="es") for p in poste_options_raw]
                    poste_es = st.selectbox("Posición", poste_options_es)

                    if poste_es:
                        idx = poste_options_es.index(poste_es) - 1
                        poste_en = poste_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["position"] == poste_en]

                    # Filtro Liga
                    campeonato_options = sorted(filtered_df["Comp"].dropna().unique())
                    campeonato = st.selectbox("Liga", [""] + campeonato_options)
                    if campeonato:
                        filtered_df = filtered_df[filtered_df["Comp"] == campeonato]

                    # Filtro Club
                    club_options = sorted(filtered_df["club_name"].dropna().unique())
                    club = st.selectbox("Club", [""] + club_options)
                    if club:
                        filtered_df = filtered_df[filtered_df["club_name"] == club]

                    # Filtro País
                    pais_options_raw = sorted(filtered_df["nationality"].dropna().unique())
                    pais_options_es = [""] + [translate_country(p, lang="es") for p in pais_options_raw]
                    pais_es = st.selectbox("País", pais_options_es, placeholder="")
                    if pais_es:
                        idx = pais_options_es.index(pais_es) - 1  # -1 por la opción vacía
                        pais_en = pais_options_raw[idx]
                        filtered_df = filtered_df[filtered_df["nationality"] == pais_en]

                    # Filtro Tramo de edad (crear dinámicamente)
                    tranche_options = [""]
                    ages = filtered_df["Age"].dropna()

                    if any(ages < 23):
                        tranche_options.append("< 23 años")
                    if any((ages >= 24) & (ages <= 29)):
                        tranche_options.append("24-29 años")
                    if any(ages >= 30):
                        tranche_options.append("30 años o más")

                    age_group = st.selectbox("Tramo de edad", tranche_options)

                    # Aplicar filtro de edad
                    if age_group:
                        if age_group == "< 23 años":
                            filtered_df = filtered_df[filtered_df["Age"] < 23]
                        elif age_group == "24-29 años":
                            filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                        elif age_group == "30 años o más":
                            filtered_df = filtered_df[filtered_df["Age"] >= 30]

                    # Filtro de valor de mercado
                    valor_min_posible = 0
                    valor_max_posible = int(filtered_df["marketValue"].max()) if not filtered_df["marketValue"].isnull().all() else 10_000_000

                    valor_max = st.slider("Valor de mercado máximo (€)",valor_min_posible,valor_max_posible,valor_max_posible,step=100000,format="%d")

                    st.markdown(f"Valor máximo seleccionado: **{format_market_value(valor_max)}**")
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valor_max]

                # Glosario en la barra lateral
                with st.sidebar.expander("Glosario de estadísticas"):
                    st.markdown("""
                    ### Portero:
                    - **GA_per90**: Goles encajados por 90 minutos  
                    - **PSxG_per90**: Post-Shot Expected Goals por 90 minutos  
                    - **/90 (PSxG-GA/90)**: Diferencia entre PSxG y goles encajados por 90 minutos  
                    - **Save%**: Porcentaje de paradas  
                    - **PSxG+/-**: Diferencia entre PSxG (xG post-tiro) y goles encajados  
                    - **Err_per90**: Errores que conducen a un tiro rival por 90 minutos  
                    - **Launch%**: Porcentaje de pases largos  
                    - **AvgLen**: Longitud media de pase (yardas)  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **AvgDist**: Distancia media de pase (yardas)  
                    - **#OPA_per90**: Acciones defensivas fuera del área por 90 minutos  
                    - **Stp%**: Porcentaje de centros detenidos dentro del área  

                    ### Defensas centrales:
                    - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                    - **PrgP_per90**: Pases progresivos por 90 minutos  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                    - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                    - **Err_per90**: Errores que conducen a un tiro rival  
                    - **Tkl%**: Porcentaje de éxito en entradas  
                    - **Int_per90**: Intercepciones por 90 minutos  
                    - **Tkl_per90**: Entradas por 90 minutos
                    - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                    - **Tkl_per90_Padj**: Entradas por 90 minutos ajustadas a la posesión
                    - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                    - **Won_per90**: Duelos aéreos ganados por 90 minutos  
                    - **Won%**: Porcentaje de duelos aéreos ganados  

                    ### Laterales:
                    - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                    - **PrgP_per90**: Pases progresivos por 90 minutos  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                    - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                    - **Err_per90**: Errores que conducen a un tiro rival  
                    - **Tkl%**: Porcentaje de éxito en entradas  
                    - **Int_per90**: Intercepciones por 90 minutos  
                    - **Tkl_per90**: Entradas por 90 minutos
                    - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                    - **Tkl_per90_Padj**: Entradas por 90 minutos ajustadas a la posesión
                    - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                    - **Won_per90**: Duelos aéreos ganados por 90 minutos  
                    - **Won%**: Porcentaje de duelos aéreos ganados  

                    ### Centrocampistas:
                    - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                    - **PrgP_per90**: Pases progresivos por 90 minutos  
                    - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                    - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                    - **Fld_per90**: Faltas recibidas por 90 minutos  
                    - **Err_per90**: Errores que conducen a un tiro rival  
                    - **Tkl%**: Porcentaje de éxito en entradas  
                    - **Int_per90**: Intercepciones por 90 minutos
                    - **Int_per90_Padj**: Intercepciones por 90 minutos ajustadas a la posesión
                    - **CrdY_per90**: Tarjetas amarillas por 90 minutos  
                    - **Won%**: Porcentaje de duelos aéreos ganados  

                    ### Mediapuntas / Extremos:
                    - **npxG_per90**: xG sin penaltis por 90 minutos  
                    - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                    - **G-xG_per90**: G - xG por 90 minutos  
                    - **PrgP_per90**: Pases progresivos por 90 minutos  
                    - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                    - **Succ_per90**: Regates exitosos por 90 minutos  
                    - **Succ%**: Porcentaje de regates exitosos  
                    - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                    - **Fld_per90**: Faltas recibidas por 90 minutos  
                    - **Dis_per90**: Balones perdidos por 90 minutos  

                    ### Delanteros:
                    - **npxG_per90**: xG sin penaltis por 90 minutos  
                    - **Sh_per90**: Tiros por 90 minutos  
                    - **G-PK_per90**: Goles menos penaltis por 90 minutos  
                    - **G-xG_per90**: G - xG por 90 minutos  
                    - **G/Sh**: Goles por tiro  
                    - **PrgP_per90**: Pases progresivos por 90 minutos  
                    - **PrgR_per90**: Recepciones progresivas por 90 minutos  
                    - **Cmp%**: Porcentaje de pases completados  
                    - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos  
                    - **Succ_per_90**: Regates exitosos por 90 minutos  
                    - **PrgC_per90**: Conducciones progresivas por 90 minutos  
                    - **Dis_per90**: Balones perdidos por 90 minutos  
                    """)

                # Condiciones mínimas en métricas específicas
                thresholds = {'Cmp%': ('Cmp', 50),'Tkl%': ('Tkl', 7),'Won%': ('Won', 6),'Succ%': ('Succ', 6)}

                if selected_stat in thresholds:
                    col, min_value = thresholds[selected_stat]
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                        st.markdown(f"<small><strong>Filtro: {col} > {min_value}</strong></small>", unsafe_allow_html=True)

                # Subconjunto de columnas
                df_stat = filtered_df[['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue', 'contract','position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Traducciones visuales (ES)
                df_stat['nationality'] = df_stat['nationality'].apply(lambda x: translate_country(x, lang="es"))
                df_stat['marketValue'] = df_stat['marketValue'].apply(format_market_value)

                # Filtros especiales para porteros
                if selected_stat in ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%']:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']

                # Caso especial GA_per90 (orden ascendente)
                if selected_stat == 'GA_per90':
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
                else:
                    df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

                # Excluir porteros en métricas % específicas
                if selected_stat in ['Won%', 'Tkl%', 'Succ%']:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                # Posición en ES (visual)
                df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="es"))

                # Top 3 (podio)
                top3 = df_stat.head(3).reset_index(drop=True)
                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['player_name']
                        image_url = player['imageUrl']
                        stat_val = round(player[selected_stat], 2) if pd.notna(player[selected_stat]) else "-"

                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_html = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>{selected_stat}:</strong> {stat_val}</div>"
                            "</div>"
                        )

                        podium_html += player_html

                podium_html += "</div></div>"
                st.markdown(podium_html, unsafe_allow_html=True)

                # Tabla final
                final_df = df_stat.rename(columns={selected_stat: 'Estadística'})
                final_df = final_df[['player_name', 'Estadística', 'Age', 'nationality', 'club_name','position', 'marketValue', 'contract']]

                # Traducción de las columnas al español
                col_labels_es = {"player_name": "Jugador","Estadística": "Estadística","Age": "Edad","nationality": "Nacionalidad","club_name": "Club",
                    "position": "Posición","marketValue": "Valor de mercado","contract": "Contrato",}
                final_df = final_df.rename(columns=col_labels_es)

                st.dataframe(final_df, use_container_width=True)

    elif selected == "Scout":
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True) # Affichage du titre de la page
            # Récupération des données
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)            
            # Caractéristiques générales (avec traductions lorsque cela est nécéssaire)
            pays_options_raw = sorted(df["nationality"].dropna().unique())
            pays_options_fr = [translate_country(p, lang="fr") for p in pays_options_raw]
            pays_fr = st.multiselect("Pays", pays_options_fr, placeholder="")
            fr_to_en = dict(zip(pays_options_fr, pays_options_raw))
            pays_en = [fr_to_en[p] for p in pays_fr] if pays_fr else []


            age_min, age_max = st.slider("Âge", 17, 42, (17, 42))
            height_min, height_max = st.slider("Taille (cm)", 163, 206, (163, 206))

            poste_options_raw = sorted(df["position"].dropna().unique())
            poste_options_fr = [translate_position(p, lang="fr") for p in poste_options_raw]
            poste_fr = st.multiselect("Poste", poste_options_fr, placeholder="")
            poste_en = [k for k, v in position_translation.get("fr", {}).items() if v in poste_fr] if poste_fr else []

            contract_years = sorted(df["contract"].dropna().apply(lambda x: str(x)[:4]).unique())
            contract_year = st.multiselect("Année de fin de contrat", contract_years, placeholder="")

            championnat = st.multiselect("Championnat", sorted(df["Comp"].dropna().unique()), placeholder="")
            
            # Mise à jour dynamique des clubs en fonction des championnats
            if championnat:
                clubs_filtered = df[df["Comp"].isin(championnat)]["club_name"].dropna().unique()
                club = st.multiselect("Club", sorted(clubs_filtered), placeholder="")
            else:
                club = st.multiselect("Club", sorted(df["club_name"].dropna().unique()), placeholder="")

            price_max = st.slider("Valeur marchande maximum (€)", 0, int(df["marketValue"].max()), 200000000, step=100000)

            # Statistiques de base avec traduction
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            fr_map = base_stat_translation.get("fr", {})

            translated_stats = [
                "Note" if col == "rating"
                else fr_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

            selected_base_stats_display = st.multiselect("Statistiques aggrégées par catégorie", translated_stats, placeholder="")
            selected_base_stats = [stat_name_mapping[disp] for disp in selected_base_stats_display if disp in stat_name_mapping]
            base_stat_limits = {}
            for display_name in selected_base_stats_display:
                stat = stat_name_mapping[display_name]
                min_val, max_val = int(df[stat].min()), int(df[stat].max())
                base_stat_limits[stat] = st.slider(
                    f"{display_name} (min / max)",
                    min_val, max_val,
                    (min_val, max_val),
                    step=1
                )

            # Statistiques avancées
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[42:]
            selected_adv_stats = st.multiselect("Statistiques brutes", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Nombre de joueurs à afficher", 3, 1800, 10) # Choix de nombre de joueurs à afficher
            
            # Centre tous les boutons
            st.markdown(
                """
                <style>
                div.stButton > button {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            recherche = st.button("🔍 Rechercher") # Bouton

            # On s'assure qu'un minimum d'informations a été renseigné
            nb_filled = sum([bool(pays_fr), bool(poste_fr), bool(contract_year), bool(championnat),bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0])

            if recherche:
                if nb_filled < 1:
                    st.error("Veuillez remplir au moins 1 critères pour lancer la recherche.")
                else:
                    # On récupère les données associées
                    df_filtered = df.copy()
                    if pays_en: df_filtered = df_filtered[df_filtered["nationality"].isin(pays_en)]
                    if poste_en: df_filtered = df_filtered[df_filtered["position"].isin(poste_en)]
                    if contract_year: df_filtered = df_filtered[df_filtered["contract"].str[:4].isin(contract_year)]
                    if championnat: df_filtered = df_filtered[df_filtered["Comp"].isin(championnat)]
                    if club: df_filtered = df_filtered[df_filtered["club_name"].isin(club)]
                    df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]
                    df_filtered = df_filtered[(df_filtered["height"] >= height_min) & (df_filtered["height"] <= height_max)]
                    df_filtered = df_filtered[df_filtered["marketValue"] <= price_max]

                    for stat, (min_v, max_v) in base_stat_limits.items():
                        df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                    for stat, (min_v, max_v) in adv_stat_limits.items():
                        if stat in df_filtered.columns:
                            df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                    
                    # Filtrage avancé spécial : seuils minimaux pour certaines stats
                    thresholds = {'Cmp%': ('Cmp', 50),'Tkl%': ('Tkl', 7),'Won%': ('Won', 6),'Succ%': ('Succ', 6)}

                    for stat in selected_adv_stats:
                        if stat in thresholds:
                            col, min_val = thresholds[stat]
                            if col in df_filtered.columns:
                                df_filtered = df_filtered[df_filtered[col] >= min_val]

                    # Filtrage gardien / joueur selon les stats avancées
                    goalkeeper_advanced_stats = ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%', 'GA_per90']

                    if any(stat in selected_adv_stats for stat in goalkeeper_advanced_stats):
                        df_filtered = df_filtered[df_filtered["position"] == "Goalkeeper"]

                    # Exclusion des gardiens pour certaines stats
                    if any(stat in ['Won%', 'Tkl%', 'Succ%'] for stat in selected_adv_stats):
                        df_filtered = df_filtered[df_filtered["position"] != "Goalkeeper"]

                    all_stats = selected_base_stats + selected_adv_stats
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name","position", "marketValue", "contract", "rating"] + all_stats

                    df_stat = df_filtered.dropna(subset=["rating"]).sort_values("rating", ascending=False)
                    
                    # Filtrage gardien / joueurs de champ selon la stat sélectionnée
                    goalkeeper_stats = ["goal_scoring_conceded", "efficiency", "error_fouls","short_clearance", "long_clearance", "positioning", "aerial_defense"]
                    # Vérifie si une stat de base sélectionnée est spécifique aux gardiens
                    selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                    if selected_goalkeeper_stats:
                        df_stat = df_stat[df_stat["position"] == "Goalkeeper"]
                    elif selected_base_stats:
                        df_stat = df_stat[df_stat["position"] != "Goalkeeper"]
                    df_stat = df_stat[display_columns].head(nb_players).reset_index(drop=True)

                    # Traductions de plusieurs catégories (postion, pays) et mise sous format des valeurs sur le marché des transferts
                    df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="fr"))
                    df_stat["nationality"] = df_stat["nationality"].apply(lambda x: translate_country(x, lang="fr"))
                    df_stat["marketValue"] = df_stat["marketValue"].apply(format_market_value)

                    # Construction du podium
                    top3 = df_stat.head(3)
                    podium_order = [0, 1, 2]
                    medals = ["🥇", "🥈", "🥉"]

                    podium_html = (
                        "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                        "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                        "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                    )

                    for display_index, i in enumerate(podium_order):
                        if i < len(top3):
                            player = top3.loc[i]
                            name = player['player_name']
                            rating = round(player['rating'], 2) if pd.notna(player['rating']) else "-"
                            image_url = player['imageUrl']
                            
                            image_html = (
                                f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                                "border-radius: 10px; margin-bottom: 0.5rem;'>"
                                if pd.notna(image_url) else ""
                            )

                            player_block = (
                                "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                                f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                                f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                                f"{image_html}"
                                f"<div style='font-size: 16px;'><strong>Note :</strong> {rating}</div>"
                                "</div>"
                            )

                            podium_html += player_block

                    podium_html += "</div></div>"

                    st.markdown(podium_html, unsafe_allow_html=True)

                    final_df = df_stat.drop(columns=["imageUrl"]) # Suppression de image_url pour la table finale
                    # Traduction des colonnes en français
                    col_labels_fr = {"player_name": "Joueur","Statistique": "Statistique","Age": "Âge","nationality": "Nationalité","club_name": "Club",
                        "position": "Poste","marketValue": "Valeur marchande","contract": "Contrat"}
                    final_df = final_df.rename(columns=col_labels_fr)

                    st.dataframe(final_df, use_container_width=True)

            # Sidebar résumé
            with st.sidebar:
                st.markdown("### 🧾 Filtres sélectionnés")
                if pays_fr:
                    st.markdown(f"- **Pays :** {', '.join(pays_fr)}")
                if poste_fr:
                    st.markdown(f"- **Postes :** {', '.join(poste_fr)}")
                st.markdown(f"- **Âge :** {age_min} - {age_max} ans")
                st.markdown(f"- **Taille :** {height_min} - {height_max} cm")
                st.markdown(f"- **Valeur max :** {format_market_value(price_max)}")
                if contract_year:
                    st.markdown(f"- **Contrat :** {', '.join(contract_year)}")
                if championnat:
                    st.markdown(f"- **Championnat :** {', '.join(championnat)}")
                if club:
                    st.markdown(f"- **Clubs :** {', '.join(club)}")

                if selected_base_stats_display:
                    st.markdown("**Stats aggrégées par catégorie :**")
                    for disp_label in selected_base_stats_display:
                        raw_stat = stat_name_mapping.get(disp_label)
                        if raw_stat in base_stat_limits:
                            st.markdown(f"- {disp_label} : {base_stat_limits[raw_stat]}")

                if selected_adv_stats:
                    st.markdown("**Stats brutes :**")
                    for stat in selected_adv_stats:
                        if stat in adv_stat_limits:
                            st.markdown(f"- {stat} : {adv_stat_limits[stat]}")

            # Placement du glossaire en sidebar
            with st.sidebar.expander("Glossaire des statistiques"):
                st.markdown("""
                ### Statistiques générales
                - **MP** : Nombre de matches joués
                - **Starts** : Nombre de matches débutés en tant que titulaire
                - **Min** : Nombre de minutes joués
                - **90s** : Nombre de minutes joués divisé par 90

                ### Gardien de but :
                - **GA_per90** : Buts encaissés par 90 minutes
                - **SoTA_per90** : Nombre de tirs cadrés concédés par 90 minutes 
                - **Save_per90** : Nombre d’arrêts effectués par 90 minutes
                - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés
                - **/90 /PSxG-GA/90** : Différence entre PSxG et buts encaissés par 90 minutes
                - **PKm_per90** : Nombre de pénaltys non arrêtés par le gardien par 90 minutes
                - **PKsv_per90** : Nombre de pénaltys arrêtés par le gardien par 90 minutes
                - **Thr_per90** : Nombre de dégagements effectués par le gardien par 90 minutes
                - **Stp_per90** : Nombre de centres arrêtés dans la surface par 90 minutes
                - **Save%** : Pourcentage d’arrêts effectués  
                - **CS%** : Pourcentage de clean sheat (matchs sans encaisser de but)
                - **AvgLen** : Longueur moyenne des passes (en yards)  
                - **Launch%** : Pourcentage de passes longues  
                - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  

                ### Joueurs de champs :
                - **Gls_per90** : Buts par 90 minutes
                - **Ast_per90** : Passe décisves par 90 minutes
                - **G+A_per90** : Buts + Passe décisives par 90 minutes  
                - **G-PK** : Buts marquées - pénaltys inscrits
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **G-xG_per90** : Buts marquées - Expected Goals par 90 minutes
                - **PK_per90** : Penaltys par 90 minutes
                - **npxG** : Non-penalty Expected Goals
                - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **PrgC_per90** : Conduites progressives par 90 minutes
                - **A-xAG** : Nombre de passe décisives - Expected Assisted Goals
                - **Sh_per90** : Tirs tentés par 90 minutes
                - **SoT_per90** : Tir cadrés par 90 minutes
                - **G/Sh** : Buts par tir
                - **SoT%** : Pourcentage de Tirs cadrés
                - **PrgP_per90** : Passes progressives par 90 minutes
                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                - **Cmp** : Nombre de passes réussis
                - **Cmp_per90** : Nombre de passes réussis par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **AvgDist**: Distance moyenne des passes (en yards)  
                - **1/3_per90** : Nombre de passes réussis dans le derniers tiers offensifs par 90 minutes
                - **PPA_per90** : Nombre de passes réussis dans la surface de réparation adverse par 90 minutes
                - **CrsPA_per90** : Nombre de centres réussis dans la surface de réparation adverse par 90 minutes
                - **Sw_per90** : Nombre de passes longues réussis par 90 minutes
                - **Crs_per90** : Nombre de centres réussis par 90 minutes
                - **Tkl** : Nombre de tacles effectués
                - **Tkl_per90** : Nombre de tacles effectués par 90 minutes
                - **Int_per90** : Nombre d'interceptions effectués par 90 minutes
                - **Clr_per90** : Nombre de dégagements effectués par 90 minutes
                - **Blocks_stats_defense_per90** : Nombre de blocs effectués par 90 minutes
                - **Int_per90_Padj** : Interceptions par 90 minutes ajustées à la possession
                - **Tkl_per90_Padj** : Tacles par 90 minutes ajustées à la possession
                - **Clr_per90_Padj** : Nombre de dégagements effectués par 90 minutes ajustées à la possession
                - **Blocks_stats_defense_per90_Padj** : Nombre de blocs effectués par 90 minutes ajustées à la possession
                - **Err_per90** : Erreurs menant à un tir adverse par 90 minutes
                - **Fld_per90** : Fautes subies par 90 minutes
                - **Touches_per90** : Nombre de touches du ballon par 90 minutes
                - **Succ_per90** : Dribbles réussis par 90 minutes
                - **Carries_per90** : Nombre de portage du ballon par 90 minutes
                - **Mis_per90** : Nombre de mauvais contrôle du ballon par 90 minutes
                - **Dis_per90** : Ballons perdus par 90 minutes
                - **Fls_per90** : Nombre de fautes provoquées par 90 minutes
                - **PKwon_per90** : Nombre de penaltys obtenus par 90 minutes
                - **PKcon_per90** : Nombre de penaltys concédés par 90 minutes
                - **Recov_per90** : Nombre de récupération du ballon par 90 minutes
                - **Tkl%** : Pourcentage de tacles effectués
                - **Succ%** : Pourcentage de dribbles réussis
                - **Won_per90** : Duels aériens gagnés par 90 minutes
                - **Won%** : Pourcentage de duels aériens gagnés
                - **CrdY_per90** : Cartons jaunes par 90 minutes
                - **CrdR_per90** : Cartons rouges par 90 minutes
                """)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True) # Display the title
            # Recover the data 
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # General Characteristics
            country_options = sorted(df["nationality"].dropna().unique())
            country = st.multiselect("Country", country_options, placeholder="")

            age_min, age_max = st.slider("Age", 17, 42, (17, 42))
            height_min, height_max = st.slider("Height (cm)", 163, 206, (163, 206))

            position_options = sorted(df["position"].dropna().unique())
            position = st.multiselect("Position", position_options, placeholder="")

            contract_years = sorted(df["contract"].dropna().apply(lambda x: str(x)[:4]).unique())
            contract_year = st.multiselect("Contract end year", contract_years, placeholder="")

            leagues = st.multiselect("League", sorted(df["Comp"].dropna().unique()), placeholder="")

            if leagues:
                filtered_clubs = df[df["Comp"].isin(leagues)]["club_name"].dropna().unique()
                club = st.multiselect("Club", sorted(filtered_clubs), placeholder="")
            else:
                club = st.multiselect("Club", sorted(df["club_name"].dropna().unique()), placeholder="")

            price_max = st.slider("Maximum market value (€)", 0, int(df["marketValue"].max()), 200000000, step=100000)

            # Base statistics
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            # Apply formatting for display
            translated_stats = [format_stat_name(col) for col in all_stats_raw]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

            selected_base_stats_display = st.multiselect("Aggregate statistics by category", translated_stats, placeholder="")
            selected_base_stats = [stat_name_mapping[disp] for disp in selected_base_stats_display if disp in stat_name_mapping]
            base_stat_limits = {}
            for display_name in selected_base_stats_display:
                stat = stat_name_mapping[display_name]
                min_val, max_val = int(df[stat].min()), int(df[stat].max())
                base_stat_limits[stat] = st.slider(f"{display_name} (min / max)", min_val, max_val, (min_val, max_val), step=1)

            # Advanced statistics
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[42:]
            selected_adv_stats = st.multiselect("Raw statistics", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Number of players to display", 3, 1800, 10) # Choice of the number of players to display

            # Center all buttons
            st.markdown(
                """
                <style>
                div.stButton > button {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            search = st.button("🔍 Search") # Button

            # We want that 1 criterias to start the search
            nb_filled = sum([bool(country), bool(position), bool(contract_year), bool(leagues),bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0])

            if search:
                if nb_filled < 1:
                    st.error("Please fill at least 1 criteria to start the search.")
                else:
                    # We recovering the data
                    df_filtered = df.copy()
                    if country: df_filtered = df_filtered[df_filtered["nationality"].isin(country)]
                    if position: df_filtered = df_filtered[df_filtered["position"].isin(position)]
                    if contract_year: df_filtered = df_filtered[df_filtered["contract"].str[:4].isin(contract_year)]
                    if leagues: df_filtered = df_filtered[df_filtered["Comp"].isin(leagues)]
                    if club: df_filtered = df_filtered[df_filtered["club_name"].isin(club)]
                    df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]
                    df_filtered = df_filtered[(df_filtered["height"] >= height_min) & (df_filtered["height"] <= height_max)]
                    df_filtered = df_filtered[df_filtered["marketValue"] <= price_max]

                    for stat, (min_v, max_v) in base_stat_limits.items():
                        df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                    for stat, (min_v, max_v) in adv_stat_limits.items():
                        if stat in df_filtered.columns:
                            df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]

                    # Thresholds made to not over-reward a player which have a low number realised on a statistic but a high percentage
                    thresholds = {'Cmp%': ('Cmp', 50),'Tkl%': ('Tkl', 7),'Won%': ('Won', 6),'Succ%': ('Succ', 6)}

                    for stat in selected_adv_stats:
                        if stat in thresholds:
                            col, min_val = thresholds[stat]
                            if col in df_filtered.columns:
                                df_filtered = df_filtered[df_filtered[col] >= min_val]

                    # Some specifics parameters for the goalkeepers
                    goalkeeper_advanced_stats = ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%', 'GA_per90']
                    if any(stat in selected_adv_stats for stat in goalkeeper_advanced_stats):
                        df_filtered = df_filtered[df_filtered["position"] == "Goalkeeper"]
                    if any(stat in ['Won%', 'Tkl%', 'Succ%'] for stat in selected_adv_stats):
                        df_filtered = df_filtered[df_filtered["position"] != "Goalkeeper"]

                    goalkeeper_stats = ["goal_scoring_conceded", "efficiency", "error_fouls","short_clearance", "long_clearance", "positioning", "aerial_defense"
                    ]
                    selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                    
                    if selected_goalkeeper_stats:
                        df_filtered = df_filtered[df_filtered["position"] == "Goalkeeper"]
                    elif selected_base_stats:
                        df_filtered = df_filtered[df_filtered["position"] != "Goalkeeper"]

                    all_stats = selected_base_stats + selected_adv_stats
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name","position", "marketValue", "contract", "rating"] + all_stats # We choose the list of informations collected

                    df_stat = df_filtered.dropna(subset=["rating"]).sort_values("rating", ascending=False)
                    df_stat = df_stat[display_columns].head(nb_players).reset_index(drop=True)

                    df_stat["marketValue"] = df_stat["marketValue"].apply(format_market_value) # Format market value

                    # We display a podium
                    top3 = df_stat.head(3)
                    podium_order = [0, 1, 2]
                    medals = ["🥇", "🥈", "🥉"]

                    podium_html = (
                        "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                        "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                        "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                    )

                    for display_index, i in enumerate(podium_order):
                        if i < len(top3):
                            player = top3.loc[i]
                            name = player['player_name']
                            rating = round(player['rating'], 2) if pd.notna(player['rating']) else "-"
                            image_url = player['imageUrl']
                            
                            image_html = (
                                f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                                "border-radius: 10px; margin-bottom: 0.5rem;'>"
                                if pd.notna(image_url) else ""
                            )

                            player_block = (
                                "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                                f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                                f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                                f"{image_html}"
                                f"<div style='font-size: 16px;'><strong>Rating :</strong> {rating}</div>"
                                "</div>"
                            )

                            podium_html += player_block

                    podium_html += "</div></div>"

                    st.markdown(podium_html, unsafe_allow_html=True)

                    final_df = df_stat.drop(columns=["imageUrl"])
                    # We clean all the columns
                    col_labels_en = {"player_name": "Player","Statistic": "Statistic","Age": "Age","nationality": "Country","club_name": "Club",
                        "position": "Position","marketValue": "Market value","contract": "Contract"}
                    final_df = final_df.rename(columns=col_labels_en)
                    st.dataframe(final_df, use_container_width=True) # We didsplay the entire list of players asked

            # Sidebar summary
            with st.sidebar:
                st.markdown("### 🧾 Selected Filters")
                if country:
                    st.markdown(f"- **Country:** {', '.join(country)}")
                if position:
                    st.markdown(f"- **Positions:** {', '.join(position)}")
                st.markdown(f"- **Age:** {age_min} - {age_max} years")
                st.markdown(f"- **Height:** {height_min} - {height_max} cm")
                st.markdown(f"- **Max value:** {format_market_value(price_max)}")
                if contract_year:
                    st.markdown(f"- **Contract:** {', '.join(contract_year)}")
                if leagues:
                    st.markdown(f"- **League:** {', '.join(leagues)}")
                if club:
                    st.markdown(f"- **Club:** {', '.join(club)}")

                if selected_base_stats_display:
                    st.markdown("**Aggregate Stats by category:**")
                    for disp_label in selected_base_stats_display:
                        raw_stat = stat_name_mapping.get(disp_label)
                        if raw_stat in base_stat_limits:
                            st.markdown(f"- {disp_label}: {base_stat_limits[raw_stat]}")

                if selected_adv_stats:
                    st.markdown("**Raw Stats:**")
                    for stat in selected_adv_stats:
                        if stat in adv_stat_limits:
                            st.markdown(f"- {stat}: {adv_stat_limits[stat]}")

            # Gloassary in the sidebar
            with st.sidebar.expander("Glossary of statistics"):
                st.markdown("""
                ### General statistics
                - **MP** : Number of matches played
                - **Starts** : Number of matches played at starter
                - **Min** : Number of minutes played
                - **90s** : Number of minutes played divided by 90

                ### Goalkeeper :
                - **GA_per90** : Goals conceded per 90 minutes  
                - **SoTA_per90** : Number of shot on target conceded per 90 minutes 
                - **Save_per90** : Number of saves made per 90 minutes
                - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                - **PSxG+/-** : Difference between PSxG and goals conceded 
                - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes             
                - **PKm_per90** : Number of penaltys non-save by the keeper per 90 minutes
                - **PKsv_per90** : Number of penaltys save by the keeper per 90 minutes
                - **Thr_per90** : Number of throws made by the keeper per 90 minutes
                - **Stp_per90** : Number of cross stopped into penalty area by the keeper
                - **Save%** : Save percentage  
                - **CS%** : Percentage og clean sheat (matches without conceded a goal)
                - **AvgLen** :  Average pass length (in yards)   
                - **Launch%** : Percentage of long passes
                - **Stp%** : Percentage of crosses stopped inside the box  
                - **#OPA_per90** : Defensive actions outside the penalty area per 90 minutes

                ### Field player :
                - **Gls_per90** : Goals per 90 minutes
                - **Ast_per90** : Assists per 90 minutes
                - **G+A_per90** : Goals + Assists per 90 minutes  
                - **G-PK** : Goals - penaltys scored
                - **G-PK_per90** : Goals scored minus penalties per 90 minutes
                - **G-xG_per90** : Buts minus Expected Goals per 90 minutes
                - **PK_per90** : Penaltys per 90 minutes
                - **npxG** : Non-penalty Expected Goals
                - **npxG_per90** : Non-penalty Expected Goals per 90 minutes 
                - **xAG_per90** : Expected Assisted Goals per 90 minutes  
                - **PrgC_per90** : Progressive carries per 90 minutes 
                - **A-xAG** : Number of assists - Expected Assisted Goals
                - **Sh_per90** : Shots attempted per 90 minutes
                - **SoT_per90** : Shot on target per 90 minutes
                - **G/Sh** : Goals per shot  
                - **SoT%** : Percentage of Shot on target
                - **PrgP_per90** : Progressive passes per 90 minutes 
                - **PrgR_per90** : Progressive passes received per 90 minutes 
                - **Cmp** : Number of passes achieved
                - **Cmp_per90** : Number of passes achieved par 90 minutes
                - **Cmp%** : Pass completion percentage
                - **AvgDist**: Average pass distance (in yards)  
                - **1/3_per90** : Number of passes achieved into last third area per 90 minutes
                - **PPA_per90** : Number of passes achieved into penalty area par 90 minutes
                - **CrsPA_per90** : Number of crosses achieved into penalty area par 90 minutes
                - **Sw_per90** : Number of long passes completed per 90 minutes
                - **Crs_per90** : Number of crosses completed per 90 minutes
                - **Tkl** : Number of tackes made
                - **Tkl_per90** : Tackles per 90 minutes 
                - **Int_per90** : Interceptions per 90 minutes 
                - **Clr_per90** : Number of clearances made per 90 minutes
                - **Blocks_stats_defense_per90**: Número de bloqueos realizados por cada 90 minutos
                - **Int_per90_Padj**: Intercepciones por cada 90 minutos ajustadas a la posesión
                - **Tkl_per90_Padj**: Entradas por cada 90 minutos ajustadas a la posesión
                - **Clr_per90_Padj**: Número de despejes realizados por cada 90 minutos ajustados a la posesión
                - **Blocks_stats_defense_per90_Padj**: Número de bloqueos realizados por cada 90 minutos ajustados a la posesión
                - **Err_per90** : Errors leading to a shot per 90 minutes  
                - **Fld_per90** : Fouls drawn per 90 minutes 
                - **Touches_per90** : Number of touches of the ball per 90 minutes
                - **Succ_per90** : Successful dribbles per 90 minutes  
                - **Carries_per90** : Number of carries per 90 minutes
                - **Mis_per90** : Number of times a player failed when attempting to gain control of a ball
                - **Dis_per90** : Dispossessions per 90 minutes
                - **Fls_per90** : Number of faults provoked per 90 minutes
                - **PKwon_per90** : Number of penaltys obtained per 90 minutes
                - **PKcon_per90** : Number of penaltys conceded par 90 minutes
                - **Recov_per90** : Number of recovery made per 90 minutes
                - **Tkl%** : Tackle success rate 
                - **Succ%** : Dribble success rate  
                - **Won_per90** : Aerial duels won per 90 minutes  
                - **Won%** : Aerial duel success rate 
                - **CrdY_per90** : Yellow cards per 90 minutes  
                - **CrdR_per90** : Red cards per 90 minutes  
                """)
        
        else:
            st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True)
            # Cargar datos
            player_path = os.path.join(os.path.dirname(__file__), "..", "data", "player", "database_player.csv")
            df = pd.read_csv(player_path)
            # Características generales (con traducciones cuando es necesario)
            pais_options_raw = sorted(df["nationality"].dropna().unique())
            pais_options_es = [translate_country(p, lang="es") for p in pais_options_raw]
            pais_es = st.multiselect("País", pais_options_es, placeholder="")
            es_to_en_country = dict(zip(pais_options_es, pais_options_raw))
            pais_en = [es_to_en_country[p] for p in pais_es] if pais_es else []

            age_min, age_max = st.slider("Edad", 17, 42, (17, 42))
            height_min, height_max = st.slider("Altura (cm)", 163, 206, (163, 206))

            poste_options_raw = sorted(df["position"].dropna().unique())
            poste_options_es = [translate_position(p, lang="es") for p in poste_options_raw]
            poste_es = st.multiselect("Posición", poste_options_es, placeholder="")
            poste_en = [k for k, v in position_translation.get("es", {}).items() if v in poste_es] if poste_es else []

            contract_years = sorted(df["contract"].dropna().apply(lambda x: str(x)[:4]).unique())
            contract_year = st.multiselect("Año de fin de contrato", contract_years, placeholder="")

            campeonato = st.multiselect("Liga", sorted(df["Comp"].dropna().unique()), placeholder="")

            # Actualización dinámica de clubes según ligas
            if campeonato:
                clubs_filtered = df[df["Comp"].isin(campeonato)]["club_name"].dropna().unique()
                club = st.multiselect("Club", sorted(clubs_filtered), placeholder="")
            else:
                club = st.multiselect("Club", sorted(df["club_name"].dropna().unique()), placeholder="")

            price_max = st.slider("Valor de mercado máximo (€)", 0, int(df["marketValue"].max()), 200000000, step=100000)

            # Estadísticas de base con traducción
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            es_map = base_stat_translation.get("es", {})
            translated_stats = [
                "Nota" if col == "rating"
                else es_map.get(col.replace("score_", ""), col)
                for col in all_stats_raw
            ]
            stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

            selected_base_stats_display = st.multiselect("Estadísticas agregadas por categoría", translated_stats, placeholder="")
            selected_base_stats = [stat_name_mapping[disp] for disp in selected_base_stats_display if disp in stat_name_mapping]

            base_stat_limits = {}
            for display_name in selected_base_stats_display:
                stat = stat_name_mapping[display_name]
                min_val, max_val = int(df[stat].min()), int(df[stat].max())
                base_stat_limits[stat] = st.slider(
                    f"{display_name} (mín / máx)",
                    min_val, max_val,
                    (min_val, max_val),
                    step=1
                )

            # Estadísticas avanzadas
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[42:]
            selected_adv_stats = st.multiselect("Estadísticas brutas", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (mín / máx)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Número de jugadores a mostrar", 3, 1800, 10)

            # Centrar botones
            st.markdown(
                """
                <style>
                div.stButton > button {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            recherche = st.button("🔍 Buscar") # Botón

            # Mínimo de información rellenada
            nb_filled = sum([bool(pais_es), bool(poste_es), bool(contract_year), bool(campeonato),bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0])

            if recherche:
                if nb_filled < 1:
                    st.error("Por favor, rellena al menos 1 criterio para lanzar la búsqueda.")
                else:
                    # Datos filtrados
                    df_filtered = df.copy()
                    if pais_en: df_filtered = df_filtered[df_filtered["nationality"].isin(pais_en)]
                    if poste_en: df_filtered = df_filtered[df_filtered["position"].isin(poste_en)]
                    if contract_year: df_filtered = df_filtered[df_filtered["contract"].str[:4].isin(contract_year)]
                    if campeonato: df_filtered = df_filtered[df_filtered["Comp"].isin(campeonato)]
                    if club: df_filtered = df_filtered[df_filtered["club_name"].isin(club)]
                    df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]
                    df_filtered = df_filtered[(df_filtered["height"] >= height_min) & (df_filtered["height"] <= height_max)]
                    df_filtered = df_filtered[df_filtered["marketValue"] <= price_max]

                    for stat, (min_v, max_v) in base_stat_limits.items():
                        df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                    for stat, (min_v, max_v) in adv_stat_limits.items():
                        if stat in df_filtered.columns:
                            df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]

                    # Filtro avanzado especial: umbrales mínimos para ciertas stats
                    thresholds = {'Cmp%': ('Cmp', 50),'Tkl%': ('Tkl', 7),'Won%': ('Won', 6),'Succ%': ('Succ', 6)}
                    for stat in selected_adv_stats:
                        if stat in thresholds:
                            col, min_value = thresholds[stat]
                            if col in df_filtered.columns:
                                df_filtered = df_filtered[df_filtered[col] >= min_value]

                    # Filtrado porteros / jugadores de campo según stats avanzadas
                    goalkeeper_advanced_stats = ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%', 'GA_per90']
                    if any(stat in selected_adv_stats for stat in goalkeeper_advanced_stats):
                        df_filtered = df_filtered[df_filtered["position"] == "Goalkeeper"]

                    # Exclusión de porteros para ciertas stats
                    if any(stat in ['Won%', 'Tkl%', 'Succ%'] for stat in selected_adv_stats):
                        df_filtered = df_filtered[df_filtered["position"] != "Goalkeeper"]

                    all_stats = selected_base_stats + selected_adv_stats
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name","position", "marketValue", "contract", "rating"] + all_stats

                    df_stat = df_filtered.dropna(subset=["rating"]).sort_values("rating", ascending=False)

                    # Filtrado portero / jugadores de campo según la base seleccionada
                    goalkeeper_stats = ["goal_scoring_conceded", "efficiency", "error_fouls", "short_clearance", "long_clearance", "positioning", "aerial_defense"]
                    selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                    if selected_goalkeeper_stats:
                        df_stat = df_stat[df_stat["position"] == "Goalkeeper"]
                    elif selected_base_stats:
                        df_stat = df_stat[df_stat["position"] != "Goalkeeper"]

                    df_stat = df_stat[display_columns].head(nb_players).reset_index(drop=True)

                    # Traducciones (posición, país) y formato de valor de mercado
                    df_stat['position'] = df_stat['position'].apply(lambda x: translate_position(x, lang="es"))
                    df_stat["nationality"] = df_stat["nationality"].apply(lambda x: translate_country(x, lang="es"))
                    df_stat["marketValue"] = df_stat["marketValue"].apply(format_market_value)

                    # Podio
                    top3 = df_stat.head(3)
                    podium_order = [0, 1, 2]
                    medals = ["🥇", "🥈", "🥉"]

                    podium_html = (
                        "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                        "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                        "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                    )

                    for display_index, i in enumerate(podium_order):
                        if i < len(top3):
                            player = top3.loc[i]
                            name = player['player_name']
                            rating = round(player['rating'], 2) if pd.notna(player['rating']) else "-"
                            image_url = player['imageUrl']

                            image_html = (
                                f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                                "border-radius: 10px; margin-bottom: 0.5rem;'>"
                                if pd.notna(image_url) else ""
                            )

                            player_block = (
                                "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                                f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                                f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                                f"{image_html}"
                                f"<div style='font-size: 16px;'><strong>Nota:</strong> {rating}</div>"
                                "</div>"
                            )

                            podium_html += player_block

                    podium_html += "</div></div>"
                    st.markdown(podium_html, unsafe_allow_html=True)

                    final_df = df_stat.drop(columns=["imageUrl"])  # Quitar image_url de la tabla
                    # Traducción de las columnas al español
                    col_labels_es = {"player_name": "Jugador","Estadística": "Estadística","Age": "Edad","nationality": "Nacionalidad","club_name": "Club",
                        "position": "Posición","marketValue": "Valor de mercado","contract": "Contrato",}
                    final_df = final_df.rename(columns=col_labels_es)
                    st.dataframe(final_df, use_container_width=True)

            # Resumen en la barra lateral
            with st.sidebar:
                st.markdown("### 🧾 Filtros seleccionados")
                if pais_es:
                    st.markdown(f"- **País:** {', '.join(pais_es)}")
                if poste_es:
                    st.markdown(f"- **Posiciones:** {', '.join(poste_es)}")
                st.markdown(f"- **Edad:** {age_min} - {age_max} años")
                st.markdown(f"- **Altura:** {height_min} - {height_max} cm")
                st.markdown(f"- **Valor máx.:** {format_market_value(price_max)}")
                if contract_year:
                    st.markdown(f"- **Contrato:** {', '.join(contract_year)}")
                if campeonato:
                    st.markdown(f"- **Liga:** {', '.join(campeonato)}")
                if club:
                    st.markdown(f"- **Clubs:** {', '.join(club)}")

                if selected_base_stats_display:
                    st.markdown("**Estadísticas agregadas por categoría:**")
                    for disp_label in selected_base_stats_display:
                        raw_stat = stat_name_mapping.get(disp_label)
                        if raw_stat in base_stat_limits:
                            st.markdown(f"- {disp_label}: {base_stat_limits[raw_stat]}")

                if selected_adv_stats:
                    st.markdown("**Estadísticas brutas:**")
                    for stat in selected_adv_stats:
                        if stat in adv_stat_limits:
                            st.markdown(f"- {stat}: {adv_stat_limits[stat]}")

            # Glosario en la barra lateral
            with st.sidebar.expander("Glosario de estadísticas"):
                st.markdown("""
                ### Estadísticas generales
                - **MP**: Partidos jugados
                - **Starts**: Partidos como titular
                - **Min**: Minutos jugados
                - **90s**: Minutos jugados dividido entre 90

                ### Portero:
                - **GA_per90**: Goles encajados por 90 minutos
                - **SoTA_per90**: Tiros a puerta recibidos por 90 minutos
                - **Save_per90**: Paradas por 90 minutos
                - **PSxG_per90**: Post-Shot Expected Goals por 90 minutos
                - **PSxG+/-**: Diferencia entre PSxG (xG post-tiro) y goles encajados
                - **/90 /PSxG-GA/90**: Diferencia entre PSxG y goles encajados por 90 minutos
                - **PKm_per90**: Penaltis no detenidos por 90 minutos
                - **PKsv_per90**: Penaltis detenidos por 90 minutos
                - **Thr_per90**: Saques/Envios del portero por 90 minutos
                - **Stp_per90**: Centros detenidos en el área por 90 minutos
                - **Save%**: Porcentaje de paradas
                - **CS%**: Porcentaje de porterías a cero
                - **AvgLen**: Longitud media de pase (yardas)
                - **Launch%**: Porcentaje de pases largos
                - **Stp%**: Porcentaje de centros detenidos en el área
                - **#OPA_per90**: Acciones defensivas fuera del área por 90 minutos

                ### Jugadores de campo:
                - **Gls_per90**: Goles por 90 minutos
                - **Ast_per90**: Asistencias por 90 minutos
                - **G+A_per90**: Goles + asistencias por 90 minutos
                - **G-PK**: Goles menos penaltis
                - **G-PK_per90**: Goles menos penaltis por 90 minutos
                - **G-xG_per90**: Goles menos xG por 90 minutos
                - **PK_per90**: Penaltis por 90 minutos
                - **npxG**: xG sin penaltis
                - **npxG_per90**: xG sin penaltis por 90 minutos
                - **xAG_per90**: Asistencias esperadas (xAG) por 90 minutos
                - **PrgC_per90**: Conducciones progresivas por 90 minutos
                - **A-xAG**: Asistencias - xAG
                - **Sh_per90**: Tiros por 90 minutos
                - **SoT_per90**: Tiros a puerta por 90 minutos
                - **G/Sh**: Goles por tiro
                - **SoT%**: Porcentaje de tiros a puerta
                - **PrgP_per90**: Pases progresivos por 90 minutos
                - **PrgR_per90**: Recepciones progresivas por 90 minutos
                - **Cmp**: Pases completados
                - **Cmp_per90**: Pases completados por 90 minutos
                - **Cmp%**: Porcentaje de pases completados
                - **AvgDist**: Distancia media de pase (yardas)
                - **1/3_per90**: Pases completados al último tercio por 90 minutos
                - **PPA_per90**: Pases completados al área rival por 90 minutos
                - **CrsPA_per90**: Centros completados al área rival por 90 minutos
                - **Sw_per90**: Cambios de juego completados por 90 minutos
                - **Crs_per90**: Centros completados por 90 minutos
                - **Tkl**: Entradas
                - **Tkl_per90**: Entradas por 90 minutos
                - **Int_per90**: Intercepciones por 90 minutos
                - **Clr_per90**: Despejes por 90 minutos
                - **Blocks_stats_defense_per90**: Number of blocks per 90 minutes
                - **Int_per90_Padj**: Interceptions per 90 minutes adjusted for possession
                - **Tkl_per90_Padj**: Tackles per 90 minutes adjusted for possession
                - **Clr_per90_Padj**: Number of clearances made per 90 minutes adjusted for possession
                - **Blocks_stats_defense_per90_Padj**: Number of blocks made per 90 minutes adjusted for possession
                - **Err_per90**: Errores que conducen a tiro por 90 minutos
                - **Fld_per90**: Faltas recibidas por 90 minutos
                - **Touches_per90**: Toques por 90 minutos
                - **Succ_per90**: Regates exitosos por 90 minutos
                - **Carries_per90**: Conducciones por 90 minutos
                - **Mis_per90**: Controles fallidos por 90 minutos
                - **Dis_per90**: Balones perdidos por 90 minutos
                - **Fls_per90**: Faltas cometidas por 90 minutos
                - **PKwon_per90**: Penaltis provocados por 90 minutos
                - **PKcon_per90**: Penaltis concedidos por 90 minutos
                - **Recov_per90**: Recuperaciones por 90 minutos
                - **Tkl%**: Porcentaje de éxito en entradas
                - **Succ%**: Porcentaje de regates exitosos
                - **Won_per90**: Duelos aéreos ganados por 90 minutos
                - **Won%**: Porcentaje de duelos aéreos ganados
                - **CrdY_per90**: Tarjetas amarillas por 90 minutos
                - **CrdR_per90**: Tarjetas rojas por 90 minutos
                """)