# Import des libraries / Importing librairies / Importación de bibliotecas
import re
import time
from typing import Tuple, List, Dict, Any
from bs4 import BeautifulSoupParte utilizada para el scraping de datos
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

# Fonction qui permet de cliquer sur l'onglet Tab / Function to click on the Tab / Función para clicar en el tab
def click_teams_tab(driver, timeout: int = 5) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.Switcher-module_switch__H9wDq, div.Switcher-module_full__RoAzn")
            )
        )
    except TimeoutException:
        print("Switcher Players/Teams introuvable ❌")
        return False

    # Recherche du bouton teams / Search for the teams button / Buscar el botón de equipos
    locator_candidates = [
        (By.ID, "teams"),
        (By.CSS_SELECTOR, "button[role='radio'][value='teams']"),
        (By.XPATH, "//button[@role='radio' and (normalize-space()='teams' or @value='teams')]"),
    ]

    teams_button = None
    
    for how, what in locator_candidates:
        try:
            teams_button = wait.until(EC.presence_of_element_located((how, what)))
            break
        except TimeoutException:
            continue

    if teams_button is None:
        print("Bouton Teams introuvable ❌")
        return False
    
    # Si le bouton teams est présent, on cherche à l'activer / If the teams button is present, we search to activate it / Si el botón de equipos est presente, on cherche à l'activer
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teams_button)
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#teams, button[role='radio'][value='teams']")))
        teams_button.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", teams_button)
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", teams_button)
        except Exception:
            pass

    # On vérifie que le bouton teams est bien activé / We check that the teams button is well activated / Verificamos que el botón de equipos está bien activado
    try:
        wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, "button#teams, button[role='radio'][value='teams']")
            .get_attribute("aria-checked") == "true"
        )
        #print("Bouton Teams cliqué ✅")
        return True
    except TimeoutException:
        print("Échec d'activation de l'onglet Teams ❌")
        return False

# Fonction permettant de cliquer sur le toggle 'per match' / Function to click on the toggle 'per match' / Función para clicar en el toggle 'per match'
def enable_per_match(driver, timeout: int = 5) -> bool:
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        wrapper = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'MiniToggle')][.//div[contains(@class,'MiniToggle') and normalize-space()='per match']]"
            ))
        )
    except TimeoutException:
        print("Toggle 'per match' introuvable ❌")
        return False

    # Recherche du toggle 'per match' / Search for the toggle 'per match' / Buscar el toggle 'per match'
    def _find_cb_and_label():
        cb = wrapper.find_element(By.XPATH, ".//label[contains(@class,'MiniToggle')]/input[@type='checkbox']")
        lab = wrapper.find_element(By.XPATH, ".//label[contains(@class,'MiniToggle')]")
        return cb, lab

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrapper)
    cb, lab = _find_cb_and_label()

    # Si on trouve le toggle 'per match', on cherche à l'activer / If we find the toggle 'per match', we search to activate it / Si encontramos el toggle 'per match', buscamos a activarlo
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//label[contains(@class,'MiniToggle')]")))
        try:
            lab.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", lab)
    except Exception:
        driver.execute_script("arguments[0].click();", lab)

    # On vérifie que le toggle 'per match' est bien activé / We check that the toggle 'per match' is well activated / Verificamos que el toggle 'per match' est bien activado
    try:
        WebDriverWait(driver, 4).until(lambda d: _find_cb_and_label()[0].is_selected())
        #print("Mode 'per match' activé ✅")
        return True
    except TimeoutException:
        print("Impossible d'activer 'per match' ❌")
        return False

# Fonction permettant d'accéder au tableau des différentes pages d'Opta Analyst / Function to access the table of the different pages of Opta Analyst / Función para acceder al tabla de las diferentes páginas de Opta Analyst
def _get_tbody_html(driver) -> str:
    # Recherche de la partie du code reservée à l'affichage du tableau par équipe / Search for the part of the code reserved for the display of the table by team / Buscar la parte del código reservada para el display del tabla por equipo
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
        print("Conteneur des 'coins' introuvable ❌")
        return False

    xp = (
        ".//button[contains(@class,'Button-module_button-coin') and "
        "contains(translate(normalize-space(.),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), %s)]"
    )
    target_text = label.strip().upper()

    try:
        btn = coins_container.find_element(By.XPATH, xp % repr(target_text))
    except Exception:
        print(f"Bouton coin '{label}' introuvable ❌")
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

