"""
scrape_understat.py — Understat players + teams stats scraper.

Data is loaded dynamically by JavaScript — uses SeleniumBase to render
the page and extract window.playersData and window.teamsData.

Leagues: EPL, La Liga, Bundesliga, Serie A, Ligue 1, RFPL

Player stats: apps, minutes, goals, npg, assists, shots, key_passes,
              yellow_cards, red_cards, xG, npxG, xA, xGChain, xGBuildup
              + per-90: xG90, npxG90, xA90, xG90+xA90,
                npxG90+xA90, xGChain90, xGBuildup90

Team stats:   matches, wins, draws, losses, goals, goals_against, pts,
              xG, xGA, npxG, npxGA, ppda, oppda, deep, deep_allowed

Output:
    data/understat_players.csv
    data/understat_teams.csv

Usage:
    py scrape_understat.py
    py scrape_understat.py --season 2023
"""

import os, sys, json, time, argparse
import pandas as pd
from seleniumbase import SB

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT_DIR  = os.path.join(os.path.dirname(__file__), 'data')
OUT_PLAYERS = os.path.join(OUT_DIR, 'understat_players.csv')
OUT_TEAMS   = os.path.join(OUT_DIR, 'understat_teams.csv')
os.makedirs(OUT_DIR, exist_ok=True)

LEAGUES = [
    {'slug': 'EPL',        'name': 'Premier League'},
    {'slug': 'La_liga',    'name': 'La Liga'},
    {'slug': 'Bundesliga', 'name': 'Bundesliga'},
    {'slug': 'Serie_A',    'name': 'Serie A'},
    {'slug': 'Ligue_1',    'name': 'Ligue 1'},
    {'slug': 'RFPL',       'name': 'Russian Premier League'},
]


# ── Type helpers ───────────────────────────────────────────────────────────────
def _int(v):
    try:    return int(v)
    except: return None


def _float(v):
    try:    return round(float(v), 4)
    except: return None


# ── Players ────────────────────────────────────────────────────────────────────
def build_players_df(players, league_name, season):
    rows = []
    for p in players:
        mins = _int(p.get('time')) or 0

        xG        = _float(p.get('xG'))
        npxG      = _float(p.get('npxG'))
        xA        = _float(p.get('xA'))
        xGChain   = _float(p.get('xGChain'))
        xGBuildup = _float(p.get('xGBuildup'))

        def per90(v):
            if v is None or mins < 1: return None
            return round(v / mins * 90, 4)

        xG90        = per90(xG)
        npxG90      = per90(npxG)
        xA90        = per90(xA)
        xGChain90   = per90(xGChain)
        xGBuildup90 = per90(xGBuildup)

        row = {
            'season':         season,
            'league':         league_name,
            'name':           p.get('player_name', ''),
            'team':           p.get('team_title', ''),
            'position':       p.get('position', ''),
            'apps':           _int(p.get('games')),
            'minutes':        mins if mins else None,
            'goals':          _int(p.get('goals')),
            'npg':            _int(p.get('npg')),
            'assists':        _int(p.get('assists')),
            'shots':          _int(p.get('shots')),
            'key_passes':     _int(p.get('key_passes')),
            'yellow_cards':   _int(p.get('yellow_cards')),
            'red_cards':      _int(p.get('red_cards')),
            'xG':             xG,
            'npxG':           npxG,
            'xA':             xA,
            'xGChain':        xGChain,
            'xGBuildup':      xGBuildup,
            'xG90':           xG90,
            'npxG90':         npxG90,
            'xA90':           xA90,
            'xG90_xA90':      round((xG90 or 0) + (xA90 or 0), 4) if (xG90 is not None or xA90 is not None) else None,
            'npxG90_xA90':    round((npxG90 or 0) + (xA90 or 0), 4) if (npxG90 is not None or xA90 is not None) else None,
            'xGChain90':      xGChain90,
            'xGBuildup90':    xGBuildup90,
        }
        rows.append(row)
    return pd.DataFrame(rows)


