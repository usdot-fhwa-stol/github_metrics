import pandas as pd
import os
from glob import glob
import re

def extract_info_from_filename(filename):
    """
    Extracts the organization and the month-year from the filename.
    Handles both 'biweekly' and specific date range filenames.
    """
    # Regular expression to match 'biweekly' format
    biweekly_pattern = re.compile(r'github_[^_]+_([^_]+)_biweekly_(\d{4}-\d{2})-\d{2}\.csv')
    # Regular expression to match 'start-end date' format
    date_range_pattern = re.compile(r'([^_]+)_(\d{4}-\d{2})-\d{1,2}_\d{4}-\d{2}-\d{1,2}\.csv')

    # Attempt to match the biweekly pattern first
    match = biweekly_pattern.search(filename)
    if match:
        organization = match.group(1)
        month_year = match.group(2)
        return organization, month_year

    # If not matched, try the date range pattern
    match = date_range_pattern.search(filename)
    if match:
        organization = match.group(1)
        month_year = match.group(2)
        return organization, month_year

    # If no pattern matches, output error
    print(f"Filename format is incorrect: {filename}")
    return None, None

def aggregate_data(input_directory, output_directory):
    """
    Aggregates data from CSV files in the specified input directory.
    """
    files = glob(os.path.join(input_directory, '*.csv'))
    all_data = []

    for file in files:
        org, month_year = extract_info_from_filename(os.path.basename(file))
        if not org or not month_year:
            continue  # Skip files with incorrect formats

        df = pd.read_csv(file)
        df['Organization'] = org
        df['Month_Year'] = month_year

        # Ensure all necessary columns are present, even if they're empty
        expected_columns = ['Total Page Views', 'Total Unique Page Views', 'Total Clones', 'Total Unique Clones', 'Total Forks', 'Total Stars']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0  # Initialize missing columns with 0

        all_data.append(df)

    if all_data:
        # Combine all data into a single DataFrame
        full_df = pd.concat(all_data, ignore_index=True)
        # Aggregate data by organization and month/year
        grouped_df = full_df.groupby(['Organization', 'Month_Year']).sum().reset_index()
        # Save the aggregated data to CSV
        grouped_df.to_csv(os.path.join(output_directory, 'aggregated_data.csv'), index=False)
        print(f"Aggregated data written successfully to {output_directory}/aggregated_data.csv")
    else:
        print("No data was aggregated. Please check the input files and column names.")

input_dir = './output'  # Set input directory path
output_dir = './aggregated_output'  # Set output directory path
os.makedirs(output_dir, exist_ok=True)
aggregate_data(input_dir, output_dir)