# Fonction pour scraper le contenu du tableau / Function to scrape the content of the table / Función para scrapear el contenido de la tabla
def scrape_table(driver, timeout: int = 6, section: str = "OVERALL"):
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, timeout)
    try:
        _ = wait.until(EC.presence_of_element_located((
            By.XPATH, "(//table[contains(@class,'Table-module_data-table')])[1]"
        )))
    except TimeoutException:
        raise RuntimeError("Premier tableau introuvable.")

    # On accède au code source de la page / We access the code source of the page / Accedemos al código fuente de la página
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # On accède aux informations associées au tableau affiché sur la page / We access the information associated with the table displayed on the page / Accedemos a la información asociada con la tabla mostrada en la página
    table = soup.select_one("table.Table-module_data-table__giW24") or \
            soup.select_one("table[class*='Table-module_data-table']")
    if table is None:
        raise RuntimeError("Premier tableau introuvable (fallback).")

    # On renomme le nom de certaines colonnes afin de les normaliser (notamment les colonnes contenant des espaces pouvant poser problème dans l'analyse de ces dernières) / We rename the name of some columns to normalize them (particularly the columns containing spaces that can cause problems in the analysis of these latter) / Renombramos el nombre de algunas columnas para normalizarlas (especialmente las columnas que contienen espacios que pueden causar problemas en el análisis de estas últimas)
    def norm(s: str) -> str:
        s = (s or "").strip().lower()
        mapping = {
            # Attacking
            "conv %": "conv_pct",
            "goals vs xg": "goals_vs_xg",
            "xg per shot": "xg_per_shot",
            "sot": "sot",
            "name": "name",
            "goal %": "goal_pct",
            "shot %": "shot_pct",
            "xg %": "xg_pct",
            "played": "played",
            "hit post": "hit_post",
            "offsides": "offsides",
            "tou in box": "touches_in_box",
            "free-kicks": "free_kicks",
            "fast breaks": "fast_breaks",
            "headers": "headers",
            "penalties": "penalties",
            "total": "total",
            "goals": "goals",
            
            # Passing
            "avg poss": "avg_poss",
            "%": "pct",
            "fwd": "fwd",
            "bwd": "bwd",
            "left": "left",
            "right": "right",
            "through balls": "through_balls",
            "all passes": "all_passes",
            "final third passes": "final_third_passes",
            "pass direction": "pass_direction",
            "crosses": "crosses",

            # Pressing
            "pressed seqs": "pressed_seqs",
            "ppda": "ppda",
            "start distance (m)": "start_distance_m",
            "high turnovers": "high_turnovers",
            "shot ending": "shot_ending",
            "goal ending": "goal_ending",
            "% end in shot": "pct_end_in_shot",

            # Sequences
            "build-ups": "build_ups",
            "direct attacks": "direct_attacks",
            "10+ passes": "ten_plus_passes",
            "direct speed": "direct_speed",
            "passes per seq": "passes_per_seq",
            "sequence time": "sequence_time",

            # Misc
            "subs used": "subs_used",
            "subs goals": "subs_goals",
            "errors lead to shot": "errors_lead_to_shot",
            "errors lead to goal": "errors_lead_to_goal",
            "fouled": "fouled",
            "fouls": "fouls",
            "yellows": "yellows",
            "reds": "reds",
            "pens won": "pens_won",
            "pens conceded": "pens_conceded",
            "opp yellows": "opp_yellows",
            "opp reds": "opp_reds",

            # Defending
            "shots in box %": "shots_in_box_pct",
            "goals in box %": "goals_in_box_pct",
            "ints": "interceptions",
            "recs": "recoveries",
            "blks": "blocks",
            "clrs": "clearances",
            "ground duels won": "ground_duels_won",
            "aerial duels won": "aerial_duels_won",

        }
        return mapping.get(s, s.replace(" ", "_").replace("-", "_"))

    # Normalisation des noms de colonnes / Normalization of the column names / Normalización de los nombres de las columnas
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

    # Recherche des noms de colonnes, ainsi que leur contenu / Search for the names of the columns, as well as their content / Buscar los nombres de las columnas, así como su contenido
    thead = table.select_one("thead")
    tbody = table.select_one("tbody")
    if not tbody:
        raise RuntimeError("tbody introuvable.")

    # Recherche du nombre de colonnes dans le body / Search for the number of columns in the body / Buscar el número de columnas en el body
    first_tr = tbody.select_one("tr")
    tds_first = first_tr.select("td") if first_tr else []
    if not tds_first:
        return [], []
    n_cols_body = len(tds_first)

    header_labels = [None] * n_cols_body  # index 0 = 'name' (équipe) / index 0 = 'name' (team) / index 0 = 'name' (equipo)

    if thead:
        rows = thead.select("tr")
        if rows:
            # On considère les lignes du bas comme les noms des colonnes / We consider the bottom lines as the names of the columns / Consideramos las líneas de abajo como los nombres de las columnas
            bottom_cells = rows[-1].select("th")
            # On considère les lignes du haut comme les groupes (si disponible) associés aux colonnes / We consider the top lines as the groups (if available) associated with the columns / Consideramos las líneas de arriba como los grupos (si disponibles) asociados con las columnas
            top_cells = rows[0].select("th") if len(rows) > 1 else []

            # Ajoute le nom du groupe au nom de la colonne associée / Add the name of the group to the name of the associated column / Añadir el nombre del grupo al nombre de la columna asociada
            expanded_groups = []
            if top_cells:
                for th in top_cells:
                    grp = th.get_text(strip=True)
                    colspan = int(th.get("colspan", "1"))
                    expanded_groups.extend([norm(grp) if grp else None] * colspan)
                # sécurisation de la longueur / security of the length / seguridad de la longitud
                if len(expanded_groups) < len(bottom_cells):
                    expanded_groups += [None] * (len(bottom_cells) - len(expanded_groups))
                elif len(expanded_groups) > len(bottom_cells):
                    expanded_groups = expanded_groups[:len(bottom_cells)]
            else:
                expanded_groups = [None] * len(bottom_cells)

            # Construction des noms de tableaux finaux (en excluant la colonne name) / Construction des noms de tableaux finaux (en excluant la colonne name) / Construcción de los nombres de tablas finales (excluyendo la columna name)
            for col_idx in range(1, n_cols_body):
                leaf = bottom_cells[col_idx].get_text(strip=True) if col_idx < len(bottom_cells) else ""
                leaf_n = norm(leaf)
                grp = expanded_groups[col_idx] if col_idx < len(expanded_groups) else None
                header_labels[col_idx] = f"{grp}__{leaf_n}" if grp else leaf_n

    # Ajout d'un nom de colonne générique si aucune colonne n'est renseigné / Add a generic column name if no column is provided / Añadir un nombre de columna genérico si ninguna columna está proporcionada
    for i in range(1, n_cols_body):
        if not header_labels[i]:
            header_labels[i] = f"col_{i}"

    # Parcours des lignes du tableau / Traversal of the lines of the table / Recorrido de las líneas de la tabla
    stats_rows, teams_rows = [], []
    for tr in tbody.select("tr"):
        tds = tr.select("td")
        if not tds:
            continue

        # Association des 1ère colonnes comme les informations sur l'équipe / Association of the first columns as the information on the team / Asociación de las primeras columnas como la información sobre el equipo
        t0 = tds[0]
        a = t0.select_one("a[href]")
        img = t0.select_one("img")
        team_href = a["href"] if a else ""
        team_logo = img["src"] if img and img.has_attr("src") else ""
        team_code = a.get_text(strip=True) if a else t0.get_text(strip=True)

        team_id = None
        if team_href:
            m = re.search(r"/team/scm-(\d+)/([^/?#]+)", team_href)
            if m:
                try:
                    team_id = int(m.group(1))
                except Exception:
                    team_id = None

        # On stocke les informations sur l'équipe / We store the information on the team / Almacenamos la información sobre el equipo
        teams_rows.append({
            "team_id": team_id,
            "team_code": team_code,
            "team_logo": team_logo,
        })

        # On récolte ensuite le reste des colonnes numériques / We then collect the rest of the numeric columns / Recopilamos el resto de las columnas numéricas
        row_vals: Dict[str, Any] = {}
        for i, td in enumerate(tds[1:], start=1):
            key = header_labels[i]
            txt = td.get_text(strip=True)
            row_vals[key] = parse_num(txt)

        row_vals.update({
            "team_id": team_id,
            "team_code": team_code,
            "section": section,  # nom de la section (OVERALL, SET-PIECES,MISC...) / name of the section (OVERALL, SET-PIECES,MISC...) / nombre de la sección (OVERALL, SET-PIECES,MISC...)
        })
        stats_rows.append(row_vals)

    return stats_rows, teams_rows

