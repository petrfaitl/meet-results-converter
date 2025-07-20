import pandas as pd
import re
import os
import argparse
from datetime import datetime
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to convert time strings (MM:SS.SS or SS.SS) to seconds
def convert_time_to_seconds(time_str):
    if pd.isna(time_str) or time_str in ['NT', 'DQ', 'DNF']:
        return None
    # Handle DQ cases (e.g., "DQ 3:49.50")
    if 'DQ' in str(time_str):
        time_str = str(time_str).replace('DQ', '').strip()
        if not time_str:
            return None
    try:
        # Check if time is in MM:SS.SS format
        if ':' in str(time_str):
            minutes, seconds = map(float, time_str.split(':'))
            return round(minutes * 60 + seconds, 2)
        # Otherwise, assume SS.SS format
        return round(float(time_str), 2)
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting time {time_str}: {e}")
        return None

# Function to extract event details from event name
def parse_event_name(event_name):
    # Regex to extract gender, age group, distance, and stroke
    pattern = r'(?P<gender>Girls|Boys|Mixed)\s*(?P<age_group>\d+\s*(&\s*Under|Year\s*Olds|\d+\s*&\s*Over)?)?\s*(?P<distance>\d+)\s*SC\s*Meter\s*(?P<stroke>Freestyle|Butterfly|Medley Relay|Backstroke|Breaststroke|IM|Freestyle\s*Relay)'
    match = re.search(pattern, event_name.strip())
    if match:
        return {
            'Gender': match.group('gender'),
            'AgeGroup': match.group('age_group') if match.group('age_group') else '12 & Over',
            'Distance': match.group('distance'),
            'Stroke': match.group('stroke')
        }
    logger.warning(f"Could not parse event name: {event_name}")
    return {
        'Gender': None,
        'AgeGroup': None,
        'Distance': None,
        'Stroke': None
    }

# Function to extract meet name and date from filename or metadata
def extract_meet_info(file_path):
    # Default values
    meet_name = os.path.splitext(os.path.basename(file_path))[0]
    meet_date = datetime.now().strftime('%Y-%m-%d')
    
    # Try to extract from filename (e.g., "2025-meet1-results.xls" -> date: 2025, name: meet1)
    filename = os.path.basename(file_path).lower()
    date_pattern = r'(\d{4})[-_](meet\d+)[-_\w]*'
    match = re.match(date_pattern, filename)
    if match:
        year = match.group(1)
        meet_name = f"Meet {match.group(2)}"
        meet_date = f"{year}-07-01"  # Default to July 1 if only year is found
        logger.info(f"Extracted from filename: meet_name={meet_name}, meet_date={meet_date}")
    
    # Try to read metadata or first row for more specific meet info
    try:
        df = pd.read_excel(file_path, nrows=1)
        if 'Results' in str(df.iloc[0, 0]):
            meet_name = str(df.iloc[0, 0]).replace('Results - ', '').strip()
            logger.info(f"Extracted meet_name from file content: {meet_name}")
    except Exception as e:
        logger.warning(f"Could not read meet name from file {file_path}: {e}")
    
    return meet_name, meet_date

# Function to calculate time difference
def calculate_time_diff(seed_time, final_time):
    if pd.isna(seed_time) or pd.isna(final_time) or 'DNF' in str(final_time).upper():
        return None
    time_diff = final_time - seed_time
    if time_diff > 0:
        return None
    return round(time_diff, 2)

# Calculate bonus points
def calculate_bonus_points(seed_time, improvement, dq, qualification, event):
    # If swimmer was disqualified or event is a relay, return no bonus
    if 'DQ' in str(dq).upper() or 'RELAY' in str(event).upper():
        return None

    bonus_points = 0

    # Bonus for not having a seed time
    if not seed_time or 'NT' in str(seed_time).upper():
        bonus_points += 1

    # Bonus for improvement (assumes improvement is a negative number)
    if improvement and float(improvement) < 0:
        bonus_points += 2

    # Bonus for qualification level
    if 'ADV' in str(qualification).upper():
        bonus_points += 6
    if 'DEV' in str(qualification).upper():
        bonus_points += 3

    return str(bonus_points) if bonus_points else None

# Calculate PB points
def calculate_pb_points(seed_time, improvement, dq, event, nt_bonus=1,pb_bonus=2):
    # If swimmer was disqualified or event is a relay, return no PB points
    if 'DQ' in str(dq).upper() or 'RELAY' in str(event).upper():
        return None

    pb_points = 0

    # If there is no seed time, return no PB points
    if not seed_time or 'NT' in str(seed_time).upper():
        pb_points += nt_bonus

    # If improvement is negative, it means the swimmer improved their time
    if improvement and float(improvement) < 0:
        pb_points += pb_bonus


    return str(pb_points) if pb_points else None

# Calculate time points
def calculate_time_points( dq,qualification, event, dev_bonus=3, adv_bonus=6):
    # If swimmer was disqualified or event is a relay, return no time points
    if 'DQ' in str(dq).upper() or 'RELAY' in str(event).upper():
        return None

    time_points = 0

    # Add bonus points based on qualification level
    if 'ADV' in str(qualification).upper():
        time_points += adv_bonus
    if 'DEV' in str(qualification).upper():
        time_points += dev_bonus

    return str(time_points) if time_points else None

