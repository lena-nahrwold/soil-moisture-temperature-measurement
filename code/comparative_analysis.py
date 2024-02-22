import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from data_processing import read_soil_types

def read_soil_data(soil_type):
    # Read data for the specified soil type
    data_folder = f"./data/{soil_type}"
    dfs = []
    for file_name in os.listdir(data_folder):
        if file_name.endswith(".csv"):
            file_path = os.path.join(data_folder, file_name)
            df = pd.read_csv(file_path)
            df["soil_type"] = soil_type  # Add soil_type column to identify data
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        print("No CSV files found.")
		return None

def generate_comparison_plots(selected_soil_types):
    # Combine CSV data for all selected soil types in one dataframe
    dfs = []
    for soil_type in selected_soil_types:
        df = read_soil_data(soil_type)
        if df is not None:
            dfs.append(df)

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"Soil Moisture, Humidity, and Temperature of {', '.join([soil_types[soil_type] for soil_type in selected_soil_types])}")

        # Change settings here for plot layout
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        for idx, soil_type in enumerate(selected_soil_types):
            sub_df = combined_df[combined_df["soil_type"] == soil_type]

            # Temperature vs Soil Moisture
            axs[0, 0].scatter(sub_df["temperature_c"], sub_df["soil_moisture_p"], alpha=0.1, label=f"{soil_types[soil_type]} ({len(sub_df)})", color=colors[idx], s=30)
            axs[0, 0].set_xlabel("Temperature (C)")
            axs[0, 0].set_ylabel("Soil Moisture (%)")
            axs[0, 0].set_title("Temperature vs Soil Moisture")
            axs[0, 0].legend(fontsize='small')

            # Humidity vs Soil Moisture
            axs[0, 1].scatter(sub_df["humidity_p"], sub_df["soil_moisture_p"], alpha=0.1, label=f"{soil_types[soil_type]} ({len(sub_df)})", color=colors[idx], s=30)
            axs[0, 1].set_xlabel("Humidity (%)")
            axs[0, 1].set_ylabel("Soil Moisture (%)")
            axs[0, 1].set_title("Humidity vs Soil Moisture")
            axs[0, 1].legend(fontsize='small')

            # Temperature vs Humidity
            axs[1, 0].scatter(sub_df["temperature_c"], sub_df["humidity_p"], alpha=0.1, label=f"{soil_types[soil_type]} ({len(sub_df)})", color=colors[idx], s=30)
            axs[1, 0].set_xlabel("Temperature (C)")
            axs[1, 0].set_ylabel("Humidity (%)")
            axs[1, 0].set_title("Temperature vs Humidity")
            axs[1, 0].legend(fontsize='small')

            # Temperature vs Head Index
            axs[1, 1].scatter(sub_df["temperature_c"], sub_df["heat_index_c"], alpha=0.1, label=f"{soil_types[soil_type]} ({len(sub_df)})", color=colors[idx], s=30)
            axs[1, 1].set_xlabel("Temperature (C)")
            axs[1, 1].set_ylabel("Heat Index (C)")
            axs[1, 1].set_title("Temperature vs Heat Index")
            axs[1, 1].legend(fontsize='small')

        plt.tight_layout()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        abbrv_str = '_'.join(selected_soil_types)
        file_name = f"./plots/soil_comparison_{abbrv_str}_{timestamp}.png"
        plt.savefig(file_name)
        print(f"Comparison plot saved as: {file_name}")
        return
    
    else: 
        print("No data found.")

if __name__ == "__main__":
    # Show avilable soil types
    soil_types = read_soil_types()
    print("Available soil types:")
    for idx, (abbrv, name) in enumerate(soil_types.items(), start=1):
        print(f"{idx}. {name} ({abbrv})")

    # Prompt user to select soil types to compare
    # Fill selected_soil_types array based on user input
    selected_soil_types = []
    while not selected_soil_types:
        selected_soil_indices = input("Enter the indices or abbrevations of soil types to compare (comma-separated): ")
        selected_soil_indices = [index.strip() for index in selected_soil_indices.split(",")]
        for index in selected_soil_indices:
            try:
                index = int(index) - 1
                selected_soil_types.append(list(soil_types.keys())[index])
            except ValueError:
                if index in soil_types:
                    selected_soil_types.append(index)
                else:
                    print("Invalid input. Please enter valid indices or soil type abbrevations.")
                    break

    # Generate the plots comparing the selected soil types
    generate_comparison_plots(selected_soil_types)