# Fonction pour extraire les données du tableau spécifique à Attacking / Function to extract the data of the specific table to Attacking / Función para extraer los datos de la tabla específica a Attacking
def extract_attacking(driver, id_season):
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, teams = [], []
    # Récupération du driver et Timeout pour laisser le temps de raffraichir la page / Retrieval of the driver and Timeout to let the page refresh / Recuperación del driver y Tiempo de espera para que la página se actualice
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # On ferme la page de cookie si cela n'est pas fait / We close the cookie page if it is not done / Cerramos la página de cookie si no se ha hecho
    try:
        handle_cookies(driver)
    except Exception:
        pass

    # On active les boutons Teams et per match / We activate the Teams and per match buttons / Activamos los botones Teams y per match
    if not click_teams_tab(driver):
        return stats, teams
    enable_per_match(driver)

    # On scrape les sections de notre choix / We scrape the sections of our choice / Escrapeamos las secciones de nuestro choice
    sections = ["OVERALL", "SET-PIECES", "MISC"]
    for sec in sections:
        prev_html = _get_tbody_html(driver)

        if not click_coin(driver, sec):
            print(f"Impossible d'activer le coin {sec} ❌ — on passe au suivant")
            continue

        # On associe le nom des colonnes avec le nom du tableau 'attacking' / We associate the name of the columns with the name of the table 'attacking' / Asociamos el nombre de las columnas con el nombre de la tabla 'attacking'
        try:
            stats_rows, teams_rows = scrape_table(driver, section=f"attacking_{sec}")
            stats.extend(stats_rows)
            # On regarde si on a pas pris les données plusieurs fois pour la même équipe / We check if we have not taken the data several times for the same team / Verificamos si no hemos tomado los datos varias veces para el mismo equipo
            seen = {t.get("team_id") for t in teams}
            for t in teams_rows:
                if t.get("team_id") not in seen:
                    teams.append(t)
                    seen.add(t.get("team_id"))
            #print(f"Tableau '{sec}' récupéré ✅ ({len(stats_rows)} lignes)")
        except Exception as e:
            print(f"Erreur lors du scraping du tableau '{sec}': {e}")

    return stats, teams


