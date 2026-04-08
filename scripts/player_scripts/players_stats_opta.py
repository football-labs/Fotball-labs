# Import des libraries / Importing librairies / Importación de bibliotecas
import re
import time
from typing import Tuple, List, Dict, Any
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from urllib.parse import urlparse
import pandas as pd
from pprint import pprint
from pathlib import Path
import os

# On accéde au chemin de la racine du projet / We access the path of the project root / Accedemos a la ruta de la raíz del proyecto
ROOT_DIR  = Path(__file__).resolve().parents[2]
DATA_DIR  = ROOT_DIR / "data"
PLAYER_DIR  = DATA_DIR / "player"


# On stocke le lien url vers opta analyst / We store the url to opta analyst / Almacenamos el url a opta analyst
BASE_ANALYST_URL = "https://theanalyst.com"
PLAYER_INFO_CSV = PLAYER_DIR / "player_info.csv"
SEASON_CSV  = PLAYER_DIR / "season.csv"
SEASON_COLS = ["country", "championship_name", "season_name", "id_season", "link_url_opta", "link_url_whoscored"]

## Partie servant pour le scraping des données / Part used for data scraping / Parte utilizada para el scraping de datos

# Fermeture de la page des cookies / Closing the cookies page / Cierre de la página de cookies
def handle_cookies(driver, accept: bool = True, timeout: int = 2) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    btn_id = "onetrust-accept-btn-handler" if accept else "onetrust-reject-all-handler"
    banner_sel = "div.ot-sdk-container[role='dialog'],#onetrust-banner-sdk,#onetrust-consent-sdk,#onetrust-button-group-parent"
    fallback_xp = ("//button[normalize-space()='I Accept' or contains(.,'Accept')]" if accept
                   else "//button[normalize-space()='Reject All' or contains(.,'Reject')]")

    # Recherche d'une bannière de cookie visible / Search for a visible cookie banner / Buscar una banniera de cookie visible
    def banner_visible(drv):
        try:
            return any(el.is_displayed() for el in drv.find_elements(By.CSS_SELECTOR, banner_sel))
        except Exception:
            return False

    if not banner_visible(driver):
        return True
    
    # Si la bannière de cookie est visible, on cherche à fermer cette page / If the cookie banner is visible, we search to close this page / Si la bannière de cookie est visible, on cherche à fermer cette page
    frames = [None] + driver.find_elements(By.CSS_SELECTOR, "iframe,frame")
    clicked = False
    for fr in frames:
        try:
            if fr:
                driver.switch_to.frame(fr)
            btns = driver.find_elements(By.ID, btn_id) or driver.find_elements(By.XPATH, fallback_xp)
            if btns:
                try:
                    btns[0].click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", btns[0])
                clicked = True
                break
        except Exception:
            continue
        finally:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

    # Attendre la disparition de la bannière / Wait for the banner to disappear / Esperar a que la banniera desaparezca
    try:
        WebDriverWait(driver, timeout).until(lambda d: not banner_visible(d))
    except TimeoutException:
        pass

    return not banner_visible(driver) or clicked

# Fonction permettant de cliquer sur le toggle 'per 90' / Function to click on the toggle 'per 90' / Función para clicar en el toggle 'per 90'
def enable_per_match(driver, timeout: int = 5) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        wrapper = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'MiniToggle')][.//div[contains(@class,'MiniToggle') and normalize-space()='per 90']]"
            ))
        )
    except TimeoutException:
        #print("Toggle 'per 90' introuvable ❌")
        return False

    # Recherche du toggle 'per 90' / Search for the toggle 'per 90' / Buscar el toggle 'per 90'
    def _find_cb_and_label():
        cb = wrapper.find_element(By.XPATH, ".//label[contains(@class,'MiniToggle')]/input[@type='checkbox']")
        lab = wrapper.find_element(By.XPATH, ".//label[contains(@class,'MiniToggle')]")
        return cb, lab

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrapper)
    cb, lab = _find_cb_and_label()

    # Si on trouve le toggle 'per 90', on cherche à l'activer / If we find the toggle 'per 90', we search to activate it / Si encontramos el toggle 'per 90', buscamos a activarlo
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//label[contains(@class,'MiniToggle')]")))
        try:
            lab.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", lab)
    except Exception:
        driver.execute_script("arguments[0].click();", lab)

    # On vérifie que le toggle 'per 90' est bien activé / We check that the toggle 'per 90' is well activated / Verificamos que el toggle 'per 90' est bien activado
    try:
        WebDriverWait(driver, 4).until(lambda d: _find_cb_and_label()[0].is_selected())
        #print("Mode 'per 90' activé ✅")
        return True
    except TimeoutException:
         #print("Impossible d'activer 'per 90' ❌")
        return False

# Fonction permettant d'ouvrir le filtre joueurs et de mettre mins played à 100 / Function to open the players filter and set mins played to 100 / Función para abrir el filtro de jugadores y establecer mins played a 100
def set_players_filter_min(driver, timeout: int = 8) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)

    try:
        # Cliquer sur le bouton "Filter Players" / We click on the button "Filter Players" / Hacemos clic en el botón "Filter Players"
        filter_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(@class,'StatsPage-module_filter-btn') and contains(., 'Filter Players')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", filter_btn)
        try:
            filter_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", filter_btn)

        # Attendre l'ouverture du drawer / Wait for the drawer to open / Esperar a que se abra el drawer
        drawer = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.StatsPage-module_filter-drawer__gTO-e"
            ))
        )

        # Récupérer le slider minimum / Retrieve the minimum slider / Recuperar el slider mínimo
        min_slider = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "input.RangeSlider-module_min__iSMBM[type='range']"
            ))
        )

        current_value = min_slider.get_attribute("value")
        if current_value == "100":
            #print("Filtre joueurs déjà réglé à 90 minute ✅")
            return True

        # On met le filtre à 100 / We set the filter to 100 / Establecemos el filtro a 100
        driver.execute_script("""
            const slider = arguments[0];
            const value = arguments[1];

            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, "value"
            ).set;

            nativeInputValueSetter.call(slider, value);
            slider.dispatchEvent(new Event('input', { bubbles: true }));
            slider.dispatchEvent(new Event('change', { bubbles: true }));
        """, min_slider, "100")

        # Attendre que le label se mette à jour / Wait for the label to be updated / Esperar a que el label se actualice
        wait.until(lambda d: any(
            "mins played: 100 -" in (el.text or "").lower()
            for el in d.find_elements(By.CSS_SELECTOR, "span.RangeSlider-module_label__0Q93A")
        ))

        #print("Filtre joueurs réglé à 100 minutes ✅")
        return True

    except TimeoutException:
        #print("Impossible d'ouvrir ou de régler le filtre joueurs à 0 ❌")
        return False
    except Exception as e:
        #print(f"Erreur lors du réglage du filtre joueurs : {e}")
        return False

