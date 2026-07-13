"""
Netflix Data Cleaning Module
================================
Handles all data cleaning operations for the Netflix Movies and TV Shows dataset.
Includes: missing value handling, duplicate removal, text standardization,
date parsing, data type fixes, and outlier detection.
"""

import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils import CleaningLogger


class NetflixCleaner:
    """Main data cleaning pipeline for the Netflix dataset."""

    # Standardized rating categories mapping
    RATING_MAP = {
        "TV-MA": "Mature",
        "TV-14": "Teen",
        "TV-PG": "Parental Guidance",
        "TV-Y": "Kids",
        "TV-Y7": "Older Kids",
        "TV-Y7-FV": "Older Kids",
        "R": "Mature",
        "PG-13": "Teen",
        "PG": "Parental Guidance",
        "G": "Kids",
        "NR": "Unrated",
        "UR": "Unrated",
        "NC-17": "Adults Only",
    }

    VALID_TYPES = ["Movie", "TV Show"]

    def __init__(self, logger: Optional[CleaningLogger] = None):
        self.logger = logger or CleaningLogger()
        self.cleaning_steps_performed: List[str] = []

    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load the Netflix dataset from CSV."""
        df = pd.read_csv(filepath)
        self.logger.log_operation(
            "LOAD",
            f"Loaded dataset with {df.shape[0]:,} rows and {df.shape[1]} columns",
            details={
                "file": filepath,
                "columns": list(df.columns),
                "memory_mb": df.memory_usage(deep=True).sum() / 1e6,
            },
        )
        return df

    def inspect(self, df: pd.DataFrame) -> Dict:
        """Perform initial inspection and return summary stats."""
        summary = {
            "rows": len(df),
            "cols": len(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "nulls_before": df.isnull().sum().to_dict(),
            "null_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicates": df.duplicated().sum(),
            "memory_mb": df.memory_usage(deep=True).sum() / 1e6,
        }
        self.logger.log_operation(
            "INSPECT",
            "Performed initial data inspection",
            details={
                "missing_cols": {k: v for k, v in summary["nulls_before"].items() if v > 0},
                "duplicate_rows": summary["duplicates"],
            },
        )
        return summary

    def drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows from the dataset."""
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        self.logger.log_operation(
            "DEDUP",
            "Removed duplicate rows",
            affected_rows=removed,
            details={"before": before, "after": len(df)},
        )
        self.cleaning_steps_performed.append("drop_duplicates")
        return df

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to clean, snake_case format."""
        rename_map = {
            "show_id": "show_id",
            "type": "content_type",
            "title": "title",
            "director": "director",
            "cast": "cast",
            "country": "country",
            "date_added": "date_added",
            "release_year": "release_year",
            "rating": "rating",
            "duration": "duration",
            "listed_in": "genre",
            "description": "description",
        }
        df = df.rename(columns=rename_map)
        self.logger.log_operation(
            "RENAME",
            "Standardized column names to snake_case",
            details={"rename_map": rename_map},
        )
        self.cleaning_steps_performed.append("standardize_columns")
        return df

    def handle_missing_director(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing director values with 'Unknown'."""
        missing = df["director"].isna().sum()
        if missing > 0:
            df["director"] = df["director"].fillna("Unknown")
            self.logger.log_operation(
                "FILL",
                "Filled missing director values with 'Unknown'",
                affected_rows=missing,
            )
        self.cleaning_steps_performed.append("fill_director")
        return df

    def handle_missing_cast(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing cast values with 'Not Available'."""
        missing = df["cast"].isna().sum()
        if missing > 0:
            df["cast"] = df["cast"].fillna("Not Available")
            self.logger.log_operation(
                "FILL",
                "Filled missing cast values with 'Not Available'",
                affected_rows=missing,
            )
        self.cleaning_steps_performed.append("fill_cast")
        return df

    def handle_missing_country(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing country values -- try to infer from other fields or mark as 'Unknown'."""
        missing = df["country"].isna().sum()
        if missing > 0:
            df["country"] = df["country"].fillna("Unknown")
            self.logger.log_operation(
                "FILL",
                "Filled missing country values with 'Unknown'",
                affected_rows=missing,
            )
        self.cleaning_steps_performed.append("fill_country")
        return df

    def parse_date_added(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize date_added column to datetime format."""
        before_missing = df["date_added"].isna().sum()
        # Parse dates in "Month Day, Year" format
        df["date_added"] = pd.to_datetime(
            df["date_added"], format="%B %d, %Y", errors="coerce"
        )
        after_missing = df["date_added"].isna().sum()
        newly_null = after_missing - before_missing

        # Drop rows where date_added couldn't be parsed (but keep originals)
        self.logger.log_operation(
            "PARSE",
            "Parsed date_added column to datetime format (Month Day, Year)",
            affected_rows=newly_null,
            details={
                "before_null": int(before_missing),
                "after_null": int(after_missing),
                "parsed_count": int(len(df) - after_missing),
            },
        )

        # Extract additional date features
        df["year_added"] = df["date_added"].dt.year
        df["month_added"] = df["date_added"].dt.month
        df["month_name_added"] = df["date_added"].dt.month_name()

        self.logger.log_operation(
            "EXTRACT",
            "Extracted year_added, month_added, and month_name_added features",
        )
        self.cleaning_steps_performed.append("parse_dates")
        return df

    def standardize_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize rating values into categories."""
        # Fill missing ratings first
        missing_ratings = df["rating"].isna().sum()
        if missing_ratings > 0:
            # For movies without rating, use the most common movie rating
            movie_rating = (
                df[df["content_type"] == "Movie"]["rating"].mode()
            )
            show_rating = (
                df[df["content_type"] == "TV Show"]["rating"].mode()
            )

            movie_mask = (df["content_type"] == "Movie") & df["rating"].isna()
            show_mask = (df["content_type"] == "TV Show") & df["rating"].isna()

            if not movie_rating.empty:
                df.loc[movie_mask, "rating"] = movie_rating.iloc[0]
            if not show_rating.empty:
                df.loc[show_mask, "rating"] = show_rating.iloc[0]

        # Create rating category column
        df["rating_category"] = df["rating"].map(self.RATING_MAP).fillna("Other")

        self.logger.log_operation(
            "STANDARDIZE",
            "Standardized ratings and created rating_category column",
            affected_rows=missing_ratings,
            details={
                "rating_categories": df["rating_category"].value_counts().to_dict()
            },
        )
        self.cleaning_steps_performed.append("standardize_rating")
        return df

    def parse_duration(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse duration into numeric values and type-specific columns."""
        # Fill missing duration
        missing_dur = df["duration"].isna().sum()
        if missing_dur > 0:
            df["duration"] = df["duration"].fillna("Unknown")

        # Extract numeric duration value
        def extract_duration(value: str) -> Tuple[Optional[int], str]:
            if value == "Unknown" or pd.isna(value):
                return None, "Unknown"
            match = re.match(r"(\d+)\s*(min|Season|Seasons)", str(value))
            if match:
                num = int(match.group(1))
                unit = "min" if "min" in match.group(2) else "seasons"
                return num, unit
            return None, "Unknown"

        duration_data = df["duration"].apply(extract_duration)
        df["duration_minutes"] = duration_data.apply(lambda x: x[0] if x[1] == "min" else None)
        df["duration_seasons"] = duration_data.apply(lambda x: x[0] if x[1] == "seasons" else None)
        df["duration_unit"] = duration_data.apply(lambda x: x[1])

        self.logger.log_operation(
            "PARSE",
            "Parsed duration into structured columns (duration_minutes, duration_seasons, duration_unit)",
            affected_rows=missing_dur,
            details={
                "movies_duration_parsed": int(df["duration_minutes"].notna().sum()),
                "shows_seasons_parsed": int(df["duration_seasons"].notna().sum()),
            },
        )
        self.cleaning_steps_performed.append("parse_duration")
        return df

    def clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize text fields -- strip whitespace, capitalize."""
        text_cols = ["title", "country", "genre", "description"]

        for col in text_cols:
            if col in df.columns:
                before_strip = df[col].str.strip().notna().sum()
                df[col] = df[col].str.strip()
                # Capitalize first letter of each sentence in description
                if col == "description":
                    df[col] = df[col].str.capitalize()

        self.logger.log_operation(
            "CLEAN_TEXT",
            "Cleaned text fields (stripped whitespace, capitalized descriptions)",
        )
        self.cleaning_steps_performed.append("clean_text")
        return df

    def split_genre_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Split the genre column into primary genre and list of genres."""
        # Use tuples instead of lists so the column remains hashable for duplicated()
        df["genre_list"] = df["genre"].str.split(", ").apply(tuple)
        df["primary_genre"] = df["genre_list"].apply(
            lambda x: x[0] if isinstance(x, tuple) and len(x) > 0 else None
        )
        df["genre_count"] = df["genre_list"].apply(
            lambda x: len(x) if isinstance(x, tuple) else 0
        )

        self.logger.log_operation(
            "SPLIT",
            "Split genre column into genre_list, primary_genre, and genre_count",
            details={
                "unique_genres": int(df["primary_genre"].nunique()),
            },
        )
        self.cleaning_steps_performed.append("split_genre")
        return df

    def flag_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flag potential outliers in release_year using IQR method."""
        Q1 = df["release_year"].quantile(0.25)
        Q3 = df["release_year"].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df["is_outlier_year"] = (df["release_year"] < lower) | (df["release_year"] > upper)

        outlier_count = df["is_outlier_year"].sum()
        self.logger.log_operation(
            "OUTLIER",
            "Flagged outlier release years using IQR method",
            affected_rows=int(outlier_count),
            details={
                "q1": int(Q1),
                "q3": int(Q3),
                "iqr": int(IQR),
                "bounds": f"[{int(lower)}, {int(upper)}]",
            },
        )
        self.cleaning_steps_performed.append("flag_outliers")
        return df

    def run_full_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run the complete cleaning pipeline on the dataset."""
        print("\n" + "=" * 60)
        print("  NETFLIX DATA CLEANING PIPELINE")
        print("=" * 60)

        df = self.drop_duplicates(df)
        df = self.standardize_column_names(df)

        # Handle missing values
        df = self.handle_missing_director(df)
        df = self.handle_missing_cast(df)
        df = self.handle_missing_country(df)

        # Parse and standardize
        df = self.parse_date_added(df)
        df = self.standardize_rating(df)
        df = self.parse_duration(df)

        # Text cleaning
        df = self.clean_text_fields(df)
        df = self.split_genre_column(df)

        # Quality checks
        df = self.flag_outliers(df)

        print("=" * 60)
        print(f"  [OK] Pipeline complete! {len(df):,} rows processed.")
        print(f"  [OK] {len(self.cleaning_steps_performed)} cleaning steps applied.")
        print("=" * 60)

        return df
