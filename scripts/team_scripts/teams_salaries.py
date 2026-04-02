import pandas as pd
import re
import unidecode
from pathlib import Path

# List of salary links / Liste des salaires / Lista de enlaces de salarios
links = ['https://fbref.com/en/comps/Big5/wages/Big-5-European-Leagues-Wages']

def extract_euro_value(val):
    """Extract the numerical value in euros from a string with the format “€ 123,456 (x)”. / Extrait la valeur numérique en euros d'une chaîne au format « € 123,456 (x) ». / Extrae el valor numérico en euros desde una cadena con formato '€ 123,456 (x)'."""
    if isinstance(val, str):
        match = re.search(r'€\s?([\d,]+)', val)
        if match:
            return int(match.group(1).replace(',', ''))
    return None

def process_wage_table(url):
    """Read and clear the salary table from a FBref link. / Lis et nettoie le tableau des salaires à partir d'un lien FBref. / Lee y limpia la tabla de salarios desde un enlace de FBref."""
    try:
        df = pd.read_html(url)[0]
        if 'Weekly Wages' in df.columns:
            df['Weekly Wages'] = df['Weekly Wages'].apply(extract_euro_value)
        if 'Annual Wages' in df.columns:
            df['Annual Wages'] = df['Annual Wages'].apply(extract_euro_value)
        if 'Squad' in df.columns:
            df['Squad'] = df['Squad'].apply(lambda x: unidecode.unidecode(str(x)) if pd.notnull(x) else x)
        return df
    except Exception as e:
        print(f"Error procesando {url}: {e}")
        return None

# We process all links and discard empty results. / Nous traitons tous les liens et rejetons les résultats vides. / Procesamos todos los enlaces y descartamos resultados vacíos
dfs = [process_wage_table(url) for url in links]
dfs = [df for df in dfs if df is not None and not df.empty]

if dfs:
    df_final = pd.concat(dfs, ignore_index=True)

    # Save output CSV / Enregistrer le CSV de sortie / Guardar el CSV de salida
    script_dir  = Path(__file__).resolve().parents[2]
    data_dir  = script_dir / "data"
    team_dir  = data_dir / "team"
    out_path = team_dir / "teams_salaries.csv"

    df_final.to_csv(out_path, index=False)
    print(f"Guardado: {out_path} | Filas: {len(df_final)} | Columnas: {df_final.shape[1]}")
    try:
        from IPython.display import display
        display(df_final.head())
    except:
        pass
else:
    print("No se obtuvieron tablas válidas.")