# Calculate total points
def calculate_total_points(place_points, pb_points, time_points):
    logger.debug(f"Calculating total points: place_points={place_points}, pb_points={pb_points}, time_points={time_points}")
    
    # Convert points to integers/floats if they are strings
    place_points = float(place_points) if place_points is not None and str(place_points).strip() else 0
    pb_points = int(pb_points) if pb_points is not None and str(pb_points).strip() else 0
    time_points = int(time_points) if time_points is not None and str(time_points).strip() else 0

    # Calculate total points
    total_points = place_points + pb_points + time_points
    return total_points if total_points > 0 else None

# Function to process a single Excel file
def process_file(file_path, output_dir):
    try:
        logger.info(f"Processing file: {file_path}")
        # Extract meet info
        meet_name, meet_date = extract_meet_info(file_path)
        
        # Load the Excel file
        df = pd.read_excel(file_path)
        
        # Initialize lists to store standardized data
        standardized_data = []
        current_event = None
        
        # Process the dataframe row by row
        for index, row in df.iterrows():
            # Check if the row contains an event name
            if pd.notna(row.iloc[0]) and 'Event' in str(row.iloc[0]):
                current_event = row.iloc[0].strip()
                index = current_event.find("  ")
                current_event = str(current_event[index+1:]).strip()
                current_event = str(current_event).replace(')', '') if ")" in current_event else current_event
                continue
            # Skip rows that are not swimmer results
            if pd.isna(row.iloc[0]) or 'Name' in str(row.iloc[0]) or 'ADV' in str(row.iloc[1]) or 'DEV' in str(row.iloc[1]) or 'Team' in str(row.iloc[0]):
                continue
            # Extract swimmer data
            name = row.iloc[1] if pd.notna(row.iloc[1]) else None
            age = row.iloc[2].strip() if pd.notna(row.iloc[2]) else None
            team = row.iloc[3] if pd.notna(row.iloc[3]) else None
            seed_time = row.iloc[4] if pd.notna(row.iloc[4]) else None
            finals_time = row.iloc[7] if pd.notna(row.iloc[7]) else None
            place_points = row.iloc[10] if pd.notna(row.iloc[10]) else None
            rank = row.iloc[13] if pd.notna(row.iloc[13]) else None
            qualification = row.iloc[9] if pd.notna(row.iloc[9]) else None

            # Trigger DQ flag
            dq = None
            if "---" in str(rank):
                dq = "DQ"
            
            # Skip if critical data is missing
            if not name or not current_event:
                continue
            
            # Parse event details
            event_details = parse_event_name(current_event)
            
            # Convert times to seconds
            seed_time_seconds = convert_time_to_seconds(seed_time)
            finals_time_seconds = convert_time_to_seconds(finals_time)

            # Calculate improvement
            improvement = calculate_time_diff(seed_time_seconds, finals_time_seconds)

            # Calculate time points
            time_points = calculate_time_points(dq, qualification, current_event)

            # Calculate pb points
            pb_points = calculate_pb_points(seed_time, improvement, dq, current_event)

            # Calculate total points
            total_points = calculate_total_points(place_points, pb_points, time_points)
            
            # Create standardized record
            record = {
                'MeetName': meet_name,
                'Date': meet_date,
                'Event': current_event,
                'Gender': event_details['Gender'],
                'AgeGroup': event_details['AgeGroup'],
                'Distance': event_details['Distance'],
                'Stroke': event_details['Stroke'],
                'Category': 'Individual' if 'Relay' not in current_event else 'Relay',
                'SwimmerName': name,
                'Age': age,
                'Team': team,
                'SeedTime': seed_time_seconds,
                'FinalsTime': finals_time_seconds,
                'Improvement': improvement,
                'Rank': rank,
                'DQ': dq,
                'Qualification': qualification,
                'PlacePoints': place_points,
                'PBPoints': pb_points,
                'TimePoints': time_points,
                'TotalPoints': total_points,
            }
            standardized_data.append(record)
        
        # Create a DataFrame from standardized data
        standardized_df = pd.DataFrame(standardized_data)
        
        # Save to CSV
        output_file = os.path.join(output_dir, f"standardized_{os.path.splitext(os.path.basename(file_path))[0]}.csv")
        standardized_df.to_csv(output_file, index=False)
        logger.info(f"Standardized data saved to {output_file}")
        
        # Return the DataFrame for potential further use
        return standardized_df
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None

# Main function to process multiple files
def main(args):
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Process all Excel files in the input directory
    excel_files = [f for f in os.listdir(input_dir) if f.endswith(('.xls', '.xlsx'))]
    if not excel_files:
        logger.warning(f"No Excel files found in {input_dir}")
        return
    
    for file_name in excel_files:
        file_path = os.path.join(input_dir, file_name)
        process_file(file_path, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize swim meet result Excel files")
    parser.add_argument('--input-dir', default='results', help='Directory containing Excel files')
    parser.add_argument('--output-dir', default='standardized_results', help='Directory to save standardized CSV files')
    args = parser.parse_args()
    main(args)