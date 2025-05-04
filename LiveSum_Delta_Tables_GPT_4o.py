import pandas as pd
import json
import numpy as np
import os
NUM_SAMPLES_TO_PROCESS = 20 # Adjust as needed
INPUT_JSON_FILE = 'train.json'
OUTPUT_DIR = 'difference_tables_4o'
# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")
#Load Data (Ensure INPUT_JSON_FILE exists and is valid)
try:
    with open(INPUT_JSON_FILE) as f:
        train_data = json.load(f)
    train_df = pd.json_normalize(train_data)
    print(f"Loaded {len(train_df)} samples from {INPUT_JSON_FILE}")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Assuming train_df is already loaded, now get the 20 Ground Truth Tables
list_of_table_dfs = []
for i in range(20):
    try:
        # Extract the table string from the i-th row
        table_string = train_df.iloc[i]['table']

        # Split the table string into rows
        table_rows = table_string.split('<NEWLINE>')

        # Extract the header and data rows
        header = table_rows[0].split(',')
        data = [row.split(',') for row in table_rows[1:]]

        # Create a pandas DataFrame
        table_df = pd.DataFrame(data, columns=header)
        table_df.drop(columns=['Corner Kicks'])
        list_of_table_dfs.append(table_df)

    except Exception as e:
        print(f"Error processing sample {i}: {e}")
        # Handle potential errors, e.g., if 'table' column is missing or format is incorrect
        # You might want to append None or an empty DataFrame to the list in case of an error
        list_of_table_dfs.append(None)

#Now lets create the Delta Tables
#1. Make the Team Stats Table from the samples
# Number of samples to process
num_samples = 20

# List to store the team_stats DataFrames for each sample
all_team_stats = []
directory = 'player_stats_output_GPT4o'  # Directory containing the CSV files
for i in range(1, num_samples + 1):
    # Construct the file names for the current sample with the directory
    home_file = os.path.join(directory, f'Sample_{i}_home_team_stats.csv')
    away_file = os.path.join(directory, f'Sample_{i}_away_team_stats.csv')

    try:
        # Calculate column-wise sums for home and away dataframes
        home_team_stats = pd.read_csv(home_file)
        away_team_stats = pd.read_csv(away_file)

        # Calculate the sum of the relevant columns
        home_goals_sum = home_team_stats['Goals'].sum() if 'Goals' in home_team_stats.columns else 0
        home_shots_sum = home_team_stats['Shots'].sum() if 'Shots' in home_team_stats.columns else 0
        home_fouls_sum = home_team_stats['Fouls'].sum() if 'Fouls' in home_team_stats.columns else 0
        home_yellow_cards_sum = home_team_stats['Yellow Cards'].sum() if 'Yellow Cards' in home_team_stats.columns else 0
        home_red_cards_sum = home_team_stats['Red Cards'].sum() if 'Red Cards' in home_team_stats.columns else 0
        home_free_kicks_sum = home_team_stats['Free Kicks'].sum() if 'Free Kicks' in home_team_stats.columns else 0
        home_offsides_sum = home_team_stats['Offsides'].sum() if 'Offsides' in home_team_stats.columns else 0

        away_goals_sum = away_team_stats['Goals'].sum() if 'Goals' in away_team_stats.columns else 0
        away_shots_sum = away_team_stats['Shots'].sum() if 'Shots' in away_team_stats.columns else 0
        away_fouls_sum = away_team_stats['Fouls'].sum() if 'Fouls' in away_team_stats.columns else 0
        away_yellow_cards_sum = away_team_stats['Yellow Cards'].sum() if 'Yellow Cards' in away_team_stats.columns else 0
        away_red_cards_sum = away_team_stats['Red Cards'].sum() if 'Red Cards' in away_team_stats.columns else 0
        away_free_kicks_sum = away_team_stats['Free Kicks'].sum() if 'Free Kicks' in away_team_stats.columns else 0
        away_offsides_sum = away_team_stats['Offsides'].sum() if 'Offsides' in away_team_stats.columns else 0

        # Create a new dataframe for team-wise stats
        team_stats = pd.DataFrame({
            'Team': ['Home Team', 'Away Team'],
            'Goals': [home_goals_sum, away_goals_sum],
            'Shots': [home_shots_sum, away_shots_sum],
            'Fouls': [home_fouls_sum, away_fouls_sum],
            'Yellow Cards': [home_yellow_cards_sum, away_yellow_cards_sum],
            'Red Cards': [home_red_cards_sum, away_red_cards_sum],
            'Free Kicks': [home_free_kicks_sum, away_free_kicks_sum],
            'Offsides': [home_offsides_sum, away_offsides_sum]
        })

        # Invert the rows to match the format of the ground truth table
        team_stats = team_stats.iloc[::-1].reset_index(drop=True)

        # Append the team_stats DataFrame to the list
        all_team_stats.append(team_stats)

        # Display the team-wise stats for the current sample (optional)
        print(f"Team Stats for Sample {i}:")
        print(team_stats)
        print("-" * 30)

    except FileNotFoundError:
        print(f"Error: Could not find files {home_file} or {away_file} for sample {i}.")
    except Exception as e:
        print(f"An error occurred while processing sample {i}: {e}")

