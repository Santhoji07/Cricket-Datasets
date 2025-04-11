import pandas as pd
import random
import os

# Load data from CSV files
def load_data():
    batter_file = r"D:\Cricket Project\Dataset\batter stats in venues.csv"
    bowler_file = r"D:\Cricket Project\Dataset\bowler stats in venues.csv"

    if not os.path.exists(batter_file) or not os.path.exists(bowler_file):
        print("Error: One or more dataset files are missing. Ensure the files are in the correct directory.")
        return None, None

    try:
        batter_stats = pd.read_csv(batter_file)
        bowler_stats = pd.read_csv(bowler_file)

        required_batter_columns = {'Player', 'Venue', 'Country', 'matches_played', 'total_runs', 'batting_average'}
        required_bowler_columns = {'Player', 'Venue', 'Country', 'matches_played', 'total_runs_conceded', 'balls_bowled', 'economy', 'total_wickets'}
        
        if not required_batter_columns.issubset(set(map(str.strip, batter_stats.columns))):
            print(f"Error: Missing required columns in batter_stats. Expected columns: {required_batter_columns}")
            return None, None

        if not required_bowler_columns.issubset(set(map(str.strip, bowler_stats.columns))):
            print(f"Error: Missing required columns in bowler_stats. Expected columns: {required_bowler_columns}")
            return None, None

        return batter_stats, bowler_stats

    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

# Filter players based on squad and venue
def filter_players(batter_stats, bowler_stats, squad, venue):
    if batter_stats is None or bowler_stats is None:
        return [], []
    
    batters = batter_stats[(batter_stats['Player'].isin(squad)) & (batter_stats['Venue'] == venue)]
    bowlers = bowler_stats[(bowler_stats['Player'].isin(squad)) & (bowler_stats['Venue'] == venue)]
    
    return batters, bowlers

# Generate a valid playing XII team with unique players and max 4 foreign players
def generate_team(batters, bowlers):
    """Generate a team ensuring no duplicate players, with batters first and bowlers after, and at most 4 foreign players."""
    batter_list = list(batters[['Player', 'Country']].drop_duplicates().itertuples(index=False, name=None))
    bowler_list = list(bowlers[['Player', 'Country']].drop_duplicates().itertuples(index=False, name=None))

    if len(batter_list) < 7 or len(bowler_list) < 4:
        return []

    selected_batters = []
    selected_bowlers = []
    foreign_count = 0

    def can_select(player):
        nonlocal foreign_count
        if player[1] != "India":
            if foreign_count < 4:
                foreign_count += 1
                return True
            return False
        return True

    random.shuffle(batter_list)
    for player in batter_list:
        if len(selected_batters) < 7 and can_select(player):
            selected_batters.append(player[0])
    
    random.shuffle(bowler_list)
    for player in bowler_list:
        if len(selected_bowlers) < 4 and can_select(player):
            selected_bowlers.append(player[0])

    if len(selected_batters) < 7 or len(selected_bowlers) < 4:
        return []

    final_team = selected_batters + selected_bowlers

    remaining_players = [p for p in (batter_list + bowler_list) if p[0] not in final_team]
    remaining_domestic = [p[0] for p in remaining_players if p[1] == "India"]
    remaining_foreign = [p[0] for p in remaining_players if p[1] != "India"]

    if len(final_team) < 12:
        if foreign_count < 4 and remaining_foreign:
            final_team.append(random.choice(remaining_foreign))
        elif remaining_domestic:
            final_team.append(random.choice(remaining_domestic))
    
    return final_team if len(final_team) == 12 else []

# Main function
def main():
    batter_stats, bowler_stats = load_data()
    
    if batter_stats is None or bowler_stats is None:
        print("Data loading failed. Exiting.")
        return

    squad = input("Enter squad players (comma-separated): ").strip().split(',')
    squad = [player.strip() for player in squad]

    venue = input("Enter match venue: ").strip()

    batters, bowlers = filter_players(batter_stats, bowler_stats, squad, venue)

    if len(batters) < 7 or len(bowlers) < 4:
        print("Not enough players in the squad with stats for the selected venue.")
        return

    best_xii = generate_team(batters, bowlers)

    if not best_xii:
        print("Unable to generate a valid team due to insufficient players.")
        return

    print("\nBest Playing XII (Batters First, Bowlers After, Max 4 Foreign Players):")
    for i, player in enumerate(best_xii, 1):
        player_stats = batters[batters['Player'] == player] if player in batters['Player'].values else bowlers[bowlers['Player'] == player]
        stats = player_stats.iloc[0] if not player_stats.empty else None
        
        details = f" - Matches: {stats['matches_played']}, Runs: {stats['total_runs']}" if stats is not None and 'total_runs' in stats else ""
        if stats is not None:
            if 'batting_average' in stats:
                details += f", Avg: {stats['batting_average']}"
            elif 'balls_bowled' in stats:
                details += f", Balls: {stats['balls_bowled']}, Econ: {stats['economy']}, Wkts: {stats['total_wickets']}"
        
        if i == 12:
            print(f"\n12th Man: {player}{details}")
        else:
            print(f"{i}. {player}{details}")

if __name__ == "__main__":
    main()
