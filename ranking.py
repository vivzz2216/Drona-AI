import sqlite3
from datetime import datetime

DB_FILE = "isl_players.db"
MIN_MINUTES = 500

def calculate_age(dob):
    """Calculate age from date of birth (dob format: 'YYYY-MM-DD')."""
    if not dob:
        return "N/A"
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.now()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        return age
    except (ValueError, TypeError):
        return "N/A"

def convert_to_stars(score: float) -> str:
    """Convert a score (0-1) to an HTML string with stars."""
    score = max(0, min(1, score))
    rating = score * 5
    full_stars = int(rating)
    decimal_part = rating - full_stars
    half_star = 1 if decimal_part >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars_html = '<i class="bi bi-star-fill"></i>' * full_stars
    if half_star:
        stars_html += '<i class="bi bi-star-half"></i>'
    stars_html += '<i class="bi bi-star"></i>' * empty_stars
    return stars_html

def get_player_by_name(name, tour_name=None):
    """Fetch a player's data from the database by their name and optional tour_name."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT jersey_no, name, position, team_name, country_name, height, dob,
               minutes_played, events_clean_sheet, goaltenders_saves, goaltenders_shots_on_goal_faced,
               goaltenders_punches, goaltenders_catches, touches_clearance, touches_good_passes,
               touches_total_passes, touches_tackles, goaltenders_goals_allowed, events_penalties_saved,
               events_yellow_cards, events_red_cards, events_goals, events_assists, events_shots_on_target,
               events_chances_created, touches_interceptions, touches_aerial_duel_won, events_key_passes,
               touches_take_on_successful, events_offsides
        FROM players
        WHERE name = ?
        """
        params = [name]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
        
        cursor.execute(query, params)
        row = cursor.fetchone()

        if row:
            player_data = {
                "number": row[0] if row[0] is not None else "N/A",
                "name": row[1] if row[1] is not None else "N/A",
                "position": row[2] if row[2] is not None else "N/A",
                "team_name": row[3] if row[3] is not None else "N/A",
                "country": row[4] if row[4] is not None else "N/A",
                "height": row[5] if row[5] is not None else "N/A",
                "dob": row[6],
                "age": calculate_age(row[6]),
                "season": tour_name if tour_name else "N/A",
                "minutes_played": row[7] if row[7] is not None else 0,
                "clean_sheets": row[8] if row[8] is not None else 0,
                "saves": row[9] if row[9] is not None else 0,
                "shots_faced": row[10] if row[10] is not None else 0,
                "punches": row[11] if row[11] is not None else 0,
                "catches": row[12] if row[12] is not None else 0,
                "clearances": row[13] if row[13] is not None else 0,
                "good_passes": row[14] if row[14] is not None else 0,
                "total_passes": row[15] if row[15] is not None else 0,
                "tackles": row[16] if row[16] is not None else 0,
                "goals_conceded": row[17] if row[17] is not None else 0,
                "penalties_saved": row[18] if row[18] is not None else 0,
                "yellow_cards": row[19] if row[19] is not None else 0,
                "red_cards": row[20] if row[20] is not None else 0,
                "goals": row[21] if row[21] is not None else 0,
                "assists": row[22] if row[22] is not None else 0,
                "shots_on_target": row[23] if row[23] is not None else 0,
                "chances_created": row[24] if row[24] is not None else 0,
                "interceptions": row[25] if row[25] is not None else 0,
                "aerial_duels_won": row[26] if row[26] is not None else 0,
                "key_passes": row[27] if row[27] is not None else 0,
                "successful_take_ons": row[28] if row[28] is not None else 0,
                "offsides": row[29] if row[29] is not None else 0,
            }

            # Calculate derived stats
            player_data["appearances"] = int(player_data["minutes_played"] / 90) if player_data["minutes_played"] else 0
            player_data["passes_per_game"] = round(player_data["total_passes"] / player_data["appearances"], 2) if player_data["appearances"] else 0
            player_data["passing_accuracy_percentage"] = round((player_data["good_passes"] / player_data["total_passes"]) * 100, 2) if player_data["total_passes"] else 0
            player_data["successful_passes"] = player_data["good_passes"]
            player_data["touches"] = player_data["total_passes"] + player_data["tackles"]

            # Add dummy heatmap path based on position (optional if using static images)
            heatmap_paths = {
                "Goalkeeper": "images/heatmaps/goalkeeper_goalpost.png",
                "Midfielder": "images/heatmaps/midfielder_midarea.png",
                "Defender": "images/heatmaps/defender_defensive.png",
                "Forward": "images/heatmaps/forward_attacking.png",
            }
            player_data["heatmap_path"] = heatmap_paths.get(player_data["position"], "images/heatmaps/default.png")

            # Position-specific stats to display
            if player_data["position"] == "Goalkeeper":
                player_data["saves_percentage"] = round((player_data["saves"] / player_data["shots_faced"]) * 100, 2) if player_data["shots_faced"] else 0
                player_data["saves_per_game"] = round(player_data["saves"] / player_data["appearances"], 2) if player_data["appearances"] else 0
                player_data["gk_successful_distribution"] = player_data["good_passes"]
                stats_to_display = [
                    {"name": "Appearances", "value": player_data["appearances"], "type": "normal"},
                    {"name": "Minutes Played", "value": player_data["minutes_played"], "type": "normal"},
                    {"name": "Clean Sheets", "value": player_data["clean_sheets"], "type": "normal"},
                    {"name": "Saves", "value": player_data["saves"], "type": "normal"},
                    {"name": "Saves Percentage", "value": player_data["saves_percentage"], "type": "circle"},
                    {"name": "Saves per Game", "value": player_data["saves_per_game"], "type": "normal"},
                    {"name": "Punches", "value": player_data["punches"], "type": "normal"},
                    {"name": "Catches", "value": player_data["catches"], "type": "normal"},
                    {"name": "Clearances", "value": player_data["clearances"], "type": "normal"},
                    {"name": "GK Successful Distribution", "value": player_data["gk_successful_distribution"], "type": "normal"},
                    {"name": "Passes per Game", "value": player_data["passes_per_game"], "type": "normal"},
                    {"name": "Passing Accuracy Percentage", "value": player_data["passing_accuracy_percentage"], "type": "circle"},
                    {"name": "Successful Passes", "value": player_data["successful_passes"], "type": "normal"},
                    {"name": "Touches", "value": player_data["touches"], "type": "normal"},
                    {"name": "Shots Faced", "value": player_data["shots_faced"], "type": "normal"},
                    {"name": "Goals Conceded", "value": player_data["goals_conceded"], "type": "normal"},
                    {"name": "Penalties Saved", "value": player_data["penalties_saved"], "type": "normal"},
                    {"name": "Yellow Cards", "value": player_data["yellow_cards"], "type": "normal"},
                    {"name": "Red Cards", "value": player_data["red_cards"], "type": "normal"},
                ]
            elif player_data["position"] == "Defender":
                stats_to_display = [
                    {"name": "Appearances", "value": player_data["appearances"], "type": "normal"},
                    {"name": "Minutes Played", "value": player_data["minutes_played"], "type": "normal"},
                    {"name": "Clean Sheets", "value": player_data["clean_sheets"], "type": "normal"},
                    {"name": "Tackles", "value": player_data["tackles"], "type": "normal"},
                    {"name": "Interceptions", "value": player_data["interceptions"], "type": "normal"},
                    {"name": "Clearances", "value": player_data["clearances"], "type": "normal"},
                    {"name": "Aerial Duels Won", "value": player_data["aerial_duels_won"], "type": "normal"},
                    {"name": "Passes per Game", "value": player_data["passes_per_game"], "type": "normal"},
                    {"name": "Passing Accuracy Percentage", "value": player_data["passing_accuracy_percentage"], "type": "circle"},
                    {"name": "Successful Passes", "value": player_data["successful_passes"], "type": "normal"},
                    {"name": "Touches", "value": player_data["touches"], "type": "normal"},
                    {"name": "Goals", "value": player_data["goals"], "type": "normal"},
                    {"name": "Assists", "value": player_data["assists"], "type": "normal"},
                    {"name": "Yellow Cards", "value": player_data["yellow_cards"], "type": "normal"},
                    {"name": "Red Cards", "value": player_data["red_cards"], "type": "normal"},
                ]
            elif player_data["position"] == "Midfielder":
                stats_to_display = [
                    {"name": "Appearances", "value": player_data["appearances"], "type": "normal"},
                    {"name": "Minutes Played", "value": player_data["minutes_played"], "type": "normal"},
                    {"name": "Goals", "value": player_data["goals"], "type": "normal"},
                    {"name": "Assists", "value": player_data["assists"], "type": "normal"},
                    {"name": "Passes per Game", "value": player_data["passes_per_game"], "type": "normal"},
                    {"name": "Passing Accuracy Percentage", "value": player_data["passing_accuracy_percentage"], "type": "circle"},
                    {"name": "Successful Passes", "value": player_data["successful_passes"], "type": "normal"},
                    {"name": "Key Passes", "value": player_data["key_passes"], "type": "normal"},
                    {"name": "Tackles", "value": player_data["tackles"], "type": "normal"},
                    {"name": "Interceptions", "value": player_data["interceptions"], "type": "normal"},
                    {"name": "Touches", "value": player_data["touches"], "type": "normal"},
                    {"name": "Yellow Cards", "value": player_data["yellow_cards"], "type": "normal"},
                    {"name": "Red Cards", "value": player_data["red_cards"], "type": "normal"},
                ]
            elif player_data["position"] == "Forward":
                player_data["conversion_rate"] = round((player_data["goals"] / player_data["shots_on_target"]) * 100, 2) if player_data["shots_on_target"] else 0
                stats_to_display = [
                    {"name": "Appearances", "value": player_data["appearances"], "type": "normal"},
                    {"name": "Minutes Played", "value": player_data["minutes_played"], "type": "normal"},
                    {"name": "Goals", "value": player_data["goals"], "type": "normal"},
                    {"name": "Assists", "value": player_data["assists"], "type": "normal"},
                    {"name": "Shots on Target", "value": player_data["shots_on_target"], "type": "normal"},
                    {"name": "Conversion Rate", "value": player_data["conversion_rate"], "type": "circle"},
                    {"name": "Successful Take-ons", "value": player_data["successful_take_ons"], "type": "normal"},
                    {"name": "Offsides", "value": player_data["offsides"], "type": "normal"},
                    {"name": "Passes per Game", "value": player_data["passes_per_game"], "type": "normal"},
                    {"name": "Passing Accuracy Percentage", "value": player_data["passing_accuracy_percentage"], "type": "circle"},
                    {"name": "Successful Passes", "value": player_data["successful_passes"], "type": "normal"},
                    {"name": "Key Passes", "value": player_data["key_passes"], "type": "normal"},
                    {"name": "Touches", "value": player_data["touches"], "type": "normal"},
                    {"name": "Yellow Cards", "value": player_data["yellow_cards"], "type": "normal"},
                    {"name": "Red Cards", "value": player_data["red_cards"], "type": "normal"},
                ]
            else:
                stats_to_display = []

            player_data["stats"] = stats_to_display
            return player_data
        return None
    finally:
        conn.close()

