# Model Card for Defensive Transition Wordalisation

This wordalisation is implemented within the TwelveGPT Education framework (https://github.com/soccermatics/twelve-gpt-educational) and is intended as an illustration of how to apply the wordalisation method to team-level tactical analysis. It analyses how Premier League teams behave defensively when they lose possession in the attacking third of the pitch during the 2024/25 season.

## Intended use

The primary use case of this wordalisation is educational and analytical. It shows how to convert team-level tracking data metrics into a natural language tactical summary, which might be of interest to coaches, analysts, or football fans. A secondary use case is to help users understand how Premier League teams compare in their defensive transition behaviour when losing the ball high up the pitch.

Professional use (e.g., live match decision-making) is out of scope. Use of the chat for queries not relating to the data at hand is also out of scope.

## Factors

This wordalisation covers all 20 Premier League clubs competing in the 2024/25 season. Data is derived from SkillCorner tracking data and covers all matches played. All metrics are averaged across the full season to give a representative picture of each team's typical defensive transition behaviour.

## Datasets

The wordalisation uses two CSV files, each representing a different tactical quality:

### Quality 1: Susceptibility to Counterattack

Measures how structurally exposed a team is at the precise moment it loses possession in the attacking third. Metrics include:

| Metric | Description |
|---|---|
| total_losses | Total ball losses in the attacking third |
| cumulative_onball_threat | Total on-ball threat conceded across all losses |
| cumulative_support_threat | Total support threat conceded across all losses |
| defensive_coverage_area_at_loss_avg | Average convex hull area of the team at moment of loss |
| spread_at_loss_avg | Average distance of players from team centroid at loss |
| vertical_compactness_at_loss_avg | How stretched the team is front-to-back at loss |
| horizontal_compactness_at_loss_avg | How stretched the team is side-to-side at loss |
| number_of_defenders_behind_the_ball_at_loss_avg | Average number of defenders behind the ball at loss |
| attackers_distance_to_goal_avg | Average distance of attackers from their own goal at loss |
| avg_onball_threat | Average on-ball threat per possession loss |
| avg_support_threat | Average support threat per possession loss |

### Quality 2: Reaction to Counterattack

Measures how quickly and effectively the team responds during a dangerous counter-attack window (a 6-second window following a turnover that creates a dangerous situation). Metrics include:

| Metric | Description |
|---|---|
| total_losses | Total turnovers in the attacking third |
| dangerous_windows | Number of turnovers that became dangerous counter-attacks |
| dangerous_rate | Proportion of turnovers becoming dangerous (dangerous_windows / total_losses) |
| reaction_time | Average seconds until the team re-organises defensively |
| number_of_defenders_behind_the_ball_danger_start/_end | Defenders behind ball at start/end of danger window |
| spread_danger_start/_end | Team spread at start/end of danger window |
| defensive_coverage_area_danger_start/_end | Coverage area at start/end of danger window |
| horizontal_compactness_danger_start/_end | Horizontal stretch at start/end of danger window |
| vertical_compactness_danger_start/_end | Vertical stretch at start/end of danger window |

## Model

### Quantitative model

For each metric, a z-score is calculated by subtracting the mean and dividing by the standard deviation across all 20 Premier League teams. Teams are displayed in a distribution plot with the selected team highlighted. Teams further to the right of each metric bar performed better on that metric.

### Normative model

The model applies a directional norm to each metric. Most metrics in this dataset are negative — meaning a lower raw value is better:

Negative metrics (lower = better):
- All compactness and spread metrics (e.g. defensive_coverage_area_at_loss_avg) — a smaller, tighter shape is harder to counter
- total_losses, dangerous_windows, dangerous_rate — fewer dangerous situations = better
- reaction_time — faster reaction = lower time = better
- All threat metrics (cumulative_onball_threat, avg_onball_threat, etc.) — less threat conceded = better
- attackers_distance_to_goal_avg — attackers very far from their own goal cannot track back

Positive metrics (higher = better):
- number_of_defenders_behind_the_ball_at_loss_avg — more defensive cover = better
- number_of_defenders_behind_the_ball_danger_start/_end — more defenders = better

Z-scores for negative metrics are multiplied by -1 so that the distribution plot always shows the "best" teams to the right.

The z-scores are translated to evaluation words using:

def describe_level(value):
    thresholds = [1.5, 1, 0.5, -0.5, -1]
    words = ["outstanding", "excellent", "good", "average", "below average", "poor"]

### Language model

The wordalisation supports both GPT-4o and Gemini APIs. The language model is prompted with:
1. A system message establishing the persona of a tactical football analyst
2. Q&A pairs from data/describe/DefensiveTransition_QnA.xlsx defining each metric
3. Example summaries from data/gpt_examples/DefensiveTransition_Susceptibility_examples.xlsx or the Reaction equivalent
4. The synthesized text generated from the team's z-scores

## Ethical considerations

This wordalisation analyses team-level tactical data only. No individual player data is used. The metrics are derived from positional tracking data and describe collective team behaviour, not any individual's performance. The data is used solely for educational and analytical purposes.

Clubs may have tactical contexts (injuries, fixture congestion, opponent quality) not captured in season averages. Users should consider these factors when interpreting summaries.

## Caveats and recommendations

- Data covers the 2024/25 Premier League season only. Conclusions should not be generalised across seasons.
- Match counts may vary slightly between teams due to data availability.
- Teams with extreme tactical profiles (e.g. very high-press or very defensive) may produce z-scores that appear striking but reflect a deliberate style rather than a weakness.
- The LLM may incorporate prior knowledge about clubs beyond what is in the provided data. Summaries should be treated as data-grounded insights, not definitive assessments.
