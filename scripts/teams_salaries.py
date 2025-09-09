import pandas as pd
import re
import unidecode  # si no lo tienes: !pip install Unidecode
from pathlib import Path

# Lista de enlaces de salarios
links = ['https://fbref.com/en/comps/Big5/wages/Big-5-European-Leagues-Wages']

def extract_euro_value(val):
    """Extrae el valor numérico en euros desde una cadena con formato '€ 123,456 (x)'."""
    if isinstance(val, str):
        match = re.search(r'€\s?([\d,]+)', val)
        if match:
            return int(match.group(1).replace(',', ''))
    return None

def process_wage_table(url):
    """Lee y limpia la tabla de salarios desde un enlace de FBref."""
    try:
        df = pd.read_html(url)[0]  # igual que lo tenías
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

# Procesamos todos los enlaces y descartamos resultados vacíos
dfs = [process_wage_table(url) for url in links]
dfs = [df for df in dfs if df is not None and not df.empty]

if dfs:
    df_final = pd.concat(dfs, ignore_index=True)

    # Guardar en carpeta data/
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / "teams_salaries.csv"

    df_final.to_csv(out_path, index=False)
    print(f"Guardado: {out_path} | Filas: {len(df_final)} | Columnas: {df_final.shape[1]}")
    try:
        from IPython.display import display
        display(df_final.head())
    except:
        pass
else:
    print("No se obtuvieron tablas válidas.")
