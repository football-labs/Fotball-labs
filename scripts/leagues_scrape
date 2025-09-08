# Combina tablas de equipos (squads) por liga desde FBref en un único CSV local:
# Salida: data/grouped_stats.csv  (carpeta 'data' fuera del directorio actual del script)

from bs4 import BeautifulSoup
import pandas as pd
from cloudscraper import CloudScraper
import re, time, random
from requests import HTTPError
from pathlib import Path  # <- NUEVO

BASE_URL = "https://fbref.com"

# Secciones (contenedores) presentes en cada página de liga (una sola página por liga)
SECTION_IDS = {
    "all_stats_squads_standard":   "std",
    "all_stats_squads_possession": "poss",
    "all_stats_squads_keeper":     "keeper",
    "all_stats_squads_playing_time":"ptime",
    "all_stats_squads_shooting":   "shoot",
    "all_stats_squads_misc":       "misc",
    "all_stats_squads_passing":    "pass",
    "all_stats_squads_gca":        "gca",
    "all_stats_squads_defense":    "def",
}

# Expansión de Big5 a sus 5 ligas (IDs FBref habituales)
BIG5_SUBLEAGUES = {
    "9":  "Premier-League",
    "12": "La-Liga",
    "20": "Bundesliga",
    "11": "Serie-A",
    "13": "Ligue-1",
}

# Resto de ligas (puedes ampliar/ajustar)
LEAGUES = {
    "23": "Eredivisie",
    "32": "Primeira-Liga",
    "37": "Belgian-Pro-League",
    "18": "Serie-B",
    "31": "Liga-MX",
    "22": "Major-League-Soccer",
    "10": "Championship",
    "24": "Brasileirao",
    "21": "Liga-Profesional-Argentina",
    "9":  "Premier-League",  # también incluimos Premier fuera de Big5 si quieres
}

def polite_sleep(a=4.0, b=8.0):
    time.sleep(random.uniform(a, b))

def get_soup(url: str, referer: str | None = None, retries: int = 5) -> BeautifulSoup:
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "referer": referer or BASE_URL,
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
    }
    scraper = CloudScraper.create_scraper()
    backoff = 2.0
    for attempt in range(retries):
        try:
            resp = scraper.get(url, headers=headers)
            resp.raise_for_status()
            uncommented = re.sub(r"<!--|-->", "", resp.text)
            return BeautifulSoup(uncommented, "html.parser")
        except HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status == 429 and attempt < retries - 1:
                wait = backoff + random.uniform(0, 1.5)
                print(f"429 Too Many Requests. Esperando {wait:.1f}s (reintento {attempt+1}/{retries})...")
                time.sleep(wait)
                backoff *= 1.8
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 1.6
                continue
            raise

def build_headers(table) -> list:
    headers = []
    for th in table.select("thead tr:not(.over_header) th"):
        over = (th.get("data-over-header") or "").strip().replace("-", "_").replace(" ", "_")
        cur = th.get_text(strip=True).replace("-", "_").replace(" ", "_")
        headers.append(f"{over}_{cur}" if over else cur)
    return headers

def _finalize_df(df: pd.DataFrame, suffix: str | None) -> pd.DataFrame:
    # copia para evitar SettingWithCopyWarning
    df = df.copy(deep=True)

    # limpieza básica
    df.dropna(how="all", inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]

    # normalizar claves: queremos SIEMPRE 'Squad' (equipo). Si viene como Team/Club o '..._Squad' lo renombramos.
    if "Squad" not in df.columns:
        candidates = [c for c in df.columns if c.endswith("_Squad")] + [c for c in df.columns if c in ("Team", "Club")]
        if candidates:
            df = df.rename(columns={candidates[0]: "Squad"})
        else:
            # si no hay Squad, esta tabla no es de equipos y no nos sirve
            raise ValueError(f"No se encontró columna 'Squad' (equipo). Columnas: {list(df.columns)}")

    # unificar 'Comp' -> 'Competition' si aparece
    if "Competition" not in df.columns and "Comp" in df.columns:
        df = df.rename(columns={"Comp": "Competition"})

    # columnas ruidosas
    df.drop(columns=[c for c in ("Rk", "Matches") if c in df.columns], inplace=True, errors="ignore")

    # sufijo para evitar colisiones entre secciones (dejamos claves sin sufijo)
    if suffix:
        rename_map = {c: f"{c}__{suffix}" for c in df.columns if c not in ("Competition", "Squad")}
        if rename_map:
            df = df.rename(columns=rename_map)

    return df