# Fonction permettant d'accéder au tableau des différentes pages d'Opta Analyst / Function to access the table of the different pages of Opta Analyst / Función para acceder al tabla de las diferentes páginas de Opta Analyst
def _get_tbody_html(driver) -> str:
    # Recherche de la partie du code reservée à l'affichage du tableau par équipe / Search for the part of the code reserved for the display of the table by player / Buscar la parte del código reservada para el display del tabla por equipo
    try:
        el = driver.find_element(By.CSS_SELECTOR, "table.Table-module_data-table__giW24 tbody")
        return el.get_attribute("innerHTML") or ""
    except Exception:
        try:
            el = driver.find_element(By.CSS_SELECTOR, "table[class*='Table-module_data-table'] tbody")
            return el.get_attribute("innerHTML") or ""
        except Exception:
            return ""

# Fonction permettant de cliquer sur les options (Overall, Set-pieces...) dans le cas où elles sont disponibles (Attacking/Defending) / Function to click on the options (Overall, Set-pieces...) in the case where they are available (Attacking/Defending) / Función para clicar en las opciones (Overall, Set-pieces...) en el caso de que estén disponibles (Attacking/Defending)
def click_coin(driver, label: str, timeout: int = 6) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    # Recherche si des options sont disponibles / Search for options that are available / Buscar si hay opciones disponibles
    try:
        coins_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.StatsPage-module_toggles__NkN06 div.StatsPage-module_coins__-LT4a")
            )
        )
    except TimeoutException:
        #print("Conteneur des 'coins' introuvable ❌")
        return False

    xp = (
        ".//button[contains(@class,'Button-module_button-coin') and "
        "contains(translate(normalize-space(.),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), %s)]"
    )
    target_text = label.strip().upper()

    try:
        btn = coins_container.find_element(By.XPATH, xp % repr(target_text))
    except Exception:
        #print(f"Bouton coin '{label}' introuvable ❌")
        return False

    # Si les options sont disponibles, on essaye de cliquer sur celui que l'on souhaite / If the options are available, we try to click on the one we want / Si las opciones están disponibles, intentamos clicar en el que queremos
    cls = btn.get_attribute("class") or ""
    if "button-coin-active" in cls:
        return True

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    try:
        btn.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", btn)
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", btn)
        except Exception:
            pass

    # Vérification si l'option est bien activé / We check that the option is well activated / Verificamos que la opción está bien activada
    try:
        wait.until(lambda d: "button-coin-active" in btn.get_attribute("class"))
        return True
    except TimeoutException:
        print(f"Le coin '{label}' ne s'est pas activé ❌")
        return False

# Fonction permettant de récupérer les données des tableaux ayant uniquement un tableau principal, sans options / Function to retrieve the data of the tables having only a main table, without options / Función para recuperar los datos de las tablas que tienen solo una tabla principal, sin opciones
def click_category_select(driver, target_label: str, from_label: str = None, timeout: int = 8) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)

    # Recherche du nom du tableau actuel (Defending, Pressing...) / Search for the name of the current table (Defending, Pressing...) / Buscar el nombre de la tabla actual (Defending, Pressing...)
    controls = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.react-select__control")))
    control = None
    if from_label:
        from_up = from_label.strip().upper()
        for c in controls:
            try:
                sv = c.find_element(By.CSS_SELECTOR, "div.react-select__single-value")
                if (sv.text or "").strip().upper() == from_up:
                    control = c
                    break
            except Exception:
                continue
    if control is None:
        control = controls[0]  # fallback: premier contrôle / fallback: primer control / fallback: primer control

    # On clique sur la barre déroulante afin d'accéder au tableau de notre choix / We click on the dropdown to access the table of our choice / Hacemos clic en la barra desplegable para acceder a la tabla de nuestro elección
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", control)
    try:
        control.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", control)

    # Attente que le barre déroulante s'affiche et cliquer sur le tableau de notre choix / Wait for the dropdown to display and click on the table of our choice / Esperar a que la barra desplegable se muestre y hacer clic en la tabla de nuestro elección
    menu = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.react-select__menu")))
    xpath_opt = (
        ".//*[contains(@class,'react-select__option') and "
        "translate(normalize-space(.),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ') = %s]"
    )
    opt = menu.find_element(By.XPATH, xpath_opt % repr(target_label.strip().upper()))
    try:
        opt.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", opt)

    # Vérification que le nom du tableau s'est bien actualisée / We check that the name of the table has been well updated / Verificamos que el nombre de la tabla se ha actualizado bien
    wait.until(lambda d: any(
        (el.text or "").strip().upper() == target_label.strip().upper()
        for el in d.find_elements(By.CSS_SELECTOR, "div.react-select__single-value")
    ))
    return True

