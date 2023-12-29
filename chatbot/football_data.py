import os

import pytz
import requests
from tqdm import tqdm

from headers import *
from datetime import datetime
from fuzzywuzzy import fuzz
import json

MAX_RATIO = 90
words_to_remove = [
    "CF",
    "SC",
    "GD",
    "FC",
    "AFC",
    "AFC",
    "AS",
    "UD",
    "CF",
    "US",
    "AC",
    "AS",
    "&",
    ".",
    "'",
    "-"
]


def call_api(endpoint):
    base_url = 'https://api.football-data.org/v4/'
    url = base_url + endpoint
    response = requests.get(url, headers=headers)
    return response


def format_date(date_str):
    cleaned_date_str = date_str.replace("T", " ").replace("Z", "")
    date_obj = datetime.strptime(cleaned_date_str, '%Y-%m-%d %H:%M:%S')

    utc = pytz.timezone('UTC')

    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    date_obj = utc.localize(date_obj).astimezone(timezone)

    formatted_date = date_obj.strftime('%H:%M %d-%m-%Y')
    return formatted_date


def get_upcoming_matches():
    match_list = []

    response = call_api('matches')

    if response.status_code == 200:
        matches_data = response.json()

        if 'matches' in matches_data:
            for match in matches_data['matches']:
                match_date_iso = match['utcDate']
                match_date = format_date(match_date_iso)

                competition_name = match['competition']['name']
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']

                match_data = f"{match_date} - {competition_name}: {home_team} vs {away_team}"

                match_list.append(match_data)

    return match_list


def get_standings(competition_code, season):
    standings_results = []
    response = call_api(f'competitions/{competition_code}/standings?season={season}')
    if response.status_code == 200:

        standings_data = response.json()

        if 'standings' in standings_data:

            for standing in standings_data['standings']:
                if standing['type'] == 'TOTAL':
                    table = standing['table']
                    for entry in table:
                        position = entry['position']
                        team_name = entry['team']['name']
                        points = entry['points']
                        played_games = entry['playedGames']

                        standing_result = {
                            "Position": position,
                            "Team": team_name,
                            "Played": played_games,
                            "Points": points
                        }

                        standings_results.append(standing_result)

    return standings_results


def get_competition_info(competition_name, file_path='../data/all_competitions_data.json'):
    competition_code = None
    competition_name_returned = None

    # Load data from the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    leagues = data['leagues']
    for league in leagues:
        current_ratio = fuzz.ratio(competition_name.lower(), league['name'].lower())
        if current_ratio > MAX_RATIO:
            competition_code = league['id']
            competition_name_returned = league['name']
            break
    return competition_name_returned, competition_code


def get_teams_list(competition_name):
    competition_name, competition_code = get_competition_info(competition_name)
    teams = []

    if competition_code is not None:
        response = call_api(f'competitions/{competition_code}/teams')

        if response.status_code == 200:
            teams_data = response.json()

            if 'teams' in teams_data:
                for team in teams_data['teams']:
                    name = team['name']
                    tla = team['tla']
                    id = team['id']

                    team_result = {
                        'id': id,
                        'name': name,
                        'tla': tla
                    }
                    teams.append(team_result)
            teams.sort(key=lambda x: x['name'])
            return competition_name, teams
    return competition_name, teams


def get_team_info(team_name, file_path='../data/all_teams_data.json'):
    team_id = None
    team_name_returned = None

    # Load data from the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for team_data in data:
        teams = team_data['teams']
        for team in teams:
            team_name_processed = team['name']
            for word in words_to_remove:
                team_name_processed = team_name_processed.replace(word, "").strip()
            current_ratio = fuzz.ratio(team_name.lower(), team_name_processed.lower())
            if current_ratio > MAX_RATIO:
                team_id = team['id']
                team_name_returned = team['name']
                break

    return team_name_returned, team_id


def get_next_matches_of_team(team_id, limit=5):
    endpoint = f'teams/{team_id}/matches'
    matches = []

    query_params = f'status=SCHEDULED&limit={limit}'
    response = call_api(endpoint + '?' + query_params)

    if response.status_code == 200:
        data = response.json()['matches']

        for match in data:
            match_date_iso = match['utcDate']
            match_date = format_date(match_date_iso)

            competition_name = match['competition']['name']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']

            match_data = f"{match_date} - {competition_name}: {home_team} vs {away_team}"

            matches.append(match_data)

    return matches


