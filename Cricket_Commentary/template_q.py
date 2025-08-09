## to do : hattrick of wickets, sixes, wides, count of no balls, runs scored after no balls, extra runs in wides or no balls
## top n, 
question_templates = [
    {
        "id": 1,
        "question": "Find the bowler who has given the most runs and how many runs has the bowler given?",
        "query": "SELECT bowler, SUM(bowler_runs_given) AS total_runs FROM {table_name} GROUP BY bowler ORDER BY total_runs DESC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 2,
        "question": "Which batsman has faced the most balls and how many balls has the batsman faced?",
        "query": "SELECT batsman, SUM(batsman_bowls_faced) AS total_balls FROM {table_name} GROUP BY batsman ORDER BY total_balls DESC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 3,
        "question": "In which over did {batsman} hit their first four and who was the bowler?",
        "query": "SELECT overs, bowler FROM {table_name} WHERE batsman = '{batsman}' AND batsman_runs = 4 ORDER BY overs ASC LIMIT 1;",
        "variables": ["table_name", "batsman"]
    },
    {
        "id": 4,
        "question": "How many fours did {batsman} hit against {bowler}? Show the tally in table.",
        "query": "SELECT COUNT(*) AS total_fours FROM {table_name} WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND batsman_runs = 4;",
        "variables": ["table_name", "batsman", "bowler"]
    },
    {
        "id": 5,
        "question": "What is the total number of wickets taken by {bowler1} and {bowler2} combined?",
        "query": "SELECT SUM(bowler_wickets) AS total_wickets FROM {table_name} WHERE bowler IN ('{bowler1}', '{bowler2}');",
        "variables": ["table_name", "bowler1", "bowler2"]
    },
    {
        "id": 6,
        "question": "Who bowled the most number of balls and how many balls has that bowler bowled?",
        "query": "SELECT bowler, SUM(bowler_bowls_done) AS total_balls FROM {table_name} GROUP BY bowler ORDER BY total_balls DESC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 7,
        "question": "How many runs did {batsman} score?",
        "query": "SELECT SUM(batsman_runs) AS total_runs FROM {table_name} WHERE batsman = '{batsman}';",
        "variables": ["table_name", "batsman"]
    },
    {
        "id": 8,
        "question": "What is the average number of runs given by {bowler}?",
        "query": "SELECT AVG(bowler_runs_given) AS avg_runs_given FROM {table_name} WHERE bowler = '{bowler}';",
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 9,
        "question": "Which batsman faced the most balls and how many balls did they face?",
        "query": "SELECT batsman, SUM(batsman_bowls_faced) AS total_bowls_faced FROM {table_name} GROUP BY batsman ORDER BY total_bowls_faced DESC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 10,
        "question": "How many wickets were taken in total combined by every bowler?",
        "query": "SELECT SUM(bowler_wickets) AS total_wickets FROM {table_name};",
        "variables": ["table_name"]
    },
    {
        "id": 11,
        "question": "Which bowler took the most wickets and gave the fewest runs?",
        "query": "SELECT bowler, SUM(bowler_wickets) AS total_wickets, SUM(bowler_runs_given) AS total_runs FROM {table_name} GROUP BY bowler ORDER BY total_wickets DESC, total_runs ASC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 12,
        "question": "Calculate the total number of fours hit by batsmen against {bowler}.",
        "query": "SELECT SUM(batsman_fours) AS total_fours FROM {table_name} WHERE bowler = '{bowler}';",
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 13,
        "question": "Calculate the total number of sixes hit by batsmen against {bowler}.",
        "query": "SELECT SUM(batsman_sixes) AS total_sixes FROM {table_name} WHERE bowler = '{bowler}';",
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 14,
        "question": "Calculate the total number of dots hit by {batsman} against {bowler}.",
        "query": "SELECT COUNT(*) AS total_dots FROM {table_name} WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND team_runs = 0;",
        "variables": ["table_name", "batsman", "bowler"]
    },
    {
        "id": 15,
        "question": "Find the batsman who scored the most runs against {bowler} and also hit the most sixes.",
        "query": "SELECT batsman, SUM(batsman_runs) AS total_runs, SUM(batsman_sixes) AS total_sixes FROM {table_name} WHERE bowler = '{bowler}' GROUP BY batsman ORDER BY total_runs DESC, total_sixes DESC LIMIT 1;",
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 16,
        "question": "What is the total number of runs scored by a batsman who faced 10 or more balls and hit 2 or more fours?",
        "query": "SELECT SUM(total_runs) AS total_runs "
                "FROM ( "
                    "SELECT batsman, "
                        "SUM(batsman_runs) AS total_runs, "
                        "SUM(batsman_bowls_faced) AS total_balls, "
                        "SUM(batsman_fours) AS total_fours "
                    "FROM {table_name} "
                    "GROUP BY batsman "
                    "HAVING SUM(batsman_bowls_faced) >= 10 AND SUM(batsman_fours) >= 2)",
        "variables": ["table_name"]
    },
    {
        "id": 18,
        "question": "Find the bowler who conceded the most runs and the batsman who scored the most runs against him in a single over. How many runs did the batsman score and how many runs did batsman score against him in single over ?",
        "query": (
        "WITH over_runs AS ( "
        "  SELECT bowler, overs, SUM(team_runs) AS runs_in_over "
        "  FROM {table_name} "
        "  GROUP BY bowler, overs "
        "), "
        "max_over AS ( "
        "  SELECT bowler, overs, runs_in_over "
        "  FROM over_runs "
        "  ORDER BY runs_in_over DESC "
        "  LIMIT 1 "
        "), "
        "batsman_runs AS ( "
        "  SELECT batsman, SUM(batsman_runs) AS batsman_runs_in_over "
        "  FROM {table_name} "
        "  WHERE bowler = (SELECT bowler FROM max_over) "
        "    AND overs = (SELECT overs FROM max_over) "
        "  GROUP BY batsman "
        "  ORDER BY batsman_runs_in_over DESC "
        "  LIMIT 1 "
        ") "
        "SELECT "
        "  (SELECT bowler FROM max_over) AS bowler, "
        "  (SELECT overs FROM max_over) AS over_number, "
        "  (SELECT runs_in_over FROM max_over) AS runs_conceded_in_over, "
        "  (SELECT batsman FROM batsman_runs) AS top_batsman, "
        "  (SELECT batsman_runs_in_over FROM batsman_runs) AS batsman_runs_in_over;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 19,
        "question": "How many times did each batsman face the bowler {bowler}?",
        "query": "SELECT batsman, COUNT(*) AS deliveries_faced FROM {table_name} WHERE bowler = '{bowler}' GROUP BY batsman;",
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 20,
        "question": "Calculate the total runs scored by each batsman and filter those who hit a six or a four.",
        "query": "SELECT batsman, SUM(batsman_runs) AS total_runs FROM {table_name} WHERE batsman_sixes > 0 OR batsman_fours > 0 GROUP BY batsman;",
        "variables": ["table_name"]
    },
    {
        "id": 21,
        "question": "Which bowler gave the most runs in an over and what was the over number?",
        "query": "SELECT overs, bowler, SUM(bowler_runs_given) AS runs_in_over FROM {table_name} GROUP BY overs, bowler ORDER BY runs_in_over DESC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 22,
        "question": "Find the bowler who conceded the fewest runs while taking at least one wicket.",
        "query": "SELECT bowler, SUM(bowler_runs_given) AS total_runs FROM {table_name} WHERE bowler_wickets > 0 GROUP BY bowler ORDER BY total_runs ASC LIMIT 1;",
        "variables": ["table_name"]
    },
    {
        "id": 23,
        "question": "Name the batsmen who hit at least one six and what is the total runs scored by them?",
        "query": "SELECT batsman, SUM(batsman_runs) AS total_runs FROM {table_name} WHERE batsman_sixes > 0 GROUP BY batsman;",
        "variables": ["table_name"]
    },
    {
        "id": 24,
        "question": "What is the total number of runs scored between {x1} and {x2} overs of the match?",
        "query": "SELECT SUM(team_runs) AS total_runs FROM {table_name} WHERE overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 25,
        "question": "Find the bowler who has given the most runs and how many runs has the bowler given between overs {x1} and {x2}?",
        "query": "SELECT bowler, SUM(bowler_runs_given) AS total_runs FROM {table_name} WHERE overs BETWEEN {x1} AND {x2} GROUP BY bowler ORDER BY total_runs DESC LIMIT 1;",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 26,
        "question": "Which batsman has faced the most balls and how many balls has the batsman faced between overs {x1} and {x2}?",
        "query": "SELECT batsman, SUM(batsman_bowls_faced) AS total_balls FROM {table_name} WHERE overs BETWEEN {x1} AND {x2} GROUP BY batsman ORDER BY total_balls DESC LIMIT 1;",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 27,
        "question": "In which over did {batsman} hit his first four between overs {x1} and {x2}?",
        "query": "SELECT overs FROM {table_name} WHERE batsman = '{batsman}' AND batsman_runs = 4 AND overs BETWEEN {x1} AND {x2} ORDER BY overs ASC LIMIT 1;",
        "variables": ["table_name", "batsman", "x1", "x2"]
    },
    {
        "id": 28,
        "question": "How many fours did {batsman} hit against {bowler} between overs {x1} and {x2}? Show the tally in table.",
        "query": "SELECT COUNT(*) AS total_fours FROM {table_name} WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND batsman_runs = 4 AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "batsman", "bowler", "x1", "x2"]
    },
    {
        "id": 29,
        "question": "What is the total number of wickets taken by {bowler1} and {bowler2} combined between overs {x1} and {x2}?",
        "query": "SELECT SUM(bowler_wickets) AS total_wickets FROM {table_name} WHERE bowler IN ('{bowler1}', '{bowler2}') AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "bowler1", "bowler2", "x1", "x2"]
    },
    {
        "id": 30,
        "question": "Who bowled the most overs and how many overs has that bowler bowled between overs {x1} and {x2}?",
        "query": "SELECT bowler, SUM(bowler_bowls_done)/6.0 AS total_overs FROM {table_name} WHERE overs BETWEEN {x1} AND {x2} GROUP BY bowler ORDER BY total_overs DESC LIMIT 1;",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 31,
        "question": "How many runs did {batsman} score between overs {x1} and {x2}?",
        "query": "SELECT SUM(batsman_runs) AS total_runs FROM {table_name} WHERE batsman = '{batsman}' AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "batsman", "x1", "x2"]
    },
    {
        "id": 32,
        "question": "What is the average number of runs given by {bowler} between overs {x1} and {x2}?",
        "query": "SELECT AVG(bowler_runs_given) AS avg_runs_given FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 33,
        "question": "Which batsman faced the most balls and how many balls did they face between overs {x1} and {x2}?",
        "query": "SELECT batsman, SUM(batsman_bowls_faced) AS total_bowls_faced FROM {table_name} WHERE overs BETWEEN {x1} AND {x2} GROUP BY batsman ORDER BY total_bowls_faced DESC LIMIT 1;",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 34,
        "question": "How many wickets were taken in total combined by every bowler between overs {x1} and {x2}?",
        "query": "SELECT SUM(bowler_wickets) AS total_wickets FROM {table_name} WHERE overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 35,
        "question": "Which bowler took the most wickets and gave the fewest runs between overs {x1} and {x2} and how many runs and wickets were they?",
        "query": "SELECT bowler, SUM(bowler_wickets) AS total_wickets, SUM(bowler_runs_given) AS total_runs FROM {table_name} WHERE overs BETWEEN {x1} AND {x2} GROUP BY bowler ORDER BY total_wickets DESC, total_runs ASC LIMIT 1;",
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 36,
        "question": "Calculate the total number of fours hit by batsmen against {bowler} between overs {x1} and {x2}",
        "query": "SELECT SUM(batsman_fours) AS total_fours FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 37,
        "question": "Calculate the total number of sixes hit by batsmen against {bowler} between overs {x1} and {x2}",
        "query": "SELECT SUM(batsman_sixes) AS total_sixes FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 38,
        "question": "Calculate the total number of dots hit by {batsman} against {bowler} between overs {x1} and {x2}",
        "query": "SELECT COUNT(*) AS total_dots FROM {table_name} WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND team_runs = 0 AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "batsman", "bowler", "x1", "x2"]
    },
    {
        "id": 39,
        "question": "Find the batsman who scored the most runs against {bowler} and also hit the most sixes between overs {x1} and {x2}",
        "query": "SELECT batsman, SUM(batsman_runs) AS total_runs, SUM(batsman_sixes) AS total_sixes FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2} GROUP BY batsman ORDER BY total_runs DESC, total_sixes DESC LIMIT 1;",
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 41,
        "question": "Calculate the total number of sixes hit by batsmen against {bowler} between overs {x1} and {x2}",
        "query": "SELECT COALESCE(SUM(batsman_sixes), 0) AS total_sixes FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 42,
        "question": "Calculate the total number of dots hit by {batsman} against {bowler} between overs {x1} and {x2}",
        "query": "SELECT COUNT(*) AS total_dots FROM {table_name} WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND team_runs = 0 AND overs BETWEEN {x1} AND {x2};",
        "variables": ["table_name", "batsman", "bowler", "x1", "x2"]
    },
    {
        "id": 43,
        "question": "Find the batsman who scored the most runs against {bowler} and also hit the most sixes between overs {x1} and {x2}",
        "query": ("SELECT batsman, SUM(batsman_runs) AS total_runs, SUM(batsman_sixes) AS total_sixes "
                  "FROM {table_name} WHERE bowler = '{bowler}' AND overs BETWEEN {x1} AND {x2} "
                  "GROUP BY batsman ORDER BY total_runs DESC, total_sixes DESC LIMIT 1;"),
        "variables": ["table_name", "bowler", "x1", "x2"]
    },
    {
        "id": 44,
        "question": "List all batsmen and the total number of runs they scored against {bowler}.",
        "query": (
            "SELECT batsman, SUM(batsman_runs) AS total_runs "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}' "
            "GROUP BY batsman "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 45,
        "question": "Show each bowler and the total number of sixes hit against them by {batsman}.",
        "query": (
            "SELECT bowler, SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes_hit "
            "FROM {table_name} "
            "WHERE batsman = '{batsman}' "
            "GROUP BY bowler "
            "ORDER BY sixes_hit DESC;"
        ),
        "variables": ["table_name", "batsman"]
    },
    {
        "id": 46,
        "question": "List all batsmen and how many deliveries they faced from {bowler}.",
        "query": (
            "SELECT batsman, COUNT(*) AS balls_faced "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}' "
            "GROUP BY batsman "
            "ORDER BY balls_faced DESC;"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 47,
        "question": "List all overs where {batsman} faced {bowler}, and how many runs they scored in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, SUM(batsman_runs) AS runs_in_over "
            "FROM {table_name} "
            "WHERE batsman = '{batsman}' AND bowler = '{bowler}' "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name", "batsman", "bowler"]
    },
    {
        "id": 48,
        "question": "Show the total runs and number of dot balls faced by each batsman against {bowler}.",
        "query": (
            "SELECT batsman, SUM(batsman_runs) AS total_runs, "
            "SUM(CASE WHEN team_runs = 0 THEN 1 ELSE 0 END) AS dot_balls "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}' "
            "GROUP BY batsman "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 49,
        "question": "List batsman-bowler pairs and the total number of deliveries between them where at least one boundary (4 or 6) was hit.",
        "query": (
            "SELECT batsman, bowler, COUNT(*) AS boundary_deliveries "
            "FROM {table_name} "
            "WHERE batsman_runs IN (4, 6) "
            "GROUP BY batsman, bowler "
            "ORDER BY boundary_deliveries DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 50,
        "question": "List each over where {batsman} faced {bowler}, showing number of boundaries (4/6) hit in each.",
        "query": (
            "SELECT overs, COUNT(*) AS boundaries "
            "FROM {table_name} "
            "WHERE batsman = '{batsman}' AND bowler = '{bowler}' AND batsman_runs IN (4,6) "
            "GROUP BY overs "
            "ORDER BY overs;"
        ),
        "variables": ["table_name", "batsman", "bowler"]
    },
    {
        "id": 51,
        "question": "List all batsmen who hit at least one six against {bowler}, with total runs and number of sixes.",
        "query": (
            "SELECT batsman, SUM(batsman_runs) AS total_runs, "
            "SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS total_sixes "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}' "
            "GROUP BY batsman "
            "HAVING total_sixes > 0 "
            "ORDER BY total_sixes DESC;"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 52,
        "question": "Show all batsmen and their dot ball percentages against {bowler} (if faced at least 6 balls).",
        "query": (
            "SELECT batsman, "
            "ROUND(100.0 * SUM(CASE WHEN team_runs = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS dot_ball_percentage, "
            "COUNT(*) AS balls_faced "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}' "
            "GROUP BY batsman "
            "HAVING balls_faced >= 6 "
            "ORDER BY dot_ball_percentage DESC;"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 53,
        "question": "List every batsman-bowler pair with total runs, balls faced, and boundaries (4 or 6) between them.",
        "query": (
            "SELECT batsman, bowler, "
            "SUM(batsman_runs) AS total_runs, "
            "COUNT(*) AS balls_faced, "
            "SUM(CASE WHEN batsman_runs IN (4,6) THEN 1 ELSE 0 END) AS boundaries "
            "FROM {table_name} "
            "GROUP BY batsman, bowler "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 54,
        "question": "List all sequences of 3 consecutive sixes hit by batsmen and on which balls.",
        "query": (
            "SELECT t1.batsman, t1.overs AS ball_1, t2.overs AS ball_2, t3.overs AS ball_3 "
            "FROM {table_name} t1 "
            "JOIN {table_name} t2 ON t2.overs = t1.overs + 0.1 AND t2.batsman = t1.batsman "
            "JOIN {table_name} t3 ON t3.overs = t2.overs + 0.1 AND t3.batsman = t1.batsman "
            "WHERE t1.batsman_runs = 6 AND t2.batsman_runs = 6 AND t3.batsman_runs = 6 "
            "ORDER BY t1.batsman, t1.overs;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 55,
        "question": "Show wides bowled by each bowler per over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, bowler, COUNT(*) AS wides "
            "FROM {table_name} "
            "WHERE runs like '%w%' "
            "GROUP BY FLOOR(overs), bowler "
            "ORDER BY over_number, bowler;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 56,
        "question": "Show no balls bowled by each bowler per over.",
        "query": (
                "SELECT FLOOR(overs) AS over_number, bowler, COUNT(*) AS no_balls "
                "FROM {table_name} "
                "WHERE runs LIKE '%nb%' "
                "GROUP BY FLOOR(overs), bowler "
                "ORDER BY over_number, bowler;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 57,
        "question": "List batsmen and total runs they scored on no balls per bowler.",
        "query": (
            "SELECT bowler, batsman, SUM(batsman_runs) AS runs_on_no_balls "
            "FROM {table_name} "
            "WHERE runs LIKE '%nb%' "
            "GROUP BY bowler, batsman "
            "ORDER BY bowler, runs_on_no_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 58,
        "question": "Show extra runs conceded through wides and no balls by each bowler, per over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, bowler, SUM(team_runs-batsman_runs) AS extras_in_over "
            "FROM {table_name} "
            "WHERE runs LIKE '%w%' OR runs LIKE '%nb%' "
            "GROUP BY FLOOR(overs), bowler "
            "ORDER BY over_number, bowler;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 59,
        "question": "Show batsmen and how many runs they scored on no ball deliveries from each bowler.",
        "query": (
            "SELECT batsman, bowler, SUM(batsman_runs) AS runs_on_no_balls "
            "FROM {table_name} "
            "WHERE runs LIKE '%nb%' "
            "GROUP BY batsman, bowler "
            "ORDER BY runs_on_no_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 60,
        "question": "List total extras conceded by each batting team in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(CASE WHEN runs LIKE '%wd%' THEN 1 ELSE 0 END) AS wides, "
            "SUM(CASE WHEN runs LIKE '%nb%' THEN 1 ELSE 0 END) AS no_balls, "
            "SUM(CASE WHEN runs LIKE '%b%' AND runs NOT LIKE '%nb%' AND runs NOT LIKE '%wd%' THEN 1 ELSE 0 END) AS byes, "
            "SUM(CASE WHEN runs LIKE '%lb%' THEN 1 ELSE 0 END) AS leg_byes, "
            "COUNT(*) AS total_extras_in_over "
            "FROM {table_name} "
            "WHERE runs LIKE '%wd%' OR runs LIKE '%nb%' OR runs LIKE '%b%' OR runs LIKE '%lb%' "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number; "
        ),
        "variables": ["table_name"]
    },
    {
        "id": 61,
        "question": "Show runs scored after no ball deliveries, by batsman and bowler pair.",
        "query": (
            "SELECT t1.bowler, t2.batsman, SUM(t2.team_runs) AS runs_after_no_ball "
            "FROM {table_name} t1 "
            "JOIN {table_name} t2 ON t2.overs = t1.overs + 0.1 AND t1.bowler = t2.bowler "
            "WHERE t1.runs LIKE '%nb%' "
            "GROUP BY t1.bowler, t2.batsman "
            "ORDER BY runs_after_no_ball DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 62,
        "question": "Show each bowler's number of hat-tricks of wides (3 consecutive balls) with start ball.",
        "query": (
            "SELECT t1.bowler, t1.overs AS wide_1, t2.overs AS wide_2, t3.overs AS wide_3 "
            "FROM {table_name} t1 "
            "JOIN {table_name} t2 ON t2.overs = t1.overs + 0.1 AND t2.bowler = t1.bowler "
            "JOIN {table_name} t3 ON t3.overs = t2.overs + 0.1 AND t3.bowler = t1.bowler "
            "WHERE t1.runs like '%w%' AND t2.runs like '%w%' AND t3.runs like '%w%' "
            "ORDER BY t1.bowler, t1.overs;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 63,
        "question": "Show total runs scored in each over with number of wickets fallen.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS total_runs, "
            "COUNT(runs like '%W%') AS wickets_in_over "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 64,
        "question": "Show runs conceded and extras per over by each bowler.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, bowler, "
            "SUM(team_runs) AS runs_in_over, "
            "SUM(team_runs-batsman_runs) AS extras_in_over "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs), bowler "
            "ORDER BY over_number, bowler;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 65,
        "question": "Show total runs, wickets, wides, and no balls in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS total_runs, "
            "SUM(bowler_wickets) AS wickets, "
            "COUNT(runs like '%w%') AS wides, "
            "COUNT(runs like '%nb%') AS no_balls "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 66,
        "question": "Show runs scored by each batsman in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, batsman, "
            "SUM(batsman_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs), batsman "
            "ORDER BY over_number, batsman;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 67,
        "question": "Show number of balls faced by each batsman in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, batsman, "
            "COUNT(*) AS balls_faced "
            "FROM {table_name} "
            "WHERE runs not like '%w%' "
            "GROUP BY FLOOR(overs), batsman "
            "ORDER BY over_number, batsman;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 68,
        "question": "Show number of dot balls bowled in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "COUNT(*) AS dot_balls "
            "FROM {table_name} "
            "WHERE team_runs = 0 "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 69,
        "question": "Show progression of cumulative score after each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over, "
            "SUM(SUM(team_runs)) OVER (ORDER BY FLOOR(overs)) AS cumulative_runs "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 70,
        "question": "Show cumulative wickets after each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "COUNT(bowler_wickets) AS wickets_in_over, "
            "SUM(SUM(bolwer_wickets)) OVER (ORDER BY FLOOR(overs)) AS cumulative_wickets "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 71,
        "question": "Show total runs scored in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 72,
        "question": "Show total runs per over by batting team.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 73,
        "question": "Show cumulative total runs after each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over, "
            "SUM(SUM(team_runs)) OVER (ORDER BY FLOOR(overs)) AS cumulative_runs "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 74,
        "question": "Show cumulative total runs after each over by batting team.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over, "
            "SUM(SUM(team_runs)) OVER (PARTITION BY batting_team ORDER BY FLOOR(overs)) AS cumulative_runs "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 75,
        "question": "Show 3-over moving average of runs to detect momentum shifts.",
        "query": (
            "SELECT over_number, "
            "AVG(runs_in_over) OVER (ORDER BY over_number ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_runs "
            "FROM ("
            "  SELECT FLOOR(overs) AS over_number, "
            "  SUM(team_runs) AS runs_in_over "
            "  FROM {table_name} "
            "  GROUP BY FLOOR(overs) "
            ") AS overwise_runs "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 76,
        "question": "Show 5-over moving average of runs by batting team.",
        "query": (
            "SELECT over_number, "
            "AVG(runs_in_over) OVER (ORDER BY over_number ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS moving_avg_runs "
            "FROM ("
            "  SELECT FLOOR(overs) AS over_number, "
            "  SUM(team_runs) AS runs_in_over "
            "  FROM {table_name} "
            "  GROUP BY FLOOR(overs) "
            ") AS overwise_runs "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 77,
        "question": "Show total runs scored by each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, SUM(batsman_runs) AS runs_scored "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman "
            "ORDER BY runs_scored DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 78,
        "question": "Show number of balls faced by each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, COUNT(*) AS balls_faced "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman "
            "ORDER BY balls_faced DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 79,
        "question": "Show runs conceded by each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, SUM(team_runs) AS runs_conceded "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler "
            "ORDER BY runs_conceded DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 80,
        "question": "Show total wickets taken by each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, SUM(bowler_wickets) AS wickets_taken "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler "
            "ORDER BY wickets_taken DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 81,
        "question": "Show number of dot balls bowled by each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, COUNT(*) AS dot_balls "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} AND team_runs = 0"
            "GROUP BY bowler "
            "ORDER BY dot_balls DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 82,
        "question": "Show number of sixes hit by each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes_hit "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman "
            "ORDER BY sixes_hit DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 83,
        "question": "Show total extras conceded by each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, SUM(team_runs-batsman_runs) AS extras_conceded "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler "
            "ORDER BY extras_conceded DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 84,
        "question": "Show total runs and wickets per over between overs {x1} and {x2}.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "SUM(team_runs) AS runs_in_over, "
            "SUM(bowler_wickets) AS wickets_in_over "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 85,
        "question": "Show number of wides bowled by each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, COUNT(runs like '%w%') AS wides "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler "
            "ORDER BY wides DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 86,
        "question": "Show total runs scored by each batsman against each bowler.",
        "query": (
            "SELECT batsman, bowler, SUM(batsman_runs) AS total_runs "
            "FROM {table_name} "
            "GROUP BY batsman, bowler "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 87,
        "question": "Show total balls faced by each batsman against each bowler.",
        "query": (
            "SELECT batsman, bowler, COUNT(*) AS balls_faced "
            "FROM {table_name} "
            "GROUP BY batsman, bowler "
            "ORDER BY balls_faced DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 88,
        "question": "Show total wickets taken by each bowler against each batsman.",
        "query": (
            "SELECT bowler, batsman, SUM(bowler_wickets) AS wickets_taken "
            "FROM {table_name} "
            "GROUP BY bowler, batsman "
            "ORDER BY wickets_taken DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 89,
        "question": "Show number of dot balls bowled by each bowler to each batsman.",
        "query": (
            "SELECT bowler, batsman, COUNT(*) AS dot_balls "
            "FROM {table_name} "
            "WHERE team_runs = 0 "
            "GROUP BY bowler, batsman "
            "ORDER BY dot_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 90,
        "question": "Show number of sixes hit by each batsman against each bowler.",
        "query": (
            "SELECT batsman, bowler, SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes_hit "
            "FROM {table_name} "
            "GROUP BY batsman, bowler "
            "ORDER BY sixes_hit DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 91,
        "question": "Show total runs conceded by each bowler to each batsman in each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, bowler, batsman, SUM(team_runs) AS runs_conceded "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs), bowler, batsman "
            "ORDER BY over_number, runs_conceded DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 92,
        "question": "Show batting strike rate of each batsman against each bowler.",
        "query": (
            "SELECT batsman, bowler, "
            "SUM(batsman_runs) AS total_runs, "
            "COUNT(*) AS balls_faced, "
            "(SUM(batsman_runs) * 100.0 / COUNT(*)) AS strike_rate "
            "FROM {table_name} "
            "GROUP BY batsman, bowler "
            "ORDER BY strike_rate DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 93,
        "question": "Show economy rate of each bowler against each batsman.",
        "query": (
            "SELECT bowler, batsman, "
            "SUM(team_runs) AS total_runs_conceded, "
            "COUNT(*) AS balls_bowled, "
            "(SUM(team_runs) * 6.0 / COUNT(*)) AS economy_rate "
            "FROM {table_name} "
            "GROUP BY bowler, batsman "
            "ORDER BY economy_rate ASC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 94,
        "question": "Show number of no balls and wides bowled by each bowler to each batsman.",
        "query": (
            "SELECT bowler, batsman, "
            "COUNT(runs like '%nb%') AS no_balls, "
            "COUNT(runs like '%w%') AS wides "
            "FROM {table_name} "
            "GROUP BY bowler, batsman "
            "ORDER BY no_balls DESC, wides DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 95,
        "question": "Show total runs scored by each batsman against each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, bowler, SUM(batsman_runs) AS total_runs "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman, bowler "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 96,
        "question": "Show total wickets taken by each bowler against each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, batsman, SUM(bowler_wickets) AS wickets_taken "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler, batsman "
            "ORDER BY wickets_taken DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 97,
        "question": "Show number of dot balls bowled by each bowler to each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, batsman, COUNT(*) AS dot_balls "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "AND team_runs = 0 "
            "GROUP BY bowler, batsman "
            "ORDER BY dot_balls DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 98,
        "question": "Show number of sixes hit by each batsman against each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, bowler, SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes_hit "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman, bowler "
            "ORDER BY sixes_hit DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 99,
        "question": "Show batting strike rate of each batsman against each bowler between overs {x1} and {x2}.",
        "query": (
            "SELECT batsman, bowler, "
            "SUM(batsman_runs) AS total_runs, "
            "COUNT(*) AS balls_faced, "
            "(SUM(batsman_runs) * 100.0 / COUNT(*)) AS strike_rate "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY batsman, bowler "
            "ORDER BY strike_rate DESC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 100,
        "question": "Show economy rate of each bowler against each batsman between overs {x1} and {x2}.",
        "query": (
            "SELECT bowler, batsman, "
            "SUM(team_runs) AS total_runs_conceded, "
            "COUNT(*) AS balls_bowled, "
            "(SUM(team_runs) * 6.0 / COUNT(*)) AS economy_rate "
            "FROM {table_name} "
            "WHERE FLOOR(overs) BETWEEN {x1} AND {x2} "
            "GROUP BY bowler, batsman "
            "ORDER BY economy_rate ASC;"
        ),
        "variables": ["table_name", "x1", "x2"]
    },
    {
        "id": 101,
        "question": "List all bowlers sorted by total runs conceded, with number of balls bowled and economy rate across all batsmen.",
        "query": (
            "SELECT bowler, "
            "SUM(team_runs) AS total_runs_conceded, "
            "COUNT(*) AS balls_bowled, "
            "(SUM(team_runs) * 6.0 / COUNT(*)) AS economy_rate "
            "FROM {table_name} "
            "GROUP BY bowler "
            "ORDER BY total_runs_conceded DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 102,
        "question": "Show how many runs each batsman scored against the bowler who conceded the most runs.",
        "query": (
            "WITH top_bowler AS ( "
            "  SELECT bowler "
            "  FROM {table_name} "
            "  GROUP BY bowler "
            "  ORDER BY SUM(team_runs) DESC "
            "  LIMIT 1 "
            ") "
            "SELECT batsman, SUM(batsman_runs) AS total_runs "
            "FROM {table_name} "
            "WHERE bowler = (SELECT bowler FROM top_bowler) "
            "GROUP BY batsman "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 103,
        "question": "Show number of sixes hit by each batsman against the bowler who conceded the most runs.",
        "query": (
            "WITH top_bowler AS ( "
            "  SELECT bowler "
            "  FROM {table_name} "
            "  GROUP BY bowler "
            "  ORDER BY SUM(team_runs) DESC "
            "  LIMIT 1 "
            ") "
            "SELECT batsman, SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS sixes_hit "
            "FROM {table_name} "
            "WHERE bowler = (SELECT bowler FROM top_bowler) "
            "GROUP BY batsman "
            "ORDER BY sixes_hit DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 104,
        "question": "Show strike rate of each batsman against the bowler who conceded the most runs.",
        "query": (
            "WITH top_bowler AS ( "
            "  SELECT bowler "
            "  FROM {table_name} "
            "  GROUP BY bowler "
            "  ORDER BY SUM(team_runs) DESC "
            "  LIMIT 1 "
            ") "
            "SELECT batsman, "
            "SUM(batsman_runs) AS total_runs, "
            "COUNT(*) AS balls_faced, "
            "(SUM(batsman_runs) * 100.0 / COUNT(*)) AS strike_rate "
            "FROM {table_name} "
            "WHERE bowler = (SELECT bowler FROM top_bowler) "
            "AND runs like '%w%' "
            "GROUP BY batsman "
            "ORDER BY strike_rate DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 105,
        "question": "Show the highest conceding over for each bowler.",
        "query": (
            "WITH bowler_over_runs AS ( "
            "  SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS runs_in_over "
            "  FROM {table_name} "
            "  GROUP BY bowler, FLOOR(overs) "
            ") "
            "SELECT bowler, over_number, runs_in_over "
            "FROM ( "
            "  SELECT *, RANK() OVER (PARTITION BY bowler ORDER BY runs_in_over DESC) AS over_rank "
            "  FROM bowler_over_runs "
            ") ranked_overs "
            "WHERE over_rank = 1 "
            "ORDER BY runs_in_over DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 106,
        "question": "Show the top 5 most expensive overs bowled by any bowler.",
        "query": (
            "SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY bowler, FLOOR(overs) "
            "ORDER BY runs_in_over DESC "
            "LIMIT 5;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 107,
        "question": "Which batsman had the highest strike rate (runs per 100 balls faced) in the match and what was the strike rate?",
        "query": (
            "SELECT batsman, "
            "ROUND((SUM(batsman_runs) * 100.0) / SUM(batsman_bowls_faced), 2) AS strike_rate "
            "FROM {table_name} "
            "GROUP BY batsman "
            "ORDER BY strike_rate DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 108,
        "question": "Find the bowler with the best economy rate (runs per over) among those who bowled at least 3 overs.",
        "query": (
            "SELECT bowler, "
            "ROUND(SUM(bowler_runs_given) / (SUM(bowler_bowls_done) / 6.0), 2) AS economy_rate "
            "FROM {table_name} "
            "GROUP BY bowler "
            "HAVING SUM(bowler_bowls_done) >= 18 "
            "ORDER BY economy_rate ASC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 109,
        "question": "Which over saw the highest total number of runs scored in the match, and how many runs were scored?",
        "query": (
            "SELECT FLOOR(overs), SUM(team_runs) AS total_runs "
            "FROM {table_name} "
            "GROUP BY FLOOR(overs) "
            "ORDER BY total_runs DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 110,
        "question": "Which batsman scored the fastest 30 runs (in the fewest balls faced)?",
        "query": (
            "SELECT batsman, MIN(ball_count) AS balls_taken FROM ("
            "SELECT batsman, SUM(batsman_runs) AS total_runs, COUNT(*) AS ball_count "
            "FROM {table_name} "
            "GROUP BY batsman, overs "
            "HAVING total_runs >= 30"
            ") AS sub "
            "GROUP BY batsman "
            "ORDER BY balls_taken ASC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 111,
        "question": "What is the percentage of dot balls bowled by {bowler}?",
        "query": (
            "SELECT ROUND(100.0 * SUM(CASE WHEN team_runs = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS dot_ball_percentage "
            "FROM {table_name} "
            "WHERE bowler = '{bowler}';"
        ),
        "variables": ["table_name", "bowler"]
    },
    {
        "id": 112,
        "question": "Which batsman had the highest boundary percentage (percentage of balls faced that resulted in a four or six)?",
        "query": (
            "SELECT batsman, "
            "ROUND(100.0 * SUM(CASE WHEN batsman_runs IN (4, 6) THEN 1 ELSE 0 END) / COUNT(*), 2) AS boundary_percentage "
            "FROM {table_name} "
            "GROUP BY batsman "
            "ORDER BY boundary_percentage DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 113,
        "question": "Identify the over in which {batsman} scored the most runs and how many runs they scored in that over.",
        "query": (
            "SELECT overs, SUM(batsman_runs) AS runs_in_over "
            "FROM {table_name} "
            "WHERE batsman = '{batsman}' "
            "GROUP BY overs "
            "ORDER BY runs_in_over DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name", "batsman"]
    },
    {
        "id": 114,
        "question": "Which batsman scored the highest percentage of their runs in boundaries (fours and sixes combined)?",
        "query": (
            "SELECT batsman, "
            "ROUND(100.0 * SUM(CASE WHEN batsman_runs IN (4, 6) THEN batsman_runs ELSE 0 END) / SUM(batsman_runs), 2) AS boundary_run_percentage "
            "FROM {table_name} "
            "GROUP BY batsman "
            "ORDER BY boundary_run_percentage DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 115,
        "question": "Who was the most expensive bowler in a single over and how many runs were conceded in that over?",
        "query": (
            "SELECT bowler, overs, SUM(bowler_runs_given) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY bowler, overs "
            "ORDER BY runs_in_over DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 116,
        "question": "Which batsman had the highest average runs per over they batted in?",
        "query": (
            "SELECT batsman, "
            "ROUND(SUM(batsman_runs) / COUNT(DISTINCT FLOOR(overs)), 2) AS avg_runs_per_over "
            "FROM {table_name} "
            "GROUP BY batsman "
            "ORDER BY avg_runs_per_over DESC "
            "LIMIT 1;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 117,
        "question": "Find all batsmen who hit more than 1 sixes and how many total runs they scored.",
        "query": (
            "SELECT batsman, SUM(batsman_runs) AS total_runs, SUM(batsman_sixes) AS total_sixes "
            "FROM {table_name} "
            "GROUP BY batsman "
            "HAVING SUM(batsman_sixes) > 1 "
            "ORDER BY total_runs DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 118,
        "question": "Find bowlers who conceded more than 15 runs in any over.",
        "query": (
            "SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY bowler, FLOOR(overs) "
            "HAVING SUM(team_runs) > 15 "
            "ORDER BY runs_in_over DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 119,
        "question": "Show the total number of dot balls bowled by each bowler.",
        "query": (
            "SELECT bowler, COUNT(*) AS total_dot_balls "
            "FROM {table_name} "
            "WHERE team_runs = 0 "
            "GROUP BY bowler "
            "ORDER BY total_dot_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 120,
        "question": "Find the number of no-balls and total runs scored on them for each over.",
        "query": (
            "SELECT FLOOR(overs) AS over_number, "
            "COUNT(*) AS no_balls_delivered, "
            "SUM(team_runs) AS runs_off_no_balls "
            "FROM {table_name} "
            "WHERE runs LIKE '%nb%' "
            "GROUP BY FLOOR(overs) "
            "ORDER BY over_number;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 121,
        "question": "Which bowlers bowled the most dot balls in the match?",
        "query": (
            "SELECT bowler, COUNT(*) AS total_dot_balls "
            "FROM {table_name} "
            "WHERE team_runs = 0 "
            "GROUP BY bowler "
            "ORDER BY total_dot_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 122,
        "question": "Which bowlers conceded the most no-balls and how many runs came off them?",
        "query": (
            "SELECT bowler, COUNT(*) AS no_balls_delivered, SUM(team_runs) AS runs_off_no_balls "
            "FROM {table_name} "
            "WHERE runs LIKE '%nb%' "
            "GROUP BY bowler "
            "ORDER BY runs_off_no_balls DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 123,
        "question": "Which bowlers conceded the most wides?",
        "query": (
            "SELECT bowler, COUNT(*) AS wides_delivered "
            "FROM {table_name} "
            "WHERE runs LIKE '%w%' "
            "GROUP BY bowler "
            "ORDER BY wides_delivered DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 124,
        "question": "In which overs did each bowler concede more than 10 runs?",
        "query": (
            "SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS runs_in_over "
            "FROM {table_name} "
            "GROUP BY bowler, FLOOR(overs) "
            "HAVING SUM(team_runs) > 10 "
            "ORDER BY runs_in_over DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 125,
        "question": "Which bowlers took wickets and how many runs did they concede?",
        "query": (
            "SELECT bowler, SUM(bowler_wickets) AS total_wickets, SUM(bowler_runs_given) AS runs_conceded "
            "FROM {table_name} "
            "WHERE bowler_wickets > 0 "
            "GROUP BY bowler "
            "ORDER BY total_wickets DESC, runs_conceded ASC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 126,
        "question": "Which bowlers had an over where they conceded a six or a four or a no-ball, and how many runs did they concede in that over?",
        "query": (
            "SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS total_runs_in_over "
            "FROM {table_name} "
            "GROUP BY bowler, FLOOR(overs) "
            "HAVING SUM(batsman_sixes) >= 1 "
            "OR SUM(batsman_fours) >= 1 "
            "OR SUM(CASE WHEN runs LIKE '%nb%' THEN 1 ELSE 0 END) >= 1 "
            "ORDER BY total_runs_in_over DESC;"
        ),
        "variables": ["table_name"]
    },
    {
        "id": 127,
        "question": "For each bowler, find their best and worst over by runs conceded and show the difference.",
        "query": (
            "WITH bowler_over_summary AS ( "
            "    SELECT bowler, FLOOR(overs) AS over_number, SUM(team_runs) AS runs_in_over "
            "    FROM {table_name} "
            "    GROUP BY bowler, FLOOR(overs) "
            "), "
            "min_max_runs AS ( "
            "    SELECT bowler, MIN(runs_in_over) AS best_over_runs, MAX(runs_in_over) AS worst_over_runs "
            "    FROM bowler_over_summary "
            "    GROUP BY bowler "
            ") "
            "SELECT bowler, best_over_runs, worst_over_runs, (worst_over_runs - best_over_runs) AS run_difference "
            "FROM min_max_runs "
            "ORDER BY run_difference DESC;"
        ),
        "variables": ["table_name"]
    }

]