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


# Affichage du titre et du logo de l'application web / Display of web application title and logo / Visualización del título y el logotipo de la aplicación web
st.set_page_config(page_title="Big 5 Performance 25/26 ⚽ ", page_icon="💯", layout="centered")

# Langue dans session_state / Language in session_state / Idioma en session_state
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

lang = st.sidebar.selectbox(
    "Choisissez votre langue / Choose your language / Elige tu idioma", 
    ["Français", "English", "Español"]
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
        "Second Striker": "Second Attaquant",
        "Centre-Forward": "Attaquant-Centre",
        "Right-Back": "Défenseur Droit",
        "Left-Back": "Défenseur Gauche",
        "Right Winger": "Ailier Droit",
        "Left Winger": "Ailier Gauche",
        "Right Midfield": "Milieu Droit",
        "Left Midfield": "Milieu Gauche",
        "Attacking Midfield": "Milieu Attaquant",
        "Goalkeeper": "Gardien",
        "Defensive Midfield": "Milieu Défensif",
        "Central Midfield": "Milieu Central",
        "Centre-Back": "Défenseur Central",
    },
    "es": {
        "Second Striker": "Segundo delantero",
        "Centre-Forward": "Delantero centro",
        "Right-Back": "Lateral derecho",
        "Left-Back": "Lateral izquierdo",
        "Right Winger": "Extremo derecho",
        "Left Winger": "Extremo izquierdo",
        "Right Midfield": "Centrocampista derecho",
        "Left Midfield": "Centrocampista izquierdo",
        "Attacking Midfield": "Mediapunta",
        "Goalkeeper": "Portero",
        "Defensive Midfield": "Mediocentro defensivo",
        "Central Midfield": "Mediocentro",
        "Centre-Back": "Defensa central",
    }
}

country_translation = {
    "fr": {
        "Germany": "Allemagne",
        "Spain": "Espagne",
        "Italy": "Italie",
        "England": "Angleterre",
        "Netherlands": "Pays-Bas",
        "Brazil": "Brésil",
        "Argentina": "Argentine",
        "Belgium": "Belgique",
        "Croatia": "Croatie",
        "Switzerland": "Suisse",
        "Senegal": "Sénégal",
        "Cameroon": "Cameroun",
        "Morocco": "Maroc",
        "Albania": "Albanie",
        "Algeria": "Algérie",
        "Andorra": "Andorre",
        "Armenia": "Arménie",
        "Australia": "Australie",
        "Austria": "Autriche",
        "Bosnia-Herzegovina": "Bosnie-Herzégovine",
        "Cape Verde": "Cap-Vert",
        "Central African Republic": "République centrafricaine",
        "Chile": "Chili",
        "Colombia": "Colombie",
        "Czech Republic": "Tchéquie",
        "Denmark": "Danemark",
        "DR Congo": "République démocratique du Congo",
        "Ecuador": "Équateur",
        "Egypt": "Égypte",
        "Equatorial Guinea": "Guinée équatoriale",
        "Estonia": "Estonie",
        "Finland": "Finlande",
        "French Guiana": "Guyane française",
        "Georgia": "Géorgie",
        "Greece": "Grèce",
        "Guinea": "Guinée",
        "Guinea-Bissau": "Guinée-Bissau",
        "Hungary": "Hongrie",
        "Iceland": "Islande",
        "Indonesia": "Indonésie",
        "Ireland": "Irlande",
        "Jamaica": "Jamaïque",
        "Japan": "Japon",
        "Jordan": "Jordanie",
        "Korea, South": "Corée du Sud",
        "Libya": "Libye",
        "Lithuania": "Lituanie",
        "Malta": "Malte",
        "Mexico": "Mexique",
        "New Zealand": "Nouvelle-Zélande",
        "North Macedonia": "Macédoine du Nord",
        "Northern Ireland": "Irlande du Nord",
        "Norway": "Norvège",
        "Peru": "Pérou",
        "Poland": "Pologne",
        "Romania": "Roumanie",
        "Russia": "Russie",
        "Scotland": "Écosse",
        "Serbia": "Serbie",
        "Slovakia": "Slovaquie",
        "Slovenia": "Slovénie",
        "Sweden": "Suède",
        "Syria": "Syrie",
        "The Gambia": "Gambie",
        "Tunisia": "Tunisie",
        "Türkiye": "Turquie",
        "United States": "États-Unis",
        "Uzbekistan": "Ouzbékistan",
        "Wales": "Pays de Galles",
        "Zambia": "Zambie",
    },
    "es": {
        "France": "Francia",
        "Canada": "Canadá",
        "Germany": "Alemania",
        "Spain": "España",
        "Italy": "Italia",
        "England": "Inglaterra",
        "Netherlands": "Países Bajos",
        "Brazil": "Brasil",
        "Argentina": "Argentina",
        "Belgium": "Bélgica",
        "Croatia": "Croacia",
        "Switzerland": "Suiza",
        "Senegal": "Senegal",
        "Cameroon": "Camerún",
        "Morocco": "Marruecos",
        "Albania": "Albania",
        "Algeria": "Argelia",
        "Andorra": "Andorra",
        "Armenia": "Armenia",
        "Australia": "Australia",
        "Austria": "Austria",
        "Bosnia-Herzegovina": "Bosnia y Herzegovina",
        "Cape Verde": "Cabo Verde",
        "Central African Republic": "República Centroafricana",
        "Chile": "Chile",
        "Colombia": "Colombia",
        "Czech Republic": "Chequia",
        "Denmark": "Dinamarca",
        "DR Congo": "República Democrática del Congo",
        "Ecuador": "Ecuador",
        "Egypt": "Egipto",
        "Equatorial Guinea": "Guinea Ecuatorial",
        "Estonia": "Estonia",
        "Finland": "Finlandia",
        "French Guiana": "Guayana Francesa",
        "Georgia": "Georgia",
        "Greece": "Grecia",
        "Guinea": "Guinea",
        "Guinea-Bissau": "Guinea-Bisáu",
        "Hungary": "Hungría",
        "Iceland": "Islandia",
        "Indonesia": "Indonesia",
        "Ireland": "Irlanda",
        "Jamaica": "Jamaica",
        "Japan": "Japón",
        "Jordan": "Jordania",
        "Korea, South": "Corea del Sur",
        "Libya": "Libia",
        "Lithuania": "Lituania",
        "Malta": "Malta",
        "Mexico": "México",
        "New Zealand": "Nueva Zelanda",
        "North Macedonia": "Macedonia del Norte",
        "Northern Ireland": "Irlanda del Norte",
        "Norway": "Noruega",
        "Peru": "Perú",
        "Poland": "Polonia",
        "Romania": "Rumanía",
        "Russia": "Rusia",
        "Scotland": "Escocia",
        "Serbia": "Serbia",
        "Slovakia": "Eslovaquia",
        "Slovenia": "Eslovenia",
        "Sweden": "Suecia",
        "Syria": "Siria",
        "The Gambia": "Gambia",
        "Tunisia": "Túnez",
        "Türkiye": "Turquía",
        "United States": "Estados Unidos",
        "Ukraine": "Ucrania",
        "Uzbekistan": "Uzbekistán",
        "Wales": "Gales",
        "Zambia": "Zambia",
        "Zimbabwe": "Zimbabue",
        "Panama": "Panamá",
        "Haiti": "Haití",
        "Guadeloupe": "Guadalupe",
        "Gabon": "Gabón",
        "Cote d'Ivoire": "Costa de Marfil",

    }
}

