import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize global variables
timestamp = None
soil_type = ""
abbrv = ""

# Function to set the global timestamp variable
def set_timestamp():
	global timestamp
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def set_soil_type():
	global soil_type
	global abbrv
	soil_types = read_soil_types()
	print("Existing soil types:")
	for abbreviation, soil_type in soil_types.items():
		print(f"{abbreviation}: {soil_type}")
	while True:
		abbrv = input("\nEnter an existing abbreviation or a new one: ").upper()
		if not abbrv:
			print("Input required. Please enter a valid abbreviation for your measured soil type.")
			continue
		elif abbrv in soil_types:
			if not os.path.exists(f"./plots/{abbrv}"):
					os.makedirs(f"./plots/{abbrv}", exist_ok=True)
			if not os.path.exists(f"./data/{abbrv}"):
					os.makedirs(f"./data/{abbrv}", exist_ok=True)
		else:
			new_soil_type = input("Enter a new soil type: ")
			soil_types[abbrv] = new_soil_type
			with open('./code/soil_types.txt', 'a') as file:
				# Write to the file
				file.write(f"{abbrv}: {new_soil_type}\n")
			print("Soil type added successfully.")
			# Create folders for new soil type
			os.makedirs(f"./plots/{abbrv}", exist_ok=True)
			os.makedirs(f"./data/{abbrv}", exist_ok=True)
		soil_type = soil_types[abbrv]
		print(f"Selected soil type: {soil_type}")
		break

def read_soil_types():
	# Read soil types and abbreviations from the text file
	soil_types = {}
	with open("./code/soil_types.txt", "r") as f:
		for line in f:
			abbreviation, soil_type = line.strip().split(": ")
			soil_types[abbreviation] = soil_type
	return soil_types
		
def combine_csv_data(start_month, start_day, start_year):
	# List to store DataFrames from selected CSV files
	dfs = []
	data_path = f"./data/{abbrv}"
	
	# Get list of CSV files in the directory
	csv_files = [file for file in os.listdir(data_path) if file.endswith(".csv")]
	# Loop through each file in the directory
	for file_name in csv_files:
		# Extract month, day and year from file name
		file_month, file_day, file_year = extract_date(file_name)
		# Check if file falls within the specified time
		if (start_year < file_year) or \
			 (start_year == file_year and start_month < file_month) or \
			 (start_year == file_year and start_month == file_month and start_day <= file_day):
				file_path = os.path.join(data_path, file_name)
				# Read data from CSV into a DataFrame
				df = pd.read_csv(file_path)
				# Append DataFrame to the list
				dfs.append(df)
				print(f"Include data from {file_year}-{file_month}-{file_day}.")
	
	if dfs:
		# Combine DataFrames into a single DataFrame
		combined_df = pd.concat(dfs, ignore_index=True)
		return combined_df
	else:
		print("No CSV files found.")
		return None

def extract_date(file_name):
	# Assuming file name format is "data_abbrv_YYYY-MM-DD_HH-MM-SS.csv"
	parts = file_name.split("_")
	date_part = parts[2].split(".")[0]
	year, month, day = map(int, date_part.split("-"))
	return month, day, year
 
