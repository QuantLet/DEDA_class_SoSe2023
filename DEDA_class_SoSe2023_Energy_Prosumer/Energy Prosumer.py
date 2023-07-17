#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 17:39:26 2023

@author: aliburak, lennartullner
"""

# please find the data at https://github.com/QuantLet/BLEM/tree/master/data
# download the data exactly as it is (still in the prosumer and consumer folders), 
# and put the prosumer and consumer folders in this data folder to not have to change the code.

# %% Set Up and Define Functions for Loading Data

# change file path to project's folder:
directory_path = 'YOUR_PATH/data'
#directory_path = '/Users/aliburak/Desktop/Draft_DEDA/data'
#directory_path = '/Users/lennartullner/Documents/GitHub/DEDA_Draft/data'
#directory_path = r'C:\Users\l.ullner\OneDrive - sonnen\Dokumente\GitHub\DEDA_Draft\data'

import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import calendar
import numpy as np
from datetime import datetime


def extract_numeric_part(file_name):
    match = re.search(r'\d+', file_name)
    if match:
        return int(match.group())
    else:
        return 0

def reorganize_data(directory):
    data = {
        'consumer': [],
        'prosumer': []
    }

    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            print(f"Processing files from {subdir_path}")
            datasets = []

            # Sort the file names based on the numeric part
            file_names = sorted(os.listdir(subdir_path), key=extract_numeric_part)

            for file_name in file_names:
                if file_name.endswith('.csv'):
                    file_path = os.path.join(subdir_path, file_name)
                    df = pd.read_csv(file_path)
                    df = process_dataframe(df)
                    datasets.append(df)
            if subdir == 'consumer':
                data['consumer'] = datasets
            elif subdir == 'prosumer':
                data['prosumer'] = datasets
    
    return data

def process_dataframe(df):
    # Drop unnecessary columns
    df = df[['time', 'energy', 'energyOut']]
    
    # Convert time from Unix milliseconds to datetime range
    df['time'] = pd.to_datetime(df['time'], unit='ms', origin='unix', utc=True)
    df['time'] = df['time'].dt.tz_convert('CET')  # Replace 'YOUR_TIMEZONE' with your desired timezone
    
    # Calculate the first difference for energy consumption and production
    df['energy_diff'] = df['energy'].diff()* 10**-10
    df['energyOut_diff'] = df['energyOut'].diff()* 10**-10
    
    return df

# %% Define Functions for Plotting

# All titles and legends have been disabled using quotes, as per requirement for the presentation
# The textbox displaing grid demand and feed in was consequently shifted to the left side.

def plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title='title', resample=True, datacol_name2=None,
                 dataname2=None, aligny=False, ylim=None, height=6):
    data = time_indexed_dataset
    
    fig, ax1 = plt.subplots(figsize=(12, height))
    
    # Plot data for the first y-axis
    ax1.plot(data.index, data[datacol_name], color='black', linewidth=0.5, label=dataname)
    
    # Resampling
    if resample:
        ax1.plot(data.resample('D')[datacol_name].mean(), label='Daily')
        ax1.plot(data.resample('W')[datacol_name].mean(), label='Weekly')
        ax1.plot(data.resample('M')[datacol_name].mean(), label='Monthly')
        
    # Add a horizontal line at y = 0
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=0.5)
    
    # Add y axis limits if needed
    if ylim is not None:
        ax1.set_ylim(ylim)    

    ax1.set_xlabel('Date')
    ax1.set_ylabel('kWh')
    
    # Adding second plot
    if datacol_name2 is not None:
        ax2 = ax1.twinx()  # Create a twin Axes for the second y-axis
        
        # Plot data for the second y-axis
        ax2.plot(data.index, data[datacol_name2], color='pink', linewidth=2, label=dataname2)
        ax2.set_ylabel(dataname2)
        
        if aligny == True:
            # Align the zero position of the second y-axis with the first y-axis
            ymin, ymax = ax1.get_ylim()
            y_range = max(abs(ymin), abs(ymax))
            ax2.set_ylim(-y_range, y_range)
        
        #visual adjustments
        ax2.grid(False)
        ax2.spines['top'].set_visible(False)
        
        # Adjust the spacing between the two y-axes
        fig.tight_layout(pad=2.0)
        
        # Create a single legend for both y-axes
        # lines_1, labels_1 = ax1.get_legend_handles_labels()
        # lines_2, labels_2 = ax2.get_legend_handles_labels()
        # lines = lines_1 + lines_2
        # labels = labels_1 + labels_2
        # ax1.legend(lines, labels, loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(title + ', ' + dataname2)
        
    #else:
        #ax1.legend(loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(title)


    # Display grid_demand and grid_feedin below the plot as a text box
    values = data[datacol_name] 
    grid_demand = values[values > 0].sum()
    grid_feedin = values[values < 0].sum() * -1
    mean = np.mean(values)
    var = np.var(values)
    text = f"Grid demand 2017: {grid_demand:.2f} kWh\nGrid feed-in 2017: {grid_feedin:.2f} kWh"
    ax1.text(0.01, -0.15, text, transform=ax1.transAxes, ha='left', va='center', 
             bbox=dict(facecolor='white', alpha=0.8))
    
    # Visual adjustments
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(False)
      
    # Save the plot with transparent background
    plt.savefig(title + '.png', transparent=True, bbox_inches='tight')
    
    plt.show()
    
    return grid_demand, grid_feedin, mean, var



def plotmonth(time_indexed_dataset, datacol_name, dataname, title='Net Load of Energy Community', \
              month=5, ylim=None, datacol_name2=None, dataname2=None, aligny=False, height=6):

    data = time_indexed_dataset
    
    # Filter data for the specified month
    data_month = data[data.index.month == month]
    data_month.loc[:, datacol_name] = pd.to_numeric(data_month.loc[:, datacol_name], errors='coerce')
    
    fig, ax1 = plt.subplots(figsize=(12, height))
    
    # Plotting aggregate net load for the specified month
    ax1.plot(data_month.index, data_month[datacol_name], color='black', linewidth=0.5, label=dataname)
    
    # Filling area under the plot
    ax1.fill_between(data_month.index, data_month.loc[:, datacol_name], where=(data_month.loc[:, datacol_name] >= 0),
                     interpolate=True, color='lightcoral', alpha = 0.5)
    ax1.fill_between(data_month.index, data_month.loc[:, datacol_name], where=(data_month.loc[:, datacol_name] < 0),
                     interpolate=True, color='lightgreen', alpha = 0.5)

    # Add a horizontal line at y = 0
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=0.5)
    
    # Add legend entries for areas under the curve
    # ax1.fill_between([], [], color='lightgreen', label='Electricity Surplus')
    # ax1.fill_between([], [], color='lightcoral', label='Electricity Demand')
    
    # Add y axis limits if needed
    if ylim is not None: ax1.set_ylim(ylim)
    
    # Display grid_demand and grid_feedin in the plot as a text box
    values = data_month[datacol_name] 
    grid_demand = values[values > 0].sum()
    grid_feedin = values[values < 0].sum() * -1
    text = f"Grid demand {calendar.month_name[month]}: {grid_demand:.2f} kWh\nGrid feed-in {calendar.month_name[month]}: {grid_feedin:.2f} kWh"
    ax1.text(0.01, -0.15, text, transform=ax1.transAxes, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))    

    ax1.set_xlabel('Date')
    ax1.set_ylabel('kWh')
    
    if datacol_name2 is not None:
        ax2 = ax1.twinx()  # Create a twin Axes for the second y-axis
        
        # Plot data for the second y-axis
        ax2.plot(data_month.index, data_month[datacol_name2], color='pink', linewidth=2, label=dataname2)
        ax2.set_ylabel(dataname2)
        
        if aligny == True:
            # Align the zero position of the second y-axis with the first y-axis
            ymin, ymax = ax1.get_ylim()
            y_range = max(abs(ymin), abs(ymax))
            ax2.set_ylim(-y_range, y_range)
        
        #visual adjustments
        ax2.grid(False)
        ax2.spines['top'].set_visible(False)   
        
        # Adjust the spacing between the two y-axes
        fig.tight_layout(pad=2.0)
        
        # Create a single legend for both y-axes
        # lines_1, labels_1 = ax1.get_legend_handles_labels()
        # lines_2, labels_2 = ax2.get_legend_handles_labels()
        # lines = lines_1 + lines_2
        # labels = labels_1 + labels_2
        # ax1.legend(lines, labels, loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(f"{title}, {dataname2} ({calendar.month_name[month]})") 
    
    #else:
        #ax1.legend(loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(f"{title} ({calendar.month_name[month]})")
    
    # Visual adjustments
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(False)
    
    # Save the plot with transparent background
    plt.savefig(f"{title}_{calendar.month_name[month]}.png", transparent=True, bbox_inches='tight')
    
    plt.show()
    
    return grid_demand, grid_feedin






def plotday(time_indexed_dataset, datacol_name, dataname, title='Net Load of Energy Community', \
            date='15-05-2017', ylim=None, datacol_name2=None, dataname2=None, aligny=False, multicol=False, height=6):
    data = time_indexed_dataset
    
    # Convert date string to datetime object
    plot_date = datetime.strptime(date, '%d-%m-%Y').date()
    
    # Filter data for the specified date
    data_day = data[data.index.date == plot_date]
    data_day.loc[:, datacol_name] = pd.to_numeric(data_day.loc[:, datacol_name], errors='coerce')
    
    fig, ax1 = plt.subplots(figsize=(12, height))
    
    # Plotting aggregate net load for the specified date
    ax1.plot(data_day.index, data_day.loc[:, datacol_name], color='black', linewidth=0.5, label=dataname)
    
    # Add a horizontal line at y = 0
    ax1.axhline(y=0, color='red', linestyle='--', linewidth=0.5)
    
    # Filling area under the plot
    ax1.fill_between(data_day.index, data_day.loc[:, datacol_name], where=(data_day.loc[:, datacol_name] >= 0),
                     interpolate=True, color='lightcoral', alpha=0.5)
    ax1.fill_between(data_day.index, data_day.loc[:, datacol_name], where=(data_day.loc[:, datacol_name] < 0),
                     interpolate=True, color='lightgreen', alpha=0.5)
    
    # Add legend entries for areas under the curve
    # ax1.fill_between([], [], color='lightgreen', label='Electricity Surplus')
    # ax1.fill_between([], [], color='lightcoral', label='Electricity Demand')
    
    # Add y axis limits if needed
    if ylim is not None:
        ax1.set_ylim(ylim)
    
    # Display grid_demand and grid_feedin in the plot as a text box
    values = data_day[datacol_name] 
    grid_demand = values[values > 0].sum()
    grid_feedin = values[values < 0].sum() * -1
    text = f"Grid demand {plot_date.strftime('%Y-%m-%d')}: {grid_demand:.2f} kWh\nGrid feed-in {plot_date.strftime('%Y-%m-%d')}: {grid_feedin:.2f} kWh"
    ax1.text(0.01, -0.15, text, transform=ax1.transAxes, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))    
        
    ax1.set_xlabel('Time (hh)')
    ax1.set_ylabel('kWh')
    
    if datacol_name2 is not None:
        ax2 = ax1.twinx()  # Create a twin Axes for the second y-axis
        
        # Plot data for the second y-axis
        ax2.plot(data_day.index, data_day[datacol_name2], color='grey', linestyle='dashed', linewidth=2, label=dataname2)
        ax2.set_ylabel(dataname2)
        
        if aligny:
            # Align the zero position of the second y-axis with the first y-axis
            ymin, ymax = ax1.get_ylim()
            ax2.set_ylim(ymin, ymax)
        
        #visual adjustments
        ax2.grid(False)
        ax2.spines['top'].set_visible(False)  
        
        # Adjust the spacing between the two y-axes
        fig.tight_layout(pad=2.0)
        
        # Create a single legend for both y-axes
        # lines_1, labels_1 = ax1.get_legend_handles_labels()
        # lines_2, labels_2 = ax2.get_legend_handles_labels()
        # lines = lines_1 + lines_2
        # labels = labels_1 + labels_2
        # ax1.legend(lines, labels, loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(f"{title} vs. {dataname2} ({plot_date.strftime('%Y-%m-%d')})") 
    
    #else:
        #ax1.legend(loc=(0.01, -0.2), ncol=2)
        #ax1.set_title(f"{title} ({plot_date.strftime('%Y-%m-%d')})")
    
    # Set x-axis tick labels to display only the hour in 'hh' format for every full hour
    ax1.set_xticks(data_day.index[data_day.index.minute == 0])
    ax1.set_xticklabels(data_day.index[data_day.index.minute == 0].strftime('%H'))
    
    # Visual adjustments
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(False)
    
    # Save the plot with transparent background
    plt.savefig(f"{title}_{plot_date.strftime('%Y-%m-%d')}.png", transparent=True, bbox_inches='tight')
    
    plt.show()
    
    return grid_demand, grid_feedin





# %% Load Data and Create a data frame with net loads

#Load data
organized_data = reorganize_data(directory_path)
consumer_data = organized_data['consumer']
prosumer_data = organized_data['prosumer']

# %% Create a data frame of net loads.

# Specify the consumer and prosumer IDs to include in the energy community
# This selection is based on previous analysis
consumer_ids = [id for id in range(1, 101) if id not in [13, 21, 26, 35, 46, 53, 57, 67, 76, 78, 80, 81]]
prosumer_ids = [19, 24, 26, 30, 72, 75, 83, 89]

# Extract 15min resampled net loads from each prosumer and consumer data set
netloads_data = pd.DataFrame(columns=[])

for prosumer_id in prosumer_ids:
    df = prosumer_data[prosumer_id - 1].resample('15T', on='time', origin = 'start').sum()
    netloads_data[f'p{prosumer_id}' ] = df['energy_diff'] - df['energyOut_diff']


for consumer_id in consumer_ids:
    df = consumer_data[consumer_id - 1].resample('15T', on='time', origin = 'start').sum()
    netloads_data[f'c{consumer_id}' ] = df['energy_diff']

# Add aggregate net load data
netloads_data['aggr_netload'] = netloads_data.sum(axis=1)
netloads_data.reset_index(inplace=True)


# %% Extract relevant data and plot individual household's net load

# Change quotes to plot some selected households only:
# Entire selection
#consumer_ids = [id for id in range(1, 101) if id not in [13, 21, 26, 35, 46, 53, 57, 67, 76, 78, 80, 81]]
#prosumer_ids = [19, 24, 26, 30, 72, 75, 83, 89]
#height = 6

# Smaller selection for plotting
#consumer_ids = [4, 20, 30, 40, 50]
#prosumer_ids = [19, 24, 26, 30, 72, 75, 83, 89]
#height = 6

# Plots for presentation:
consumer_ids = [4]
prosumer_ids = [26]
height = 4

for prosumer_id in prosumer_ids:
    netload = netloads_data.iloc[:-1, :][['time', f'p{prosumer_id}']].set_index('time')
    time_indexed_dataset, datacol_name, dataname, title = netload, f'p{prosumer_id}', 'Net Load', f'Prosumer {prosumer_id}\'s Net Load'

    plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, height=height)
    plotmonth(time_indexed_dataset, datacol_name, dataname, title, height=height)
    plotday(time_indexed_dataset, datacol_name, dataname, title, height=height, date='15-05-2017')


for consumer_id in consumer_ids:
    netload = netloads_data.iloc[:-1, :][['time', f'c{consumer_id}']].set_index('time')
    time_indexed_dataset, datacol_name, dataname, title = netload, f'c{consumer_id}', 'Net Load', f'Consumer {consumer_id}\'s Net Load'

    plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, height=height)
    plotmonth(time_indexed_dataset, datacol_name, dataname, title, height=height)
    plotday(time_indexed_dataset, datacol_name, dataname, title, height=height, date='15-05-2017')

# %% Plot 2 boxplots for the means of each consumer and each prosumer

# Calculate the mean for prosumer columns
prosumers_mean = netloads_data.filter(regex='^p').mean(axis=0)

# Calculate the mean for consumer columns
consumers_mean = netloads_data.filter(regex='^c').mean(axis=0)

# Create separate DataFrames for prosumers and consumers means
prosumers_df = pd.DataFrame({'Mean Net Load (kWh)': prosumers_mean})
consumers_df = pd.DataFrame({'Mean Net Load (kWh)': consumers_mean})

# Generate the box plot for prosumers
fig, ax1 = plt.subplots(figsize=(12, 4))
ax1.boxplot(prosumers_df['Mean Net Load (kWh)'], labels=['Prosumers'], notch=False, showfliers=False, vert=False)
ax1.set_xlabel('Mean Net Load (kWh)')
ax1.set_title('')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.xaxis.grid(False)  # Remove x-axis grid lines
ax1.yaxis.grid(False)  # Remove y-axis grid lines
ax1.patch.set_alpha(0.0)  # Set plot background transparent
plt.savefig('prosumers_box_plot.png', transparent=True)
plt.show()

# Generate the box plot for consumers
fig, ax2 = plt.subplots(figsize=(12, 4))
ax2.boxplot(consumers_df['Mean Net Load (kWh)'], labels=['Consumers'], notch=False, showfliers=False, vert=False)
ax2.set_xlabel('Mean Net Load (kWh)')
ax2.set_title('')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.xaxis.grid(False)  # Remove x-axis grid lines
ax2.yaxis.grid(False)  # Remove y-axis grid lines
ax2.patch.set_alpha(0.0)  # Set plot background transparent
plt.savefig('consumers_box_plot.png', transparent=True)
plt.show()


# %% Extract relevant data and plot community's net load

aggr_netload = netloads_data.iloc[:-1, :][['time', 'aggr_netload']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = aggr_netload, 'aggr_netload', 'Aggregate Net Load', 'Net Load of Energy Community'

grid_demand_start, grid_feedin_start, mean_com, var_com = plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, ylim=(-20,30))
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='01-01-2017')


# %% Heat pump adoption.
heat_pumps_installed = 25       # base this on goal of heat pump installations in Germany

#Calculate electricity demand for heat pumps
import demandlib.bdew as bdew
temperature = pd.read_csv(directory_path + "/temperature.csv")["temperature"]

from workalendar.europe import Germany
cal = Germany()
holidays = dict(cal.holidays(2017))

# Create DataFrame for 2023
demand_th = pd.DataFrame(
    index=pd.date_range(
        datetime(2017, 1, 1, 0), periods=8760, freq="H"
    )
)

## improve: use .sum() to get specific demand for each household?

demand_th = bdew.HeatBuilding(
    demand_th.index,
    holidays=holidays,
    temperature=temperature,
    shlp_type="EFH",
    building_class=1, # German: Baualtersklasse. It can assume values in the range 1-11.
    wind_class=0, # Wind classification for building location (0=not windy or 1=windy)
    annual_heat_demand=15000,
    name="HeatPump",
).get_bdew_profile()

# resample, interpolate to get 15min from 1h values, unit = kw/15min.
#Because by resampling the last 3 15min periods are missed, we add 3 15min periods containing the value of the last period.
demand_th = demand_th.resample('15T').interpolate() / 4
new_rows = pd.concat([demand_th.iloc[[-1]]] * 4)
new_index = pd.date_range(start=demand_th.index[-1] + pd.Timedelta(minutes=15),
                          periods=4, freq='15T')
new_rows.index = new_index
demand_th = pd.concat([demand_th, new_rows])

#Convert thermal demand to electrical demand and multiply by number of new heat pumps.
conversion_rate = 0.35 # conversion thermal to electrical demand
hp_load = demand_th * conversion_rate * heat_pumps_installed  # possible improvement: base heat pumps on specific household demands.

# Add heat pump loads and new total net laod to our data frame.

netloads_data['hp_load_original'] = hp_load.values
netloads_data['NL_with_HP'] = netloads_data['aggr_netload'] + netloads_data['hp_load_original']


# %% Plot heat pump load, singular and aggregated

aggr_netload = netloads_data.iloc[:-1, :][['time', 'hp_load_original']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = aggr_netload, 'hp_load_original', 'Heat pump load', 'Load of heat pumps'

plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, ylim=(-20,30))
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='01-01-2017')


# %% Plot Community's Net Load after heat pumps are installed

aggr_netload = netloads_data.iloc[:-1, :][['time', 'NL_with_HP']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = aggr_netload, 'NL_with_HP', 'New Net Load', 'Net Load of Energy Community with Heat Pumps'

grid_demand_whp, grid_feedin_whp, mean_hps, var_hps = plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, ylim=(-20,30))
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='17-03-2017')


# ALI: ADD MOV PLOT HERE
# Lennart @ Ali: use the plotmonth function with the parameters set just like in the line above. the add month= for
# each month plot. Similiar to the code below (that code doesnt work yet):

# saving the plots 
for i in np.arange(1, 13):
    plotmonth(time_indexed_dataset, datacol_name, dataname, title, month=i)

# %% Battery Simulation and Plot

size = [100, 200, 500, 1000, 2000, 1090]
net_load = netloads_data['NL_with_HP']
battery_data = pd.DataFrame(index=range(len(net_load)), columns=[f"Charge {s}" for s in size] + [f"SOC {s}" for s in size] + [f"Charge/Discharge {s}" for s in size])

for s in range(len(size)):
    column_charge = f"Charge {size[s]}"
    column_soc = f"SOC {size[s]}"
    column_charge_discharge = f"Charge/Discharge {size[s]}"
    
    beg = size[s] / 2  # assumption: beginning SOC of battery is 10%
    min_size = 0.05 * size[s]  # assumption: battery does not get discharged to less than 5% of total battery capacity
    max_size = 0.95 * size[s]  # assumption: battery does not get charged to more than 95% of total battery capacity
    
    battery_data[column_charge] = pd.NA
    battery_data[column_soc] = pd.NA
    battery_data[column_charge_discharge] = pd.NA
    
    for i in range(len(battery_data)):
        if i == 0:
            battery_data.at[i, column_charge] = beg - net_load[i]
        else:
            prev = battery_data.at[i - 1, column_charge]
            nl = net_load[i]
            battery_data.at[i, column_charge] = prev - nl
        
        battery_data.at[i, column_charge] = max(min_size, min(battery_data.at[i, column_charge], max_size))
        battery_data.at[i, column_soc] = battery_data.at[i, column_charge] / size[s]
        
        if i != 0:
            battery_data.at[i, column_charge_discharge] = battery_data.at[i, column_charge] - battery_data.at[i - 1, column_charge]
        else:
            battery_data.at[i, column_charge_discharge] = battery_data.at[i, column_charge] - beg
            
battery_data.insert(0, 'Timestamp', netloads_data['time'])

# Set the style of the plot
plt.style.use('seaborn-whitegrid')

# Define the window size
window = 30 * 24 * 4  # 30 days * 24 hours/day * 4 intervals/hour

# Iterate over each battery size and create a graph
for s in size:
    column_name = f"SOC {s}"
    
    # Calculate the rolling average
    rolling_avg = battery_data[column_name].rolling(window=window, center=True).mean()

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(battery_data['Timestamp'], battery_data[column_name], color='black', linewidth=0.5, label='SOC')
    ax.plot(battery_data['Timestamp'], rolling_avg, linewidth=2, label=f'{window//(4*24)}-day Rolling Average')
    
    # Set plot title and axis labels
    ax.set_title(f'State Of Charge, Battery Size: {s} kWh', fontsize=14)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('SOC', fontsize=12)
    
    # Customize tick labels and legend
    ax.tick_params(axis='both', labelsize=10)
    ax.legend(fontsize=10)

    # Rotate x-axis tick labels for better readability
    plt.xticks(rotation=45)

    # Add grid lines
    ax.grid(True, linestyle='--', alpha=0.5)

    # Remove plot borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Show the plot
    plt.savefig(f'State Of Charge, Battery Size: {s} kWh.png', transparent=True)
    plt.tight_layout()
    plt.show()


# %% Analyse Impact of Battery by Plotting Battery Adjusted Net Load

# Add battery to net load data
netloads_data['battery adjustment'] = battery_data['Charge/Discharge 1090'].values
netloads_data['NL battery optimized'] = netloads_data['NL_with_HP'].values + netloads_data['battery adjustment']
netloads_data['battery_SOC_1090'] = battery_data['SOC 1090'].values

# Extract Relevant Data, including 30 day rolling average of battery SOC.
NL_batt_opt = netloads_data[['time', 'NL battery optimized']].set_index('time')
rolling_avg = battery_data['SOC 1090'].rolling(window=window, center=True).mean() # adding rolling average of SOC for 2nd plot axis
NL_batt_opt['battery_SOC_1090_rollavg'] = rolling_avg.values
time_indexed_dataset, datacol_name, dataname, title = NL_batt_opt.iloc[0:-1,:], 'NL battery optimized', 'Aggregate Net Load', 'Battery Optimized Net Load of Energy Community'

# And plot.
grid_demand_batt, grid_feedin_batt, mean_batt, var_batt = plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title, datacol_name2='battery_SOC_1090_rollavg', dataname2="Battery SOC")
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title)


      
# %% Optimize by shifting demand of heat pumps to surplus periods

netloads_data['hp_load'] = hp_load.values
netloads_data['loadshift'] = 0

#Determine maximum flexibility capacity of the heat pump
hp_max = max(hp_load.values)

# # Algorithm for load shifting

for t in netloads_data.index:
    
    # Verbose:
    if t == 1000:
        print('t = 1000')
    if t == 10000:
        print('t = 10000')
    if t == 20000:
        print('t = 20000')
        
    netload_t = netloads_data.loc[t,'aggr_netload'] + netloads_data.loc[t,'hp_load']    # net load at time t
    
    if netload_t <0 :  # community has electricity surplus
        surplus = - netload_t
        
        # search surrounding time steps to shift demand from.
        tx = 1 # begin by looking one time step ahead.
        
        # loop until enough demand has been shifted to tiem t that surplus is gone.
        while surplus > 0:
            
            demand_tx = max(0, netloads_data.loc[t+tx,'aggr_netload']  + netloads_data.loc[t+tx,'hp_load']) # demand size
            
            if demand_tx > 0: # in time step tx there is electricity demand.
                hp_load_tx = netloads_data.loc[t+tx,'hp_load']  # heat pump loads in tx.
                hp_free_capacity_t = hp_max - netloads_data.loc[t,'hp_load']    # potential to power up heat pump loads in t.
                loadshift_tx = - min(surplus, hp_load_tx, demand_tx, hp_free_capacity_t)
                    # shift size (must be <= either of surplus in t, demand in tx, heat pump load in tx and free heat pump capacity in t)
                netloads_data.loc[t+tx,'hp_load'] += loadshift_tx   # heat pump load decrease in tx (powering down)
                netloads_data.loc[t,'hp_load'] -= loadshift_tx  # heat pump load increas in t (powering up)
                netloads_data.loc[t+tx,'loadshift'] += loadshift_tx # record load shift in t and tx
                netloads_data.loc[t,'loadshift'] -= loadshift_tx
                surplus += loadshift_tx # update size of surplus in t.
                
            # let the loop gp over 16 periods before and after t (1,-1,2,-2,3,-3,...16,-16), unless out of scope (eg tx > t)
            if tx > 0:
                if tx < t:
                    tx = -tx
                else:
                    tx += 1
            else:
                tx -= 1
                if t-tx < len(netloads_data.index):
                    tx = -tx
            if tx not in range(-16, 17, 1):# manually stop looking for demand if search window is out of range.
                surplus = 0

# calculate new optimized net load.
netloads_data['Optimized Net Load'] = netloads_data['aggr_netload'] + netloads_data['hp_load']


# %% Plot Community's Net Load after Time Shift Optimization

NL_HP_opt = netloads_data.iloc[:-1, :][['time', 'Optimized Net Load', 'NL_with_HP']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = NL_HP_opt,'Optimized Net Load', \
    'Optimized Net Load', 'Optimized Net Load of Energy Community'

grid_demand_opt, grid_feedin_opt, mean_opt, var_opt = plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title)
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='17-03-2017', datacol_name2='NL_with_HP' , \
        dataname2='Net Load Unoptimized', aligny=True)    


# %% Impact analysis:
    
#Assign values to variables

grid_demand_batt_decrease = (grid_demand_whp - grid_demand_batt) 
grid_feedin_batt_decrease = (grid_feedin_whp - grid_feedin_batt) 
grid_demand_opt_decrease = (grid_demand_whp - grid_demand_opt) 
grid_feedin_opt_decrease = (grid_feedin_whp - grid_feedin_opt) 

grid_demand_batt_decrease_p = (grid_demand_batt_decrease / grid_demand_whp) * 100
grid_feedin_batt_decrease_p = (grid_feedin_batt_decrease / grid_feedin_whp) * 100
grid_demand_opt_decrease_p = (grid_demand_opt_decrease / grid_demand_whp) * 100
grid_feedin_opt_decrease_p = (grid_feedin_opt_decrease / grid_feedin_whp) * 100

# Format values with two decimal points and units
variables = {
    "grid_demand_start": f"{grid_demand_start:.2f} kWh",
    "grid_feedin_start": f"{grid_feedin_start:.2f} kWh",
    "grid_demand_whp": f"{grid_demand_whp:.2f} kWh",
    "grid_feedin_whp": f"{grid_feedin_whp:.2f} kWh",
    "grid_demand_batt": f"{grid_demand_batt:.2f} kWh",
    "grid_demand_batt_decrease": f"{grid_demand_batt_decrease:.2f} kWh",
    "grid_demand_batt_decrease_percent": f"{grid_demand_batt_decrease_p:.2f}%",
    "grid_feedin_batt": f"{grid_feedin_batt:.2f} kWh",
    "grid_feedin_batt_decrease": f"{grid_feedin_batt_decrease:.2f} kWh",
    "grid_feedin_batt_decrease-percent": f"{grid_feedin_batt_decrease_p:.2f}%",
    "grid_demand_opt": f"{grid_demand_opt:.2f} kWh",
    "grid_demand_opt_decrease": f"{grid_demand_opt_decrease:.2f} kWh",
    "grid_demand_opt_decrease_percent": f"{grid_demand_opt_decrease_p:.2f}%",    
    "grid_feedin_opt": f"{grid_feedin_opt:.2f} kWh",
    "grid_feedin_opt_decrease": f"{grid_feedin_opt_decrease:.2f} kWh",
    "grid_feedin_opt_decrease_percent": f"{grid_feedin_opt_decrease_p:.2f}%",
    "mean_optimized": f"{mean_opt}",
    "variance_optimized": f"{var_opt}",
    "mean_with_heat_pumps": f"{mean_hps}",
    "variance_with_heat_pumps": f"{var_hps}",
    "mean_community": f"{mean_com}",
    "variance_community": f"{var_com}"
    }

# Print the variables with formatted values
for variable, value in variables.items():
    print(f"{variable.replace('_', ' ').title()}: {value}")




# %% Visual impact analysis:
    
# before change:

aggr_netload = netloads_data.iloc[:-1, :][['time', 'NL_with_HP']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = aggr_netload, 'NL_with_HP', 'New Net Load', \
    'Net Load of Energy Community with Heat Pumps'

plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title)
plotmonth(time_indexed_dataset, datacol_name, dataname, title, month=2)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='15-02-2017', ylim=(-10,25))
    
# %%    
# after change:
NL_HP_opt = netloads_data.iloc[:-1, :][['time', 'Optimized Net Load', 'NL_with_HP']].set_index('time')

time_indexed_dataset, datacol_name, dataname, title = NL_HP_opt,'Optimized Net Load', \
    'Optimized Net Load', 'Optimized Net Load of Energy Community'

plotyear_rsp(time_indexed_dataset, datacol_name, dataname, title)
plotmonth(time_indexed_dataset, datacol_name, dataname, title)
plotday(time_indexed_dataset, datacol_name, dataname, title, date='17-03-2017', datacol_name2='NL_with_HP' , \
        dataname2='Net Load Unoptimized', aligny=True, ylim=(-10,25), multicol=True)    


# %% Optional code: Looking at different days in winter, to find one to examplifier the load shift

# from datetime import datetime, timedelta

# start_date = datetime(2017, 1, 1)
# end_date = datetime(2017, 3, 30)

# dates_list = []

# while start_date <= end_date:
#     dates_list.append(start_date.strftime('%d-%m-%Y'))
#     start_date += timedelta(days=1)
    
# for i in dates_list:
#     plotday(time_indexed_dataset, datacol_name, dataname, title, date=i, datacol_name2='NL_with_HP' , \
#         dataname2='Net Load Unoptimized', aligny=True, ylim=(-10,25), multicol=True) 