# Fonction pour extraire les données ayant un tableau unique : Passing, Pressing... (sans section) / Function to extract the data of a unique table: Passing, Pressing... (without section) / Función para extraer los datos de una tabla única: Passing, Pressing... (sin sección)
def extract_table_for_category(driver, category_label: str = "Passing", from_label: str = "Attacking"):
    # Initialisation des variables pour stocker les données / Initialization of the variables to store the data / Inicialización de las variables para almacenar los datos
    stats, teams = [], []
    # On accède aux informations sur la tableau via le driver / We access the information on the table via the driver / Accedemos a la información sobre la tabla via el driver
    prev_html = _get_tbody_html(driver)

    # On clique pour accéder au tableau de notre chix / We click to access the table of our choice / Hacemos clic para acceder a la tabla de nuestro choice
    if not click_category_select(driver, category_label, from_label=from_label):
        print(f"Impossible d'activer la catégorie '{category_label}' ❌")
        return stats, teams

    try:
        stats_rows, teams_rows = scrape_table(driver, section=category_label.upper())
        stats.extend(stats_rows)
        # On récupère les données en ne prenant pas deux fois les mêmes données d'un même équipe / We collect the data without taking the same data several times for the same team / Recopilamos los datos sin tomar los mismos datos varias veces para el mismo equipo
        seen = set(t.get("team_id") for t in teams)
        for t in teams_rows:
            if t.get("team_id") not in seen:
                teams.append(t)
                seen.add(t.get("team_id"))
        #print(f"Tableau catégorie '{category_label}' récupéré ✅ ({len(stats_rows)} lignes)")
    except Exception as e:
        print(f"Erreur lors du scraping de la catégorie '{category_label}': {e}")

    return stats, teams

