import pandas as pd
import json
import re
from openai import OpenAI
from io import StringIO
import os # Import os module for checking file existence

### SECRET KEY (OPENAI) - Make sure to replace with your actual key or use environment variables
# It's recommended to use environment variables for API keys
# For example: client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# Ensure you have set the OPENAI_API_KEY environment variable if you use this method.
try:
    client = OpenAI(
    api_key="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"
    )
    # Test connection (optional but recommended)
    client.models.list() 
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please ensure your API key is correct and valid.")
    exit() # Exit if the client can't be initialized


# --- Configuration ---
NUM_SAMPLES_TO_PROCESS = 50 # Number of samples to process
INPUT_JSON_FILE = 'train.json'
OUTPUT_DIR = 'player_stats_output_GPT4o_updated_5' # Directory to save CSV files

# --- Ensure output directory exists ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")

# --- Helper Functions ---

# Function to make commentary more readable (optional, applied per sample)
def format_commentary(commentary_text):
    return commentary_text.replace('. ', '.\n')

# Function to extract all player events from a single commentary
def extract_all_events_from_commentary(commentary):
    # Regex to match any sentence with a PlayerX (Team) pattern, capturing player, team, and sentence
    pattern = r"(Player\d+)\s*\((Home Team|Away Team)\)(.*?)(?:\.|\n|$)"
    matches = re.finditer(pattern, commentary, re.IGNORECASE) # Added ignorecase just in case

    events_by_player = {'Home Team': {}, 'Away Team': {}}
    all_players = {'Home Team': set(), 'Away Team': set()}

    for match in matches:
        player = match.group(1)
        team = match.group(2)
        # Reconstruct the full sentence/event text including the player/team identifier
        event_text = match.group(0).strip() 

        # Normalize team name if needed (e.g., ensure consistent casing)
        if "home" in team.lower():
            team_key = "Home Team"
        elif "away" in team.lower():
            team_key = "Away Team"
        else:
            continue # Skip if team is not clearly home or away

        all_players[team_key].add(player)

        if player not in events_by_player[team_key]:
            events_by_player[team_key][player] = []
        events_by_player[team_key][player].append(event_text)

    return events_by_player, all_players

# Function to generate the prompt for the OpenAI API
def generate_prompt_for_player(player_name, statements):
    input_statements = "\n".join(
        f"- {s}" for s in statements if pd.notna(s) and s
    )

    if not input_statements:
        input_statements = "No specific events recorded for this player."

    return f"""
You are an expert sports analyst specializing in soccer commentary and game event tracking. Your task is to meticulously process inputs related to a soccer match:

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
    {statements}
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

def save_output_to_file(output_text, player_name, sample_number, output_dir="gpt_outputs_update_9"):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a unique filename for each sample
    filename = f"sample_{sample_number+1}_{player_name.replace(' ', '_')}.txt"
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text.strip())

def get_model_response(prompt, player_name, sample_number):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert data extraction and structuring engine. Your sole task is to rigorously parse text to identify specific information and present it accurately as a markdown table."""
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2000,
            temperature=0.0,
        )
        
        content = response.choices[0].message.content.strip()
        save_output_to_file(content, player_name, sample_number)  # Save to file
        return content
    except Exception as e:
        print(f"Error calling OpenAI API for player {player_name}: {e}")
        return None
