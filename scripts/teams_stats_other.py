# Import des libraries / Importing librairies / Importación de bibliotecas
import re
import time
from typing import Tuple, List, Dict, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, WebDriverException, InvalidSessionIdException, NoSuchWindowException
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from pprint import pprint
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse

## Partie servant pour le scraping des données / Part used for data scraping / Parte utilizada para el scraping de datos

# Initialisation du driver en mettant les options désirés / Initialising the driver by setting the desired options / Inicialización del controlador configurando las opciones deseadas.
def make_driver(headed: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    if not headed:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--window-size=1366,900")
        chrome_options.add_argument("--lang=fr-FR")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    else:
        chrome_options.add_argument("--window-size=1366,900")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.page_load_strategy = "eager"

    drv = webdriver.Chrome(options=chrome_options)
    drv.set_page_load_timeout(40)
    drv.set_script_timeout(40)
    return drv


# Fermeture de la page des cookies / Closing the cookies page / Cierre de la página de cookies
def handle_cookies(driver, accept: bool = True, timeout: int = 2) -> bool:
    # Récupération du driver en laissant du Timeout pour laisser le temps de raffraichir la page / Retrieving the driver by leaving a timeout to allow time to refresh the page / Recuperación del controlador dejando un tiempo de espera para que se actualice la página
    wait = WebDriverWait(driver, timeout)
    btn_id = "onetrust-accept-btn-handler" if accept else "onetrust-reject-all-handler"
    banner_sel = "div.ot-sdk-container[role='dialog'],#onetrust-banner-sdk,#onetrust-consent-sdk,#onetrust-button-group-parent"
    fallback_xp = ("//button[normalize-space()='I Accept' or contains(.,'Accept')]" if accept
                   else "//button[normalize-space()='Reject All' or contains(.,'Reject')]")

    # Recherche d'une bannière de cookie visible / Search for a visible cookie banner / Búsqueda de un banner de cookies visible
    def banner_visible(drv):
        try:
            return any(el.is_displayed() for el in drv.find_elements(By.CSS_SELECTOR, banner_sel))
        except Exception:
            return False

    if not banner_visible(driver):
        return True
    
    # Si la bannière de cookie est visible, on cherche à fermer cette page / If the cookie banner is visible, we try to close this page / Si el banner de cookies está visible, se intenta cerrar esta página
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

    # Attendre la disparition de la bannière / Wait for the banner to disappear / Esperar a que desaparezca el banner
    try:
        WebDriverWait(driver, timeout).until(lambda d: not banner_visible(d))
    except TimeoutException:
        pass

    return not banner_visible(driver) or clicked

# Ouvre une URL avec quelques retries pour éviter les blocages de chargement / Open a URL with a few retries to avoid load stalls / Abre una URL con algunos reintentos para evitar bloqueos de carga.
def get_with_retries(driver, url: str, tries: int = 3, sleep_s: float = 1.0):
    last_err = None
    for _ in range(tries):
        try:
            driver.get(url)
            return
        except TimeoutException as e:
            last_err = e
            # Si la page reste bloquée, on stoppe le chargement et on réessaie. / If the page hangs, stop loading and retry. / Si la página se cuelga, se detiene la carga y se reintenta.
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass
            time.sleep(sleep_s)
    if last_err:
        raise last_err


# Ouvre l'onglet 'Statistiques des Équipes' / Opens the 'Team Statistics' / Abre la pestaña 'Estadísticas de los Equipos'
def click_team_statistics(driver, timeout: int = 20) -> None:
    wait = WebDriverWait(driver, timeout)

    # Vérifie si l'onglet est déjà ouvert / Check if tab is already open / Verifica si la pestaña ya está abierta
    def _on_team_stats(drv):
        url = (drv.current_url or "").lower()
        if "/teamstatistics/" in url:
            return True
        try:
            sel = drv.find_elements(By.CSS_SELECTOR, "#sub-navigation a[href*='/teamstatistics/'].selected")
            return len(sel) > 0
        except Exception:
            return False

    # Essaie de cliquer sur le lien dans la navigation / Try to click link in navigation / Intenta hacer clic en el enlace en la navegación
    def _click_link_in(drv) -> bool:
        try:
            nav = WebDriverWait(drv, max(2, timeout // 2)).until(
                EC.presence_of_element_located((By.ID, "sub-navigation"))
            )
            links = nav.find_elements(By.CSS_SELECTOR, "a[href*='/teamstatistics/']")
            if not links:
                links = nav.find_elements(
                    By.XPATH,
                    ".//a[normalize-space()='Statistiques des Équipes' "
                )
            if links:
                link = links[0]
                drv.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                try:
                    WebDriverWait(drv, 4).until(EC.element_to_be_clickable(link)).click()
                except ElementClickInterceptedException:
                    drv.execute_script("arguments[0].click();", link)
                except Exception:
                    ActionChains(drv).move_to_element(link).pause(0.2).click(link).perform()
                return True
        except Exception:
            pass
        return False

    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    # Premier essai direct / First direct attempt / Primer intento directo
    if _click_link_in(driver):
        wait.until(_on_team_stats)
        print("Fonctionne au 1er essai")
        return

    # Essai dans les iframes / Try inside iframes / Intentar dentro de iframes
    frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
    for fr in frames:
        try:
            driver.switch_to.frame(fr)
            if _click_link_in(driver):
                driver.switch_to.default_content()
                wait.until(_on_team_stats)
                print("Fonctionne via les iframes")
                return
        except Exception:
            pass
        finally:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

    # Dernier fallback : navigation directe via URL / Last fallback: direct navigation via URL / Último recurso: navegación directa por URL
    cur = driver.current_url
    try:
        from urllib.parse import urlparse, urlunparse

        p = urlparse(cur)
        parts = [seg for seg in p.path.split("/") if seg]
        if "stages" in [s.lower() for s in parts]:
            i = [s.lower() for s in parts].index("stages")
            if i + 1 < len(parts):
                stage_id = parts[i + 1]
                base_parts = parts[: i + 2]
                candidates = [
                    "/" + "/".join(base_parts + ["TeamStatistics"]) + "/",
                    "/" + "/".join(base_parts + ["teamstatistics"]) + "/",
                ]
                for cand in candidates:
                    cand_url = urlunparse((p.scheme, p.netloc, cand, "", "", ""))
                    try:
                        get_with_retries(driver, cand_url, tries=2, sleep_s=1.0)
                        if "/teamstatistics" in (driver.current_url or "").lower():
                            print("Onglet 'Statistiques des Équipes' ouvert")
                            return
                    except Exception:
                        continue
    except Exception:
        pass

    # Si on arrive ici, on a échoué. / If we reach here, we failed. / Si llegamos aquí, fallamos.
    cur = driver.current_url
    raise TimeoutException(f"Impossible d'ouvrir l'onglet Team Statistics depuis {cur}")


# Récupérer la liste des équipes à partir de l'url du championnat / Retrieve the list of teams from the championship URL / Recuperar la lista de equipos a partir de la URL del campeonato
def _clean_team_text(txt: str) -> str:
    # Normalise les noms / Normalises names / Normaliza los nombres
    txt = re.sub(r"^\s*\d+\.\s*", "", (txt or "").strip())
    txt = re.sub(r"\s+", " ", txt)
    return txt

# Si aucun texte n'est visible, on donne le nom issu du lien url / If no text is visible, the name from the URL link is given / Si no se ve ningún texto, se muestra el nombre del enlace URL
def _name_from_href_fallback(href: str) -> str:
    try:
        last = href.rstrip("/").split("/")[-1]
        last = re.sub(r"^[a-z]{2,}-", "", last)
        parts = [p for p in last.split("-") if p]
        # On récupère le nom depuis l'url de l'équipe associé / We retrieve the name from the associated team's URL / Se recupera el nombre de la URL del equipo asociado
        parts = [p.capitalize() for p in parts]
        # Recolle avec tirets si le nom contient des composés / Rejoin with hyphens if the name contains compounds / Recoloca con guiones si el nombre contiene compuestos
        if len(parts) > 1:
            out = []
            i = 0
            while i < len(parts):
                if parts[i] == "Saint" and i + 1 < len(parts):
                    out.append(f"Saint-{parts[i+1]}")
                    i += 2
                else:
                    out.append(parts[i])
                    i += 1
            return " ".join(out)
        return parts[0] if parts else ""
    except Exception:
        return ""

# On extrait les informations de chaque équipe afin d'accéder dans un second temps leurs informations associées / Information is extracted from each team so that their associated information can be accessed at a later stage / Se extrae la información de cada equipo para acceder posteriormente a su información asociada 
# Extraire la liste des équipes depuis l’onglet "Général" de "Statistiques des Équipes" / Extract team list from "General" tab of "Team Statistics" / Extraer la lista de equipos desde la pestaña "General" de "Estadísticas de los Equipos"
def extract_team_basic_info_from_summary(driver, timeout: int = 20, min_rows: int = 8):
    # Attente du driver / Wait for driver / Espera del driver
    wait = WebDriverWait(driver, timeout)
    print(f"[INFO] Début extract_team_basic_info_from_summary — url={driver.current_url!r} / timeout={timeout} / min_rows={min_rows}")  # Début / Start / Inicio

    # Vérifier que l’onglet 'Statistiques des Équipes' est bien actif (sécurité) / Ensure 'Team Statistics' tab is active (safety) / Comprobar que la pestaña 'Estadísticas de los Equipos' está activa (seguridad)
    try:
        # On tente de détecter que l’on est déjà sur /teamstatistics/ / Try to detect we are already on /teamstatistics/ / Intentar detectar que ya estamos en /teamstatistics/
        cur = (driver.current_url or "").lower()
        if "/teamstatistics/" not in cur:
            print("[INFO] Pas sur /teamstatistics/ → on tente de forcer l’onglet via click_team_statistics()")  # Info / Info / Info
            try:
                click_team_statistics(driver, timeout=max(10, timeout // 2))
            except Exception as e:
                print(f"[WARN] Échec click_team_statistics: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia
        else:
            print("[INFO] Déjà sur /teamstatistics/")  # OK / OK / OK
    except Exception as e:
        print(f"[WARN] Vérification d’onglet échouée: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # Sélectionner l’onglet "Général" si besoin / Select "General" tab if needed / Seleccionar la pestaña "General" si es necesario
    try:
        wait.until(EC.presence_of_element_located((By.ID, "stage-team-stats")))
        summary_tab = driver.find_element(By.CSS_SELECTOR, '#stage-team-stats-options a[href="#stage-team-stats-summary"]')
        if "selected" not in (summary_tab.get_attribute("class") or ""):
            print("[INFO] Onglet 'Général' non sélectionné → clic()")  # Info / Info / Info
            try:
                summary_tab.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", summary_tab)
            except Exception:
                ActionChains(driver).move_to_element(summary_tab).pause(0.2).click(summary_tab).perform()
        else:
            print("[INFO] Onglet 'Général' déjà actif")  # OK / OK / OK
    except Exception as e:
        print(f"[WARN] Impossible d’activer l’onglet 'Général': {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # Petite aide visuelle pour déclencher le lazy-load / Small visual nudge to trigger lazy-load / Pequeño impulso visual para activar lazy-load
    try:
        driver.execute_script("window.scrollTo(0,0);")
        driver.execute_script("document.querySelector('#top-team-stats-summary-content')?.scrollIntoView({block:'center'});")
        driver.execute_script("window.dispatchEvent(new Event('scroll'));")
    except Exception:
        pass

    # Helper pour chercher les liens d’équipes dans le DOM courant / Helper to find team anchors in current DOM / Helper para buscar enlaces de equipos en el DOM actual
    def _anchors_in_current_context():
        return driver.find_elements(By.CSS_SELECTOR, "#top-team-stats-summary-content a.team-link")

    # Essayer d’abord dans le document principal, sinon regarder dans les iframes / Try main doc first, else check iframes / Probar primero el documento principal, luego iframes
    anchors = []
    frame_found = None
    try:
        anchors = _anchors_in_current_context()
    except Exception:
        anchors = []

    if not anchors:
        print("[INFO] 0 lien d’équipe dans le document principal → on tente dans les iframes")  # Info / Info / Info
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
        for fr in frames:
            try:
                driver.switch_to.frame(fr)
                anchors = _anchors_in_current_context()
                if anchors:
                    frame_found = fr
                    print("[INFO] Liens d’équipes trouvés dans une iframe")  # OK / OK / OK
                    break
            except Exception:
                pass
            finally:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
        # Se replacer dans le bon contexte si trouvé / Return to proper context if found / Volver al contexto adecuado si se encontró
        if frame_found:
            try:
                driver.switch_to.frame(frame_found)
            except Exception as e:
                print(f"[WARN] Impossible de rebasculer vers l’iframe trouvée: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # Attendre au moins 1 lien, avec ré-essais et micro-sleeps (en CI c’est plus lent) / Wait for >=1 link, with retries and micro-sleeps (CI is slower) / Esperar ≥1 enlace, con reintentos y micro-pausas (CI es más lento)
    try:
        wait.until(lambda d: len(_anchors_in_current_context()) >= 1)
    except TimeoutException:
        print("[WARN] Toujours 0 lien après wait.until → on ré-essaie avec scroll/refresh d’événements")  # Avertissement / Warning / Advertencia
        try:
            driver.execute_script("document.querySelector('#stage-team-stats')?.scrollIntoView({block:'center'});")
            driver.execute_script("window.dispatchEvent(new Event('scroll'));")
            time.sleep(0.5)
        except Exception:
            pass

    # Stabiliser le nombre d’anchors (éviter StaleElement en CI) / Stabilize anchors count (avoid StaleElement in CI) / Estabilizar el número de anchors (evitar StaleElement en CI)
    def _safe_count():
        try:
            return len(_anchors_in_current_context())
        except Exception:
            return 0

    for attempt in range(12):  # ~2.4s max
        n1 = _safe_count()
        time.sleep(0.2)
        n2 = _safe_count()
        print(f"[DEBUG] Stabilisation anchors — essai={attempt+1} / n1={n1} / n2={n2}")  # Debug / Debug / Depuración
        if n2 == n1 and n2 >= min_rows:
            break
        # petit scroll ping / small scroll ping / pequeño ping de scroll
        try:
            driver.execute_script("window.dispatchEvent(new Event('scroll'));")
        except Exception:
            pass

    anchors = _anchors_in_current_context()
    print(f"[INFO] Nombre de liens d’équipes détectés: {len(anchors)}")  # Info / Info / Info
    if not anchors:
        # Sortir proprement du contexte iframe si on y était / Leave iframe context if we were in / Salir del contexto de iframe si estábamos allí
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        raise TimeoutException("Aucun lien d'équipe trouvé.")  # Erreur / Error / Error

    # Préparer l’origine pour les URLs complètes / Prepare origin for absolute URLs / Preparar el origen para URLs absolutas
    try:
        # Revenir au contexte principal pour lire l’URL, puis revenir si nécessaire / Back to main to read URL, then back if needed / Volver al principal para leer URL y luego volver si es necesario
        driver.switch_to.default_content()
    except Exception:
        pass
    parsed = urlparse(driver.current_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    # Si on avait basculé dans une iframe, on y retourne pour lire les éléments / If we had switched into an iframe, go back / Si habíamos cambiado a un iframe, volvemos
    if frame_found:
        try:
            driver.switch_to.frame(frame_found)
        except Exception:
            pass

    results = []
    total = len(anchors)
    for i in range(total):
        # Re-récupérer l’élément à chaque itération (évite StaleElement) / Re-grab element each loop (avoid StaleElement) / Re-obtener el elemento cada iteración (evitar StaleElement)
        try:
            a = _anchors_in_current_context()[i]
        except Exception:
            # Si l’index a changé, reprendre depuis le début / If index changed, refresh list / Si el índice cambió, refrescar lista
            try:
                anchors = _anchors_in_current_context()
                if i >= len(anchors):
                    print(f"[INFO] Index {i} hors bornes après refresh — on continue")  # Info / Info / Info
                    continue
                a = anchors[i]
            except Exception:
                continue

        # Scroll vers l’élément (certains tests headless en ont besoin) / Scroll to element (headless often needs it) / Desplazar al elemento (headless a menudo lo necesita)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
            time.sleep(0.05)
        except Exception:
            pass

        # URL de l’équipe / Team URL / URL del equipo
        try:
            href_raw = (a.get_attribute("href") or a.get_attribute("data-href") or "").strip()
        except Exception:
            href_raw = ""
        href = urljoin(origin, href_raw) if href_raw else ""

        # ID d’équipe / Team ID / ID de equipo
        m = re.search(r"/teams/(\d+)/", href)
        if not m:
            print(f"[SKIP] Anchor #{i+1}/{total}: pas d’ID détecté → href={href!r}")  # Saut / Skip / Omitir
            continue
        try:
            team_id = int(m.group(1))
        except Exception:
            print(f"[SKIP] Anchor #{i+1}/{total}: ID non convertible → href={href!r}")  # Saut / Skip / Omitir
            continue

        # Nom d’équipe (avec fallback) / Team name (with fallback) / Nombre del equipo (con fallback)
        team_name = ""
        for getter in ("text", "innerText", "textContent"):
            try:
                if getter == "text":
                    txt = a.text
                else:
                    txt = a.get_attribute(getter)
                team_name = _clean_team_text(txt or "")
                if team_name:
                    break
            except StaleElementReferenceException:
                try:
                    a = _anchors_in_current_context()[i]
                    txt = a.text if getter == "text" else a.get_attribute(getter)
                    team_name = _clean_team_text(txt or "")
                    if team_name:
                        break
                except Exception:
                    continue
            except Exception:
                continue

        if not team_name:
            team_name = _name_from_href_fallback(href)
            if team_name:
                print(f"[FALLBACK] Nom dérivé de l’URL pour team_id={team_id}: {team_name!r}")  # Secours / Fallback / Recurso
            else:
                print(f"[WARN] Nom introuvable pour team_id={team_id} / href={href!r}")  # Avertissement / Warning / Advertencia

        # Log de l’équipe collectée / Collected team log / Registro de equipo recolectado
        print(f"[OK] Équipe #{i+1}/{total}: id={team_id} | name={team_name!r} | url={href}")  # OK / OK / OK

        results.append({
            "team_id": team_id,
            "team_name": team_name,
            "team_url": href,
        })

    # Déduplication par team_id / Deduplicate by team_id / Deduplciar por team_id
    uniq, seen = [], set()
    for row in results:
        if row["team_id"] not in seen:
            uniq.append(row)
            seen.add(row["team_id"])

    # Sortir proprement d’une iframe si utilisée / Leave iframe cleanly if used / Salir limpiamente del iframe si se usó
    try:
        driver.switch_to.default_content()
    except Exception:
        pass

    print(f"[INFO] Total équipes collectées={len(results)} / uniques={len(uniq)}")  # Récap / Recap / Resumen
    return uniq


# Extraire les 5 meilleurs joueurs de chaque équipe / Pick the top 5 players from each team / Seleccionar a los 5 mejores jugadores de cada equipo
# Extraire les 5 meilleurs joueurs d'une équipe / Extract the team's top 5 players / Extraer los 5 mejores jugadores del equipo
def extract_top5_ratings_from_team(driver, team_url: str, timeout: int = 20) -> dict:
    # On normalise le nom d'équipe / We standardise the team name / Se normaliza el nombre del equipo
    def _clean_name(txt: str) -> str:
        if not txt: return ""
        txt = txt.replace("\xa0", " ")
        txt = re.sub(r"^\s*\d+[\.\)]?\s*", "", txt)
        txt = re.sub(r"\s{2,}", " ", txt)
        return txt.strip()

    print(f"[INFO] TOP5 — navigation vers team_url={team_url!r}")  # Début / Start / Inicio
    # On récupère l'url de l'équipe / We retrieve the team's URL / Recuperamos la URL del equipo
    try:
        try:
            get_with_retries(driver, team_url, tries=2, sleep_s=1.0)  # Navigation robuste / Robust nav / Navegación robusta
            print("[INFO] Navigation OK via get_with_retries")  # Info / Info / Info
        except NameError:
            driver.get(team_url)
            print("[INFO] Navigation OK via driver.get")  # Info / Info / Info
    except Exception as e:
        print(f"[WARN] Échec navigation vers l'équipe: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # Cookies / Cookies / Cookies
    try:
        ok = handle_cookies(driver, accept=False, timeout=2)
        print(f"[INFO] Cookies gérés: {ok}")  # Info / Info / Info
    except Exception as e:
        print(f"[WARN] handle_cookies a échoué: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # On attend le driver et on cherche le tableau des joueurs / We wait for the driver and look for the players' table / Esperamos al driver y buscamos la tabla de jugadores
    wait = WebDriverWait(driver, timeout)

    # Activer l’onglet "Général" si besoin / Activate "General" tab if needed / Activar la pestaña "General" si es necesario
    try:
        wait.until(EC.presence_of_element_located((By.ID, "stage-team-stats")))
        tab = driver.find_element(By.CSS_SELECTOR, '#stage-team-stats-options a[href="#stage-team-stats-summary"]')
        if "selected" not in (tab.get_attribute("class") or ""):
            print("[INFO] Onglet 'Général' non sélectionné → clic()")  # Info / Info / Info
            try:
                tab.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", tab)
            except Exception:
                ActionChains(driver).move_to_element(tab).pause(0.2).click(tab).perform()
        else:
            print("[INFO] Onglet 'Général' déjà actif")  # OK / OK / OK
    except Exception as e:
        print(f"[WARN] Activation onglet 'Général' impossible: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia

    # Scroll pour déclencher le lazy-load / Scroll to trigger lazy-load / Scroll para activar lazy-load
    try:
        driver.execute_script("document.querySelector('#statistics-table-summary')?.scrollIntoView({block:'center'});")
        driver.execute_script("window.dispatchEvent(new Event('scroll'));")
    except Exception:
        pass

    # Helper: présence du corps de table joueurs / Helper: presence of player table body / Helper: presencia del cuerpo de la tabla
    def _player_body():
        try:
            return driver.find_element(By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body")
        except Exception:
            return None

    frame_found = None
    # Tentative dans le document principal / Try in main document / Intento en el documento principal
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body")))
        print("[INFO] Table joueurs trouvée dans le document principal")  # OK / OK / OK
    except TimeoutException:
        print("[INFO] Pas de table joueurs en document principal → on tente les iframes")  # Info / Info / Info
        # Recherche dans les iframes / Search in iframes / Búsqueda en iframes
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
        for fr in frames:
            try:
                driver.switch_to.frame(fr)
                WebDriverWait(driver, max(4, timeout // 2)).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body"))
                )
                frame_found = fr
                print("[INFO] Table joueurs trouvée dans une iframe")  # OK / OK / OK
                break
            except Exception:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
                continue
        # Si trouvée en iframe, se replacer dedans / If found in iframe, switch back / Si se encontró en iframe, volver a entrar
        if frame_found:
            try:
                driver.switch_to.frame(frame_found)
            except Exception as e:
                print(f"[WARN] Re-bascule vers l’iframe impossible: {type(e).__name__}: {e}")  # Avertissement / Warning / Advertencia
        else:
            raise TimeoutException("Impossible de localiser la table des joueurs (#player-table-statistics-body)")  # Erreur / Error / Error

    # Récupération des lignes / Fetch rows / Recuperación de filas
    rows = driver.find_elements(By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body > tr:not(.not-current-player)")
    print(f"[INFO] Lignes joueurs éligibles trouvées: {len(rows)}")  # Info / Info / Info

    if not rows:
        # Sélecteur de secours sans filtre :not(.not-current-player) / Fallback selector without :not(.not-current-player) / Selector de respaldo sin :not(.not-current-player)
        rows = driver.find_elements(By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body > tr")
        print(f"[INFO] Tentative sans filtre not-current-player → {len(rows)} lignes")  # Info / Info / Info

    # Recherche du nom des 5 meilleurs joueurs par équipe (en omettant les joueurs plus au club) / Get top 5 player names per team (skipping non-current) / Buscar los 5 mejores por equipo (omitiendo no actuales)
    names = []
    for idx, tr in enumerate(rows, start=1):
        name = ""
        for sel in ["td.grid-abs a.player-link span.iconize",
                    "td.grid-ghost-cell a.player-link span.iconize",
                    "a.player-link"]:
            try:
                el = tr.find_element(By.CSS_SELECTOR, sel)
                name = _clean_name(el.text or el.get_attribute("textContent") or "")
                if name:
                    break
            except Exception:
                continue
        if name:
            print(f"[OK] Joueur #{idx}: {name}")  # OK / OK / OK
            names.append(name)
            if len(names) == 5:
                break
        else:
            print(f"[SKIP] Ligne #{idx}: nom introuvable")  # Saut / Skip / Omitir

    while len(names) < 5:
        names.append("")

    # Sortie propre d’iframe si utilisée / Cleanly leave iframe if used / Salir limpiamente del iframe si se usó
    if frame_found is not None:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

    print(f"[INFO] TOP5 final = {names}")  # Récap / Recap / Resumen
    return {
        "1st_best_player": names[0],
        "2nd_best_player": names[1],
        "3rd_best_player": names[2],
        "4th_best_player": names[3],
        "5th_best_player": names[4],
    }

# On extrait le nom de la formation type ainsi que les XI type / We extract the name of the typical formation and the typical starting XI / Se extrae el nombre de la formación tipo y el XI tipo
def extract_formation_and_xi_from_team(
    driver,
    team_url: str,
    timeout: int = 20,
    reuse_current: bool = True
) -> dict:
    
    # On récupère la page récupéré précedemment / We retrieve the previously retrieved page / Recuperamos la página recuperada anteriormente
    def _same_page(u1: str, u2: str) -> bool:
        try:
            p1, p2 = urlparse(u1), urlparse(u2)
            return (p1.netloc == p2.netloc) and (p1.path == p2.path)
        except Exception:
            return False
            
    # On récupère la position des joueurs sur le XI type / We retrieve the players' positions on the typical XI / Se recupera la posición de los jugadores en el XI tipo
    def _parse_pos(style: str) -> str:
        # Position sur le XI : ex: "top: 75%; left: 55%;" / Position on the XI: e.g. ‘top: 75%; left: 55%;’ / Posición en el XI: por ejemplo: «top: 75%; left: 55%;»
        if not style:
            return ""
        m_top  = re.search(r"top\s*:\s*([\d\.]+)\s*%",  style, flags=re.I)
        m_left = re.search(r"left\s*:\s*([\d\.]+)\s*%", style, flags=re.I)
        if not (m_top and m_left):
            return ""
        top  = re.sub(r"\.0+$", "", m_top.group(1))
        left = re.sub(r"\.0+$", "", m_left.group(1))
        return f"{top}; {left}"

    # Retrouve l'url de l'équipe si besoin / Find the team's URL if necessary / Busca la URL del equipo si es necesario
    cur = driver.current_url or ""
    if (not reuse_current) or (not _same_page(cur, team_url)):
        driver.get(team_url)
        try:
            handle_cookies(driver, accept=False, timeout=2)
        except Exception:
            pass

    # Attente du driver / Waiting for the driver / Esperando el controlador
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    wait = WebDriverWait(driver, timeout)

    # Cherche la table de la formation / Find the formation table Busca la tabla de formación
    try:
        wait.until(EC.presence_of_element_located((By.ID, "stage-team-stats")))
        tab = driver.find_element(By.CSS_SELECTOR, '#stage-team-stats-options a[href="#stage-team-stats-summary"]')
        if "selected" not in (tab.get_attribute("class") or ""):
            try:
                tab.click()
            except Exception:
                driver.execute_script("arguments[0].click();", tab)
    except Exception:
        pass

    try:
        driver.execute_script("window.scrollTo(0,0);")
        driver.execute_script("document.querySelector('#team-formations')?.scrollIntoView({block:'center'});")
        driver.execute_script("window.dispatchEvent(new Event('scroll'));")
    except Exception:
        pass

    # Attente du chargement de la page / Waiting for page to load / Esperando a que se cargue la página
    try:
        wait.until(EC.presence_of_element_located((By.ID, "team-formations")))
    except TimeoutException:
        # Dernier recours : re-scroll / Last resort: re-scroll / Último recurso: volver a desplazarse
        try:
            driver.execute_script("document.querySelector('#team-formations')?.scrollIntoView({block:'center'});")
        except Exception:
            pass

    # On s'assure qu'on a bien le XI type de la saison / We make sure we have the right starting XI for the season / Nos aseguramos de tener el XI tipo de la temporada
    try:
        saison_btn = driver.find_element(
            By.CSS_SELECTOR,
            '#team-formations-filter-type .listbox.left a.option[data-value="2"]'
        )
        if "selected" not in (saison_btn.get_attribute("class") or ""):
            saison_btn.click()
            time.sleep(0.05)
    except Exception:
        pass 

    # Selectionne la 1ère tactique / Select the first tactic / Selecciona la primera táctica
    formation_type = ""
    try:
        sel_el = driver.find_element(By.CSS_SELECTOR, '#team-formations-filter-formation select.filter-drop')
        select = Select(sel_el)
        if select.options:
            first = select.options[0]
            # Récupère le nom de la formation / Retrieves the name of the formation / Recupera el nombre de la formación.
            formation_type = (first.get_attribute("data-source") or "").strip()
            if not formation_type:
                txt = (first.text or "").strip()
                m = re.match(r"^(\d+)", txt)
                if m:
                    formation_type = m.group(1)
            # On raffraichit la page si besoin / Refresh the page if necessary / Actualiza la página si es necesario.
            if not first.is_selected():
                select.select_by_index(0)
                time.sleep(0.05)
    except Exception:
        pass

    # On s'assure que la liste des joueurs est disponible / We ensure that the list of players is available / Nos aseguramos de que la lista de jugadores esté disponible
    def _ul_count() -> int:
        return len(driver.find_elements(
            By.CSS_SELECTOR,
            "#team-formations-content .team-pitch-formation ul.player-wrapper"
        ))

    for _ in range(4):
        if _ul_count() > 0:
            break
        try:
            driver.execute_script("window.dispatchEvent(new Event('scroll'));")
            driver.execute_script("document.querySelector('#team-formations-content')?.scrollIntoView({block:'center'});")
        except Exception:
            pass
        time.sleep(0.08)

    wait.until(lambda d: _ul_count() > 0)

    # Récupère le nom des 11 joueurs et leur position / Retrieve the names of the 11 players and their positions / Recupera los nombres de los 11 jugadores y su posición
    players_uls = driver.find_elements(
        By.CSS_SELECTOR,
        "#team-formations-content .team-pitch-formation ul.player-wrapper"
    )

    players = []
    for ul in players_uls[:11]:
        # Nom / Name / Nombre
        try:
            name_el = ul.find_element(By.CSS_SELECTOR, "a.player-link.player-name")
            name = (name_el.text or name_el.get_attribute("textContent") or "").strip()
        except Exception:
            name = ""
        # Position / Position / Posición
        pos = _parse_pos(ul.get_attribute("style") or "")
        players.append((name, pos))

    # Compléter si < 11 / Complete if < 11 / Completar si < 11
    while len(players) < 11:
        players.append(("", ""))

    # On ajoute les informations dans les noms de colonnes associés / The information is added to the associated column names / Se añade la información en los nombres de las columnas asociadas
    out = {"formation_type": formation_type}
    ords = ["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th","11th"]
    for i, sfx in enumerate(ords, start=1):
        nm, ps = players[i-1]
        out[f"{sfx}_player_name"] = nm
        out[f"{sfx}_player_position"] = ps
    return out

## Partie pour choisir les saisons à scraper / Off to choose which seasons to scrap / Partida para elegir las temporadas que se van a descartar

# Lecture de la liste de saisons / Reading the list of seasons / Lectura de la lista de temporadas
try:
    from IPython.display import display
except Exception:
    display = print

try:
    DATA_DIR
except NameError:
    DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEASON_CSV = DATA_DIR / "season.csv"
SEASON_COLS = ["country", "championship_name", "season_name", "id_season", "link_url_opta", "link_url_whoscored"]

# Récupération des indices / Recovery of indices / Recuperación de los índices
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
    # Si le fichier n'existe pas, on le crée / If the file does not exist, it is created / Si el archivo no existe, se crea.
    if not path.exists():
        return pd.DataFrame(columns=SEASON_COLS)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in SEASON_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[SEASON_COLS]

# Récupère toutes les saisons disponibles / Collect all available seasons / Recupera todas las temporadas disponibles
def choose_seasons_all(path: Path = SEASON_CSV) -> List[Tuple[int, str, pd.Series]]:
 
    df = _read_season_catalog(path)
    if df.empty:
        raise RuntimeError(
            f"Aucune saison trouvée dans {path}. "
            f"Ajoute des lignes avec colonnes {SEASON_COLS}."
        )

    selections: List[Tuple[int, str, pd.Series]] = []
    for i, row in df.iterrows():
        try:
            id_season = int(row["id_season"])
        except Exception:
            print(f"[WARN] id_season invalide à la ligne {i+1}: {row.get('id_season')!r}")
            continue

        link_url = str(row.get("link_url_whoscored", "")).strip()
        if not link_url:
            print(f"[WARN] link_url_whoscored manquant à la ligne {i+1} pour "
                  f"{row.get('country','?')} — {row.get('championship_name','?')} {row.get('season_name','?')}")
            continue

        print(f"→ Saison {row.get('country','?')} — {row.get('championship_name','?')} "
              f"{row.get('season_name','?')} (id={id_season})")
        selections.append((id_season, link_url, row))

    if not selections:
        raise RuntimeError("Aucune saison exploitable (toutes les lignes étaient invalides/incomplètes).")
    return selections


TEAMS_STATS_OTHER_PATH = DATA_DIR / "teams_stats_other.csv"

# Si teams_stats_other.csv contient déjà des équipes pour id_season, on les charge et on retourne, sinon on scrape les informations associées / If teams_stats_other.csv already contains teams for id_season, we load them and return; otherwise, we scrape the associated information / Si teams_stats_other.csv ya contiene equipos para id_season, los cargamos y los devolvemos; de lo contrario, extraemos la información asociada
def ensure_df_teams_for_season(driver, id_season: int, _row: pd.Series,
                               path: Path = TEAMS_STATS_OTHER_PATH) -> pd.DataFrame:
    id_season_str = str(id_season)

    # Si on a déjà les données, on ne change pas / If we already have the data, we don't change it / Si ya tenemos los datos, no cambiamos nada
    if path.exists():
        df_all = pd.read_csv(path, dtype=str, keep_default_na=False)
        if "id_season" in df_all.columns and (df_all["id_season"] == id_season_str).any():
            df_season = df_all[df_all["id_season"] == id_season_str].copy()
            if "team_id" in df_season.columns:
                df_season["team_id"] = pd.to_numeric(df_season["team_id"], errors="coerce").astype("Int64")
            print(f"[INFO] Saison {id_season_str} déjà présente dans le fichier ({len(df_season)} équipes) → pas de scraping.")  # Saison déjà prise / Season already handled / Temporada ya registrada
            return df_season.reset_index(drop=True)
    else:
        df_all = pd.DataFrame(columns=["id_season","season_name","country","championship_name","team_id","team_name","team_url"])  # Fichier absent → DF vide / File missing → empty DF / Archivo ausente → DF vacío

    # Sinon on scrape les données / Otherwise we scrape the data / Si no, recopilamos los datos
    teams_info = extract_team_basic_info_from_summary(driver, timeout=10)

    df_season = pd.DataFrame(teams_info)
    # On spécifie la recherche sur l'identifiant, le nom et l'url de l'équipe / We ensure id, name and url columns exist / Nos aseguramos de que existan id, nombre y url
    for c in ["team_id", "team_name", "team_url"]:
        if c not in df_season.columns:
            df_season[c] = ""
    df_season["team_id"] = pd.to_numeric(df_season["team_id"], errors="coerce").astype("Int64")

    # On ajoute les informations de la saison et du championnat / Add season and competition info / Añadimos la temporada y la competición
    df_season.insert(0, "id_season", id_season_str)
    df_season.insert(1, "season_name", _row.get("season_name"))
    df_season.insert(2, "country", _row.get("country"))
    df_season.insert(3, "championship_name", _row.get("championship_name"))

    if "team_id" in df_all.columns:
        existing_global_ids = set(pd.to_numeric(df_all["team_id"], errors="coerce").astype("Int64").dropna().astype(int).tolist())
    else:
        existing_global_ids = set()

    for _, r in df_season.iterrows():
        tid = r.get("team_id")
        tname = r.get("team_name", "")
        if pd.notna(tid) and int(tid) in existing_global_ids:
            print(f"[INFO] Équipe déjà dans le fichier (toutes saisons) : {tname} (id={tid})")  # Déjà présente / Already present / Ya presente
        else:
            print(f"[INFO] Nouvelle équipe à ajouter : {tname} (id={tid})")  # Nouvelle entrée / New entry / Nueva entrada

    # On ajoute cela dans le fichier / Append to CSV / Añadir al CSV
    if path.exists():
        df_all = pd.read_csv(path, dtype=str, keep_default_na=False)
    else:
        df_all = pd.DataFrame(columns=df_season.columns)

    # On harmonise les colonnes / Harmonize columns / Armonizar columnas
    for c in df_season.columns:
        if c not in df_all.columns: df_all[c] = ""
    for c in df_all.columns:
        if c not in df_season.columns: df_season[c] = ""

    before = len(df_all)  # Lignes avant concat / Rows before concat / Filas antes de concatenar
    df_all = pd.concat([df_all, df_season], ignore_index=True)
    df_all["id_season"] = df_all["id_season"].astype(str)
    df_all["team_id"] = pd.to_numeric(df_all["team_id"], errors="coerce").astype("Int64")
    df_all = df_all.drop_duplicates(subset=["id_season","team_id"], keep="last").reset_index(drop=True)
    df_all.to_csv(path, index=False)
    print(f"[INFO] CSV mis à jour : {path} (lignes avant={before}, après dédup={len(df_all)})")  # Récap écriture / Write recap / Resumen de escritura

    return df_season.reset_index(drop=True)


# Fonction main / Function main / Función main
def run_scrape_whoscored(headed: bool = True):
    # Sélection des saisons / Season selection / Selección de temporadas
    selections = choose_seasons_all()
    if not selections:
        print("Aucune saison à scraper, arrêt.")
        return

    # Driver / Driver / Controlador
    try:
        driver = make_driver(headed=headed)
    except NameError:
        chrome_options = Options()
        if not headed:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1366,900")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=chrome_options)

    try:
        for (id_season, season_url, _row) in selections:
            print("\n" + "=" * 70)
            print(f"Scraping saison {id_season} → {season_url}")
            print("=" * 70)

            try:

                # Ouvrir la page de saison / Open season page / Abrir la página de la temporada de forma robusta
                get_with_retries(driver, season_url, tries=3, sleep_s=2.0)
                time.sleep(0.5)

                # Gérer les cookies / Handle cookies / Gestionar cookies
                handle_cookies(driver, accept=False, timeout=10)
                print("Page des Cookies fermée")

                # Cliquer l’onglet / Click the tab / Hacer clic en la pestaña
                click_team_statistics(driver, timeout=20)

                # Récupération (ou chargement) des équipes pour la saison / Recovery (or loading) of teams for the season / Recuperación (o carga) de los equipos para la temporada
                df_teams = ensure_df_teams_for_season(
                    driver, id_season, _row, path=DATA_DIR / "teams_stats_other.csv"
                )

                # Pour chaque équipe : on récupère le Top5 + Formation/XI / For each team: we collect the Top 5 + Line-up/XI / Para cada equipo: se recupera el Top 5 + Formación/XI.
                rows_out = []
                ords = ["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th","11th"]
                top5_keys = ["1st_best_player","2nd_best_player","3rd_best_player","4th_best_player","5th_best_player"]

                for _, r in df_teams.iterrows():
                    team_url = r["team_url"]

                    # TOP 5 / TOP 5 / TOP 5
                    try:
                        top5 = extract_top5_ratings_from_team(driver, team_url, timeout=8)
                    except Exception as e:
                        print(f"[WARN] top5: {r.get('team_name','?')}: {type(e).__name__}: {e}")
                        top5 = {k: "" for k in top5_keys}

                    # FORMATION + XI / Line-up + XI / Formación/XI
                    try:
                        xi = extract_formation_and_xi_from_team(driver, team_url, timeout=8, reuse_current=True)
                    except Exception as e:
                        print(f"[WARN] formation/XI: {r.get('team_name','?')}: {type(e).__name__}: {e}")
                        xi = {"formation_type": ""}
                        for sfx in ords:
                            xi[f"{sfx}_player_name"] = ""
                            xi[f"{sfx}_player_position"] = ""

                    row_out = {**r.to_dict(), **top5, **xi}
                    rows_out.append(row_out)

                    # Vérification / Verification / Verificación
                    top5_full = all(row_out[k] for k in top5_keys)
                    xi_full = bool(row_out.get("formation_type")) and all(
                        row_out[f"{s}_player_name"] and row_out[f"{s}_player_position"] for s in ords
                    )
                    print(f"✔ OK — {row_out.get('team_name','?')}" if (top5_full and xi_full)
                          else f"✖ Incomplet — {row_out.get('team_name','?')}")

                    time.sleep(0.02)

                df_out = pd.DataFrame(rows_out)

                # Sauvegarde / Save / Copia de seguridad
                csv_path = DATA_DIR / "teams_stats_other.csv"
                if csv_path.exists():
                    all_prev = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
                else:
                    all_prev = pd.DataFrame(columns=df_out.columns)

                for c in df_out.columns:
                    if c not in all_prev.columns: all_prev[c] = ""
                for c in all_prev.columns:
                    if c not in df_out.columns: df_out[c] = ""

                all_cat = pd.concat([all_prev, df_out], ignore_index=True)
                all_cat["id_season"] = all_cat["id_season"].astype(str)
                all_cat["team_id"] = pd.to_numeric(all_cat["team_id"], errors="coerce").astype("Int64")
                all_cat = all_cat.drop_duplicates(subset=["id_season", "team_id"], keep="last").reset_index(drop=True)
                all_cat.to_csv(csv_path, index=False)
                print(f"→ Mise à jour écrite dans {csv_path}")

            except Exception as e:
                print(f"[WARN] Échec sur la saison {id_season}: {type(e).__name__}: {e}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass



# Execution du web scraping pour la saison de son choix / Execution of web scraping for the season of your choice / Ejecución del web scraping para la temporada que elija
if __name__ == "__main__":
    run_scrape_whoscored(headed=False)