def rank_by_goals(tour_name=None):
    """Rank players by total goals scored."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, events_goals, minutes_played, image_path
        FROM players
        WHERE minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
        query += " ORDER BY events_goals DESC LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team, goals, minutes, image_path = row
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "stat_value": goals,
                    "minutes_played": minutes,
                    "image_path": image_path or "images/players/placeholder.jpg",
                }
            )
        return players
    finally:
        conn.close()

def rank_by_assists(tour_name=None):
    """Rank players by total assists."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, events_assists, minutes_played
        FROM players
        WHERE minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
        query += " ORDER BY events_assists DESC LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team, assists, minutes = row
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "stat_value": assists,
                    "minutes_played": minutes,
                }
            )
        return players
    finally:
        conn.close()

def rank_by_passes(tour_name=None):
    """Rank players by total passes."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, touches_total_passes, minutes_played
        FROM players
        WHERE minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
        query += " ORDER BY touches_total_passes DESC LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team, passes, minutes = row
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "stat_value": passes,
                    "minutes_played": minutes,
                }
            )
        return players
    finally:
        conn.close()

def rank_by_saves(tour_name=None):
    """Rank goalkeepers by total saves."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, goaltenders_saves, minutes_played, image_path
        FROM players
        WHERE position = 'Goalkeeper' AND minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)
        query += " ORDER BY goaltenders_saves DESC LIMIT 10"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team, saves, minutes, image_path = row
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "stat_value": saves if saves is not None else 0,  # Handle None values
                    "minutes_played": minutes,
                    "image_path": image_path or "images/players/placeholder.jpg",
                }
            )
        return players
    finally:
        conn.close()