def get_last_matches_of_team(team_id, limit=5):
    endpoint = f'teams/{team_id}/matches'
    recent_matches = []

    response = call_api(endpoint)

    if response.status_code == 200:
        data = response.json()['matches']

        for match in data:
            match_date_iso = match['utcDate']
            match_date = format_date(match_date_iso)
            if match['status'] == "FINISHED":
                competition_name = match['competition']['name']
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']

                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']

                match_data = f"{match_date} - {competition_name}: {home_team} {home_score} - {away_score} {away_team}"
                recent_matches.append(match_data)
        recent_matches = recent_matches[-limit:]
        return recent_matches


def get_next_matches_of_league(competition_code):
    today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    season = today.year
    next_matches = []

    if not check_season_exists(competition_code, str(season)):
        season -= 1

    endpoint = f"competitions/{competition_code}/matches?season={season}"
    response = call_api(endpoint)
    data = response.json()

    matches = data.get("matches", [])
    next_matchday_date = None
    next_matchday = None

    for match in matches:
        match_date_str = match.get("utcDate")
        match_date = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%SZ")
        match_date = match_date.replace(tzinfo=pytz.utc)
        match_date = match_date.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        match_day = match.get("matchday")

        if match_date > today and (next_matchday_date is None or match_date < next_matchday_date):
            next_matchday_date = match_date
            next_matchday = match_day

    if next_matchday is not None:
        endpoint = f"competitions/{competition_code}/matches?season={season}&matchday={next_matchday}"
        response = call_api(endpoint)
        data = response.json()
        matches = data.get("matches", [])
        next_match = matches[1] if matches else None
        next_match_status = next_match.get("status", "")
        if next_match_status == "FINISHED":
            new_matchday = next_matchday + 1
            endpoint = f"competitions/{competition_code}/matches?season={season}&matchday={new_matchday}"
            response = call_api(endpoint)
            data = response.json()
            matches = data.get("matches", [])
        matches_by_date = {}

        for match in matches:
            match_date_str = match.get("utcDate")
            match_date = format_date(match_date_str)

            if match_date not in matches_by_date:
                matches_by_date[match_date] = []

            home_team = match.get("homeTeam", {}).get("name")
            away_team = match.get("awayTeam", {}).get("name")
            match_data = f"\t{home_team} vs {away_team}"
            matches_by_date[match_date].append(match_data)

        for match_date, match_data in matches_by_date.items():
            next_matches.append(f"{match_date}:\n" + "\n".join(match_data))

    return next_matches


def get_last_matches_of_league(competition_code):
    today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    season = today.year
    latest_matches = []

    if not check_season_exists(competition_code, str(season)):
        season -= 1

    endpoint = f"competitions/{competition_code}/matches?season={season}"
    response = call_api(endpoint)
    data = response.json()

    matches = data.get("matches", [])
    latest_matchday_date = None
    latest_matchday = None

    for match in reversed(matches):
        match_date_str = match.get("utcDate", "")
        match_date = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%SZ")
        match_date = match_date.replace(tzinfo=pytz.utc)
        match_date = match_date.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
        match_day = match.get("season", {}).get("currentMatchday", 0)

        if match_date <= today and (latest_matchday_date is None or match_date >= latest_matchday_date):
            latest_matchday_date = match_date
            latest_matchday = match_day

    if latest_matchday is not None:
        endpoint = f"competitions/{competition_code}/matches?season={season}&matchday={latest_matchday}"
        response = call_api(endpoint)
        data = response.json()
        matches = data.get("matches", [])
        last_match = matches[-1] if matches else None
        last_match_status = last_match.get("status", "")

        if last_match_status != "FINISHED":
            previous_matchday = latest_matchday - 1
            endpoint = f"competitions/{competition_code}/matches?season={season}&matchday={previous_matchday}"
            response = call_api(endpoint)
            data = response.json()
            matches = data.get("matches", [])

        matches_by_date = {}

        for match in matches:
            match_date_str = match.get("utcDate", "")
            match_date = format_date(match_date_str)

            if match_date not in matches_by_date:
                matches_by_date[match_date] = []

            home_team = match.get("homeTeam", {}).get("name", "")
            away_team = match.get("awayTeam", {}).get("name", "")
            home_score = match.get("score", {}).get("fullTime", {}).get("home", "")
            away_score = match.get("score", {}).get("fullTime", {}).get("away", "")
            match_data = f"\t{home_team} {home_score} - {away_score} {away_team}"
            matches_by_date[match_date].append(match_data)

        for match_date, match_data in matches_by_date.items():
            latest_matches.append(f"{match_date}:\n" + "\n".join(match_data))

    return latest_matches


