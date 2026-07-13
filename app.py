"""
Netflix Data Explorer — Streamlit Dashboard
==============================================
Interactive dashboard for exploring the cleaned Netflix Movies & TV Shows dataset.

Run with: streamlit run app.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config (MUST be first Streamlit command) ──
st.set_page_config(
    page_title="Netflix Data Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ──
DATA_PATH = "data/cleaned/netflix_titles_cleaned.csv"
NETFLIX_RED = "#E50914"
NETFLIX_DARK = "#221F1F"
NETFLIX_LIGHT = "#F5F5F5"
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ── Data Loading ──
@st.cache_data(show_spinner="Loading Netflix data...")
def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        st.error(f"Cleaned data not found at {DATA_PATH}. Run the pipeline first: `python run.py`")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    # Parse dates
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    return df


# ── Sidebar ──
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        # Branding
        st.markdown(
            f"""
            <div style="text-align:center; padding: 1rem 0;">
                <span style="font-size:3rem;">🎬</span>
                <h2 style="color:{NETFLIX_RED}; margin:0;">Netflix</h2>
                <p style="color:gray; font-size:0.85rem;">Data Explorer</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation
        page = st.radio(
            "Navigate",
            ["📊 Overview", "🔍 Content Explorer", "📈 Analytics", "✅ Data Quality"],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("### Filters")
        st.caption("Apply filters across all pages")

        # Content type filter
        content_types = ["All"] + sorted(df["content_type"].dropna().unique().tolist())
        selected_type = st.selectbox("Content Type", content_types, key="_filter_type")

        # Genre filter
        all_genres = []
        if "primary_genre" in df.columns:
            all_genres = ["All"] + sorted(df["primary_genre"].dropna().unique().tolist())
        selected_genre = st.selectbox("Genre", all_genres, key="_filter_genre")

        # Year range filter
        if "release_year" in df.columns:
            min_year = int(df["release_year"].min())
            max_year = int(df["release_year"].max())
            year_range = st.slider(
                "Release Year", min_year, max_year, (min_year, max_year),
                key="_filter_year",
            )
        else:
            year_range = (1900, 2025)

        # Rating filter
        if "rating_category" in df.columns:
            ratings = ["All"] + sorted(df["rating_category"].dropna().unique().tolist())
            selected_rating = st.selectbox("Rating Category", ratings, key="_filter_rating")
        else:
            selected_rating = "All"

        # Country filter
        if "country" in df.columns:
            countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
            selected_country = st.selectbox("Country", countries, key="_filter_country")
        else:
            selected_country = "All"

        st.divider()
        st.caption(f"Dataset: {len(df):,} titles · {df.shape[1]} columns")

        # Reset button — clears session state keys to force widges back to defaults
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state["_filter_type"] = "All"
            st.session_state["_filter_genre"] = "All"
            st.session_state["_filter_rating"] = "All"
            st.session_state["_filter_country"] = "All"
            if "release_year" in df.columns:
                st.session_state["_filter_year"] = (
                    int(df["release_year"].min()), int(df["release_year"].max())
                )
            st.rerun()

        # Persist filter defaults in session state for the reset button
        if "_filter_type" not in st.session_state:
            st.session_state["_filter_type"] = "All"
        if "_filter_genre" not in st.session_state:
            st.session_state["_filter_genre"] = "All"
        if "_filter_rating" not in st.session_state:
            st.session_state["_filter_rating"] = "All"
        if "_filter_country" not in st.session_state:
            st.session_state["_filter_country"] = "All"
        if "release_year" in df.columns:
            if "_filter_year" not in st.session_state:
                st.session_state["_filter_year"] = (int(df["release_year"].min()), int(df["release_year"].max()))

    filters = {
        "content_type": selected_type,
        "genre": selected_genre,
        "year_range": year_range,
        "rating": selected_rating,
        "country": selected_country,
    }
    return page, filters


# ── Apply Filters ──
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    filtered = df.copy()

    if filters["content_type"] != "All":
        filtered = filtered[filtered["content_type"] == filters["content_type"]]

    if filters["genre"] != "All" and "primary_genre" in filtered.columns:
        filtered = filtered[filtered["primary_genre"] == filters["genre"]]

    if "release_year" in filtered.columns:
        filtered = filtered[
            (filtered["release_year"] >= filters["year_range"][0])
            & (filtered["release_year"] <= filters["year_range"][1])
        ]

    if filters["rating"] != "All" and "rating_category" in filtered.columns:
        filtered = filtered[filtered["rating_category"] == filters["rating"]]

    if filters["country"] != "All" and "country" in filtered.columns:
        filtered = filtered[filtered["country"] == filters["country"]]

    return filtered


# ── Page: Overview ──
def page_overview(df: pd.DataFrame):
    st.markdown(
        f"""
        <h1 style="color:{NETFLIX_DARK}; border-bottom: 3px solid {NETFLIX_RED}; padding-bottom: 0.5rem;">
            Netflix Content Overview
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI Row ──
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Titles", f"{len(df):,}", help="Total number of movies and TV shows")
    with col2:
        movie_count = len(df[df["content_type"] == "Movie"])
        st.metric("Movies", f"{movie_count:,}", help=f"{movie_count/len(df)*100:.1f}% of content")
    with col3:
        show_count = len(df[df["content_type"] == "TV Show"])
        st.metric("TV Shows", f"{show_count:,}", help=f"{show_count/len(df)*100:.1f}% of content")
    with col4:
        if "primary_genre" in df.columns:
            top_genre = df["primary_genre"].mode().iloc[0] if not df["primary_genre"].mode().empty else "N/A"
            st.metric("Top Genre", top_genre, help="Most common primary genre")
    with col5:
        if "release_year" in df.columns:
            recent_year = int(df["release_year"].max())
            oldest_year = int(df["release_year"].min())
            st.metric("Year Range", f"{oldest_year}–{recent_year}", help="Range of release years")

    st.divider()

    # ── Two-column layout ──
    left_col, right_col = st.columns([1, 1])

    with left_col:
        # Content Type Distribution
        type_counts = df["content_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.pie(
            type_counts,
            values="count",
            names="type",
            title="Content Type Distribution",
            color_discrete_sequence=[NETFLIX_RED, "#333333"],
            hole=0.45,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            marker=dict(line=dict(color="white", width=2)),
        )
        fig.update_layout(
            height=400,
            margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        if "rating_category" in df.columns:
            rating_counts = df["rating_category"].value_counts().reset_index()
            rating_counts.columns = ["rating", "count"]
            fig = px.bar(
                rating_counts,
                x="rating",
                y="count",
                title="Content by Rating Category",
                color="rating",
                color_discrete_sequence=px.colors.sequential.Reds_r,
            )
            fig.update_traces(showlegend=False)
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=10, l=40, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="Number of Titles",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Bottom row: additional stats ──
    bcol1, bcol2 = st.columns(2)

    with bcol1:
        # Top 10 Countries
        if "country" in df.columns:
            country_counts = (
                df["country"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            country_counts.columns = ["country", "count"]
            fig = px.bar(
                country_counts,
                y="country",
                x="count",
                title="Top 10 Countries by Content Production",
                orientation="h",
                color="count",
                color_continuous_scale=["#FFE0E0", NETFLIX_RED],
            )
            fig.update_traces(showlegend=False)
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="",
                xaxis_title="Number of Titles",
            )
            st.plotly_chart(fig, use_container_width=True)

    with bcol2:
        if "primary_genre" in df.columns:
            genre_counts = (
                df["primary_genre"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            genre_counts.columns = ["genre", "count"]
            fig = px.bar(
                genre_counts,
                y="genre",
                x="count",
                title="Top 10 Genres",
                orientation="h",
                color="count",
                color_continuous_scale=["#FFE0E0", NETFLIX_RED],
            )
            fig.update_traces(showlegend=False)
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="",
                xaxis_title="Number of Titles",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Release Year Trend ──
    st.divider()
    if "release_year" in df.columns:
        year_counts = df["release_year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["year", "count"]
        fig = px.area(
            year_counts,
            x="year",
            y="count",
            title="Content Releases Over Time",
        )
        fig.update_traces(
            line_color=NETFLIX_RED,
            fillcolor="rgba(229, 9, 20, 0.15)",
            line_width=2,
        )
        fig.update_layout(
            height=350,
            margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Release Year",
            yaxis_title="Number of Titles",
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Page: Content Explorer ──
def page_explorer(df: pd.DataFrame):
    st.markdown(
        f"""
        <h1 style="color:{NETFLIX_DARK}; border-bottom: 3px solid {NETFLIX_RED}; padding-bottom: 0.5rem;">
            Content Explorer
        </h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Browse, search, and filter the Netflix catalog. Click column headers to sort.")

    # Search bar
    search_query = st.text_input(
        "🔍 Search titles, directors, or cast",
        placeholder="e.g., Stranger Things, Christopher Nolan...",
        label_visibility="collapsed",
    )

    # Column selector
    display_cols = [
        "title", "content_type", "primary_genre", "release_year",
        "rating_category", "country", "director", "cast",
        "duration_minutes", "duration_seasons", "date_added",
        "description",
    ]
    available_cols = [c for c in display_cols if c in df.columns]

    with st.expander("⚙️ Column Visibility", expanded=False):
        selected_cols = st.multiselect(
            "Choose columns to display",
            options=available_cols,
            default=[c for c in available_cols if c not in ("description", "cast")],
            label_visibility="collapsed",
        )

    if not selected_cols:
        selected_cols = ["title", "content_type", "release_year"]

    # Apply search filter
    display_df = df.copy()
    if search_query:
        search_mask = display_df.astype(str).apply(
            lambda row: row.str.contains(search_query, case=False, na=False).any(),
            axis=1,
        )
        display_df = display_df[search_mask]
        st.caption(f"Found {len(display_df):,} results for **'{search_query}'**")

    # Format display columns
    display_data = display_df[selected_cols].copy()
    if "date_added" in display_data.columns and pd.api.types.is_datetime64_any_dtype(
        display_data["date_added"]
    ):
        display_data["date_added"] = display_data["date_added"].dt.strftime("%b %d, %Y")

    # Show data table
    st.dataframe(
        display_data,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Title", width="large"),
            "director": st.column_config.TextColumn("Director", width="medium"),
            "cast": st.column_config.TextColumn("Cast", width="large"),
            "description": st.column_config.TextColumn("Description", width="xlarge"),
            "release_year": st.column_config.NumberColumn("Year", format="%d"),
            "duration_minutes": st.column_config.NumberColumn("Minutes", format="%d min"),
            "duration_seasons": st.column_config.NumberColumn("Seasons", format="%d seasons"),
        },
    )

    # Row count info
    total_matching = len(display_df)
    total_all = len(df)
    st.caption(f"Showing {total_matching:,} of {total_all:,} titles")


# ── Page: Analytics ──
def page_analytics(df: pd.DataFrame):
    st.markdown(
        f"""
        <h1 style="color:{NETFLIX_DARK}; border-bottom: 3px solid {NETFLIX_RED}; padding-bottom: 0.5rem;">
            Analytics
        </h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Interactive charts with cross-filtering")

    # ── Row 1: Duration Analysis ──
    if "duration_minutes" in df.columns:
        st.subheader("🎞️ Movie Duration Analysis")
        movie_df = df[df["content_type"] == "Movie"]["duration_minutes"].dropna()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Movie Length", f"{movie_df.mean():.0f} min")
        with col2:
            st.metric("Median", f"{movie_df.median():.0f} min")
        with col3:
            st.metric("Longest Movie", f"{movie_df.max():.0f} min")

        fig = px.histogram(
            movie_df,
            nbins=50,
            title="Distribution of Movie Durations",
            color_discrete_sequence=[NETFLIX_RED],
            labels={"value": "Duration (minutes)", "count": "Number of Movies"},
        )
        fig.add_vline(x=movie_df.median(), line_dash="dash", line_color=NETFLIX_DARK,
                       annotation_text=f"Median: {movie_df.median():.0f} min")
        fig.update_layout(height=350, margin=dict(t=40), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Monthly Additions Heatmap ──
    if all(c in df.columns for c in ["year_added", "month_name_added"]):
        st.subheader("📅 Content Additions Calendar")
        monthly_ct = (
            df.groupby(["year_added", "month_name_added"])
            .size()
            .reset_index(name="count")
        )
        monthly_ct["month_name_added"] = pd.Categorical(
            monthly_ct["month_name_added"],
            categories=MONTH_ORDER,
            ordered=True,
        )
        heatmap_data = monthly_ct.pivot_table(
            index="year_added", columns="month_name_added", values="count", fill_value=0
        )

        fig = px.imshow(
            heatmap_data,
            title="Titles Added to Netflix (by Month & Year)",
            color_continuous_scale=["#FFF0F0", "#FFCCCC", NETFLIX_RED],
            aspect="auto",
            labels={"x": "Month", "y": "Year", "color": "Titles"},
        )
        fig.update_layout(height=400, margin=dict(t=40), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Genre Comparison ──
    if "primary_genre" in df.columns and "content_type" in df.columns:
        st.subheader("🎭 Genre Comparison: Movies vs TV Shows")
        genre_ct = (
            df.groupby(["primary_genre", "content_type"])
            .size()
            .reset_index(name="count")
        )
        top_genres = (
            genre_ct.groupby("primary_genre")["count"]
            .sum()
            .sort_values(ascending=False)
            .head(12)
            .index
        )
        genre_ct = genre_ct[genre_ct["primary_genre"].isin(top_genres)]

        fig = px.bar(
            genre_ct,
            x="count",
            y="primary_genre",
            color="content_type",
            orientation="h",
            title="Top Genres by Content Type",
            color_discrete_map={"Movie": NETFLIX_RED, "TV Show": NETFLIX_DARK},
            barmode="group",
        )
        fig.update_layout(
            height=500,
            margin=dict(t=40),
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title="",
            xaxis_title="Number of Titles",
            legend_title="Type",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 4: Rating vs Duration ──
    if all(c in df.columns for c in ["duration_minutes", "rating_category", "content_type"]):
        st.subheader("📊 Rating vs Duration (Movies)")
        movie_plot = df[(df["content_type"] == "Movie") & (df["duration_minutes"].notna())]
        fig = px.box(
            movie_plot,
            x="rating_category",
            y="duration_minutes",
            title="Movie Duration Distribution by Rating Category",
            color="rating_category",
            color_discrete_sequence=px.colors.sequential.Reds_r,
            points="outliers",
        )
        fig.update_traces(showlegend=False)
        fig.update_layout(
            height=450,
            margin=dict(t=40),
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Rating Category",
            yaxis_title="Duration (minutes)",
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Page: Data Quality ──
def page_quality(df: pd.DataFrame):
    st.markdown(
        f"""
        <h1 style="color:{NETFLIX_DARK}; border-bottom: 3px solid {NETFLIX_RED}; padding-bottom: 0.5rem;">
            Data Quality Report
        </h1>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Completeness and quality metrics for the cleaned dataset")

    # ── Completeness Overview ──
    st.subheader("📋 Column Completeness")
    completeness = []
    for col in df.columns:
        total = len(df)
        non_null = df[col].notna().sum()
        null_count = total - non_null
        null_pct = (null_count / total) * 100
        dtype = str(df[col].dtype)
        completeness.append(
            {"Column": col, "Type": dtype, "Non-Null": non_null, "Nulls": null_count, "Null %": f"{null_pct:.1f}%"}
        )

    comp_df = pd.DataFrame(completeness)

    # Color-coded completeness bar
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=comp_df["Column"],
        x=comp_df["Non-Null"],
        name="Complete",
        orientation="h",
        marker_color=NETFLIX_RED,
        hovertemplate="%{y}: %{x:,} complete<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=comp_df["Column"],
        x=comp_df["Nulls"],
        name="Missing",
        orientation="h",
        marker_color="#DDDDDD",
        hovertemplate="%{y}: %{x:,} missing<extra></extra>",
    ))
    fig.update_layout(
        barmode="stack",
        height=500,
        margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Row Count",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Quality Table ──
    with st.expander("📊 Detailed Quality Metrics", expanded=False):
        # Color coding for null percentage
        def color_null(val):
            if "0.0%" in str(val):
                return "background-color: #DFF0D8"
            elif any(f"{i}." in str(val) for i in range(1, 10)):
                return "background-color: #FCF8E3"
            return ""

        styled = comp_df.style.map(color_null, subset=["Null %"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Data Types ──
    st.subheader("📌 Column Data Types")
    dtype_df = pd.DataFrame(
        {"Column": comp_df["Column"], "Data Type": comp_df["Type"]}
    )
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    # ── Cleaning Summary ──
    st.subheader("🧹 Cleaning Summary")
    original_cols = 12  # Base Netflix dataset
    new_features = df.shape[1] - original_cols
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Columns", original_cols)
    with col2:
        st.metric("New Features Added", new_features, delta=f"+{new_features}")
    with col3:
        st.metric("Total Columns", df.shape[1])

    # Read cleaning report if available
    report_path = "output/cleaning_report.txt"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report_text = f.read()
        with st.expander("📄 View Full Cleaning Report", expanded=False):
            st.text(report_text)


# ── Main App ──
def main():
    # Load data
    df = load_data()

    # Sidebar
    page, filters = render_sidebar(df)

    # Apply filters
    filtered_df = apply_filters(df, filters)

    # Show active filter indicator
    active_filters = [k for k, v in filters.items() if v != "All" and (
        k != "year_range" or v != (int(df["release_year"].min()), int(df["release_year"].max()))
    )]
    if active_filters:
        st.caption(f"🎯 Active filters: {', '.join(active_filters)} | Showing {len(filtered_df):,} titles")

    # Page routing — handle empty data gracefully
    pages = {
        "📊 Overview": page_overview,
        "🔍 Content Explorer": page_explorer,
        "📈 Analytics": page_analytics,
        "✅ Data Quality": page_quality,
    }
    page_handler = pages.get(page, page_overview)

    # Guard: show a friendly message if no data matches filters
    if filtered_df.empty and page not in ("✅ Data Quality",):
        st.info("ℹ️ No titles match the current filter selection. Try adjusting the filters in the sidebar.")
    else:
        page_handler(filtered_df)

    # Footer
    st.divider()
    st.caption(
        "🎬 Netflix Data Explorer — Built with Streamlit & Plotly | "
        f"Data: Netflix Movies and TV Shows ({len(df):,} titles)"
    )


if __name__ == "__main__":
    main()
