import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import logging
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load data with improved season inference
def load_player_data():
    try:
        data = pd.read_csv('isl_dataset.csv')
        data['name'] = data['name'].str.strip().str.lower()  # Standardize names
        required_cols = ['name', 'tour_id', 'tour_name', 'events.goals', 'events.assists', 'minutes_played', 
                         'events.shots_on_target', 'touches.successful_tackles']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}. Using defaults where applicable.")
        
        if 'tour_name' in data.columns:
            data['season'] = data['tour_name'].astype(str).str.extract(r'(ISL\d+|ISL \d{4}-\d{2}|Season \d+)')[0]
            season_map = {
                'ISL6': 'ISL6', 'ISL7': 'ISL7',
                'ISL 2020-21': 'ISL6', 'ISL 2021-22': 'ISL7',
                'Season 6': 'ISL6', 'Season 7': 'ISL7'
            }
            data['season'] = data['season'].map(season_map).fillna('Unknown')
            logger.info(f"Inferred seasons: {data['season'].unique()}")
        elif 'tour_id' in data.columns:
            season_map = {148: 'ISL6', 202: 'ISL7', 'ISL6_001': 'ISL6', 'ISL7_001': 'ISL7', 'ISL6_002': 'ISL6', 'ISL7_002': 'ISL7'}
            data['season'] = data['tour_id'].map(season_map).fillna('Unknown')
            logger.info(f"Inferred seasons from tour_id: {data['season'].unique()}")
        else:
            logger.error("No season info found.")
            raise KeyError("Season information missing")
        
        return data
    except FileNotFoundError:
        logger.error("isl_dataset.csv not found.")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

# Feature engineering
def engineer_features(df):
    if 'age' not in df.columns and 'dob' in df.columns:
        df['age'] = datetime.now().year - pd.to_datetime(df['dob'], errors='coerce').dt.year
        df['age'] = df['age'].fillna(0).astype(int)
    elif 'age' not in df.columns:
        df['age'] = 0
    
    for col in ['events.shots_on_target', 'events.key_passes', 'touches.successful_tackles']:
        if col not in df.columns:
            df[col] = 0
    
    df['goal_efficiency'] = df['events.goals'] / df['events.shots_on_target'].replace(0, 1)
    df['work_rate'] = df['minutes_played'] / df['age'].replace(0, 1)
    return df

# Prepare model data
def prepare_model_data(df):
    df_isl6 = df[df['season'] == 'ISL6'].drop(columns=['season'])
    df_isl7 = df[df['season'] == 'ISL7'].drop(columns=['season'])
    
    common_players = pd.merge(df_isl6, df_isl7, on='name', suffixes=('_isl6', '_isl7'), how='inner')
    if common_players.empty:
        logger.warning("No common players found.")
        return None, None, None
    
    common_players['goal_increase'] = common_players['events.goals_isl7'] - common_players['events.goals_isl6']
    common_players['assist_increase'] = common_players['events.assists_isl7'] - common_players['events.assists_isl6']
    common_players['minutes_increase'] = common_players['minutes_played_isl7'] - common_players['minutes_played_isl6']
    
    features = ['goal_increase', 'assist_increase', 'minutes_increase']
    X = common_players[features].fillna(0)
    y = common_players.apply(lambda row: predict_growth_for_player(row.filter(like='_isl6').to_dict(), 
                                                                  row.filter(like='_isl7').to_dict()), axis=1)
    return X, y, common_players

