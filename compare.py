# compare.py
import sqlite3

DB_FILE = "isl_players.db"
MIN_MINUTES = 1000  # Assuming a default value for MIN_MINUTES


def get_all_players(tour_name=None):
    """Fetch all players from the database for the comparison dropdown."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, country_name, position
        FROM players
        WHERE minutes_played >= ?
        """
        params = [MIN_MINUTES]
        
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
            
        query += " ORDER BY position, name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team_name, country_name, position = row
            players.append({
                "name": name,
                "team_name": team_name,
                "country_name": country_name,
                "position": position
            })
        return players
    finally:
        conn.close()


def get_player_stats(player_name, tour_name=None):
    """Get detailed stats for a specific player."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, country_name, position, events_goals, events_assists,
               touches_total_passes, events_clean_sheet, minutes_played,
               events_shots_on_target, touches_successful_tackles, events_fouls_committed,
               image_path, goaltenders_saves, goaltenders_goals_allowed,
               touches_interceptions, touches_clearance, events_chances_created
        FROM players
        WHERE name = ?
        """
        params = [player_name]
        
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
            
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if not row:
            return None
            
        (
            name, team_name, country_name, position, goals, assists,
            total_passes, clean_sheet, minutes_played, shots_on_target,
            successful_tackles, fouls_committed, image_path, saves,
            goals_conceded, interceptions, clearances, chances_created
        ) = row
        
        return {
            "name": name,
            "team_name": team_name,
            "country_name": country_name,
            "position": position,
            "goals": goals or 0,
            "assists": assists or 0,
            "passes": total_passes or 0,
            "clean_sheets": clean_sheet or 0,
            "minutes_played": minutes_played or 0,
            "shots_on_target": shots_on_target or 0,
            "tackles_won": successful_tackles or 0,
            "fouls_committed": fouls_committed or 0,
            "saves": saves or 0,
            "goals_conceded": goals_conceded or 0,
            "interceptions": interceptions or 0,
            "clearances": clearances or 0,
            "chances_created": chances_created or 0,
            "image_path": image_path or "images/players/placeholder.jpg"
        }
    finally:
        conn.close()
