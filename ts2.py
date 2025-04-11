import pandas as pd
import random

def load_data(batter_file, bowler_file):
    batter_stats = pd.read_csv(batter_file)
    bowler_stats = pd.read_csv(bowler_file)
    return batter_stats, bowler_stats

def filter_by_squad_and_venue(batter_stats, bowler_stats, squad, venue):
    batters = batter_stats[(batter_stats['Venue'] == venue) & (batter_stats['Player'].isin(squad))].copy()
    bowlers = bowler_stats[(bowler_stats['Venue'] == venue) & (bowler_stats['Player'].isin(squad))].copy()
    
    combined_players = {}
    for _, row in batters.iterrows():
        combined_players[row['Player']] = row.to_dict()
    for _, row in bowlers.iterrows():
        if row['Player'] in combined_players:
            if evaluate_player(row.to_dict()) > evaluate_player(combined_players[row['Player']]):
                combined_players[row['Player']].update(row.to_dict())
        else:
            combined_players[row['Player']] = row.to_dict()
    
    return list(combined_players.values())

def evaluate_player(player):
    return (
        player.get('total_runs', 0) * 1.5 +
        player.get('batting_average', 0) * 2 +
        player.get('total_wickets', 0) * 3 +
        (100 - player.get('economy', 0)) * 1.5
    )

def fitness(team):
    return sum(evaluate_player(player) for player in team)

def initialize_population(players, size=10):
    population = []
    for _ in range(size):
        random.shuffle(players)
        team = players[:12]
        population.append(team)
    return population

def select_parents(population):
    population.sort(key=fitness, reverse=True)
    return population[:2]

def crossover(parent1, parent2):
    split = len(parent1) // 2
    child1 = parent1[:split] + parent2[split:]
    child2 = parent2[:split] + parent1[split:]
    return child1, child2

def mutate(team, players):
    if random.random() < 0.2:
        replace_idx = random.randint(0, len(team) - 1)
        potential_replacements = [p for p in players if p not in team]
        if potential_replacements:
            team[replace_idx] = random.choice(potential_replacements)
    return team

def genetic_algorithm(players, generations=20, population_size=10):
    population = initialize_population(players, population_size)
    
    for _ in range(generations):
        parents = select_parents(population)
        children = []
        for _ in range(population_size // 2):
            child1, child2 = crossover(parents[0], parents[1])
            children.append(mutate(child1, players))
            children.append(mutate(child2, players))
        population = children
    
    return select_parents(population)[0]

def display_selected_team(selected_team):
    print("\nBest Playing XII:")
    for i, player in enumerate(selected_team, 1):
        print(f"{i}. ID: {player.get('p_id', 'N/A')}, Name: {player['Player']}, Matches: {player['matches_played']}, \
                Runs Scored: {player.get('total_runs', 'N/A')}, \
                Batting Avg: {player.get('batting_average', 'N/A')}, Runs Conceded: {player.get('total_runs_conceded', 'N/A')}, \
                Balls Bowled: {player.get('balls_bowled', 'N/A')}, Economy: {player.get('economy', 'N/A')}, \
                Wickets: {player.get('total_wickets', 'N/A')}, Performance Score: {evaluate_player(player)}")

def main():
    batter_file = "batter stats in venues.csv"
    bowler_file = "bowler stats in venues.csv"
    
    squad = input("Enter squad players (comma-separated): ").strip().split(',')
    squad = [player.strip() for player in squad]
    venue = input("Enter the match venue: ").strip()
    
    batter_stats, bowler_stats = load_data(batter_file, bowler_file)
    players = filter_by_squad_and_venue(batter_stats, bowler_stats, squad, venue)
    selected_team = genetic_algorithm(players)
    display_selected_team(selected_team)

if __name__ == "__main__":
    main()
