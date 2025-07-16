import subprocess
import os
import argparse
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_directory(path, create_if_missing=True):
    """Validate or create a directory."""
    if not path:
        return None
    if not os.path.exists(path) and create_if_missing:
        try:
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return None
    if not os.path.isdir(path):
        logger.error(f"Path is not a directory: {path}")
        return None
    return os.path.abspath(path)

def run_script(script_name, args):
    """Run a Python script with the given arguments."""
    try:
        # Ensure the script exists in the current directory or bundled executable
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if not os.path.exists(script_path):
            logger.error(f"Script {script_name} not found at {script_path}")
            return False
        
        # Construct the command
        command = [sys.executable, script_path] + args
        logger.info(f"Executing command: {' '.join(command)}")
        
        # Run the script
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully ran {script_name}: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_name}: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running {script_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run swim data standardization and aggregation pipeline")
    parser.add_argument('--input-dir', help='Directory containing input Excel files (prompted if not provided)')
    parser.add_argument('--standardized-dir', help='Directory for standardized CSV files (created as standardized_results if not provided)')
    parser.add_argument('--aggregated-dir', help='Directory for aggregated CSV files (created as aggregated_results if not provided)')
    args = parser.parse_args()

    # Prompt for input directory if not provided
    input_dir = args.input_dir
    if not input_dir:
        input_dir = input("Enter the input directory for Excel files (e.g., meet_results): ").strip()
    input_dir = validate_directory(input_dir, create_if_missing=False)
    if not input_dir:
        logger.error("Invalid or missing input directory. Exiting.")
        sys.exit(1)

    # Set or create standardized output directory
    standardized_dir = args.standardized_dir or 'standardized_results'
    standardized_dir = validate_directory(standardized_dir, create_if_missing=True)
    if not standardized_dir:
        logger.error("Invalid or missing standardized output directory. Exiting.")
        sys.exit(1)

    # Set or create aggregated output directory
    aggregated_dir = args.aggregated_dir or 'aggregated_results'
    aggregated_dir = validate_directory(aggregated_dir, create_if_missing=True)
    if not aggregated_dir:
        logger.error("Invalid or missing aggregated output directory. Exiting.")
        sys.exit(1)

    # Run standardization script
    logger.info("Running standardization script...")
    standardize_args = ['--input-dir', input_dir, '--output-dir', standardized_dir]
    if not run_script('standardize_swim_data.py', standardize_args):
        logger.error("Standardization script failed. Exiting.")
        sys.exit(1)

    # Run aggregation script
    logger.info("Running aggregation script...")
    aggregate_args = ['--input-dir', standardized_dir, '--output-dir', aggregated_dir]
    if not run_script('aggregate_swim_data.py', aggregate_args):
        logger.error("Aggregation script failed. Exiting.")
        sys.exit(1)

    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()