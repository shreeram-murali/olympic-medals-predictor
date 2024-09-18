import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('olympic_analysis_data.csv')

# 1. Number of medals vs. time (trajectory of top few countries over the years)
top_countries = df.groupby('country_name')['total_medal_count'].sum().nlargest(20).index
plt.figure(figsize=(12, 6))
for country in top_countries:
    country_data = df[df['country_name'] == country].sort_values('year')
    plt.plot(country_data['year'], country_data['total_medal_count'], label=country)
plt.title('Number of Medals Over Time for Top 5 Countries')
plt.xlabel('Year')
plt.ylabel('Number of Medals')
plt.legend()
plt.savefig('medals_over_time.png')
plt.close()

# 2. Correlation heatmap of the predictor variables
predictor_vars = ['population', 'gdp_per_capita', 'life_expectancy', 'pop_20_39_percent', 'total_medal_count']
corr_matrix = df[predictor_vars].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
plt.title('Correlation Heatmap of Predictor Variables')
plt.savefig('correlation_heatmap.png')
plt.close()

# 4. Number of medals vs. GDP per capita (scatter plot)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='gdp_per_capita', y='total_medal_count', alpha=0.6)
plt.title('Number of Medals vs GDP per Capita')
plt.xlabel('GDP per Capita')
plt.ylabel('Number of Medals')
plt.xscale('log')  # Using log scale for GDP per capita due to its wide range
plt.savefig('medals_vs_gdp.png')
plt.close()

# 5. Bonus: Box plot of medals for host vs non-host countries
plt.figure(figsize=(8, 6))
sns.boxplot(data=df, x='hosting_status', y='total_medal_count')
plt.title('Medal Distribution: Host vs Non-Host Countries')
plt.xlabel('Hosting Status (0: Non-Host, 1: Host)')
plt.ylabel('Number of Medals')
plt.savefig('medals_host_vs_nonhost.png')
plt.close()

print("Graphs have been generated and saved.")