import pandas as pd
import numpy as np
import os

# ----------------------------------------------------------
# Cargar datos / Load data / Charger les données
# ----------------------------------------------------------
df = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/player/players_data-2025_2026.csv")

# ----------------------------------------------------------
# Mapeo de posiciones / Position mapping / Correspondance des postes
# ----------------------------------------------------------
pos_map = {
    'DF': 'Defender',
    'MF': 'Midfielder',
    'FW': 'Forward',
    'GK': 'Goalkeeper'
}

def expand_positions(pos):
    if pd.isna(pos):
        return np.nan
    if not isinstance(pos, str):
        pos = str(pos)
    parts = [p.strip() for p in pos.split(',') if p and p.strip()]
    parts = ['DF' if p == 'D' else p for p in parts]
    full_parts = [pos_map.get(p, p) for p in parts]
    return ','.join(full_parts)

df['Pos'] = df['Pos'].apply(expand_positions)

# ----------------------------------------------------------
# Posición primaria y secundaria / Primary & secondary position / Poste principal et secondaire
# ----------------------------------------------------------
pos_tokens = df['Pos'].str.split(r'\s*,\s*', regex=True)
df['primary_pos'] = pos_tokens.str[0]
df['secondary_pos'] = pos_tokens.str[1]

df['primary_pos'].replace('', pd.NA, inplace=True)
df['secondary_pos'].replace('', pd.NA, inplace=True)

# ----------------------------------------------------------
# Normalización de países / Nation normalization / Normalisation des pays
# ----------------------------------------------------------
df['Nation'] = df['Nation'].str.split().str[1]
df['Comp'] = df['Comp'].str.split().str[1]

nation_mapping = {
    'ENG': 'England', 'ESP': 'Spain', 'IRL': 'Ireland', 'FRA': 'France', 'MAR': 'Morocco',
    'ALG': 'Algeria', 'EGY': 'Egypt', 'TUN': 'Tunisia', 'KSA': 'Saudi Arabia', 'DEN': 'Denmark',
    'BRA': 'Brazil', 'ITA': 'Italy', 'NGA': 'Nigeria', 'SCO': 'Scotland', 'USA': 'USA',
    'AUT': 'Austria', 'GER': 'Germany', 'CIV': 'Ivory Coast', 'MNE': 'Montenegro', 'SUI': 'Switzerland',
    'SWE': 'Sweden', 'GHA': 'Ghana', 'NOR': 'Norway', 'ROU': 'Romania', 'NED': 'Netherlands',
    'ARG': 'Argentina', 'PAR': 'Paraguay', 'GAB': 'Gabon', 'POR': 'Portugal', 'MEX': 'Mexico',
    'SEN': 'Senegal', 'PAN': 'Panama', 'PUR': 'Puerto Rico', 'JAM': 'Jamaica', 'URU': 'Uruguay',
    'VEN': 'Venezuela', 'HAI': 'Haiti', 'ISL': 'Iceland', 'JPN': 'Japan', 'ALB': 'Albania',
    'COL': 'Colombia', 'TOG': 'Togo', 'GUI': 'Guinea', 'CRO': 'Croatia', 'SLE': 'Sierra Leone',
    'CAN': 'Canada', 'COD': 'Congo (DR)', 'CMR': 'Cameroon', 'HUN': 'Hungary', 'ZAM': 'Zambia',
    'CZE': 'Czech Republic', 'BEL': 'Belgium', 'SUR': 'Suriname', 'POL': 'Poland', 'SVK': 'Slovakia',
    'GNB': 'Guinea-Bissau', 'SVN': 'Slovenia', 'MLI': 'Mali', 'NIR': 'Northern Ireland', 'SRB': 'Serbia',
    'CHI': 'Chile', 'WAL': 'Wales', 'AUS': 'Australia', 'NZL': 'New Zealand', 'ECU': 'Ecuador',
    'TUR': 'Turkey', 'GAM': 'Gambia', 'CGO': 'Congo', 'BAN': 'Bangladesh', 'EQG': 'Equatorial Guinea',
    'CPV': 'Cape Verde', 'GEO': 'Georgia', 'BIH': 'Bosnia and Herzegovina', 'BFA': 'Burkina Faso',
    'GRE': 'Greece', 'UKR': 'Ukraine', 'MKD': 'North Macedonia', 'CRC': 'Costa Rica', 'MAS': 'Malaysia',
    'LTU': 'Lithuania', 'RUS': 'Russia', 'DOM': 'Dominican Republic', 'IRQ': 'Iraq', 'KOR': 'South Korea',
    'PHI': 'Philippines', 'BEN': 'Benin', 'IDN': 'Indonesia', 'FIN': 'Finland', 'ZIM': 'Zimbabwe',
    'ISR': 'Israel', 'CYP': 'Cyprus', 'UZB': 'Uzbekistan', 'ANG': 'Angola', 'CTA': 'Central African Republic',
    'GLP': 'Guadeloupe', 'MAD': 'Madagascar', 'PER': 'Peru', 'MOZ': 'Mozambique', 'EST': 'Estonia',
    'ARM': 'Armenia', 'KVX': 'Kosovo', 'LBY': 'Libya', 'BDI': 'Burundi', 'KEN': 'Kenya',
    'COM': 'Comoros', 'MDA': 'Moldova', 'GUF': 'French Guiana', 'MTQ': 'Martinique', 'MSR': 'Montserrat',
    'LUX': 'Luxembourg', 'JOR': 'Jordan', 'IRN': 'Iran', 'MLT': 'Malta', 'CUW': 'Curaçao',
    'PLE': 'Palestine', 'BUL': 'Bulgaria', 'BOE': 'Bonaire', 'CUB': 'Cuba', 'BLR': 'Belarus',
    'RSA': 'South Africa', 'AND': 'Andorra', 'LBR': 'Liberia', 'THA': 'Thailand', 'SYR': 'Syria',
    'RWA': 'Rwanda', 'UGA': 'Uganda', 'HON': 'Honduras', 'GUA': 'Guatemala', 'GUY': 'Guyana',
    'TRI': 'Trinidad and Tobago', 'SLV': 'El Salvador', 'GRN': 'Grenada', 'NAM': 'Namibia', 'BER': 'Bermuda'
}

df['Nation'] = df['Nation'].replace(nation_mapping)

# ----------------------------------------------------------
# Exportar archivo final a data/players/fbref/
# Export final file to data/players/fbref/
# Exporter le fichier final vers data/players/fbref/
# ----------------------------------------------------------
output_dir = "data/players/fbref"
output_filename = f"{output_dir}/fbref_players_2026.csv"

# Crear directorios si no existen / Create directories / Créer les dossiers
os.makedirs(output_dir, exist_ok=True)

df.to_csv(output_filename, index=False)

print(f"Archivo exportado a: {output_filename}")
# File exported
# Fichier exporté