# Fonction pour scraper uniquement la page courante du tableau / Function to scrape only the current page of the table / Función para scrapear solo la página actual de la tabla
def scrape_table_page(driver, timeout: int = 6, section: str = "OVERALL"):
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        _ = wait.until(EC.presence_of_element_located((
            By.XPATH, "(//table[contains(@class,'Table-module_data-table')])[1]"
        )))
    except TimeoutException:
        raise RuntimeError("Premier tableau introuvable.")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.select_one("table.Table-module_data-table__giW24") or \
            soup.select_one("table[class*='Table-module_data-table']")
    if table is None:
        raise RuntimeError("Premier tableau introuvable (fallback).")

    def norm(s: str) -> str:
        s = (s or "").strip().lower()
        mapping = {
            # Attacking
            "conv %": "conv_pct", "goals vs xg": "goals_vs_xg", "xg per shot": "xg_per_shot", "shot %": "shot_pct",

            # Passing
            "%": "pct", "through balls": "through_balls", "open play passes": "open_play_passes",
            "in final third": "in_final_third", "assists": "assists", "chances created": "chances_created", "xa": "xa",

            # Defending
            "pos won": "pos_won", "ints": "interceptions", "ground duels": "ground_duels", "aerial duels": "aerial_duels",

            # Carrying
            "all carries": "all_carries", "progressive": "progressive", "ended with": "ended_with",
            "distance (m)": "distance_(m)", "avg (m)": "avg_(m)",

            # Goalkeeping
            "goals conceded": "goals_conceded", "saves made": "saves_made", "save %": "save_pct",
            "xgot conceded": "xgot_conceded", "goals prevented": "goals_prevented", "gp rate": "gp_rate",
        }
        return mapping.get(s, s.replace(" ", "_").replace("-", "_"))

    # Fonction permettant de parser les nombres / Function to parse the numbers / Función para parsear los números
    def parse_num(txt: str):
        txt = (txt or "").strip()
        if not txt:
            return None
        if txt.endswith("%"):
            try:
                return float(txt[:-1])
            except ValueError:
                return None
        try:
            if txt.isdigit() or (txt.startswith("-") and txt[1:].isdigit()):
                return int(txt)
            return float(txt.replace(",", ""))
        except ValueError:
            return None

    thead = table.select_one("thead")
    tbody = table.select_one("tbody")
    if not tbody:
        raise RuntimeError("tbody introuvable.")

    first_tr = tbody.select_one("tr")
    tds_first = first_tr.select("td") if first_tr else []
    if not tds_first:
        return [], []

    n_cols_body = len(tds_first)
    header_labels = [None] * n_cols_body

    # Si le thead existe, on parcourt les lignes et on récupère les cellules / If the thead exists, we loop through the rows and retrieve the cells / Si el thead existe, recorremos las líneas y recuperamos las celdas
    if thead:
        rows = thead.select("tr")
        if rows:
            bottom_cells = rows[-1].select("th")
            top_cells = rows[0].select("th") if len(rows) > 1 else []

            expanded_groups = []
            if top_cells:
                for th in top_cells:
                    grp = th.get_text(strip=True)
                    colspan = int(th.get("colspan", "1"))
                    expanded_groups.extend([norm(grp) if grp else None] * colspan)

                if len(expanded_groups) < len(bottom_cells):
                    expanded_groups += [None] * (len(bottom_cells) - len(expanded_groups))
                elif len(expanded_groups) > len(bottom_cells):
                    expanded_groups = expanded_groups[:len(bottom_cells)]
            else:
                expanded_groups = [None] * len(bottom_cells)

            for col_idx in range(1, n_cols_body):
                leaf = bottom_cells[col_idx].get_text(strip=True) if col_idx < len(bottom_cells) else ""
                leaf_n = norm(leaf)
                grp = expanded_groups[col_idx] if col_idx < len(expanded_groups) else None
                header_labels[col_idx] = f"{grp}__{leaf_n}" if grp else leaf_n

    for i in range(1, n_cols_body):
        if not header_labels[i]:
            header_labels[i] = f"col_{i}"
    
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats_rows, players_rows = [], []
    for tr in tbody.select("tr"):
        tds = tr.select("td")
        if not tds:
            continue

        t0 = tds[0]
        a = t0.select_one("a[href]")
        player_href = a["href"] if a else ""

        player_id = None
        player_code = None

        if player_href:
            m = re.search(r"/player/sc-(\d+)/([^/?#]+)", player_href)
            if m:
                try:
                    player_id = int(m.group(1))
                except Exception:
                    player_id = None
                player_code = m.group(2).replace("-", " ")

        if not player_code:
            player_code = a.get_text(strip=True) if a else t0.get_text(strip=True)

        # On ajoute les données au tableau des joueurs / We add the data to the players table / Añadimos los datos a la tabla de jugadores
        players_rows.append({"player_id": player_id,"player_code": player_code,"player_href": player_href})

        row_vals: Dict[str, Any] = {}
        for i, td in enumerate(tds[1:], start=1):
            key = header_labels[i]
            txt = td.get_text(strip=True)
            row_vals[key] = parse_num(txt)

        row_vals.update({"player_id": player_id,"player_code": player_code,"player_href": player_href,"section": section})
        stats_rows.append(row_vals)

    return stats_rows, players_rows

# Lire la pagination courante : "1 of 11" / Read the current pagination : "1 of 11" / Leer la paginación actual : "1 de 11"
def get_table_pagination_info(driver, timeout: int = 5):
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        container = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.TablePagination-module_pagination-container__yN7kR"
            ))
        )
        span = container.find_element(By.TAG_NAME, "span")
        txt = (span.text or "").strip()

        m = re.search(r"(\d+)\s+of\s+(\d+)", txt, flags=re.IGNORECASE)
        if not m:
            return 1, 1

        current_page = int(m.group(1))
        total_pages = int(m.group(2))
        return current_page, total_pages

    except Exception:
        return 1, 1

