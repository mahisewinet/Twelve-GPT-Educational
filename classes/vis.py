import streamlit as st
import pandas as pd
import numpy as np                     # used indirectly by DistributionPlot
from classes.visual import DistributionPlot   # your existing class
# format_metric is used inside DistributionPlot, so no direct import needed


def create_reaction_distribution_plot(selected_team: str, df: pd.DataFrame):
    """
    Generate a DistributionPlot for reaction metrics.
    Adjust column names to match your actual CSV.
    """
    df_plot = df.copy()

    # Define the metrics you want to plot.
    # Replace these with the actual metric names (base name, raw column, z column)
    base_names = ['reaction_speed', 'area_start', 'distance_start', 'vertical_stretch_start','horizontal_stretch_start']  # example
    raw_cols = ['reaction_speed_start_avg', 'team_convex_hull_raw_start_avg', 'player_dist_from_centroid_end_avg', 'team_stretch_y_end_avg','team_stretch_x_end_avg']
    z_cols = ['reaction_speed_start_zscore', 'team_convex_hull_raw_start_zscore', 'player_dist_from_centroid_start_zscore', 'team_stretch_y_start_zscore','team_stretch_x_start_zscore']

    # Create columns for DistributionPlot: base (raw) and base+'_Z' (z-score)
    for base, raw, z in zip(base_names, raw_cols, z_cols):
        df_plot[base] = df_plot[raw]          # raw values for annotation
        df_plot[base + '_Z'] = df_plot[z]     # z‑scores for x‑axis

    # Create the plot
    plot = DistributionPlot(
        columns=base_names,
        labels=['Worse', 'Average', 'Better'],
        pdf=False,
        plot_type='other'
    )

    plot.add_title(
        f'Reaction Comparison: {selected_team}',
        'Distribution of reaction metrics across all teams (z‑scores)'
    )

    # Add all teams as background
    plot.add_group_data(
        df_plot=df_plot,
        plots='_Z',
        names=df_plot['team_shortname'],
        legend='Other teams',
        hover='_Z',
        hover_string='z‑score: %{customdata:.2f}'
    )

    # Highlight the selected team
    team_row = df_plot[df_plot['team_shortname'] == selected_team].iloc[0]
    plot.add_data_point(
        ser_plot=team_row,
        plots='_Z',
        name=selected_team,
        hover='_Z',
        hover_string='z‑score: %{customdata:.2f}',
        text=selected_team
    )
  
    return plot

def create_team_distribution_plot(selected_team: str, df: pd.DataFrame):
    """
    Generate a DistributionPlot with all teams as background and the selected team highlighted.
    Uses z_avg_* columns for positioning and avg_* columns for annotation values.
    """
    # Work on a copy to avoid modifying the original
    df_plot = df.copy()

    # Define base names (used for column creation and annotations)
    #base_names = ['onball_threat', 'support_threat', 'reaction_speed', 'distance']
    base_names=["Area of the players behind the ball",
        "Average distance of these players from their centroid",
        "Vertical stretch",
        "Horizontal stretch",
        "No of defenders behind the ball",
        "Proximity to goal(distance)",
        "On-Ball threat",
        "Support threat",
        "Reaction Speed"]
    # Corresponding raw and z-score columns in the CSV
    raw_cols = ['team_convex_hull_raw_avg_x','player_dist_from_centroid_avg_x','team_stretch_y_avg_x','team_stretch_x_avg_x','team_defenders_behind_avg_x','avg_onball_threat', 'avg_support_threat', 'avg_reaction_speed', 'avg_distance']
    z_cols = ['team_convex_hull_raw_zscore_x','player_dist_from_centroid_zscore_y','team_stretch_y_zscore_y','team_stretch_x_zscore_x','team_defenders_behind_zscore_y','z_avg_onball_threat', 'z_avg_support_threat', 'z_avg_reaction_speed', 'z_avg_distance']

    # Create columns in the format expected by DistributionPlot:
    # - base column (e.g., 'onball_threat') holds the raw value for annotations
    # - base + '_Z' column (e.g., 'onball_threat_Z') holds the z‑score for the x‑axis
    for base, raw, z in zip(base_names, raw_cols, z_cols):
        df_plot[base] = df_plot[raw]          # raw values for annotations
        df_plot[base + '_Z'] = df_plot[z]     # z‑scores for positioning

    # Create the plot
    plot = DistributionPlot(
        columns=base_names,
        labels=['Worse', 'Average', 'Better'],
        pdf=False,
        plot_type='other'          # avoids "per 90" in annotations
    )

    # Add title and subtitle
    plot.add_title(
        f'Team Comparison: {selected_team}',
        'Distribution of key metrics across all teams (z‑scores)'
    )

    # Add all teams as the background group (light green dots)
    plot.add_group_data(
        df_plot=df_plot,
        plots='_Z',                 # use the '_Z' columns for x values
        names=df_plot['team_shortname'],
        legend='Other teams',
        hover='_Z',                  # show z‑score on hover
        hover_string='z‑score: %{customdata:.2f}'
    )

    # Extract the row for the selected team
    team_row = df_plot[df_plot['team_shortname'] == selected_team].iloc[0]

    # Add the selected team as a highlighted data point (white square)
    plot.add_data_point(
        ser_plot=team_row,
        plots='_Z',
        name=selected_team,
        hover='_Z',
        hover_string='z‑score: %{customdata:.2f}',
        text=selected_team
    )

    return plot