# Now, the 'all_team_stats' list contains the team_stats DataFrames for the first 20 samples.
# You can access each DataFrame using its index in the list (e.g., all_team_stats[0] for the first sample).
#2. Make the Delta Tables for each sample using the team_stats
# Assuming list_of_table_dfs and all_team_stats are already populated
list_of_difference_dfs = []
# Iterate through the 20 samples
for i in range(20):
    try:
        # Get the table_df (ground truth) and team_stats (calculated) for the current sample
        table_df = list_of_table_dfs[i].copy() # Use .copy() to avoid modifying the original DataFrame
        team_stats = all_team_stats[i].copy() # Use .copy() to avoid modifying the original DataFrame

        # Ensure 'Team' column exists in both DataFrames
        if 'Team' not in table_df.columns or 'Team' not in team_stats.columns:
            print(f"Warning: 'Team' column missing in one of the DataFrames for sample {i}. Skipping difference calculation.")
            list_of_difference_dfs.append(None) # Or handle this case as needed
            continue

        # Set 'Team' as index for both DataFrames
        table_df.set_index('Team', inplace=True)
        team_stats.set_index('Team', inplace=True)

        # Identify common columns for subtraction (excluding index 'Team')
        common_cols = list(set(table_df.columns) & set(team_stats.columns))

        # Convert common columns in table_df to integer type
        for col in common_cols:
            if table_df[col].dtype != 'int64':
                table_df[col] = pd.to_numeric(table_df[col], errors='coerce').fillna(0).astype(int)

        # Calculate the differences
        difference_df = table_df[common_cols] - team_stats[common_cols]

        # Append the resulting difference DataFrame to the list
        list_of_difference_dfs.append(difference_df)

        # Display the difference DataFrame for the current sample (optional)
        print(f"Difference DataFrame for Sample {i+1}:")
        print(difference_df)
        print("-" * 30)
    except Exception as e:
        print(f"An error occurred while calculating the difference for sample {i}: {e}")
        list_of_difference_dfs.append(None) # Or handle the error as needed
#save the difference DataFrames to CSV files
for i, difference_df in enumerate(list_of_difference_dfs):
    if difference_df is not None:  # Check if a difference DataFrame was successfully created for this sample
        try:
            # Save the DataFrame to a CSV file
            difference_df.to_csv( os.path.join(OUTPUT_DIR, f'Sample_{i+1}_delta_table.csv'), index=False)
            print(f"Saved difference DataFrame for Sample {i} to 'difference_sample_{i}.csv'")
        except Exception as e:
            print(f"Error saving difference DataFrame for Sample {i}: {e}")
    else:
        print(f"No difference DataFrame to save for Sample {i}.")
# Now, 'list_of_difference_dfs' contains the DataFrames representing the differences for each of the 20 samples.
# You can access each difference DataFrame using its index in the list (e.g., list_of_difference_dfs[0]).

# Assuming list_of_table_dfs and all_team_stats are already populated
# and list_of_difference_dfs has been created in the previous step

categories_to_track = ['Goals', 'Shots', 'Fouls', 'Yellow Cards', 'Red Cards', 'Free Kicks', 'Offsides']

# Initialize a dictionary to store the running total of deltas for each category
total_delta_sum = {category: 0 for category in categories_to_track}

# Iterate through the list of difference DataFrames (one for each sample)
for i, difference_df in enumerate(list_of_difference_dfs):
    if difference_df is not None:  # Check if a difference DataFrame was successfully created for this sample
        for category in categories_to_track:
            if category in difference_df.columns:
                # Ensure the column is numeric before summing
                difference_df[category] = pd.to_numeric(difference_df[category], errors='coerce').fillna(0)
                total_delta_sum[category] += difference_df[category].sum()
            else:
                print(f"Warning: Category '{category}' not found in difference DataFrame for sample {i}.")

# Calculate the average difference for each tracked category
average_delta = {
    category: total / len(list_of_difference_dfs) if len(list_of_difference_dfs) > 0 else 0
    for category, total in total_delta_sum.items()
}

# Create a DataFrame to display the average differences
average_difference_df = pd.DataFrame(list(average_delta.items()), columns=['Category', 'Average Difference'])

# Display the average difference table
print("\nAverage Difference Table (over 20 samples):")
print(average_difference_df)
# Save the average difference table to a CSV file
average_difference_df.to_csv( os.path.join(OUTPUT_DIR, f'average_delta.csv'), index=False)