def rank_goalkeepers(tour_name=None):
    """Rank goalkeepers based on save percentage, goals allowed per 90, and clean sheet percentage."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, goaltenders_saves, goaltenders_shots_on_goal_faced,
               goaltenders_goals_allowed, events_clean_sheet, minutes_played
        FROM players
        WHERE position = 'Goalkeeper' AND minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)

        print(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} rows: {rows[:2]}")  # Show first 2 rows for brevity

        players = []
        for row in rows:
            try:
                name, team, saves, shots_faced, goals_allowed, clean_sheets, minutes = row
                # Handle None values
                saves = saves if saves is not None else 0
                shots_faced = shots_faced if shots_faced is not None else 0
                goals_allowed = goals_allowed if goals_allowed is not None else 0
                clean_sheets = clean_sheets if clean_sheets is not None else 0
                minutes = minutes if minutes is not None else 0

                save_pct = saves / shots_faced if shots_faced > 0 else 0
                goals_allowed_per_90 = (goals_allowed / minutes) * 90 if minutes > 0 else 0
                clean_sheet_pct = clean_sheets / (minutes / 90) if minutes > 0 else 0

                player = {
                    "name": name,
                    "team_name": team,
                    "minutes_played": minutes,
                    "save_pct": save_pct,
                    "goals_allowed_per_90": goals_allowed_per_90,
                    "clean_sheet_pct": clean_sheet_pct,
                }
                players.append(player)
            except Exception as e:
                print(f"Error processing row {row}: {e}")

        if not players:
            print(f"No goalkeepers processed for tour_name: {tour_name}")
            return []

        max_clean_sheet_pct = max(p["clean_sheet_pct"] for p in players)
        for p in players:
            norm_save_pct = p["save_pct"]
            inverted_goals_allowed = 1 / (1 + p["goals_allowed_per_90"]) if p["goals_allowed_per_90"] >= 0 else 1
            norm_clean_sheet_pct = (
                p["clean_sheet_pct"] / max_clean_sheet_pct if max_clean_sheet_pct > 0 else 0
            )
            p["score"] = (
                (0.4 * norm_save_pct)
                + (0.3 * inverted_goals_allowed)
                + (0.3 * norm_clean_sheet_pct)
            )
            p["stars"] = convert_to_stars(p["score"])

        print(f"Ranked {len(players)} goalkeepers: {players[:2]}")  # Show first 2 ranked players
        return sorted(players, key=lambda x: x["score"], reverse=True)
    except Exception as e:
        print(f"Error in rank_goalkeepers: {e}")
        return []
    finally:
        conn.close()
        
def rank_defenders(tour_name=None):
    """Rank defenders based on tackles, interceptions, clearances, aerial duels won, and clean sheet percentage."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, touches_tackles, touches_interceptions, touches_clearance,
               touches_aerial_duel_won, events_clean_sheet, minutes_played
        FROM players
        WHERE position = 'Defender' AND minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            (
                name,
                team,
                tackles,
                interceptions,
                clearances,
                aerial_won,
                clean_sheets,
                minutes,
            ) = row
            tackles_per_90 = (tackles / minutes) * 90 if minutes > 0 else 0
            interceptions_per_90 = (interceptions / minutes) * 90 if minutes > 0 else 0
            clearances_per_90 = (clearances / minutes) * 90 if minutes > 0 else 0
            aerial_won_per_90 = (aerial_won / minutes) * 90 if minutes > 0 else 0
            clean_sheet_pct = clean_sheets / (minutes / 90) if minutes > 0 else 0
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "minutes_played": minutes,
                    "tackles_per_90": tackles_per_90,
                    "interceptions_per_90": interceptions_per_90,
                    "clearances_per_90": clearances_per_90,
                    "aerial_won_per_90": aerial_won_per_90,
                    "clean_sheet_pct": clean_sheet_pct,
                }
            )

        if not players:
            return []

        max_tackles = max(p["tackles_per_90"] for p in players)
        max_interceptions = max(p["interceptions_per_90"] for p in players)
        max_clearances = max(p["clearances_per_90"] for p in players)
        max_aerial_won = max(p["aerial_won_per_90"] for p in players)
        max_clean_sheet_pct = max(p["clean_sheet_pct"] for p in players)

        for p in players:
            p["score"] = (
                0.2 * (p["tackles_per_90"] / max_tackles if max_tackles > 0 else 0)
                + 0.2 * (p["interceptions_per_90"] / max_interceptions if max_interceptions > 0 else 0)
                + 0.2 * (p["clearances_per_90"] / max_clearances if max_clearances > 0 else 0)
                + 0.2 * (p["aerial_won_per_90"] / max_aerial_won if max_aerial_won > 0 else 0)
                + 0.2 * (p["clean_sheet_pct"] / max_clean_sheet_pct if max_clean_sheet_pct > 0 else 0)
            )
            p["stars"] = convert_to_stars(p["score"])

        return sorted(players, key=lambda x: x["score"], reverse=True)
    finally:
        conn.close()

