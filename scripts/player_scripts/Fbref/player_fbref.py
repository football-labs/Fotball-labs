from bs4 import BeautifulSoup
import pandas as pd
from cloudscraper import CloudScraper
import re
import time
import random
import os

def fetch_data(url, league_id, league_name, url_add_str):
    headers = {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Thu, 24 Oct 2024 09:58:04 GMT',
        'priority': 'u=0, i',
        'referer': f'https://fbref.com/en/comps/{league_id}/{url_add_str}{league_name}-Stats',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    scraper = CloudScraper.create_scraper()

    response = scraper.get(
        url=url,
        headers=headers
    )

    if league_id == "Big5":
        soup = BeautifulSoup(response.content, 'html.parser')

        header_row = []
        for th in soup.select("thead tr:not(.over_header) th"):
            over_header = th.get('data-over-header', '').replace('-', '_').replace(' ', '_')
            current_header = th.get_text(strip=True).replace('-', '_').replace(' ', '_')
            if over_header:
                new_header = f"{over_header.replace(' ', '')}_{current_header}"
            else:
                new_header = current_header
            header_row.append(new_header)

        rows = []
        for row in soup.select("tbody tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            rows.append(cells)

        if len(header_row) > len(rows[0]):
            header_row.pop(0)

        df = pd.DataFrame(rows, columns=header_row)

    else:
        soup = BeautifulSoup(re.sub("<!--|-->", "", response.text), 'html.parser')

        # Trouver toutes les tables sur la page / Find all tables on the page / Encuentra todas las tablas en la página
        tables = soup.find_all("div", class_="table_container")

        # Choisir la 2nd table / Select the second table / Selecciona la segunda tabla.
        if len(tables) < 2:
            raise ValueError("Second table not found on the page!")

        target_table = tables[2]

        header_row = []
        for th in target_table.select("thead tr:not(.over_header) th"):
            over_header = th.get('data-over-header', '').replace('-', '_').replace(' ', '_')
            current_header = th.get_text(strip=True).replace('-', '_').replace(' ', '_')
            if over_header:
                new_header = f"{over_header.replace(' ', '')}_{current_header}"
            else:
                new_header = current_header
            header_row.append(new_header)

        rows = []
        for row in target_table.select("tbody tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            if len(cells) == 0:
                continue
            rows.append(cells)

        # Faire correspondre les longueurs d'en-tête et de ligne / Match header and row lengths / Hacer coincidir las longitudes de los encabezados y las filas
        if rows and len(header_row) != len(rows[0]):
            print(f"Header columns: {len(header_row)}, First row cells: {len(rows[0])}")
            min_len = min(len(header_row), len(rows[0]))
            header_row = header_row[:min_len]
            rows = [r[:min_len] for r in rows]

        df = pd.DataFrame(rows, columns=header_row)

    df.dropna(how='all', inplace=True)

    # Modifier les colonnes « Nation » et « Comp » / Edit 'Nation' and 'Comp' columns / Editar las columnas «Nación» y «Comp».
    df = extract_uppercase(df)

    # Enlever la colonne 'Matches' + Remove 'Matches' column / Eliminar la columna «Matches»
    df = df.drop(columns=['Matches'])

    # Extraire l'âge dans le bon format / Extract only age from format '23-190' / Extraer solo la edad del formato «23-190».
    df['Age'] = df['Age'].str.split('-', expand=True)[0]

    print(f"Done! -> URL: {url}")

    return df

# Cette fonction convertit les données des colonnes « Nation » et « Comp » dans un nouveau format / This function converts the data of columns 'Nation' and 'Comp' into a new form / Esta función convierte los datos de las columnas «Nation» y «Comp» a un nuevo formato.
def extract_uppercase(df):
    # Extraire la partie en majuscules de la colonne « Nation » / Extract the part in uppercase from 'Nation' column / Extraiga la parte en mayúsculas de la columna «Nation»
    if 'Nation' in df.columns:
        df['Nation'] = df['Nation'].str.extract(r'([A-Z]+)')[0]

    # Extraire la partie commençant par une majuscule dans la colonne « Comp » / Extract the part starting with uppercase in 'Comp' column / Extraiga la parte que comienza con mayúscula en la columna «Comp».
    if 'Comp' in df.columns:
        df['Comp'] = df['Comp'].str.extract(r'([A-Z][a-zA-Z\s]*)')[0]

    return df

# Championnats / Leagues / Ligas
leagues = {
    "Big5": "Big-5-European-Leagues",
    "23": "Eredivisie",
    "32": "Primeira-Liga",
    "37": "Belgian-Pro-League",
    "18": "Serie-B",
    "31": "Liga-MX",
    "22": "Major-League-Soccer",
    "10": "Championship",
    "24": "Brasileirao",
    "21": "Liga-Profesional-Argentina"
}

all_dfs = []

for league_id, league_name in leagues.items():
    if league_id == "Big5":
        url_add_str = "players/"
    else:
        url_add_str = ""

    urls = [
        f'https://fbref.com/en/comps/{league_id}/stats/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/shooting/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/passing/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/passing_types/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/gca/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/defense/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/possession/{url_add_str}{league_name}-Stats',
        f'https://fbref.com/en/comps/{league_id}/misc/{url_add_str}{league_name}-Stats'
    ]

    dfs = []
    for url in urls:
        success = False
        tries = 0
        while not success and tries < 3:
            try:
                df = fetch_data(url, league_id, league_name, url_add_str)
                if not df.empty:
                    dfs.append(df)
                success = True
                time.sleep(random.uniform(3, 6))
            except Exception as e:
                print(f"Error for {url}: {e}. Retrying...")
                time.sleep(random.uniform(3, 6))
                tries += 1

    if dfs:
        df_merged = pd.concat(dfs, axis=1)
        df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]
        if league_id != "Big5":
            df_merged = df_merged.drop_duplicates(subset=["Rk", "Player"], keep=False)
            df_merged = df_merged.drop("Rk", axis=1, errors='ignore')
            df_merged["Comp"] = league_name
        all_dfs.append(df_merged)
        print(f"Done! -> {league_name}")

# Fusionner tous les DF / Merge all DFs / Combinar todos los DF
final_df = pd.concat(all_dfs, axis=0)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(root_dir, 'data', 'player')
os.makedirs(output_dir, exist_ok=True)
final_df.to_csv(os.path.join(output_dir, 'all_leagues_stats.csv'), index=False)
