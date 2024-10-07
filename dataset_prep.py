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
    elif type(x) == str:
        if x.isnumeric() or x.lstrip('-').isnumeric():
            return float(x)
        if '\u2212' in x:
            return float(x.replace('\u2212', '-'))
        if '\u2013' in x:
            return float(x.replace('\u2013', '-'))
        if 'k' in x:
            if len(x) > 1:
                return float(x.replace('k', '')) * 1000
            return 1000.0
        if 'M' in x:
            if len(x) > 1:
                return float(x.replace('M', '')) * 1000000
            return 1000000.0
        if 'B' in x:
            return float(x.replace('B', '')) * 1000000000  
    else:
        raise ValueError(f'Cannot convert {x} to float')

def interpolate_years(df: pd.DataFrame, year_range: tuple, fill_value=None) -> pd.DataFrame:
    """
    Function to interpolate values for missing years in the dataframe. 
    If all the entries for a country are missing, we set them to fill_value.
    Input
        df: pandas DataFrame
        year_range: tuple of two integers (start_year, end_year)
        fill_value: value to fill for countries with all missing values 
    Output:
        df: pandas DataFrame with interpolated values for missing years
    Usage:
        df = interpolate_years(df, (1952, 2021))
    """
    all_years = list(range(year_range[0], year_range[1]))

    for year in all_years:
        if str(year) not in df.columns:
            df[str(year)] = np.nan
    
    year_columns = [str(year) for year in all_years]
    df = df[['country'] + year_columns]

    for year in year_columns:
        df[year] = df[year].apply(value_to_float)

    for i, row in df.iterrows():
        numeric_data = pd.to_numeric(row[year_columns], errors='coerce')
        if numeric_data.isna().all():
            df.loc[i, year_columns] = fill_value
        else:
            interpolated = numeric_data.interpolate(method='linear', limit_direction='both')
            first_valid = interpolated.first_valid_index()
            last_valid = interpolated.last_valid_index()
        
            if first_valid is not None and last_valid is not None:
                interpolated.loc[:first_valid] = interpolated.loc[first_valid]
                interpolated.loc[last_valid:] = interpolated.loc[last_valid]
            
            df.loc[i, year_columns] = interpolated
    
    return df

def standardize_country_names(df, country_col='country'):
    """
    Function to replace mismatched country names to a standarised one. 
    Input:
        - df: dataframe 
        - country_col: string that represents the country column in said dataframe
    Output:
        - dataframe
    """
    country_mapping = {
        'United States of America': 'USA',
        'United States': 'USA',
        'Russian Federation': 'Russia',
        "ROC": 'Russia', 
        'Great Britain': 'UK',
        "People's Republic of China": 'China', 
        "United Arab Emirates": 'UAE', 
        "Syrian Arab Republic": 'Syria', 
        "Republic of Korea": 'South Korea', 
        "Democratic People's Republic of Korea": 'North Korea', 
        "United Republic of Tanzania": 'Tanzania', 
        "Federal Republic of Germany": 'Germany', 
        "German Democratic Republic (Germany)": 'Germany', 
        "Republic of Moldova": 'Moldova', 
        "Côte d'Ivoire": "Cote d'Ivoire", 
        "Islamic Republic of Iran": 'Iran', 
    }
    df[country_col] = df[country_col].replace(country_mapping)
    return df

def check_country_mismatches(df_list, country_col='country'):
    all_countries = set()
    for df in df_list:
        all_countries.update(df[country_col].unique())
    
    for df in df_list:
        missing_countries = all_countries - set(df[country_col].unique())
        if missing_countries:
            print(f"Countries missing in {df.name if hasattr(df, 'name') else 'a dataframe'}:")
            print(missing_countries)
            print()


