import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from ranking import (
    rank_goalkeepers,
    rank_defenders,
    rank_forwards,
    rank_midfielders,
    get_player_by_name,
    rank_by_goals,
    rank_by_assists,
    rank_by_passes,
    rank_by_saves,
)
from compare import get_all_players, get_player_stats
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import flask_sqlalchemy
from predict import predict_growth
from marketvalue_predict import predict_market_value

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 1800  # 30 minutes
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize db with Flask-SQLAlchemy
db = SQLAlchemy(app)
logger.info(f"Flask-SQLAlchemy version: {flask_sqlalchemy.__version__}")
logger.info(f"db type: {type(db)}")

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "error"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.before_request
def before_request():
    session.permanent = True

SEASON_TO_TOUR_NAME = {"2019–20": "ISL6", "2020–21": "ISL7"}
ISL_SEASONS = list(SEASON_TO_TOUR_NAME.keys())

indian_football_tournaments = [
    {"Tournament": "Indian Super League (ISL)", "Level": "National", "Logo": "static/images/isl_logo.png"},
    {"Tournament": "I-League", "Level": "National", "Logo": "static/images/ileague_logo.png"},
    {"Tournament": "Super Cup", "Level": "National", "Logo": "static/images/super_cup_logo.png"},
    {"Tournament": "Santosh Trophy", "Level": "National", "Logo": "static/images/santosh_trophy_logo.png"},
    {"Tournament": "Durand Cup", "Level": "National", "Logo": "static/images/durand_cup_logo.png"},
    {"Tournament": "Federation Cup", "Level": "National", "Logo": "static/images/federation_cup_logo.png"},
    {"Tournament": "I-League 2nd Division", "Level": "Regional", "Logo": "static/images/ileague_2nd_logo.png"},
    {"Tournament": "Calcutta Football League (CFL)", "Level": "Regional", "Logo": "static/images/cfl_logo.png"},
    {"Tournament": "Mizoram Premier League (MPL)", "Level": "Regional", "Logo": "static/images/mpl_logo.png"},
    {"Tournament": "Goa Professional League", "Level": "Regional", "Logo": "static/images/goa_league_logo.png"},
    {"Tournament": "Subroto Cup", "Level": "Youth", "Logo": "static/images/subroto_cup_logo.png"},
    {"Tournament": "Junior National Championships", "Level": "Youth", "Logo": "static/images/junior_national_logo.png"},
    {"Tournament": "Sub-Junior National Championships", "Level": "Youth", "Logo": "static/images/sub_junior_national_logo.png"},
]

cricket_content = {
    "tournaments": [
        {"Tournament": "IPL", "Level": "National", "Logo": "static/images/ipl_logo.png"},
        {"Tournament": "Ranji Trophy", "Level": "Regional", "Logo": "static/images/ranji_logo.png"},
    ]
}

football_content = {"tournaments": indian_football_tournaments}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        remember = request.form.get("remember", False)
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.role == role:
            login_user(user, remember=remember)
            session.permanent = True
            flash("Logged in successfully!", "success")
            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("dashboard")
            return redirect(next_page)
        else:
            flash("Invalid credentials or role!", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))
        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "error")
            return redirect(url_for("signup"))
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", football_content=football_content)

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("dashboard"))
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)

@app.route("/football", methods=["GET"])
@login_required
def football():
    return render_template("dashboard.html", football_content=football_content)

@app.route('/isl', methods=['GET'])
@login_required
def isl():
    return render_template("season_selection.html", seasons=ISL_SEASONS, position="Goalkeeper")

