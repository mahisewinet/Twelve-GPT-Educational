import streamlit as st
from utils.page_components import add_common_page_elements
import pandas as pd
import plotly.express as px
from classes.vis import create_team_distribution_plot, create_reaction_distribution_plot

# Setup containers
sidebar_container = add_common_page_elements()
page_body = st.container()

# Categories and metrics
categories = {
    "Susceptibility to Counter-Attack": [
        "Area of the players behind the ball",
        "Average distance of these players from their centroid",
        "Vertical stretch",
        "Horizontal stretch",
        "No of defenders behind the ball",
        "Proximity to goal(distance)",
        "On-Ball threat",
        "Support threat",
        "Reaction speed"
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

def display_correlation_table(df, selected_metrics, category):
    """
    Display a correlation table for the selected metrics.
    Maps UI metric names to actual column names in the dataframe.
    """
    # Mapping from UI metric name to column name in the CSV
    if category == "Susceptibility to Counter-Attack":
        mapping = {
            "Area of the players behind the ball":"team_convex_hull_raw_zscore_x",
            "Average distance of these players from their centroid":"player_dist_from_centroid_zscore_x",
            "Vertical stretch":"team_stretch_y_zscore_x",
            "Horizontal stretch":"team_stretch_x_zscore_x",
            "No of defenders behind the ball":"team_defenders_behind_zscore_x",
            "On-Ball threat":"z_avg_onball_threat",
            "Reaction speed":"z_avg_reaction_speed",
            "Support threat": "z_avg_support_threat",
            "Proximity to goal(distance)": "z_avg_distance"
            # Add more if available
        }
    else:  # Reaction to Counter-Attack
        mapping = {
            "Reaction speed": "reaction_speed_start_zscore",
            "Area of the players behind the ball (start of dangerous event)": "team_convex_hull_raw_start_zscore",
            "Average distance of these players from their centroisd(start of dangerous event)": "player_dist_from_centroid_start_zscore",
            "Vertical stretch (start of dangerous event)": "team_stretch_y_start_zscore",
            "Horizontal stretch (start of dangerous event)": "team_stretch_x_start_zscore",
            "Area of the players behind the ball (end of dangerous event)": "team_convex_hull_raw_end_avg",
            "Average distance of these players from their centroid(end of dangerous event)": "team_convex_hull_raw_end_zscore",
            "Vertical stretch (end of dangerous event)": "team_stretch_y_end_zscore",
            "Horizontal stretch (end of dangerous event)": "team_stretch_x_end_zscore",
            "No of defenders behind the ball": "team_defenders_behind_start_avg"
        }

    # Collect actual column names for the selected metrics
    cols = []
    labels = []
    for metric in selected_metrics:
        if metric in mapping:
            cols.append(mapping[metric])
            labels.append(metric)
        else:
            st.warning(f"Metric '{metric}' is not available for correlation and will be skipped.")

    if len(cols) < 2:
        st.info("Select at least two valid metrics to see the correlation matrix.")
        return

    # Compute correlation matrix
    corr_df = df[cols].corr()

    # Rename columns and index to use friendly metric names
    corr_df.index = labels
    corr_df.columns = labels

    # Display as a styled table (heatmap effect)
    st.dataframe(
        corr_df.style.background_gradient(cmap='RdBu_r', axis=None, vmin=-1, vmax=1)
    )

with page_body:
    
    @st.cache_data
    def load_susceptibility_data():
        return pd.read_csv('data/joined_csv/Susceptibility_Quality.csv')
    
    @st.cache_data
    def load_reaction_data():
        return pd.read_csv('data/joined_csv/Reaction to counter attack.csv')

    # Load both dataframes
    df_sus = load_susceptibility_data()
    df_reac = load_reaction_data()

    # Team selection
    selected_team = st.selectbox("Select team", df_sus["team_shortname"].unique())

    # Category selection
    selected_category = st.selectbox("Select Quality", list(categories.keys()))

    # Metric multiselect
    selected_metrics = st.multiselect(
        "Select Metric",
        categories[selected_category]
    )

    st.write("Correlation Metrics")
    st.write("Set Metrics Weight")

    # Weight inputs
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

    #st.write("Selected Metrics with Weights:")
    #st.write(weights)

    # --- Correlation Table Section ---
    st.markdown("---")
    st.subheader("Correlation Metrics")
    if selected_metrics:
        # Choose the correct dataframe based on category
        if selected_category == "Susceptibility to Counter-Attack":
            df_corr = df_sus
        else:
            df_corr = df_reac
        display_correlation_table(df_corr, selected_metrics, selected_category)
    else:
        st.info("Select metrics to see their correlation matrix.")

    # --- Distribution Plot Section (always shown when a team is selected) ---
    if selected_team:
        if selected_category == "Susceptibility to Counter-Attack":
            plot = create_team_distribution_plot(selected_team, df_sus)
        else:
            plot = create_reaction_distribution_plot(selected_team, df_reac)
        
        # Optional: adjust plot height
        plot.fig.update_layout(height=800)
        plot.show()