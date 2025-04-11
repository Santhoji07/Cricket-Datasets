import pandas as pd

# Load dataset
df = pd.read_csv('player_stats_in_venues.csv')

# Ask for the venue
venue = input("Enter the venue name: ").strip()

# Filter data for the selected venue
venue_data = df[df['Venue'].str.lower() == venue.lower()]

if venue_data.empty:
    print("No data available for this venue.")
else:
    players_in_venue = venue_data['Player_bat'].unique()

    while True:
        player_input = input("\nEnter player name (or type 'exit' to quit): ").strip()
        if player_input.lower() == 'exit':
            break

        matched_players = [p for p in players_in_venue if p.lower() == player_input.lower()]

        if not matched_players:
            suggestions = [p for p in players_in_venue if player_input.lower() in p.lower()]
            if suggestions:
                print(f"\nNo exact match found for '{player_input}'. Did you mean:")
                for idx, name in enumerate(suggestions, 1):
                    print(f"  {idx}. {name}")
                choice = input("Enter the number of the player you meant, or press Enter to try again: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                    selected_player = suggestions[int(choice) - 1]
                else:
                    print("Try again.")
                    continue
            else:
                print("No similar player names found. Try again.")
                continue
        else:
            selected_player = matched_players[0]

        # Get player data for venue
        player_data = venue_data[venue_data['Player_bat'].str.lower() == selected_player.lower()]

        print(f"\n📍 Venue: {venue}")
        print(f"👤 Player: {selected_player}")
        print("-" * 40)

        for _, row in player_data.iterrows():
            print(f"Country: {row['Country_bat']}")
            print(f"Matches Played (Bat): {row['matches_played_bat']}")
            print(f"Total Runs: {row['total_runs']}")
            print(f"Batting Average: {row['batting_average']}")
            print(f"Batting Performance: {row['Performance_bat']}")
            print(f"Matches Played (Bowl): {row['matches_played_bowl']}")
            print(f"Runs Conceded: {row['total_runs_conceded']}")
            print(f"Balls Bowled: {row['balls_bowled']}")
            print(f"Economy: {row['economy']}")
            print(f"Total Wickets: {row['total_wickets']}")
            print(f"Bowling Strike Rate: {row['Bowling_Strike_Rate']}")
            print(f"Bowling Performance: {row['Performance_bowl']}")
            print("-" * 40)
