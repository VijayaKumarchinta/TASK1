"""
Visualization and Reporting Module for Netflix Data Cleaning.
Generates charts, summaries, and comparison reports.
"""

import os
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.utils import ensure_dir, get_hashable_cols


class NetflixVisualizer:
    """Generates visualizations and comparison reports."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        ensure_dir(output_dir)
        ensure_dir(os.path.join(output_dir, "charts"))

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams.update({
            "figure.figsize": (12, 6),
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
        })

    def _save_chart(self, name: str):
        """Save the current matplotlib figure."""
        path = os.path.join(self.output_dir, "charts", name)
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  [CHART] Chart saved: {path}")
        return path

    def plot_content_distribution(self, df: pd.DataFrame) -> str:
        """Plot distribution of Movies vs TV Shows."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        counts = df["content_type"].value_counts()
        colors = ["#E50914", "#221F1F"]

        # Pie chart
        ax1.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            explode=(0.05, 0),
            shadow=False,
        )
        ax1.set_title("Content Type Distribution")

        # Bar chart
        bars = ax2.bar(counts.index, counts.values, color=colors, width=0.4)
        ax2.set_title("Content Type Count")
        ax2.set_ylabel("Number of Titles")
        for bar, val in zip(bars, counts.values):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 50,
                f"{val:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        return self._save_chart("content_distribution.png")

    def plot_missing_values(self, before: pd.Series, after: pd.Series) -> str:
        """Plot missing values comparison before and after cleaning."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        for ax, data, title in zip(
            axes, [before, after],
            ["Missing Values -- Before", "Missing Values -- After"]
        ):
            missing = data[data > 0]
            if len(missing) == 0:
                ax.text(0.5, 0.5, "[OK] No missing values!", ha="center", va="center", fontsize=13)
                ax.set_title(title)
                continue

            bars = ax.barh(
                missing.index, missing.values,
                color="#E50914" if "Before" in title else "#2E8B57"
            )
            ax.set_title(title)
            ax.set_xlabel("Count")
            for bar, val in zip(bars, missing.values):
                ax.text(
                    bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=10
                )

        return self._save_chart("missing_values_comparison.png")

    def plot_rating_distribution(self, df: pd.DataFrame) -> str:
        """Plot the distribution of content ratings."""
        fig, ax = plt.subplots(figsize=(14, 5))
        rating_counts = df["rating_category"].value_counts()
        colors = plt.cm.Reds_r(
            np.linspace(0.3, 0.9, len(rating_counts))
        )
        bars = ax.bar(rating_counts.index, rating_counts.values, color=colors)
        ax.set_title("Content by Rating Category")
        ax.set_xlabel("Rating Category")
        ax.set_ylabel("Number of Titles")
        ax.tick_params(axis="x", rotation=30)

        for bar, val in zip(bars, rating_counts.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 50,
                f"{val:,}",
                ha="center", va="bottom", fontsize=9,
            )

        return self._save_chart("rating_distribution.png")

    def plot_release_year_trend(self, df: pd.DataFrame) -> str:
        """Plot the trend of releases over years."""
        fig, ax = plt.subplots(figsize=(14, 5))
        year_counts = df["release_year"].value_counts().sort_index()
        year_counts = year_counts[year_counts.index >= 2000]  # Focus on recent

        ax.fill_between(year_counts.index, year_counts.values, alpha=0.3, color="#E50914")
        ax.plot(year_counts.index, year_counts.values, color="#E50914", linewidth=2)
        ax.set_title("Netflix Content Releases (2000 onwards)")
        ax.set_xlabel("Release Year")
        ax.set_ylabel("Number of Titles")

        return self._save_chart("release_year_trend.png")

    def plot_top_countries(self, df: pd.DataFrame, top_n: int = 15) -> str:
        """Plot top countries by content production."""
        fig, ax = plt.subplots(figsize=(12, 6))

        country_counts = df["country"].value_counts().head(top_n)
        bars = ax.barh(
            country_counts.index[::-1],
            country_counts.values[::-1],
            color="#E50914",
        )
        ax.set_title(f"Top {top_n} Countries by Content Production")
        ax.set_xlabel("Number of Titles")

        for bar, val in zip(bars, country_counts.values[::-1]):
            ax.text(
                bar.get_width() + 10,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                fontsize=9,
            )

        return self._save_chart("top_countries.png")

    def plot_top_genres(self, df: pd.DataFrame, top_n: int = 15) -> str:
        """Plot top primary genres."""
        fig, ax = plt.subplots(figsize=(12, 6))

        genre_counts = df["primary_genre"].value_counts().head(top_n)
        bars = ax.barh(
            genre_counts.index[::-1],
            genre_counts.values[::-1],
            color="#221F1F",
        )
        ax.set_title(f"Top {top_n} Genres on Netflix")
        ax.set_xlabel("Number of Titles")

        for bar, val in zip(bars, genre_counts.values[::-1]):
            ax.text(
                bar.get_width() + 10,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center",
                fontsize=9,
            )

        return self._save_chart("top_genres.png")

    def plot_duration_distribution(self, df: pd.DataFrame) -> str:
        """Plot duration distribution for movies."""
        fig, ax = plt.subplots(figsize=(12, 5))

        movie_durations = df[df["content_type"] == "Movie"]["duration_minutes"].dropna()
        ax.hist(movie_durations, bins=50, color="#E50914", alpha=0.7, edgecolor="white")
        ax.set_title("Movie Duration Distribution")
        ax.set_xlabel("Duration (minutes)")
        ax.set_ylabel("Number of Movies")

        median_dur = movie_durations.median()
        ax.axvline(median_dur, color="#221F1F", linestyle="--", linewidth=2, label=f"Median: {median_dur:.0f} min")
        ax.legend()

        return self._save_chart("duration_distribution.png")

    def plot_monthly_additions(self, df: pd.DataFrame) -> str:
        """Plot content additions by month."""
        fig, ax = plt.subplots(figsize=(12, 5))

        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        monthly = df["month_name_added"].value_counts().reindex(month_order).fillna(0)

        bars = ax.bar(month_order, monthly.values, color="#E50914", alpha=0.8)
        ax.set_title("Content Additions by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Titles Added")
        ax.tick_params(axis="x", rotation=45)

        return self._save_chart("monthly_additions.png")

    def generate_all_charts(self, df: pd.DataFrame, null_before: pd.Series, null_after: pd.Series) -> Dict[str, str]:
        """Generate all standard charts and return paths."""
        print("\n" + "=" * 60)
        print("  GENERATING VISUALIZATIONS")
        print("=" * 60)

        charts = {}
        charts["content_distribution"] = self.plot_content_distribution(df)
        charts["missing_values"] = self.plot_missing_values(null_before, null_after)
        charts["rating_distribution"] = self.plot_rating_distribution(df)
        charts["release_year_trend"] = self.plot_release_year_trend(df)
        charts["top_countries"] = self.plot_top_countries(df)
        charts["top_genres"] = self.plot_top_genres(df)
        charts["duration_distribution"] = self.plot_duration_distribution(df)
        charts["monthly_additions"] = self.plot_monthly_additions(df)

        print("=" * 60)
        print(f"  [OK] All charts saved to {self.output_dir}/charts/")
        print("=" * 60)

        return charts


def generate_comparison_report(
    raw_df: pd.DataFrame, cleaned_df: pd.DataFrame, output_dir: str = "output"
) -> str:
    """Generate a before/after comparison report."""
    ensure_dir(output_dir)

    lines = [
        "=" * 70,
        "  BEFORE vs AFTER CLEANING COMPARISON",
        "=" * 70,
        "",
        f"  {'Metric':<30} {'Before':<15} {'After':<15}",
        "-" * 60,
        f"  {'Total Rows':<30} {len(raw_df):<15,} {len(cleaned_df):<15,}",
        f"  {'Total Columns':<30} {len(raw_df.columns):<15} {len(cleaned_df.columns):<15}",
        f"  {'Duplicates Removed':<30} {raw_df.duplicated().sum():<15,} {cleaned_df[get_hashable_cols(cleaned_df)].duplicated().sum():<15,}",
        "",
        "  MISSING VALUES:",
        f"  {'Column':<30} {'Before':<15} {'After':<15}",
        "-" * 60,
    ]

    for col in raw_df.columns:
        raw_null = int(raw_df[col].isna().sum())
        if col in cleaned_df.columns:
            clean_null = int(cleaned_df[col].isna().sum())
        else:
            clean_null = "N/A"
        if raw_null > 0:
            lines.append(f"  {col:<30} {raw_null:<15,} {str(clean_null):<15}")

    lines.extend([
        "",
        "-" * 70,
        "  NEW COLUMNS ADDED:",
    ])

    new_cols = set(cleaned_df.columns) - set(raw_df.columns)
    if new_cols:
        for col in sorted(new_cols):
            lines.append(f"  [OK] {col}")
    else:
        lines.append("  (none)")

    lines.extend([
        "",
        "  CLEANING STEPS PERFORMED:",
    ])

    steps = [
        "1. Removed duplicate rows",
        "2. Standardized column names to snake_case",
        "3. Filled missing director values with 'Unknown'",
        "4. Filled missing cast values with 'Not Available'",
        "5. Filled missing country values with 'Unknown'",
        "6. Parsed date_added to datetime format",
        "7. Extracted year/month features from dates",
        "8. Standardized ratings into categories",
        "9. Parsed duration into structured numeric columns",
        "10. Cleaned text fields (whitespace, capitalization)",
        "11. Split genre column into primary genre and list",
        "12. Flagged outlier release years using IQR",
    ]
    for step in steps:
        lines.append(f"  ? {step}")

    lines.extend(["", "=" * 70, "  END OF COMPARISON REPORT", "=" * 70])

    report = "\n".join(lines)
    path = os.path.join(output_dir, "comparison_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n[DOC] Comparison report saved to: {path}")

    return path
