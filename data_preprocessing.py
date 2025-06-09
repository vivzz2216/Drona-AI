import sqlite3

DB_FILE = 'isl_players.db'

def preprocess_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check for missing critical fields and set defaults if necessary
    updates = [
        # Ensure minutes_played is not negative or NULL; set to 0 if invalid
        "UPDATE players SET minutes_played = 0 WHERE minutes_played IS NULL OR minutes_played < 0",
        # Ensure position is not NULL; set to 'Unknown' if missing
        "UPDATE players SET position = 'Unknown' WHERE position IS NULL OR position = ''"
    ]
    for query in updates:
        cursor.execute(query)

    # Verify data integrity (example: ensure stats are non-negative)
    stat_columns = [
        'goaltenders_saves', 'goaltenders_shots_on_goal_faced', 'goaltenders_goals_allowed',
        'events_clean_sheet', 'touches_tackles', 'touches_interceptions', 'touches_clearance',
        'touches_aerial_duel_won', 'events_goals', 'events_assists', 'events_shots_on_target',
        'events_chances_created', 'touches_total_passes', 'touches_good_passes', 'events_key_passes'
    ]
    for col in stat_columns:
        cursor.execute(f"UPDATE players SET {col} = 0 WHERE {col} IS NULL OR {col} < 0")

    # Commit changes
    conn.commit()
    conn.close()
    print("Data preprocessing completed.")

if __name__ == "__main__":
    preprocess_data()