base_stat_translation = {
    "fr": {
        "goal_scoring_created": "Création de buts",
        "goal_scoring_conceded": "Occasions concédées",
        "efficiency": "Efficacité",
        "error_fouls": "Erreurs et fautes",
        "short_clearance": "Relance courte",
        "long_clearance": "Relance longue",
        "positioning": "Positionnement",
        "aerial_defense": "Jeu aérien défensif",
        "finish": "Finition",
        "building": "Construction du jeu",
        "creation": "Création d'occasions",
        "dribble": "Dribbles",
        "projection": "Projection",
        "defensive_actions": "Actions défensives",
        "waste": "Pertes de balle",
        "faults_committed": "Fautes commises",
        "provoked_fouls": "Fautes provoquées",
        "aerial": "Jeu aérien",
    },
    "es": {
        "goal_scoring_created": "Creación de goles",
        "goal_scoring_conceded": "Ocasiones concedidas",
        "efficiency": "Eficiencia",
        "error_fouls": "Errores y faltas",
        "short_clearance": "Salida en corto",
        "long_clearance": "Salida en largo",
        "positioning": "Posicionamiento",
        "aerial_defense": "Juego aéreo defensivo",
        "finish": "Finalización",
        "building": "Construcción del juego",
        "creation": "Creación de ocasiones",
        "dribble": "Regates",
        "projection": "Proyección",
        "defensive_actions": "Acciones defensivas",
        "waste": "Pérdidas de balón",
        "faults_committed": "Faltas cometidas",
        "provoked_fouls": "Faltas provocadas",
        "aerial": "Juego aéreo",
    },
}

foot_translation = {
    "fr": {"right": "Droit", "left": "Gaucher", "both": "Ambidextre"},
    "es": {"right": "Diestro", "left": "Zurdo", "both": "Ambidiestro"},
}
foot_en_pretty = {"right": "Right", "left": "Left", "both": "Both"}


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

# Mapping des noms d'équipe (fbref_opta_join -> database_player) / Mapping of teams name (fbref_opta_join -> database_player) / Asignación de nombres de equipos (fbref_opta_join -> database_player)
df_to_info = {
    "Sevilla": "Sevilla FC",
    "Betis": "Real Betis",
    "RB Leipzig": "Leipzig",
    "Osasuna": "CA Osasuna",
    "Nott'ham Forest": "Nott'm Forest",
    "Newcastle Utd": "Newcastle",
    "Milan": "AC Milan",
    "Manchester Utd": "Man Utd",
    "Manchester City": "Man City",
    "Mallorca": "RCD Mallorca",
    "Mainz 05": "Mainz",
    "Leeds United": "Leeds",
    "Köln": "1.FC Köln",
    "Hamburger FC": "Hamburg",
    "Gladbach": "Mönchengladbach",
    "Elche": "Elche CF",
    "Eint Frankfurt": "Frankfurt",
    "Celta Vigo": "Celta de Vigo",
    "Atlético Madrid": "Atlético",
}

#  Catégorie des postes pour le radar / Position category for the radar plot / Categoría de posiciones para el radar plot
position_category = {
    "Goalkeeper": "Gardiens de but",
    "Centre-Back": "Défenseurs centraux",
    "Right-Back": "Défenseurs latéraux",
    "Left-Back": "Défenseurs latéraux",
    "Left Midfield": "Milieux de terrain",
    "Right Midfield": "Milieux de terrain",
    "Central Midfield": "Milieux de terrain",
    "Defensive Midfield": "Milieux de terrain",
    "Attacking Midfield": "Milieux offensifs / Ailiers",
    "Right Winger": "Milieux offensifs / Ailiers",
    "Left Winger": "Milieux offensifs / Ailiers",
    "Second Striker": "Attaquants",
    "Centre-Forward": "Attaquants"
}