# Cliquer sur la page suivante / Click on the next page / Hacer clic en la página siguiente
def go_to_next_table_page(driver, current_page: int, timeout: int = 8) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)

    try:
        container = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.TablePagination-module_pagination-container__yN7kR"
            ))
        )

        buttons = container.find_elements(By.TAG_NAME, "button")
        if len(buttons) < 2:
            #print("Boutons de pagination introuvables ❌")
            return False

        next_btn = buttons[1]  # le bouton '>'

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)

        old_page = current_page

        try:
            next_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", next_btn)

        wait.until(lambda d: get_table_pagination_info(d, timeout=2)[0] > old_page)
        return True

    except TimeoutException:
        #print("Impossible de passer à la page suivante ❌")
        return False
    except Exception as e:
        print(f"Erreur pagination page suivante : {e}")
        return False

# Fonction pour revenir à la première page du tableau / Function to return to the first page of the table / Función para volver a la primera página de la tabla
def reset_table_to_first_page(driver, timeout: int = 8, max_back_clicks: int = 100) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)

    try:
        # Attendre que la pagination soit visible
        container = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.TablePagination-module_pagination-container__yN7kR"
            ))
        )

        for _ in range(max_back_clicks):
            current_page, total_pages = get_table_pagination_info(driver, timeout=2)

            # Déjà sur la première page / Already on the first page / Ya estamos en la primera página
            if current_page <= 1:
                return True

            old_tbody_html = _get_tbody_html(driver)

            # Boutons pagination : [<, >] / Pagination buttons : [<, >] / Botones de paginación : [<, >]
            buttons = container.find_elements(By.TAG_NAME, "button")
            if len(buttons) < 2:
                #print("Boutons de pagination introuvables ❌")
                return False

            prev_btn = buttons[0]  # bouton "<"
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", prev_btn)

            try:
                prev_btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", prev_btn)

            # Attendre que la page diminue ou que le tableau change / Wait for the page to decrease or the table to change / Esperar a que la página disminuya o que la tabla cambie
            wait.until(lambda d: get_table_pagination_info(d, timeout=2)[0] < current_page or _get_tbody_html(d) != old_tbody_html)

            # Reprendre le container car le DOM peut être rerendu / Take back the container because the DOM may be rerendered / Recuperar el container porque el DOM puede ser rerenderizado
            container = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.TablePagination-module_pagination-container__yN7kR"
                ))
            )

        #print("Impossible de revenir à la première page dans la limite autorisée ❌")
        return False

    except TimeoutException:
        #print("Pagination introuvable pour reset à la première page ❌")
        return False
    except Exception as e:
        #print(f"Erreur reset pagination : {e}")
        return False
        
# Fonction pour scraper toutes les pages du tableau / Function to scrape all the pages of the table / Función para scrapear todas las páginas de la tabla
def scrape_table(driver, timeout: int = 6, section: str = "OVERALL"):
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    all_stats_rows = []
    all_players_rows = []

    seen_row_keys = set()
    seen_players = set()

    # Revenir à la page 1 avant de commencer / Return to the first page before starting / Volver a la primera página antes de comenzar
    reset_table_to_first_page(driver, timeout=timeout + 2)

    while True:
        current_page, total_pages = get_table_pagination_info(driver, timeout=timeout)
        #print(f"Scraping page {current_page}/{total_pages} pour la section {section}")

        stats_rows, players_rows = scrape_table_page(driver, timeout=timeout, section=section)

        for row in stats_rows:
            row_key = (row.get("player_id"), row.get("section"))
            if row_key not in seen_row_keys:
                all_stats_rows.append(row)
                seen_row_keys.add(row_key)

        for p in players_rows:
            pid = p.get("player_id")
            if pid not in seen_players:
                all_players_rows.append(p)
                seen_players.add(pid)

        # Si on est sur la dernière page, on arrête / If we are on the last page, we stop / Si estamos en la última página, paramos
        if current_page >= total_pages:
            break
        
        # On va à la page suivante / We go to the next page / Vamos a la página siguiente
        ok = go_to_next_table_page(driver, current_page=current_page, timeout=timeout + 2)
        if not ok:
            #print("Arrêt pagination car impossible d'aller à la page suivante.") / Stop pagination because it is impossible to go to the next page. / Paramos la paginación porque no es posible ir a la página siguiente.
            break

        time.sleep(0.8)

    return all_stats_rows, all_players_rows
               
# Fonction pour extraire les données du tableau spécifique à Attacking / Function to extract the data of the specific table to Attacking / Función para extraer los datos de la tabla específica a Attacking
def extract_attacking(driver, id_season):
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, players = [], []
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # On ferme la page de cookie si cela n'est pas fait / We close the cookie page if it is not done / Cerramos la página de cookie si no se ha hecho
    try:
        handle_cookies(driver)
    except Exception:
        pass
    
    # On met les bons paramètres / We set the good parameters / Establecemos los parámetros correctos
    enable_per_match(driver)
    set_players_filter_min(driver)
    # On scrape les sections de notre choix / We scrape the sections of our choice / Escrapeamos las secciones de nuestro choice
    sections = ["OVERALL", "NON-PENALTY"]
    for sec in sections:
        prev_html = _get_tbody_html(driver)
        if not click_coin(driver, sec):
            #print(f"Impossible d'activer le coin {sec} ❌ — on passe au suivant")
            continue

        # On associe le nom des colonnes avec le nom du tableau 'attacking' / We associate the name of the columns with the name of the table 'attacking' / Asociamos el nombre de las columnas con el nombre de la tabla 'attacking'
        try:
            stats_rows, players_rows = scrape_table(driver, section=f"attacking_{sec}")
            stats.extend(stats_rows)
            # On regarde si on a pas pris les données plusieurs fois pour la même équipe / We check if we have not taken the data several times for the same team / Verificamos si no hemos tomado los datos varias veces para el mismo equipo
            seen = {t.get("player_id") for t in players}
            for t in players_rows:
                if t.get("player_id") not in seen:
                    players.append(t)
                    seen.add(t.get("player_id"))
            #print(f"Tableau '{sec}' récupéré ✅ ({len(stats_rows)} lignes)")
        except Exception as e:
            print(f"Erreur lors du scraping du tableau '{sec}': {e}")

    return stats, players

