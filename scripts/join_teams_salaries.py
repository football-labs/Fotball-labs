import pandas as pd
from pathlib import Path

df_salaries = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/teams_salaries.csv')
df_all_teams_stats = pd.read_csv('https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/grouped_stats.csv')

weekly_col = 'Weekly Wages (EUR)' if 'Weekly Wages (EUR)' in df_salaries.columns else 'Weekly Wages'
annual_col = 'Annual Wages (EUR)' if 'Annual Wages (EUR)' in df_salaries.columns else 'Annual Wages'
annual_col = '% Estimated' if '% Estimated' in df_salaries.columns else '% Estimated'
# Claves de unión: Competition + Squad si es posible; si no, solo Squad
if all(k in df_salaries.columns for k in ['Competition','Squad']) and \
   all(k in df_all_teams_stats.columns for k in ['Competition','Squad']):
    merge_keys = ['Competition','Squad']
else:
    merge_keys = ['Squad']

# Prepara df de salarios con solo las columnas necesarias (y sin duplicados)
cols_keep = [c for c in merge_keys + [weekly_col, annual_col] if c in df_salaries.columns]
sal = df_salaries[cols_keep].copy()

# Si por cualquier motivo hubiera duplicados por clave, nos quedamos con la primera
sal = sal.drop_duplicates(subset=merge_keys, keep='first')

# Merge LEFT: conserva todo de all_teams_stats y añade los salarios
df_all_teams_stats = df_all_teams_stats.merge(sal, on=merge_keys, how='left')
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)

out_path = data_dir / "join_teams_salaries.csv"
df_all_teams_stats.to_csv(out_path, index=False, encoding="utf-8")