# Fonction pour extraire les données provenant spécifiquement de Defending / Function to extract the data from Defending / Función para extraer los datos de Defending
def extract_defending(driver, from_label: str = "Misc."):
    # On initialise les variables pour stocker les données / We initialize the variables to store the data / Inicializamos las variables para almacenar los datos
    stats, teams = [], []

    # On clique sur la catégorie Defending / We click on the category Defending / Hacemos clic en la categoría Defending
    if not click_category_select(driver, target_label="Defending", from_label=from_label):
        print("Impossible d'activer la catégorie 'Defending' ❌")
        return stats, teams

    # On parcourt les sections disponibles associées / We traverse the available sections associated / Recorremos las secciones disponibles asociadas
    defending_sections = [
        ("OVERALL", ["OVERALL"]),
        ("SET-PIECES", ["SET-PIECES"]),
        ("DEFENSIVE_ACTIONS", ["DEFENSIVE ACTIONS"]),
        ("MISC", ["MISC"]),
    ]

    # On clique sur les sections de notre choix / We click on the sections of our choice / Hacemos clic en las secciones de nuestro choice
    for canonical, label_variants in defending_sections:
        clicked = False
        for lab in label_variants:
            if click_coin(driver, lab):
                clicked = True
                break
        if not clicked:
            print(f"Impossible d'activer le coin '{canonical}' (Defending) ❌ — on passe au suivant")
            continue

        # On associe les données à partir de la catégorie ainsi que la section associées / We associate the data from the category as well as the associated section / Asociamos los datos desde la categoría así como la sección asociada
        try:
            sec_tag = f"DEFENDING_{canonical.replace('_', '-')}"
            stats_rows, teams_rows = scrape_table(driver, section=sec_tag)
            stats.extend(stats_rows)

            # On fait attention à ne pas stocker les informations d'une même équipe plusieurs fois / We pay attention to not store the information of the same team several times / Nos aseguramos de no almacenar la información de un mismo equipo varias veces
            seen = {t.get("team_id") for t in teams}
            for t in teams_rows:
                if t.get("team_id") not in seen:
                    teams.append(t)
                    seen.add(t.get("team_id"))

            #print(f"Tableau 'Defending / {canonical}' récupéré ✅ ({len(stats_rows)} lignes)")
        except Exception as e:
            print(f"Erreur lors du scraping 'Defending / {canonical}': {e}")

    return stats, teams

# Fonction pour agréger les données par équipe / Function to aggregate the data by team / Función para agregar los datos por equipo
def aggregate_stats_by_team(
    stats_list: List[Dict[str, Any]],
    teams_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    # index des infos d'équipe / index of the team information / índice de la información del equipo
    by_team_meta: Dict[Any, Dict[str, Any]] = {}
    for t in teams_list:
        tid = t.get("team_id")
        if tid is None:
            continue
        by_team_meta[tid] = {
            "team_id": tid,
            "team_code": t.get("team_code"),
            "team_logo": t.get("team_logo"),
        }

    # agrégation des données / aggregation of the data / agregación de los datos
    agg: Dict[Any, Dict[str, Any]] = {}
    for row in stats_list:
        # Récupèration de l'identifiant de l'équipe / Retrieval of the team identifier / Recuperación del identificador del equipo
        tid = row.get("team_id")
        if tid is None:
            continue
        sec = str(row.get("section", "OVERALL")).lower().replace("-", "_")

        # Aggrège selon l'identifiant de l'équipe / Aggregate according to the team identifier / Agregamos según el identificador del equipo
        if tid not in agg:
            base = {"team_id": tid}
            if tid in by_team_meta:
                base.update({
                    "team_code": by_team_meta[tid].get("team_code"),
                    "team_logo": by_team_meta[tid].get("team_logo"),
                })
            agg[tid] = base

        # Complèter les données par des valeurs None si non disponible / Complete the data by None values if not available / Completar los datos por valores None si no están disponibles
        if agg[tid].get("team_code") is None and row.get("team_code"):
            agg[tid]["team_code"] = row.get("team_code")

        # Stockage des données par équipe / Storage of the data by team / Almacenamiento de los datos por equipo
        for k, v in row.items():
            if k in ("team_id", "team_code", "section"):
                continue
            pref_key = f"{sec}__{k}"
            agg[tid][pref_key] = v

    # Ajouter équipes n'ayant pas de stats sur une catégorie au cas où / Add teams that have no stats on a category in case / Añadir equipos que no tienen estadísticas en una categoría en caso de que
    for tid, meta in by_team_meta.items():
        if tid not in agg:
            agg[tid] = meta

    return list(agg.values())

## Partie pour choisir les saisons à scraper / Partie pour choisir les saisons à scraper / Parte para elegir las saisons a scrapear

# Fonction pour trouver le chemin de la racine du projet / Function to find the path of the project root / Función para encontrar la ruta de la raíz del proyecto
def _project_root() -> Path:
    try:
        return Path(__file__).resolve().parents[1]  # .../projet
    except Exception:
        return Path(os.getcwd()).resolve()

ROOT_DIR = _project_root()
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)



