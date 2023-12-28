from football_data import *
import random

cup_id = ["WC", "CLI", "EC", "CL"]
league_cup_id = ["CLI", "CL"]

bot_name = "Johan Cruyff"


def handle_intent(intent, tag):
    if tag == 'UpcomingFixtures':
        handle_upcoming_fixtures(intent)
    elif tag == 'FixturesLeagues':
        handle_fixtures_leagues(intent)
    elif tag == 'FixturesTeam':
        handle_fixtures_team(intent)
    elif tag == 'Table':
        handle_table(intent)
    elif tag == 'LastRoundResult':
        handle_last_round_result(intent)
    elif tag == 'ResultsOfTeam':
        handle_result_team(intent)
    elif tag == 'TopScorer':
        handle_top_scorer(intent)
    elif tag == 'TeamOfLeague':
        handle_team_of_league(intent)
    elif tag == 'CoachOfTeam':
        handle_coach_of_team(intent)
    elif tag == 'PlayersOfTeam':
        handle_players_of_team(intent)
    else:
        if 'responses' in intent:
            handle_other(intent)


def handle_last_round_result(intent):
    print(f"{bot_name}: You've asked for the last round's result of a specific league.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
    if competition_code is not None:
        results_of_team = get_last_matches_of_league(competition_code)
        if results_of_team is not None:
            results_text = "\n".join(results_of_team)
            print(f"{bot_name}: {header} of {competition_name_input} league:")
            print(f"\n{results_text}")
        else:
            print(f"{bot_name}: Sorry! I do not have data about your concerns...")
    else:
        print(f"{bot_name}: Sorry! I do not have data about your concerns...")


def handle_result_team(intent):
    print(f"{bot_name}: You've inquired about the recent results of a club.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    if competition_code is not None:
        print(f"{bot_name}: Which team in {competition_name_input} you want to know the "
              f"results?")
        team_name_input = input("You: ")
        team_name_input, team_id = get_team_info(competition_name_input, team_name_input)
        print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
        if team_id is not None:
            results_of_team = get_last_matches_of_team(team_id)
            if results_of_team is not None:
                results_text = "\n".join(results_of_team)
                print(f"{bot_name}: {header}")
                print(f"\n{results_text}")
            else:
                print(f"{bot_name}: Sorry! I do not have data about your concerns...")
        else:
            print(f"{bot_name}: Can not found {team_name_input} in {competition_name_input}...")
            print(f"{bot_name}: You can ask me about the team name of a specific league(e.g., 'Teams "
                  f"in leagues')")
    else:
        print(f"Sorry!{competition_name_input} is invalid league...")


def handle_upcoming_fixtures(intent):
    print(f"{bot_name}: You've asked for the upcoming match schedule.")
    print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
    header = random.choice(intent['responses'])
    matches_list = get_upcoming_matches()
    if matches_list is not None:
        results_text = "\n".join(matches_list)
        print(f"{bot_name}: {header}")
        print(f"\n{results_text}")
    else:
        print(f"{bot_name}: Sorry! I do not have data about your concerns...")


def handle_fixtures_leagues(intent):
    print(f"{bot_name}: Your request for the upcoming match schedule of a specific league has been "
          f"received.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
    if competition_code is not None:
        matches_list = get_next_matches_of_league(competition_code)
        if matches_list is not None:
            results_text = "\n".join(matches_list)
            print(f"{bot_name}: {header}")
            print(f"\n{results_text}")
        else:
            print(f"{bot_name}: Sorry! I do not have data about your concerns...")
    else:
        print(f"{bot_name}: Sorry! I do not update new data of {competition_name_input}...")


def handle_fixtures_team(intent):
    print(f"{bot_name}: You just requested to view the upcoming match schedule of a specific team.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])

    if competition_code is not None:
        print(f"{bot_name}: Which team in {competition_name_input} you want to know the fixtures?")
        team_name_input = input("You: ")
        team_name_input, team_id = get_team_info(competition_name_input, team_name_input)
        print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
        if team_id is not None:
            matches_list = get_next_matches_of_team(team_id)
            if matches_list is not None:
                results_text = "\n".join(matches_list)
                print(f"{bot_name}: {header}")
                print(f"\n{results_text}")
            else:
                print(f"{bot_name}: Sorry! I do not have data about your concerns...")
        else:
            print(f"{bot_name}: Can not found {team_name_input} in {competition_name_input}...")
            print(f"{bot_name}: You can ask me about the team name of a specific league(e.g., 'Teams "
                  f"in leagues')")
    else:
        print(f"Sorry!{competition_name_input} is invalid league...")


def handle_table(intent):
    print(f"{bot_name}: Thank you for your request to view a league's table.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])

    if competition_code is not None:
        season = None
        while season is None:
            print(f"{bot_name}: Please enter the data's season (e.g., '2023'): ")
            season_input = input("You: ")
            if season_input.isdigit() and len(season_input) == 4:
                season = season_input
            else:
                continue
        print(f"{bot_name}: Please wait a moment for me to retrieve the data!")

        if competition_code in cup_id:
            print(
                f"{bot_name}: Sorry! My API does not have data of each {competition_name_input}'s "
                f"table because the cup competition has many tables...")
        else:
            table_data = get_standings(competition_code, season)
            if table_data:
                print(f"{bot_name}: {header}")
                print(f"{'Position':<10}{'Team':<30}{'Played':^10}{'Points'}")

                for entry in table_data:
                    print(
                        f"{entry['Position']:<10}{entry['Team']:<30}{entry['Played']:^10}{entry['Points']}")
            else:
                print(f"{bot_name}: Sorry! I do not have data of {competition_name_input}...")
    else:
        print(f"{bot_name}: Sorry! I do not have data of {competition_name_input}...")


def handle_top_scorer(intent):
    print(f"{bot_name}: You've asked for the top 10 goal scorer of a specific league.")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])

    if competition_code is not None:
        season = None
        previous_goals = None
        rank = 0
        while season is None:
            print(f"{bot_name}: Please enter the data's season (e.g., '2023'): ")
            season_input = input("You: ")
            if season_input.isdigit() and len(season_input) == 4:
                season = season_input
            elif season_input == 'Quit'.lower():
                break
            else:
                print(f"{bot_name}: The format of the season is invalid!. Please enter the season again.")
                print(f"{bot_name}: If you want to exit this query, type 'quit'!")
                continue
            print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
            if competition_code in cup_id not in league_cup_id:
                if check_season_exists(competition_code, season):
                    top_scorers_data = get_top_scorers_league(competition_code, season)
                    if top_scorers_data:
                        print(f"{bot_name}: {header}")
                        print(
                            f"{'Rank':<10}{'Player/Club':<45}{'Goals':<15}")
                        for entry in top_scorers_data:
                            player_name = entry.get('Player')
                            goals = entry.get('Goals')
                            team_name = entry.get('Team')
                            if goals != previous_goals:
                                rank += 1
                            formatted_player = f"{player_name}/{team_name}"
                            print(
                                f"{rank:<10}{formatted_player:<45}{goals:<15}")
                            previous_goals = goals
                    else:
                        print(f"{bot_name}: Sorry! I do not have data of {competition_name_input}...")
                else:
                    print(f"{bot_name}: {competition_name_input} was not held in {season}!")
            else:
                top_scorers_data = get_top_scorers_league(competition_code, season)
                if top_scorers_data:
                    print(f"{bot_name}: {header}")
                    print(
                        f"{'Rank':<10}{'Player/Club':<45}{'Goals':<15}")
                    for entry in top_scorers_data:
                        player_name = entry.get('Player')
                        goals = entry.get('Goals')
                        team_name = entry.get('Team')
                        if goals != previous_goals:
                            rank += 1
                        formatted_player = f"{player_name}/{team_name}"
                        print(
                            f"{rank:<10}{formatted_player:<45}{goals:<15}")
                        previous_goals = goals
                else:
                    print(f"Sorry! I do not have data about top scorer of {competition_name_input} league...")
    else:
        print(f"Sorry! I do not have data of {competition_name_input}...")


def handle_team_of_league(intent):
    print(f"{bot_name}: You've asked for all team's name of a league.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
    if competition_code is not None:
        _, team_data = get_teams_list(competition_name_input)
        if team_data:
            print(f"{bot_name}: {header}")
            print(f"{'Name Club':<30}{'Short name':<10}")
            for team in team_data:
                print(f"{team['name']:<30} {team['tla']:<10}")
        else:
            print(f"Sorry! I do not have data of {competition_name_input}...")
    else:
        print(f"Sorry! I do not have data of {competition_name_input}...")


def handle_coach_of_team(intent):
    print(f"{bot_name}: You've inquired about the coach's name of a club.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    if competition_code is not None:
        print(f"{bot_name}: Which team in {competition_name_input} you want to know the "
              f"coach info?")
        team_name_input = input("You: ")
        team_name_input, team_id = get_team_info(competition_name_input, team_name_input)
        print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
        if team_id is not None:
            _, _, coach_name = get_coach_info(competition_name_input, team_name_input)
            print(f"{bot_name}: {header}")
            if coach_name != 'Unknown':
                print(f"{bot_name}: Coach of {team_name_input} in {competition_name_input}: {coach_name}.")
            else:
                print(f"{bot_name}: Coach information not found for {team_name_input} in {competition_name_input}.")
        else:
            print(f"{bot_name}: Can not found {team_name_input} in {competition_name_input}...")
            print(f"{bot_name}: You can ask me about the team name of a specific league(e.g., 'Teams "
                  f"in leagues')")
    else:
        print(f"Sorry!{competition_name_input} is invalid league...")


def handle_players_of_team(intent):
    print(f"{bot_name}: You've asked for the squad of a team.")
    print(f"{bot_name}: Can you let me know the competition name, please?")
    competition_name_input = input("You: ")
    competition_name_input, competition_code = get_competition_info(competition_name_input)
    header = random.choice(intent['responses'])
    if competition_code is not None:
        print(f"{bot_name}: Which team in {competition_name_input} you want to know "
              f"players info?")
        team_name_input = input("You: ")
        team_name_input, team_id = get_team_info(competition_name_input, team_name_input)
        print(f"{bot_name}: Please wait a moment for me to retrieve the data!")
        if team_id is not None:
            team_name_input, team_id, players = get_players_data(competition_name_input, team_name_input)
            if players:
                print(f"{bot_name}: {header}")
                position_mapping = {
                    "Goalkeeper": "Gk",
                    "Defence": "DF",
                    "Midfield": "MF",
                    "Offence": "FW"
                }
                print("{:<15} {:<45} {:<30} {:<15}".format("Position", "Name",
                                                           "Nationality", "Age"))
                for position in position_mapping:
                    sorted_players = [player for player in players if player['Position'] == position]
                    if sorted_players:
                        for player in sorted_players:
                            position_abbreviation = position_mapping[position]
                            print("{:<15} {:<45} {:<30} {:<15}".format(position_abbreviation,
                                                                       player['Player Name'],
                                                                       player['Nationality'],
                                                                       player['Age']))
            else:
                print(f"{bot_name}: No player information found for {team_name_input} in {competition_name_input}.")
        else:
            print(f"{bot_name}: Can not find {team_name_input} in {competition_name_input}...")
            print(f"{bot_name}: You can ask me about the team name of a specific league(e.g., 'Teams "
                  f"in leagues')")
    else:
        print(f"{bot_name}: Sorry! {competition_name_input} is invalid league...")


def handle_other(intent):
    print(f"{bot_name}: {random.choice(intent['responses'])}")
