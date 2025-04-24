import pandas as pd

# Load dataset
df = pd.read_csv("cleaned_player_stats_with_matches_played.csv")
print("✅ Dataset loaded. Total rows:", len(df))

# Step 1: Input venue
venue_name = input("Enter venue name: ").strip()
venue_df = df[df['Venue'] == venue_name].copy()

if venue_df.empty:
    print(f"❌ No data available for venue '{venue_name}'")
    exit()

print(f"📍 Players available for venue '{venue_name}':", len(venue_df))

# Step 2: Manual input of up to 20 players
print("\n✍️ Enter up to 20 player names (press ENTER to stop early):")
manual_players = []
while len(manual_players) < 20:
    name = input(f"Player {len(manual_players)+1}: ").strip()
    if not name:
        break
    if name in venue_df["Player_bat"].values:
        if name not in manual_players:
            manual_players.append(name)
        else:
            print("⚠️ Player already added.")
    else:
        print("❌ Player not found for this venue.")

if len(manual_players) < 12:
    print("❌ Not enough players to form a team. Need at least 12.")
    exit()

# Step 3: Build squad DataFrame
squad = venue_df[venue_df["Player_bat"].isin(manual_players)].copy()

# Step 4: Fitness function
def player_fitness(player):
    return (
        player["batting_average"] * 1.5 +
        player["total_runs"] * 0.05 +
        player["total_wickets"] * 4 -
        player["economy"] * 1.2
    )

squad["fitness_score"] = squad.apply(player_fitness, axis=1)

# Step 5: Build valid Playing XI + 12th man
from itertools import combinations

def is_valid_xi(team_df):
    roles = team_df["Role"].value_counts()
    return (
        roles.get("Batter", 0) == 5 and
        roles.get("Wicket-Keeper", 0) == 1 and
        roles.get("Bowler", 0) == 3 and
        roles.get("All-Rounder", 0) == 2
    )

best_fitness = 0
best_xi = None
best_12th = None

# Generate all 12-player combinations
for combo in combinations(squad.index, 12):
    sub_team = squad.loc[list(combo)]
    for i in range(12):
        xi = sub_team.drop(sub_team.index[i])
        if is_valid_xi(xi):
            fitness = xi["fitness_score"].sum()
            if fitness > best_fitness:
                best_fitness = fitness
                best_xi = xi
                best_12th = sub_team.iloc[i]

# Step 6: Display result
if best_xi is not None:
    print("\n🏏 Final Playing XI:")
    print(best_xi[["Player_bat", "Role", "matches_played", "fitness_score"]])

    print("\n🧢 12th Man (Impact Player):")
    print(best_12th[["Player_bat", "Role", "matches_played", "fitness_score"]])

    print(f"\n🔥 Total Fitness Score (XI only): {round(best_xi['fitness_score'].sum(), 2)}")
else:
    print("❌ Couldn't form a valid Playing XI with provided players.")
