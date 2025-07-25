# Swim Results Converter

The **Swim Results Converter** is a Python package designed to standardize and aggregate swim meet results from Excel files into structured CSV files. It processes raw swim meet data (e.g., `2025-meet2-results.xls`) into standardized CSVs and then aggregates them to summarize swimmer performance, including points and qualifications.

## Features

-   **Standardization**: Converts Excel files into standardized CSVs with detailed swimmer and event data, including time conversions, bonus points, and disqualification (DQ) handling.
-   **Aggregation**: Summarizes standardized data by swimmer, meet, and event, computing total points and qualification counts (ADV and DEV).
-   **Command-Line Interface**: Run the full pipeline with `swim-results-converter` or standardize data alone with `standardize_swim_data.py`.
-   **Flexible Input**: Processes Excel files (`.xls`, `.xlsx`) with a specific structure, extracting meet details and event information.
-   **Error Handling**: Logs issues for invalid files or missing data, ensuring robust processing.

## Prerequisites

-   **Python**: Version 3.8 or higher.
-   **Dependencies**:
    -   `pandas>=1.5.0`: For data processing.
    -   `openpyxl>=3.0.0`: For reading Excel files.

## Installation

### Step 1: Clone or Download the Repository

If the package is hosted in a Git repository (e.g., GitHub):

```bash
git clone https://github.com/petrfaitl/meet-results-converter.git
cd swim_data_pipeline
```

Alternatively, download and unzip the package archive (`swim_results_converter.zip` or `swim_results_converter.tar.gz`):

```bash
unzip swim_results_converter.zip -d swim_data_pipeline
cd swim_data_pipeline
```

### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install pandas openpyxl
```

### Step 3: Install the Package

Install the `swim_results_converter` package to make the `swim-results-converter` command available:

```bash
pip install .
```

This installs the package and sets up the command-line tool.

## Usage

The package provides two main ways to process swim meet data: running the full pipeline (standardization + aggregation) or standardizing data only.

### Option 1: Run the Full Pipeline

The `swim-results-converter` command runs both standardization and aggregation steps.

#### With Prompt

```bash
swim-results-converter
```

-   You’ll be prompted to enter the input directory (e.g., `meet_results`).
-   Default output directories are `standardized_results` for standardized CSVs and `aggregated_results` for aggregated CSVs.

#### With Explicit Arguments

```bash
swim-results-converter --input-dir meet_results --standardized-dir standardized_results --aggregated-dir aggregated_results --aggregate-results
```

-   `--input-dir`: Directory containing input Excel files.
-   `--standardized-dir`: Directory for standardized CSVs.
-   `--aggregate-results`: Turn aggregate results on.
-   `--aggregated-dir`: Directory for aggregated CSVs.

### Option 2: Run Standardization Only

To standardize Excel files without aggregation, run the `standardize_swim_data.py` script directly:

```bash
python src/swim_results_converter/standardize_swim_data.py --input-dir meet_results --output-dir standardized_results
```

-   `--input-dir`: Directory with Excel files (defaults to `meet_results`).
-   `--output-dir`: Directory for standardized CSVs (defaults to `standardized_results`).

If no arguments are provided, it uses default directories:

```bash
python src/swim_results_converter/standardize_swim_data.py
```

## Input Requirements

-   **Input Directory**: Place Excel files (`.xls` or `.xlsx`) in the input directory (e.g., `meet_results/`).
-   **File Naming**: Files should follow the format `YYYY-meetN-results.xls` (e.g., `2025-meet2-results.xls`) for proper meet name and date extraction.
-   **Excel File Structure**: The script expects the following columns in the Excel file:
    -   Column 0: Event name (e.g., "Event 1 Boys 12 & Under 50 SC Meter Freestyle").
    -   Column 1: Swimmer name.
    -   Column 2: Age.
    -   Column 3: Team.
    -   Column 4: Seed time (e.g., "MM:SS.SS", "SS.SS", or "NT").
    -   Column 7: Finals time (e.g., "MM:SS.SS", "SS.SS", "DQ", or "DNF").
    -   Column 9: Qualification (e.g., "ADV", "DEV", or empty).
    -   Column 10: Place points (numeric or 0 if missing).
    -   Column 13: Rank (numeric or "---" for DQ).
-   **Notes**:
    -   Rows with "Event" in column 0 are treated as event headers.
    -   Rows with "Name", "ADV", "DEV", or "Team" in column 0 or 1 are skipped.
    -   If your Excel files have a different structure, contact the package maintainer to adjust column mappings.

## Output

-   **Standardized CSVs** (in `standardized_results/`):

    -   Example: `standardized_2025-meet2-results.csv`.
    -   Columns:
        -   `MeetName`: Name of the meet (e.g., "Meet meet2").
        -   `Date`: Meet date (e.g., "2025-07-01").
        -   `Event`: Full event name (e.g., "Boys 12 & Under 50 SC Meter Freestyle").
        -   `Gender`: Parsed from event (e.g., "Boys", "Girls", "Mixed").
        -   `AgeGroup`: Parsed from event (e.g., "12 & Under").
        -   `Distance`: Parsed from event (e.g., "50").
        -   `Stroke`: Parsed from event (e.g., "Freestyle").
        -   `Category`: Individual event or Relay
        -   `SwimmerName`: Name of the swimmer.
        -   `Age`: Swimmer’s age.
        -   `Team`: Swimmer’s team.
        -   `SeedTime`: Seed time in seconds (or null for "NT" or "DQ").
        -   `FinalsTime`: Finals time in seconds (or null for "DQ" or "DNF").
        -   `Improvement`: Time difference (FinalsTime - SeedTime, negative for improvement, null if no improvement).
        -   `Rank`: Swimmer’s rank (or "---" for DQ).
        -   `DQ`: "DQ" if disqualified, null otherwise.
        -   `Qualification`: Qualification status (e.g., "ADV", "DEV", or empty).
        -   `PlacePoints`: Points from placement (numeric, 0 if missing).
        -   `PBPoints`: Calculated points (1 for no seed time, 2 for improvement null for relays or DQs).
        -   `TimePoints`: Calculated points (6 for ADV, 3 for DEV, null for relays or DQs).
        -   `TotalPoints`: Calculated sum of all points

-   **Aggregated CSVs** (in `aggregated_results/`):
    -   Example: `aggregated_2025-meet2-results.csv`.
    -   Columns:
        -   `MeetName`: Name of the meet.
        -   `Date`: Meet date.
        -   `Gender`: Swimmer’s gender.
        -   `AgeGroup`: Swimmer’s age group.
        -   `SwimmerName`: Name of the swimmer.
        -   `Age`: Swimmer’s age.
        -   `Team`: Swimmer’s team.
        -   `PlacePoints`: Sum of place points for non-relay events.
        -   `TimePoints`: Sum of place points for non-relay events.
        -   `PBPoints`: Sum of PB points for non-relay events.
        -   `TotalPoints`: Sum of `PlacePoints`, `TimePoints` and `PBPoints`.
        -   `QualificationADVCount`: Number of ADV qualifications.
        -   `QualificationDEVCount`: Number of DEV qualifications.

## Troubleshooting

-   **Command Not Found** (`swim-results-converter`):

    -   Ensure the package is installed with `pip install .`.
    -   Add the Python `Scripts` directory to your PATH:
        -   Windows: `C:\PythonXX\Scripts`
        -   macOS/Linux: `~/.local/bin`
    -   Verify with:
        ```bash
        pip show swim_results_converter
        ```

-   **Module Not Found** (`pandas` or `openpyxl`):

    -   Install missing dependencies:
        ```bash
        pip install pandas openpyxl
        ```

-   **Excel File Errors**:

    -   Check that input Excel files are in the correct format (see "Input Requirements").
    -   Verify file paths and permissions.
    -   Review logs in the console for specific errors (e.g., missing columns, invalid data).
    -   If the column structure differs, contact the maintainer to update `standardize_swim_data.py`.

-   **No Output Files**:
    -   Ensure the input directory contains valid `.xls` or `.xlsx` files.
    -   Check that the output directories are writable.
    -   Look for error messages in the logs.

## Development and Customization

-   **Source Code**: The package is structured under `src/swim_results_converter/`:
    -   `run_swim_data_pipeline.py`: Runs the full pipeline.
    -   `standardize_swim_data.py`: Standardizes Excel files into CSVs.
    -   `aggregate_swim_data.py`: Aggregates standardized CSVs.
-   **Customizing Excel Parsing**: If your Excel files have a different column structure, modify the `process_file` function in `standardize_swim_data.py` to adjust column indices.
-   **Contributing**: Fork the repository, make changes, and submit a pull request. Contact the maintainer for specific requirements.

## License

MIT License

Copyright (c) 2025 Petr Faitl

## Contact

For issues, feature requests, or support, contact Petr at petr@riveroaks.xyz or open an issue in the repository (if applicable).
