import streamlit as st
import pandas as pd
from classes.visual import DistributionPlot   # your existing class

@st.cache_data
def load_reaction_data():
    """Load the reaction to counter attack data."""
    return pd.read_csv('Reaction to counter attack.csv')

def create_reaction_distribution_plot(selected_team: str, df: pd.DataFrame):
    """
    Generate a DistributionPlot for the reaction metrics.
    The selected team is highlighted in white.
    """
    # List of z‑score columns to plot (exactly as in the CSV)
    z_columns = [
        'team_convex_hull_raw_start_zscore',
        'team_convex_hull_raw_end_zscore',
        'team_stretch_x_start_zscore',
        'team_stretch_x_end_zscore',
        'team_stretch_y_start_zscore',
        'team_stretch_y_end_zscore',
        'reaction_speed_start_zscore',
        'reaction_speed_end_zscore'
    ]

    # Create a copy to avoid modifying the original
    df_plot = df.copy()

    # We will use the original column names as base names.
    # Since they already contain the z‑score values, we set plots='' (no suffix).
    plot = DistributionPlot(
        columns=z_columns,                     # these are the base column names
        labels=['Worse', 'Average', 'Better'], # x‑axis labels
        pdf=False,
        plot_type='other'                       # shows raw values in annotations
    )

    # Add title and subtitle
    plot.add_title(
        f'Reaction to Counter Attack: {selected_team}',
        'Distribution of z‑scores across all teams'
    )

    # Add all teams as the background group
    plot.add_group_data(
        df_plot=df_plot,
        plots='',                                # no suffix – use the column as is
        names=df_plot['Team'],
        legend='Other teams',
        hover='',                                 # show the same value on hover
        hover_string='z‑score: %{customdata:.2f}'
    )

    # Extract the row for the selected team
    team_row = df_plot[df_plot['Team'] == selected_team].iloc[0]

    # Add the selected team as a highlighted data point
    plot.add_data_point(
        ser_plot=team_row,
        plots='',
        name=selected_team,
        hover='',
        hover_string='z‑score: %{customdata:.2f}',
        text=selected_team
    )

    return plot