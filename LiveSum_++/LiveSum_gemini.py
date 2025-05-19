import pandas as pd
import json
import re
import os # Import os module for checking file existence

# --- Google AI SDK specific imports ---
import google.generativeai as genai
# Import types for configuration if needed (often auto-imported or part of genai)
# from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold (will confirm exact path)

# --- Configuration ---
NUM_SAMPLES_TO_PROCESS = 5 # Number of samples to process
INPUT_JSON_FILE = 'train.json'
# Changed output directory to reflect the SDK change
OUTPUT_DIR = 'player_stats_output_gemini_1' # Directory to save CSV files

# --- Google AI SDK Configuration ---
# TODO: IMPORTANT! Replace with your Google AI API Key from Google AI Studio
# You can get an API key from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY = "AIzaSyCOhbBdHk70FJJhU5c6xfBw-q4RJgyBlAY" # <--- REPLACE THIS
MODEL_NAME = "geminigemini-2.5-flash-preview-04-17" # Using "-latest" is often good practice
                                      # Alternatives: "gemini-1.5-flash", "gemini-1.5-pro-latest", "gemini-1.5-pro"

# --- Initialize Google AI SDK ---
try:
    if GOOGLE_API_KEY == "YOUR_GOOGLE_AI_API_KEY":
        raise ValueError("Please replace 'YOUR_GOOGLE_AI_API_KEY' with your actual API key.")
    genai.configure(api_key=GOOGLE_API_KEY)
    # Instantiate the model
    gemini_model = genai.GenerativeModel(MODEL_NAME)
    # Test with a simple call if desired (optional)
    # gemini_model.generate_content("test", generation_config=genai.types.GenerationConfig(candidate_count=1))
    print(f"Google AI SDK initialized successfully. Using model: {MODEL_NAME}")
except ValueError as ve:
    print(f"Configuration Error: {ve}")
    exit()
except Exception as e:
    print(f"Error initializing Google AI SDK: {e}")
    print("Please ensure your API key is correct and valid.")
    exit()

# --- Ensure output directory exists ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")

# --- Helper Functions --- (These remain largely the same)

def format_commentary(commentary_text):
    return commentary_text.replace('. ', '.\n')

def extract_all_events_from_commentary(commentary):
    pattern = r"(Player\d+)\s*\((Home Team|Away Team)\)(.*?)(?:\.|\n|$)"
    matches = re.finditer(pattern, commentary, re.IGNORECASE)
    events_by_player = {'Home Team': {}, 'Away Team': {}}
    all_players = {'Home Team': set(), 'Away Team': set()}
    for match in matches:
        player, team, event_text_suffix = match.groups()
        event_text = match.group(0).strip()
        team_key = "Home Team" if "home" in team.lower() else "Away Team"
        all_players[team_key].add(player)
        events_by_player[team_key].setdefault(player, []).append(event_text)
    return events_by_player, all_players

