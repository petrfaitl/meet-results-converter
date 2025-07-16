import pandas as pd
import os
import argparse
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to process a single standardized CSV file
def process_file(file_path):
    try:
        logger.info(f"Processing file: {file_path}")
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Ensure required columns exist
        required_columns = ['MeetName', 'Date', 'Gender', 'AgeGroup', 'SwimmerName', 'Age', 'Team', 
                           'PlacePoints', 'BonusPoints', 'Qualification']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in {file_path}")
            return None, None
        
        # Handle missing or invalid data
        df = df.dropna(subset=['SwimmerName', 'Gender', 'AgeGroup', 'Team'])
        df['PlacePoints'] = pd.to_numeric(df['PlacePoints'], errors='coerce').fillna(0).astype(int)
        df['BonusPoints'] = pd.to_numeric(df['BonusPoints'], errors='coerce').fillna(0).astype(int)
        df['Qualification'] = df['Qualification'].fillna('').astype(str)
        
        # Calculate ADV and DEV counts
        df['QualificationADV'] = df['Qualification'].str.contains('ADV', na=False).astype(int)
        df['QualificationDEV'] = df['Qualification'].str.contains('DEV', na=False).astype(int)
        
        return df, os.path.basename(file_path)
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None, None

# Function to aggregate data for a single file
def aggregate_data(df):
    # Filter out relay events for individual swimmer aggregation
    individual_df = df[~df['Event'].str.contains('Relay', na=False)]
    
    # Aggregate by SwimmerName, Gender, AgeGroup, Team, MeetName, and Date
    aggregated = individual_df.groupby(['MeetName', 'Date', 'Gender', 'AgeGroup', 'SwimmerName', 'Age', 'Team']).agg({
        'PlacePoints': 'sum',
        'BonusPoints': 'sum',
        'QualificationADV': 'sum',
        'QualificationDEV': 'sum'
    }).reset_index()
    
    # Calculate TotalPoints
    aggregated['TotalPoints'] = aggregated['PlacePoints'] + aggregated['BonusPoints']
    
    # Rename columns for clarity
    aggregated = aggregated.rename(columns={
        'QualificationADV': 'QualificationADVCount',
        'QualificationDEV': 'QualificationDEVCount'
    })
    
    # Sort by SwimmerName, MeetName, and Date for readability
    aggregated = aggregated.sort_values(['SwimmerName', 'MeetName', 'Date'])
    
    return aggregated

# Main function
def main(args):
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Process all CSV files in the input directory
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    if not csv_files:
        logger.warning(f"No CSV files found in {input_dir}")
        return
    
    for file_name in csv_files:
        file_path = os.path.join(input_dir, file_name)
        df, input_filename = process_file(file_path)
        
        if df is not None:
            # Aggregate data
            aggregated_df = aggregate_data(df)
            
            # Generate output filename based on input filename
            output_filename = input_filename.replace('standardized_', 'aggregated_')
            output_file = os.path.join(output_dir, output_filename)
            
            # Save to CSV
            aggregated_df.to_csv(output_file, index=False)
            logger.info(f"Aggregated data saved to {output_file}")
            
            # Preview the first few rows
            logger.info(f"Preview of aggregated data for {input_filename}:")
            logger.info(aggregated_df.head().to_string())
        else:
            logger.error(f"Skipping aggregation for {file_name} due to processing errors")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate standardized swim meet result CSV files")
    parser.add_argument('--input-dir', required=True, help='Directory containing standardized CSV files')
    parser.add_argument('--output-dir', required=True, help='Directory to save aggregated CSV files')
    args = parser.parse_args()
    main(args)