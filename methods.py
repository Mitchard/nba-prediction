
# ----- IMPORTS -----
import numpy as np
import pandas as pd

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats, playergamelog

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashteamstats, teamgamelog

# ----- CLASSES -----


# ----- STATIC METHODS -----
@staticmethod
def get_player_stats(player_name: str, season: str):
    """
    Inputs:
        player_name (string): Full name of the desired player
        season (string): Desired season formatted as "YYYY-YY" (i.e "2024-25")
    Returns:
        season_stats (DataFrame): Season totals + per-game averages.
        game_logs (DataFrame): Game-by-game stats for the season.
    """
    
    # Look up player ID
    player_search = players.find_players_by_full_name(player_name)
    if not player_search:
        raise ValueError(f"Player '{player_name}' not found.")
    player_id = player_search[0]["id"]

    # Get career stats, filter by season
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career.get_data_frames()[0]

    season_stats = career_df[career_df["SEASON_ID"] == season]
    if season_stats.empty:
        raise ValueError(f"No stats found for {player_name} in season {season}.")

    # Get game logs for this season
    logs = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=season,
        season_type_all_star="Regular Season"
    )
    game_logs = logs.get_data_frames()[0]

    # Make sure rows are chronological
    game_logs["GAME_DATE"] = pd.to_datetime(game_logs["GAME_DATE"])
    game_logs = game_logs.sort_values("GAME_DATE").reset_index(drop=True)

    return season_stats.reset_index(drop=True), game_logs

@staticmethod
def get_team_stats(team_name: str, season: str):
    """
    Inputs:
        team_name (string): Full name of desired team
        season (string): Desired season formatted as "YYYY-YY" (i.e "2024-25")
    Returns:
        season_stats (DataFrame): Team season totals & per-game averages
        game_logs (DataFrame): Game-by-game results for the season
    """

    # Find team ID
    team_search = teams.find_teams_by_full_name(team_name)
    if not team_search:
        raise ValueError(f"Team '{team_name}' not found.")

    team_id = team_search[0]["id"]

    # Get season statistics (totals & averages for all teams)
    league_stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame"   # You can also use "Totals"
    )
    df = league_stats.get_data_frames()[0]

    # Filter to the chosen team
    season_stats = df[df["TEAM_ID"] == team_id]
    if season_stats.empty:
        raise ValueError(f"No stats found for {team_name} in season {season}.")

    # Get game-by-game logs
    logs = teamgamelog.TeamGameLog(
        team_id=team_id,
        season=season,
        season_type_all_star="Regular Season"
    )
    game_logs = logs.get_data_frames()[0]

    # Ensure chronological order
    game_logs["GAME_DATE"] = pd.to_datetime(
        game_logs["GAME_DATE"],
        format="%b %d, %Y"
    )

    game_logs = game_logs.sort_values("GAME_DATE").reset_index(drop=True)

    return season_stats.reset_index(drop=True), game_logs

def main():
    
    team_name = "Golden State Warriors"
    player_name = 'Lebron James'
    season = '2023-24'

    player_stats = get_player_stats(player_name, season)

    team_stats = get_team_stats(team_name, season)

    print(team_stats)

if __name__ == '__main__':
    main()