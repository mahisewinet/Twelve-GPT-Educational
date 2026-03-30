"""
Defensive Transition page.
Analyses how Premier League teams behave when they lose possession in the
attacking third — their susceptibility to counter-attacks and how quickly
they react.

Runs top to bottom every time the user interacts with the app.
"""

import streamlit as st

from classes.data_source import TeamStats
from classes.data_point import Team
from classes.visual import DistributionPlotTeam
from classes.description import TeamDescription
from classes.chat import TeamChat

from utils.page_components import add_common_page_elements
from utils.utils import select_team, create_chat

# ── Page setup ──────────────────────────────────────────────────────────────
sidebar_container = add_common_page_elements()
page_container = st.sidebar.container()
sidebar_container = st.sidebar.container()

st.divider()

# ── Quality selector (must come first — controls which CSV is loaded) ────────
selected_quality = sidebar_container.selectbox(
    "Select Quality",
    [
        TeamStats.QUALITY_SUSCEPTIBILITY,
        TeamStats.QUALITY_REACTION,
    ],
)

# ── Load data and compute z-scores + ranks at runtime ───────────────────────
teams = TeamStats(quality=selected_quality)
teams.calculate_statistics(
    metrics=teams._metrics,
    negative_metrics=teams._negative_metrics,
)

# ── Team selector ────────────────────────────────────────────────────────────
team = select_team(sidebar_container, teams)

# ── Expander 1: Model card ───────────────────────────────────────────────────
with open("model cards/model-card-defensive-transition.md", "r", encoding="utf8") as f:
    model_card_text = f.read()
st.expander("Model card for Defensive Transition", expanded=False).markdown(
    model_card_text
)

# ── Expander 2: Dataframe (includes raw values + z-scores + ranks) ───────────
st.expander("Dataframe used", expanded=False).write(teams.df)

# ── Chat state hash — resets when quality OR team changes ───────────────────
to_hash = (team.id, selected_quality, "defensive_transition")
chat = create_chat(to_hash, TeamChat, team, teams)

# ── Initial content — only generated once when chat is new ──────────────────
if chat.state == "empty":
    chat.messages_to_display.clear()  # prevent accumulating duplicates on retries

    # Distribution plot
    # metrics[::-1] reverses order because the plot renders bottom-to-top
    visual = DistributionPlotTeam(teams._metrics[::-1])
    visual.add_title_from_team(team)
    visual.add_teams(teams)          # all 20 teams (background)
    visual.add_team(team, len(teams.df))  # focal team (highlighted)

    # AI summary — Chat Transcript expander appears automatically inside stream_gpt()
    description = TeamDescription(team, quality=selected_quality)
    summary = description.stream_gpt(stream=True)

    # Add initial prompt + visual + summary to the chat display
    chat.add_message(
        "Please can you summarise " + team.name + " for me?",
        role="user",
        user_only=False,
        visible=False,
    )
    chat.add_message(visual)
    chat.add_message(summary)

    chat.state = "default"  # prevents regeneration on subsequent reruns

# ── Display messages and persist state ──────────────────────────────────────
# Note: chat.get_input() is intentionally omitted — no chat box on this page
chat.display_messages()
chat.save_state()