@app.route('/isl/rank')
def isl_rank():
    selected_season = request.args.get('season', '2023-24')
    position = request.args.get('position', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of players per page

    # Convert season to tour_name
    tour_name = SEASON_TO_TOUR_NAME.get(selected_season)
    if not tour_name:
        flash("Invalid season selected!", "error")
        return redirect(url_for("isl"))

    # Store selected season in session
    session['selected_season'] = selected_season

    # Get all players from all positions if position is 'all'
    if position == 'all':
        players = []
        ranking_functions = {
            'Goalkeeper': rank_goalkeepers,
            'Defender': rank_defenders,
            'Forward': rank_forwards,
            'Midfielder': rank_midfielders
        }
        
        for pos, func in ranking_functions.items():
            pos_players = func(tour_name=tour_name)
            for player in pos_players:
                player['position'] = pos
            players.extend(pos_players)
    else:
        # Get players for specific position
        ranking_functions = {
            'Goalkeeper': rank_goalkeepers,
            'Defender': rank_defenders,
            'Forward': rank_forwards,
            'Midfielder': rank_midfielders
        }
        
        if position in ranking_functions:
            players = ranking_functions[position](tour_name=tour_name)
            for player in players:
                player['position'] = position
        else:
            players = []

    # Calculate pagination
    total_players = len(players)
    total_pages = (total_players + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    return render_template('rank.html', 
                         players=players,
                         position=position,
                         season=selected_season,
                         current_page=page,
                         total_pages=total_pages,
                         start_index=start_index,
                         end_index=end_index)

@app.route("/isl/analytics", methods=["GET"])
@login_required
def isl_analytics():
    season = request.args.get('season', '2023-24')
    tour_name = SEASON_TO_TOUR_NAME.get(season)
    if not tour_name:
        flash("Invalid season selected!", "error")
        return redirect(url_for("isl"))

    # Get all players
    all_players = []
    all_players.extend(rank_goalkeepers(tour_name=tour_name))
    all_players.extend(rank_defenders(tour_name=tour_name))
    all_players.extend(rank_forwards(tour_name=tour_name))
    all_players.extend(rank_midfielders(tour_name=tour_name))

    if not all_players:
        return render_template("analytics.html", error="No player data available for analysis.")

    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_players)

    # Basic statistics
    avg_minutes = df["minutes_played"].mean()
    avg_score = df["score"].mean()
    team_counts = df["team_name"].value_counts().to_dict()

    # Position distribution
    position_counts = df["position"].value_counts().to_dict()

    # Top players by position
    top_goalkeepers = df[df["position"] == "Goalkeeper"].nlargest(3, "score")[["name", "team_name", "score"]].to_dict("records")
    top_defenders = df[df["position"] == "Defender"].nlargest(3, "score")[["name", "team_name", "score"]].to_dict("records")
    top_midfielders = df[df["position"] == "Midfielder"].nlargest(3, "score")[["name", "team_name", "score"]].to_dict("records")
    top_forwards = df[df["position"] == "Forward"].nlargest(3, "score")[["name", "team_name", "score"]].to_dict("records")

    # Create visualizations
    plt.style.use('dark_background')
    
    # 1. Top 5 Players by Score
    plt.figure(figsize=(10, 6))
    top_5_players = df.nlargest(5, "score")
    sns.barplot(x="score", y="name", hue="team_name", data=top_5_players, palette="viridis")
    plt.title(f"Top 5 Players by Score - {season}", color="white")
    plt.xlabel("Score", color="white")
    plt.ylabel("Player", color="white")
    plt.gca().set_facecolor("#102131")
    plt.gcf().set_facecolor("#102131")
    plt.tick_params(colors="white")
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format="png", bbox_inches="tight")
    buffer1.seek(0)
    top_players_graph = base64.b64encode(buffer1.getvalue()).decode("utf-8")
    plt.close()

    # 2. Position Distribution
    plt.figure(figsize=(8, 8))
    plt.pie(position_counts.values(), labels=position_counts.keys(), autopct='%1.1f%%', colors=sns.color_palette("viridis"))
    plt.title(f"Player Position Distribution - {season}", color="white")
    plt.gcf().set_facecolor("#102131")
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format="png", bbox_inches="tight")
    buffer2.seek(0)
    position_graph = base64.b64encode(buffer2.getvalue()).decode("utf-8")
    plt.close()

    # 3. Team Distribution
    plt.figure(figsize=(12, 6))
    sns.barplot(x=list(team_counts.keys()), y=list(team_counts.values()), palette="viridis")
    plt.title(f"Players per Team - {season}", color="white")
    plt.xlabel("Team", color="white")
    plt.ylabel("Number of Players", color="white")
    plt.xticks(rotation=45, ha='right')
    plt.gca().set_facecolor("#102131")
    plt.gcf().set_facecolor("#102131")
    plt.tick_params(colors="white")
    buffer3 = io.BytesIO()
    plt.savefig(buffer3, format="png", bbox_inches="tight")
    buffer3.seek(0)
    team_graph = base64.b64encode(buffer3.getvalue()).decode("utf-8")
    plt.close()

    return render_template(
        "analytics.html",
        avg_minutes=round(avg_minutes, 2),
        avg_score=round(avg_score, 2),
        team_counts=team_counts,
        position_counts=position_counts,
        top_goalkeepers=top_goalkeepers,
        top_defenders=top_defenders,
        top_midfielders=top_midfielders,
        top_forwards=top_forwards,
        top_players_graph=top_players_graph,
        position_graph=position_graph,
        team_graph=team_graph,
        season=season,
        seasons=ISL_SEASONS
    )

