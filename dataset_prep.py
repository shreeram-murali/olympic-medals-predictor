import pandas as pd
import numpy as np

def value_to_float(x):
    """
    Function to convert the values in the columns to float
    Example:
    1.2K -> 1200.0
    1.2M -> 1200000.0
    Usage:
    df['col'] = df['col'].apply(value_to_float)
    """
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0

def main():
    # Read the CSV files
    medals_df = pd.read_csv('dataset/summer_olympic_medal_tally_updated.csv')
    pop_df = pd.read_csv('dataset/pop.csv')
    lex_df = pd.read_csv('dataset/lex.csv')
    pop_20_39_df = pd.read_csv('dataset/population_aged_20_39_years_both_sexes_percent.csv')
    gdp_df = pd.read_csv('dataset/gdp_pcap.csv')
    hosts_df = pd.read_csv('dataset/olympic_hosts.csv')

    # Melt the dataframes to have year as a column
    pop_df = pd.melt(pop_df, id_vars=['country'], var_name='year', value_name='population')
    lex_df = pd.melt(lex_df, id_vars=['country'], var_name='year', value_name='life_expectancy')
    pop_20_39_df = pd.melt(pop_20_39_df, id_vars=['country'], var_name='year', value_name='pop_20_39_percent')
    gdp_df = pd.melt(gdp_df, id_vars=['country'], var_name='year', value_name='gdp_per_capita')

    # Convert year to int
    for df in [pop_df, lex_df, pop_20_39_df, gdp_df]:
        df['year'] = df['year'].astype(int)

    # Apply value_to_float function to population and gdp_per_capita columns
    pop_df['population'] = pop_df['population'].apply(value_to_float)
    gdp_df['gdp_per_capita'] = gdp_df['gdp_per_capita'].apply(value_to_float)

    # Merge all dataframes
    final_df = medals_df.copy()
    for df in [pop_df, lex_df, pop_20_39_df, gdp_df]:
        final_df = final_df.merge(df, left_on=['country_name', 'year'], right_on=['country', 'year'], how='left')
        final_df = final_df.drop('country', axis=1)  # Drop the redundant 'country' column after each merge

    # Handle missing values (you might want to use a more sophisticated method depending on your data)
    # final_df = final_df.dropna()
    final_df = final_df.interpolate()

    # Convert data types as needed
    final_df['total_medal_count'] = final_df['total_medal_count'].astype(int)
    final_df['hosting_status'] = final_df['hosting_status'].astype(int)
    final_df['population'] = final_df['population'].astype(float)
    final_df['gdp_per_capita'] = final_df['gdp_per_capita'].astype(float)
    final_df['life_expectancy'] = final_df['life_expectancy'].astype(float)
    final_df['pop_20_39_percent'] = final_df['pop_20_39_percent'].astype(float)

    # Reorder columns
    column_order = ['country_name', 'country_code_2', 'country_code_3', 'year', 'hosting_status', 'population', 
                    'gdp_per_capita', 'life_expectancy', 'pop_20_39_percent', 'total_medal_count', 'slug_game']
    final_df = final_df[column_order]

    # Display the first few rows and info about the dataframe
    print(final_df.head())
    print(final_df.info())

    # Save the final dataframe to a CSV file
    final_df.to_csv('olympic_analysis_data_interpolated.csv', index=False)

if __name__ == '__main__':
    main()