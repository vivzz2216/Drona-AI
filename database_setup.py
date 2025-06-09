import sqlite3
import csv
import os

# Define the database file
DB_FILE = 'isl_players.db'

# Define columns that should be stored as TEXT; others will be INTEGER
TEXT_COLUMNS = [
    'tour_name', 'name', 'short_name', 'position', 'position_short',
    'team_name', 'team_short_name', 'country_name', 'dob', 'player_foot',
    'image_path'  # Add image_path to TEXT columns
]

def sanitize_column_name(col_name):
    """Replace dots with underscores to make column names SQL-friendly."""
    return col_name.replace('.', '_')

def sanitize_player_name_for_filename(player_name):
    """Convert a player's name into a valid filename."""
    return player_name.lower().replace(' ', '_').replace("'", '').replace('.', '')

def setup_database(csv_file_path):
    # Remove existing database file to start fresh
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Read the CSV to get column names from the header
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # First row is the header
        csv_columns = [sanitize_column_name(col) for col in header]  # Sanitize column names

    # Add image_path to the list of columns
    all_columns = csv_columns + ['image_path']

    # Create the table with appropriate data types
    create_table_query = 'CREATE TABLE IF NOT EXISTS players ('
    for col in all_columns:
        col_type = 'TEXT' if col in TEXT_COLUMNS else 'INTEGER'
        create_table_query += f'"{col}" {col_type}, '  # Quote column names
    create_table_query = create_table_query.rstrip(', ') + ')'
    cursor.execute(create_table_query)

    # Insert data from CSV into the table
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Preprocess data: handle empty strings and type conversion
            sanitized_row = {sanitize_column_name(key): value for key, value in row.items()}
            for key in sanitized_row:
                if key not in TEXT_COLUMNS:
                    # Convert numerical fields to int, empty strings to 0
                    sanitized_row[key] = int(sanitized_row[key]) if sanitized_row[key].strip() else 0
                elif key == 'dob':
                    # Handle date of birth: keep as text, empty strings to None (NULL)
                    sanitized_row[key] = sanitized_row[key].strip() if sanitized_row[key].strip() else None

            # Add image_path based on the player's name
            player_name = sanitized_row.get('name', '')
            if player_name:
                sanitized_player_name = sanitize_player_name_for_filename(player_name)
                image_path = f'images/players/{sanitized_player_name}.jpg'
            else:
                image_path = 'images/players/placeholder.jpg'  # Fallback if name is missing
            sanitized_row['image_path'] = image_path

            # Insert the row
            placeholders = ','.join(['?' for _ in sanitized_row])
            columns = ','.join([f'"{key}"' for key in sanitized_row.keys()])  # Quote column names
            insert_query = f'INSERT INTO players ({columns}) VALUES ({placeholders})'
            cursor.execute(insert_query, list(sanitized_row.values()))

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' created and data inserted successfully.")

if __name__ == "__main__":
    # Replace with your actual CSV file path if different
    setup_database('isl_dataset.csv')