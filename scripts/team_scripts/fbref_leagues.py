import pandas as pd

## Configuración general de pandas ## General pandas configuration ## Configuration générale de pandas
pd.options.display.max_columns = 500


def load_dataframes() -> dict:
    """
    ## Cargar todos los CSV originales y renombrar columnas ##
    ## Load all original CSVs and rename columns ##
    ## Charger tous les CSV originaux et renommer les colonnes ##
    """

    # ---------- Standard ----------
    df_standard = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Stardard.csv")
    df_standard.columns = [
        "rk","squad","comp","players","age","poss",
        "playing_time_mp","playing_time_starts","playing_time_min","playing_time_90s",
        "performance_gls","performance_ast","performance_g_plus_a",
        "performance_g_minus_pk","performance_pk","performance_pkatt",
        "performance_crdy","performance_crdr",
        "expected_xg","expected_npxg","expected_xag","expected_npxg_plus_xag",
        "progression_prgc","progression_prgp",
        "per90_gls","per90_ast","per90_g_plus_a","per90_g_minus_pk",
        "per90_g_plus_a_minus_pk","per90_xg","per90_xag",
        "per90_xg_plus_xag","per90_npxg","per90_npxg_plus_xag",
    ]
    df_standard = df_standard.iloc[1:].reset_index(drop=True)

    # ---------- Goalkeepers ----------
    df_gk = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Goalkeeping.csv")
    df_gk.columns = [
        "rk","squad","comp","players",
        "playing_time_mp","playing_time_starts","playing_time_min","playing_time_90s",
        "playing_time_ga","playing_time_ga90",
        "performance_sota","performance_saves","performance_save_pct",
        "performance_w","performance_d","performance_l",
        "performance_cs","performance_cs_pct",
        "penalty_pkatt","penalty_pka","penalty_pksv","penalty_pkm","penalty_save_pct",
    ]
    df_gk = df_gk.iloc[1:].reset_index(drop=True)

    # ---------- Advanced GK ----------
    df_gk_advanced = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Advanced%20Goalkeeping.csv")
    df_gk_advanced.columns = [
        "rk","squad","comp","players",
        "gk_90s","goals_ga","goals_pka","goals_fk","goals_ck","goals_og",
        "expected_psxg","expected_psxg_per_sot","expected_psxg_plus_minus","expected_per90",
        "launched_cmp","launched_att","launched_cmp_pct",
        "passes_att_gk","passes_thr","passes_launch_pct","passes_avglen",
        "goal_kicks_att","goal_kicks_launch_pct","goal_kicks_avglen",
        "crosses_opp","crosses_stp","crosses_stp_pct",
        "sweeper_opa","sweeper_opa_per90","sweeper_avgdist",
    ]
    df_gk_advanced = df_gk_advanced.iloc[1:].reset_index(drop=True)

    # ---------- Shooting ----------
    df_shooting = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Shooting.csv")
    df_shooting.columns = [
        "rk","squad","comp","players",
        "shooting_90s","shooting_gls","shooting_sh","shooting_sot",
        "shooting_sot_pct","shooting_sh_per90","shooting_sot_per90",
        "shooting_g_per_sh","shooting_g_per_sot","shooting_dist",
        "shooting_fk","shooting_pk","shooting_pkatt",
        "expected_xg","expected_npxg","expected_npxg_per_sh",
        "expected_g_minus_xg","expected_np_g_minus_xg",
    ]
    df_shooting = df_shooting.iloc[1:].reset_index(drop=True)

    # ---------- Passing ----------
    df_passing = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Passing.csv")
    df_passing.columns = [
        "rk","squad","comp","players",
        "passing_90s","passing_cmp","passing_att","passing_cmp_pct",
        "passing_totdist","passing_prgdist",
        "short_cmp","short_att","short_cmp_pct",
        "medium_cmp","medium_att","medium_cmp_pct",
        "long_cmp","long_att","long_cmp_pct",
        "expected_ast","expected_xag","expected_xa","expected_a_minus_xag",
        "passing_kp","passing_final_third","passing_ppa","passing_crspa","passing_prgp",
    ]
    df_passing = df_passing.iloc[1:].reset_index(drop=True)

    # ---------- Passing Types ----------
    df_passing_types = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Passing%20Types.csv")
    df_passing_types.columns = [
        "rk","squad","comp","players",
        "pass_types_90s","pass_types_att","pass_types_live","pass_types_dead",
        "pass_types_fk","pass_types_tb","pass_types_sw","pass_types_crs","pass_types_ti",
        "corner_ck","corner_in","corner_out","corner_str",
        "outcomes_cmp","outcomes_off","outcomes_blocks",
    ]
    df_passing_types = df_passing_types.iloc[1:].reset_index(drop=True)

    # ---------- Goal & Shot Creation ----------
    df_goal_shot_creation = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Goal%26ShotCreation.csv")
    df_goal_shot_creation.columns = [
        "rk","squad","comp","players",
        "sca_90s","sca","sca_per90","sca_passlive","sca_passdead",
        "sca_to","sca_sh","sca_fld","sca_def",
        "gca","gca_per90","gca_passlive","gca_passdead",
        "gca_to","gca_sh","gca_fld","gca_def",
    ]
    df_goal_shot_creation = df_goal_shot_creation.iloc[1:].reset_index(drop=True)

    # ---------- Defensive Actions ----------
    df_defensive = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Defensive%20actions.csv")
    df_defensive.columns = [
        "rk","squad","comp","players",
        "def_90s","tackles_tkl","tackles_tklw",
        "tackles_def_3rd","tackles_mid_3rd","tackles_att_3rd",
        "challenges_tkl","challenges_att","challenges_tkl_pct","challenges_lost",
        "blocks_blocks","blocks_sh","blocks_pass","blocks_int",
        "blocks_tkl_int","blocks_clr","blocks_err",
    ]
    df_defensive = df_defensive.iloc[1:].reset_index(drop=True)

    # ---------- Possession ----------
    df_possession = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Possesion.csv")
    df_possession.columns = [
        "rk","squad","comp","players",
        "poss","poss_90s","touches_total","touches_def_pen","touches_def_3rd",
        "touches_mid_3rd","touches_att_3rd","touches_att_pen",
        "takeons_live","takeons_att","takeons_succ","takeons_succ_pct",
        "takeons_tkld","takeons_tkld_pct",
        "carries_total","carries_totdist","carries_prgdist","carries_prgc",
        "carries_final_third","carries_cpa","carries_mis","carries_dis",
        "receiving_rec","receiving_prgr",
    ]
    df_possession = df_possession.iloc[1:].reset_index(drop=True)

    # ---------- Playing time ----------
    df_playing_time = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Playing_Time.csv")
    df_playing_time.columns = [
        "rk","squad","comp","players",
        "age","playing_time_mp","playing_time_min",
        "playing_time_min_per_mp","playing_time_min_pct","playing_time_90s",
        "starts_starts","starts_min_per_start","starts_compl",
        "subs_subs","subs_min_per_sub","subs_unsub",
        "team_success_ppm","team_success_ong","team_success_onga",
        "team_success_plus_minus","team_success_plus_minus_per90",
        "team_success_xg_onxg","team_success_xg_onxga",
        "team_success_xg_plus_minus","team_success_xg_plus_minus_per90",
    ]
    df_playing_time = df_playing_time.iloc[1:].reset_index(drop=True)

    # ---------- Misc ----------
    df_misc = pd.read_csv("https://raw.githubusercontent.com/football-labs/Fotball-labs/refs/heads/main/data/team/fbref_all_stats/Misc.csv")
    df_misc.columns = df_misc.iloc[0]
    df_misc = df_misc.iloc[1:].reset_index(drop=True)
    df_misc = df_misc.loc[:, ~df_misc.columns.astype(str).str.match(r"^Unnamed")]
    df_misc = df_misc[df_misc.iloc[:, 0].astype(str) != "Rk"].reset_index(drop=True)
    df_misc.columns = [
        "rk","squad","comp","players","misc_90s",
        "performance_crdy","performance_crdr","performance_2crdy",
        "performance_fls","performance_fld","performance_off",
        "performance_crs","performance_int","performance_tklw",
        "performance_pkwon","performance_pkcon","performance_og",
        "performance_recov","aerial_won","aerial_lost","aerial_won_pct",
    ]


    return {
        "standard": df_standard,
        "gk": df_gk,
        "gk_adv": df_gk_advanced,
        "shooting": df_shooting,
        "passing": df_passing,
        "passing_types": df_passing_types,
        "goal_shot_creation": df_goal_shot_creation,
        "defensive": df_defensive,
        "possession": df_possession,
        "playing_time": df_playing_time,
        "misc": df_misc,
    }


