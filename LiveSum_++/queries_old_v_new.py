query_list = [{'id': 1, 'name': 'Analysis: Aggressive Start (Second Half)',
    'query':
    'Who came out of the tunnel fired up? Show the foul count for each team in the first five minutes of the second half.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Team_s, COUNT(*) as foul_count 
        FROM parsed_commentary_{match_id}
        WHERE half = 'Second Half' AND match_minute 
        BETWEEN 45 AND 50 AND Event_Type = 'Foul' 
        GROUP BY Team_s 
        ORDER BY foul_count DESC;
        """
    , 'Natural Language Explanation':
    """
        This query aims to show which team was more active just after the half-time break, 
        by tracking how many fouls each team had in the first five minutes of the second half. 
        """
    , 'headers': ['Team_s', 'foul_count']}, {'id': 2, 'name':
    'Analysis: Back-to-Back Corners', 'query':
    'Did any team build pressure with corners? Show me if a team won two or more in a row.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        EventSequence AS (SELECT Team_s, Event_Type, LAG(Event_Type, 1) OVER (ORDER BY row_id) as prev_event, LAG(Team_s, 1) OVER (ORDER BY row_id) as prev_team FROM AllEventsWithRowID)
        SELECT Team_s, COUNT(*) as consecutive_corners FROM EventSequence WHERE Event_Type = 'Corner' AND prev_event = 'Corner' AND Team_s = prev_team GROUP BY Team_s;
        """
    , 'Natural Language Explanation':
    """
        The idea here is to see where teams won two or more corners consecutively, indicating that the opposition defense 
        and goalkeeper were heavily tested by a barrage of shots in a short period.
        """
    , 'headers': ['Team_s', 'consecutive_corners']}, {'id': 3, 'name':
    'Analysis: Corner Effectiveness', 'query':
    "How good were {Team}'s corners? Show me the percentage that led to a shot within the next three events."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        TeamCorners AS (SELECT row_id FROM AllEventsWithRowID WHERE Event_Type = 'Corner' AND Team_s = '{Team}'),
        SuccessfulCorners AS (SELECT COUNT(*) as success_count FROM TeamCorners tc 
        WHERE EXISTS (SELECT 1 FROM AllEventsWithRowID s WHERE s.Team_s = '{Team}' AND s.Event_Type IN ('Shot', 'Goal') AND s.row_id BETWEEN tc.row_id + 1 AND tc.row_id + 3))
        SELECT CAST((SELECT success_count FROM SuccessfulCorners) AS REAL) * 100.0 / COUNT(*) FROM TeamCorners;
        """
    , 'Natural Language Explanation':
    """
        This is checking how 'dangerous' a team's corners were by finding how many (as a percent) led to a shot within 3 events, 
        usually indicative of the 1 to 3 minutes after the corner was taken. 
        """
    , 'headers': []}, {'id': 4, 'name':
    'Analysis: Early Goal Check (First 5 Mins)', 'query':
    'Was there a flying start to the match? Show me any goals scored in the first five minutes.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Score FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' AND match_minute < 5;
        """
    , 'Natural Language Explanation':
    """
        This is checking if the match got off to a quick start, 
        namely by checking if there were any goals scored inside the first 5 minutes. 
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 5, 'name':
    'Analysis: Final Minutes Goals (First Half)', 'query':
    'Any late drama before the break? Show me goals from the last {X} minutes of the first half: who scored, when, and the commentary description.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Score, Description FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' AND half = 'First Half' AND match_minute >= 45 - {X};
        """
    , 'Natural Language Explanation':
    """
        This query is trying to find any late drama before the half-time break, 
        namely if any goals were scored in the final X minutes of the first half. 
        If there were, it would print out who scored, when, and the commentary if the goal. 
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score', 'Description']}, {
    'id': 6, 'name': 'Analysis: First Card of the Match', 'query':
    'Who was the first player to have their name taken? Show the full details of the first yellow card.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Yellow Card' 
        ORDER BY match_minute ASC, injury_time_minutes ASC, Time ASC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query simply finds the first player, in the entire match, to have been issued a yellow card. 
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 7,
    'name': 'Analysis: First Event of Match', 'query':
    'How did the action get started? Show me the very first recorded event after the opening kick-off.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} WHERE Event_Type != 'Match Start' 
        ORDER BY match_minute ASC, injury_time_minutes ASC, Time ASC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is just looking at the very beginning of the match, 
        specifically at the event right after the match started. 
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 8, 'name': 'Analysis: First Foul of the Match', 'query':
    'Who set the physical tone early? Show me the details of the very first foul of the game.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Foul' 
        ORDER BY match_minute ASC, injury_time_minutes ASC, Time ASC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This looks at the first foul to occur after the match began
        and prints out the necessary details: Who, when, and for what team.
        """
    , 'headers': ['Time', 'Player_s', 'Team_s']}, {'id': 9, 'name':
    'Analysis: First Scorer Wins?', 'query':
    "Did the team that opened the scoring go on to win? Just give me a 'Yes' or 'No'."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Goals AS (SELECT * FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal'), 
        FinalScore AS (SELECT Team_s, COUNT(Team_s) AS total_goals FROM Goals GROUP BY Team_s),
        MatchResult AS (SELECT MAX(CASE WHEN A.total_goals > B.total_goals THEN A.Team_s ELSE B.Team_s END) AS WinningTeam, MIN(A.total_goals) AS LoserScore FROM FinalScore AS A, FinalScore AS B WHERE A.Team_s <> B.Team_s),
        OrderedGoals AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute ASC) as goal_order FROM Goals),
        FirstGoalScorer AS (SELECT Team_s FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal' ORDER BY match_minute ASC LIMIT 1)
        SELECT CASE WHEN (SELECT Team_s FROM FirstGoalScorer) = (SELECT WinningTeam FROM MatchResult) Then 'Yes' ELSE 'No' END AS First_Scorer_Won;
        """
    , 'Natural Language Description':
    """
        Find out if the team who scored first went on to win the match.
        1. Find all the goals
        2. Find the final score (and differetntiate the teams)
        3. Determine if the winning team from the final score matches the first team to score
        """
    , 'headers': ['First_Scorer_Won']}, {'id': 10, 'name':
    'Analysis: Free-Kick Shots', 'query':
    'Any dangerous free-kicks? Show me a list of all shots taken directly from a free-kick.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Shot' 
        AND Description LIKE '%from the free-kick%';
        """
    , 'Natural Language Description':
    """
        This query looks to find any shots that came directly from a free-kick.
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 11,
    'name': 'Analysis: Goals from Deflections', 'query':
    'Any lucky goals today? Show me a list of all goals that took a deflection.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Score, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' 
        AND Description LIKE '%deflection%';
        """
    , 'Natural Language Description':
    """
        Often times, goals can unfortunately take a deflection and go in due to a drastic change in direction. 
        This query attempts to find all such events (if any) that happened in the match.
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score', 'Description']}, {
    'id': 12, 'name': 'Analysis: Goalscorer Substituted Off', 'query':
    'Were any goalscorers taken off? Show me players who scored a goal and were later subbed out.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT g.Time as Goal_Time, s.Time as Sub_Time, g.Player_s, g.Team_s
        FROM parsed_commentary_{match_id} g JOIN parsed_commentary_{match_id} s ON g.Player_s = s.Player_Out AND g.Team_s = s.Team_s
        WHERE g.Event_Type = 'Goal' AND s.Event_Type = 'Substitution' AND s.match_minute > g.match_minute;
        """
    , 'Natural Language Description':
    """
        This query tries to find all the goalscorers and see if there were any goalscorers who were later substituted for any reason.
        """
    , 'headers': ['Goal_Time', 'Sub_Time', 'Player_s', 'Team_s']}, {'id': 
    13, 'name': 'Analysis: Injury Forced Sub', 'query':
    'Show me the subs that were forced by an injury. I need a list of players injured and then immediately subbed off.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id})
        SELECT i.Time, i.Player_s, i.Team_s FROM AllEventsWithRowID i
        JOIN AllEventsWithRowID s ON i.Player_s = s.Player_Out AND i.Team_s = s.Team_s
        WHERE i.Event_Type = 'Injury' AND s.Event_Type = 'Substitution' AND s.row_id BETWEEN i.row_id + 1 AND i.row_id + 3;
        """
    , 'Natural Language Description':
    """
        This query is intended to find the Injury substitutes, 
        essentially the players brought on in replacement of an injured player.
        """
    , 'headers': ['Time', 'Player_s', 'Team_s']}, {'id': 14, 'name':
    'Analysis: Late Game Activity by Team', 'query':
    'Which team finished stronger? Show me who had more actions in the final {X} minutes and what their total was.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, COUNT(*) AS actions 
        FROM parsed_commentary_{match_id} 
        WHERE match_minute >= 90 - {X} 
        GROUP BY Team_s 
        ORDER BY actions DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        Typically the last minutes of a football match are usually frantic as teams may be pushing for an equalizer, 
        pushing for a winning goal, or even just trying to preserve their fragile lead. 
        This query aims to evaluate both teams on the events that they were involved in during this period, and then finds the "stronger" (more active) team.
        """
    , 'headers': ['Team_s', 'actions']}, {'id': 15, 'name':
    'Analysis: Lead Changes Count', 'query':
    'How many times did the lead swing back and forth? Give me the moments when the lead changed.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Goals AS (SELECT * FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal'), 
        FinalScore AS (SELECT Team_s, COUNT(Team_s) AS total_goals FROM Goals GROUP BY Team_s),
        OrderedGoals AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute ASC) AS goal_order FROM Goals),
        CumulativeScore AS (SELECT goal_order, match_minute, Team_s, Player_s, Score, Time,
            SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 0) THEN 1 ELSE 0 END)
                OVER (ORDER BY goal_order) AS team1_goals,
            SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END)
                OVER (ORDER BY goal_order) AS team2_goals
        FROM OrderedGoals),
        TiedMoments AS (SELECT 0 AS goal_order UNION SELECT goal_order FROM CumulativeScore WHERE team1_goals = team2_goals),
        NextGoals AS (SELECT MIN(cs.goal_order) AS goal_order_after_tie FROM TiedMoments tm JOIN CumulativeScore cs ON cs.goal_order > tm.goal_order GROUP BY tm.goal_order),
        Final AS (SELECT cs.* FROM CumulativeScore cs JOIN NextGoals ng ON cs.goal_order = ng.goal_order_after_tie)
        SELECT Time, Player_s, Team_s, Score
        FROM Final
        ORDER BY goal_order;
        """
    , 'Natural Language Description':
    """
        This simply is to see if the match was back-and-forth, specifically by tracking how many times the lead changed.
        The process by which it attempts to do this is:
        1. Find all the goals (since these are the only way the lead can change)
        2. Find the moments where the game was tied
        3. Count the goals that changed the lead and return those moments
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 16,
    'name': 'Analysis: Longest Period without a Foul', 'query':
    'What was the cleanest spell of the match? Show the two fouls that bookend the longest period without one.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        FoulTimes AS (SELECT row_id, match_minute, LAG(row_id, 1) OVER (ORDER BY row_id) as prev_foul_row_id, (match_minute - LAG(match_minute, 1, 0) OVER (ORDER BY row_id)) as gap FROM AllEventsWithRowID WHERE Event_Type = 'Foul'),
        MaxGap AS (SELECT MAX(gap) as max_gap FROM FoulTimes)
        SELECT p.Time, p.Event_Type, p.Player_s FROM AllEventsWithRowID p JOIN FoulTimes ft ON p.row_id = ft.row_id OR p.row_id = ft.prev_foul_row_id WHERE ft.gap = (SELECT max_gap FROM MaxGap);
        """
    , 'Natural Language Description':
    """
        This query is designed to find the longest period without a foul in the match.
        It does this by:
        1. Finding all the fouls in the match
        2. Calculating the time gaps between consecutive fouls
        3. Finding the maximum gap and returning the fouls that bookend this period
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s']}, {'id': 17, 'name':
    'Analysis: Post-Sub Concession', 'query':
    'Did a sub backfire for {Team}? Show me any goals they conceded within 5 minutes of making a change.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH SubTimes AS (SELECT match_minute as sub_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution' AND Team_s = '{Team}')
        SELECT g.Time, g.Player_s, g.Score FROM SubTimes st
        JOIN parsed_commentary_{match_id} g ON g.Event_Type = 'Goal' AND g.Team_s != '{Team}'
        WHERE g.match_minute BETWEEN st.sub_minute AND st.sub_minute + 5;
        """
    , 'Natural Language Description':
    """
        This query checks if a substitution led to conceding a goal shortly after.
        It does this by:
        1. Finding the minute of each substitution made
        2. Checking if any goals were conceded within 5 minutes of those substitutions
        """
    , 'headers': ['Time', 'Player_s', 'Score']}, {'id': 18, 'name':
    'Analysis: Red Card Impact', 'query':
    'What was the score when the red card came out, and how did it finish? Show both scorelines.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH RedCardEvent AS (SELECT Score FROM parsed_commentary_{match_id} WHERE Event_Type = 'Red Card' ORDER BY match_minute, injury_time_minutes, Time LIMIT 1)
        SELECT r.Score as score_at_red_card, f.Score as final_score 
        FROM RedCardEvent r, (SELECT Score FROM parsed_commentary_{match_id} WHERE Event_Type = 'Full Time' LIMIT 1) f;
        """
    , 'Natural Language Description':
    """
        This query is designed to show the impact of a red card (if any) on the match score.
        It does this by:
        1. Finding the score at the moment of the red card
        2. Finding the final score at full time
        3. Returning both scores for comparison
        """
    , 'headers': ['score_at_red_card', 'final_score']}, {'id': 19, 'name':
    'Analysis: Score at Halftime', 'query':
    'What was the story at the break? Just show me the halftime score.',
    'difficulty': 'Easy', 'SQL':
    """
        SELECT Score 
        FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Half Time' 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query simply retrieves the score at halftime.
        It does this by looking for the 'Half Time' event and returning the score at that moment.
        """
    , 'headers': ['Score']}, {'id': 20, 'name':
    'Analysis: Shortest Time Between Goals', 'query':
    'What was the quickest one-two punch of the game? Show me the two goals scored closest together.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalTimes AS (SELECT row_id, match_minute, LAG(row_id, 1) OVER (ORDER BY row_id) as prev_goal_row_id, (match_minute - LAG(match_minute, 1, -99) OVER (ORDER BY row_id)) as gap FROM AllEventsWithRowID WHERE Event_Type = 'Goal'),
        MinGap AS (SELECT MIN(gap) as min_gap FROM GoalTimes WHERE gap >= 0)
        SELECT p.Time, p.Player_s, p.Team_s, p.Score FROM AllEventsWithRowID p JOIN GoalTimes gt ON p.row_id = gt.row_id OR p.row_id = gt.prev_goal_row_id WHERE gt.gap = (SELECT min_gap FROM MinGap);
        """
    , 'Natural Language Description':
    """
        This query is designed to find the two goals that were scored closest together in time.
        It does this by:
        1. Finding all the goals in the match
        2. Calculating the time gaps between consecutive goals
        3. Finding the minimum gap and returning the details of the two goals that bookend this period
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 21,
    'name': 'Analysis: Shot to Goal Kick Ratio', 'query':
    'Show me the ratio of poor shots. How many times did a shot or goal event lead directly to a goal kick in the logs?'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        EventSequence AS (SELECT Event_Type, LEAD(Event_Type, 1) OVER (ORDER BY row_id) as next_event FROM AllEventsWithRowID)
        SELECT COUNT(*) FROM EventSequence WHERE Event_Type IN ('Shot', 'Goal') AND next_event = 'Goal kick';
        """
    , 'Natural Language Description':
    """
        This query aims to find how many times a shot or goal event was immediately followed by a goal kick.
        It does this by:
        1. Finding all the events in the match
        2. Checking if a shot or goal was immediately followed by a goal kick
        3. Counting those occurrences to give a ratio of poor shots leading to goal kicks
        """
    , 'headers': ['*']}, {'id': 22, 'name': 'Analysis: Stoppage Time Cards',
    'query':
    'Did things get heated in added time? Show me all the cards dished out in stoppage time in either half.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, Time, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type IN ('Yellow Card', 'Red Card') 
        AND injury_time_minutes > 0;
        """
    , 'Natural Language Description':
    """
        This query is designed to find any cards issued during stoppage time in either half.
        It does this by:
        1. Looking for events that are either yellow or red cards
        2. Filtering those events to only include those that occurred during stoppage time (where injury_time_minutes > 0)
        3. Returning the details of those cards, including the half they occurred in
        """
    , 'headers': ['half', 'Time', 'Player_s', 'Team_s', 'Description']}, {
    'id': 23, 'name': 'Analysis: Sub Creating a Chance', 'query':
    'Did any sub set up a teammate quickly? Show me shots created by a sub for another player within 10 minutes of coming on.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        SubEvents AS (SELECT Player_In, Team_s, match_minute AS sub_minute FROM AllEventsWithRowID WHERE Event_Type = 'Substitution')
        SELECT s.Time, s.Player_s, s.Team_s, s.Description FROM AllEventsWithRowID s
        JOIN SubEvents sub ON s.Team_s = sub.Team_s
        WHERE s.Event_Type = 'Shot' AND s.match_minute BETWEEN sub.sub_minute AND sub.sub_minute + 10
        AND s.Player_s != sub.Player_In AND EXISTS (SELECT 1 FROM AllEventsWithRowID p WHERE p.Player_s = sub.Player_In AND p.row_id = s.row_id - 1);
        """
    , 'Natural Language Description':
    """
        This query is designed to find instances where a substitute player created a chance for another player within 10 minutes of coming on.
        It does this by:
        1. Identifying all substitutions and their timings
        2. Checking for shots taken by other players within 10 minutes of the substitute coming on
        3. Ensuring that the shot was not taken by the substitute themselves
        4. Returning the details of those shots, including the time, player, team, and description
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 24,
    'name': 'Analysis: Team Reaction to Conceding', 'query':
    'How did {Team} respond to going behind? Show me all the shots they had in the 10 minutes after conceding.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH GoalConceded AS (SELECT match_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal' AND Team_s != '{Team}' ORDER BY match_minute ASC LIMIT 1)
        SELECT c.Time, c.Player_s, c.Description FROM parsed_commentary_{match_id} AS c, GoalConceded AS gc
        WHERE c.Team_s = '{Team}' AND c.Event_Type = 'Shot' AND c.match_minute > gc.match_minute AND c.match_minute <= gc.match_minute + 10;
        """
    , 'Natural Language Description':
    """
        This query is designed to find how a specific team reacted after conceding a goal.
        It does this by:
        1. Identifying the minute when the opposing team scored their goal
        2. Checking for shots taken by the specified team within 10 minutes after that goal
        3. Returning the details of those shots, including the time, player, and description
        """
    , 'headers': ['Time', 'Player_s', 'Description']}, {'id': 25, 'name':
    'Analysis: Wasted Shots', 'query':
    "Show me the poor finishing. I need a count for each team of shots that went 'high and wide' or 'well over'."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Team_s, COUNT(*) as wasted_shots 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Shot' 
        AND (Description LIKE '%well over%' OR Description LIKE '%high and wide%') 
        GROUP BY Team_s 
        ORDER BY wasted_shots DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the number of poor finishing attempts by each team.
        It does this by:
        1. Looking for shots that have descriptions indicating they went 'high and wide' or 'well over'
        2. Counting those shots for each team
        3. Returning the count of wasted shots for each team, ordered by the number of wasted shots in descending order
        """
    , 'headers': ['Team_s', 'wasted_shots']}, {'id': 26, 'name':
    'Analysis: Yellow Card Tactical Sub', 'query':
    'Which managers played it safe? Show me players who were booked and then later taken off.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT T1.Player_s, T1.Team_s, T1.Time AS Card_Time, T2.Time AS Sub_Time FROM parsed_commentary_{match_id} T1 
        JOIN parsed_commentary_{match_id} T2 ON T1.Player_s = T2.Player_Out
        WHERE T1.Event_Type = 'Yellow Card' 
        AND T2.Event_Type = 'Substitution' 
        AND T2.match_minute > T1.match_minute;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who received a yellow card and were subsequently substituted off.
        It does this by:
        1. Identifying all yellow card events and their timings
        2. Joining those events with substitution events where the player who received the yellow card was substituted off
        3. Ensuring that the substitution occurred after the yellow card was issued
        4. Returning the details of those players, including their name, team, card time, and substitution time
        """
    , 'headers': ['Player_s', 'Team_s', 'Card_Time', 'Sub_Time']}, {'id': 
    27, 'name': 'Between Goals: All Events (Both Teams)', 'query':
    'For any team that scored more than once, what happened between their first and second goals? Show me the full timeline for BOTH teams during these periods.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (
            SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}
        ), RankedGoals AS (
            SELECT Team_s, row_id, ROW_NUMBER() OVER(PARTITION BY Team_s ORDER BY row_id ASC) as goal_num FROM AllEventsWithRowID WHERE Event_Type = 'Goal' AND Team_s IS NOT NULL
        ), TeamGoalIntervals AS (
            SELECT Team_s, MIN(CASE WHEN goal_num = 1 THEN row_id END) AS first_goal_row_id, MIN(CASE WHEN goal_num = 2 THEN row_id END) AS second_goal_row_id FROM RankedGoals GROUP BY Team_s HAVING COUNT(Team_s) >= 2
        )
        SELECT DISTINCT c.Time, c.Player_s, c.Team_s, c.Event_Type, c.Description
        FROM AllEventsWithRowID AS c
        JOIN TeamGoalIntervals AS tgi ON c.row_id BETWEEN tgi.first_goal_row_id AND tgi.second_goal_row_id
        ORDER BY c.row_id;
        """
    , 'Natural Language Description':
    """
        This query is designed to find all events that occurred between the first and second goals for any team that scored more than once.
        It does this by:
        1. Identifying all events in the match and assigning a row ID to each event
        2. Ranking the goals for each team to find the first and second goals
        3. Creating intervals for each team's first and second goals
        4. Joining those intervals with the original events to find all events that occurred between the first and second goals
        5. Returning the details of those events, including the time, player, team, event type, and description
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Event_Type', 'Description'
    ]}, {'id': 28, 'name':
    'Comparison: First Half vs Second Half Dominance', 'query':
    'Who dominated each half? Show the total event count for both teams, broken down by half.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, Team_s, COUNT(*) as event_count 
        FROM parsed_commentary_{match_id} 
        WHERE Team_s IS NOT NULL 
        GROUP BY half, Team_s 
        ORDER BY half, event_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the dominance of each team in the first and second halves of the match.
        It does this by:
        1. Grouping all events by half and team
        2. Counting the number of events for each team in each half
        3. Returning the total event count for both teams, broken down by half
        4. Ordering the results by half and event count in descending order
        """
    , 'headers': ['half', 'Team_s', 'event_count']}, {'id': 29, 'name':
    'Comparison: Goalkeeper Activity', 'query':
    'Which keeper was the busier of the two? Show a breakdown of saves, punches, and catches for each.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as keeper_actions 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Save' OR Description LIKE '%keeper%' OR Description LIKE '%goalkeeper%' 
        GROUP BY Player_s, Team_s 
        ORDER BY keeper_actions DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the activity of both goalkeepers in the match.
        It does this by:
        1. Filtering the events to only include those related to goalkeeper actions (saves, punches, catches)
        2. Grouping those actions by goalkeeper and team
        3. Counting the number of actions for each goalkeeper
        4. Returning the results ordered by the number of actions in descending order
        """
    , 'headers': ['Player_s', 'Team_s', 'keeper_actions']}, {'id': 30,
    'name': 'Comparison: Goals Per Half', 'query':
    'Was it a game of two halves for goalscoring? Show me which half had the most goals and the count.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, COUNT(*) AS goals 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' 
        GROUP BY half 
        ORDER BY goals DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find out which half of the match had the most goals scored.
        It does this by:
        1. Filtering the events to only include goals
        2. Grouping those goals by half
        3. Counting the number of goals in each half
        4. Returning the half with the highest goal count
        """
    , 'headers': ['half', 'goals']}, {'id': 31, 'name':
    'Comparison: Offside Trap Success', 'query':
    'Who had the better-organised back line? Show me the offside count for both teams.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, COUNT(*) AS offside_count 
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Offside' AND Team_s IS NOT NULL 
        GROUP BY Team_s 
        ORDER BY offside_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the effectiveness of each team's defensive line in terms of offside traps.
        It does this by:
        1. Filtering the events to only include offsides
        2. Grouping those offsides by team
        3. Counting the number of offsides for each team
        4. Returning the results ordered by the number of offsides in descending order
        """
    , 'headers': ['Team_s', 'offside_count']}, {'id': 32, 'name':
    'Comparison: Shots Per Half', 'query':
    "Let's compare the attacking intent. Show me the shot count for both teams, split by first and second half."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, Team_s, COUNT(*) AS shot_count 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Shot' AND Team_s IS NOT NULL 
        GROUP BY half, Team_s 
        ORDER BY half, shot_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the attacking intent of both teams in the first and second halves of the match.
        It does this by:
        1. Filtering the events to only include shots
        2. Grouping those shots by half and team
        3. Counting the number of shots for each team in each half
        4. Returning the results ordered by half and shot count in descending order
        """
    , 'headers': ['half', 'Team_s', 'shot_count']}, {'id': 33, 'name':
    'IL - Injury List', 'query':
    'Who had to receive treatment? List all the players who got injured, when it happened, and which team they play for.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Injury';
        """
    , 'Natural Language Description':
    """
        This query is designed to find all the players who received treatment for injuries during the match.
        It does this by:
        1. Filtering the events to only include injuries
        2. Returning the details of those injuries, including the time, player, and team
        """
    , 'headers': ['Time', 'Player_s', 'Team_s']}, {'id': 34, 'name':
    'List: All Yellow Cards', 'query':
    "Who went into the ref's book? Give me a list of all the yellow cards, who got them, when, and what it was for."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Yellow Card';
        """
    , 'Natural Language Description':
    """
        This query is designed to find all the yellow cards issued during the match.
        It does this by:
        1. Filtering the events to only include yellow cards
        2. Returning the details of those yellow cards, including the time, player, team, and description of the offense
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 35,
    'name': 'List: Team Roster for Match', 'query':
    'Who featured for {Team} today? Give me a complete list of their players involved, including subs.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s FROM (SELECT Player_s FROM parsed_commentary_{match_id} WHERE Team_s = '{Team}' 
        UNION 
        SELECT Player_In FROM parsed_commentary_{match_id} WHERE Team_s = '{Team}') WHERE Player_s IS NOT NULL 
        GROUP BY Player_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to provide a complete list of players who featured for a specific team in the match.
        It does this by:
        1. Selecting players who were directly involved in the match (either as starters or substitutes)
        2. Combining the lists of starting players and substitutes  
        3. Ensuring that each player is only listed once
        4. Returning the unique list of players for that team
        """
    , 'headers': ['Player_s']}, {'id': 36, 'name':
    'Player Focus: Brace Scorer', 'query':
    'Did anyone bag a brace today? Show me any player who scored exactly two goals.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' AND Player_s IS NOT NULL 
        GROUP BY Player_s, Team_s 
        HAVING COUNT(*) = 2;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who scored exactly two goals in the match.
        It does this by:
        1. Filtering the events to only include goals
        2. Grouping those goals by player and team
        3. Counting the number of goals for each player
        4. Returning the players who scored exactly two goals, along with their team
        """
    , 'headers': ['Player_s', 'Team_s']}, {'id': 37, 'name':
    'Player Focus: Early Match Involvement', 'query':
    'How did {Player} start the game? Show me everything he was involved in during the first {X} minutes.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Player_s = '{Player}' AND match_minute <= {X};
        """
    , 'Natural Language Description':
    """
        This query is designed to find all the events that a specific player was involved in during the first X minutes of the match.
        It does this by:
        1. Filtering the events to only include those involving the specified player
        2. Limiting the results to the first X minutes of the match
        3. Returning the time, event type, and description of each event
        """
    , 'headers': ['Time', 'Event_Type', 'Description']}, {'id': 38, 'name':
    'Player Focus: Early Substitution Check', 'query':
    'Was {Player} an early change? Show me if he was subbed on before the hour mark.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_Out FROM parsed_commentary_{match_id} 
        WHERE Player_In = '{Player}' 
        AND Event_Type = 'Substitution' 
        AND match_minute < 60;
        """
    , 'Natural Language Description':
    """
        This query is designed to check if a specific player was substituted on before the 60th minute of the match.
        It does this by:
        1. Filtering the substitution events to only include those where the specified player was substituted in
        2. Checking if the substitution occurred before the 60th minute
        3. Returning the time of the substitution and the player who was substituted out
        """
    , 'headers': ['Time', 'Player_Out']}, {'id': 39, 'name':
    'Player Focus: Final Shot of the Match', 'query':
    'Who had the last crack at goal? Show me the details of the final shot of the game.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Shot' 
        ORDER BY match_minute DESC, injury_time_minutes DESC, Time DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the last shot taken in the match.
        It does this by:
        1. Filtering the events to only include shots
        2. Ordering those shots by match minute, injury time, and time in descending order
        3. Limiting the results to the most recent shot (the last one taken in the match)
        4. Returning the time, player, team, and description of that shot
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 40,
    'name': 'Player Focus: First Half Card Check', 'query':
    'Did {Player} get into any trouble in the first half? Show me the details if he got a card.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Description FROM parsed_commentary_{match_id} 
        WHERE Player_s = '{Player}' AND Event_Type IN ('Yellow Card', 'Red Card') AND half = 'First Half';
        """
    , 'Natural Language Description':
    """
        This query is designed to check if a specific player received any cards in the first half of the match.
        It does this by:
        1. Filtering the events to only include cards (yellow or red)
        2. Checking if the specified player was involved in those events
        3. Ensuring that the events occurred in the first half of the match
        4. Returning the time and description of the card event
        """
    , 'headers': ['Time', 'Description']}, {'id': 41, 'name':
    'Player Focus: Full Match Timeline', 'query':
    'Give me the full story on {Player}. Show me a timeline of every key moment he was involved in all game.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Description 
        FROM parsed_commentary_{match_id} WHERE Player_s = '{Player}' OR Player_In = '{Player}' OR Player_Out = '{Player}' 
        ORDER BY match_minute, injury_time_minutes;
        """
    , 'Natural Language Description':
    """
        This query is designed to provide a complete timeline of all key moments involving a specific player throughout the match.
        It does this by:
        1. Filtering the events to include those where the player was either directly involved (as Player_s) or substituted in or out
        2. Ordering those events by match minute and injury time
        3. Returning the time, event type, and description of each event
        """
    , 'headers': ['Time', 'Event_Type', 'Description']}, {'id': 42, 'name':
    'Player Focus: Getting Carded for a Foul', 'query':
    'Show me the fouls that were straight-up yellow cards. List players who got booked for a foul they committed in the same minute.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT f.Player_s, f.Team_s FROM parsed_commentary_{match_id} f
        JOIN parsed_commentary_{match_id} c ON f.Player_s = c.Player_s AND f.match_minute = c.match_minute
        WHERE f.Event_Type = 'Foul' AND c.Event_Type = 'Yellow Card';
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who received a yellow card for a foul they committed in the same minute.
        It does this by:
        1. Filtering the events to include fouls and yellow cards
        2. Joining the fouls with the yellow cards based on the player and the minute of the event
        3. Ensuring that the foul and the yellow card occurred in the same minute
        4. Returning the players who were booked for their own fouls, along with their team
        """
    , 'headers': ['Player_s', 'Team_s']}, {'id': 43, 'name':
    'Player Focus: Late Game Heroics', 'query':
    'Did {Player} step up at the end? Show me any goals or proxy assists he was involved in during the last 10 minutes.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id})
        SELECT Time, Event_Type, Description FROM AllEventsWithRowID p1 WHERE p1.Player_s = '{Player}' AND p1.match_minute >= 80 AND p1.Event_Type = 'Goal'
        UNION ALL
        SELECT p2.Time, 'Assist (Proxy)', p2.Description FROM AllEventsWithRowID p2 JOIN AllEventsWithRowID p3 ON p2.row_id = p3.row_id - 1
        WHERE p2.Player_s = '{Player}' AND p3.Event_Type = 'Goal' AND p3.match_minute >= 80;
        """
    , 'Natural Language Description':
    """
        This query is designed to find any goals or proxy assists involving a specific player in the last 10 minutes of the match.
        It does this by:
        1. Identifying all events in the match and assigning a row ID to each event
        2. Filtering those events to find goals scored by the player in the last 10 minutes
        3. Additionally, checking for proxy assists where the player assisted a goal in the last 10 minutes
        4. Returning the time, event type, and description of those events
        """
    , 'headers': []}, {'id': 44, 'name': 'Player Focus: Offside Count',
    'query':
    'Was {Player} caught straying? Show me every time he was flagged for offside.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time 
        FROM parsed_commentary_{match_id} 
        WHERE Player_s = '{Player}' 
        AND Event_Type = 'Offside';
        """
    , 'Natural Language Description':
    """
        This query is designed to find all instances where a specific player was flagged for offside during the match.
        It does this by:
        1. Filtering the events to only include offsides
        2. Checking if the specified player was involved in those events
        3. Returning the time of each offside event
        """
    , 'headers': ['Time']}, {'id': 45, 'name':
    'Player Focus: Offside Frequency by Half', 'query':
    "Was {Player}'s timing off more in one half? Show his offside count for the first vs the second half."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, COUNT(*) as offside_count 
        FROM parsed_commentary_{match_id} WHERE Player_s = '{Player}' 
        AND Event_Type = 'Offside' GROUP BY half ORDER BY offside_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the number of offsides committed by a specific player in the first and second halves of the match.
        It does this by:
        1. Filtering the events to only include offsides involving the specified player
        2. Grouping those offsides by half
        3. Counting the number of offsides in each half
        4. Returning the count of offsides for each half, ordered by the count in descending order
        """
    , 'headers': ['half', 'offside_count']}, {'id': 46, 'name':
    'Player Focus: Second Half Goal Check', 'query':
    'Did {Player} find the net after the break? Show me the details if he scored in the second half.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Score, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Player_s = '{Player}' 
        AND Event_Type = 'Goal' 
        AND half = 'Second Half';
        """
    , 'Natural Language Description':
    """
        This query is designed to check if a specific player scored a goal in the second half of the match.
        It does this by:
        1. Filtering the events to only include goals scored by the specified player
        2. Ensuring that the goal occurred in the second half of the match
        3. Returning the time, score, and description of the goal event
        """
    , 'headers': ['Time', 'Score', 'Description']}, {'id': 47, 'name':
    'Player Focus: Sub Foul Rate', 'query':
    'Which substitute was the biggest nuisance? Show me the sub who committed the most fouls.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, COUNT(*) as foul_count FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Foul' AND Player_s IN (SELECT Player_In FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution')
        GROUP BY Player_s 
        ORDER BY foul_count DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the substitute player who committed the most fouls during the match.
        It does this by:
        1. Filtering the events to only include fouls committed by substitute players
        2. Identifying the players who were substituted in
        3. Grouping those fouls by the substitute player
        4. Counting the number of fouls for each substitute player
        5. Returning the substitute player with the highest foul count
        """
    , 'headers': ['Player_s', 'foul_count']}, {'id': 48, 'name':
    "Player Focus: The 'Complete' Game", 'query':
    'Did any player have an eventful day? List anyone who scored, got booked, and was also subbed off.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT p1.Player_s FROM parsed_commentary_{match_id} p1
        WHERE p1.Event_Type = 'Goal' AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} p2 WHERE p2.Player_s = p1.Player_s AND p2.Event_Type IN ('Yellow Card', 'Red Card')
        ) AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} p3 WHERE p3.Player_Out = p1.Player_s AND p3.Event_Type = 'Substitution'
        ) GROUP BY p1.Player_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who had a complete game by scoring a goal, receiving a card, and being substituted off.
        It does this by:
        1. Filtering the events to find players who scored a goal
        2. Checking if those players also received a yellow or red card during the match
        3. Ensuring that those players were substituted off at some point in the match
        4. Returning the names of those players who met all three criteria
        """
    , 'headers': ['Player_s']}, {'id': 49, 'name':
    'Player Focus: Unsuccessful Shots', 'query':
    "Which players from {Team} had their shooting boots on but couldn't find the net? List their players who shot but didn't score."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT DISTINCT Player_s 
        FROM parsed_commentary_{match_id} 
        WHERE Team_s = '{Team}' 
        AND Event_Type = 'Shot' 
        AND Player_s NOT IN (SELECT DISTINCT Player_s FROM parsed_commentary_{match_id} WHERE Team_s = '{Team}' AND Event_Type = 'Goal');
        """
    , 'Natural Language Description':
    """
        This query is designed to find players from a specific team who attempted shots but did not score.
        It does this by:
        1. Filtering the events to include only shots taken by players from the specified team
        2. Excluding those players who scored goals during the match
        3. Returning the distinct list of players who had shots but failed to find the net
        """
    , 'headers': ['Player_s']}, {'id': 50, 'name': 'Scoring Summary',
    'query':
    "Let's get the full story of the goals. Pull up every scorer, the minute they scored, their team, and what the new scoreline was."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Score 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal';
        """
    , 'Natural Language Description':
    """
        This query is designed to provide a complete summary of all goals scored in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Returning the time of the goal, the player who scored, their team, and the scoreline at the time of the goal
        --> This will give a clear overview of the scoring events throughout the match
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 51,
    'name': 'Stat: Final Action of First Half', 'query':
    'What was the last kick of the first half? Show me the details of the final event before the halftime whistle.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} WHERE Event_Type != 'Half Time' AND half = 'First Half' 
        ORDER BY match_minute DESC, injury_time_minutes DESC, Time DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the last event that occurred in the first half of the match.
        It does this by:
        1. Filtering the events to exclude the halftime event
        2. Ensuring that the events are from the first half
        3. Ordering those events by match minute, injury time, and time in descending order
        4. Limiting the results to the most recent event (the last one before halftime)
        5. Returning the time, event type, player involved, team, and description of that event
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 52, 'name': 'Stat: First Goal of the Match', 'query':
    'Who broke the initial deadlock? I need the player, team, time, and score for the opening goal.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Player_s, Team_s, Time, Score 
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal' 
        ORDER BY match_minute ASC, injury_time_minutes ASC, Time ASC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first goal scored in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Ordering those goals by match minute, injury time, and time in ascending order
        3. Limiting the results to the first goal scored
        4. Returning the player who scored, their team, the time of the goal, and the scoreline at that moment
        """
    , 'headers': ['Player_s', 'Team_s', 'Time', 'Score']}, {'id': 53,
    'name': 'Stat: First Half Shots on Target', 'query':
    'How many times did {Team} test the keeper in the first half? Show me all their shots on target before the break.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Description 
        FROM parsed_commentary_{match_id} WHERE Team_s = '{Team}' 
        AND Event_Type = 'Shot' 
        AND half = 'First Half' 
        AND Description LIKE '%on target%';
        """
    , 'Natural Language Description':
    """
        This query is designed to find all shots on target taken by a specific team in the first half of the match.
        It does this by:
        1. Filtering the events to include only shots taken by the specified team
        2. Ensuring that those shots occurred in the first half
        3. Checking if the description of the shot indicates that it was on target
        4. Returning the time of the shot, the player who took it, and a description of the shot
        """
    , 'headers': ['Time', 'Player_s', 'Description']}, {'id': 54, 'name':
    'Stat: Hat-trick Check', 'query':
    'Did anyone take the match ball home? Show me any player who scored three or more, their team, and the goal count.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) AS goals 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' GROUP BY Player_s, Team_s 
        HAVING goals >= 3;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who scored three or more goals in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Grouping those goals by player and team
        3. Counting the number of goals for each player
        4. Returning the players who scored three or more goals, along with their team and goal count
        """
    , 'headers': ['Player_s', 'Team_s', 'goals']}, {'id': 55, 'name':
    'Stat: Last Goal of the Match', 'query':
    'Who had the final say in the scoring? Show me the details of the last goal.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Score 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Goal' 
        ORDER BY match_minute DESC, injury_time_minutes DESC, Time DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the last goal scored in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Ordering those goals by match minute, injury time, and time in descending order
        3. Limiting the results to the most recent goal scored
        4. Returning the time of the goal, the player who scored, their team, and the scoreline at that moment
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 56,
    'name': 'Stat: Player with Most Fouls', 'query':
    'Who was the biggest offender on the pitch? Show me the player who committed the most fouls and their total.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) AS fouls_committed 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Foul' AND Player_s IS NOT NULL 
        GROUP BY Player_s, Team_s 
        ORDER BY fouls_committed DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the player who committed the most fouls during the match.
        It does this by:
        1. Filtering the events to include only fouls
        2. Grouping those fouls by player and team
        3. Counting the number of fouls committed by each player
        4. Returning the player with the highest foul count, along with their team and total fouls committed
        """
    , 'headers': ['Player_s', 'Team_s', 'fouls_committed']}, {'id': 57,
    'name': 'Stat: Player with Multiple Cards', 'query':
    'Did any player lose their head? Show me anyone who got more than one card and how many they received.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) AS card_count 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type IN ('Yellow Card', 'Red Card') 
        GROUP BY Player_s, Team_s HAVING card_count > 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who received more than one card during the match.
        It does this by:
        1. Filtering the events to include only cards (yellow or red)
        2. Grouping those cards by player and team
        3. Counting the number of cards received by each player
        4. Returning the players who received more than one card, along with their team and total card count
        """
    , 'headers': ['Player_s', 'Team_s', 'card_count']}, {'id': 58, 'name':
    'Stat: Second Half Corners', 'query':
    'How many corners did {Team} get after halftime? List them all with the time and the player who took it.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_s 
        FROM parsed_commentary_{match_id} 
        WHERE Team_s = '{Team}' AND Event_Type = 'Corner' 
        AND half = 'Second Half';
        """
    , 'Natural Language Description':
    """
        This query is designed to find all corners taken by a specific team in the second half of the match.
        It does this by:
        1. Filtering the events to include only corners taken by the specified team
        2. Ensuring that those corners occurred in the second half
        3. Returning the time of each corner and the player who took it
        ---> This will give a clear overview of the team's corner-taking activity in the second half
        """
    , 'headers': ['Time', 'Player_s']}, {'id': 59, 'name':
    'Stat: Team with Most Corners', 'query':
    'Which team was earning more set pieces? Show me the team with the most corners and their total.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, COUNT(*) as corner_count 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Corner' AND Team_s IS NOT NULL 
        GROUP BY Team_s 
        ORDER BY corner_count DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the team that earned the most corners during the match.
        It does this by:
        1. Filtering the events to include only corners
        2. Grouping those corners by team
        3. Counting the number of corners for each team
        4. Returning the team with the highest corner count, along with their total corners
        """
    , 'headers': ['Team_s', 'corner_count']}, {'id': 60, 'name':
    'Stat: Team with Most Fouls', 'query':
    'Which side was putting themselves about more? Show me the team that committed the most fouls and the total number.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, COUNT(*) AS foul_count 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Foul' AND Team_s IS NOT NULL 
        GROUP BY Team_s 
        ORDER BY foul_count DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the team that committed the most fouls during the match.
        It does this by:
        1. Filtering the events to include only fouls
        2. Grouping those fouls by team
        3. Counting the number of fouls for each team
        4. Returning the team with the highest foul count, along with their total fouls
        """
    , 'headers': ['Team_s', 'foul_count']}, {'id': 61, 'name':
    'Stat: Total Injury Time Played', 'query':
    'What was the total injury time awarded across the entire match?',
    'difficulty': 'Medium', 'SQL':
    """
        SELECT SUM(max_stoppage) as total_stoppage_time 
        FROM (SELECT half, MAX(injury_time_minutes) as max_stoppage FROM parsed_commentary_{match_id} GROUP BY half);
        """
    , 'Natural Language Description':
    """
        This query is designed to calculate the total injury time awarded across the entire match.
        It does this by:
        1. Grouping the events by half to find the maximum stoppage time for each half
        2. Summing those maximum stoppage times to get the total injury time for the match
        3. Returning the total stoppage time as a single value
        """
    , 'headers': ['total_stoppage_time']}, {'id': 62, 'name':
    'Stat: Total Red Cards', 'query':
    'What was the final red card tally for the match?', 'difficulty':
    'Easy', 'SQL':
    """
        SELECT COUNT(*) 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Red Card';
        """
    , 'Natural Language Description':
    """
        This query is designed to count the total number of red cards issued during the match.
        It does this by:
        1. Filtering the events to include only red cards
        2. Counting the number of red card events
        3. Returning the total count of red cards as a single value
        """
    , 'headers': ['*']}, {'id': 63, 'name': "The '90th Minute Heroics'",
    'query':
    'Give me all the drama from the death. Show me every goal, card, and shot in the 90th minute and stoppage time.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Player_s, Team_s, Description FROM parsed_commentary_{match_id}
        WHERE match_minute >= 90 AND half = 'Second Half' AND Event_Type IN ('Goal', 'Shot', 'Yellow Card', 'Red Card')
        ORDER BY match_minute, injury_time_minutes;
        """
    , 'Natural Language Description':
    """
        This query is designed to capture all the key events that occurred in the 90th minute and stoppage time of the match.
        It does this by:
        1. Filtering the events to include only those that occurred in the second half, specifically in the 90th minute and beyond
        2. Including only goals, shots, yellow cards, and red cards
        3. Ordering those events by match minute and injury time to maintain the chronological order
        4. Returning the time, event type, player involved, team, and description of each event
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 64, 'name': "The 'Afters' Stat", 'query':
    'Did tempers flare after the final whistle? Show me any cards that were shown after the match ended.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        FinalWhistle AS (SELECT row_id FROM AllEventsWithRowID WHERE Event_Type = 'Full Time' LIMIT 1)
        SELECT aewr.Time, aewr.Player_s, aewr.Team_s, aewr.Description
        FROM AllEventsWithRowID AS aewr, FinalWhistle AS fw
        WHERE aewr.row_id > fw.row_id AND aewr.Event_Type IN ('Yellow Card', 'Red Card');
        """
    , 'Natural Language Description':
    """
        This query is designed to find any cards issued after the final whistle of the match.
        It does this by:
        1. Identifying the row ID of the final whistle event
        2. Selecting all events that occurred after the final whistle
        3. Filtering those events to include only yellow and red cards
        4. Returning the time, player involved, team, and description of each card issued after the match ended
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 65,
    'name': "The 'Aggressor's Timeline'", 'query':
    'Who was the main enforcer? For the player with the most fouls, show me a timeline of all their fouls and cards.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH TopFouler AS (SELECT Player_s FROM parsed_commentary_{match_id} WHERE Event_Type = 'Foul' AND Player_s IS NOT NULL GROUP BY Player_s ORDER BY COUNT(*) DESC LIMIT 1)
        SELECT Time, Event_Type, Description FROM parsed_commentary_{match_id}
        WHERE Player_s = (SELECT Player_s FROM TopFouler) AND Event_Type IN ('Foul', 'Yellow Card', 'Red Card') ORDER BY match_minute;
        """
    , 'Natural Language Description':
    """
        This query is designed to create a timeline of all fouls and cards for the player who committed the most fouls during the match.
        It does this by:
        1. Identifying the player with the highest foul count
        2. Filtering the events to include only those involving that player
        3. Including only fouls and cards (yellow and red)
        4. Ordering those events by match minute to create a chronological timeline
        5. Returning the time, event type, and description of each event for that player
        """
    , 'headers': ['Time', 'Event_Type', 'Description']}, {'id': 66, 'name':
    "The 'Build-up Play' Timeline", 'query':
    "Let's break down the goals. For every goal scored, show me the two actions that came right before it."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalRowIDs AS (SELECT row_id FROM AllEventsWithRowID WHERE Event_Type = 'Goal')
        SELECT p.Time, p.Event_Type, p.Player_s, p.Team_s, p.Description FROM AllEventsWithRowID p
        JOIN GoalRowIDs g ON p.row_id BETWEEN g.row_id - 2 AND g.row_id
        ORDER BY g.row_id, p.row_id;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the build-up to each goal scored in the match.
        It does this by:
        1. Assigning a row ID to each event in the match to maintain their order
        2. Identifying the row IDs of all goal events
        3. Selecting the two events that occurred immediately before each goal
        4. Joining those events with the goal events based on their row IDs
        5. Returning the time, event type, player involved, team, and description of those build-up events
        6. Ordering the results by the row ID of the goals and the row IDs of the build-up events
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 67, 'name': "The 'Busiest Player' Index", 'query':
    'Who was at the heart of everything? Show me the player with the most actions recorded in the whole match.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as total_events FROM parsed_commentary_{match_id}
        WHERE Player_s IS NOT NULL GROUP BY Player_s, Team_s ORDER BY total_events DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the player who was involved in the most actions during the match.
        It does this by:
        1. Filtering the events to include only those where a player is involved
        2. Grouping those events by player and team
        3. Counting the total number of events for each player
        4. Ordering the results by the total number of events in descending order
        5. Returning the player with the highest count, along with their team
        """
    , 'headers': ['Player_s', 'Team_s', 'total_events']}, {'id': 68, 'name':
    "The 'Calamity Sub' Stat", 'query':
    'Did any sub have a disastrous start? Show me a substitute who gave away a foul that led to a shot within 5 minutes of coming on.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH SubTimes AS (SELECT Player_In, match_minute AS sub_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution')
        SELECT f.Time, f.Player_s, f.Description FROM SubTimes st
        JOIN parsed_commentary_{match_id} f ON st.Player_In = f.Player_s
        WHERE f.Event_Type = 'Foul' AND f.match_minute BETWEEN st.sub_minute AND st.sub_minute + 5
        AND EXISTS (SELECT 1 FROM parsed_commentary_{match_id} s WHERE s.Event_Type = 'Shot' AND s.Team_s != f.Team_s AND s.match_minute BETWEEN f.match_minute AND f.match_minute + 1);
        """
    , 'Natural Language Description':
    """
        This query is designed to find substitutes who committed a foul that led to a shot within 5 minutes of being substituted in.
        It does this by:
        1. Identifying the minute a substitute player came on
        2. Joining that information with foul events to find fouls committed by substitutes
        3. Filtering those fouls to only include those that occurred within 5 minutes of the substitution
        4. Checking if there was a shot taken by the opposing team within one minute of the foul
        5. Returning the time of the foul, the player who committed it, and a description of the foul
        ---> This will help identify substitutes who had an immediate negative impact on the game
        """
    , 'headers': ['Time', 'Player_s', 'Description']}, {'id': 69, 'name':
    "The 'Captain's Example' Check", 'query':
    'How did the skipper, {Player}, fare with the ref? Show me any cards he received.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Description FROM parsed_commentary_{match_id}
        WHERE Player_s = '{Player}' 
        AND Event_Type IN ('Yellow Card', 'Red Card');
        """
    , 'Natural Language Description':
    """
        This query is designed to find any cards received by a specific player during the match.
        It does this by:
        1. Filtering the events to include only those involving the specified player
        2. Checking if the event type is either a yellow card or a red card
        3. Returning the time of the card, the type of card, and a description of the event
        ---> This will help assess the disciplinary record of the captain during the match
        """
    , 'headers': ['Time', 'Event_Type', 'Description']}, {'id': 70, 'name':
    "The 'Cautionary Tale' Foul Rate", 'query':
    "How did the first booking affect {Team}'s discipline? Show me their foul rate before that card versus their foul rate after."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH FirstCardMinute AS (SELECT MIN(match_minute) as card_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Yellow Card' AND Team_s = '{Team}')
        SELECT 'Fouls per minute before card' as metric, CAST(COUNT(*) AS REAL) / (SELECT card_minute FROM FirstCardMinute) as rate
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Foul' AND Team_s = '{Team}' AND match_minute < (SELECT card_minute FROM FirstCardMinute)
        UNION ALL
        SELECT 'Fouls per minute after card' as metric, CAST(COUNT(*) AS REAL) / (90 - (SELECT card_minute FROM FirstCardMinute)) as rate
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Foul' AND Team_s = '{Team}' AND match_minute >= (SELECT card_minute FROM FirstCardMinute);
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the foul rate of a specific team before and after their first yellow card.
        It does this by:
        1. Identifying the minute of the first yellow card for the specified team
        2. Calculating the foul rate before that card by counting fouls and dividing by the time before the card
        3. Calculating the foul rate after that card by counting fouls and dividing by the remaining time in the match
        4. Returning both rates with descriptive labels
        ---> This will help assess how the team's discipline changed after receiving their first booking
        """
    , 'headers': []}, {'id': 71, 'name': "The 'Commentator's xG'", 'query':
    "Which team created the golden opportunities? Show me all the shots the commentary called 'one-on-one' or 'point-blank'."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description FROM parsed_commentary_{match_id} WHERE Event_Type IN ('Shot', 'Goal')
        AND (Description LIKE '%one-on-one%' OR Description LIKE '%point-blank%' OR Description LIKE '%open goal%');
        """
    , 'Natural Language Description':
    """
        This query is designed to find all shots that were considered high-quality scoring opportunities by the commentary.
        It does this by:
        1. Filtering the events to include only shots and goals
        2. Checking if the description of the shot includes terms like 'one-on-one', 'point-blank', or 'open goal'
        3. Returning the time of the shot, the player who took it, their team, and a description of the shot
        ---> This will help identify the most significant scoring chances in the match according to the commentary
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 72,
    'name': "The 'Consolation Goal' Finder", 'query':
    'Were there any late, meaningless goals? Show me goals scored by a team that was already down by two or more.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalEventsWithPrevScore AS (
            SELECT Time, Player_s, Team_s, Score, LAG(Score, 1, '0 - 0') OVER (ORDER BY row_id) as score_before_this_goal
            FROM AllEventsWithRowID WHERE Event_Type = 'Goal'
        )
        SELECT Time, Player_s, Team_s, Score FROM GoalEventsWithPrevScore
        WHERE (
            SELECT
                (CASE
                    WHEN Team_s = (SELECT T.Team_s FROM parsed_commentary_{match_id} T WHERE T.Team_s IS NOT NULL ORDER BY Time LIMIT 1)
                    THEN CAST(SUBSTR(score_before_this_goal, 1, INSTR(score_before_this_goal, ' - ') - 1) AS INTEGER) - CAST(SUBSTR(score_before_this_goal, INSTR(score_before_this_goal, ' - ') + 3) AS INTEGER)
                    ELSE CAST(SUBSTR(score_before_this_goal, INSTR(score_before_this_goal, ' - ') + 3) AS INTEGER) - CAST(SUBSTR(score_before_this_goal, 1, INSTR(score_before_this_goal, ' - ') - 1) AS INTEGER)
                END) <= -2
        );
        """
    , 'Natural Language Description':
    """
        This query is designed to find goals scored by a team that was already trailing by two or more goals.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying goal events and capturing the score before each goal
        3. Calculating the score difference before each goal
        4. Filtering those goals to include only those where the scoring team was down by two or more goals
        5. Returning the time of the goal, the player who scored, their team, and the score at that moment
        ---> This will help identify late consolation goals that had little impact on the match outcome
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 73,
    'name': "The 'Desperation' Sub", 'query':
    'Which manager made the last desperate change? Show me the details of the final sub of the game.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Team_s, Player_In, Player_Out FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution' ORDER BY match_minute DESC, injury_time_minutes DESC, Time DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the last substitution made in the match.
        It does this by:
        1. Filtering the events to include only substitutions
        2. Ordering those substitutions by match minute, injury time, and time in descending order
        3. Limiting the results to the most recent substitution
        4. Returning the time of the substitution, the team making the change, the player coming in, and the player going out
        ---> This will help identify the final tactical move made by the manager in the match
        """
    , 'headers': ['Time', 'Team_s', 'Player_In', 'Player_Out']}, {'id': 74,
    'name': "The 'Dirty Tackle' Log", 'query':
    "Show me the really bad challenges. List any fouls the commentary called 'nasty', 'late', or 'reckless'."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description FROM parsed_commentary_{match_id} WHERE Event_Type = 'Foul' AND (Description LIKE '%nasty%' OR Description LIKE '%late%' OR Description LIKE '%reckless%');
        """
    , 'Natural Language Description':
    """
        This query is designed to find fouls that were described as particularly bad or reckless by the commentary.
        It does this by:
        1. Filtering the events to include only fouls
        2. Checking if the description of the foul includes terms like 'nasty', 'late', or 'reckless'
        3. Returning the time of the foul, the player who committed it, their team, and a description of the foul
        ---> This will help identify the most egregious fouls in the match according to the commentary
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 75,
    'name': "The 'Discipline Decay' Analysis", 'query':
    'Show me the card count for each team, broken down by half, so we can see if things got worse after the break.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, SUM(CASE WHEN half = 'First Half' THEN 1 ELSE 0 END) as first_half_cards, SUM(CASE WHEN half = 'Second Half' THEN 1 ELSE 0 END) as second_half_cards
        FROM parsed_commentary_{match_id} WHERE Event_Type IN ('Yellow Card', 'Red Card') AND Team_s IS NOT NULL GROUP BY Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the card count for each team, broken down by half.
        It does this by:
        1. Filtering the events to include only yellow and red cards
        2. Grouping those cards by team
        3. Summing the number of cards for each team in both the first and second halves
        4. Returning the team name, the count of cards in the first half, and the count of cards in the second half
        ---> This will help assess whether a team's discipline worsened after halftime
        """
    , 'headers': ['Team_s', 'first_half_cards', 'second_half_cards']}, {
    'id': 76, 'name': "The 'Early Hook' Tactical Sub", 'query':
    "Who was the first player hooked for tactical reasons? Show me the first sub who wasn't injured in the five minutes prior."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT s.Time, s.Player_Out, s.Team_s FROM parsed_commentary_{match_id} s
        WHERE s.Event_Type = 'Substitution' AND s.Player_Out IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} i WHERE i.Event_Type = 'Injury' AND i.Player_s = s.Player_Out AND i.match_minute BETWEEN s.match_minute - 5 AND s.match_minute
        ) ORDER BY s.match_minute ASC, s.Time ASC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first substitution made for tactical reasons, excluding those due to injury.
        It does this by:
        1. Filtering the events to include only substitutions where a player was substituted out
        2. Ensuring that the player substituted out was not injured in the five minutes prior to the substitution
        3. Ordering those substitutions by match minute and time in ascending order
        4. Limiting the results to the first substitution that meets these criteria
        5. Returning the time of the substitution, the player who was substituted out, and their team
        ---> This will help identify early tactical changes made by the manager that were not due to injury
        """
    , 'headers': ['Time', 'Player_Out', 'Team_s']}, {'id': 77, 'name':
    "The 'Equalizer' Events", 'query':
    'Show me all the goals that levelled the scores. I need a list of every single equalizer.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Goals AS (SELECT * FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal'),
        OrderedGoals AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute ASC) AS goal_order FROM Goals),
        CumulativeScore AS (SELECT goal_order, match_minute, Team_s, Player_s, Score, Time,
        SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 0) THEN 1 ELSE 0 END)
            OVER (ORDER BY goal_order) AS team1_goals,
        SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END)
            OVER (ORDER BY goal_order) AS team2_goals
        FROM OrderedGoals),
        TiedMoments AS (SELECT 0 AS goal_order UNION SELECT goal_order FROM CumulativeScore WHERE team1_goals = team2_goals)
        SELECT Time, Player_s, Team_s, Score
        FROM CumulativeScore cs
        JOIN TiedMoments tm ON cs.goal_order = tm.goal_order
        ORDER BY cs.goal_order;
        """
    , 'Natural Language Description':
    """
        This query is designed to find all goals that equalized the score in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Checking if the score after the goal was equal (i.e., both teams had the same number of goals)
        3. Returning the time of the goal, the player who scored, their team, and the score at that moment
        ---> This will help identify all moments in the match where the score was leveled by a goal
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 78,
    'name': "The 'Final 10 Frenzy' Subs", 'query':
    'Who rolled the dice at the end? Show the number of subs each team made in the last ten minutes of normal time.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, COUNT(*) as late_substitutions
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution' AND match_minute >= 80 AND Team_s IS NOT NULL GROUP BY Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to count the number of substitutions made by each team in the last ten minutes of normal time.
        It does this by:
        1. Filtering the events to include only substitutions made in the last ten minutes of normal time (from minute 80 onwards)
        2. Grouping those substitutions by team
        3. Counting the number of substitutions for each team
        4. Returning the team name and the count of late substitutions
        ---> This will help identify which teams made tactical changes in the closing stages of the match
        """
    , 'headers': ['Team_s', 'late_substitutions']}, {'id': 79, 'name':
    "The 'Foul Magnet' Award", 'query':
    'Who was on the receiving end all day? Show me the player who was fouled the most.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as fouls_won FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Foul' AND Description LIKE '%wins a free kick%'
        GROUP BY Player_s, Team_s ORDER BY fouls_won DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the player who was fouled the most during the match.
        It does this by:
        1. Filtering the events to include only fouls where the player was fouled (i.e., the description indicates they won a free kick)
        2. Grouping those fouls by player and team
        3. Counting the number of times each player was fouled
        4. Ordering the results by the count of fouls won in descending order
        5. Returning the player with the highest count, along with their team
        ---> This will help identify the player who was targeted the most by the opposition's defenders
        """
    , 'headers': ['Player_s', 'Team_s', 'fouls_won']}, {'id': 80, 'name':
    "The 'Game Reset' Stat", 'query':
    'How did the game change after the red card? Show me the very next major event after the sending-off.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        RedCardTime AS (SELECT row_id FROM AllEventsWithRowID WHERE Event_Type = 'Red Card' ORDER BY row_id DESC LIMIT 1)
        SELECT aewr.Time, aewr.Event_Type, aewr.Player_s, aewr.Team_s
        FROM AllEventsWithRowID AS aewr, RedCardTime AS rct
        WHERE aewr.row_id > rct.row_id AND aewr.Event_Type IN ('Goal', 'Shot', 'Corner', 'Yellow Card', 'Red Card')
        ORDER BY aewr.row_id ASC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first major event that occurred after a red card was issued in the match.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying the row ID of the last red card event
        3. Selecting the first event that occurred after the red card
        4. Filtering those events to include only significant actions like goals, shots, corners, yellow cards, and red cards
        5. Returning the time of the event, the type of event, the player involved, and their team
        ---> This will help analyze how the match dynamics changed immediately after a player was sent off
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s']}, {'id': 81,
    'name': "The 'Gegenpress' Foul", 'query':
    "Who was doing the pressing from the front? Show me the player who committed the most fouls in the opposition's half."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as high_fouls FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Foul' AND Description LIKE '%attacking half%'
        GROUP BY Player_s, Team_s ORDER BY high_fouls DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the player who committed the most fouls in the opposition's half of the pitch.
        It does this by:
        1. Filtering the events to include only fouls that occurred in the attacking half (indicated by the description)
        2. Grouping those fouls by player and team
        3. Counting the number of fouls for each player
        4. Ordering the results by the count of fouls in descending order
        5. Returning the player with the highest count, along with their team
        ---> This will help identify the player who was most aggressive in pressing the opposition and winning the ball back in their half
        """
    , 'headers': ['Player_s', 'Team_s', 'high_fouls']}, {'id': 82, 'name':
    "The 'Go-Ahead Goal' Specialist", 'query':
    'Who was the player for the big moment? Show me all the goals that put a team ahead when the scores were level.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Goals AS (SELECT * FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal'), 
        FinalScore AS (SELECT Team_s, COUNT(Team_s) AS total_goals FROM Goals GROUP BY Team_s),
        OrderedGoals AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute ASC) AS goal_order FROM Goals),
        CumulativeScore AS (SELECT 
        goal_order, 
        match_minute, 
        Team_s, 
        Player_s, 
        Score, 
        Time,
        SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 0) THEN 1 ELSE 0 END)
            OVER (ORDER BY goal_order) AS team1_goals,
        SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END)
            OVER (ORDER BY goal_order) AS team2_goals
        FROM OrderedGoals),
        TiedMoments AS (SELECT 0 AS goal_order UNION SELECT goal_order FROM CumulativeScore WHERE team1_goals = team2_goals),
        NextGoals AS (SELECT MIN(cs.goal_order) AS goal_order_after_tie FROM TiedMoments tm JOIN CumulativeScore cs ON cs.goal_order > tm.goal_order GROUP BY tm.goal_order),
        Final AS (SELECT cs.* FROM CumulativeScore cs JOIN NextGoals ng ON cs.goal_order = ng.goal_order_after_tie)
        SELECT Time, Player_s, Team_s, Score
        FROM Final
        ORDER BY goal_order;
        """
    , 'Natural Language Description':
    """"
        The premise of this query is to find all the players who broke the deadlock (gave either team the lead) and when they scored.
        To do this, this query uses the following steps:
        1. Find all the goals
        2. Determine when the Match was Tied
        3. Find the Goal immediately after each Tie and return that
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 83,
    'name': "The 'Goal & Assist' Combo (Proxy)", 'query':
    'Who set up the goals? For each scorer, show me the player from their team who made the action right before.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalEvents AS (SELECT row_id, Team_s, Player_s as goalscorer FROM AllEventsWithRowID WHERE Event_Type = 'Goal')
        SELECT g.goalscorer, p.Player_s as provider, p.Event_Type as preceding_event FROM GoalEvents g
        JOIN AllEventsWithRowID p ON p.row_id = g.row_id - 1
        WHERE p.Team_s = g.Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the player who assisted each goal scored in the match.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying goal events and capturing the team and player who scored
        3. Joining those goal events with the previous event to find the player who provided the assist
        4. Filtering to ensure the assist came from the same team as the scorer
        5. Returning the goalscorer, the player who assisted them, and the type of event that preceded the goal
        ---> This will help identify the key playmakers who contributed to the goals scored in the match
        """
    , 'headers': ['goalscorer', 'provider', 'preceding_event']}, {'id': 84,
    'name': "The 'Goal from Nothing' Stat", 'query':
    "Any moments of individual brilliance? Show me goals where the action before wasn't a pass, cross, or shot."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalEvents AS (SELECT row_id, Player_s, Team_s, Score, Description FROM AllEventsWithRowID WHERE Event_Type = 'Goal')
        SELECT g.Player_s, g.Team_s, g.Score, g.Description FROM GoalEvents g
        JOIN AllEventsWithRowID p ON p.row_id = g.row_id - 1
        WHERE p.Event_Type NOT IN ('Shot', 'Pass', 'Cross', 'Corner', 'Free-kick');
        """
    , 'Natural Language Description':
    """
        This query is designed to find goals that were scored following an event that was not a typical build-up play action like a pass, cross, or shot.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying goal events and capturing the player, team, score, and description of the goal
        3. Joining those goal events with the previous event to check what preceded the goal
        4. Filtering to ensure the preceding event was not a shot, pass, cross, corner, or free-kick
        5. Returning the player who scored, their team, the score at that moment, and a description of the goal
        ---> This will help identify moments of individual brilliance where a player scored without a typical assist or build-up play
        """
    , 'headers': ['Player_s', 'Team_s', 'Score', 'Description']}, {'id': 85,
    'name': "The 'Header Specialist' Goal", 'query':
    'For every headed goal, what was the delivery? Show me the event that happened right before any goal scored with a header.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        HeaderGoals AS (
            SELECT Time, Player_s, Team_s, row_id,
            LAG(Event_Type, 1) OVER (ORDER BY row_id) as preceding_event_type,
            LAG(Player_s, 1) OVER (ORDER BY row_id) as preceding_player
            FROM AllEventsWithRowID WHERE Event_Type = 'Goal' AND Description LIKE '%header%'
        )
        SELECT Player_s, Team_s, preceding_event_type, preceding_player FROM HeaderGoals;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the event that immediately preceded any headed goal scored in the match.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying goal events that were scored with a header
        3. Using the LAG function to retrieve the type of event and player involved in the event that occurred right before each headed goal
        4. Returning the player who scored the headed goal, their team, the type of preceding event, and the player involved in that event
        ---> This will help analyze the build-up to headed goals and identify key players involved in those moments
        """
    , 'headers': ['Player_s', 'Team_s', 'preceding_event_type',
    'preceding_player']}, {'id': 86, 'name': "The 'Heated Rivalry' Index",
    'query':
    'When did tempers flare the most? Show me the two fouls that happened closest together in time.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        FoulTimes AS (SELECT row_id, match_minute, LAG(row_id, 1) OVER (ORDER BY row_id) as prev_foul_row_id, (match_minute - LAG(match_minute, 1, -99) OVER (ORDER BY row_id)) as gap FROM AllEventsWithRowID WHERE Event_Type = 'Foul'),
        MinGap AS (SELECT MIN(gap) as min_gap FROM FoulTimes WHERE gap >= 0)
        SELECT p.Time, p.Event_Type, p.Player_s, p.Team_s, p.Description FROM AllEventsWithRowID p JOIN FoulTimes ft ON p.row_id = ft.row_id OR p.row_id = ft.prev_foul_row_id WHERE ft.gap = (SELECT min_gap FROM MinGap);
        """
    , 'Natural Language Description':
    """
        This query is designed to find the two fouls that occurred closest together in time during the match.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Filtering the events to include only fouls
        3. Calculating the time gap between each foul and the previous one
        4. Finding the minimum gap between fouls
        5. Selecting the details of the two fouls that had the minimum time gap
        6. Returning the time, event type, player involved, team, and description of those fouls
        ---> This will help identify moments of heightened tension in the match where players were particularly aggressive
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 87, 'name': "The 'Hot-Headed Sub' Card", 'query':
    'Which substitute got themselves into trouble the fastest? Show me the player and how many minutes it took for them to get booked after coming on.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH SubTimes AS (SELECT Player_In, match_minute AS sub_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution' AND Player_In IS NOT NULL),
        CardTimes AS (SELECT Player_s, MIN(match_minute) AS card_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Yellow Card' GROUP BY Player_s)
        SELECT st.Player_In, ct.card_minute - st.sub_minute AS minutes_to_card FROM SubTimes st JOIN CardTimes ct ON st.Player_In = ct.Player_s
        WHERE ct.card_minute >= st.sub_minute ORDER BY minutes_to_card ASC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the substitute player who received a yellow card the quickest after being substituted in.
        It does this by:
        1. Identifying the minute each substitute player came on
        2. Finding the minute each player received their first yellow card
        3. Calculating the difference in minutes between the substitution and the yellow card
        4. Filtering to include only those substitutes who received a card after coming on
        5. Returning the substitute player and the time it took them to receive a card
        ---> This will help identify substitutes who were immediately involved in aggressive play or misconduct after entering the match
        """
    , 'headers': ['Player_In', 'minutes_to_card']}, {'id': 88, 'name':
    "The 'Impact Sub's' First Action", 'query':
    'How quickly did subs get involved? For each one, show me their first action and how long it took them to do it.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH SubEvents AS (SELECT Player_In, match_minute as sub_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution' AND Player_In IS NOT NULL)
        SELECT se.Player_In,
          (SELECT pa.Event_Type FROM parsed_commentary_{match_id} pa WHERE pa.Event_Type != 'Substitution' AND pa.Player_s = se.Player_In AND pa.match_minute >= se.sub_minute ORDER BY pa.match_minute, pa.Time ASC LIMIT 1) as first_action,
          (SELECT MIN(pa.match_minute) FROM parsed_commentary_{match_id} pa WHERE pa.Player_s = se.Player_In AND pa.match_minute >= se.sub_minute) - se.sub_minute as minutes_to_first_action
        FROM SubEvents se;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first action taken by each substitute player after they were brought on.
        It does this by:
        1. Identifying the minute each substitute player came on
        2. Finding the first action (event type) that each substitute player took after their substitution
        3. Calculating the time it took for each substitute to take their first action after coming on
        4. Returning the substitute player, their first action, and the time taken to perform that action
        ---> This will help assess how quickly substitutes were able to make an impact on the match after being introduced
        """
    , 'headers': ['Player_In', 'first_action', 'minutes_to_first_action']},
    {'id': 89, 'name': "The 'Injury Prone' Half", 'query':
    'Which half was more brutal? Show a count of injuries for the first half versus the second.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, COUNT(*) as injury_count FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Injury' GROUP BY half ORDER BY injury_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the number of injuries that occurred in each half of the match.
        It does this by:
        1. Filtering the events to include only injuries
        2. Grouping those injuries by half (first or second)
        3. Counting the number of injuries in each half
        4. Ordering the results by the count of injuries in descending order
        5. Returning the half and the corresponding injury count
        ---> This will help identify which half of the match was more physically demanding and resulted in more injuries
        """
    , 'headers': ['half', 'injury_count']}, {'id': 90, 'name':
    "The 'Keeper Sweeper' Action", 'query':
    "Was the keeper for {Team} playing off his line? Show me any of his actions described as 'outside of his area'."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Description 
        FROM parsed_commentary_{match_id} 
        WHERE Team_s = '{Team}' 
        AND Event_Type = 'Save' 
        AND Description LIKE '%outside%';
        """
    , 'Natural Language Description':
    """
        This query is designed to find actions taken by the goalkeeper of a specific team that were described as being outside of their area.
        It does this by:
        1. Filtering the events to include only those related to the goalkeeper's actions
        2. Checking if the description of the action includes terms like 'outside of his area'
        3. Ensuring the action belongs to the specified team
        4. Returning the time of the action and the description of what the goalkeeper did
        ---> This will help analyze the goalkeeper's involvement in play beyond their usual duties within the penalty area, indicating a more proactive or aggressive role in the match
        """
    , 'headers': ['Time', 'Description']}, {'id': 91, 'name':
    "The 'Last Chance Saloon' Sub", 'query':
    'Who was the final throw of the dice? Show me the last sub of the match and how much time was left.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Player_In, Team_s, 90 - match_minute as minutes_left FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Substitution' ORDER BY match_minute DESC, injury_time_minutes DESC, Time DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the last substitution made in the match and how much time was left when it occurred.
        It does this by:
        1. Filtering the events to include only substitutions
        2. Ordering those substitutions by match minute, injury time, and time in descending order
        3. Limiting the results to the most recent substitution
        4. Calculating how many minutes were left in the match at the time of the substitution
        5. Returning the time of the substitution, the player who came in, their team, and the minutes left
        ---> This will help identify the final tactical move made by the manager in the match, especially if it was a last-ditch effort to change the outcome
        """
    , 'headers': ['Time', 'Player_In', 'Team_s', 'minutes_left']}, {'id': 
    92, 'name': "The 'Last-Gasp Defender' Stat", 'query':
    'In added time, who was the busiest defender? Show the player and their count of tackles, blocks, and clearances.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as defensive_actions FROM parsed_commentary_{match_id}
        WHERE half = 'Second Half' AND injury_time_minutes > 0 AND (Event_Type = 'Tackle' OR Description LIKE '%clearance%' OR Description LIKE '%block%') AND Player_s IS NOT NULL
        GROUP BY Player_s, Team_s ORDER BY defensive_actions DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the busiest defender in added time of the second half.
        It does this by:
        1. Filtering the events to include only those in the second half with added time
        2. Checking for defensive actions such as tackles, clearances, and blocks
        3. Grouping those actions by player and team
        4. Counting the number of defensive actions for each player
        5. Ordering the results by the count of defensive actions in descending order
        6. Returning the player, their team, and the count of defensive actions
        ---> This will help identify which defender was most active in trying to secure the result during the critical moments of added time
        """
    , 'headers': ['Player_s', 'Team_s', 'defensive_actions']}, {'id': 93,
    'name': "The 'Lead Durability' Test", 'query':
    'When {Team} got their noses in front, how long did they hold on? Show me how many minutes their lead lasted.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GoalScores AS (
            SELECT match_minute, Team_s,
            (SELECT T.Team_s FROM AllEventsWithRowID T WHERE T.Team_s IS NOT NULL ORDER BY row_id LIMIT 1) as team1_name,
            SUM(CASE WHEN Team_s = (SELECT T.Team_s FROM AllEventsWithRowID T WHERE T.Team_s IS NOT NULL ORDER BY row_id LIMIT 1) THEN 1 ELSE 0 END) OVER (ORDER BY row_id) as team1_score,
            SUM(CASE WHEN Team_s != (SELECT T.Team_s FROM AllEventsWithRowID T WHERE T.Team_s IS NOT NULL ORDER BY row_id LIMIT 1) THEN 1 ELSE 0 END) OVER (ORDER BY row_id) as team2_score
            FROM AllEventsWithRowID WHERE Event_Type = 'Goal'
        ), LeadTime AS (
            SELECT MIN(match_minute) AS minute_took_lead FROM GoalScores
            WHERE ('{Team}' = team1_name AND team1_score > team2_score AND (team1_score - 1) <= team2_score) OR ('{Team}' != team1_name AND team2_score > team1_score AND (team2_score - 1) <= team1_score)
        ), EqualizerTime AS (
            SELECT MIN(match_minute) AS minute_conceded_equalizer FROM GoalScores WHERE match_minute > (SELECT minute_took_lead FROM LeadTime) AND team1_score = team2_score
        )
        SELECT COALESCE((SELECT minute_conceded_equalizer FROM EqualizerTime), 90) - (SELECT minute_took_lead FROM LeadTime) AS minutes_lead_lasted;
        """
    , 'Natural Language Description':
    """
        This query is designed to find out how long a team held their lead after scoring.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying goal events and calculating the cumulative score for each team
        3. Finding the minute when the specified team took the lead
        4. Checking for the first equalizer scored by the opposing team after the lead was taken
        5. Calculating the difference in minutes between when the lead was taken and when the equalizer was scored
        6. Returning the total minutes the lead lasted, or 90 if no equalizer was scored
        ---> This will help assess the durability of a team's lead and how effectively they managed it until the end of the match
        """
    , 'headers': ['minutes_lead_lasted']}, {'id': 94, 'name':
    "The 'Long-Range Threat' Team", 'query':
    'Who was trying their luck from distance? Show which team had more shots from outside the box.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Team_s, COUNT(*) as long_range_shots FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Shot' AND (Description LIKE '%outside the box%' OR Description LIKE '%from distance%')
        GROUP BY Team_s ORDER BY long_range_shots DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to find out which team attempted the most shots from outside the penalty area.
        It does this by:
        1. Filtering the events to include only shots
        2. Checking if the description of the shot indicates it was taken from outside the box or from distance
        3. Grouping those shots by team
        4. Counting the number of long-range shots for each team
        5. Ordering the results by the count of long-range shots in descending order
        6. Returning the team name and the count of long-range shots
        ---> This will help identify which team was more adventurous in their attacking play, looking for goals from outside the box
        """
    , 'headers': ['Team_s', 'long_range_shots']}, {'id': 95, 'name':
    "The 'Loss of Composure' Index", 'query':
    'After {Team} conceded, who was the first of their players to give away a foul?'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH ConcededTime AS (SELECT MIN(match_minute) as minute_conceded FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal' AND Team_s != '{Team}')
        SELECT f.Time, f.Player_s, f.Description FROM parsed_commentary_{match_id} f, ConcededTime ct
        WHERE f.Team_s = '{Team}' AND f.Event_Type = 'Foul' AND f.match_minute > ct.minute_conceded
        ORDER BY f.match_minute ASC, f.Time ASC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first foul committed by a player from a specific team after they conceded a goal.
        It does this by:
        1. Identifying the minute when the specified team conceded a goal
        2. Filtering the events to include only fouls committed by players from that team
        3. Checking if the foul occurred after the team conceded
        4. Ordering the results by match minute and time to find the earliest foul after conceding
        5. Returning the time of the foul, the player who committed it, and a description of the foul
        ---> This will help analyze the immediate reaction of the team after conceding a goal, particularly in terms of discipline and composure
        """
    , 'headers': ['Time', 'Player_s', 'Description']}, {'id': 96, 'name':
    "The 'Manager's Plan B' First Sub", 'query':
    'What was the first roll of the dice from each manager? Show me the first sub for each team.'
    , 'difficulty': 'Hard', 'SQL':
    """
        SELECT Team_s, Time, Player_In, Player_Out FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY Team_s ORDER BY match_minute, injury_time_minutes, Time) as sub_rank
            FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution'
        ) WHERE sub_rank = 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the first substitution made by each team in the match.
        It does this by:
        1. Filtering the events to include only substitutions
        2. Assigning a rank to each substitution for each team based on the order they occurred in the match
        3. Selecting only the first substitution for each team
        4. Returning the team name, time of the substitution, player who came in, and player who went out
        ---> This will help identify the initial tactical changes made by each manager in the match, particularly in response to the flow of play or injuries
        """
    , 'headers': ['Team_s', 'Time', 'Player_In', 'Player_Out']}, {'id': 97,
    'name': "The 'One-Man Wrecking Crew'", 'query':
    'Was there an all-action player? Show me anyone who scored, committed a foul, and won a foul, all in the same half.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT p1.Player_s FROM parsed_commentary_{match_id} p1
        WHERE p1.Event_Type = 'Goal' AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} p2
            WHERE p2.Player_s = p1.Player_s AND p2.half = p1.half AND p2.Event_Type = 'Foul' AND p2.Description NOT LIKE '%wins a free kick%'
        ) AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} p3
            WHERE p3.Player_s = p1.Player_s AND p3.half = p1.half AND p3.Event_Type = 'Foul' AND p3.Description LIKE '%wins a free kick%'
        ) GROUP BY p1.Player_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who had a significant all-round performance in a single half of the match.
        It does this by:
        1. Filtering the events to include only goals scored by players
        2. Checking if the same player committed a foul in that half (excluding fouls where they won a free kick)
        3. Checking if the same player also won a foul in that half (indicating they were fouled)
        4. Grouping the results by player to ensure uniqueness
        5. Returning the names of players who met all these criteria
        ---> This will help identify players who were not only involved in scoring but also actively engaged in the physical aspects of the game, contributing to both attacking and defensive phases
        """
    , 'headers': ['Player_s']}, {'id': 98, 'name':
    "The 'Panic Stations' Double Sub", 'query':
    'Show me when a manager hit the panic button. Any instances of a team making two subs in a five-minute window?'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH SubsWithRowID AS (SELECT Time, Player_In, Team_s, match_minute, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution')
        SELECT s1.Time as First_Sub_Time, s1.Player_In as First_Player_In, s1.Team_s, s2.Time as Second_Sub_Time, s2.Player_In as Second_Player_In
        FROM SubsWithRowID s1 JOIN SubsWithRowID s2 ON s1.Team_s = s2.Team_s AND s2.row_id > s1.row_id WHERE s2.match_minute - s1.match_minute <= 5;
        """
    , 'Natural Language Description':
    """
        This query is designed to find instances where a team made two substitutions within a five-minute window.
        It does this by:
        1. Assigning a row ID to each substitution event to maintain their order
        2. Joining the substitutions table with itself to find pairs of substitutions made by the same team
        3. Filtering those pairs to include only those where the second substitution occurred within five minutes of the first
        4. Returning the time of the first substitution, the player who came in, the team, the time of the second substitution, and the player who came in for that substitution
        ---> This will help identify moments when managers felt the need to make quick changes, possibly in response to a tactical shift or an urgent need to change the game's dynamics
        """
    , 'headers': ['First_Sub_Time', 'First_Player_In', 'Team_s',
    'Second_Sub_Time', 'Second_Player_In']}, {'id': 99, 'name':
    "The 'Poacher vs. Worker' Index", 'query':
    'For every player who scored, were they just a goal threat or involved all over? Show their goal count next to a count of their other actions.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, SUM(CASE WHEN Event_Type = 'Goal' THEN 1 ELSE 0 END) as goals, SUM(CASE WHEN Event_Type != 'Goal' THEN 1 ELSE 0 END) as other_actions
        FROM parsed_commentary_{match_id} WHERE Player_s IN (SELECT DISTINCT Player_s FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal')
        GROUP BY Player_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the contributions of players who scored goals in the match.
        It does this by:
        1. Filtering the events to include only those involving players who scored goals
        2. Counting the number of goals scored by each player
        3. Counting the number of other actions (events that are not goals) for each player
        4. Grouping the results by player to ensure uniqueness
        5. Returning the player's name, their goal count, and their count of other actions
        ---> This will help differentiate between players who are primarily goal scorers and those who contribute more broadly to the team's play, providing insight into their overall impact on the match
        """
    , 'headers': ['Player_s', 'goals', 'other_actions']}, {'id': 100,
    'name': "The 'Possession Without Penetration' Index", 'query':
    "All possession and no punch. Show me the timeline of {Team}'s longest spell with the ball that didn't create a single shot."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER(ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        Streaks AS (
            SELECT *, (row_id - ROW_NUMBER() OVER (PARTITION BY Team_s ORDER BY row_id)) as streak_id
            FROM AllEventsWithRowID WHERE Team_s IS NOT NULL
        ), StreakSummary AS (
            SELECT Team_s, streak_id, COUNT(*) as streak_length, MIN(row_id) as start_row_id, MAX(row_id) as end_row_id, SUM(CASE WHEN Event_Type IN ('Shot', 'Goal') THEN 1 ELSE 0 END) as shots_in_streak
            FROM Streaks GROUP BY Team_s, streak_id
        ), LongestShotless AS (
            SELECT start_row_id, end_row_id FROM StreakSummary WHERE Team_s = '{Team}' AND shots_in_streak = 0 ORDER BY streak_length DESC LIMIT 1
        )
        SELECT p.Time, p.Event_Type, p.Player_s, p.Team_s, p.Description FROM AllEventsWithRowID p JOIN LongestShotless l ON p.row_id BETWEEN l.start_row_id AND l.end_row_id ORDER BY p.row_id;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the longest period of possession for a specific team that did not result in any shots.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying streaks of possession events for each team
        3. Summarizing those streaks to count their length, determine the start and end row IDs, and check if any shots were taken during that streak
        4. Filtering to find the longest streak of possession for the specified team that did not include any shots
        5. Returning the events that occurred during that streak, including the time, event type, player involved, team, and description
        ---> This will help analyze periods of possession where the team maintained control of the ball without creating any goal-scoring opportunities, indicating a lack of penetration in their play
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 101, 'name': "The 'Post-Goal Momentum Swing'", 'query':
    'After each goal, who took control? Show which team had more events in the five minutes that followed.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH GoalMinutes AS (SELECT DISTINCT match_minute as goal_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal')
        SELECT gm.goal_minute as post_goal_period_start, p.Team_s, COUNT(*) as event_count
        FROM parsed_commentary_{match_id} p, GoalMinutes gm
        WHERE p.match_minute > gm.goal_minute AND p.match_minute <= gm.goal_minute + 5 AND p.Team_s IS NOT NULL
        GROUP BY gm.goal_minute, p.Team_s ORDER BY gm.goal_minute, event_count DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the momentum shift after each goal scored in the match.
        It does this by:
        1. Identifying the minutes when goals were scored
        2. Counting the number of events for each team in the five minutes following each goal
        3. Grouping the results by the goal minute and team
        4. Returning the start of the post-goal period, the team involved, and the count of events they had during that period
        ---> This will help assess which team capitalized on the momentum after scoring, indicating their ability to control the game immediately following a goal
        """
    , 'headers': ['post_goal_period_start', 'Team_s', 'event_count']}, {
    'id': 102, 'name': "The 'Pressure Cooker' Foul", 'query':
    'Show me the fouls that were immediately punished. List any foul that led to a goal from a free-kick or penalty in the same minute.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT f.Time, f.Player_s, f.Team_s, f.Description
        FROM parsed_commentary_{match_id} f WHERE f.Event_Type = 'Foul' AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} g
            WHERE g.Event_Type = 'Goal' AND g.Team_s != f.Team_s AND g.match_minute = f.match_minute AND (g.Description LIKE '%free-kick%' OR g.Description LIKE '%penalty%')
        );
        """
    , 'Natural Language Description':
    """
        This query is designed to find fouls that directly led to a goal being scored in the same minute, specifically from a free-kick or penalty.
        It does this by:
        1. Filtering the events to include only fouls
        2. Checking if there is a corresponding goal event in the same minute that was scored from a free-kick or penalty
        3. Ensuring the goal was scored by the opposing team
        4. Returning the time of the foul, the player who committed it, their team, and a description of the foul
        ---> This will help identify critical moments in the match where a foul led to an immediate scoring opportunity for the opposition, highlighting the impact of defensive errors
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 103,
    'name': "The 'Professional Foul' Log", 'query':
    "Show me the 'dark arts'. List any fouls that the commentary called 'cynical' or 'professional'."
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Time, Player_s, Team_s, Description FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Foul' AND (Description LIKE '%cynical%' OR Description LIKE '%professional%');
        """
    , 'Natural Language Description':
    """
        This query is designed to identify fouls that were described in the commentary as 'cynical' or 'professional'.
        It does this by:
        1. Filtering the events to include only fouls
        2. Checking the description of each foul for keywords like 'cynical' or 'professional'
        3. Returning the time of the foul, the player who committed it, their team, and a description of the foul
        ---> This will help analyze instances where players intentionally committed fouls to disrupt the flow of play or prevent a scoring opportunity, 
        often referred to as 'dark arts' in football
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Description']}, {'id': 104,
    'name': "The 'Quickfire Double' Brace", 'query':
    'Did any player hit them with a quick one-two? Show me anyone who scored twice in 15 minutes or less.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH PlayerGoals AS (
            SELECT Player_s, match_minute, LAG(match_minute, 1) OVER (PARTITION BY Player_s ORDER BY match_minute, Time) as prev_goal_minute
            FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal' AND Player_s IS NOT NULL
        )
        SELECT Player_s, prev_goal_minute, match_minute 
        FROM PlayerGoals 
        WHERE match_minute - prev_goal_minute <= 15;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who scored two goals within a 15-minute window.
        It does this by:
        1. Identifying goal events and capturing the minute each goal was scored
        2. Using a window function to find the previous goal scored by the same player
        3. Calculating the time difference between the current goal and the previous goal
        4. Filtering the results to include only those players who scored two goals within 15 minutes of each other
        5. Returning the player's name, the minute of the previous goal, and the minute of the current goal
        ---> This will help identify players who had a particularly explosive scoring performance, showcasing their ability to find the net in quick succession
        """
    , 'headers': ['Player_s', 'prev_goal_minute', 'match_minute']}, {'id': 
    105, 'name': "The 'Referee's Patience' Index", 'query':
    'Did the ref let more go as the game wore on, or less? Show a simple count of fouls in the first half vs the second.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT half, COUNT(*) as foul_count 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Foul' 
        GROUP BY half;
        """
    , 'Natural Language Description':
    """
        This query is designed to compare the number of fouls committed in each half of the match.
        It does this by:
        1. Filtering the events to include only fouls
        2. Grouping those fouls by half (first or second)
        3. Counting the number of fouls in each half
        4. Returning the half and the corresponding foul count
        ---> This will help analyze the referee's consistency in officiating throughout the match, 
        indicating whether they were more lenient or strict in the first half compared to the second
        """
    , 'headers': ['half', 'foul_count']}, {'id': 106, 'name':
    "The 'Scoring Method' Breakdown", 'query':
    'How were the goals scored? Give me a simple breakdown: how many headers versus how many with the feet.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT
            SUM(CASE WHEN Description LIKE '%header%' THEN 1 ELSE 0 END) as header_goals,
            SUM(CASE WHEN Description NOT LIKE '%header%' THEN 1 ELSE 0 END) as foot_or_other_goals
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal';
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the method of scoring goals in the match.
        It does this by:
        1. Filtering the events to include only goals
        2. Counting the number of goals scored with headers by checking if the description contains the word 'header'
        3. Counting the number of goals scored with feet or other methods by excluding headers from the count
        4. Returning the counts of header goals and foot or other goals
        ---> This will help provide insight into the types of goals scored in the match, indicating whether teams relied more on aerial threats or ground-based play to find the net
        """
    , 'headers': ['header_goals', 'foot_or_other_goals']}, {'id': 107,
    'name': "The 'Scrappy Period' Analysis", 'query':
    'Pinpoint the most chaotic spell of the match. I want the 10-minute period with the highest number of cards and fouls.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT (CAST(match_minute / 10 AS INT) * 10) || '-' || (CAST(match_minute / 10 AS INT) * 10 + 10) || ' mins' AS time_window, COUNT(*) AS incidents
        FROM parsed_commentary_{match_id} WHERE Event_Type IN ('Foul', 'Yellow Card', 'Red Card')
        GROUP BY 1 ORDER BY incidents DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the most chaotic 10-minute period in the match based on the number of fouls and cards issued.
        It does this by:
        1. Grouping the match into 10-minute intervals
        2. Counting the number of incidents (fouls, yellow cards, and red cards) that occurred in each interval
        3. Ordering the results by the count of incidents in descending order
        4. Limiting the results to the interval with the highest number of incidents
        5. Returning the time window of that interval and the count of incidents
        ---> This will help identify the most intense and potentially controversial period of the match, where the referee was most active in managing player conduct
        """
    , 'headers': ['time_window', 'incidents']}, {'id': 108, 'name':
    "The 'Set-Piece Battle'", 'query':
    'How dangerous were the set-pieces? Show me how many shots each team generated within a minute of a corner or direct free-kick.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH DeadBalls AS (SELECT Team_s, match_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Corner' OR Description LIKE '%direct free kick%')
        SELECT db.Team_s, COUNT(s.Time) as shots_from_set_pieces FROM DeadBalls db
        JOIN parsed_commentary_{match_id} s ON db.Team_s = s.Team_s
        WHERE s.Event_Type IN ('Shot', 'Goal') AND s.match_minute >= db.match_minute AND s.match_minute <= db.match_minute + 1
        GROUP BY db.Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the effectiveness of set-pieces in generating shots.
        It does this by:
        1. Identifying dead-ball situations (corners and direct free-kicks) and capturing the team and match minute
        2. Joining those dead-ball events with shot events to find shots taken by the same team within one minute of the dead-ball event
        3. Counting the number of shots generated from set-pieces for each team
        4. Grouping the results by team to ensure uniqueness
        5. Returning the team name and the count of shots generated from set-pieces
        ---> This will help assess how effective each team's set-piece situations were in creating goal-scoring opportunities,  
        indicating their tactical prowess in dead-ball scenarios
        """
    , 'headers': ['Team_s', 'shots_from_set_pieces']}, {'id': 109, 'name':
    "The 'Shooting Gallery' Period", 'query':
    'When was the game at its most end-to-end? Find the 5-minute spell with the most shots.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT (CAST(match_minute / 5 AS INT) * 5) || '-' || (CAST(match_minute / 5 AS INT) * 5 + 5) || ' mins' AS time_window, COUNT(*) as shot_count
        FROM parsed_commentary_{match_id} WHERE Event_Type IN ('Shot', 'Goal')
        GROUP BY 1 ORDER BY shot_count DESC LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the most action-packed 5-minute period in terms of shots taken.
        It does this by:
        1. Grouping the match into 5-minute intervals
        2. Counting the number of shots and goals that occurred in each interval
        3. Ordering the results by the count of shots in descending order
        4. Limiting the results to the interval with the highest number of shots
        5. Returning the time window of that interval and the count of shots
        ---> This will help identify the most exciting and dynamic period of the match, 
        where both teams were actively trying to score, leading to a flurry of shots
        """
    , 'headers': ['time_window', 'shot_count']}, {'id': 110, 'name':
    "The 'Starter vs. Sub' Goals", 'query':
    'Where did the goals come from, the starters or the bench? Show me a count for each.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        Starters AS (SELECT Player_s FROM AllEventsWithRowID WHERE row_id < 23 AND Player_s IS NOT NULL GROUP BY Player_s)
        SELECT
            SUM(CASE WHEN Player_s IN (SELECT Player_s FROM Starters) THEN 1 ELSE 0 END) as starter_goals,
            SUM(CASE WHEN Player_s NOT IN (SELECT Player_s FROM Starters) THEN 1 ELSE 0 END) as substitute_goals
        FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal';
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the source of goals scored in the match, distinguishing between starters and substitutes.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying starters based on their row ID (assuming starters are those with a row ID less than 23)
        3. Counting the number of goals scored by players who were starters and those who were substitutes
        4. Returning the count of goals scored by starters and substitutes
        ---> This will help assess the impact of both starting players and substitutes on the match outcome, 
        indicating whether the team's depth was a factor in their scoring success
        """
    , 'headers': ['starter_goals', 'substitute_goals']}, {'id': 111, 'name':
    "The 'Sub-on-Sub-off' Anomaly", 'query':
    'Did anyone have a nightmare cameo? Show me any player who came on as a sub and then got subbed off himself.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT s_on.Time, s_on.Player_In, s_on.Team_s FROM parsed_commentary_{match_id} s_on
        WHERE s_on.Event_Type = 'Substitution' AND EXISTS (
            SELECT 1 FROM parsed_commentary_{match_id} s_off
            WHERE s_off.Event_Type = 'Substitution'
            AND s_on.Player_In = s_off.Player_Out AND s_off.match_minute > s_on.match_minute
        );
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who came on as substitutes and were subsequently substituted off themselves.
        It does this by:
        1. Filtering the events to include only substitutions where a player came on
        2. Checking if there is a subsequent substitution event where the player who came on was substituted off
        3. Ensuring that the substitution off occurred after the substitution on
        4. Returning the time of the substitution, the player who came on, and their team
        ---> This will help identify instances where a substitute player had a brief appearance in the match, possibly indicating a tactical error or an injury,
        showcasing the challenges managers face in making effective substitutions
        """
    , 'headers': ['Time', 'Player_In', 'Team_s']}, {'id': 112, 'name':
    "The 'Subbed to Save' Pattern", 'query':
    'Which players on a yellow were quickly hooked? Show me anyone subbed off within 15 minutes of being booked.'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT c.Time as card_time, s.Time as sub_time, c.Player_s, c.Team_s 
        FROM parsed_commentary_{match_id} c
        JOIN parsed_commentary_{match_id} s ON c.Player_s = s.Player_Out AND c.Team_s = s.Team_s
        WHERE c.Event_Type = 'Yellow Card'
        AND s.Event_Type = 'Substitution' 
        AND s.match_minute > c.match_minute 
        AND s.match_minute - c.match_minute <= 15;
        """
    , 'Natural Language Description':
    """
        This query is designed to find players who received a yellow card and were substituted off within 15 minutes of being booked.
        It does this by:
        1. Filtering the events to include yellow cards
        2. Joining the yellow card events with substitution events where the player who received the card was substituted off
        3. Ensuring that the substitution occurred after the yellow card was issued and within 15 minutes
        4. Returning the time of the yellow card, the time of the substitution, the player involved, and their team
        ---> This will help analyze the tactical decisions made by managers in response to players being booked, 
        particularly in terms of protecting them from a potential second yellow card,
        indicating a proactive approach to managing player discipline and match risk
        """
    , 'headers': ['card_time', 'sub_time', 'Player_s', 'Team_s']}, {'id': 
    113, 'name': "The 'Super Sub' Goal", 'query':
    'Did any substitute make an instant impact? Show me any player who scored after coming off the bench.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT g.Time, g.Player_s, g.Team_s, g.Score 
        FROM parsed_commentary_{match_id} g 
        WHERE g.Event_Type = 'Goal' 
        AND g.Player_s IN (SELECT Player_In FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution');
        """
    , 'Natural Language Description':
    """
        This query is designed to find substitutes who made an immediate impact by scoring a goal after coming off the bench.
        It does this by:
        1. Filtering the events to include goals scored
        2. Checking if the player who scored was a substitute by looking for their name in the list of players who came on as substitutes
        3. Returning the time of the goal, the player who scored, their team, and the score of the goal
        ---> This will help identify the effectiveness of substitutes in changing the course of the match, particularly in terms of scoring goals,
        showcasing the importance of squad depth and tactical flexibility in football
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 114,
    'name': "The 'Tired Legs' Theory", 'query':
    "Let's test the 'tired legs' theory. Show me each team's foul count before the 75th minute and their foul count after."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Team_s, SUM(CASE WHEN match_minute < 75 THEN 1 ELSE 0 END) AS fouls_first_75, SUM(CASE WHEN match_minute >= 75 THEN 1 ELSE 0 END) AS fouls_last_15_plus
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Foul' 
        AND Team_s IS NOT NULL 
        GROUP BY Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the number of fouls committed by each team before and after the 75th minute of the match.
        It does this by:
        1. Filtering the events to include only fouls
        2. Grouping the fouls by team
        3. Summing the fouls committed by each team in two time periods: before the 75th minute and from the 75th minute onwards
        4. Returning the team name, the count of fouls in the first 75 minutes, and the count of fouls in the last 15+ minutes
        ---> This will help assess whether fatigue or tactical changes led to an increase in fouling behavior as the match progressed,
        providing insight into the physical demands placed on players and their impact on discipline in the latter stages of the game
        """
    , 'headers': ['Team_s', 'fouls_first_75', 'fouls_last_15_plus']}, {'id':
    115, 'name': "The 'Turning Point' Goal", 'query':
    "Let's pinpoint the decisive moment. I want the details of the goal that ultimately won the match: the one that put the winning team ahead for good."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Goals AS (SELECT * FROM parsed_commentary_{match_id} p WHERE p.Event_Type = 'Goal'), 
        FinalScore AS (SELECT Team_s, COUNT(Team_s) AS total_goals FROM Goals GROUP BY Team_s),
        MatchResult AS (SELECT MAX(CASE WHEN A.total_goals > B.total_goals THEN A.Team_s ELSE B.Team_s END) AS WinningTeam, MIN(A.total_goals) AS LoserScore FROM FinalScore AS A, FinalScore AS B WHERE A.Team_s <> B.Team_s),
        OrderedGoals AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute ASC) as goal_order FROM Goals),
        CumulativeScore AS (SELECT goal_order, match_minute, Team_s, Player_s, Score, Time, SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 0) THEN 1 ELSE 0 END) OVER (ORDER BY goal_order) AS team1_goals, SUM(CASE WHEN Team_s = (SELECT Team_s FROM FinalScore LIMIT 1 OFFSET 1) THEN 1 ELSE 0 END) OVER (ORDER BY goal_order) AS team2_goals FROM OrderedGoals),
        TiedMoments AS (SELECT goal_order FROM CumulativeScore WHERE team1_goals = team2_goals),
        LastTie AS (SELECT MAX(goal_order) AS last_tie_order FROM TiedMoments),
        FinalLeadGoal AS (SELECT * FROM CumulativeScore 
                          WHERE goal_order > (SELECT last_tie_order FROM LastTie) 
                          AND Team_s = (SELECT WinningTeam FROM MatchResult)
                          ORDER BY goal_order LIMIT 1)
        SELECT Time, Player_s, Team_s, Score 
        FROM FinalLeadGoal;
        """
    , 'Natural Language Description':
    """
        The premise here is to do the following:
        1. Find all the goals
        2. Find the final score
        3. Filter all the goals to show only those for the team that won, ranked in order of when they happened
        4. Find the ties in the match and rank them in order of when they happened
        5. Select the goal from those where the winning team took the lead for the FINAL Time (i.e. the first goal immediately after the final tie).
        6. Return the time, player, team, and score of that goal.
        ---> This will help identify the goal that ultimately secured the victory for the winning team, providing insight into the decisive moment in the match.
        """
    , 'headers': ['Time', 'Player_s', 'Team_s', 'Score']}, {'id': 116,
    'name': "The 'Turnover Cost' Analysis", 'query':
    'Which player was most guilty of giving the ball away in dangerous areas? Show a count of who lost possession leading to a shot within a minute.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH Turnovers AS (SELECT p.Player_s, p.Team_s, p.match_minute FROM parsed_commentary_{match_id} p WHERE p.Description LIKE '%loses possession%')
        SELECT t.Player_s, COUNT(*) AS costly_turnovers FROM Turnovers t
        WHERE EXISTS (SELECT 1 FROM parsed_commentary_{match_id} s WHERE s.Event_Type IN ('Shot', 'Goal') AND s.Team_s != t.Team_s AND s.match_minute > t.match_minute AND s.match_minute <= t.match_minute + 1)
        GROUP BY t.Player_s 
        ORDER BY costly_turnovers DESC;
        """
    , 'Natural Language Description':
    """
        This query is designed to identify players who frequently lost possession in dangerous areas that led to shots.
        It does this by:
        1. Filtering the events to include only turnovers where players lost possession
        2. Checking if there was a subsequent shot or goal by the opposing team within one minute of the turnover
        3. Counting the number of such turnovers for each player
        4. Grouping the results by player to ensure uniqueness
        5. Returning the player's name and the count of costly turnovers
        ---> This will help assess which players were most prone to giving the ball away in critical areas, 
        potentially leading to scoring opportunities for the opposition,
        indicating areas for improvement in ball retention and decision-making under pressure
        """
    , 'headers': ['Player_s', 'costly_turnovers']}, {'id': 117, 'name':
    "The 'Unluckiest Player' Award", 'query':
    'Who was denied by the woodwork most often? Show the player and how many times they hit the post or bar.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s, COUNT(*) as woodwork_hits FROM parsed_commentary_{match_id}
        WHERE Event_Type = 'Shot' AND Description LIKE '%hits the woodwork%'
        GROUP BY Player_s, Team_s 
        ORDER BY woodwork_hits DESC 
        LIMIT 1;
        """
    , 'Natural Language Description':
    """
        This query is designed to identify the player who hit the woodwork (post or bar) the most times during the match.
        It does this by:
        1. Filtering the events to include only shots that hit the woodwork
        2. Counting the number of times each player hit the woodwork
        3. Grouping the results by player and team to ensure uniqueness
        4. Ordering the results by the count of woodwork hits in descending order
        5. Limiting the results to the player with the highest count
        ---> This will help highlight the unluckiest player of the match, showcasing their near misses and the potential impact on the game's outcome,
        indicating how close they came to scoring despite not finding the net
        """
    , 'headers': ['Player_s', 'Team_s', 'woodwork_hits']}, {'id': 118,
    'name': "The 'Walking Wounded' Stat", 'query':
    'Which players were toughing it out? Show me anyone who got treatment but stayed on the pitch.'
    , 'difficulty': 'Medium', 'SQL':
    """
        SELECT Player_s, Team_s 
        FROM parsed_commentary_{match_id} 
        WHERE Event_Type = 'Injury' 
        AND Player_s IS NOT NULL 
        AND Player_s NOT IN (SELECT Player_Out FROM parsed_commentary_{match_id} WHERE Event_Type = 'Substitution') 
        GROUP BY Player_s, Team_s;
        """
    , 'Natural Language Description':
    """
        This query is designed to identify players who received treatment for injuries but remained on the pitch.
        It does this by:
        1. Filtering the events to include only injury events
        2. Ensuring that the player who received treatment is not listed as substituted out
        3. Grouping the results by player and team to ensure uniqueness
        4. Returning the player's name and their team
        ---> This will help highlight players who demonstrated resilience and determination by continuing to play despite receiving treatment for injuries,
        showcasing their commitment to the match and potentially their importance to the team's performance
        """
    , 'headers': ['Player_s', 'Team_s']}, {'id': 119, 'name':
    "The 'Wasted Dominance' Events", 'query':
    "Show me the best example of possession without end product. Find the longest spell a team had the ball that didn't even lead to a shot."
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        Streaks AS (
            SELECT *, (row_id - ROW_NUMBER() OVER (PARTITION BY Team_s ORDER BY row_id)) as streak_id
            FROM AllEventsWithRowID WHERE Team_s IS NOT NULL
        ), StreakSummary AS (
            SELECT streak_id, Team_s, COUNT(*) as streak_length, MIN(row_id) as start_row_id, MAX(row_id) as end_row_id, SUM(CASE WHEN Event_Type IN ('Shot', 'Goal') THEN 1 ELSE 0 END) as shots_in_streak
            FROM Streaks GROUP BY Team_s, streak_id
        ), LongestShotless AS (
            SELECT start_row_id, end_row_id FROM StreakSummary WHERE shots_in_streak = 0 ORDER BY streak_length DESC LIMIT 1
        )
        SELECT p.Time, p.Event_Type, p.Player_s, p.Team_s, p.Description FROM AllEventsWithRowID p JOIN LongestShotless l ON p.row_id = l.start_row_id OR p.row_id = l.end_row_id ORDER BY p.row_id;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the longest period of possession for a team that did not result in any shots.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying streaks of possession events for each team
        3. Summarizing those streaks to count their length, determine the start and end row IDs, and check if any shots were taken during that streak
        4. Filtering to find the longest streak of possession that did not include any shots
        5. Returning the events that occurred during that streak, including the time, event type, player involved, team, and description
        ---> This will help analyze periods of possession where a team maintained control of the ball without creating any goal-scoring opportunities, 
        indicating a lack of penetration in their play
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 120, 'name': 'Timeline: Longest Lull in Play', 'query':
    'When did the game go quiet? Show me the start and end of the longest period without a shot, goal, card, or sub.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH AllEventsWithRowID AS (SELECT *, ROW_NUMBER() OVER (ORDER BY match_minute, injury_time_minutes, Time) as row_id FROM parsed_commentary_{match_id}),
        GameEvents AS (SELECT row_id, match_minute FROM AllEventsWithRowID WHERE Event_Type IN ('Shot', 'Goal', 'Yellow Card', 'Red Card', 'Substitution')),
        EventLulls AS (SELECT (match_minute - LAG(match_minute, 1, 0) OVER (ORDER BY row_id)) as lull_duration, LAG(row_id, 1) OVER (ORDER BY row_id) as start_event_row_id, row_id as end_event_row_id FROM GameEvents),
        MaxLull AS (SELECT start_event_row_id, end_event_row_id FROM EventLulls ORDER BY lull_duration DESC LIMIT 1)
        SELECT p.Time, p.Event_Type, p.Player_s, p.Team_s, p.Description 
        FROM AllEventsWithRowID p JOIN MaxLull ml ON p.row_id = ml.start_event_row_id OR p.row_id = ml.end_event_row_id 
        ORDER BY p.row_id;
        """
    , 'Natural Language Description':
    """
        This query is designed to find the longest period of inactivity in the match, where no shots, goals, cards, or substitutions occurred.
        It does this by:
        1. Assigning a row ID to each event to maintain their order
        2. Identifying game events (shots, goals, cards, substitutions) and their corresponding match minutes
        3. Calculating the lull duration between consecutive game events
        4. Finding the longest lull by ordering the results by lull duration and limiting to the top result
        5. Returning the start and end events of that lull, including the time, event type, player involved, team, and description
        ---> This will help pinpoint the quietest period in the match, where the action slowed down significantly,
        indicating a lull in play that may have affected the game's flow and momentum
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 121, 'name': 'Timeline: Post-First Goal Momentum', 'query':
    'What was the reaction to the opening goal? Show me a timeline of everything that happened in the ten minutes after it.'
    , 'difficulty': 'Hard', 'SQL':
    """
        WITH FirstGoal AS (SELECT match_minute FROM parsed_commentary_{match_id} WHERE Event_Type = 'Goal' ORDER BY match_minute ASC LIMIT 1)
        SELECT c.Time, c.Event_Type, c.Player_s, c.Team_s, c.Description 
        FROM parsed_commentary_{match_id} c, FirstGoal fg
        WHERE c.match_minute > fg.match_minute 
        AND c.match_minute <= fg.match_minute + 10 
        ORDER BY c.match_minute ASC;
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze the immediate aftermath of the first goal scored in the match.
        It does this by:
        1. Identifying the minute when the first goal was scored
        2. Filtering the commentary events to include only those that occurred in the ten minutes following the first goal
        3. Ordering the results by match minute to maintain the timeline
        4. Returning the time of each event, the type of event, the player involved, their team, and a description of the event
        ---> This will help assess how both teams reacted to the opening goal, including any tactical changes, substitutions, or momentum shifts,
        providing insight into the psychological impact of scoring/conceding first in a match
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 122, 'name': 'Timeline: Second Half Stoppage Time Summary',
    'query':
    'Give me the highlights from the frantic finish. What was the key action in second-half stoppage time?'
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Event_Type, Player_s, Team_s, Description 
        FROM parsed_commentary_{match_id} 
        WHERE half = 'Second Half' 
        AND injury_time_minutes > 0
        AND Event_Type IN ('Goal', 'Yellow Card', 'Red Card', 'Substitution') 
        ORDER BY Time;
        """
    , 'Natural Language Description':
    """
        This query is designed to summarize the key actions that occurred during stoppage time in the second half of the match.`
        It does this by:
        1. Filtering the commentary events to include only those from the second half where stoppage time was played
        2. Including only significant events such as goals, yellow cards, red cards, and substitutions
        3. Ordering the results by time to maintain the sequence of events
        4. Returning the time of each event, the type of event, the player involved, their team, and a description of the event
        ---> This will help highlight the most critical moments in the match's closing stages, particularly in terms of scoring opportunities, 
        disciplinary actions, and tactical changes,
        providing insight into how the match concluded and any last-minute drama that unfolded
        """
    , 'headers': ['Time', 'Event_Type', 'Player_s', 'Team_s', 'Description'
    ]}, {'id': 123, 'name': 'Timeline: Shot in Minute Window', 'query':
    "Let's focus on a key period. Show me all the shots on goal that occurred between Minutes {X} and {Y}."
    , 'difficulty': 'Easy', 'SQL':
    """
        SELECT Time, Team_s, Player_s, Description FROM parsed_commentary_{match_id} WHERE Event_Type = 'Shot' AND match_minute >= {X} AND match_minute < {Y};
        """
    , 'Natural Language Description':
    """
        This query is designed to analyze all shots on goal that occurred within a specific minute window during the match.
        It does this by:
        1. Filtering the commentary events to include only shots
        2. Specifying the minute range for the analysis (from {X} to {Y})
        3. Returning the time of each shot, the team that took the shot, the player who took it, and a description of the shot
        ---> This will help assess the attacking intent and effectiveness of both teams during that particular period,
        providing insight into how well each team was able to create goal-scoring opportunities in that minute window
        """
    , 'headers': ['Time', 'Team_s', 'Player_s', 'Description']}]
