#!/usr/bin/env python3
"""
Netflix Data Cleaning Pipeline - Main Entry Point
Cleans, transforms, and analyzes the Netflix Movies and TV Shows dataset.

Usage:
    python run.py                  # Run full pipeline with default paths
    python run.py --input <path>   # Specify input CSV path
    python run.py --output <dir>   # Specify output directory
    python run.py --no-charts      # Skip chart generation
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from src.cleaner import NetflixCleaner
from src.utils import (CleaningLogger, describe_dataframe_basics,
                                export_to_excel, get_hashable_cols)
from src.visualizer import NetflixVisualizer, generate_comparison_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Netflix Data Cleaning Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py
  python run.py --input data/raw/netflix_titles.csv --output ./my_output
  python run.py --no-charts
        """,
    )
    parser.add_argument(
        "--input",
        default="data/raw/netflix_titles.csv",
        help="Path to input CSV file (default: data/raw/netflix_titles.csv)",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory for reports and charts (default: output)",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation",
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel export (CSV only)",
    )
    parser.add_argument(
        "--save-cleaned",
        default="data/cleaned/netflix_titles_cleaned.csv",
        help="Path to save cleaned CSV (default: data/cleaned/netflix_titles_cleaned.csv)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        print("   Make sure the dataset is downloaded. Run the pipeline from the project root.")
        sys.exit(1)

    # Ensure output directories exist
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.dirname(args.save_cleaned), exist_ok=True)

    # Initialize components
    logger = CleaningLogger()
    cleaner = NetflixCleaner(logger)
    visualizer = NetflixVisualizer(output_dir=args.output)

    # Step 1: Load
    header("STEP 1: LOADING DATA")
    raw_df = cleaner.load_data(args.input)

    # Step 2: Inspect
    header("STEP 2: INITIAL INSPECTION")
    summary = cleaner.inspect(raw_df)
    overview_text = describe_dataframe_basics(summary)
    print("\n" + overview_text)

    # Save raw data stats
    null_before = raw_df.isnull().sum()

    # Step 3: Clean
    header("STEP 3: RUNNING CLEANING PIPELINE")
    cleaned_df = cleaner.run_full_pipeline(raw_df.copy())

    # Step 4: Validate
    header("STEP 4: VALIDATION")

    null_after = cleaned_df.isnull().sum()
    total_before = int(null_before.sum())
    total_after = int(null_after.sum())
    resolved = total_before - total_after

    print(f"  [MISSING] Original columns had {total_before:,} missing values")
    print(f"  [MISSING] After cleaning (incl. new derived cols): {total_after:,}")
    print(f"  [MISSING] Note: Increase is from new columns (year_added, duration_minutes, etc.)")

    dup_before = int(raw_df.duplicated().sum())
    dup_after = int(cleaned_df[get_hashable_cols(cleaned_df)].duplicated().sum())
    print(f"  [DUPLICATES] Before: {dup_before} | After: {dup_after}")
    print(f"\n  [OK] Dataset shape: {cleaned_df.shape[0]:,} rows x {cleaned_df.shape[1]} columns")

    # Step 5: Save Cleaned Data (CSV + Excel)
    header("STEP 5: SAVING CLEANED DATA")
    cleaned_df.to_csv(args.save_cleaned, index=False)
    file_size_mb = os.path.getsize(args.save_cleaned) / 1e6
    print(f"  [CSV] Cleaned data -> {args.save_cleaned}")
    print(f"  [INFO] CSV file size: {file_size_mb:.2f} MB")

    if not args.no_excel:
        excel_path = str(Path(args.save_cleaned).with_suffix('.xlsx'))
        export_to_excel(cleaned_df, excel_path)

    # Step 6: Generate Charts
    if not args.no_charts:
        visualizer.generate_all_charts(cleaned_df, null_before, null_after)
    else:
        print("\n  [SKIP] Chart generation skipped (--no-charts)")

    # Step 7: Generate Reports
    header("STEP 6: GENERATING REPORTS")

    # Cleaning summary
    report_path = os.path.join(args.output, "cleaning_report.txt")
    logger.save_report(report_path)
    logger.save_json_log(os.path.join(args.output, "cleaning_log.json"))

    # Before/After comparison
    generate_comparison_report(raw_df, cleaned_df, args.output)

    # Final Summary
    header("PIPELINE COMPLETE!")
    print(f"\n  [DIR] Output:      {os.path.abspath(args.output)}")
    print(f"  [FILE] Cleaned:    {os.path.abspath(args.save_cleaned)}")
    print(f"  [FILE] Report:     {os.path.abspath(report_path)}")
    print("\n  Done! Check the output/ directory for results.")
    print()


def header(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


if __name__ == "__main__":
    main()