def prep_squad(df: pd.DataFrame, key: str = "squad") -> pd.DataFrame:
    """
    ## Normalizar la columna 'squad' ##
    ## Normalize 'squad' column ##
    ## Normaliser la colonne 'squad' ##
    """
    df = df.copy()
    df[key] = df[key].astype(str).str.strip()
    return df


def build_joined_dataframe(dfs: dict) -> pd.DataFrame:
    """
    ## Unir estadísticas de campo y porteros solo por 'squad' ##
    ## Join field and GK stats by 'squad' only ##
    ## Fusionner stats de champ et gardiens uniquement par 'squad' ##
    """
    key = "squad"

    # ---------- FIELD PLAYERS ----------
    dfs_field = [
        prep_squad(dfs["standard"], key),
        prep_squad(dfs["shooting"], key),
        prep_squad(dfs["passing"], key),
        prep_squad(dfs["passing_types"], key),
        prep_squad(dfs["possession"], key),
        prep_squad(dfs["defensive"], key),
        prep_squad(dfs["misc"], key),
        prep_squad(dfs["playing_time"], key),
        prep_squad(dfs["goal_shot_creation"], key),
    ]

    df_field = dfs_field[0]
    for df in dfs_field[1:]:
        new_cols = [c for c in df.columns if c != key and c not in df_field.columns]
        df_field = df_field.merge(df[[key] + new_cols], on=key, how="left")

    # ---------- GOALKEEPERS ----------
    dfs_gk = [
        prep_squad(dfs["gk"], key),
        prep_squad(dfs["gk_adv"], key),
    ]

    df_gk_all = dfs_gk[0]
    for df in dfs_gk[1:]:
        new_cols = [c for c in df.columns if c != key and c not in df_gk_all.columns]
        df_gk_all = df_gk_all.merge(df[[key] + new_cols], on=key, how="left")

    # ---------- REMOVE DUPLICATES ----------
    cols_to_drop_from_gk = [c for c in df_gk_all.columns if c in df_field.columns and c != key]
    df_gk_all_reduced = df_gk_all.drop(columns=cols_to_drop_from_gk)

    # ---------- FINAL JOIN ----------
    df_all = df_field.merge(df_gk_all_reduced, on=key, how="left")

    return df_all


