import pandas as pd
import random
import os

# Load data from CSV files
def load_data():
    batter_file = r"D:\Cricket Project\Dataset\batter stats in venue.csv"
    bowler_file = r"D:\Cricket Project\Dataset\bower stats in venue.csv"

    if not os.path.exists(batter_file) or not os.path.exists(bowler_file):
        print("Error: One or more dataset files are missing. Ensure the files are in the correct directory.")
        return None, None

    try:
        batter_stats = pd.read_csv(batter_file)
        bowler_stats = pd.read_csv(bowler_file)

        required_columns = {'Player', 'Venue', 'Performance'}
        for df, name in zip([batter_stats, bowler_stats], ['batter_stats', 'bowler_stats']):
            if not required_columns.issubset(df.columns):
                print(f"Error: Missing required columns in {name}. Expected columns: {required_columns}")
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

    return batters.sort_values(by="Performance", ascending=False), bowlers.sort_values(by="Performance", ascending=False)

# Generate a valid playing XII team with unique players and correct order
def generate_team(batters, bowlers):
    """Generate a team ensuring no duplicate players, with batters first and bowlers after."""
    batter_list = batters['Player'].unique().tolist()
    bowler_list = bowlers['Player'].unique().tolist()

    # Ensure minimum number of batters and bowlers
    if len(batter_list) < 7 or len(bowler_list) < 4:
        return []

    # Select top 7 batters and top 4 bowlers (instead of random sampling)
    selected_batters = batter_list[:7]
    selected_bowlers = bowler_list[:4]

    # Combine batters first, then bowlers
    final_team = selected_batters + selected_bowlers

    # Select 12th man (ensuring uniqueness)
    remaining_players = list(set(batter_list + bowler_list) - set(final_team))
    if remaining_players:
        final_team.append(remaining_players[0])  # Pick the next best player

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

    print("\n🏏 **Best Playing XII (Batters First, Bowlers After):**")
    for i, player in enumerate(best_xii, 1):
        if i == 12:
            print(f"\n🔹 **12th Man:** {player}")
        else:
            print(f"{i}. {player}")

if __name__ == "__main__":
    main()
