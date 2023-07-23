import pandas as pd

# Read the CPI data from the CSV file
data = pd.read_csv('Data/filtered_data_cpi.csv', delimiter=';')

# Convert the 'Date' column to datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Sort the data by date in ascending order
data.sort_values('Date', inplace=True)

# Calculate the rate of inflation as the percentage change in the price_change column
data['Inflation'] = data['price_change'].pct_change() * 100

# Create a new DataFrame with only the 'Date' and 'Inflation' columns
inflation_data = data[['Date', 'Inflation']]

# Exclude line 2 corresponding to date 2017-01-01
inflation_data = inflation_data[inflation_data['Date'] != '2017-01-01']

# Save the new DataFrame to a CSV file with ';' as the separator
inflation_data.to_csv('Data/filtered_data_cpi_inflation.csv', sep=';', index=False)