def clean_comp_column(df_all: pd.DataFrame) -> pd.DataFrame:
    """
    ## Limpiar nombres de competiciones en 'comp' ##
    ## Clean 'comp' competition names ##
    ## Nettoyer les noms de compétitions dans 'comp' ##
    """
    reemplazos = {
        'es\xa0La Liga': 'La Liga',
        'fr\xa0Ligue 1': 'Ligue 1',
        'eng\xa0Premier League': 'Premier League',
        'it\xa0Serie A': 'Serie A',
        'de\xa0Bundesliga': 'Bundesliga',
    }

    if "comp" in df_all.columns:
        df_all["comp"] = df_all["comp"].replace(reemplazos)

    return df_all


def main():
    """
    ## Pipeline completo: cargar, unir, limpiar y exportar ##
    ## Full pipeline: load, join, clean and export ##
    ## Pipeline complet : charger, fusionner, nettoyer et exporter ##
    """
    dfs = load_dataframes()
    df_all = build_joined_dataframe(dfs)
    df_all = clean_comp_column(df_all)

    # Exportar al path dentro del repo (SIN prefijo Fotball-labs)
    output_path = "data/team/grouped_stats.csv"

    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df_all.to_csv(output_path, index=False, encoding="utf-8")

    print("Archivo exportado a:", output_path)
    print("File exported to:", output_path)
    print("Fichier exporté vers :", output_path)


if __name__ == "__main__":
    main()


