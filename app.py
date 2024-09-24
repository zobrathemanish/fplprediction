from flask import Flask, render_template
import requests
import pandas as pd

app = Flask(__name__)

def get_gameweek():
    bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(bootstrap_url)
    
    if response.status_code == 200:
        data = response.json()
        return data['events']  # List of gameweek events
    else:
        return None

# Function to fetch player data from FPL API
def get_player_data():
    bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(bootstrap_url)
    
    if response.status_code == 200:
        data = response.json()
        players = pd.DataFrame(data['elements'])  # Player data
        return players
    else:
        return None

@app.route('/')
def display_players():
    # Fetch the player data
    players_df = get_player_data()

    # Fetch the current gameweek
    gameweek_data = get_gameweek()
    current_gameweek = None
    if gameweek_data:
        current_gameweek_info = next((gw for gw in gameweek_data if gw['is_current']), None)
        if current_gameweek_info:
            current_gameweek = current_gameweek_info['id']    

    # Remove the .jpg extension from the 'photo' field
    players_df['photo'] = players_df['photo'].str.replace('.jpg', '', regex=False)

    columns = ['web_name', 'ep_this', 'photo', 
               'expected_goals', 'expected_assists', 'expected_goal_involvements']
    # Reduce to important columns and sort by expected points
    player_df_reduced = players_df[columns]
    numeric_columns = ['ep_this', 'expected_goals', 'expected_assists', 'expected_goal_involvements']

    for column in numeric_columns:
        # Convert to numeric, forcing errors to NaN
        player_df_reduced[column] = pd.to_numeric(players_df[column], errors='coerce')
        # Round and convert to int, filling NaN with 0 if needed
        player_df_reduced[column] = player_df_reduced[column].fillna(0).round(0).astype(int)
        
    # Sort the DataFrame by 'ep_this' in descending order
    player_df_reduced = player_df_reduced.sort_values(by='ep_this', ascending=False)

    # Convert the DataFrame to a list of dictionaries for rendering in the HTML template
    player_data = player_df_reduced.to_dict(orient='records')

    # Render the data in the HTML template
    return render_template('players.html', players=player_data, current_gameweek=current_gameweek)

if __name__ == '__main__':
    app.run(debug=True)
