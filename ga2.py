import pandas as pd
from itertools import combinations

# Load dataset
df = pd.read_csv("cleaned_player_stats_with_matches_played.csv")
print("✅ Dataset loaded. Total rows:", len(df))

# Input venue
venue_name = input("Enter venue name: ").strip()
venue_df = df[df['Venue'] == venue_name].copy()

if venue_df.empty:
    print(f"❌ No data available for venue '{venue_name}'")
    exit()

print(f"📍 Players available for venue '{venue_name}':", len(venue_df))

# Enter player names manually (max 20, no duplicates)
print("\n✍️ Enter up to 20 player names for your squad (press ENTER to stop early):")
manual_players = []
manual_players_set = set()

while len(manual_players) < 20:
    name = input(f"Player {len(manual_players)+1}: ").strip()
    if not name:
        break

    name_cleaned = name.lower()

    if name_cleaned in manual_players_set:
        print("⚠️ Duplicate player. Already added.")
        continue

    matched_players = venue_df[venue_df["Player"].str.lower().str.strip() == name_cleaned]

    if not matched_players.empty:
        actual_name = matched_players.iloc[0]["Player"]
        manual_players.append(actual_name)
        manual_players_set.add(name_cleaned)
    else:
        print("❌ Player not found for this venue.")

if len(manual_players) < 12:
    print("❌ Not enough players to form a team. Need at least 12.")
    exit()

# Create squad
squad = venue_df[venue_df["Player"].isin(manual_players)].copy()

# Fitness function
def player_fitness(player):
    return (
        player["batting_average"] * 1.5 +
        player["total_runs"] * 0.05 +
        player["total_wickets"] * 4 -
        player["economy"] * 1.2
    )

squad["fitness_score"] = squad.apply(player_fitness, axis=1)

# Validation function for team structure
def is_valid_xi(team_df):
    roles = team_df["Role"].value_counts()
    foreign_players = (team_df["Country"] != "India").sum()

    return (
        roles.get("Batter", 0) == 5 and
        roles.get("Wicket-Keeper", 0) == 1 and
        roles.get("Bowler", 0) == 3 and
        roles.get("All-Rounder", 0) == 2 and
        foreign_players <= 4
    )

# Try all 12-player combinations
best_fitness = 0
best_xi = None
best_12th = None

for combo in combinations(squad.index, 12):
    team_of_12 = squad.loc[list(combo)]
    for i in range(12):
        xi = team_of_12.drop(team_of_12.index[i])
        if is_valid_xi(xi):
            fitness = xi["fitness_score"].sum()
            if fitness > best_fitness:
                best_fitness = fitness
                best_xi = xi
                best_12th = team_of_12.iloc[i]

# Display output
display_cols = [
    "Player", "Role", "Country", "matches_played",
    "batting_average", "total_runs", "total_wickets", "economy", "fitness_score"
]

if best_xi is not None:
    print("\n🏏 Final Playing XI:")
    print(best_xi[display_cols].reset_index(drop=True).to_string(index=False))

    print("\n🧢 12th Man (Impact Player):")
    print(best_12th[display_cols].to_frame().T.to_string(index=False))

    print(f"\n🔥 Total Fitness Score (XI only): {round(best_xi['fitness_score'].sum(), 2)}")
else:
    print("❌ Couldn't form a valid team with given squad.")
