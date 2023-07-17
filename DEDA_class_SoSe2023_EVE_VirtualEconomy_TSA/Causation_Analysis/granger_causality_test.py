import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

def read_and_process_data(file_path, date_column, value_column):
    data = pd.read_csv(file_path, sep=';', parse_dates=[date_column])
    data.set_index(date_column, inplace=True)
    data[value_column] = data[value_column].astype(float)
    return data

def check_stationarity(series, name):
    result = adfuller(series)
    print(f"Results of ADF test for {name}")
    print(f"ADF Statistic: {result[0]}")
    print(f"p-value: {result[1]}")
    print("Stationary" if result[1] < 0.05 else "Non-Stationary")
    print()

def perform_granger_causality_test(data, max_lag):
    lag_lengths = []
    p_values = []

    for lag in range(1, max_lag + 1):
        results = grangercausalitytests(data, maxlag=lag)
        p_value = results[lag][0]['ssr_chi2test'][1]
        lag_lengths.append(lag)
        p_values.append(p_value)

    return lag_lengths, p_values

def plot_granger_causality(lag_lengths, p_values):
    plt.plot(lag_lengths, p_values, marker='o')
    plt.xlabel('Lag Length')
    plt.ylabel('Granger Causality p-value')
    plt.title('Sensitivity Analysis: Lag Length vs Granger Causality')
    plt.savefig('Causation_Analysis/granger_causality_plot.png', transparent=True)
    plt.show()

def save_p_values_to_csv(lag_lengths, p_values):
    data = {'Lag Length': lag_lengths, 'p-value': p_values}
    df = pd.DataFrame(data)
    df.to_csv('Causation_Analysis/granger_causality_p_values.csv', index=False)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    causation_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(causation_dir, 'Data')

    cpi_data_path = os.path.join(data_dir, 'filtered_data_cpi_inflation.csv')
    cpi_data = read_and_process_data(cpi_data_path, 'Date', 'Inflation')

    ms_growth_data_path = os.path.join(data_dir, 'filtered_data_ms_growth.csv')
    money_supply_growth_data = read_and_process_data(ms_growth_data_path, 'Date', 'GrowthRate')

    merged_data = cpi_data.merge(money_supply_growth_data, left_index=True, right_index=True)
    merged_data.dropna(inplace=True)

    check_stationarity(merged_data['Inflation'], "Inflation Rate")
    check_stationarity(merged_data['GrowthRate'], "Money Supply Growth Rate")

    stationary_data = merged_data[['GrowthRate', 'Inflation']].dropna()
    lag_lengths, p_values = perform_granger_causality_test(stationary_data, max_lag=10)

    plot_granger_causality(lag_lengths, p_values)
    save_p_values_to_csv(lag_lengths, p_values)

if __name__ == "__main__":
    main()