# Function to parse the markdown table from the response
def parse_table_to_df(table_str, player_name):
    if not table_str or "Player" not in table_str:
        print(f"❌ Parsing Error: Response for {player_name} doesn't look like a markdown table with 'Player' column.")
        print(f"Raw response:\n---\n{table_str}\n---")
        return pd.DataFrame()

    try:
        # Remove markdown code block wrappers (```markdown ... ```)
        table_str = re.sub(r"^```(?:markdown)?\s*|```$", "", table_str.strip(), flags=re.MULTILINE).strip()

        lines = [line.strip() for line in table_str.splitlines() if line.strip()]

        if len(lines) < 2:
            print(f"❌ Parsing Error: Not enough lines in table for {player_name}.")
            print(f"Raw response:\n---\n{table_str}\n---")
            return pd.DataFrame()
        # --- Find the header line ---
        header_index = -1
        expected_header = ['Player', 'Shots', 'Goals', 'Assists', 'Free Kicks', 'Fouls', 'Yellow Cards', 'Red Cards', 'Offsides']
        # Heuristic: Header starts/ends with '|' and contains key columns like 'Player' and 'Shots'
        for i, line in enumerate(lines):
            if line.startswith('|') and line.endswith('|') and expected_header[0] in line and expected_header[1] in line:
                 # Basic validation of header structure
                 potential_header = [h.strip() for h in line.strip('|').split('|')]
                 if len(potential_header) == len(expected_header): # Check column count
                    header_index = i
                    break # Found it

        if header_index == -1:
            print(f"❌ Parsing Error: Could not find valid header line for {player_name}.")
            print(f"Cleaned lines:\n---\n{lines}\n---")
            return pd.DataFrame()
        # --- Header line found at header_index ---

        header_line = lines[header_index]

        # --- Find the data line (must come after header and potential separator) ---
        data_line = None
        # Start searching *after* the header line
        for i in range(header_index + 1, len(lines)):
            line = lines[i]
            # Skip the separator line
            if not re.match(r'^\|?[\s\-|\u00A0]+(\|[\s\-|\u00A0]+)*\|?$', line): # More robust separator check
                # This is the first non-separator line after the header
                if line.startswith('|') and line.endswith('|'): # Check if it looks like a data row
                   data_line = line
                   break # Found the first data line

        if data_line is None:
            print(f"❌ Parsing Error: No valid data line found after header for {player_name}.")
            print(f"Header found: {header_line}")
            print(f"Lines searched after header:\n---\n{lines[header_index+1:]}\n---")
            return pd.DataFrame()
        # --- Data line found ---

        # Parse header and data (strip will now work correctly after NBSP replacement)
        header = [h.strip() for h in header_line.strip('|').split('|')]
        data = [d.strip() for d in data_line.strip('|').split('|')] # strip removes leading/trailing spaces

        # --- Header Validation (using the *actual* parsed header) ---
        if header != expected_header:
            # Allow for minor variations if needed, but strict check is safer
            print(f"❌ Parsing Error: Parsed header does not match expected format for {player_name}.")
            print(f"Parsed Header: {header}")
            print(f"Expected:      {expected_header}")
            print(f"Raw response:\n---\n{table_str}\n---")
            return pd.DataFrame()
        # --- Header matches expected ---


        if len(data) != len(header):
            print(f"❌ Parsing Error: Mismatched number of columns between header and data for {player_name}.")
            print(f"Header ({len(header)}): {header}")
            print(f"Data ({len(data)}):   {data}")
            print(f"Raw response:\n---\n{table_str}\n---")
            return pd.DataFrame()

        df = pd.DataFrame([data], columns=header)

        # Handle incorrect/missing player name
        if df['Player'].iloc[0] != player_name:
            print(f"⚠️ Warning: LLM returned data for player '{df['Player'].iloc[0]}' instead of expected '{player_name}'. Correcting.")
            df['Player'] = player_name

        numeric_cols = [col for col in header if col != 'Player']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        return df

    except Exception as e:
        print(f"❌ Parsing Error for player {player_name}: {e}")
        print(f"Problematic table string:\n---\n{table_str}\n---")
        return pd.DataFrame()

# --- Main Processing Logic ---

# Part 1: Load Data
try:
    with open(INPUT_JSON_FILE) as f:
        train_data = json.load(f)
    train_df = pd.json_normalize(train_data)
    print(f"Loaded {len(train_df)} samples from {INPUT_JSON_FILE}")
except FileNotFoundError:
    print(f"Error: Input file '{INPUT_JSON_FILE}' not found.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{INPUT_JSON_FILE}'.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred loading the data: {e}")
    exit()