# Statistiques par catégorie pour le radar / Statistics by categorie for the radar plot / Estadísticas por categoría para el radar plot
category_stats = {
    "Gardiens de but": ["GA_per90", "PSxG_per90", "/90", "Save%", "PSxG+/-", "Err_per90","Launch%", "AvgLen", "Cmp%", "AvgDist", "#OPA_per90", "Stp%"],
    "Défenseurs centraux": ["G-PK_per90", "PrgP_per90","Cmp%","xAG_per90","PrgC_per90","Err_per90","Tkl%","Int_per90","Tkl_per90","CrdY_per90","Won_per90","Won%" ],
    "Défenseurs latéraux": ["G-PK_per90", "PrgP_per90", "Cmp%", "xAG_per90", "Succ_per90", "PrgC_per90", "Err_per90", "Tkl%", "Int_per90", "Tkl_per90", "CrdY_per90", "Won%"],
    "Milieux de terrain": ["G-PK_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "PrgC_per90", "Fld_per90", "Err_per90", "Tkl%", "Int_per90", "CrdY_per90", "Won%"],
    "Milieux offensifs / Ailiers": ["npxG_per90","G-PK_per90", "G-xG_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "Succ_per90", "Succ%", "PrgC_per90", "Fld_per90", "Dis_per90"],
    "Attaquants": ["npxG_per90","Sh_per90", "G-PK_per90", "G-xG_per90", "G/Sh", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90","Succ_per90", "PrgC_per90", "Dis_per90"    ]
}

invert_stats = {"GA_per90", "PSxG_per90","Err_per90", "CrdY_per90", "Dis_per90"}

# Fonction pour renommer les noms des catégories / Function for renaming category names / Función para renombrar los nombres de las categorías
def format_stat_name(stat):
    if stat.startswith("score_"):
        return stat.replace("score_", "").replace("_", " ").capitalize()
    return stat.capitalize() if stat == "rating" else stat

# Fonction pour effectuer un radar plot avec les données / Radar plot function with data / Función para realizar un radar plot con los datos
def plot_pizza_radar(labels, player_values, median_values, title="Radar",legend_labels=("Joueur", "Médiane")):
    # Paramètres de la pizza plot / Parameters of the pizza plot
    pizza = PyPizza(
        params=labels,
        background_color="#EFF0D1",
        straight_line_color="#000000",
        straight_line_lw=1,
        last_circle_lw=1,
        last_circle_color="#000000",
        other_circle_ls="--",
        other_circle_color="#000000",
        other_circle_lw=0.5
    )
    
    # Mise des couleurs et valeurs sur la pizza plot / Dislay colors and values on the pizza plot / Colores y valores en la pizza plot
    fig, ax = pizza.make_pizza(
        values=[round(v) for v in player_values],
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
    params_offset = [
        abs(p - m) < threshold for p, m in zip(player_values, median_values)
    ]
    pizza.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)

    # Titre du radar / Radar title / Título del radar
    fig.text(
        0.5, 1.00, title,
        ha="center", fontsize=14, fontweight="bold", color="#000000"
    )

    # Légende personnalisée / Custom legend / Légende personnalisée
    legend_elements = [
        Patch(facecolor="#7FBFFF", edgecolor='black', label=legend_labels[0]),
        Patch(facecolor="#e63946", edgecolor='black', label=legend_labels[1])
    ]
    ax.legend(
        handles=legend_elements,
        loc='lower center', bbox_to_anchor=(0.5, -0.15),
        ncol=2, fontsize=10, frameon=False
    )

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

    # Ajouter le joueur sélectionné au début pour calculer les similarités
    # Add the player selected at the beginning to calculate similarities
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
        candidates_df = candidates_df[
            candidates_df['Comp'] == competition
        ]
    elif filter_type == "pays":
        candidates_df = candidates_df[
            candidates_df['nationality'] == country
        ]
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

    # Colonnes à afficher / Columns to display / Columnas a mostrar
    final_cols = [
        'player_name', 'percentage_similarity', 'Age', 'nationality',  'club_name', 'marketValue', 'contract'
    ]
    # Traduction du pays du joueur / Translation of the player's country / Traducción del país del jugador
    if lang == "Français":
        candidates_df['nationality'] = candidates_df['nationality'].apply(
            lambda x: translate_country(x, lang="fr")
        )
    elif lang == "Español":
        candidates_df['nationality'] = candidates_df['nationality'].apply(
            lambda x: translate_country(x, lang="es")
        )


    return candidates_df[final_cols].head(top_n)

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
        "attacking_set_pieces__xg_pct",
        "passing__avg_poss",
        "passing__pass_direction__fwd",
        "passing__pass_direction__left",
        "passing__pass_direction__right",
        "passing__crosses__pct",
        "pressing__pressed_seqs",
        "pressing__ppda",
        "pressing__start_distance_m",
        "sequences__ten_plus_passes",
        "sequences__direct_speed",
        "sequences__passes_per_seq",
        "sequences__sequence_time",
        "sequences__build_ups__total",
        "sequences__direct_attacks__total",
        "misc.__fouled",
        "misc.__fouls",
        "defending_set_pieces__xg_pct",
        "defending_defensive_actions__clearances",
        "defending_defensive_actions__ground_duels_won",
        "defending_defensive_actions__aerial_duels_won",
        "defending_misc__offsides",
    ] if col in df.columns]

    stats_df = candidates_df[stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Ajouter l'équipe sélectionné au début pour calculer les similarités
    # Add the team selected at the beginning to calculate similarities
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
        candidates_df = candidates_df[
            candidates_df['championship_name'] == competition
        ]

    candidates_df = candidates_df.sort_values(by='percentage_similarity', ascending=False) # Trier par similarité / Sort by similarity / Ordenar por similitud
    
    # Colonnes à afficher / Columns to display / Columnas a mostrar
    final_cols = [
        'team_code', 'percentage_similarity', 'championship_name', 'country'
    ]
    # Traduction du pays du joueur / Translation of the player's country / Traducción del país del jugador
    if lang == "Français":
        candidates_df['country'] = candidates_df['country'].apply(
            lambda x: translate_country(x, lang="fr")
        )
    elif lang == "Español":
        candidates_df['country'] = candidates_df['country'].apply(
            lambda x: translate_country(x, lang="es")
        )


    return candidates_df[final_cols].head(top_n)

# Sélecteur de MODE (Équipes / Joueurs) / Selector of MODE (Teams / Players) / Selector de MODE (Equipos / Jugadores)
mode_label = {
    "Français": "Type d'analyse",
    "English": "Analysis type",
    "Español": "Tipo de análisis",
}[lang]

mode_options = {
    "Français": ["Équipes", "Joueurs"],
    "English": ["Teams", "Players"],
    "Español": ["Equipos", "Jugadores"],
}[lang]

mode = option_menu(
    menu_title=None,
    options=mode_options,
    icons=["shield", "person-lines-fill"], 
    orientation="horizontal",
)

# Menus selon le MODE / Menus according to MODE /Menús según el MODO
if (mode in ["Équipes", "Teams", "Equipos"]):
    # MENU ÉQUIPE / MENU TEAM / MENU EQUIPO
    if lang == "Français":
        menu_labels = ["Menu", "Équipe", "Duel", "Stats +", "Stats", "Top"]
    elif lang == "English":
        menu_labels = ["Home", "Team", "F2F", "Stats +", "Stats", "Top"]
    else:
        menu_labels = ["Inicio", "Equipo", "Duelo", "Stats +", "Stats", "Top"]

    selected = option_menu(
        menu_title=None,
        options=menu_labels,
        icons=["house", "people", "crosshair", "trophy", "list-ol", "award"],
        orientation="horizontal",
    )

    # Code de la partie Équipe / Code of the Team part / Código de la parte Equipo
    if selected in ["Menu", "Home", "Inicio"]:
        if lang == "Français":
            # Titre de la page
            st.markdown(
                "<h3 style='text-align: center;'>Visualisation des performances des équipes sur la saison 25/26</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_team_performance.png") # Utilisation de la 1er bannière en image

            # Sous-titre
            st.markdown(
                "<h4 style='text-align: center;'>Présentation</h4>", 
                unsafe_allow_html=True)

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
                    <li><em>La documentation du projet</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">Le code associé à l'application</a></li>
                </ul>
                """,
                unsafe_allow_html=True
            )

        elif lang == "English":
            # Page title
            st.markdown(
                "<h3 style='text-align: center;'>Visualization of team performance over the 25/26 season</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_team_performance.png") # Using the 1st image banner

            # Subtitle
            st.markdown(
                "<h4 style='text-align: center;'>Presentation</h4>", 
                unsafe_allow_html=True)

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
                    <li><em>The project documentation</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">The code used to build the application</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
        else :
            # Título de la página
            st.markdown(
                "<h3 style='text-align: center;'>Visualización del rendimiento de los equipos durante la temporada 25/26</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_team_performance.png") # Usando el primer banner de imagen

            # Subtítulo
            st.markdown(
                "<h4 style='text-align: center;'>Presentación</h4>", 
                unsafe_allow_html=True)

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
                    <li><em>La documentación del proyecto</em></li>
                    <li><a href="https://github.com/football-labs/Fotball-labs" target="_blank">El código utilizado para construir la aplicación</a></li>
                </ul>
                """, unsafe_allow_html=True
            )
                    

    elif selected in ["Équipe", "Team", "Equipo"]:
        if lang == "Français":
            # Afficher le titre
            st.markdown("<h4 style='text-align: center;'>📊 Analyse d'une équipe</h4>", unsafe_allow_html=True)
            # Charger les données
            df = pd.read_csv('../data/team/fbref_analyst_joined.csv')
            info_player = pd.read_csv('../data/player/database_player.csv')

            championship_names = [''] + sorted(df['championship_name'].dropna().unique().tolist()) # Extraire la liste des championnats

            selected_championship = st.sidebar.selectbox("Choisissez un championnat :", championship_names) # Sélection de championnat

            championship_data = df[df['championship_name'] == selected_championship]
                    
            teams_names = [''] + sorted(championship_data['team_code'].dropna().unique().tolist()) # Extraire la liste des équipes dans le championnat choisi

            selected_team = st.sidebar.selectbox("Choisissez une équipe :", teams_names) # Sélection de l'équipe

            # Si un championnat est sélectionné, on cache l’image   
            if not selected_championship or not selected_team:
                # Aucun championnat sélectionné → afficher l'image d'intro
                st.image("../image/championship_analysis.jpg") # Utilisation de la 1er bannière en image
                st.info("Dérouler la barre latérale pour choisir la langue et le championnat à analyser")
            else:
                team_data = df[df['team_code'] == selected_team].iloc[0] # Filtrer le DataFrame pour l'équipe sélectionnée
                pays = translate_country(team_data['country'], lang="fr") # On traduit le nom du pays

                # On indique le noms des colonnes utilisées
                df_team_col = "team_code"     # dans df
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
                    <p><strong>Power Ranking :</strong> 30ème (F)</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Classement :</strong> {team_data['rank_league']}</p>
                    <p><strong>Pts :</strong> {int(team_data['pts_league'])}</p>
                    <p><strong>Différence de buts :</strong> {int(team_data['Team_Success_+/___ptime'])}</p>
                    <p><strong>Style de jeu Offensif :</strong> Jeu d'alternance (F)</p>
                    <p><strong>Style de jeu Défensif :</strong> Pressing Haut (F)</p>
                </div>

                <div style="flex: 2; min-width: 280px;">
                    <p><strong>Âge moyen :</strong> {team_data['Age__std']}</p>
                    <p><strong>Taille effectif :</strong> {int(team_data['#_Pl__std']) if pd.notna(team_data['#_Pl__std']) else "-"}</p>
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
                    comparison_filter = st.radio(
                        label="En comparaison avec",         
                        options=["Big 5", "Championnat"],
                        index=0,
                        horizontal=True,
                        label_visibility="collapsed",         
                        key="comparison_filter_radio"  
                    )

                filter_arg = {"Big 5": None, "Championnat": "championnat"}[comparison_filter]

                # Groupe filtré selon le filtre sélectionné
                if filter_arg is None:
                    group_df = df  # Pas de filtre
                else:  # "championnat"
                    group_df = df[df['championship_name'] == team_data['championship_name']]

                similar_df = find_similar_teams(selected_team, df, filter_type=filter_arg)

                # Affichage du titre et du tableau
                if not similar_df.empty:
                    # Titre centré
                    st.markdown(
                        f"<h4 style='text-align:center;'>Équipes similaires à {team_data['team_code']}</h4>",
                        unsafe_allow_html=True
                    )

                    # DataFrame centré
                    d1, d2, d3 = st.columns([0.1, 0.8, 0.1])  # ajuste les ratios si besoin
                    with d2:
                        st.dataframe(similar_df, use_container_width=True)

        else:
            st.info("Autre langues")

        # ...
    elif selected in ["Duel", "F2F", "Duelo"]:
        st.header("⚖️ Comparaison entre équipes/compétitions")
        # ...
    elif selected == "Stats +":
        st.header("📈 Stats aggrégées par catégorie")
        # ...
    elif selected == "Stats":
        st.header("📋 Stats brutes")
        # ...
    elif selected in ["Top"]:
        st.header("🏅 Power Ranking")
        # ...

else:
    # MENU JOUEURS
    if lang == "Français":
        menu_labels = ["Menu", "Joueur", "Duel", "Stats +", "Stats", "Scout"]
    elif lang == "English":
        menu_labels = ["Home", "Player", "F2F", "Stats +", "Stats", "Scout"]
    else:
        menu_labels = ["Inicio", "Atleta", "Duelo", "Stats +", "Stats", "Scout"]

    selected = option_menu(
        menu_title=None,
        options=menu_labels,
        icons=["house", "person", "crosshair", "trophy", "list-ol", "binoculars"],
        orientation="horizontal",
    )

    # Code de la partie Joueur / Code of the Player part / Código de la parte Jugador
    if selected in ["Menu", "Home", "Inicio"]:
        if lang == "Français":
            # Titre de la page
            st.markdown(
                "<h3 style='text-align: center;'>Visualisation des performances des joueurs sur la saison 25/26</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_player_performance.png") # Utilisation de la 1er bannière en image

            # Sous-titre
            st.markdown(
                "<h4 style='text-align: center;'>Présentation</h4>", 
                unsafe_allow_html=True)

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
            # Page title
            st.markdown(
                "<h3 style='text-align: center;'>Visualization of player performance over the 25/26 season</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_player_performance.png") # Using the 1st image banner

            # Subtitle
            st.markdown(
                "<h4 style='text-align: center;'>Presentation</h4>", 
                unsafe_allow_html=True)

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
            # Título de la página
            st.markdown(
                "<h3 style='text-align: center;'>Visualización del rendimiento de los jugadores durante la temporada 25/26</h3>", 
                unsafe_allow_html=True)

            st.image("../image/logo_player_performance.png") # Usando el primer banner de imagen

            # Subtítulo
            st.markdown(
                "<h4 style='text-align: center;'>Presentación</h4>", 
                unsafe_allow_html=True)

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
            # Afficher le titre
            st.markdown("<h4 style='text-align: center;'>📊 Analyse d'un joueur</h4>", unsafe_allow_html=True)

            df = pd.read_csv('../data/player/database_player.csv') # Charger les données

            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist()) # Extraire la liste des joueurs

            selected_player = st.sidebar.selectbox("Choisissez un joueur :", player_names) # Sélection de joueur

            # Si un joueur est sélectionnée, on cache l’image   
            if not selected_player:
                # Aucun joueur sélectionné → afficher l'image d'intro
                st.image("../image/player_analysis.jpg") # Utilisation de la 1er bannière en image
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
                    <p><strong>Autre(s) poste(s) :</strong> {position_other_translated}</p>
                    <p><strong>Agent :</strong> {agent_name}</p>
                    <p><strong>Équipementier :</strong> {outfitter}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

                # Filtre unique pour radar + similarité
                comparison_filter = st.radio(
                    "En comparaison à son poste : ",
                    options=[
                        "Vue globale",
                        "Championnat",
                        "Tranche d’âge",
                        "Pays"
                    ],
                    index=0,
                    horizontal=True
                )

                filter_arg = {
                    "Vue globale": None,
                    "Championnat": "championnat",
                    "Tranche d’âge": "tranche_age",
                    "Pays": "pays"
                }[comparison_filter]

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
                            - **Int_per90** : Interceptions par 90 minutes
                            - **Tkl_per90** : Tacles par 90 minutes
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
                            - **Int_per90** : Interceptions par 90 minutes
                            - **Tkl_per90** : Tacles par 90 minutes
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
                            - **Int_per90** : Interceptions par 90 minutes
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

                if poste_cat and poste_cat in category_stats:
                    stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]
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

                        # On normalise le profil du joueur en percentiles
                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0)

                        # On calcule la médiane selon la catégorie de poste
                        group_median = (
                            rank_pct.drop(index=player_data['player_name'], errors='ignore')
                                    .median()
                                    .reindex(stats_cols)
                                    .fillna(0)
                        )

                        # Calcul de la note si elle existe
                        rating_text = f" - Note : {round(player_rating, 2)}" if player_rating is not None else ""

                        # Affichage du titre avec note
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar de performance de {player_data['player_name']} vs {nb_players} joueurs dans sa catégorie {rating_text}</h4>",
                            unsafe_allow_html=True
                        )

                        # Construction de la pizza plot (joueur-médiane à son poste) pour les statistiques avancées
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player_norm * 100,
                            median_values=group_median * 100,
                            title=f"Statistiques avancées de {player_data['player_name']} de vs Médiane à son poste",
                            legend_labels=(player_data['player_name'], "Médiane poste")
                        )

                        # Liste des colonnes à afficher selon le poste
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
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
                                    labels=pizza_labels,
                                    player_values=player_scaled,
                                    median_values=median_scaled,
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
                    # Affichage du titre
                    st.markdown(
                        f"<h4 style='text-align: center;'>Joueurs similaires à {player_data['player_name']}</h4>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(similar_df)
                else:
                    st.info("Aucun joueur similaire trouvé avec les critères sélectionnés.")


        elif lang == "English":
            # Display the title
            st.markdown("<h4 style='text-align: center;'>📊 Player analysis</h4>", unsafe_allow_html=True)

            df = pd.read_csv('../data/player/database_player.csv') # Collect the data

            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist()) # Extract the list of players

            selected_player = st.sidebar.selectbox("Select a player :", player_names) # Select a player

            # If a player is selected, the image is hidden.   
            if not selected_player:
                # No player selected → show intro image
                st.image("../image/player_analysis.jpg")
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
                st.markdown(
                    f"<h4 style='text-align: center;'>Player profile</h4>",
                    unsafe_allow_html=True
                )

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
                comparison_filter = st.radio(
                    "Compared to his position :",
                    options=[
                        "Overview",
                        "Championship",
                        "Age group",
                        "Country"
                    ],
                    index=0,
                    horizontal=True
                )

                filter_arg = {
                    "Overview": None,
                    "Championship": "championnat",
                    "Age group": "tranche_age",
                    "Country": "pays"
                }[comparison_filter]

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
                            - **Int_per90**: Interceptions per 90 minutes  
                            - **Tkl_per90**: Tackles per 90 minutes  
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
                            - **Int_per90**: Interceptions per 90 minutes  
                            - **Tkl_per90**: Tackles per 90 minutes  
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
                            - **Int_per90**: Interceptions per 90 minutes  
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

                if poste_cat and poste_cat in category_stats:
                    stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]
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

                        # The percentile rank is established for each player by category (0 = lowest, 1 = highest)
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        # We are reversing the metrics where ‘smaller = better’
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        # The player's profile is standardised in percentiles.
                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0)

                        # The median is calculated according to position category.
                        group_median = (
                            rank_pct.drop(index=player_data['player_name'], errors='ignore')
                                    .median()
                                    .reindex(stats_cols)
                                    .fillna(0)
                        )
                        # Rating calculation if available
                        rating_text = f" - Rating : {round(player_rating, 2)}" if player_rating is not None else ""

                        # Title display with note
                        st.markdown(
                            f"<h4 style='text-align: center;'>Performance radar from {player_data['player_name']} vs {nb_players} players in his category {rating_text}</h4>",
                            unsafe_allow_html=True
                        )
                        
                        # Bulding the pizza plot (player-median) for the advanced statistics
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player_norm * 100,
                            median_values=group_median * 100,
                            title=f"Advanced statistics of {player_data['player_name']} vs. median at the same position",
                            legend_labels=(player_data['player_name'], "Median position")
                        )

                        # List of columns to be displayed by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

                        # We keep only the columns present
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                        # Checks that all columns exist for the player
                        if all(col in player_data for col in pizza_cols):

                            player_values = [player_data[col] for col in pizza_cols]

                            # Calculation of median values on the filtered group
                            group_df_scores = group_df[pizza_cols].dropna()
                            if len(group_df_scores) >= 5:
                                group_median = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median]

                                # Bulding the pizza plot (player-median) for the basic statistics
                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,
                                    player_values=player_scaled,
                                    median_values=median_scaled,
                                    title=f"Basic statistics of {player_data['player_name']} vs. median at the same position",
                                    legend_labels=(player_data['player_name'], "Median position")
                                )

                        # List of columns to be displayed by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

                        # We keep only the columns present
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                        # Checks that all columns exist for the player
                        if all(col in player_data for col in pizza_cols):

                            player_values = [player_data[col] for col in pizza_cols]

                            # Calculation of median values on the filtered group
                            group_df_scores = group_df[pizza_cols].dropna()
                            if len(group_df_scores) >= 5:
                                group_median = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median]


                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,
                                    player_values=player_scaled,
                                    median_values=median_scaled,
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
                    # Display the title
                    st.markdown(
                        f"<h4 style='text-align: center;'>Players similar to {player_data['player_name']}</h4>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(similar_df)
                else:
                    st.info("Not enough players in this group to generate a radar (minimum requirement: 5).")
        else:
            # Título
            st.markdown("<h4 style='text-align: center;'>📊 Análisis de un jugador</h4>", unsafe_allow_html=True)

            df = pd.read_csv('../data/player/database_player.csv')  # Cargar datos

            player_names = [''] + sorted(df['player_name'].dropna().unique().tolist())  # Lista de jugadores

            selected_player = st.sidebar.selectbox("Elige un jugador:", player_names)  # Selección de jugador

            # Si no hay jugador seleccionado → mostrar imagen de introducción
            if not selected_player:
                st.image("../image/player_analysis.jpg")  # Banner de introducción
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
                comparison_filter = st.radio(
                    "En comparación con su posición:",
                    options=[
                        "Vista general",
                        "Liga",
                        "Tramo de edad",
                        "País"
                    ],
                    index=0,
                    horizontal=True
                )

                # Mapeo de la opción de UI (ES) a las claves internas usadas en tu lógica
                filter_arg = {
                    "Vista general": None,
                    "Liga": "championnat",
                    "Tramo de edad": "tranche_age",
                    "País": "pays"
                }[comparison_filter]

                # ⚠️ Categoría del puesto: se mantiene en FRANCÉS
                poste_cat = position_category.get(player_data['position'], None)

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
                            - **Int_per90**: Intercepciones por 90 minutos  
                            - **Tkl_per90**: Entradas por 90 minutos  
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
                            - **Int_per90**: Intercepciones por 90 minutos  
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

                if poste_cat and poste_cat in category_stats:
                    stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]
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

                        # Percentiles por categoría (0 = peor, 1 = mejor)
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        # Invertir métricas donde "más pequeño = mejor"
                        invert_stats = globals().get("invert_stats", set())
                        for col in stats_cols:
                            if col in invert_stats:
                                rank_pct[col] = 1 - rank_pct[col]

                        # Perfil del jugador normalizado (percentiles)
                        player_norm = rank_pct.loc[player_data['player_name']].reindex(stats_cols).fillna(0)

                        # Mediana del grupo (sin el propio jugador)
                        group_median = (
                            rank_pct
                            .drop(index=player_data['player_name'], errors='ignore')
                            .median()
                            .reindex(stats_cols)
                            .fillna(0)
                        )

                        # Nota si existe
                        rating_text = f" - Nota: {round(player_rating, 2)}" if player_rating is not None else ""

                        # Título con nota
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar de rendimiento de {player_data['player_name']} frente a {nb_players} jugadores de su categoría{rating_text}</h4>",
                            unsafe_allow_html=True
                        )

                        # Radar (avanzadas)
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player_norm * 100,
                            median_values=group_median * 100,
                            title=f"Estadísticas avanzadas de {player_data['player_name']} vs Mediana del puesto",
                            legend_labels=(player_data['player_name'], "Mediana del puesto")
                        )

                        # Columnas para el radar (básicas)
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

                        # Mantener solo las columnas presentes
                        pizza_cols = [col for col in pizza_cols if col in df.columns]
                        # Etiquetas en español
                        pizza_labels = [translate_base_stat(col.replace("score_", ""), lang="es") for col in pizza_cols]

                        # Verificar que el jugador tenga todas las columnas
                        if all(col in player_data for col in pizza_cols):

                            player_values = [player_data[col] for col in pizza_cols]

                            # Mediana del grupo para estas columnas
                            group_df_scores = group_df[pizza_cols].dropna()
                            if len(group_df_scores) >= 5:
                                group_median_list = group_df_scores.median().tolist()

                                player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                                median_scaled = [round(v) for v in group_median_list]

                                # Radar (básicas)
                                fig_pizza_stat_basis = plot_pizza_radar(
                                    labels=pizza_labels,
                                    player_values=player_scaled,
                                    median_values=median_scaled,
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

                # Jugadores similares (mismo filtro)
                similar_df = find_similar_players(selected_player, df, filter_type=filter_arg)
                if not similar_df.empty:
                    st.markdown(
                        f"<h4 style='text-align: center;'>Jugadores similares a {player_data['player_name']}</h4>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(similar_df)
                else:
                    st.info("No se encontraron jugadores similares con los criterios seleccionados.")
            

    elif selected in ["Duel", "F2F", "Duelo"]:
        if lang == "Français":
            st.markdown(
                "<h4 style='text-align: center;'>🥊 Comparaison de deux joueurs</h4>", 
                unsafe_allow_html=True)
            

            df = pd.read_csv("../data/player/database_player.csv") # Récupérer les données
            player_names = sorted(df['player_name'].dropna().unique().tolist()) # Ordonner par le nom du joueur

            st.sidebar.markdown("### Sélection des joueurs") # Sélection dans la sidebar

            player1 = st.sidebar.selectbox("Premier joueur :", [''] + player_names, key="player1") # Sélection du 1er joueur
            
            if not player1:
                # Aucun joueur sélectionné → afficher l'image d'intro
                st.image("../image/player_comparison.jpg")
                st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")

            if player1:
                # Nous stockons les informations du 1er joueur
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None)

                # Tous les position de la même catégorie
                sub_positions_same_cat = [
                    pos for pos, cat in position_category.items() if cat == poste_cat
                ]

                # On filtre tous les joueurs ayant un poste dans cette catégorie
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]


                player2 = st.sidebar.selectbox("Second joueur (même poste) :", [''] + player2_names, key="player2") # Sélection du 2nd joueur
                
                if not player2:
                    # Aucun joueur sélectionné → afficher l'image d'intro
                    st.image("../image/player_comparison.jpg")
                    st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")


                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0] # Récupération du nom du 2nd joueur
                    
                    # On affiche le profil des joueurs
                    st.markdown("<h4 style='text-align: center;'>Profils des joueurs</h4>", unsafe_allow_html=True)

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
                                - **Int_per90** : Interceptions par 90 minutes
                                - **Tkl_per90** : Tacles par 90 minutes
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
                                - **Int_per90** : Interceptions par 90 minutes
                                - **Tkl_per90** : Tacles par 90 minutes
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
                                - **Int_per90** : Interceptions par 90 minutes
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
                    if poste_cat and poste_cat in category_stats:
                        stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]  # On récupère la catégories de stats selon le poste

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
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar comparatif : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",
                            unsafe_allow_html=True
                        )
                        
                        # Création de la la pizza plot des statistiques avancées
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player1_norm * 100,
                            median_values=player2_norm * 100,
                            title=f"Statistiques avancées de {player1} vs {player2}",
                            legend_labels=(player1, player2)
                        )

                        # Liste de colonnes de score par poste
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

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
                                labels=pizza_labels,
                                player_values=player1_scaled,
                                median_values=player2_scaled,
                                title=f"Statistiques de base de {player1} vs {player2}",
                                legend_labels=(player1, player2)
                            )

                        # Affichage dans Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)

        elif lang == "English":
            # Display the title
            st.markdown(
                "<h4 style='text-align: center;'>🥊 Player Comparison</h4>", 
                unsafe_allow_html=True)

            df = pd.read_csv("../data/player/database_player.csv") # Recover the data
            player_names = sorted(df['player_name'].dropna().unique().tolist()) # Order by data 

            st.sidebar.markdown("### Player selection") # Selection in the sidebar

            player1 = st.sidebar.selectbox("First player :", [''] + player_names, key="player1") # Select the first player
            
            if not player1:
                # If the player is selected, we hide the image
                st.image("../image/player_comparison.jpg")
                st.info("Scroll down the sidebar to select the language and players for analysis")

            if player1:
                # Collecting the data for the players
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None)

                # All positions in the same category
                sub_positions_same_cat = [
                    pos for pos, cat in position_category.items() if cat == poste_cat
                ]

                # We filter all players with a position in this category
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]

                player2 = st.sidebar.selectbox("Second player (same position) :", [''] + player2_names, key="player2") # Select the 2nd player
                
                if not player2:
                    # If the player is selected, we hide the image
                    st.image("../image/player_comparison.jpg")
                    st.info("Scroll down the sidebar to select the language and players for analysis")
                        
                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0] # Collecting the name of the player 2
                    
                    # We display players profiles
                    st.markdown("<h4 style='text-align: center;'>Players profile</h4>", unsafe_allow_html=True)

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
                                - **Int_per90**: Interceptions per 90 minutes  
                                - **Tkl_per90**: Tackles per 90 minutes  
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
                                - **Int_per90**: Interceptions per 90 minutes  
                                - **Tkl_per90**: Tackles per 90 minutes  
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
                                - **Int_per90**: Interceptions per 90 minutes  
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
                    if poste_cat and poste_cat in category_stats:
                        stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]  # We retrieve the stat categories according to position.

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

                        # We are reversing the metrics where ‘smaller = better’
                        invert_stats = globals().get("invert_stats", set())
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
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar comparison : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",
                            unsafe_allow_html=True
                        )
                        
                        # Creating the advanced statistics pizza plot
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player1_norm * 100,
                            median_values=player2_norm * 100,
                            title=f"Advanced statistics of {player1} vs {player2}",
                            legend_labels=(player1, player2)
                        )

                        # List of score columns by position
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

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
                                labels=pizza_labels,
                                player_values=player1_scaled,
                                median_values=player2_scaled,
                                title=f"Basic statistics of {player1} vs {player2}",
                                legend_labels=(player1, player2)
                            )

                        # Display in Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)
        
        else:
            st.markdown(
                "<h4 style='text-align: center;'>🥊 Comparación de dos jugadores</h4>", 
                unsafe_allow_html=True)

            df = pd.read_csv("../data/player/database_player.csv")  # Cargar datos
            player_names = sorted(df['player_name'].dropna().unique().tolist())  # Ordenar por nombre

            st.sidebar.markdown("### Selección de jugadores")  # Selección en la barra lateral

            player1 = st.sidebar.selectbox("Primer jugador:", [''] + player_names, key="player1")  # Jugador 1

            if not player1:
                # Sin selección → imagen de intro
                st.image("../image/player_comparison.jpg")
                st.info("Despliega la barra lateral para elegir el idioma y los jugadores a analizar")

            if player1:
                # Datos del primer jugador
                player1_data = df[df['player_name'] == player1].iloc[0]
                sub_position = player1_data['position']
                poste_cat = position_category.get(sub_position, None) 

                # Todas las position de la misma categoría
                sub_positions_same_cat = [pos for pos, cat in position_category.items() if cat == poste_cat]

                # Filtrar jugadores de la misma categoría
                same_category_players = df[df['position'].isin(sub_positions_same_cat)]
                player2_names = sorted(same_category_players['player_name'].dropna().unique().tolist())
                player2_names = [p for p in player2_names if p != player1]

                player2 = st.sidebar.selectbox("Segundo jugador (misma posición):", [''] + player2_names, key="player2")  # Jugador 2

                if not player2:
                    st.image("../image/player_comparison.jpg")
                    st.info("Despliega la barra lateral para elegir el idioma y los jugadores a analizar")

                if player2:
                    player2_data = df[df['player_name'] == player2].iloc[0]  # Datos del segundo jugador

                    # Perfiles de los jugadores
                    st.markdown("<h4 style='text-align: center;'>Perfiles de los jugadores</h4>", unsafe_allow_html=True)

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
                                - **Int_per90**: Intercepciones por 90 minutos
                                - **Tkl_per90**: Entradas por 90 minutos
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
                                - **Int_per90**: Intercepciones por 90 minutos
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
                    if poste_cat and poste_cat in category_stats:
                        stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]

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

                        # Percentiles (0 = peor, 1 = mejor)
                        rank_pct = radar_vals.rank(pct=True, method='average', ascending=True)

                        # Invertir métricas donde "más pequeño = mejor"
                        invert_stats = globals().get("invert_stats", set())
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
                        st.markdown(
                            f"<h4 style='text-align: center;'>Radar comparativo: {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",
                            unsafe_allow_html=True
                        )

                        # Radar de estadísticas avanzadas
                        fig_pizza_stat_adv = plot_pizza_radar(
                            labels=stats_cols,
                            player_values=player1_norm * 100,
                            median_values=player2_norm * 100,
                            title=f"Estadísticas avanzadas de {player1} vs {player2}",
                            legend_labels=(player1, {player2})
                        )

                        # Columnas de puntuación por puesto
                        if poste_cat == "Gardiens de but":
                            pizza_cols = [
                                "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                                "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                            ]
                        else:
                            pizza_cols = [
                                "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                                "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                                "score_faults_committed", "score_provoked_fouls", "score_aerial"
                            ]

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
                                labels=pizza_labels,
                                player_values=player1_scaled,
                                median_values=player2_scaled,
                                title=f"Estadísticas básicas de {player1} vs {player2}",
                                legend_labels=(player1, player2)
                            )

                        # Mostrar en Streamlit
                        col1, col2 = st.columns(2)
                        with col1:
                            st.pyplot(fig_pizza_stat_basis)
                        with col2:
                            st.pyplot(fig_pizza_stat_adv)


    elif selected == "Stats +":
        # Page en français
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏅 Classement des joueurs (0-100) pour les statistiques aggrégées par catégorie selon leur poste</h4>", unsafe_allow_html=True) # Affichage du titre de la page
            df = pd.read_csv("../data/player/database_player.csv") # Récupération des données
            
            # Récupération des colonnes "score_" + "rating"
            all_stats_raw = [col for col in df.columns if col.startswith("score_")]
            if "rating" in df.columns:
                all_stats_raw.append("rating")

            # Traduction pour l'affichage
            fr_map = base_stat_translation.get("fr", {})

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
                st.image("../image/player_ranking_basis.jpg")
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

                    valeur_max = st.slider(
                        "Valeur marchande maximum (€)",
                        valeur_min_possible,
                        valeur_max_possible,
                        valeur_max_possible,
                        step=100000,
                        format="%d"
                    )

                    st.markdown(f"Valeur maximum sélectionné : **{format_market_value(valeur_max)}**") # Affichage du choix de l'utilisateur
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]

                # Définir les statistiques spécifiques aux gardiens
                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]

                # Liste de colonnes
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue','contract',
                    'position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Filtrage conditionnel selon la statistique sélectionnée
                if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                    df_stat = df_stat[df_stat['position'] == 'Goalkeeper']
                else:
                    df_stat = df_stat[df_stat['position'] != 'Goalkeeper']

                df_stat['position'] = df_stat['position'].apply(
                    lambda x: translate_position(x, lang="fr")
                )

                # Traduction du pays du joueur dans la table
                df_stat['nationality'] = df_stat['nationality'].apply(
                    lambda x: translate_country(x, lang="fr")
                )
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
                final_df = final_df[[
                    'player_name', 'Statistique', 'Age', 'nationality', 'club_name', 'position','marketValue', 'contract'
                ]]

                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":

            st.markdown("<h4 style='text-align: center;'>🏅 Player rankings (0-100) for aggregate statistics by category according to their position</h4>", unsafe_allow_html=True) # Display title
            df = pd.read_csv("../data/player/database_player.csv") # Collect the data
            
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
                st.image("../image/player_ranking_basis.jpg")
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

                    valeur_max = st.slider(
                        "Maximum market value (€)",
                        valeur_min_possible,
                        valeur_max_possible,
                        valeur_max_possible,
                        step=100000,
                        format="%d"
                    )

                    st.markdown(f"Maximum value selected: **{format_market_value(valeur_max)}**") # Display the choice of the user
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valeur_max]
            

                # Define statistics specific to goalkeepers
                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]
                # Selecting columns
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','position',
                    'Comp', 'marketValue','contract', selected_stat]
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

                # Closing the container
                podium_html += "</div>"

                # Final display
                st.markdown(podium_html, unsafe_allow_html=True)

                # We display the table with the columns desired
                final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
                final_df = final_df[[
                    'player_name', 'Statistic', 'Age', 'nationality', 'club_name', 'position', 'marketValue', 'contract'
                ]]

                st.dataframe(final_df, use_container_width=True)
        
        else:
            # Página en español
            st.markdown("<h4 style='text-align: center;'>🏅 Clasificación de jugadores (0-100) para estadísticas agregadas por categoría según su posición</h4>", unsafe_allow_html=True)
            df = pd.read_csv("../data/player/database_player.csv")  # Cargar datos

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
                st.image("../image/player_ranking_basis.jpg")
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

                    valor_max = st.slider(
                        "Valor de mercado máximo (€)",
                        valor_min_posible,
                        valor_max_posible,
                        valor_max_posible,
                        step=100000,
                        format="%d"
                    )

                    st.markdown(f"Valor máximo seleccionado: **{format_market_value(valor_max)}**")
                    filtered_df = filtered_df[filtered_df["marketValue"] <= valor_max]

                # Stats específicas de porteros
                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]

                # Subconjunto de columnas
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue', 'contract',
                    'position', selected_stat]
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
                final_df = final_df[
                    ['player_name', 'Estadística', 'Age', 'nationality', 'club_name',
                    'position', 'marketValue', 'contract']
                ]

                st.dataframe(final_df, use_container_width=True)

    elif selected == "Stats":
        # Page en français
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'>🏆 Classement des joueurs pour les statistiques brutes</h4>", unsafe_allow_html=True) # Affichage du titre de la page
            df = pd.read_csv("../data/player/database_player.csv") # Récupération des données

            all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # Liste des statistiques disponibles

            selected_stat = st.sidebar.selectbox("Choisissez une statistique :", [""] + all_stats) # Choix de la statistique dans la sidebar
            
            if not selected_stat:
                # Si la métrique est selectionné, nous cachons l'image
                st.image("../image/player_ranking.jpg")
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

                    valeur_max = st.slider(
                        "Valeur marchande maximum (€)",
                        valeur_min_possible,
                        valeur_max_possible,
                        valeur_max_possible,
                        step=100000,
                        format="%d"
                    )

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
                thresholds = {
                    'Cmp%': ('Cmp', 50),
                    'Tkl%': ('Tkl', 7),
                    'Won%': ('Won', 6),
                    'Succ%': ('Succ', 6)
                }

                if selected_stat in thresholds:
                    col, min_value = thresholds[selected_stat]
                    
                    # S'assurer que la colonne existe et que les valeurs sont numériques
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                        st.markdown(f"<small><strong>Filtre : {col} > {min_value}</strong></small>", unsafe_allow_html=True)

                # Liste de colonnes
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name','Comp', 'marketValue','contract',
                    'position', selected_stat]
                ].dropna(subset=[selected_stat])

                # Traduction du pays du joueur dans la table
                df_stat['nationality'] = df_stat['nationality'].apply(
                    lambda x: translate_country(x, lang="fr")
                )
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

                df_stat['position'] = df_stat['position'].apply(
                    lambda x: translate_position(x, lang="fr")
                )
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
                final_df = final_df[[
                    'player_name', 'Statistique', 'Age', 'nationality', 'club_name', 'position','marketValue', 'contract'
                ]]

                st.dataframe(final_df, use_container_width=True)

        elif lang == "English":
            st.markdown("<h4 style='text-align: center;'>🏆 Player rankings for raw statistics</h4>", unsafe_allow_html=True) # Display the title
            
            df = pd.read_csv("../data/player/database_player.csv") # Recovering data

            all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # List of available statistics

            selected_stat = st.sidebar.selectbox("Choose a metric :", [""] + all_stats) # Choice of statistics in the sidebar
            
            if not selected_stat:
                # If the metric is selected, we hide the image
                st.image("../image/player_ranking.jpg")
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

                    valeur_max = st.slider(
                        "Maximum market value (€)",
                        valeur_min_possible,
                        valeur_max_possible,
                        valeur_max_possible,
                        step=100000,
                        format="%d"
                    )

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
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name',
                    'Comp', 'marketValue','contract',
                    'position', selected_stat]
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
                final_df = final_df[[
                    'player_name', 'Statistic', 'Age', 'nationality', 'club_name', 'marketValue', 'contract'
                ]]

                st.dataframe(final_df, use_container_width=True)
        else:
            # Página en español
            st.markdown("<h4 style='text-align: center;'>🏆 Clasificación de jugadores por estadísticas brutas</h4>", unsafe_allow_html=True)
            df = pd.read_csv("../data/player/database_player.csv")  # Cargar datos

            # Lista de estadísticas disponibles
            all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns))

            # Selección de la estadística en la barra lateral
            selected_stat = st.sidebar.selectbox("Elige una estadística:", [""] + all_stats)

            if not selected_stat:
                st.image("../image/player_ranking.jpg")
                st.info("Despliega la barra lateral para seleccionar el idioma, la métrica y los filtros que quieras")

            if selected_stat:
                # --- Filtros en la barra lateral ---
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

                    valor_max = st.slider(
                        "Valor de mercado máximo (€)",
                        valor_min_posible,
                        valor_max_posible,
                        valor_max_posible,
                        step=100000,
                        format="%d"
                    )

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
                thresholds = {
                    'Cmp%': ('Cmp', 50),
                    'Tkl%': ('Tkl', 7),
                    'Won%': ('Won', 6),
                    'Succ%': ('Succ', 6)
                }

                if selected_stat in thresholds:
                    col, min_value = thresholds[selected_stat]
                    if col in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                        st.markdown(f"<small><strong>Filtro: {col} > {min_value}</strong></small>", unsafe_allow_html=True)

                # Subconjunto de columnas
                df_stat = filtered_df[
                    ['player_name', 'imageUrl', 'Age', 'nationality', 'club_name',
                    'Comp', 'marketValue', 'contract',
                    'position', selected_stat]
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
                final_df = final_df[
                    ['player_name', 'Estadística', 'Age', 'nationality', 'club_name',
                    'position', 'marketValue', 'contract']
                ]

                st.dataframe(final_df, use_container_width=True)

    elif selected == "Scout":
        # Page en français
        if lang == "Français":
            st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True) # Affichage du titre de la page
            df = pd.read_csv("../data/player/database_player.csv") # Récupération des données
            
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

            # Statistiques avancées (à partir de la 30e colonne)
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[42:]
            selected_adv_stats = st.multiselect("Statistiques brutes", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Nombre de joueurs à afficher", 3, 1800, 10) # Choix de nombre de joueurs à afficher
            
            # Injecte du CSS pour centrer tous les boutons
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

            # Et ici le vrai bouton fonctionnel
            recherche = st.button("🔍 Rechercher")

            # On s'assure qu'un minimum d'informations a été renseigné
            nb_filled = sum([
                bool(pays_fr), bool(poste_fr), bool(contract_year), bool(championnat),
                bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0
            ])

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
                    thresholds = {
                        'Cmp%': ('Cmp', 50),
                        'Tkl%': ('Tkl', 7),
                        'Won%': ('Won', 6),
                        'Succ%': ('Succ', 6)
                    }

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
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name",
                                    "position", "marketValue", "contract", "rating"] + all_stats

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
            df = pd.read_csv("../data/player/database_player.csv") # Recover the data 

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

            # Advanced statistics (from column 30)
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[30:]
            selected_adv_stats = st.multiselect("Raw statistics", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Number of players to display", 3, 1800, 10) # Choice of the number of players to display

            # Inject CSS to center all buttons
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

            # And here's the real functional button
            search = st.button("🔍 Search")


            # We want that 1 criterias to start the search
            nb_filled = sum([
                bool(country), bool(position), bool(contract_year), bool(leagues),
                bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0
            ])

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
                    thresholds = {
                        'Cmp%': ('Cmp', 50),
                        'Tkl%': ('Tkl', 7),
                        'Won%': ('Won', 6),
                        'Succ%': ('Succ', 6)
                    }

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

                    goalkeeper_stats = [
                        "goal_scoring_conceded", "efficiency", "error_fouls",
                        "short_clearance", "long_clearance", "positioning", "aerial_defense"
                    ]
                    selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                    
                    if selected_goalkeeper_stats:
                        df_filtered = df_filtered[df_filtered["position"] == "Goalkeeper"]
                    elif selected_base_stats:
                        df_filtered = df_filtered[df_filtered["position"] != "Goalkeeper"]

                    all_stats = selected_base_stats + selected_adv_stats
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name",
                                    "position", "marketValue", "contract", "rating"] + all_stats # We choose the list of informations collected

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
            # Página en español
            st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True)
            df = pd.read_csv("../data/player/database_player.csv")  # Cargar datos

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

            # Estadísticas avanzadas (a partir de la columna 30)
            selected_adv_stats, adv_stat_limits = [], {}
            adv_columns = df.columns[30:]
            selected_adv_stats = st.multiselect("Estadísticas brutas", list(adv_columns), placeholder="")
            for stat in selected_adv_stats:
                if stat in df.columns:
                    min_val, max_val = float(df[stat].min()), float(df[stat].max())
                    adv_stat_limits[stat] = st.slider(f"{stat} (mín / máx)", min_val, max_val, (min_val, max_val))

            nb_players = st.slider("Número de jugadores a mostrar", 3, 1800, 10)

            # CSS para centrar botones
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

            # Botón
            recherche = st.button("🔍 Buscar")

            # Mínimo de información rellenada
            nb_filled = sum([
                bool(pais_es), bool(poste_es), bool(contract_year), bool(campeonato),
                bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0
            ])

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
                    thresholds = {
                        'Cmp%': ('Cmp', 50),
                        'Tkl%': ('Tkl', 7),
                        'Won%': ('Won', 6),
                        'Succ%': ('Succ', 6)
                    }
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
                    display_columns = ["player_name", "imageUrl", "Age", "nationality", "club_name",
                                    "position", "marketValue", "contract", "rating"] + all_stats

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
