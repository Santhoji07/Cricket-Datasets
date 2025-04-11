import pandas as pd

# Load your original CSV file
df = pd.read_csv("player_stats_in_venues.csv")

# Normalize the Venue column (strip trailing spaces)
df['Venue'] = df['Venue'].str.strip()

# Define aggregation rules for merging duplicate player records
aggregation_functions = {
    'p_id': 'first',
    'Country_bat': 'first',
    'matches_played_bat': 'sum',
    'total_runs': 'sum',
    'batting_average': 'mean',
    'Performance_bat': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
    'matches_played_bowl': 'sum',
    'total_runs_conceded': 'sum',
    'balls_bowled': 'sum',
    'economy': 'mean',
    'total_wickets': 'sum',
    'Bowling_Strike_Rate': 'mean',
    'Performance_bowl': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
}

# Group by Venue and Player to merge duplicate entries
df_cleaned = df.groupby(['Venue', 'Player_bat'], as_index=False).agg(aggregation_functions)

# Save the cleaned data to a new CSV
df_cleaned.to_csv("cleaned_player_stats_in_venues.csv", index=False)
print("Cleaned CSV saved as cleaned_player_stats_in_venues.csv")
