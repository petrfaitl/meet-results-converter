import argparse
import logging
import os
import sys
from . import standardize_swim_data
from . import aggregate_swim_data

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

def main():
    parser = argparse.ArgumentParser(description="Run swim data standardization and aggregation pipeline")
    parser.add_argument('--input-dir', help='Directory containing input Excel files (prompted if not provided)')
    parser.add_argument('--standardized-dir', help='Directory for standardized CSV files (created as standardized_results if not provided)')
    parser.add_argument('--aggregated-dir', help='Directory for aggregated CSV files (created as aggregated_results if not provided)')
    parser.add_argument('--aggregate-results', action='store_true', help='Flag to indicate if aggregation of results should be performed')
    
    args = parser.parse_args()

    # prompt for Aggregate results to be generated
    if not args.aggregate_results:
        input_aggregate = input("Do you want to Aggregate Results generated? (yes/no): ").strip().lower()
        if input_aggregate in ['yes', 'y']:
            args.aggregate_results = True
        else:
            args.aggregate_results = False

    # Prompt for input directory if not provided
    input_dir = args.input_dir
    if not input_dir:
        input_dir = input("Enter the input directory for Excel files (e.g., results): ").strip()
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

    

    # Run standardization script
    logger.info("Running standardization script...")
    try:
        # Create a namespace for arguments
        standardize_args = argparse.Namespace(input_dir=input_dir, output_dir=standardized_dir)
        standardize_swim_data.main(standardize_args)
    except Exception as e:
        logger.error(f"Standardization script failed: {e}")
        sys.exit(1)

    # Set or create aggregated output directory
    if not args.aggregate_results:
        logger.info("Aggregation of results is not requested. Skipping aggregation step.")
    else:
        aggregated_dir = args.aggregated_dir or 'aggregated_results'
        aggregated_dir = validate_directory(aggregated_dir, create_if_missing=True)
        if not aggregated_dir:
            logger.error("Invalid or missing aggregated output directory. Exiting.")
            sys.exit(1)

            
        # Run aggregation script
        logger.info("Running aggregation script...")
        try:
            # Create a namespace for arguments
            aggregate_args = argparse.Namespace(input_dir=standardized_dir, output_dir=aggregated_dir)
            aggregate_swim_data.main(aggregate_args)
        except Exception as e:
            logger.error(f"Aggregation script failed: {e}")
            sys.exit(1)

    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()