SEASON_CSV = DATA_DIR / "season.csv"
SEASON_COLS = ["country", "championship_name", "season_name", "id_season", "link_url"]


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
        link_url = str(row["link_url"]).strip()
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
        df_old_mark = df_old.merge(
            df_new[keys].drop_duplicates(),
            on=keys,
            how="left",
            indicator=True
        )
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
    selections = choose_all_seasons() if all_seasons else choose_seasons_interactively()
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
                stats_list, teams_list = extract_attacking(driver, id_season)

                # PASSING (depuis Attacking) / PASSING (from Attacking) / PASSING (desde Attacking) 
                stats_passing, teams_passing = extract_table_for_category(
                    driver, category_label="Passing", from_label="Attacking"
                )

                # PRESSING (depuis Passing) / PRESSING (from Passing) / PRESSING (desde Passing)
                stats_pressing, teams_pressing = extract_table_for_category(
                    driver, category_label="Pressing", from_label="Passing"
                )

                # SEQUENCES (depuis Pressing) / SEQUENCES (from Pressing) / SEQUENCES (desde Pressing)
                stats_sequences, teams_sequences = extract_table_for_category(
                    driver, category_label="Sequences", from_label="Pressing"
                )

                # MISC. (depuis Sequences) / Misc. (from Sequences) / Misc. (desde Sequences)
                stats_misc, teams_misc = extract_table_for_category(
                    driver, category_label="Misc.", from_label="Sequences"
                )

                # DEFENDING (depuis 'Sequences') / DEFENDING (from 'Sequences') / DEFENDING (desde 'Sequences')
                stats_defending, teams_defending = extract_defending(
                    driver, from_label="Misc."
                )

                # Fusionner stats / Merge stats / Fusionar stats
                stats_list.extend(stats_passing)
                stats_list.extend(stats_pressing)
                stats_list.extend(stats_sequences)
                stats_list.extend(stats_misc)
                stats_list.extend(stats_defending)

                # Fusionner teams selon team_id sans doublons / Merge teams according to team_id without duplicates / Fusionar equipos según team_id sin duplicados
                seen = {t.get("team_id") for t in teams_list}
                for bucket in [teams_passing, teams_pressing, teams_sequences, teams_misc, teams_defending]:
                    for t in (bucket or []):
                        tid = t.get("team_id")
                        if tid and tid not in seen:
                            teams_list.append(t)
                            seen.add(tid)

                # Agrégation par équipes / Aggregation by teams / Agregación por equipos
                agg_rows = aggregate_stats_by_team(stats_list, teams_list)
                
                # Aperçu / Overview / Aperçu
                #print("\nAperçu agrégé par équipe (1 ligne) :")
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
                    
                    # On fait la liste des colonnes à enlever, et on les supprime / We make the list of the columns to remove, and we remove them / Hacemos la lista de las columnas a eliminar, y las eliminamos
                    drop_cols = ["attacking_set_pieces__played","attacking_misc__played", "passing__played","passing__all_passes__total",
                                 "passing__all_passes__successful","passing__final_third_passes__total","pressing__played",
                                 "sequences__played","defending_overall__played","defending_set_pieces__played",
                                 "defending_defensive_actions__played","defending_misc__played",
                                 
                    ]
                    
                    df_agg = df_agg.drop(columns=drop_cols, errors="ignore")
                    out_path = DATA_DIR / "teams_stats.csv" # Chemin du fichier de sortie / Path of the output file / Ruta del archivo de salida
                    upsert_csv_by_keys(out_path, df_agg, keys=["id_season", "team_id"])
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
