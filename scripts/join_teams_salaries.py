import pandas as pd
from pathlib import Path
from unidecode import unidecode

# Leer datos | Lire les données | Read data
df_salaries = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/teams_salaries.csv')
df_all_teams_stats = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/grouped_stats.csv')

# Columnas de interés | Colonnes d'intérêt | Columns of interest
weekly_col = 'Weekly Wages' if 'Weekly Wages' in df_salaries.columns else 'Weekly Wages'
annual_col = 'Annual Wages' if 'Annual Wages' in df_salaries.columns else 'Annual Wages'
estimated_col = '% Estimated' if '% Estimated' in df_salaries.columns else '% Estimated'

# Función para normalizar nombres: quitar acentos, espacios y pasar a minúsculas | Fonction pour normaliser les noms : enlever accents, espaces et mettre en minuscules | Function to normalize names: remove accents, strip spaces, lowercase
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

# Crear columnas normalizadas para merge | Créer des colonnes normalisées pour la jointure | Create normalized columns for merge
df_salaries['Squad_norm'] = df_salaries['Squad'].apply(normalize_name)
df_all_teams_stats['Squad_norm'] = df_all_teams_stats['Squad'].apply(normalize_name)

# Definir claves de unión | Définir les clés de fusion | Define merge keys
if all(k in df_salaries.columns for k in ['Competition','Squad']) and \
   all(k in df_all_teams_stats.columns for k in ['Competition','Squad']):
    merge_keys = ['Competition', 'Squad_norm']  # usar Competition + Squad si existe | utiliser Competition + Squad si disponible | use Competition + Squad if exists
else:
    merge_keys = ['Squad_norm']  # si no, solo Squad | sinon seulement Squad | otherwise only Squad

# Preparar df de salarios con columnas necesarias y sin duplicados | Préparer le df des salaires avec les colonnes nécessaires et supprimer les doublons | Prepare salary df with necessary columns and remove duplicates
cols_keep = [c for c in merge_keys + [weekly_col, annual_col, estimated_col] if c in df_salaries.columns] + ['Squad_norm']
sal = df_salaries[cols_keep].drop_duplicates(subset=merge_keys, keep='first')

# Merge LEFT: conservar todo de df_all_teams_stats y añadir salarios | Jointure LEFT: conserver tout de df_all_teams_stats et ajouter les salaires | LEFT Merge: keep all from df_all_teams_stats and add salaries
df_all_teams_stats = df_all_teams_stats.merge(sal, on=merge_keys, how='left')

# Guardar CSV | Enregistrer CSV | Save CSV
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
out_path = data_dir / "join_teams_salaries.csv"
df_all_teams_stats.to_csv(out_path, index=False, encoding="utf-8")
