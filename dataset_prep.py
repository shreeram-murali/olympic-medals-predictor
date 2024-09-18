import pandas as pd

# Read the Olympic medals CSV file
medals_df = pd.read_csv('dataset/olympic_medals.csv')

# Read the Olympic hosts CSV file
hosts_df = pd.read_csv('dataset/olympic_hosts.csv')

# Filter the hosts dataframe to include only Summer Olympics
summer_games = hosts_df[hosts_df['game_season'] == 'Summer']

# Create a list of Summer Olympic slug names
summer_slugs = summer_games['game_slug'].tolist()

# Filter the medals dataframe to include only Summer Olympics
summer_medals_df = medals_df[medals_df['slug_game'].isin(summer_slugs)]

# Group by country, game (year), and medal type, then count the medals
medal_counts = summer_medals_df.groupby(['country_name', 'country_code', 'slug_game', 'medal_type']).size().unstack(fill_value=0)

# Calculate the total medal count
medal_counts['total_medal_count'] = medal_counts.sum(axis=1)

# Reset the index to make country_name, country_code, and slug_game regular columns
medal_counts = medal_counts.reset_index()

# Select only the required columns
result = medal_counts[['country_name', 'country_code', 'slug_game', 'total_medal_count']]

# Sort the results by total medal count in descending order
result = result.sort_values(['slug_game', 'total_medal_count'], ascending=[True, False])

# Save the result to a new CSV file
result.to_csv('summer_olympic_medal_tally.csv', index=False)

# Display the first few rows of the result
print(result.head(10))