# Fonction pour extraire les données du tableau spécifique à Passing / Function to extract the data of the specific table to Passing / Función para extraer los datos de la tabla específica a Passing
def extract_passing(driver, from_label: str = "Attacking"):
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, players = [], []
    
    # On clique sur la catégorie Passing / We click on the category Passing / Hacemos clic en la categoría Passing
    if not click_category_select(driver, target_label="Passing", from_label=from_label):
        print("Impossible d'activer la catégorie 'Passing' ❌")
        return stats, players

    # Récupération du driver / Timeout pour laisser le temps de raffraichir la page
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # On ferme la page de cookie si cela n'est pas fait / We close the cookie page if it is not done / Cerramos la página de cookie si no se ha hecho
    try:
        handle_cookies(driver)
    except Exception:
        pass
    
    # On met les bons paramètres / We set the good parameters / Establecemos los parámetros correctos
    set_players_filter_min(driver)
    # On scrape les sections de notre choix / We scrape the sections of our choice / Escrapeamos las secciones de nuestro choice
    sections = ["OVERALL","CHANCE CREATION"]
    for sec in sections:
        prev_html = _get_tbody_html(driver)

        if not click_coin(driver, sec):
            #print(f"Impossible d'activer le coin {sec} ❌ — on passe au suivant")
            continue

        # On associe le nom des colonnes avec le nom du tableau 'passing' / We associate the name of the columns with the name of the table 'passing' / Asociamos el nombre de las columnas con el nombre de la tabla 'passing'
        try:
            stats_rows, players_rows = scrape_table(driver, section=f"passing_{sec}")
            stats.extend(stats_rows)
            # On regarde si on a pas pris les données plusieurs fois pour le même joueur / We check if we have not taken the data several times for the same player / Verificamos si no hemos tomado los datos varias veces para el mismo jugador
            seen = {t.get("player_id") for t in players}
            for t in players_rows:
                if t.get("player_id") not in seen:
                    players.append(t)
                    seen.add(t.get("player_id"))
            print(f"Tableau '{sec}' récupéré ✅ ({len(stats_rows)} lignes)")
        except Exception as e:
            print(f"Erreur lors du scraping du tableau '{sec}': {e}")

    return stats, players

# Fonction pour extraire les données provenant spécifiquement de Defending / Function to extract the data from the specific table to Defending / Función para extraer los datos de la tabla específica a Defending
def extract_defending(driver, from_label: str = "Passing"):
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, players = [], []
    
    # On clique sur la catégorie Defending / We click on the category Defending / Hacemos clic en la categoría Defending
    if not click_category_select(driver, target_label="Defending", from_label=from_label):
        print("Impossible d'activer la catégorie 'Defending' ❌")
        return stats, players

    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # On ferme la page de cookie si cela n'est pas fait / We close the cookie page if it is not done / Cerramos la página de cookie si no se ha hecho
    try:
        handle_cookies(driver)
    except Exception:
        pass

    # On met les bons paramètres / We set the good parameters / Establecemos los parámetros correctos
    set_players_filter_min(driver)
    # On scrape les sections de notre choix / We scrape the sections of our choice / Escrapeamos las secciones de nuestro choice
    sections = ["OVERALL","DISCIPLINE"]
    for sec in sections:
        prev_html = _get_tbody_html(driver)

        if not click_coin(driver, sec):
            #print(f"Impossible d'activer le coin {sec} ❌ — on passe au suivant")
            continue

        # On associe le nom des colonnes avec le nom du tableau 'defending' / We associate the name of the columns with the name of the table 'defending' / Asociamos el nombre de las columnas con el nombre de la tabla 'defending'
        try:
            stats_rows, players_rows = scrape_table(driver, section=f"defending_{sec}")
            stats.extend(stats_rows)
            # On regarde si on a pas pris les données plusieurs fois pour le même joueur / We check if we have not taken the data several times for the same player / Verificamos si no hemos tomado los datos varias veces para el mismo jugador
            seen = {t.get("player_id") for t in players}
            for t in players_rows:
                if t.get("player_id") not in seen:
                    players.append(t)
                    seen.add(t.get("player_id"))
            print(f"Tableau '{sec}' récupéré ✅ ({len(stats_rows)} lignes)")
        except Exception as e:
            print(f"Erreur lors du scraping du tableau '{sec}': {e}")

    return stats, players

# Fonction pour extraire les données ayant un tableau unique : Passing, Pressing... (sans section) / Function to extract the data of a unique table: Passing, Pressing... (without section) / Función para extraer los datos de una tabla única: Passing, Pressing... (sin sección)
def extract_table_for_category(driver, category_label: str = "Carrying", from_label: str = "Defending"):
    # Initialisation des variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, players = [], []

    # On clique pour accéder au tableau de notre choix / We click to access the table of our choice / Hacemos clic para acceder a la tabla de nuestro choice
    if not click_category_select(driver, category_label, from_label=from_label):
        print(f"Impossible d'activer la catégorie '{category_label}' ❌")
        return stats, players

    # Attendre que la page soit bien rechargée / Wait for the page to be well reloaded / Esperar a que la página se haya cargado bien
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Refaire les paramètres d'affichage après changement de catégorie / Refill the display parameters after category change / Refill the display parameters after category change
    try:
        handle_cookies(driver)
    except Exception:
        pass
    
    # On met les bons paramètres / We set the good parameters / Establecemos los parámetros correctos
    set_players_filter_min(driver)

    # Scraping du tableau / Scraping the table / Escrapeando la tabla
    try:
        stats_rows, players_rows = scrape_table(driver, section=category_label.upper())
        stats.extend(stats_rows)

        # On récupère les données en ne prenant pas deux fois les mêmes données d'un même joueur / We retrieve the data without taking the same data twice for the same player / Recuperamos los datos sin tomar los mismos datos dos veces para el mismo jugador
        seen = set(t.get("player_id") for t in players)
        for t in players_rows:
            if t.get("player_id") not in seen:
                players.append(t)
                seen.add(t.get("player_id"))

        print(f"Tableau catégorie '{category_label}' récupéré ✅ ({len(stats_rows)} lignes)")
    except Exception as e:
        print(f"Erreur lors du scraping de la catégorie '{category_label}': {e}")

    return stats, players

