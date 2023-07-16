import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller

def perform_adf_test(data, column, num_lags):
    adf_results = []
    for lag in num_lags:
        adf_result = adfuller(data[column].dropna(), maxlag=lag)
        adf_results.append(adf_result[1])
    return adf_results

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stationarity_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(stationarity_dir, 'Data')

    cpi_file = os.path.join(data_dir, 'filtered_data_cpi_inflation.csv')
    ms_growth_file = os.path.join(data_dir, 'filtered_data_ms_growth.csv')

    # Read the consumer price index data
    cpi_data = pd.read_csv(cpi_file, delimiter=';', parse_dates=['Date'])
    cpi_data.set_index('Date', inplace=True)

    # Read the money supply growth data
    money_supply_growth_data = pd.read_csv(ms_growth_file, delimiter=';', parse_dates=['Date'])
    money_supply_growth_data.set_index('Date', inplace=True)

    # Define the number of lags for ADF test
    num_lags = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Perform ADF test on the inflation series
    adf_results_inflation = perform_adf_test(cpi_data, 'Inflation', num_lags)
    print(f"ADF Test -Inflation Rate p-values: {adf_results_inflation}")

    # Perform ADF test on the money supply growth rate series
    adf_results_growth_rate = perform_adf_test(money_supply_growth_data, 'GrowthRate', num_lags)
    print(f"ADF Test - Money Supply Growth Rate p-values: {adf_results_growth_rate}")

    # Save ADF test results in a CSV file
    adf_results_df = pd.DataFrame({'Lag': num_lags, 'Inflation': adf_results_inflation, 'GrowthRate': adf_results_growth_rate})
    adf_results_df.to_csv(os.path.join(script_dir, 'Sttionarity/adf_results.csv'), index=False)

    # Visualize ADF test results
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    ax1 = axes[0]
    ax1.plot(num_lags, adf_results_inflation, marker='o')
    ax1.set_title('ADF Test - Inflation')
    ax1.set_xlabel('Number of Lags')
    ax1.set_ylabel('p-value')
    ax1.axhline(y=0.05, color='r', linestyle='--')

    ax2 = axes[1]
    ax2.plot(num_lags, adf_results_growth_rate, marker='o')
    ax2.set_title('ADF Test - Money Supply Growth Rate')
    ax2.set_xlabel('Number of Lags')
    ax2.set_ylabel('p-value')
    ax2.axhline(y=0.05, color='r', linestyle='--')

    # Adjust subplot spacing manually
    fig.subplots_adjust(hspace=0.4)

    # Save the plot with transparent background
    plt.savefig(os.path.join(script_dir, 'Stationarity/ADF_test_results.png'), transparent=True)

    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()