@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    season = request.args.get("season") or session.get("selected_season", "2023-24")
    if season not in ["2019–20", "2020–21", "2021–22", "2022–23", "2023-24"]:
        flash("Invalid season selected", "error")
        return redirect(url_for("isl"))
    
    # Convert season to tour_name
    tour_name = SEASON_TO_TOUR_NAME.get(season)
    if not tour_name:
        flash("Invalid season selected", "error")
        return redirect(url_for("isl"))
    
    # Store selected season in session
    session["selected_season"] = season
    
    # Get all players for the dropdown
    players = get_all_players(tour_name=tour_name)
    
    if request.method == "POST":
        player1_name = request.form.get("player1")
        player2_name = request.form.get("player2")
        position = request.form.get("position")
        
        if not player1_name or not player2_name or not position:
            flash("Please select both players and their position", "error")
            return redirect(url_for("compare", season=season))
        
        if player1_name == player2_name:
            flash("Please select different players to compare", "error")
            return redirect(url_for("compare", season=season))
        
        player1 = get_player_stats(player1_name, tour_name=tour_name)
        player2 = get_player_stats(player2_name, tour_name=tour_name)
        
        if not player1 or not player2:
            flash("One or both players not found", "error")
            return redirect(url_for("compare", season=season))
            
        # Verify players are of the same position
        if player1.get("position") != position or player2.get("position") != position:
            flash("Players must be of the same position", "error")
            return redirect(url_for("compare", season=season))
        
        # Define stats to compare based on position
        stats_to_compare = []
        if position == "Goalkeeper":
            stats_to_compare = [
                {"name": "minutes_played", "display": "Minutes Played", "better": "higher"},
                {"name": "clean_sheets", "display": "Clean Sheets", "better": "higher"},
                {"name": "goals_conceded", "display": "Goals Conceded", "better": "lower"},
                {"name": "saves", "display": "Saves", "better": "higher"}
            ]
        elif position == "Defender":
            stats_to_compare = [
                {"name": "minutes_played", "display": "Minutes Played", "better": "higher"},
                {"name": "goals", "display": "Goals", "better": "higher"},
                {"name": "assists", "display": "Assists", "better": "higher"},
                {"name": "clean_sheets", "display": "Clean Sheets", "better": "higher"},
                {"name": "tackles_won", "display": "Tackles Won", "better": "higher"},
                {"name": "interceptions", "display": "Interceptions", "better": "higher"},
                {"name": "clearances", "display": "Clearances", "better": "higher"}
            ]
        elif position == "Midfielder":
            stats_to_compare = [
                {"name": "minutes_played", "display": "Minutes Played", "better": "higher"},
                {"name": "goals", "display": "Goals", "better": "higher"},
                {"name": "assists", "display": "Assists", "better": "higher"},
                {"name": "passes", "display": "Passes", "better": "higher"},
                {"name": "chances_created", "display": "Chances Created", "better": "higher"},
                {"name": "tackles_won", "display": "Tackles Won", "better": "higher"},
                {"name": "interceptions", "display": "Interceptions", "better": "higher"}
            ]
        elif position == "Forward":
            stats_to_compare = [
                {"name": "minutes_played", "display": "Minutes Played", "better": "higher"},
                {"name": "goals", "display": "Goals", "better": "higher"},
                {"name": "assists", "display": "Assists", "better": "higher"},
                {"name": "shots_on_target", "display": "Shots on Target", "better": "higher"},
                {"name": "chances_created", "display": "Chances Created", "better": "higher"}
            ]
        
        return render_template(
            "compare.html",
            player1=player1,
            player2=player2,
            stats_to_compare=stats_to_compare,
            players=players,
            season=season,
            seasons=["2019–20", "2020–21", "2021–22", "2022–23", "2023-24"]
        )
    
    # GET request - show the comparison form
    return render_template(
        "compare.html",
        players=players,
        season=season,
        seasons=["2019–20", "2020–21", "2021–22", "2022–23", "2023-24"]
    )