# Improved growth prediction for a player
def predict_growth_for_player(player_isl6, player_isl7):
    def to_float(value, key):
        try:
            return float(value) if pd.notnull(value) else 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid {key}, using 0")
            return 0.0

    player_data = {
        'player_name': player_isl6.get('name', 'Unknown'),
        'events.goals_isl6': to_float(player_isl6.get('events.goals', 0), 'goals_isl6'),
        'events.assists_isl6': to_float(player_isl6.get('events.assists', 0), 'assists_isl6'),
        'minutes_played_isl6': to_float(player_isl6.get('minutes_played', 0), 'minutes_isl6'),
        'events.shots_on_target_isl6': to_float(player_isl6.get('events.shots_on_target', 0), 'shots_isl6'),
        'events.goals_isl7': to_float(player_isl7.get('events.goals', 0), 'goals_isl7'),
        'events.assists_isl7': to_float(player_isl7.get('events.assists', 0), 'assists_isl7'),
        'minutes_played_isl7': to_float(player_isl7.get('minutes_played', 0), 'minutes_isl7'),
        'events.shots_on_target_isl7': to_float(player_isl7.get('events.shots_on_target', 0), 'shots_isl7'),
    }

    # Calculate increases
    goal_increase = player_data['events.goals_isl7'] - player_data['events.goals_isl6']
    assist_increase = player_data['events.assists_isl7'] - player_data['events.assists_isl6']
    minutes_increase = player_data['minutes_played_isl7'] - player_data['minutes_played_isl6']

    # Percentage improvements (avoid division by zero)
    goal_pct = ((player_data['events.goals_isl7'] - player_data['events.goals_isl6']) / 
                max(player_data['events.goals_isl6'], 1)) * 100 if player_data['events.goals_isl6'] > 0 else player_data['events.goals_isl7'] * 10
    assist_pct = ((player_data['events.assists_isl7'] - player_data['events.assists_isl6']) / 
                  max(player_data['events.assists_isl6'], 1)) * 100 if player_data['events.assists_isl6'] > 0 else player_data['events.assists_isl7'] * 10
    minutes_pct = ((player_data['minutes_played_isl7'] - player_data['minutes_played_isl6']) / 
                   max(player_data['minutes_played_isl6'], 1)) * 100 if player_data['minutes_played_isl6'] > 0 else player_data['minutes_played_isl7'] / 100

    # Cap percentage increases to avoid extremes
    goal_pct = min(goal_pct, 200)  # Max 200% improvement
    assist_pct = min(assist_pct, 200)
    minutes_pct = min(minutes_pct, 200)

    # Baseline performance (ISL7 stats)
    baseline = (player_data['events.goals_isl7'] * 5 + player_data['events.assists_isl7'] * 5 + 
                player_data['minutes_played_isl7'] / 100)

    # Growth potential: 50% improvement + 50% current performance
    improvement_score = (goal_pct * 0.4 + assist_pct * 0.3 + minutes_pct * 0.3) / 100 * 50  # Max 50 from improvement
    performance_score = min(baseline, 50)  # Max 50 from performance
    growth_potential = max(0, min(100, improvement_score + performance_score))

    logger.info(f"Growth potential: {growth_potential:.2f}, Goal %: {goal_pct:.1f}, Assist %: {assist_pct:.1f}, "
                f"Minutes %: {minutes_pct:.1f}, Baseline: {baseline:.1f}")
    return growth_potential

# Predict growth for a specific player
def predict_growth(player):
    df = load_player_data()
    player_name = player.get('name', 'Unknown').strip().lower()
    
    # Correctly filter DataFrame for ISL6 and ISL7 seasons
    df_isl6 = df[(df['season'] == 'ISL6') & (df['name'] == player_name)]
    df_isl7 = df[(df['season'] == 'ISL7') & (df['name'] == player_name)]
    
    logger.info(f"ISL6 rows: {len(df_isl6)}, ISL7 rows: {len(df_isl7)}")
    if df_isl6.empty and df_isl7.empty:
        logger.warning(f"No data for {player_name}.")
        return 0, None, {'summary': 'No data available.'}
    
    player_isl6 = df_isl6.iloc[0].to_dict() if not df_isl6.empty else {'name': player_name, 'events.goals': 0, 'events.assists': 0, 'minutes_played': 0, 'events.shots_on_target': 0}
    player_isl7 = df_isl7.iloc[0].to_dict() if not df_isl7.empty else {'name': player_name, 'events.goals': 0, 'events.assists': 0, 'minutes_played': 0, 'events.shots_on_target': 0}
    
    prediction = predict_growth_for_player(player_isl6, player_isl7)
    
    plt.figure(figsize=(6, 4))
    goals = [player_isl6.get('events.goals', 0), player_isl7.get('events.goals', 0)]
    plt.bar(['ISL6', 'ISL7'], goals, color=['blue', 'green'])
    plt.title(f"Goals for {player_name}", color="white")
    plt.gca().set_facecolor("#102131")
    plt.gcf().set_facecolor("#102131")
    plt.tick_params(colors="white")
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    visualization = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close()
    
    analysis = {
        'summary': f"{player_name} growth potential: {prediction:.2f}.",
        'key_factors': {'goals_isl6': goals[0], 'goals_isl7': goals[1], 'growth_potential': prediction}
    }
    return prediction, visualization, analysis

# Main execution
if __name__ == "__main__":
    df = load_player_data()
    df = engineer_features(df)
    X, y, common_players = prepare_model_data(df)
    if X is not None:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        logger.info(f"Feature importance: {dict(zip(X.columns, model.feature_importances_))}")
    
    player = {'name': 'Player A', 'tour_name': 'ISL 2021-22'}
    prediction, visualization, analysis = predict_growth(player)
    logger.info(f"Prediction for Player A: {prediction:.2f}, Analysis: {analysis}")