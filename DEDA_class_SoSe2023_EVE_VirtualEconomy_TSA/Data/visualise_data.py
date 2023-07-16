import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
import datetime

# Read the CSV files
df_cpi = pd.read_csv('filtered_data_cpi.csv', delimiter=';')
df_ms = pd.read_csv('filtered_data_ms.csv', delimiter=';')

# Convert 'Date' column to datetime format
df_cpi['Date'] = pd.to_datetime(df_cpi['Date'])
df_ms['Date'] = pd.to_datetime(df_ms['Date'])

# Get the number of rows and columns in each DataFrame
rows_cpi, cols_cpi = df_cpi.shape
rows_ms, cols_ms = df_ms.shape

print(f"Size of CPI data: {rows_cpi} rows x {cols_cpi} columns")
print(f"Size of Money Supply data: {rows_ms} rows x {cols_ms} columns")

# Check the complexity (granularity) of the data
cpi_granularity = df_cpi['Date'].diff().min()
ms_granularity = df_ms['Date'].diff().min()

print(f"Complexity (granularity) of CPI data: {cpi_granularity}")
print(f"Complexity (granularity) of Money Supply data: {ms_granularity}")

# Visualize and save CPI data
plt.figure(figsize=(10, 5))
plt.plot(df_cpi['Date'], df_cpi['price_change'])
plt.title('CPI Data')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)

# Customize the x-axis ticks
locator = AutoDateLocator()
formatter = AutoDateFormatter(locator)
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

plt.tight_layout()  # Adjust the layout to prevent label cutoff
plt.savefig('Data/cpi_figure.png', transparent=True)
plt.close()

# Visualize and save Money Supply data
plt.figure(figsize=(10, 5))
plt.plot(df_ms['Date'], df_ms['MoneySupply'])
plt.title('Money Supply Data')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)

# Customize the x-axis ticks
locator = AutoDateLocator()
formatter = AutoDateFormatter(locator)
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

plt.tight_layout()  # Adjust the layout to prevent label cutoff
plt.savefig('Data/money_supply_figure.png', transparent=True)
plt.close()