# ── Teams ──────────────────────────────────────────────────────────────────────
def build_teams_df(teams_data, league_name, season):
    """
    teams_data is window.teamsData: a dict keyed by team name.
    Each value has 'title', 'id', and 'history' (list of match dicts).
    We aggregate the history to season totals.
    """
    rows = []
    for team_key, team in teams_data.items():
        history = team.get('history', [])
        if not history:
            continue

        matches      = len(history)
        wins         = sum(1 for m in history if m.get('wins') == 1 or m.get('result') == 'w')
        draws        = sum(1 for m in history if m.get('draws') == 1 or m.get('result') == 'd')
        losses       = sum(1 for m in history if m.get('loses') == 1 or m.get('result') == 'l')
        goals        = sum(_int(m.get('scored', 0)) or 0 for m in history)
        goals_against= sum(_int(m.get('missed', 0)) or 0 for m in history)
        pts          = wins * 3 + draws

        def sum_f(key):
            vals = [_float(m.get(key)) for m in history]
            vals = [v for v in vals if v is not None]
            return round(sum(vals), 4) if vals else None

        xG           = sum_f('xG')
        xGA          = sum_f('xGA')
        npxG         = sum_f('npxG')
        npxGA        = sum_f('npxGA')
        deep         = sum_f('deep')
        deep_allowed = sum_f('deep_allowed')

        # ppda: passes per defensive action (lower = more pressing)
        # stored per match; average the ratio correctly via aggregating att/def counts
        ppda_att  = sum(_float(m.get('ppda', {}).get('att', 0)) or 0 for m in history if isinstance(m.get('ppda'), dict))
        ppda_def  = sum(_float(m.get('ppda', {}).get('def', 0)) or 0 for m in history if isinstance(m.get('ppda'), dict))
        oppda_att = sum(_float(m.get('ppda_allowed', {}).get('att', 0)) or 0 for m in history if isinstance(m.get('ppda_allowed'), dict))
        oppda_def = sum(_float(m.get('ppda_allowed', {}).get('def', 0)) or 0 for m in history if isinstance(m.get('ppda_allowed'), dict))

        ppda  = round(ppda_att  / ppda_def,  4) if ppda_def  > 0 else None
        oppda = round(oppda_att / oppda_def, 4) if oppda_def > 0 else None

        row = {
            'season':        season,
            'league':        league_name,
            'team':          team.get('title', team_key),
            'matches':       matches,
            'wins':          wins,
            'draws':         draws,
            'losses':        losses,
            'goals':         goals,
            'goals_against': goals_against,
            'pts':           pts,
            'xG':            xG,
            'xGA':           xGA,
            'npxG':          npxG,
            'npxGA':         npxGA,
            'xGD':           round((xG or 0) - (xGA or 0), 4) if (xG is not None and xGA is not None) else None,
            'npxGD':         round((npxG or 0) - (npxGA or 0), 4) if (npxG is not None and npxGA is not None) else None,
            'ppda':          ppda,
            'oppda':         oppda,
            'deep':          deep,
            'deep_allowed':  deep_allowed,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values('pts', ascending=False).reset_index(drop=True)
    return df


# ── Wait helpers ───────────────────────────────────────────────────────────────
def wait_for_js_var(sb, var_name, timeout=20):
    """Wait until a JS variable is a non-empty object/array."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            count = sb.execute_script(
                f'var d = window.{var_name};'
                f'if (!d) return 0;'
                f'if (Array.isArray(d)) return d.length;'
                f'return Object.keys(d).length;'
            )
            if count and count > 0:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--season', type=int, default=2024,
                        help='Season start year (default: 2024 = 2024/25)')
    args = parser.parse_args()

    all_players = []
    all_teams   = []

    with SB(uc=True, headless=True, page_load_strategy='eager') as sb:
        for league in LEAGUES:
            url = f"https://understat.com/league/{league['slug']}/{args.season}"
            print(f"\n[{league['name']}] {url}")
            try:
                sb.open(url)

                # Wait for players data
                found_players = wait_for_js_var(sb, 'playersData', timeout=20)
                if not found_players:
                    print("  playersData not ready, reloading...")
                    sb.driver.refresh()
                    found_players = wait_for_js_var(sb, 'playersData', timeout=20)

                # Wait for teams data
                found_teams = wait_for_js_var(sb, 'teamsData', timeout=20)

                # Players
                if found_players:
                    raw = sb.execute_script('return JSON.stringify(window.playersData)')
                    players = json.loads(raw)
                    print(f"  {len(players)} players")
                    df_p = build_players_df(players, league['name'], args.season)
                    all_players.append(df_p)
                else:
                    print("  No playersData found, skipping players")

                # Teams
                if found_teams:
                    raw = sb.execute_script('return JSON.stringify(window.teamsData)')
                    teams = json.loads(raw)
                    print(f"  {len(teams)} teams")
                    df_t = build_teams_df(teams, league['name'], args.season)
                    all_teams.append(df_t)
                else:
                    print("  No teamsData found, skipping teams")

                # Save incrementally after each league
                if all_players:
                    pd.concat(all_players, ignore_index=True).to_csv(
                        OUT_PLAYERS, index=False, encoding='utf-8-sig')
                if all_teams:
                    pd.concat(all_teams, ignore_index=True).to_csv(
                        OUT_TEAMS, index=False, encoding='utf-8-sig')
                print(f"  Saved incrementally")

            except Exception as e:
                print(f"  Error: {e}")

            time.sleep(1)

    print("\n=== DONE ===")
    if all_players:
        final_p = pd.concat(all_players, ignore_index=True)
        final_p.to_csv(OUT_PLAYERS, index=False, encoding='utf-8-sig')
        print(f"Players: {len(final_p)} rows -> {OUT_PLAYERS}")
        print(final_p.groupby('league').size().to_string())
    else:
        print("No player data collected.")

    if all_teams:
        final_t = pd.concat(all_teams, ignore_index=True)
        final_t.to_csv(OUT_TEAMS, index=False, encoding='utf-8-sig')
        print(f"\nTeams: {len(final_t)} rows -> {OUT_TEAMS}")
        print(final_t.groupby('league').size().to_string())
    else:
        print("No team data collected.")


if __name__ == '__main__':
    main()
