import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_player_data():
    """Load player data from CSV."""
    try:
        df = pd.read_csv('isl_dataset.csv')
        return df
    except Exception as e:
        logger.error(f"Error loading player data: {e}")
        return pd.DataFrame()

def predict_growth(player):
    """Predict player growth potential."""
    df = load_player_data()
    player_name = player.get('name', 'Unknown').strip().lower()
    
    df_isl6 = df[(df['season'] == 'ISL6') & (df['name'].str.lower() == player_name)]
    df_isl7 = df[(df['season'] == 'ISL7') & (df['name'].str.lower() == player_name)]
    
    if df_isl6.empty and df_isl7.empty:
        return 0, None, {'summary': 'No data available for this player.', 'key_factors': {}}
    
    player_isl6 = df_isl6.iloc[0].to_dict() if not df_isl6.empty else {'events.goals': 0, 'events.assists': 0, 'minutes_played': 0}
    player_isl7 = df_isl7.iloc[0].to_dict() if not df_isl7.empty else {'events.goals': 0, 'events.assists': 0, 'minutes_played': 0}
    
    goals_diff = player_isl7.get('events.goals', 0) - player_isl6.get('events.goals', 0)
    assists_diff = player_isl7.get('events.assists', 0) - player_isl6.get('events.assists', 0)
    minutes_diff = player_isl7.get('minutes_played', 0) - player_isl6.get('minutes_played', 0)
    growth = (goals_diff * 10 + assists_diff * 5 + minutes_diff * 0.01)
    growth = max(min(growth, 100), 0)
    
    plt.figure(figsize=(6, 4))
    plt.plot(['ISL6', 'ISL7'], [player_isl6.get('events.goals', 0), player_isl7.get('events.goals', 0)], marker='o', color='b')
    plt.title(f"Goal Progression for {player['name']}")
    plt.ylabel("Goals")
    plt.gca().set_facecolor('#102131')
    plt.gcf().set_facecolor('#102131')
    plt.tick_params(colors='white')
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    visualization = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close()
    
    analysis = {
        'summary': f"Predicted growth potential for {player['name']} is {growth:.2f}% based on performance trends.",
        'key_factors': {
            'goals_difference': goals_diff,
            'assists_difference': assists_diff,
            'minutes_difference': minutes_diff,
            'growth_potential': growth
        }
    }
    return growth, visualization, analysis

def calculate_market_value(player):
    """Calculate market value based on player stats."""
    goals = float(player.get('events.goals', 0))
    assists = float(player.get('events.assists', 0))
    minutes = float(player.get('minutes_played', 0))
    shots = float(player.get('events.shots_on_target', 0))
    tackles = float(player.get('touches.successful_tackles', 0))
    base_mv = (goals * 150000) + (assists * 75000) + (minutes * 50) + (shots * 20000) + (tackles * 10000)
    return max(base_mv, 10000)

def predict_market_value(player):
    """Predict market value trend across seasons and future projection."""
    try:
        df = load_player_data()
        player_name = player.get('name', 'Unknown').strip().lower()
        
        # Fetch data for ISL6 and ISL7
        df_isl6 = df[(df['season'] == 'ISL6') & (df['name'].str.lower() == player_name)]
        df_isl7 = df[(df['season'] == 'ISL7') & (df['name'].str.lower() == player_name)]
        
        if df_isl6.empty and df_isl7.empty:
            # Use current player data if no historical data exists
            current_mv = calculate_market_value(player)
            growth_potential, _, _ = predict_growth(player)
            future_mv = current_mv * (1 + growth_potential / 100)
            seasons = ['Current', 'Future']
            values = [current_mv, future_mv]
        else:
            player_isl6 = df_isl6.iloc[0].to_dict() if not df_isl6.empty else {'events.goals': 0, 'events.assists': 0, 'minutes_played': 0}
            player_isl7 = df_isl7.iloc[0].to_dict() if not df_isl7.empty else {'events.goals': 0, 'events.assists': 0, 'minutes_played': 0}
            mv_isl6 = calculate_market_value(player_isl6)
            mv_isl7 = calculate_market_value(player_isl7)
            growth_potential, _, _ = predict_growth(player)
            current_mv = mv_isl7
            future_mv = current_mv * (1 + growth_potential / 100)
            seasons = ['ISL6', 'ISL7', 'Future']
            values = [mv_isl6, mv_isl7, future_mv]
        
        # Visualization: Line graph
        plt.figure(figsize=(10, 6))
        plt.plot(seasons, values, marker='o', color='#ff4d4d', linewidth=2, markersize=8)
        plt.title(f"Market Value Trend for {player['name']}", color="white", fontsize=14)
        plt.ylabel("Market Value (INR)", color="white", fontsize=12)
        plt.xlabel("Season", color="white", fontsize=12)
        plt.gca().set_facecolor("#102131")
        plt.gcf().set_facecolor("#102131")
        plt.tick_params(colors="white")
        plt.grid(True, linestyle='--', alpha=0.3)
        for i, value in enumerate(values):
            plt.text(i, value, f"₹{value:,.0f}", ha='center', va='bottom', color='white', fontsize=10)
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        visualization = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()
        
        trend = "rising" if future_mv > current_mv else "lowering" if future_mv < current_mv else "stable"
        analysis = {
            'summary': f"{player['name']}'s market value is {trend}. Current: ₹{current_mv:,.0f}, Future: ₹{future_mv:,.0f} (based on {growth_potential:.2f}% growth).",
            'key_factors': {
                'current_market_value': current_mv,
                'future_market_value': future_mv,
                'growth_potential': growth_potential
            }
        }
        if len(seasons) > 2:  # Add historical values if available
            analysis['key_factors']['isl6_market_value'] = mv_isl6
            analysis['key_factors']['isl7_market_value'] = mv_isl7
        
        return current_mv, future_mv, visualization, analysis
    
    except Exception as e:
        logger.error(f"Error predicting market value for {player.get('name', 'Unknown')}: {e}")
        return 0, 0, None, {'summary': f"Error in prediction: {str(e)}", 'key_factors': {}}

if __name__ == "__main__":
    sample_player = {'name': 'Test Player', 'events.goals': 10, 'events.assists': 5, 'minutes_played': 1800}
    current_mv, future_mv, viz, analysis = predict_market_value(sample_player)
    logger.info(f"Current: {current_mv}, Future: {future_mv}, Analysis: {analysis}")