def _convert_numeric_best_effort(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(deep=True)
    for c in df.columns:
        if c in ("Competition", "Squad"):
            continue
        if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]):
            cleaned = df[c].astype(str).str.replace(",", "", regex=False)
            conv = pd.to_numeric(cleaned, errors="coerce")
            if conv.notna().any():
                df[c] = conv
    return df

def parse_table_from_container(soup: BeautifulSoup, container_id: str, col_suffix: str | None = None) -> pd.DataFrame:
    container = soup.find("div", id=container_id)
    if container is None:
        raise ValueError(f"No se encontró el contenedor '{container_id}'.")
    table = container.find("table")
    if table is None:
        raise ValueError(f"Sin tabla dentro de '{container_id}'.")
    headers = build_headers(table)

    rows = []
    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if not cells or all(c == "" for c in cells):
            continue
        rows.append(cells)

    if rows:
        m = min(len(headers), len(rows[0]))
        headers = headers[:m]
        rows = [r[:m] for r in rows]

    df = pd.DataFrame(rows, columns=headers)
    return _finalize_df(df, col_suffix)

def merge_on_keys(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    # Merge siempre por Competition + Squad (ambas deben existir)
    for k in ("Competition", "Squad"):
        if k not in left.columns or k not in right.columns:
            raise ValueError(f"Falta clave '{k}' en el merge.")
    return left.merge(right, on=["Competition", "Squad"], how="outer")

def fetch_league_squads_page(league_id: str, league_slug: str) -> pd.DataFrame | None:
    page_url = f"{BASE_URL}/en/comps/{league_id}/{league_slug}-Stats"
    try:
        soup = get_soup(page_url, referer=BASE_URL + "/en/")
    except Exception as e:
        print(f"[{league_slug}] error al obtener la página: {e}")
        return None

    merged = None
    found = 0
    for container_id, suffix in SECTION_IDS.items():
        try:
            df_sec = parse_table_from_container(soup, container_id, col_suffix=suffix)
            # Asegurar columna 'Competition' con el nombre humano de la liga
            if "Competition" not in df_sec.columns:
                df_sec.insert(0, "Competition", league_slug.replace("-", " "))
            else:
                # normalizar valor si viene distinto
                if df_sec["Competition"].nunique() == 1 and df_sec["Competition"].iloc[0] in ("", None):
                    df_sec["Competition"] = league_slug.replace("-", " ")
            # merge
            merged = df_sec if merged is None else merge_on_keys(merged, df_sec)
            found += 1
        except Exception as e:
            print(f"[{league_slug}] faltante/problema en {container_id}: {e}")

    if not found or merged is None:
        print(f"[{league_slug}] no se encontraron secciones de squads.")
        return None

    merged = _convert_numeric_best_effort(merged)
    return merged

def main():
    all_dfs = []

    # ---- BIG5 como equipos: expandimos a sus 5 ligas ----
    print("Big5 -> expandiendo a: Premier, La Liga, Bundesliga, Serie A, Ligue 1")
    for lid, lslug in BIG5_SUBLEAGUES.items():
        print(f"Fetching: {lslug} (id={lid}) [Big5]")
        df = fetch_league_squads_page(lid, lslug)
        if df is not None and not df.empty:
            all_dfs.append(df)
        polite_sleep(6.0, 10.0)

    # ---- Resto de ligas ----
    for lid, lslug in LEAGUES.items():
        # Evitar duplicar Premier si ya te vale con la del bloque Big5
        if lid in BIG5_SUBLEAGUES:
            continue
        print(f"Fetching: {lslug} (id={lid})")
        df = fetch_league_squads_page(lid, lslug)
        if df is not None and not df.empty:
            all_dfs.append(df)
        polite_sleep(6.0, 10.0)

    if not all_dfs:
        print("No se recopiló información de ligas.")
        return

    final_df = pd.concat(all_dfs, axis=0, ignore_index=True)
    final_df = final_df.loc[:, ~final_df.columns.duplicated()]

    # ----- NUEVO: guardar fuera del directorio del script, en ../data/grouped_stats.csv -----
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    out_path = data_dir / "grouped_stats.csv"
    final_df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Guardado: {out_path} | Filas: {len(final_df)} | Columnas: {len(final_df.columns)}")

if __name__ == "__main__":
    main()
