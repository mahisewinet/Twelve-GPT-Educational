import streamlit as st
from utils.page_components import add_common_page_elements
import pandas as pd
import numpy as np

# Setup containers
sidebar_container = add_common_page_elements()
page_body = st.container()

# --- Load team list and full data ---
TEAM_CSV_PATH = "data/joined_csv/Arsenal_Defensive_Transitions_with_metrics.csv"

@st.cache_data
def load_full_data(path):
    """Load the full CSV once and cache it."""
    return pd.read_csv(path)

@st.cache_data
def get_team_list(df):
    """Extract unique team names from event_team column."""
    return sorted(df['event_team'].dropna().unique())

# Load full data
full_df = load_full_data(TEAM_CSV_PATH)
team_names = get_team_list(full_df)

# --- Sidebar: Team selection ---
with sidebar_container:
    st.subheader("Team Selection")
    if team_names:
        selected_team = st.selectbox("Choose a team", team_names)
    else:
        selected_team = None
        st.warning("No teams available")

# Filter data for selected team
if selected_team is not None:
    team_data = full_df[full_df['event_team'] == selected_team].copy()
else:
    team_data = pd.DataFrame()

# --- Categories and metrics (your original list) ---
categories = {
    "Susceptibility to Counter-Attack": [
        "Area of the players behind the ball",
        "Average distance of these players from their centroid",
        "vertical stretch",
        "horizontal stretch",
        "No of defenders behind the ball",
        "Proximity to goal(distance)",
        "On-Ball threat",
        "Support threat",
    ],
    "Reaction to Counter-Attack": [
        "Reaction speed",
        "Area of the players behind the ball (start of dangerous event)",
        "Average distance of these players from their centroid(start of dangerous event)",
        "Vertical stretch (start of dangerous event)",
        "Horizontal stretch (start of dangerous event)",
        "Area of the players behind the ball (end of dangerous event)",
        "Average distance of these players from their centroid(end of dangerous event)",
        "Vertical stretch (end of dangerous event)",
        "Horizontal stretch (end of dangerous event)",
        "No of defenders behind the ball"
    ]
}

# --- Mapping from display names to actual column names in your CSV ---
# 🔧 ADJUST THESE TO MATCH YOUR CSV'S EXACT COLUMN NAMES
column_map = {
    "Area of the players behind the ball": "area",
    "Average distance of these players from their centroid": "avg_dist_centroid",
    "vertical stretch": "stretch_x",
    "horizontal stretch": "stretch_y",
    "No of defenders behind the ball": "num_behind_ball",
    "Proximity to goal(distance)": "proximity_to_goal",          # example – change as needed
    "On-Ball threat": "on_ball_threat",                          # example
    "Support threat": "support_threat",                          # example
    "Reaction speed": "reaction_speed",                          # example
    "Area of the players behind the ball (start of dangerous event)": "area_start",
    "Average distance of these players from their centroid(start of dangerous event)": "avg_dist_centroid_start",
    "Vertical stretch (start of dangerous event)": "stretch_x_start",
    "Horizontal stretch (start of dangerous event)": "stretch_y_start",
    "Area of the players behind the ball (end of dangerous event)": "area_end",
    "Average distance of these players from their centroid(end of dangerous event)": "avg_dist_centroid_end",
    "Vertical stretch (end of dangerous event)": "stretch_x_end",
    "Horizontal stretch (end of dangerous event)": "stretch_y_end",
}

with page_body:
    selected_category = st.selectbox("Select Quality", list(categories.keys()))
    selected_metrics = st.multiselect("Select Metric", categories[selected_category])

    # --- Correlation section (moved above weights per your layout) ---
    st.write("Correlation Metrics")
    if not team_data.empty and len(selected_metrics) >= 2:
        # Get actual column names that exist in team_data
        available_cols = []
        for display_name in selected_metrics:
            col = column_map.get(display_name)
            if col is not None and col in team_data.columns:
                available_cols.append(col)
            else:
                st.warning(f"Column for '{display_name}' not found in data. Check column_map.")
        
        if len(available_cols) >= 2:
            corr_matrix = team_data[available_cols].corr()
            # Display as a styled DataFrame
            st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm').format("{:.2f}"))
            # Optional: display as a heatmap (uncomment if you want)
            # import plotly.express as px
            # fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
            # st.plotly_chart(fig)
        else:
            st.info("Not enough valid metrics available for correlation.")
    elif team_data.empty:
        st.info("No data for the selected team.")
    else:
        st.info("Select at least two metrics to see correlation.")

    # --- Weight inputs (unchanged) ---
    st.write("Set Metrics Weight")
    weights = {}
    if selected_metrics:
        for i in range(0, len(selected_metrics), 2):
            cols = st.columns(2)
            weights[selected_metrics[i]] = cols[0].number_input(
                label=f"Weight for '{selected_metrics[i]}'",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.01,
                format="%.2f"
            )
            if i + 1 < len(selected_metrics):
                weights[selected_metrics[i + 1]] = cols[1].number_input(
                    label=f"Weight for '{selected_metrics[i + 1]}'",
                    min_value=0.0,
                    max_value=1.0,
                    value=1.0,
                    step=0.01,
                    format="%.2f"
                )

    st.write("Selected Metrics with Weights:")
    st.write(weights)