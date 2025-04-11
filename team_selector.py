import pandas as pd
import random
import os

random.seed(42)

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

        required_columns = {'Player', 'Venue', 'Country'}
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
    foreign_players = []
    domestic_players = []

    # Separate domestic and foreign players
    for player, country in batter_list + bowler_list:
        if country != "India":
            foreign_players.append(player)
        else:
            domestic_players.append(player)

    # Ensure at most 4 foreign players
    random.shuffle(foreign_players)
    selected_foreign = foreign_players[:4]

    # Fill remaining slots with domestic players
    remaining_slots = 12 - len(selected_foreign)
    random.shuffle(domestic_players)
    selected_domestic = domestic_players[:remaining_slots]

    final_team = selected_foreign + selected_domestic
    random.shuffle(final_team)

    return final_team if len(final_team) == 12 else []


# Genetic Algorithm to find the best team
def genetic_algorithm(batters, bowlers, generations=50, population_size=20):
    population = []

    for _ in range(population_size):
        team = generate_team(batters, bowlers)
        if team:
            population.append(team)

    if not population:
        return []

    for _ in range(generations):
        population = sorted(population, key=lambda team: random.random(), reverse=True)
        population = population[:10]
        new_population = population.copy()

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child = parent1[:7] + parent2[7:]
            child = list(set(child))  # Remove duplicates

            # Ensure max 4 foreign players
            foreign_players = [p for p in child if p in batters[batters['Country'] != 'India']['Player'].tolist() or 
                               p in bowlers[bowlers['Country'] != 'India']['Player'].tolist()]
            domestic_players = [p for p in child if p in batters[batters['Country'] == 'India']['Player'].tolist() or 
                                p in bowlers[bowlers['Country'] == 'India']['Player'].tolist()]

            if len(foreign_players) > 4:
                random.shuffle(foreign_players)
                foreign_players = foreign_players[:4]  # Trim extra foreign players

            remaining_slots = 12 - len(foreign_players)
            domestic_players = domestic_players[:remaining_slots]  # Fill with domestic players

            child = foreign_players + domestic_players

            while len(child) < 12:
                remaining_players = list(set(batters['Player']).union(set(bowlers['Player'])) - set(child))
                if remaining_players:
                    child.append(random.choice(remaining_players))

            new_population.append(child)

        population = new_population

    return population[0] if population else []


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

    best_xii = genetic_algorithm(batters, bowlers)

    if not best_xii:
        print("Unable to generate a valid team due to insufficient players.")
        return

    print("\nBest Playing XII (Batters First, Bowlers After, Max 4 Foreign Players):")
    for i, player in enumerate(best_xii, 1):
        if i == 12:
            print(f"\n12th Man: {player}")
        else:
            print(f"{i}. {player}")

if __name__ == "__main__":
    main()
