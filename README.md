# 🎬 Netflix Data Cleaning & Preprocessing Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-3.0%2B-green)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive **data cleaning and preprocessing pipeline** built for the Netflix Movies and TV Shows dataset (~8,800 titles). This project demonstrates professional-grade data cleaning techniques using Python and Pandas.

---

## 📋 Task Overview

**Objective:** Clean and prepare a raw dataset containing nulls, duplicates, and inconsistent formats.

**Dataset:** [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) — 8,807 titles with 12 columns of metadata.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Duplicate Removal** | Identifies and removes duplicate rows |
| **Missing Value Handling** | Intelligently fills missing directors, cast, countries, and ratings |
| **Date Parsing** | Converts "Month Day, Year" strings to proper datetime |
| **Data Type Correction** | Fixes incorrect data types across all columns |
| **Text Standardization** | Strips whitespace, capitalizes descriptions |
| **Rating Classification** | Groups ratings into meaningful categories (Kids, Teen, Mature, etc.) |
| **Duration Parsing** | Separates movie durations (minutes) from TV show seasons |
| **Genre Analysis** | Splits multi-genre entries, extracts primary genre |
| **Outlier Detection** | Flags anomalous release years using IQR method |
| **Visualizations** | Generates 8 informative charts (PNG) |
| **Comprehensive Reports** | Auto-generates cleaning summaries and JSON logs |

---

## 📁 Project Structure

```
netflix-data-cleaning/
├── data/
│   ├── raw/                      # Original unprocessed data
│   │   └── netflix_titles.csv
│   └── cleaned/                  # Final cleaned output
│       └── netflix_titles_cleaned.csv
├── src/
│   ├── __init__.py
│   ├── cleaner.py                # Core cleaning pipeline
│   ├── utils.py                  # Logging & reporting utilities
│   └── visualizer.py             # Chart generation & comparisons
├── output/                       # Auto-generated reports & charts
│   ├── cleaning_report.txt       # Detailed cleaning summary
│   ├── cleaning_log.json         # Machine-readable operation log
│   ├── comparison_report.txt     # Before/After analysis
│   └── charts/                   # Generated visualizations
│       ├── content_distribution.png
│       ├── missing_values_comparison.png
│       ├── rating_distribution.png
│       ├── release_year_trend.png
│       ├── top_countries.png
│       ├── top_genres.png
│       ├── duration_distribution.png
│       └── monthly_additions.png
├── screenshots/                  # Screenshots for submission
├── notebooks/                    # Jupyter notebooks (optional)
├── requirements.txt              # Python dependencies
├── run.py                        # Main entry point
└── README.md                     # This file
```

---

## 🛠️ Cleaning Operations (12 Steps)

| # | Operation | Description |
|---|-----------|-------------|
| 1 | **Drop Duplicates** | Removes exact duplicate rows |
| 2 | **Standardize Columns** | Renames columns to consistent snake_case |
| 3 | **Fill Director** | Missing directors → `"Unknown"` |
| 4 | **Fill Cast** | Missing cast → `"Not Available"` |
| 5 | **Fill Country** | Missing countries → `"Unknown"` |
| 6 | **Parse Date Added** | Converts text dates to `datetime` |
| 7 | **Extract Date Features** | Creates `year_added`, `month_added` columns |
| 8 | **Standardize Ratings** | Maps ratings to categories (Kids, Teen, Mature, etc.) |
| 9 | **Parse Duration** | Separates minutes vs seasons into numeric columns |
| 10 | **Clean Text** | Strips whitespace, capitalizes descriptions |
| 11 | **Split Genre** | Extracts primary genre and genre count |
| 12 | **Flag Outliers** | Identifies outlier release years via IQR |

---

## ⚡ Quick Start

### 1. Clone or download the project

```bash
cd netflix-data-cleaning
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the dataset

**Option A: Auto-download (recommended)**
```bash
python -c "
import kagglehub
path = kagglehub.dataset_download('shivamb/netflix-shows')
import shutil, os
for f in os.listdir(path):
    if f.endswith('.csv'):
        os.makedirs('data/raw', exist_ok=True)
        shutil.copy(os.path.join(path, f), 'data/raw/netflix_titles.csv')
        print(f'Downloaded to: data/raw/netflix_titles.csv')
