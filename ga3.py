import pandas as pd
import numpy as np
from random import sample, choices, randint

# Load dataset
df = pd.read_csv("cleaned_player_stats_with_matches_played.csv")

def get_squad(venue_name, manual_players):
    """Filter dataset for selected venue and players"""
    venue_df = df[df['Venue'] == venue_name].copy()
    squad = venue_df[venue_df["Player"].isin(manual_players)].copy()
    
    # Calculate fitness scores
    squad["fitness_score"] = squad.apply(player_fitness, axis=1)
    return squad

def player_fitness(player):
    """Calculate individual player fitness score"""
    return (
        player["batting_average"] * 1.5 +
        player["total_runs"] * 0.05 +
        player["total_wickets"] * 4 - 
        player["economy"] * 1.2
    )

def is_valid_xi(team_df):
    """Check if team meets composition requirements"""
    roles = team_df["Role"].value_counts()
    foreign_players = (team_df["Country"] != "India").sum()
    
    return (
        roles.get("Batter", 0) >= 3 and
        roles.get("Wicket-Keeper", 0) >= 1 and
        roles.get("Bowler", 0) >= 3 and
        roles.get("All-Rounder", 0) >= 1 and
        foreign_players <= 4 and
        len(team_df) == 11
    )

def initialize_population(squad, population_size=50):
    """Create initial population of random teams"""
    population = []
    player_indices = list(squad.index)
    
    for _ in range(population_size):
        team_indices = sample(player_indices, 11)
        population.append(team_indices)
    
    return population

def calculate_fitness(population, squad):
    """Calculate fitness scores for each team in population"""
    fitness_scores = []
    for team_indices in population:
        team = squad.loc[team_indices]
        if is_valid_xi(team):
            fitness = team["fitness_score"].sum()
        else:
            fitness = -1000  # Penalize invalid teams
        fitness_scores.append(fitness)
    
    return fitness_scores

def selection(population, fitness_scores, num_parents=20):
    """Select parents for next generation using tournament selection"""
    parents = []
    for _ in range(num_parents):
        # Randomly select 3 teams and pick the best one
        tournament = choices(range(len(population)), k=3)
        best_in_tournament = max(tournament, key=lambda x: fitness_scores[x])
        parents.append(population[best_in_tournament])
    
    return parents

def crossover(parent1, parent2, squad):
    """Create child team by combining parts of parent teams"""
    # Take 6 players from parent1 and 5 from parent2
    child = parent1[:6] + parent2[6:11]
    
    # Ensure exactly 11 unique players
    if len(set(child)) < 11:
        # If duplicates exist, fill with random players not in the team
        available_players = list(set(squad.index) - set(child))
        needed = 11 - len(set(child))
        if available_players and needed > 0:
            child = list(set(child)) + sample(available_players, min(needed, len(available_players)))
    
    return child[:11]  # Ensure exactly 11 players

def mutation(team_indices, squad, mutation_rate=0.1):
    """Randomly swap a player with probability mutation_rate"""
    if np.random.random() < mutation_rate and len(team_indices) == 11:
        # Select the index of the player to swap
        swap_idx = randint(0, 10)

        # Available players that are not already in the team
        available_players = list(set(squad.index) - set(team_indices))

        if available_players:
            # Create a new list of team indices
            new_team = team_indices.copy()
            new_player = sample(available_players, 1)[0]
            new_team[swap_idx] = new_player
            return new_team
    
    return team_indices

def genetic_algorithm(squad, generations=100, population_size=50):
    """Main genetic algorithm loop"""
    # Ensure squad has at least 12 players
    if len(squad) < 12:
        print("Warning: Squad size is less than 12. Some players will be in both XI and impact player position.")
    
    population = initialize_population(squad, population_size)
    
    best_fitness = -float('inf')
    best_team = None
    
    for generation in range(generations):
        fitness_scores = calculate_fitness(population, squad)
        
        # Track best team across all generations
        current_best_idx = np.argmax(fitness_scores)
        if fitness_scores[current_best_idx] > best_fitness:
            best_fitness = fitness_scores[current_best_idx]
            best_team = population[current_best_idx]
        
        # Select parents
        parents = selection(population, fitness_scores)
        
        # Create next generation
        next_generation = []
        while len(next_generation) < population_size:
            parent1, parent2 = sample(parents, 2)
            child = crossover(parent1, parent2, squad)
            child = mutation(child, squad)
            if len(child) == 11:  # Only add valid teams
                next_generation.append(child)
        
        population = next_generation
    
    # Return the best team found across all generations
    best_xi = squad.loc[best_team]
    
    # Select impact player (best remaining player not in XI)
    remaining_players = squad[~squad.index.isin(best_team)]
    
    if len(remaining_players) > 0:
        best_12th = remaining_players.loc[remaining_players["fitness_score"].idxmax()]
    else:
        # If no remaining players, just duplicate the best player from XI
        best_12th = best_xi.loc[best_xi["fitness_score"].idxmax()].copy()
        print("\n⚠️ Warning: No remaining players for 12th man. Selecting best player from XI as impact player.")
    
    return best_xi, best_12th

# Example usage
venue_name = "Wankhede Stadium, Mumbai"
manual_players = ["A Badoni", "AD Russell", "HH Pandya", "JJ Bumrah", 
                 "KL Rahul", "Ishan Kishan", "R Jadeja", "J Archer",
                 "R Pant", "V Kohli", "MS Dhoni", "B Kumar",
                 "S Dhawan", "R Sharma", "H Pandya", "Y Chahal",
                 "M Shami", "D Warner", "A Rashid", "Q de Kock"]

squad = get_squad(venue_name, manual_players)
best_xi, best_12th = genetic_algorithm(squad)

# Display results
display_cols = ["Player", "Role", "Country", "matches_played", "batting_average", 
               "total_runs", "total_wickets", "economy", "fitness_score"]

print("\n🏏 Final Playing XI:")
print(best_xi[display_cols].reset_index(drop=True).to_string(index=False))

print("\n🧢 12th Man (Impact Player):")
print(best_12th[display_cols].to_frame().T.to_string(index=False))

print(f"\n🔥 Total Fitness Score (XI only): {round(best_xi['fitness_score'].sum(), 2)}")