def rank_forwards(tour_name=None):
    """Rank forwards based on goals, assists, shots on target, and chances created."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, events_goals, events_assists, events_shots_on_target,
               events_chances_created, minutes_played
        FROM players
        WHERE position = 'Forward' AND minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            name, team, goals, assists, shots_on_target, chances_created, minutes = row
            goals_per_90 = (goals / minutes) * 90 if minutes > 0 else 0
            assists_per_90 = (assists / minutes) * 90 if minutes > 0 else 0
            shots_per_90 = (shots_on_target / minutes) * 90 if minutes > 0 else 0
            chances_per_90 = (chances_created / minutes) * 90 if minutes > 0 else 0
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "minutes_played": minutes,
                    "goals_per_90": goals_per_90,
                    "assists_per_90": assists_per_90,
                    "shots_per_90": shots_per_90,
                    "chances_per_90": chances_per_90,
                }
            )

        if not players:
            return []

        max_goals = max(p["goals_per_90"] for p in players)
        max_assists = max(p["assists_per_90"] for p in players)
        max_shots = max(p["shots_per_90"] for p in players)
        max_chances = max(p["chances_per_90"] for p in players)

        for p in players:
            p["score"] = (
                0.4 * (p["goals_per_90"] / max_goals if max_goals > 0 else 0)
                + 0.3 * (p["assists_per_90"] / max_assists if max_assists > 0 else 0)
                + 0.15 * (p["shots_per_90"] / max_shots if max_shots > 0 else 0)
                + 0.15 * (p["chances_per_90"] / max_chances if max_chances > 0 else 0)
            )
            p["stars"] = convert_to_stars(p["score"])

        return sorted(players, key=lambda x: x["score"], reverse=True)
    finally:
        conn.close()

def rank_midfielders(tour_name=None):
    """Rank midfielders based on passes, pass accuracy, key passes, assists, tackles, interceptions, and goals."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        query = """
        SELECT name, team_name, touches_total_passes, touches_good_passes, events_key_passes,
               events_assists, touches_tackles, touches_interceptions, events_goals, minutes_played
        FROM players
        WHERE position = 'Midfielder' AND minutes_played >= ?
        """
        params = [MIN_MINUTES]
        if tour_name:
            query += " AND tour_name = ?"
            params.append(tour_name)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        players = []
        for row in rows:
            (
                name,
                team,
                total_passes,
                good_passes,
                key_passes,
                assists,
                tackles,
                interceptions,
                goals,
                minutes,
            ) = row
            passes_per_90 = (total_passes / minutes) * 90 if minutes > 0 else 0
            pass_accuracy = good_passes / total_passes if total_passes > 0 else 0
            key_passes_per_90 = (key_passes / minutes) * 90 if minutes > 0 else 0
            assists_per_90 = (assists / minutes) * 90 if minutes > 0 else 0
            tackles_per_90 = (tackles / minutes) * 90 if minutes > 0 else 0
            interceptions_per_90 = (interceptions / minutes) * 90 if minutes > 0 else 0
            goals_per_90 = (goals / minutes) * 90 if minutes > 0 else 0
            players.append(
                {
                    "name": name,
                    "team_name": team,
                    "minutes_played": minutes,
                    "passes_per_90": passes_per_90,
                    "pass_accuracy": pass_accuracy,
                    "key_passes_per_90": key_passes_per_90,
                    "assists_per_90": assists_per_90,
                    "tackles_per_90": tackles_per_90,
                    "interceptions_per_90": interceptions_per_90,
                    "goals_per_90": goals_per_90,
                }
            )

        if not players:
            return []

        max_passes = max(p["passes_per_90"] for p in players)
        max_key_passes = max(p["key_passes_per_90"] for p in players)
        max_assists = max(p["assists_per_90"] for p in players)
        max_tackles = max(p["tackles_per_90"] for p in players)
        max_interceptions = max(p["interceptions_per_90"] for p in players)
        max_goals = max(p["goals_per_90"] for p in players)

        for p in players:
            p["score"] = (
                0.1 * (p["passes_per_90"] / max_passes if max_passes > 0 else 0)
                + 0.1 * p["pass_accuracy"]
                + 0.15 * (p["key_passes_per_90"] / max_key_passes if max_key_passes > 0 else 0)
                + 0.15 * (p["assists_per_90"] / max_assists if max_assists > 0 else 0)
                + 0.15 * (p["tackles_per_90"] / max_tackles if max_tackles > 0 else 0)
                + 0.15 * (p["interceptions_per_90"] / max_interceptions if max_interceptions > 0 else 0)
                + 0.2 * (p["goals_per_90"] / max_goals if max_goals > 0 else 0)
            )
            p["stars"] = convert_to_stars(p["score"])

        return sorted(players, key=lambda x: x["score"], reverse=True)
    finally:
        conn.close()

if __name__ == "__main__":
    for pos, func in [
        ("Goalkeeper", rank_goalkeepers),
        ("Defender", rank_defenders),
        ("Forward", rank_forwards),
        ("Midfielder", rank_midfielders),
    ]:
        print(f"\nTop 5 {pos}s:")
        players = func(tour_name="isl 6")
        for i, p in enumerate(players[:5], 1):
            print(f"{i}. {p['name']} ({p['team_name']}) - Score: {p['score']:.2f}")