@app.route('/player/<player_name>', methods=['GET'])
@login_required
def player_profile(player_name):
    season = request.args.get('season') or session.get('selected_season')
    if not season:
        return render_template("season_selection.html", seasons=ISL_SEASONS, position="Player Profile")
    if request.args.get('season'):
        session['selected_season'] = season
    tour_name = SEASON_TO_TOUR_NAME.get(season)
    player = get_player_by_name(player_name, tour_name=tour_name)
    if not player:
        flash("Player not found!", "error")
        return redirect(url_for("isl"))
    return render_template("player_profile.html", player=player, season=season)

@app.route('/predict/growth/<player_name>', methods=['GET'])
@login_required
def predict_growth_route(player_name):
    season = request.args.get('season') or session.get('selected_season')
    if not season:
        return render_template("season_selection.html", seasons=ISL_SEASONS, position="Growth Prediction")
    tour_name = SEASON_TO_TOUR_NAME.get(season)
    player = get_player_by_name(player_name, tour_name=tour_name)
    if not player:
        flash("Player not found!", "error")
        return redirect(url_for("isl"))
    
    # Debug: Log the player dictionary
    logger.info(f"Player data for {player_name}: {player}")
    
    # Get the growth prediction, visualization, and analysis
    prediction, visualization, analysis = predict_growth(player)
    
    return render_template(
        "predict.html",
        player=player,
        prediction=prediction,
        visualization=visualization,
        analysis=analysis,
        type="Growth",
        season=season
    )

@app.route('/isl/stats', methods=['GET'])
@login_required
def isl_stats():
    season = request.args.get('season') or session.get('selected_season')
    if not season:
        return render_template("season_selection.html", seasons=ISL_SEASONS, position="Stats")
    if request.args.get('season'):
        session['selected_season'] = season
    tour_name = SEASON_TO_TOUR_NAME.get(season)
    if not tour_name:
        flash("Invalid season selected!", "error")
        return redirect(url_for("isl"))
    goals_rank = rank_by_goals(tour_name=tour_name)
    assists_rank = rank_by_assists(tour_name=tour_name)
    passes_rank = rank_by_passes(tour_name=tour_name)
    saves_rank = rank_by_saves(tour_name=tour_name)
    return render_template(
        "stats.html",
        goals_rank=goals_rank,
        assists_rank=assists_rank,
        passes_rank=passes_rank,
        saves_rank=saves_rank,
        season=season
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)