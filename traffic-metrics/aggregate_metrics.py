import pandas as pd
import os
from glob import glob
import re

def extract_info_from_filename(filename):
    # Regular expressions to match 'biweekly' and 'date range' formats
    biweekly_pattern = re.compile(r'github_[^_]+_([^_]+)_biweekly_(\d{4}-\d{2})-\d{2}\.csv')
    date_range_pattern = re.compile(r'([^_]+)_(\d{4}-\d{2})-\d{1,2}_\d{4}-\d{2}-\d{1,2}\.csv')

    # Try matching biweekly pattern first
    match = biweekly_pattern.search(filename)
    if match:
        return match.group(1), match.group(2)

    # Try date range pattern if biweekly didn't match
    match = date_range_pattern.search(filename)
    if match:
        return match.group(1), match.group(2)

    # Return None if no pattern matches
    return None, None

def aggregate_data(input_directory, output_directory):
    files = glob(os.path.join(input_directory, '*.csv'))
    all_data = []

    # Process each file
    for file in files:
        org, month_year = extract_info_from_filename(os.path.basename(file))
        if not org or not month_year:
            continue  # Skip file if it doesn't match expected filename patterns

        df = pd.read_csv(file)
        df['Organization'] = org
        df['Month_Year'] = month_year

        # Drop columns starting with 'Total'
        df = df.drop(columns=[col for col in df.columns if col.startswith('Total')])

        all_data.append(df)

    # Concatenate all data frames into one
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        grouped_df = full_df.groupby(['Organization', 'Month_Year']).sum().reset_index()

        # Remove columns with all zero values
        grouped_df = grouped_df.loc[:, (grouped_df != 0).any(axis=0)]

        # Save the final DataFrame
        grouped_df.to_csv(os.path.join(output_directory, 'aggregated_data.csv'), index=False)
        print("Aggregated data written successfully.")
    else:
        print("No data was aggregated.")
        
input_dir = './output'
output_dir = './aggregated_output'
os.makedirs(output_dir, exist_ok=True)
aggregate_data(input_dir, output_dir)