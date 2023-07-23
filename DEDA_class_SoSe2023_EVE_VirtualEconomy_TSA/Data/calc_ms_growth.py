import csv

# Read the filtered data from the CSV file
filtered_data = []

with open('filtered_data_ms.csv', 'r') as file:
    reader = csv.reader(file, delimiter=';')
    header = next(reader)  # Skip the header
    for row in reader:
        date = row[0]
        money_supply = float(row[1])
        filtered_data.append((date, money_supply))

# Calculate the growth rate of money supply
growth_data = []
previous_money_supply = None

for i in range(len(filtered_data)):
    current_date, current_money_supply = filtered_data[i]
    if previous_money_supply is not None:
        growth_rate = (current_money_supply - previous_money_supply) / previous_money_supply
        growth_data.append((current_date, growth_rate))
    previous_money_supply = current_money_supply

# Write the growth data to a new CSV file
with open('filtered_data_ms_growth.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Date', 'GrowthRate'])
    writer.writerows(growth_data)