def generate_prompt_for_player(player_name, statements):
    input_statements = "\n".join(
        f"- {s}" for s in statements if pd.notna(s) and s
    )
    if not input_statements:
        input_statements = "No specific events recorded for this player."

    return f"""You are an expert sports analyst specializing in soccer commentary and game event tracking. Your task is to meticulously process inputs related to a soccer match.
You are also an expert data extraction and structuring engine. Your sole task is to rigorously parse text to identify specific information and present it accurately as a markdown table.

You will compile statistics for the specific players, adhering strictly to the definitions and formatting rules provided.

---
**Objective:** Analyze commentary snippets for a specific player and count explicit occurrences of defined events for that player.

**Input:**
* **Player Name:** The name of the single player to track.
    <PLAYER_NAME>
    {player_name}
    </PLAYER_NAME>

* **Commentary Snippets:** A list of commentary text snippets potentially mentioning the player.
    <PLAYER_COMMENTARY_SNIPPETS>
    {input_statements}
    </PLAYER_COMMENTARY_SNIPPETS>

## Instructions (Part 2 - Finalized for Strictness):

1.  Identify the target player name from `<PLAYER_NAME>`.
2.  Initialize counts for the following player-specific events to 0: Shots, Goals, Assists, Free Kicks (taken), Fouls (committed), Yellow Cards, Red Cards, Offsides.
3.  Analyze each snippet within `<PLAYER_COMMENTARY_SNIPPETS>`.
4.  **Absolute Strict Counting & Unambiguous Attribution:**
    * Events are counted **ONLY** if they are **EXPLICITLY** stated and **UNAMBIGUOUSLY ATTRIBUTED** to the player named in `<PLAYER_NAME>` within the snippet.
    * **NEVER** infer, guess, or hallucinate events. If the snippet does not *clearly* state the target player performed the action, do not count it.
    * If the snippet mentions an action performed by a *different* player, or if the actor is *unclear* or *implied* but not explicitly the target player, **DO NOT COUNT** that action for the target player.
5.  Increment counts based on the following event definitions and keywords when attributed to the target player. Apply the **Absolute Strict Counting & Unambiguous Attribution** rule (Point 4) to every potential increment.
    * **Important Note on Combined Events:** If a single snippet describes multiple distinct events attributed to the player (e.g., committing a foul *and* receiving a yellow card for it), increment the count for *each* explicitly mentioned event.
    * **Free Kicks (Taken):** Player is mentioned as taking or attempting a free kick or penalty kick, **OR** the player is explicitly mentioned as being fouled or winning a free kick/penalty as a result of an opponent's action. **Crucially: Any explicit mention of the player taking a penalty kick or scoring from the penalty spot COUNTS as a Free Kick (Taken). **Keywords: `[free kick, penalty, takes the kick, takes the penalty, fouled by, wins a free kick, wins a penalty, brought down by, tripped by, earns a free kick]`
    * **Free Kicks:** If the Player is mentioned conceding a free kick or penalty, that does not count as a free kick but rather counts as a foul.
    * **Fouls (Committed):** Count only when the commentary explicitly states the target player committed a foul or an action considered a foul. This includes, but is not limited to: dangerous play, rough tackles, reckless challenges, handling the ball (as the offender), or actions leading to disciplinary cards for aggression/misconduct like getting into a fight or confrontation. **ENSURE** the target player is the clear actor. Keywords: `[foul, dangerous play, penalty (if context explicitly implies committed by the player), rough tackle, reckless challenge, hand ball (committed), handling (committed), challenges (when describing a committed foul), fight (committed by the player), confrontation (initiated/committed by the player)]`
    * **Yellow Cards:** Player is explicitly mentioned receiving a yellow card. Keywords: `[yellow card, booked, caution]`
    * **Red Cards:** Player is explicitly mentioned receiving a red card. Keywords: `[red card, second yellow card, sent off]`
    * **Shots:** Player is explicitly mentioned taking any attempt on goal (on or off target, saved, blocked, hitting woodwork, scoring). Keywords: `[hits the bar, shot, saved, missed, header (ONLY if explicitly an attempt on goal by the target player), goes high, goal, blocked, post, attempt]`
    * **Goals:** Player is explicitly mentioned scoring a goal. Keywords: `[goal, scores]`. **Note:** Scoring a goal counts as *both* a 'Goal' and a 'Shot'.
    * **Assists:** Count an assist **ONLY** when the commentary explicitly states the target player provided a pass or action that **directly led** to a goal. **The target player must be the one *giving* the assist, never the receiver.** Keywords: `[assist (provided by target player), assisted by (when this phrase clearly links the assist *to* the target player), assistance (provided by the target player), sets up (a goal for another player), pass leads to goal (from the target player)]` **Absolutely NO assist is counted for the target player if the snippet indicates they were *assisted by* someone else.** Example: If the snippet is "Goal scored by Player4, assisted by Player7" and your target is Player4, this counts as a Goal (and Shot) for Player4, but **ZERO assists** for Player4. If Player7 is the target, it counts 1 assist for Player7.
    * **Offsides:** Player is explicitly mentioned being in an offside position. Keywords: `[offside]`
    * **Yellow Cards:** If a reason is mentioned for the yellow card being provided, that reason should add a count to the fouls committed by the player. Example: "Player4 received a yellow card for a foul" counts as 1 yellow card and 1 foul for Player4.
    * **Yellow Cards:** If a player receives a yellow card, but no reason is mentioned, then it should be counted as a yellow card only. Example: "Player4 received a yellow card" counts as 1 yellow card for Player4.
    * **Red Cards:** If a reason is mentioned for the red card being provided, that reason should add a count to the fouls committed by the player. Example: "Player4 received a red card for a foul" counts as 1 red card and 1 foul for Player4.
    * **Follow these statements exactly** as they are provided. Do not add any additional context or information. Your task is to extract and count the events strictly based on the provided definitions and keywords.
    *"Player11(Home Team)'s right-footed shot from outside the box into the bottom left corner." (Count: 1 shot)
    *"Player4(Home Team)'s left-footed shot from outside the box into the top right corner, assisted by Player9(Home Team)." (Count: 1 shot)
    *"Player29's header wide of the target." (Count: 1 shot)
    *"Player4(Home Team) scored a goal." (Count: 1 goal, 1 shot)
    *"Player4(Home Team)'s header into the top left corner, assisted by Player9(Home Team) with a cross after a corner kick." (Count: 1 shot)
    *"Player4(Home Team) with a cross off a set piece, The score now stands at Home Team 2, Away Team 0." (Count: 1 assist)
    *"Player10(Home Team)'s right-footed shot from outside the box into the bottom right corner, assisted by Player14(Home Team)." (Count: 1 shot)
    *"Player11(Home Team), and Player9(Home Team)'s header from the center is saved in the goal."--> If the target player is Player11, count as nothing. If the target player is Player9, count as 1 shot.
    *"Player20(Away Team) outside the box, finding the bottom left corner." (Count: 1 shot)
    **APPLY YOUR JUDGEMENT FOR STATEMENTS LIKE THESE. DO NOT HALLUCINATE ANY EVENT OR STATISTIC THAT IS NOT EXPLICITLY PRESENT IN THE STATEMENT. IF A STATEMENT BEGINS WITH "PlayerX takes a shot..." AND THE PLAYER IS NOT THE TARGET PLAYER, DO NOT COUNT A GOAL. COUNT ONLY A SHOT.**
    **"Do not infer a goal has been scored simply because the shot's destination is described (e.g., 'into the net'). Only the explicit mention of the word 'goal' or phrases like 'scores' should indicate a goal."**
    **Offsides:** If a statement mentions two players, one of whom is the target player, and the other is not, do not count an offside **UNLESS THE TARGET PLAYER IS STATED AS THE PLAYER IN AN OFFSIDE POSITION**. Example: "Player20(Away Team) attempts a through ball, but Player27(Away Team) is offside for the Away Team." should not be counted as an offside for Player20. However, "Player20(Away Team) is offside" should be counted as an offside for Player20.
    **Shots:** If a statement mentions that a shot is from a free kick or penalty, then it should be counted for the player as both a *shot* and a *free kick*. Example: "Player2(Home Team)'s attempt on goal is blocked after a free kick in the attacking half, with the shot coming from the right side of the six-yard box and assisted by Player11(Home Team)'s cross." should be counted as 1 shot and 1 free kick for Player2.
    **Free Kicks:** If a statement is similar to this: "Player26(Away Team) fouls Player11(Home Team), earning a free kick in the attacking half." and the target player is Player26, then this should be counted as 1 foul and *NOTHING ELSE*.
    **Free Kicks:** If a statement is similar to this: "Player28(Away Team) is fouled in the box." and the target player is Player28, then this should be counted as *NOTHING*. **APPLY THIS LOGIC TO ALL STATEMENTS OF THIS FORM.** another example: "Player9(Home Team) is fouled in the box."
    **Free Kicks:** If a statement is similar to this: "Player34(Away Team) fouls Player4(Home Team) and wins a free kick in their own defensive half." and the target player is Player34, then this should be counted as 1 foul and *NOTHING ELSE*.
    *"Player26(Away Team) has been fouled by Player35(Away Team) with a handball." (Count: NO EVENTS, 0)

**Output (Part 2):**
* **Reasoning:** First, provide your detailed reasoning for the player statistics. For each snippet where an event was counted for the target player, explain which event was identified and why. Follow this structure:
    * Analyzing the snippets for <PLAYER_NAME>:
    * - "Snippet X text excerpt..." -> Counts as 1 [Event Type] because [reason based on keywords/context].
    * - ... (continue for all relevant snippets) ...
    *CHECK YOUR CALCULATIONS TO MAKE SURE YOU ARE TABULATING CORRECTLY. THE FINAL TABLE COUNTS MUST MATCH YOUR REASONING. DO NOT HALLUCINATE ANY STATISTICS. IF A STATISTIC IS NOT EXPLICITLY MENTIONED IN THE COMMENTARY, DO NOT COUNT IT.**
    *Example:
    Analyzing the snippets for Player26:

    - "Player26(Away Team) earns a free kick in their own half." -> Counts as 1 Free Kick because the snippet explicitly states Player26 earned a free kick.
    - "Player26(Away Team) committed a foul." -> Counts as 1 Foul because the snippet explicitly states Player26 committed a foul.
    - "Player26(Away Team) receives a yellow card for a rough tackle." -> Counts as 1 Yellow Card and 1 Foul because the snippet explicitly states Player26 received a yellow card for a rough tackle, which is a foul.
    - "Player26(Away Team) commits a foul." -> Counts as 1 Foul because the snippet explicitly states Player26 committed a foul.
    - "Player26(Away Team) receives his second yellow card for a reckless foul." -> Counts as 1 Yellow Card, 1 Foul, and 1 Red Card because the snippet explicitly states Player26 received a second yellow card for a reckless foul, which results in a red card.

    Final Summary Table:
    ```markdown
    | Player   | Shots | Goals | Assists | Free Kicks | Fouls | Yellow Cards | Red Cards | Offsides |
    |----------|-------|-------|---------|------------|-------|--------------|-----------|----------|
    | Player26 | 0     | 0     | 0       | 1          | 4     | 2            | 1         | 0        |
    ```
    *
    *Example:
        Analyzing the snippets for Player10:
    - "Player10(Home Team) commits a foul." -> Counts as 1 Foul because the snippet explicitly states Player10 committed a foul.
    - "Player10(Home Team) commits a foul, resulting in Player21(Away Team) winning a free kick in their own defensive half, The foul by Player10(Home Team) awards Player21(Away Team) a free kick in their defensive half." -> Counts as 1 Foul because the snippet explicitly states Player10 committed a foul.
    - "Player10(Home Team) commits a foul." -> Counts as 1 Foul because the snippet explicitly states Player10 committed a foul.
    - "Player10(Home Team) earns a free kick in the opponent's half." -> Counts as 1 Free Kick because the snippet explicitly states Player10 earned a free kick.
    - "Player10(Home Team) commits a foul." -> Counts as 1 Foul because the snippet explicitly states Player10 committed a foul.
    - "Player10(Home Team) is currently delayed in the match due to an injury." -> No countable event because the snippet does not mention any of the defined events.
    - "Player10(Home Team) receives a yellow card for a harsh tackle." -> Counts as 1 Yellow Card and 1 Foul because the snippet explicitly states Player10 received a yellow card for a harsh tackle.
    - "Player10(Home Team) is being held up due to an injury." -> No countable event because the snippet does not mention any of the defined events.

    Final Summary Table:
    ```markdown
    | Player   | Shots | Goals | Assists | Free Kicks | Fouls | Yellow Cards | Red Cards | Offsides |
    |----------|-------|-------|---------|------------|-------|--------------|-----------|----------|
    | Player10 | 0     | 0     | 0       | 1          | 5     | 1            | 0         | 0        |
    ```*
* **Final Summary Table:** After the reasoning, provide the final summary table for the target player's statistics.
* **Formatting:**
    * Add the heading `Final Summary Table:` before the markdown table.
    * Start the markdown table strictly with ```markdown
    * Create the header row: `| Player | Shots | Goals | Assists | Free Kicks | Fouls | Yellow Cards | Red Cards| Offsides |`
    * Create the data row for the target player, filling in the final counts: `| <PLAYER_NAME> | [Total Shots] | [Total Goals] | [Total Assists] | [Total Free Kicks] | [Total Fouls] | [Total Yellow Cards] | [Total Red Cards] | [Total Offsides] |`
    * End the markdown table strictly with ```

---

**Overall Execution:**

1.  Process all snippets in `<PLAYER_COMMENTARY_SNIPPETS>` completely to determine final player stats and generate reasoning.
2.  Present the outputs in the following strict order:
    a.  Reasoning for player statistics (formatted as specified)
    b.  `Final Summary Table:` (heading)
    c.  Player statistics markdown table (formatted strictly within ```markdown and ```)
Adhere precisely to all formatting rules, headings, and markdown block requirements. Do not include any extra text or commentary outside of the specified outputs.
"""

def save_output_to_file(output_text, player_name, sample_number, output_dir_param=OUTPUT_DIR):
    os.makedirs(output_dir_param, exist_ok=True)
    filename = f"sample_{sample_number+1}_{player_name.replace(' ', '_')}.txt"
    file_path = os.path.join(output_dir_param, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text.strip())

def get_model_response(prompt, player_name, sample_number):
    try:
        # --- Generation Configuration for google.generativeai ---
        # Ensure genai.types is accessible or import GenerationConfig directly
        generation_config = genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=2000,
            # candidate_count=1 # Default is 1, explicitly setting if needed
        )

        # --- Safety Settings for google.generativeai ---
        # Ensure genai.types is accessible or import HarmCategory, HarmBlockThreshold
        safety_settings = [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        ]

        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        content = response.text.strip()
        save_output_to_file(content, player_name, sample_number)
        return content
    except Exception as e:
        print(f"Error calling Google AI API for player {player_name}: {e}")
        # More detailed error for google.generativeai if available
        if hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        if response and not response.candidates: 
            print("No candidates returned in the response.")