# Fonction pour obtenir le lien complet du joueur / Function to get the complete player link / Función para obtener el enlace completo del jugador
def make_full_player_url(player_href: str) -> str:
    player_href = (player_href or "").strip()
    if not player_href:
        return ""
    if player_href.startswith("http://") or player_href.startswith("https://"):
        return player_href
    return f"{BASE_ANALYST_URL}{player_href}"

# Fonction pour récupérer les informations de fiche de joueur / Function to retrieve the player information cache / Función para recuperar la información de la cache de jugador
def read_player_info_cache(path: Path) -> pd.DataFrame:
    expected_cols = ["player_id", "player_href", "dob", "age","current_club", "affiliation", "position"]
    if not path.exists():
        return pd.DataFrame(columns=expected_cols)

    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in expected_cols:
        if c not in df.columns:
            df[c] = ""
    return df[expected_cols]

def upsert_player_info_cache(path: Path, df_new: pd.DataFrame) -> pd.DataFrame:
    return upsert_csv_by_keys(path, df_new, keys=["player_id"])

# Fonction pour récupérer les informations des joueurs / Function to retrieve the player information / Función para recuperar la información de los jugadores
def parse_player_information_from_html(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    card = soup.select_one("div.ctp-player-information")
    info = {"dob": None,"age": None,"current_club": None,"affiliation": None,"position": None}

    if card is None:
        return info

    rows = card.select("div.PlayerInfoCard-module_row__ShTkN")
    for row in rows:
        label_el = row.select_one("div.PlayerInfoCard-module_label__fOCou")
        value_el = row.select_one("div.PlayerInfoCard-module_value__Nkp43")

        if not label_el or not value_el:
            continue

        label = label_el.get_text(strip=True).lower().replace(":", "")
        value = value_el.get_text(" ", strip=True)

        if label == "dob":
            info["dob"] = value
        elif label == "age":
            try:
                info["age"] = int(value)
            except Exception:
                info["age"] = value
        elif label == "current club":
            info["current_club"] = value
        elif label == "affiliation":
            info["affiliation"] = value
        elif label == "position":
            info["position"] = value

    return info

# Fonction pour éviter de scraper 2 fois le même joueur / Function to avoid scraping the same player twice / Función para evitar scrapear al mismo jugador dos veces
def enrich_agg_rows_with_player_info(driver, agg_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Lecture du cache existant / Reading the existing cache / Lectura de la cache existente
    cache_df = read_player_info_cache(PLAYER_INFO_CSV)

    cache_by_id: Dict[str, Dict[str, Any]] = {}
    for _, r in cache_df.iterrows():
        pid = str(r.get("player_id", "")).strip()
        if pid:
            cache_by_id[pid] = {"player_id": pid,"player_href": r.get("player_href", ""),"dob": r.get("dob", ""),
                "age": r.get("age", ""),"current_club": r.get("current_club", ""),
                "affiliation": r.get("affiliation", ""),"position": r.get("position", "")}

    rows_to_scrape = []
    for row in agg_rows:
        pid = row.get("player_id")
        href = row.get("player_href")

        if pid is None:
            continue

        pid_str = str(pid).strip()

        cached = cache_by_id.get(pid_str)
        if cached and any(cached.get(k) for k in ["dob", "age", "current_club", "affiliation", "position"]):
            continue

        rows_to_scrape.append({"player_id": pid,"player_href": href})

    # Scraping seulement des joueurs manquants / Scraping only the missing players / Escrapeando solo los jugadores que faltan
    scraped_rows = []
    total = len(rows_to_scrape)

    for idx, item in enumerate(rows_to_scrape, start=1):
        pid = item["player_id"]
        href = item["player_href"]

        print(f"Scraping fiche joueur {idx}/{total} : {href}")
        info = scrape_player_information(driver, href)

        scraped_rows.append({"player_id": pid,"player_href": href,"dob": info.get("dob"),"age": info.get("age"),
            "current_club": info.get("current_club"),"affiliation": info.get("affiliation"),"position": info.get("position")})

    # Mise à jour du cache disque / Update the disk cache / Actualizar la cache en disco
    if scraped_rows:
        df_new = pd.DataFrame(scraped_rows)
        cache_df = upsert_player_info_cache(PLAYER_INFO_CSV, df_new)

        # reconstruire le dictionnaire cache après update
        cache_by_id = {}
        for _, r in cache_df.iterrows():
            pid = str(r.get("player_id", "")).strip()
            if pid:
                cache_by_id[pid] = {"player_id": pid,"player_href": r.get("player_href", ""),
                    "dob": r.get("dob", ""),"age": r.get("age", ""),"current_club": r.get("current_club", ""),
                    "affiliation": r.get("affiliation", ""),"position": r.get("position", "")}

    # Injection dans agg_rows
    for row in agg_rows:
        pid = row.get("player_id")
        if pid is None:
            continue

        cached = cache_by_id.get(str(pid).strip(), {})
        row["dob"] = cached.get("dob") or None
        row["age"] = cached.get("age") or None
        row["current_club"] = cached.get("current_club") or None
        row["affiliation"] = cached.get("affiliation") or None
        row["position"] = cached.get("position") or None

    return agg_rows

# Fonction pour scraper les informations des joueurs
def scrape_player_information(driver, player_href: str, timeout: int = 8) -> Dict[str, Any]:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice 
    full_url = make_full_player_url(player_href)
    if not full_url:
        return {"dob": None,"age": None,"current_club": None,"affiliation": None,"position": None}
    try:
        driver.get(full_url)
        
        # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
        wait = WebDriverWait(driver, timeout)
        wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.ctp-player-information"
            ))
        )

        return parse_player_information_from_html(driver.page_source)

    except Exception as e:
        #print(f"Erreur scraping fiche joueur {full_url}: {e}")
        return {"dob": None,"age": None,"current_club": None,"affiliation": None,"position": None}