def main():
    # Read the CSV files
    medals_df = pd.read_csv('dataset/summer_olympic_medal_tally_updated.csv')
    pop_df = pd.read_csv('dataset/pop.csv')
    lex_df = pd.read_csv('dataset/lex.csv')
    pop_20_39_df = pd.read_csv('dataset/population_aged_20_39_years_both_sexes_percent.csv')
    gdp_df = pd.read_csv('dataset/gdp_pcap.csv')
    area_df = pd.read_csv('dataset/surface_area_sq_km.csv')
    urban_df = pd.read_csv('dataset/urban_population_percent_of_total.csv')
    bmi_df = pd.read_csv('dataset/body_mass_index_bmi_men_kgperm2.csv')
    democracy_df = pd.read_csv('dataset/democracy_score.csv')

    # Standardise the country names in medals_df
    medals_df = standardize_country_names(medals_df, 'country_name')

    # Calculate mean BMI for each country
    bmi_mean = bmi_df.set_index('country').mean(axis=1).to_dict()

    # Interpolate missing values for the democracy score, area, and urban population dataframes
    democracy_df = interpolate_years(democracy_df, (1952, 2021), fill_value=-10)
    area_df = interpolate_years(area_df, (1952, 2021))
    urban_df = interpolate_years(urban_df, (1952, 2021))

    # Melt the dataframes to have year as a column
    pop_df = pd.melt(pop_df, id_vars=['country'], var_name='year', value_name='population')
    lex_df = pd.melt(lex_df, id_vars=['country'], var_name='year', value_name='life_expectancy')
    pop_20_39_df = pd.melt(pop_20_39_df, id_vars=['country'], var_name='year', value_name='pop_20_39_percent')
    gdp_df = pd.melt(gdp_df, id_vars=['country'], var_name='year', value_name='gdp_per_capita')
    area_df = pd.melt(area_df, id_vars=['country'], var_name='year', value_name='surface_area_sq_km')
    urban_df = pd.melt(urban_df, id_vars=['country'], var_name='year', value_name='urban_population_percent')
    bmi_df = pd.melt(bmi_df, id_vars=['country'], var_name='year', value_name='bmi')
    democracy_df = pd.melt(democracy_df, id_vars=['country'], var_name='year', value_name='democracy_score')

    # Convert year to int
    for df in [pop_df, lex_df, pop_20_39_df, gdp_df, area_df, urban_df, bmi_df, democracy_df]:
        df['year'] = df['year'].astype(int)

    # Apply value_to_float function to population and gdp_per_capita columns
    pop_df['population'] = pop_df['population'].apply(value_to_float)
    gdp_df['gdp_per_capita'] = gdp_df['gdp_per_capita'].apply(value_to_float)
    area_df['surface_area_sq_km'] = area_df['surface_area_sq_km'].apply(value_to_float)
    democracy_df['democracy_score'] = democracy_df['democracy_score'].apply(value_to_float)

    # Merge all dataframes
    final_df = medals_df.copy()
    # for df in [pop_df, lex_df, pop_20_39_df, gdp_df, area_df, urban_df, bmi_df]:
    for df in [pop_df, lex_df, pop_20_39_df, gdp_df, area_df, urban_df, democracy_df]:
        final_df = final_df.merge(df, left_on=['country_name', 'year'], right_on=['country', 'year'], how='left')
        final_df = final_df.drop('country', axis=1)  # Drop the redundant 'country' column after each merge

    # Handle missing values
    final_df = final_df.dropna() # Drop rows with missing values
    # final_df = final_df.interpolate() # Interpolate missing values

    # Convert data types as needed
    final_df['total_medal_count'] = final_df['total_medal_count'].astype(int)
    final_df['hosting_status'] = final_df['hosting_status'].astype(int)
    final_df['population'] = final_df['population'].astype(int)
    final_df['gdp_per_capita'] = final_df['gdp_per_capita'].astype(int)
    final_df['life_expectancy'] = final_df['life_expectancy'].astype(float)
    final_df['pop_20_39_percent'] = final_df['pop_20_39_percent'].astype(float)
    final_df['area_sq_km'] = final_df['surface_area_sq_km'].astype(int)
    final_df['urban_population_percent'] = final_df['urban_population_percent'].astype(float)
    final_df['bmi_mean'] = final_df['country_name'].map(bmi_mean).astype(float)
    final_df['democracy_score'] = final_df['democracy_score'].astype(int)

    # Reorder columns
    column_order = ['country_name', 'country_code_2', 'country_code_3', 'year', 'hosting_status', 'population', 
                    'gdp_per_capita', 'life_expectancy', 'pop_20_39_percent', 'urban_population_percent', 'bmi_mean',
                    'area_sq_km', 'democracy_score', 'total_medal_count', 'slug_game']
    final_df = final_df[column_order]

    # Save the final dataframe to a CSV file
    final_df = final_df.dropna()
    print(final_df.head())
    print(final_df.info())

    final_df.to_csv('olympic_analysis_data.csv', index=False)

if __name__ == '__main__':
    main()