def get_top_scorers_league(competition_code, season):
    top_scorers = []

    endpoint = f'competitions/{competition_code}/scorers'
    query_params = f'season={season}'
    response = call_api(endpoint + '?' + query_params)

    if response.status_code == 200:
        scorers_data = response.json()

        if 'scorers' in scorers_data:
            for scorer in scorers_data['scorers']:
                player_name = scorer['player']['name']
                team_name = scorer['team']['name']
                goals = scorer['goals']

                top_scorer = {
                    "Player": player_name,
                    "Team": team_name,
                    "Goals": goals
                }

                top_scorers.append(top_scorer)

    return top_scorers


def get_players_data(team_name):
    team_name, team_id = get_team_info(team_name)
    age = None
    if team_id is not None:
        players = []

        response = call_api(f'teams/{team_id}')

        if response.status_code == 200:
            team_data = response.json()
            if 'squad' in team_data:
                current_date = datetime.now()

                for player in team_data['squad']:
                    player_name = player['name']
                    position = player.get('position', 'Unknown')
                    date_of_birth_str = player.get('dateOfBirth', 'Unknown')
                    nationality = player.get('nationality', 'Unknown')
                    number_shirt = player.get('shirtNumber', 'Unknown')

                    if date_of_birth_str != 'Unknown':
                        date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
                        age = current_date.year - date_of_birth.year

                    player_info = {
                        'Player Name': player_name,
                        'Position': position,
                        'Date of Birth': date_of_birth_str,
                        'Nationality': nationality,
                        'Age': age,
                        'Number': number_shirt
                    }

                    players.append(player_info)

        return team_name, team_id, players

    return []


def get_coach_info(team_name):
    team_name, team_id = get_team_info(team_name)

    if team_id is not None:
        response = call_api(f'teams/{team_id}')

        if response.status_code == 200:
            team_data = response.json()
            coach_info = team_data.get('coach', {})

            first_name = coach_info.get('firstName', '')
            last_name = coach_info.get('lastName', '')

            coach_name = f"{first_name} {last_name}".strip()

            return team_name, team_id, coach_name

    return 'Unknown'


def check_season_exists(competition_code, season):
    response = call_api(f'competitions/{competition_code}')
    if response.status_code == 200:
        seasons_data = response.json()
        season_list = [season_data['startDate'][:4] for season_data in seasons_data.get('seasons', [])]
        return season in season_list
    return False


def export_teams_data_to_json(output_file_path='../data/all_teams_data.json'):
    with open('../data/all_competitions_data.json') as f:
        competitions_data = json.load(f)

    leagues = competitions_data.get('leagues', [])

    all_teams_data = []
    teams = []

    for league in tqdm(leagues, desc='Exporting data', unit=' leagues'):
        if 'id' in league:
            response = call_api(f'competitions/{league["id"]}/teams')

            if response.status_code == 200:
                teams_data = response.json()

                if 'teams' in teams_data:
                    for team in teams_data['teams']:
                        name = team.get('name', '')
                        tla = team.get('tla', '')
                        team_id = team.get('id', '')

                        if not any(existing_team['id'] == team_id for existing_team in teams):
                            team_result = {
                                'id': team_id,
                                'name': name,
                                'tla': tla
                            }
                            teams.append(team_result)

    teams.sort(key=lambda x: x['name'])

    all_teams_data.append({'teams': teams})

    if os.path.isfile(output_file_path):
        user_response = input("The file already exists. Do you want to overwrite it? (Yes/No): ").lower()

        if user_response == 'yes':
            with tqdm(total=1, desc='Writing data', unit=' file', bar_format='{l_bar}{bar}') as pbar:
                with open(output_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(all_teams_data, json_file, ensure_ascii=False, indent=2)
                pbar.update(1)
            print(f'Data overwritten in {output_file_path}')
        else:
            new_file_path = input("Enter a new file name: ")
            with tqdm(total=1, desc='Writing data', unit=' file', bar_format='{l_bar}{bar}') as pbar:
                with open(new_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(all_teams_data, json_file, ensure_ascii=False, indent=2)
                pbar.update(1)
            print(f'Data saved to {new_file_path}')
    else:
        with tqdm(total=1, desc='Writing data', unit=' file', bar_format='{l_bar}{bar}') as pbar:
            with open(output_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(all_teams_data, json_file, ensure_ascii=False, indent=2)
            pbar.update(1)
        print(f'Data saved to {output_file_path}')
