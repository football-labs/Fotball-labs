# Import libraries
import pandas as pd
from unidecode import unidecode
from pathlib import Path
import json

# Paths
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
mapping_path = data_dir / "mapping.json"
out_path = data_dir / "fbref_analyst_joined.csv"

# Load CSV files
fbref = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/join_teams_salaries.csv'
)
opta = pd.read_csv(
    'https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/teams_stats.csv'
)

# Filter Big5 leagues
big5 = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
df_big5 = fbref[fbref['Competition'].isin(big5)]

# Normalize team names (remove accents, lowercase)
def normalize_name(x):
    return unidecode(str(x)).strip().lower()

df_big5["Squad_clean"] = df_big5["Squad"].apply(normalize_name)
opta["team_code_clean"] = opta["team_code"].apply(normalize_name)

# Load mapping from JSON (normalized lowercase keys/values)
with open(mapping_path, "r", encoding="utf-8") as f:
    mapping = json.load(f)

# Apply mapping to normalized names in opta
opta["team_code_clean"] = opta["team_code_clean"].replace(mapping)

# Merge using normalized columns
opta_merged = opta.merge(
    df_big5[["Squad_clean", "% Estimated", "Annual Wages", "Weekly Wages"]],
    left_on="team_code_clean",
    right_on="Squad_clean",
    how="left"
)

# Drop helper columns
opta_merged = opta_merged.drop(columns=["Squad_clean", "team_code_clean"])

# Save the final merged CSV
opta_merged.to_csv(out_path, index=False, encoding="utf-8")
