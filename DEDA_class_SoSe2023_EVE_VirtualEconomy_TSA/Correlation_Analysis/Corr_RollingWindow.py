import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    correlation_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(correlation_dir, 'Data')

    cpi_file = os.path.join(data_dir, 'filtered_data_cpi_inflation.csv')
    ms_growth_file = os.path.join(data_dir, 'filtered_data_ms_growth.csv')

    # Read the consumer price index data
    cpi_data = pd.read_csv(cpi_file, delimiter=';', parse_dates=['Date'])
    cpi_data.set_index('Date', inplace=True)

    # Read the money supply growth data
    money_supply_growth_data = pd.read_csv(ms_growth_file, delimiter=';', parse_dates=['Date'])
    money_supply_growth_data.set_index('Date', inplace=True)

    # Set the desired date range
    start_date = '2017-02-01'
    end_date = '2023-03-01'
    cpi_data = cpi_data.loc[start_date:end_date]
    money_supply_growth_data = money_supply_growth_data.loc[start_date:end_date]

    # Calculate the correlation between the two series on a rolling window
    window = 6
    correlation = cpi_data['Inflation'].rolling(window=window).corr(money_supply_growth_data['GrowthRate'])

    # Plot the inflation rate with transparent background
    plt.figure(figsize=(10, 4))
    plt.plot(cpi_data.index, cpi_data['Inflation'])
    plt.title('Inflation Rate')
    plt.xlabel('Date')
    plt.ylabel('Inflation Rate')
    plt.savefig('Correlation_Analysis/inflation_rate_plot.png', transparent=True)
    plt.close()

    # Plot the money supply growth with transparent background
    plt.figure(figsize=(10, 4))
    plt.plot(money_supply_growth_data.index, money_supply_growth_data['GrowthRate'])
    plt.title('Money Supply Growth')
    plt.xlabel('Date')
    plt.ylabel('Growth Rate')
    plt.savefig('Correlation_Analysis/money_supply_growth_plot.png', transparent=True)
    plt.close()

    # Plot the correlation with transparent background and dashed line on 0.0
    plt.figure(figsize=(10, 4))
    plt.plot(correlation.index, correlation)
    plt.axhline(y=0.0, color='r', linestyle='--')
    plt.title(f'Correlation (Rolling Window: {window})')
    plt.xlabel('Date')
    plt.ylabel('Correlation')
    plt.savefig('Correlation_Analysis/correlation_plot.png', transparent=True)
    plt.close()

if __name__ == "__main__":
    main()
