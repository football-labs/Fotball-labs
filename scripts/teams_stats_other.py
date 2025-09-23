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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def make_driver(headed: bool = True) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1366,900")
    chrome_options.page_load_strategy = "eager"

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if not headed:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--lang=fr-FR")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

    try:
        if headed:
            drv = webdriver.Chrome(options=chrome_options)
        else:
            import undetected_chromedriver as uc
            drv = uc.Chrome(options=chrome_options, headless=True)
    except Exception:
        drv = webdriver.Chrome(options=chrome_options)

    try:
        drv.execute_cdp_cmd("Network.enable", {})
        drv.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
        })
        drv.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/Paris"})
        drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = window.chrome || { runtime: {} };
                Object.defineProperty(navigator, 'language', {get: () => 'fr-FR'});
                Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR','fr']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
                try { localStorage.setItem('cookie_consent','1'); } catch(e){}
                try { document.cookie='cookie_consent=1; Path=/; Max-Age='+(60*60*24*365)+'; SameSite=Lax'; } catch(e){}
            """
        })
    except Exception:
        pass

    drv.set_page_load_timeout(60)
    drv.set_script_timeout(60)
    return drv



# Bloque les pages de cookies sur toute la durée du driver
def seed_domain_consent(driver):
    print("[cookies] seeding domain consent at site root…")
    start_url = driver.current_url
    root = "https://fr.whoscored.com/"

    try:
        # Aller à la racine du domaine pour s'assurer du bon scope d'origine
        driver.get(root)
        # court délais pour que le document soit prêt
        time.sleep(0.2)

        # Poser un flag simple côté navigateur
        driver.execute_script("""
            try { localStorage.setItem('cookie_consent', '1'); } catch(e) {}

            // Cookie 'host-only' (fr.whoscored.com) valable 1 an
            try {
                document.cookie = [
                    'cookie_consent=1',
                    'Path=/',
                    'Max-Age=' + (60*60*24*365),
                    'SameSite=Lax'
                ].join('; ');
            } catch(e) {}
        """)

        print("[cookies] seed done on site root")
    except Exception as e:
        print("[cookies] seed error:", e)
    finally:
        # Revenir où on était si nécessaire
        try:
            if start_url and start_url != root:
                driver.get(start_url)
                time.sleep(0.2)
        except Exception as e:
            print("[cookies] return-to-start error:", e)


# Fermeture de la page des cookies / Closing the cookies page / Cierre de la página de cookies
def handle_cookies(driver, accept: bool = True, timeout: int = 8) -> bool:

    def overlay_present() -> bool:
        js = r"""
        const doc=document;
        const text = (doc.body && doc.body.innerText || '').toLowerCase();
        const hasTxt = text.includes('nous respectons votre vie privée')
                    || text.includes('consentez-vous')
                    || (text.includes('cookies') && text.includes('partenaires'));
        const overlays = Array.from(doc.querySelectorAll('div,section,aside,dialog'))
          .filter(el=>{
            const st=getComputedStyle(el); if(!st) return false;
            const zi=parseInt(st.zIndex)||0, op=parseFloat(st.opacity||'1');
            const pos=st.position, w=el.offsetWidth, h=el.offsetHeight;
            return (pos==='fixed'||pos==='sticky') && zi>=1000 && op>0.01 && w>200 && h>100;
          });
        return hasTxt || overlays.length>0;
        """
        try:
            return bool(driver.execute_script(js))
        except Exception:
            return False

    end = time.time() + 1.0
    while time.time() < end:
        time.sleep(0.05)

    start_url = driver.current_url

    def click_accept_in_banner() -> bool:
        # Ne clique que le bouton dans le conteneur “vie privée”
        js = r"""
        function findPrivacyBanner(doc){
          const nodes = Array.from(doc.querySelectorAll('div,section,dialog'));
          for (const el of nodes){
            const t = (el.innerText||'').toLowerCase();
            if (!t) continue;
            if (t.includes('nous respectons votre vie privée')) return el;
          }
          return null;
        }
        function preventAllNav(banner){
          if (!banner) return;
          banner.addEventListener('click', (ev)=>{
            // neutralise toute navigation/lien dans la bannière
            if (ev.target && ev.target.closest('a')) {
              ev.preventDefault(); ev.stopPropagation();
              return false;
            }
          }, {capture:true, passive:false});
          const links = banner.querySelectorAll('a');
          links.forEach(a=>{
            a.addEventListener('click',(ev)=>{ev.preventDefault(); ev.stopPropagation(); return false;},
                               {capture:true, passive:false});
          });
        }
        function clickNode(n){
          try { n.click(); return true; }
          catch(e){
            try{
              n.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true}));
              n.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,cancelable:true}));
              n.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
              return true;
            }catch(e2){ return false; }
          }
        }

        const banner = findPrivacyBanner(document);
        if (!banner) return {ok:false, reason:'no-banner'};

        // on ne considère QUE des <button> dans la bannière
        const btns = Array.from(banner.querySelectorAll('button'));
        const wanted = (el)=>{
          const t=(el.innerText||el.textContent||'').trim().toLowerCase();
          return t==='tout accepter' || /\btout\s+accepter\b/.test(t) || t==='accepter' || t==='accept';
        };
        const matches = btns.filter(wanted);

        if (!matches.length) {
          return {ok:false, reason:'no-accept-button'};
        }

        // empêche toute navigation dans la bannière avant clic
        preventAllNav(banner);

        // clique le premier match
        const ok = clickNode(matches[0]);
        return {ok: !!ok, reason: ok?'clicked':'click-failed'};
        """
        try:
            res = driver.execute_script(js)
            return bool(res and res.get("ok"))
        except Exception:
            return False

    def fallback_hide_and_flag():
        # Masque/retire la bannière & overlays + pose un consent flag
        js = r"""
        (function(){
          let removed=0;
          const doc=document;
          // bannière “vie privée”
          const nodes = Array.from(doc.querySelectorAll('div,section,dialog'));
          for (const el of nodes){
            const t=(el.innerText||'').toLowerCase();
            if (t && (t.includes('nous respectons votre vie privée') || (t.includes('cookies') && t.includes('partenaires')))){
              try{ el.style.display='none'; el.style.opacity='0'; el.remove&&el.remove(); removed++; }catch(e){}
            }
          }
          // overlays “plein écran”
          const overlays = Array.from(doc.querySelectorAll('div,section,aside,dialog')).filter(el=>{
            const st=getComputedStyle(el); if(!st) return false;
            const zi=parseInt(st.zIndex)||0, op=parseFloat(st.opacity||'1');
            const pos=st.position, w=el.offsetWidth, h=el.offsetHeight;
            return (pos==='fixed'||pos==='sticky') && zi>=1000 && op>0.01 && w>200 && h>100;
          });
          for (const el of overlays.slice(0,8)){
            try{ el.style.display='none'; el.style.opacity='0'; el.remove&&el.remove(); removed++; }catch(e){}
          }
          try { localStorage.setItem('cookie_consent','1'); } catch(e){}
          try { document.cookie='cookie_consent=1; Path=/; Max-Age='+(60*60*24*365)+'; SameSite=Lax'; } catch(e){}
          return removed;
        })();
        """
        try:
            driver.execute_script(js)
        except Exception:
            pass

    # 1) si rien à faire ou accept=False, on saute le clic et on se contente du fallback si overlay détecté
    if accept:
        # tente un clic STRICT dans la bannière
        clicked = click_accept_in_banner()
        # laisse 300ms pour que la modale se retire
        time.sleep(0.3)

        # si redirection, on revient en arrière et on bascule fallback
        cur = driver.current_url or ""
        if cur != start_url and "/accounts/" in cur:
            try:
                driver.back()
                time.sleep(0.4)
            except Exception:
                pass
            fallback_hide_and_flag()
        elif overlay_present():
            # si la bannière est encore là, on ne clique plus : fallback direct
            fallback_hide_and_flag()
    else:
        # pas de clic en mode refuse ; si overlay, fallback direct
        if overlay_present():
            fallback_hide_and_flag()

    # 2) vérif finale : tant que overlay détecté, on attend un peu (sans s’obstiner)
    deadline = time.time() + max(0.8, timeout/2)
    while time.time() < deadline:
        if not overlay_present():
            return True
        time.sleep(0.1)

    # on renvoie True pour ne pas bloquer le scraping ; le fallback a normalement neutralisé l’overlay
    return True


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
                    ".//a[normalize-space()='Statistiques des Équipes' or contains(., 'Team Statistics') or contains(., 'Estadísticas de los equipos')]"
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
        return

    # Essai dans les iframes / Try inside iframes / Intentar dentro de iframes
    frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
    for fr in frames:
        try:
            driver.switch_to.frame(fr)
            if _click_link_in(driver):
                driver.switch_to.default_content()
                wait.until(_on_team_stats)
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
                stage_id = parts[i+1]
                base_parts = parts[:i+2]
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

    raise TimeoutException(f"Impossible d'ouvrir l'onglet Statistiques des Équipes depuis {cur}")



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
def extract_team_basic_info_from_summary(driver, timeout: int = 20, min_rows: int = 8):
    # Attente du driver / Waiting for the driver / Esperando el controlador
    wait = WebDriverWait(driver, timeout)

    # S'assurer que l’onglet "Général" est actif / Ensure that the ‘General’ tab is active / Asegúrese de que la pestaña «General» esté activa
    wait.until(EC.presence_of_element_located((By.ID, "stage-team-stats")))
    try:
        summary_tab = driver.find_element(By.CSS_SELECTOR, '#stage-team-stats-options a[href="#stage-team-stats-summary"]')
        if "selected" not in (summary_tab.get_attribute("class") or ""):
            summary_tab.click()
    except Exception:
        pass

    # Attendre que des lignes soient présentes / Wait until lines are present / Esperar a que haya líneas
    def _anchors():
        return driver.find_elements(By.CSS_SELECTOR, "#top-team-stats-summary-content a.team-link")

    wait.until(lambda d: len(_anchors()) >= 1)
    for _ in range(10):
        n1 = len(_anchors())
        time.sleep(0.2)
        n2 = len(_anchors())
        if n2 == n1 and n2 >= min_rows:
            break

    anchors = _anchors()
    if not anchors:
        raise TimeoutException("Aucun lien d'équipe trouvé.")

    parsed = urlparse(driver.current_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    results = []
    for i in range(len(anchors)):
        # Re-récupérer l'élément à chaque itération / Retrieve the element again at each iteration / Recuperar el elemento en cada iteración
        try:
            a = _anchors()[i]
        except Exception:
            # Si l’index a changé, reprendre depuis le début / If the index has changed, start again from the beginning / Si el índice ha cambiado, volver a empezar desde el principio
            anchors = _anchors()
            if i >= len(anchors):
                continue
            a = anchors[i]
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
            time.sleep(0.05)
        except Exception:
            pass

        # Récupèration de l'URL / URL retrieval / Recuperación de la URL
        href_raw = (a.get_attribute("href") or a.get_attribute("data-href") or "").strip()
        href = urljoin(origin, href_raw)

        # ID d'équipe / Team ID / ID del equipo
        m = re.search(r"/teams/(\d+)/", href)
        if not m:
            # Si pas d'ID, ignorer la ligne / If no ID, skip the line / Si no hay ID, ignorar la línea
            continue
        team_id = int(m.group(1))

        # Récupération du Nom d'équipe / Recovering the Team Name / Recuperación del nombre del equipo
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
                    a = _anchors()[i]
                    if getter == "text":
                        txt = a.text
                    else:
                        txt = a.get_attribute(getter)
                    team_name = _clean_team_text(txt or "")
                    if team_name:
                        break
                except Exception:
                    continue
            except Exception:
                continue

        if not team_name:
            # Récupèrer le nom d'équipe depuis l'url si cela n'a pas été fait auparavant / Retrieve the team name from the URL if this has not been done previously / Recuperar el nombre del equipo desde la URL si no se ha hecho anteriormente
            team_name = _name_from_href_fallback(href)

        results.append({
            "team_id": team_id,
            "team_name": team_name,
            "team_url": href,
        })

    # Enlever doublons si besoin / Remove duplicates if necessary / Eliminar duplicados si es necesario
    uniq, seen = [], set()
    for row in results:
        if row["team_id"] not in seen:
            uniq.append(row)
            seen.add(row["team_id"])

    return uniq

# Extraire les 5 meilleurs joueurs de chaque équipe / Pick the top 5 players from each team / Seleccionar a los 5 mejores jugadores de cada equipo
def extract_top5_ratings_from_team(driver, team_url: str, timeout: int = 20) -> dict:
    # On normalise le nom d'équipe / We standardise the team name / Se normaliza el nombre del equipo
    def _clean_name(txt: str) -> str:
        if not txt: return ""
        txt = txt.replace("\xa0", " ")
        txt = re.sub(r"^\s*\d+[\.\)]?\s*", "", txt)
        txt = re.sub(r"\s{2,}", " ", txt)
        return txt.strip()

    # On récupère l'url de l'équipe / We retrieve the team's URL / Recuperamos la URL del equipo.
    driver.get(team_url)
    print("webdriver =", driver.execute_script("return navigator.webdriver"))
    print("lang =", driver.execute_script("return navigator.language"))
    print("plugins =", driver.execute_script("return navigator.plugins && navigator.plugins.length"))
    print("rows top5 =", len(driver.find_elements(By.CSS_SELECTOR,
        "#top-player-stats-summary-grid #player-table-statistics-body > tr:not(.not-current-player)")))

    try:
        handle_cookies(driver, accept=True, timeout=10)
    except Exception:
        pass

    # On attend le driver et on cherche le tableau des joueurs / We wait for the driver and look for the players' table / Esperamos al conductor y buscamos la tabla de jugadores
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "stage-team-stats")))
        tab = driver.find_element(By.CSS_SELECTOR, '#stage-team-stats-options a[href="#stage-team-stats-summary"]')
        if "selected" not in (tab.get_attribute("class") or ""):
            try: tab.click()
            except Exception: driver.execute_script("arguments[0].click();", tab)
    except Exception:
        pass

    try:
        driver.execute_script("document.querySelector('#statistics-table-summary')?.scrollIntoView({block:'center'});")
    except Exception:
        pass

    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#top-player-stats-summary-grid #player-table-statistics-body"))
    )

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#top-player-stats-summary-grid #player-table-statistics-body > tr:not(.not-current-player)"
    )

    # Recherche du nom des 5 meilleurs joueurs par équipe en omettant les joueurs plus au club / Search for the names of the top 5 players per team, excluding players who are no longer with the club / Buscar los nombres de los 5 mejores jugadores por equipo, omitiendo a los jugadores que ya no están en el club
    names = []
    for tr in rows:
        name = ""
        for sel in ["td.grid-abs a.player-link span.iconize",
                    "td.grid-ghost-cell a.player-link span.iconize",
                    "a.player-link"]:
            try:
                name = tr.find_element(By.CSS_SELECTOR, sel).text
                break
            except Exception:
                continue
        name = _clean_name(name)
        if name:
            names.append(name)
            if len(names) == 5:
                break
    while len(names) < 5: names.append("")
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
            handle_cookies(driver, accept=True, timeout=10)
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
            return df_season.reset_index(drop=True)

    # Sinon on scrape les données / Si no, recopilamos los datos
    teams_info = extract_team_basic_info_from_summary(driver, timeout=10)

    df_season = pd.DataFrame(teams_info)
    # On spécifie la recherche sur les informations sur l'identifiant, le nom et l'url de l'équipe / We specify the search for information on the team's ID, name and URL / Se especifica la búsqueda de información sobre el identificador, el nombre y la URL del equipo
    for c in ["team_id", "team_name", "team_url"]:
        if c not in df_season.columns:
            df_season[c] = ""
    df_season["team_id"] = pd.to_numeric(df_season["team_id"], errors="coerce").astype("Int64")

    # On ajoute les informations de la saison et du championnat / Add the season and championship information / Se añade la información sobre la temporada y el campeonato
    df_season.insert(0, "id_season", id_season_str)
    df_season.insert(1, "season_name", _row.get("season_name"))
    df_season.insert(2, "country", _row.get("country"))
    df_season.insert(3, "championship_name", _row.get("championship_name"))

    # On ajoute cela dans le fichier / Add this to the file / Añadimos esto al archivo
    if path.exists():
        df_all = pd.read_csv(path, dtype=str, keep_default_na=False)
    else:
        df_all = pd.DataFrame(columns=df_season.columns)

    # On harmonise les colonnes / We harmonise the columns / Se armonizan las columnas
    for c in df_season.columns:
        if c not in df_all.columns: df_all[c] = ""
    for c in df_all.columns:
        if c not in df_season.columns: df_season[c] = ""

    df_all = pd.concat([df_all, df_season], ignore_index=True)
    df_all["id_season"] = df_all["id_season"].astype(str)
    df_all["team_id"] = pd.to_numeric(df_all["team_id"], errors="coerce").astype("Int64")
    df_all = df_all.drop_duplicates(subset=["id_season","team_id"], keep="last").reset_index(drop=True)
    df_all.to_csv(path, index=False)

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
                
                seed_domain_consent(driver)
                
                # Gérer les cookies / Handle cookies / Gestionar cookies
                handle_cookies(driver, accept=True, timeout=10)
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
