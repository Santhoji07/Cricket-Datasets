import pandas as pd
import random

# Step 1: Load your cleaned dataset
df = pd.read_csv("cleaned_player_stats_with_matches_played.csv")
print("✅ Dataset loaded. Total rows:", len(df))

# Step 2: Choose the venue
venue_name = "Eden Gardens, Kolkata"  # ← Change this if needed
venue_df = df[df['Venue'] == venue_name].copy()
print(f"📍 Players found for venue '{venue_name}':", len(venue_df))

# Step 3: Group players by role
batters = venue_df[venue_df["Role"] == "Batter"]
keepers = venue_df[venue_df["Role"] == "Wicket-Keeper"]
bowlers = venue_df[venue_df["Role"] == "Bowler"]
all_rounders = venue_df[venue_df["Role"] == "All-Rounder"]

print("👥 Role counts:")
print("  Batters:", len(batters))
print("  Keepers:", len(keepers))
print("  Bowlers:", len(bowlers))
print("  All-Rounders:", len(all_rounders))

# Step 3.5: Check if enough players are available
if len(batters) < 5 or len(keepers) < 1 or len(bowlers) < 3 or len(all_rounders) < 2:
    print("❌ Not enough players for one or more roles. Try a different venue or adjust role requirements.")
    exit()

# Step 4: Function to generate a random valid team
def generate_random_team():
    try:
        team = pd.concat([
            batters.sample(5),
            keepers.sample(1),
            bowlers.sample(3),
            all_rounders.sample(2)
        ])
        return team
    except:
        return None

# Step 5: Fitness score of a team (calculated directly from player stats)
def team_fitness(team):
    if team is None or len(team) != 11:
        return 0
    return (
        team["batting_average"].sum() * 1.5 +
        team["total_runs"].sum() * 0.05 +
        team["total_wickets"].sum() * 4 -
        team["economy"].sum() * 1.2
    )

# Step 6: Initialize population of random teams
population = []
print("⏳ Generating initial population...")
while len(population) < 50:
    team = generate_random_team()
    if team is not None and len(team) == 11:
        population.append(team)
print("✅ Population generated.")

# Step 7: Genetic Algorithm loop (50 generations)
for generation in range(50):
    population.sort(key=team_fitness, reverse=True)
    next_gen = population[:10]

    while len(next_gen) < 50:
        parent1 = random.choice(next_gen)
        parent2 = random.choice(next_gen)

        combined = pd.concat([
            parent1.sample(6, replace=False),
            parent2.sample(5, replace=False)
        ])

        # Update this line if your player column is not "Player_bat"
        combined = combined.drop_duplicates(subset='Player_bat')

        if len(combined) == 11:
            roles = combined["Role"].value_counts()
            if (
                roles.get("Batter", 0) == 5 and
                roles.get("Wicket-Keeper", 0) == 1 and
                roles.get("Bowler", 0) == 3 and
                roles.get("All-Rounder", 0) == 2
            ):
                next_gen.append(combined)

    population = next_gen

# Step 8: Display the best team
if population:
    best_team = population[0]
    print("\n🏆 Best Playing XI for", venue_name)
    print(best_team[["Player_bat", "Role", "batting_average", "total_runs", "total_wickets", "economy"]])
    print("\n🔥 Total Fitness Score:", round(team_fitness(best_team), 2))
else:
    print("❌ No valid teams were generated.")