"
```

**Option B: Manual download**
1. Download from [Kaggle](https://www.kaggle.com/datasets/shivamb/netflix-shows)
2. Place `netflix_titles.csv` in `data/raw/`

### 4. Run the pipeline

```bash
# Full pipeline
python run.py

# Custom paths
python run.py --input data/raw/netflix_titles.csv --output ./my_reports

# Skip chart generation (faster)
python run.py --no-charts
```

---

## 📊 Sample Output

### Before Cleaning
```
Columns with missing values:
  - director:   2,634 (29.9%)
  - cast:         825 (9.4%)
  - country:      831 (9.4%)
  - date_added:    10 (0.1%)
  - rating:         4 (0.05%)
  - duration:       3 (0.03%)

Duplicate rows: 0
```

### After Cleaning
```
✅ Missing values resolved: 4,307
✅ 12 cleaning steps applied
✅ 8 charts generated
✅ Final shape: 8,807 rows × 18 columns
```

### New Columns Created
| Column | Description |
|--------|-------------|
| `content_type` | Renamed from `type` |
| `genre` | Renamed from `listed_in` |
| `year_added` | Extracted year from `date_added` |
| `month_added` | Extracted month number |
| `month_name_added` | Month name (e.g., "January") |
| `rating_category` | Categorized rating (Kids, Teen, etc.) |
| `duration_minutes` | Movie runtime in minutes |
| `duration_seasons` | TV show season count |
| `duration_unit` | Unit type ("min" or "seasons") |
| `genre_list` | List of all genres |
| `primary_genre` | First/most relevant genre |
| `genre_count` | Number of genres per title |
| `is_outlier_year` | Flag for outlier release years |

---

## 📸 Screenshots

Place your pipeline screenshots in the `screenshots/` directory:

1. **Raw data preview** — First look at the unprocessed dataset
2. **Missing values** — Before/after comparison
3. **Cleaned data** — Final clean dataset preview
4. **Charts** — Sample visualizations

---

## 🧪 Interview Preparation

This project prepares you to answer these common interview questions:

1. **How do you handle missing values?** — Fill with `"Unknown"`, mode imputation, or remove if excessive
2. **What's the difference between `dropna()` and `fillna()`?** — `dropna()` removes missing rows; `fillna()` replaces them with a value
3. **How do you treat outliers?** — IQR method with 1.5× rule flags potential outliers
4. **How do you standardize data?** — Text cleaning, date parsing, categorical mapping
5. **What are data quality checks?** — Null counts, duplicates, data types, value ranges, uniqueness
6. **How do you manage inconsistent formats?** — Regex parsing, datetime conversion, categorical mappings
7. **Why is data cleaning important?** — Garbage in, garbage out; dirty data leads to incorrect analysis
8. **How do you validate cleaning?** — Compare before/after stats, verify data types, check value distributions

---

## 📝 Submission Checklist

- [ ] ✅ Code pushed to GitHub repository
- [ ] ✅ Cleaned dataset included (`data/cleaned/`)
- [ ] ✅ Screenshots in `screenshots/` folder
- [ ] ✅ This README is complete
- [ ] ✅ Cleaning report generated (`output/cleaning_report.txt`)
- [ ] ✅ Charts generated (`output/charts/`)
- [ ] ✅ Dependencies listed (`requirements.txt`)

---

## 🎯 Bonus Ideas (Go Beyond!)

| Idea | Description |
|------|-------------|
| **Excel Export** | Save cleaned data as `.xlsx` with formatting |
| **SQL Export** | Output cleaning results to a SQLite database |
| **Interactive Dashboard** | Build a Streamlit dashboard for the cleaned data |
| **Advanced NLP** | Analyze descriptions for sentiment or topic modeling |
| **ML Ready** | Encode categorical features for machine learning |
| **API** | Serve the cleaning pipeline as a Flask/FastAPI endpoint |

---

## 📄 License

This project is created for educational purposes as part of a Data Analyst Internship task.

---

*Made with ❤️ using Python, Pandas & Open Source*
