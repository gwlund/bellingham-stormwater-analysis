import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
data = pd.read_csv('/path/to/your/data.csv')

# Identify duplicates
duplicates = data[data.duplicated(keep=False)]

# Process dates and relevant columns for E. coli and Enterococcus
data['Sample Date'] = pd.to_datetime(data['Sample Date'], errors='coerce', format='%m-%d-%y')
ecoli = data[['Sample Date', 'Site ID', 'E. coli']].dropna()
enterococcus = data[['Sample Date', 'Site ID', 'Enterococcus']].dropna()

# Sort data by date
ecoli = ecoli.sort_values('Sample Date')
enterococcus = enterococcus.sort_values('Sample Date')

# Aggregate data for plotting
ecoli_aggregated = ecoli.groupby(['Sample Date', 'Site ID'])['E. coli'].mean().unstack()
enterococcus_aggregated = enterococcus.groupby(['Sample Date', 'Site ID'])['Enterococcus'].mean().unstack()

# Plotting the control charts
fig, ax = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
ecoli_aggregated.clip(upper=5000).plot(ax=ax[0], marker='o', linestyle='-', title='E. coli Readings by Site Over Time with Clamped Values')
ax[0].set_ylabel('E. coli (cfu/100ml)')
ax[0].axhline(y=310, color='red', linestyle='--', label='Threshold (310 cfu/100ml)')
enterococcus_aggregated.plot(ax=ax[1], marker='o', linestyle='-', title='Enterococcus Readings by Site Over Time')
ax[1].set_ylabel('Enterococcus (cfu/100ml)')
ax[1].axhline(y=500, color='red', linestyle='--', label='Threshold (500 cfu/100ml)')
plt.tight_layout()
plt.show()

# Generate histograms
fig, ax = plt.subplots(figsize=(12, 8))
colors = plt.cm.viridis(np.linspace(0, 1, len(ecoli_aggregated.columns)))
for (site, values), color in zip(ecoli_aggregated.items(), colors):
    ax.hist(values.dropna(), bins=20, color=color, alpha=0.6, edgecolor='black', label=site)
ax.axvline(x=310, color='red', linestyle='--', label='Threshold (310 cfu/100ml)')
ax.set_title('E. coli Distribution Across Sites')
ax.set_xlabel('E. coli (cfu/100ml)')
ax.set_ylabel('Frequency')
ax.legend(title='Site ID')
plt.show()

# Calculate exceedances for E. coli
ecoli_exceedances = ecoli[ecoli['E. coli'] > 310]
ecoli_exceedances['Year'] = ecoli_exceedances['Sample Date'].dt.year
exceedance_counts = ecoli_exceedances.groupby(['Year', 'Site ID']).size().reset_index(name='Exceedance Count')
total_counts = ecoli.groupby([ecoli['Sample Date'].dt.year, 'Site ID']).size().reset_index(name='Total Readings')
total_counts.rename(columns={'Sample Date': 'Year'}, inplace=True)
exceedance_data = pd.merge(total_counts, exceedance_counts, on=['Year', 'Site ID'], how='left').fillna(0)
exceedance_data['Exceedance Percentage'] = (exceedance_data['Exceedance Count'] / exceedance_data['Total Readings']) * 100

print(exceedance_data)
