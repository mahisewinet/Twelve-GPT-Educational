from abc import ABC, abstractmethod
from typing import List, Union, Dict
import pandas as pd
from classes.description import Description   # assuming Description is in classes/description.py

class TeamDefenseDescription(Description):
    @property
    def gpt_examples_path(self):
        # Path to Excel with examples of final descriptions
        return f"{self.gpt_examples_base}/TeamDefense_examples.xlsx"

    @property
    def describe_paths(self):
        # Path to Excel with Q&A about defensive metrics
        return [f"{self.describe_base}/TeamDefense_QnA.xlsx"]

    def __init__(self, team_name: str, metrics: Dict[str, float]):
        """
        team_name: name of the team
        metrics: dictionary with keys like 'convex_hull_area', 'avg_dist_centroid', etc.
        """
        self.team_name = team_name
        self.metrics = metrics
        super().__init__()

    def get_intro_messages(self) -> List[Dict[str, str]]:
        intro = [
            {
                "role": "system",
                "content": (
                    "You are a Performance Analysts specialising in defensive structure and organisation. "
                    "You provide succinct, data‑driven descriptions of a team's defensive shape, compactness, and threat levels."
                ),
            },
            {
                "role": "user",
                "content": "What do you mean by 'defensive structure'?",
            },
            {
                "role": "assistant",
                "content": (
                    "I'm referring to the spatial organisation of players behind the ball – how compact the shape is, "
                    "how stretched vertically or horizontally, and the number of defenders actually behind the ball."
                ),
            },
        ]
        # If we have describe_paths, we add a few extra Q&A
        if len(self.describe_paths) > 0:
            intro += [
                {
                    "role": "user",
                    "content": "First, could you answer some questions about defensive metrics for me?",
                },
                {"role": "assistant", "content": "Sure!"},
            ]
        return intro

    def synthesize_text(self) -> str:
        """
        Convert the metrics into a statistical description.
        """
        lines = []
        lines.append(f"Here is a statistical description of {self.team_name}'s defensive structure.\n")

        # Map the metric names to readable descriptions
        metric_labels = {
            'convex_hull_area': 'area of the convex hull formed by players behind the ball',
            'avg_dist_centroid': 'average distance from the centroid of the defensive group',
            'length_stretch': 'vertical stretch (distance between deepest defender and highest attacker)',
            'width_stretch': 'horizontal stretch (width of the defensive shape)',
            'num_defenders_behind_ball': 'number of defenders positioned behind the ball',
            'distance_from_goal': 'distance of the player with the ball from the opponent’s goal',
            'on_ball_threat': 'on‑ball threat',
            'support_threat': 'support threat',
        }

        for key, value in self.metrics.items():
            if key in metric_labels:
                lines.append(f"- {metric_labels[key]}: {value:.2f} (units depend on metric).")
            else:
                lines.append(f"- {key}: {value:.2f}.")

        # Optionally add comparisons to league averages if you have them
        # lines.append(f"Compared to other teams, ...")

        return "\n".join(lines)

    def get_prompt_messages(self) -> List[Dict[str, str]]:
        prompt = (
            f"Please use the statistical description enclosed with ``` to write a concise, 4‑sentence summary of the team's defensive structure. "
            "The first sentence should give an overview of the overall defensive shape (compactness, stretch). "
            "The second sentence should focus on the number of defenders behind the ball and how far the ball carrier is from goal. "
            "The third sentence should comment on the on‑ball and support threat levels. "
            "The final sentence should summarise the team's defensive strengths or weaknesses based on these numbers."
        )
        return [{"role": "user", "content": prompt}]