def create_plots(df, output_directory):
	# Create subplots with 2 rows and 2 columns
	fig, axs = plt.subplots(2, 2, figsize=(12, 6))
	plt.suptitle(f"Soil Moisture Analysis for Soil Type: {soil_type}")
	
	# Change settings here for plot layout
	# Temperature vs Soil Moisture
	axs[0, 0].scatter(df["temperature_c"].values, df["soil_moisture_p"].values, color="blue", alpha=0.25)
	axs[0, 0].set_xlabel("Temperature (C)")
	axs[0, 0].set_ylabel("Soil Moisture (%)")
	axs[0, 0].set_title("Temperature vs Soil Moisture")
	# Humidity vs Soil Moisture
	axs[0, 1].scatter(df["humidity_p"].values, df["soil_moisture_p"].values, color="orange", alpha=0.25)
	axs[0, 1].set_xlabel("Humidity (%)")
	axs[0, 1].set_ylabel("Soil Moisture (%)")
	axs[0, 1].set_title("Humidity vs Soil Moisture")
	# Temperature vs Humidity
	axs[1, 0].scatter(df["temperature_c"].values, df["humidity_p"].values, color="green", alpha=0.25)
	axs[1, 0].set_xlabel("Temperature (C)")
	axs[1, 0].set_ylabel("Humidity (%)")
	axs[1, 0].set_title("Temperature vs Humidity")
	# Temperature vs Heat Index
	axs[1, 1].scatter(df["temperature_c"].values, df["heat_index_c"].values, color="red", alpha=0.25)
	axs[1, 1].set_xlabel("Temperature (C)")
	axs[1, 1].set_ylabel("Heat Index (C)")
	axs[1, 1].set_title("Temperature vs Heat Index")
	
	# Add description about the number of measurements and date of processing
	num_measurements = len(df)
	formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S").strftime("%B %d, %Y %I:%M %p")
	description = f"Number of measurements: {num_measurements}\nDate of processing: {formatted_timestamp}"
	plt.figtext(0.5, 0.01, description, wrap=True, horizontalalignment="center", fontsize=10, fontweight="bold")
	
	# Adjust layout to prevent overlap
	plt.tight_layout()
	
	# Save plot as png with timestamp
	filename = os.path.join(output_directory, f"plot_{abbrv}_{timestamp}.png")
	plt.savefig(filename)
	print(f"\nSaved plot to '{filename}'.")
	
	# Show plots
	# plt.show()
	
def process_data(csv_file_path):
	# Load data from CSV into a DataFrame
	df = pd.read_csv(csv_file_path)
	create_plots(df, f"./plots/{abbrv}")
	
	# Store data to CSV file on your local machine
	filename = f"data/{abbrv}/data_{abbrv}_{timestamp}.csv"
	df.to_csv(filename, index=False)
	if os.path.exists(filename):
		print(f"Saved CSV data to '{filename}'.")
		delete_csv = input(f"\nDo you want to remove the file from your micro SD card to take measurements in another soil type? (y/n): ").lower()
		if delete_csv == "y":
			# Delete data from microSD card
			os.remove(csv_file_path)
			print("Removed CSV file from microSD card.")
		else:
			print("CSV file is kept.")
	else:
		raise FileNotFoundError(f"Error saving CSV data from microSD card to your local machine. File '{filename}' not found.")
		 
	# User interaction to select previously measured data
	if len(os.listdir(f"./data/{abbrv}")) > 1:
		print(f"\nYou previously collected data for {soil_type}:")
		files = os.listdir(f"./data/{abbrv}")
		# Print the list of files
		for file in files:
			print(file)
		generate_plots = input(f"\nDo you want to generate plots with previously measured data for {soil_type}? (y/n): ").lower()
		if generate_plots == "y":
			print("Please enter the start date for selecting CSV files:")
			start_month = int(input("Start month (1-12): "))
			start_day = int(input("Start day (1-31): "))
			start_year = int(input("Start year: "))
			# Combine CSV data into a single DataFrame
			combined_df = combine_csv_data(start_month, start_day, start_year)
			if combined_df is not None:
					# Create new folder
					new_folder_path = f"./plots/{abbrv}/plot_{abbrv}_{start_year}-{start_month}-{start_day}_{datetime.now().strftime('%Y-%m-%d')}"
					os.makedirs(new_folder_path, exist_ok=True)

					# Create plots from combined DataFrame and save to output directory
					create_plots(combined_df, new_folder_path)
		elif generate_plots == "n":
				print("Plot generation with previously measured data skipped.")
		else:
				print("Invalid input. Please enter 'y' or 'n'.")


def main():
	# Define path to directory where micro SD card is mounted
	sd_card_path = "./data/" # /path/to/your/sdcard 
	# Define the filename to process
	filename_to_process = "example_ps_data.csv" # "DATA.CSV"
	# Check if micro SD card is plugged in
	if os.path.exists(sd_card_path):
		# Check if the file exists on the micro SD card
		csv_file_path = os.path.join(sd_card_path, filename_to_process)
		if os.path.exists(csv_file_path):
			# Process the data
			set_timestamp()
			set_soil_type()
			process_data(csv_file_path)
		else:
			print(f"File '{filename_to_process}' not found on the micro SD card.")
	else:
		print("Micro SD card not found.")


if __name__ == "__main__":
	main()