# Part 2 & 3: Process each sample, extract events, generate prompts, call API, parse, and save
#min(NUM_SAMPLES_TO_PROCESS, len(train_df))
for i in range(43, 44):
    print(f"\n--- Processing Sample {i+1} ---")
    sample_row = train_df.iloc[i]
    raw_commentary = sample_row['text']

    # Optional: Format commentary for readability if needed for debugging
    # formatted_commentary = format_commentary(raw_commentary)
    # Use raw_commentary for extraction as formatting might interfere with regex
    
    # Step 2.1: Extract events and players for THIS sample
    events_by_player, players_in_sample = extract_all_events_from_commentary(raw_commentary)
    
    home_players = sorted(list(players_in_sample['Home Team']))
    away_players = sorted(list(players_in_sample['Away Team']))

    print(f"Home Players Found: {len(home_players)} {home_players if len(home_players) < 10 else '[Truncated]'}")
    print(f"Away Players Found: {len(away_players)} {away_players if len(away_players) < 10 else '[Truncated]'}")

    # Initialize empty DataFrames for this sample's stats
    home_stats_list = []
    away_stats_list = []

    # Step 3.1: Process Home Team Players
    print("Processing Home Team...")
    for player in home_players:
        player_event_statements = events_by_player['Home Team'].get(player, []) # Get events or empty list
        
        # Generate prompt for this player using their specific events
        player_prompt = generate_prompt_for_player(player, player_event_statements)
        
        # Get response from API
        response_content = get_model_response(player_prompt, player, i)
        
        if response_content:
            # Parse the table from the response
            table_df = parse_table_to_df(response_content, player)
            if not table_df.empty:
                home_stats_list.append(table_df)
            else:
                 print(f"Could not parse valid stats table for Home Player: {player}")
        else:
            print(f"No response or error getting stats for Home Player: {player}")


    # Step 3.2: Process Away Team Players
    print("Processing Away Team...")
    for player in away_players:
        player_event_statements = events_by_player['Away Team'].get(player, []) # Get events or empty list
        
        # Generate prompt
        player_prompt = generate_prompt_for_player(player, player_event_statements)
        
        # Get response
        response_content = get_model_response(player_prompt, player, i)
        
        if response_content:
            # Parse table
            table_df = parse_table_to_df(response_content, player)
            if not table_df.empty:
                away_stats_list.append(table_df)
            else:
                 print(f"Could not parse valid stats table for Away Player: {player}")
        else:
            print(f"No response or error getting stats for Away Player: {player}")

    # Step 3.3: Combine and Save CSVs for the current sample
    home_output_file = os.path.join(OUTPUT_DIR, f'Sample_{i+1}_home_team_stats.csv')
    if home_stats_list:
        home_stats_df = pd.concat(home_stats_list, ignore_index=True)
        home_stats_df.to_csv(home_output_file, index=False)
        print(f"Saved Home Team stats to {home_output_file}")
    else:
        print(f"No valid home team stats generated for Sample {i+1}. Skipping CSV creation.")
        # Optional: Create an empty file anyway if required
        # pd.DataFrame(columns=['Player', 'Free Kicks', 'Fouls', 'Yellow Cards', 'Corner Kicks', 'Shots', 'Goals', 'Assists', 'Offsides']).to_csv(home_output_file, index=False)


    away_output_file = os.path.join(OUTPUT_DIR, f'Sample_{i+1}_away_team_stats.csv')
    if away_stats_list:
        away_stats_df = pd.concat(away_stats_list, ignore_index=True)
        away_stats_df.to_csv(away_output_file, index=False)
        print(f"Saved Away Team stats to {away_output_file}")
    else:
        print(f"No valid away team stats generated for Sample {i+1}. Skipping CSV creation.")
        # Optional: Create an empty file anyway if required
        # pd.DataFrame(columns=['Player', 'Free Kicks', 'Fouls', 'Yellow Cards', 'Corner Kicks', 'Shots', 'Goals', 'Assists', 'Offsides']).to_csv(away_output_file, index=False)

    print(f"--- Sample {i+1} processing completed. ---")

print("\nAll specified samples processed.")