# Fonction pour agréger les données par équipe / Function to aggregate the data by player / Función para agregar los datos por equipo
def aggregate_stats_by_player(stats_list: List[Dict[str, Any]], players_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # index des infos joueur / index of the player information / índice de la información del jugador        
    by_player_meta: Dict[Any, Dict[str, Any]] = {}
    for t in players_list:
        tid = t.get("player_id")
        if tid is None:
            continue
        by_player_meta[tid] = {"player_id": tid,"player_code": t.get("player_code"),"player_href": t.get("player_href")}

    # agrégation des données / aggregation of the data / agregación de los datos
    agg: Dict[Any, Dict[str, Any]] = {}
    for row in stats_list:
        tid = row.get("player_id")
        if tid is None:
            continue

        sec = str(row.get("section", "OVERALL")).lower().replace("-", "_")

        if tid not in agg:
            base = {"player_id": tid}
            if tid in by_player_meta:
                base.update({
                    "player_code": by_player_meta[tid].get("player_code"),"player_href": by_player_meta[tid].get("player_href")})
            agg[tid] = base

        # fallback si info absente dans agg mais présente dans row / fallback if the information is missing in agg but present in row / fallback si la información est faltante en agg pero presente en row
        if agg[tid].get("player_code") is None and row.get("player_code"):
            agg[tid]["player_code"] = row.get("player_code")

        if agg[tid].get("player_href") is None and row.get("player_href"):
            agg[tid]["player_href"] = row.get("player_href")

        # stockage des stats / storage of the stats / almacenamiento de las estadísticas
        for k, v in row.items():
            if k in ("player_id", "player_code", "player_href", "section"):
                continue
            pref_key = f"{sec}__{k}"
            agg[tid][pref_key] = v

    # ajouter les joueurs sans stats si besoin / add the players without stats if needed / agregar los jugadores sin estadísticas si es necesario
    for tid, meta in by_player_meta.items():
        if tid not in agg:
            agg[tid] = meta

    return list(agg.values())

## Partie pour choisir les saisons à scraper / Partie pour choisir les saisons à scraper / Parte para elegir las saisons a scrapear

# Récupération des indices de son choix / Retrieval of the indices of son choice / Recuperación de los índices de son choice
def _parse_multi_indices(raw: str, n: int) -> List[int]:
    raw = (raw or "").strip().lower()
    if raw in {"all", "*", "tout", "tous", "toutes"}:
        return list(range(1, n + 1))

    tokens = re.split(r"[,\s]+", raw)
    sel = set()
    for tok in tokens:
        if not tok:
            continue
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", tok)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b:
                a, b = b, a
            for k in range(a, b + 1):
                if 1 <= k <= n:
                    sel.add(k)
        else:
            if tok.isdigit():
                k = int(tok)
                if 1 <= k <= n:
                    sel.add(k)
    return sorted(sel)
    
# Fonction pour lire season.csv / Function to read season.csv / Función para leer season.csv
def _read_season_catalog(path: Path) -> pd.DataFrame:
    # Si le fichier n'existe pas, on le crée
    if not path.exists():
        return pd.DataFrame(columns=SEASON_COLS)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in SEASON_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[SEASON_COLS]

# Recherche de toutes les saisons / Search for all the seasons / Buscar todas las saisons
def choose_all_seasons() -> List[Tuple[int, str, pd.Series]]:
    df = _read_season_catalog(SEASON_CSV)
    if df.empty:
        raise RuntimeError(
            f"Aucune saison trouvée dans {SEASON_CSV}. "
            f"Ajoute des lignes avec colonnes {SEASON_COLS}."
        )

    selections: List[Tuple[int, str, pd.Series]] = []
    for idx, row in df.iterrows():
        try:
            id_season = int(str(row["id_season"]).strip())
        except Exception:
            print(f"[SKIP] id_season invalide à la ligne {idx+1}: {row['id_season']}")
            continue
        link_url = str(row["link_url_opta"]).strip()
        if not link_url:
            print(f"[SKIP] link_url manquant à la ligne {idx+1}")
            continue
        selections.append((id_season, link_url, row))
    return selections

# Fonction pour mettre à jour la base de données / Function to update the database / Función para actualizar la base de datos
def upsert_csv_by_keys(path: Path, df_new: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    # On crée le fichier si besoin / We create the file if needed / Creamos el archivo si es necesario
    if path.exists():
        df_old = pd.read_csv(path)
    else:
        df_old = pd.DataFrame(columns=df_new.columns)

    # On ajoute les données nouvelles / We add the new data / Añadimos los datos nuevos
    all_cols = list(dict.fromkeys([*df_old.columns, *df_new.columns])) 
    df_old = df_old.reindex(columns=all_cols)
    df_new = df_new.reindex(columns=all_cols)

    # On actualise les données en supprimmant les anciennes informations / We update the data by removing the old information / Actualizamos los datos eliminando la información antigua
    if not df_old.empty:
        # Jointure pour repérer les lignes à conserver / Jointure pour repérer les lignes à conserver / Unión para identificar las líneas a conservar
        df_old_mark = df_old.merge(df_new[keys].drop_duplicates(),on=keys,how="left",indicator=True)
        df_old_keep = df_old_mark[df_old_mark["_merge"] == "left_only"][df_old.columns]
        out = pd.concat([df_old_keep, df_new], ignore_index=True)
    else:
        out = df_new.copy()

    other_cols = [c for c in out.columns if c not in keys]
    out = out[keys + other_cols]

    out.to_csv(path, index=False)
    return out

# Fonction main pour le web scraping de the analyst / Function main for the web scraping of the analyst / Función main para el web scraping de the analyst
def run_scrape_the_analyst(headed: bool = True, all_seasons: bool = True):
    # Récupérer la liste de saisons / Retrieve the list of seasons / Recuperar la lista de saisons
    selections = choose_all_seasons()
    if not selections:
        print("Aucune saison sélectionnée/trouvée, arrêt.")
        return

    # On crée le driver en ajoutant les options désirées / We create the driver adding the desired options / Creamos el driver añadiendo las opciones deseadas
    chrome_options = Options()
    if not headed:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1366,900")
    chrome_options.add_argument("--no-sandbox")              
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)

    # On scrape la saison de son choix / We scrape the season of our choice / Escrapeamos la saison de nuestro choice
    try:
        for (id_season, season_url, _row) in selections:
            print("\n" + "=" * 70)
            print(f"Scraping saison {id_season} → {season_url}")
            print("=" * 70)

            try:
                # On ouvre la page de la saison / We open the page of the season / Abrimos la página de la saison
                driver.get(season_url)
                time.sleep(2)

                # On s'occupe de la page des cookies / We take care of the cookie page / Nos ocupamos de la página de cookies
                try:
                    handle_cookies(driver, accept=False)
                except Exception:
                    pass
                
                ## On traite les données par catégories / We treat the data by categories / Tratamos los datos por categorías
                
                # ATTACKING
                stats_list, players_list = extract_attacking(driver, id_season)
                print("On passe à Passing")
                # PASSING (depuis Attacking) / PASSING (from Attacking) / PASSING (desde Attacking) 
                stats_passing, players_passing = extract_passing(driver, from_label="Attacking")
                print("On passe à Defending")
                # DEFENDING (depuis 'PASSING') / DEFENDING (from 'PASSING') / DEFENDING (desde 'PASSING')
                stats_defending, players_defending = extract_defending(driver, from_label="Passing")
                print("On passe à Carrying")
                # CARRYING (depuis DEFENDING) / CARRYING (from DEFENDING) / CARRYING (desde DEFENDING)
                stats_carrying, players_carrying = extract_table_for_category(driver, category_label="Carrying", from_label="Defending")
                print("On passe à Goalkeeping")
                # GOALKEEPING / GOALKEEPING (from 'CARRIING') / GOALKEEPING (desde 'CARRIING')
                stats_goalkeeping, players_goalkeeping = extract_table_for_category(driver, category_label="Goalkeeping", from_label="Carrying")

                # Fusionner stats / Merge stats / Fusionar estadísticas
                stats_list.extend(stats_passing)
                stats_list.extend(stats_defending)
                stats_list.extend(stats_carrying)
                stats_list.extend(stats_goalkeeping)

                #print("\nAperçu stat_list (1 ligne) :")
                #pprint(stats_list[:1])
                # Fusionner players selon player_id sans doublons / Merge players according to player_id without duplicates / Fusionar jugadores según player_id sin duplicados
                seen = {t.get("player_id") for t in players_list}
                for bucket in [players_passing, players_defending, players_carrying, players_goalkeeping]:
                    for t in (bucket or []):
                        tid = t.get("player_id")
                        if tid and tid not in seen:
                            players_list.append(t)
                            seen.add(tid)

                # Agrégation par joueur / Aggregation by player / Agragación por jugador
                agg_rows = aggregate_stats_by_player(stats_list, players_list)

                # Enrichissement avec les informations de la fiche joueur / Enrichment with the player information cache / Enriquecimiento con la información de la cache de jugador    
                agg_rows = enrich_agg_rows_with_player_info(driver, agg_rows)
                
                # Aperçu / Overview / Aperçu
                #print("\nAperçu agrégé par joueur (1 ligne) :")
                #pprint(agg_rows[:1])

                # On sauvegarde les données dans un fichier csv, en ajoutant l'identifiant de la saison / We save the data in a csv file, adding the season identifier / Guardamos los datos en un archivo csv, añadiendo el identificador de la saison
                if agg_rows:
                    # On aggrége les données / We aggregate the data / Agregamos los datos
                    df_agg = pd.DataFrame(agg_rows)
                    # On ajoute l'identifiant de la saison, le nom de la saison, du pays, et du championnat / We add the season identifier, the season name, the country, and the championship name / Añadimos el identificador de la saison, el nombre de la saison, el país, y el nombre del campeonato
                    df_agg.insert(0, "id_season", id_season)
                    df_agg.insert(1, "season_name", _row.get("season_name"))
                    df_agg.insert(2, "country", _row.get("country"))
                    df_agg.insert(3, "championship_name", _row.get("championship_name"))
                    
                    # On fait la liste des colonnes à enlever, et on les supprime / We make the list of the columns to remove, and we remove them 
                    # Hacemos la lista de las columnas a eliminar, y las eliminamos
                    drop_cols = ["attacking_non_penalty__apps","attacking_non_penalty__mins","passing_overall__apps","passing_overall__mins",
                    "defending_overall__apps","defending_overall__mins", "carrying__apps","carrying__mins","passing_chance creation__apps",
                    "passing_chance creation__mins", "defending_discipline__apps", "defending_discipline__mins"]
                    
                    df_agg = df_agg.drop(columns=drop_cols, errors="ignore")
                    out_path = PLAYER_DIR / "players_stats.csv" # Chemin du fichier de sortie / Path of the output file / Ruta del archivo de salida
                    upsert_csv_by_keys(out_path, df_agg, keys=["id_season", "player_id"])
                    print(f"→ Fichier mis à jour pour la saison {id_season}")

            except Exception as e:
                # On continue avec la saison suivante sans planter tout le batch / We continue with the next season without crashing the whole batch / Continuamos con la siguiente temporada sin hacer caer todo el batch
                print(f"[WARN] Échec sur la saison {id_season}: {e}")
    
    # Fermeture du driver / Closing of the driver / Cierre del driver
    finally:
        driver.quit()
        
# Execution du web scraping pour la saison de son choix / Execution of the web scraping for the season of son choice / Ejecución del web scraping para la temporada de son choice
if __name__ == "__main__":
    run_scrape_the_analyst(headed=False, all_seasons=True) # Sans afficher la page et pour toutes les saisons / Without displaying the page and for all the seasons / Sin mostrar la página y para todas las temporadas