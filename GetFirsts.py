import requests
from datetime import datetime
import time
import os
import json
from API_KEY import API_KEY

URL = "https://americas.api.riotgames.com/"
ARENA_QUEUE_ID = 1700
game_name = "Price"
tag_line = "ecirp"
check_number_of_matches = 200
epoch_time_march_1st = int((datetime(2024, 3, 1) - datetime(1970, 1, 1)).total_seconds())
file_path_output = "sorted_champions.txt"
start_spot = 0
MATCH_IDS_FOLDER = "match_ids"


def get_riot_account(game_name, tag_line):
    api_url = "riot/account/v1/accounts/by-riot-id/"
    endpoint = f"{URL}{api_url}{game_name}/{tag_line}"
    
    headers = {
        "X-Riot-Token": API_KEY
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
        
def get_match_ids(puuid, n):
    api_url = "lol/match/v5/matches/by-puuid/"
    params = {
        "start": start_spot,  # Start index for pagination
        "count": 100  # Number of matches per page
    }
    headers = {
        "X-Riot-Token": API_KEY
    }
    match_ids = []

    for _ in range(n):
        endpoint = f"{URL}{api_url}{puuid}/ids?start={params["start"]}&count={params["count"]}&queue={ARENA_QUEUE_ID}&startTime={epoch_time_march_1st}"
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            match_ids.extend(data)
            params["start"] += 100  # Increment start index for next page
        else:
            print(f"Error: {response.status_code}")
            break

    return match_ids
    
    
def get_match_data_from_matchId(match_id):
    # check local first
    
    file_path = os.path.join(MATCH_IDS_FOLDER, f"{match_id}.json")
    if os.path.exists(file_path):
        # If the file exists, read from it
        with open(file_path, "r") as file:
            return json.load(file)
            
    api_url = "lol/match/v5/matches/"
    endpoint = f"{URL}{api_url}{match_id}"
    
    headers = {
        "X-Riot-Token": API_KEY
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        # Write the response to the file
        with open(file_path, "w") as file:
            json.dump(response.json(), file)
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
    
def get_winning_champions_from_match_datas(match_datas):
    winning_champions = []
    for match_data in match_datas:
        participants = match_data.get("info").get("participants")
        for participant in participants:
            if(participant["puuid"] == puuid and participant["placement"] == 1):
                winning_champions.append(participant["championName"])
    return winning_champions
    
    

if not os.path.exists(MATCH_IDS_FOLDER):
    os.makedirs(MATCH_IDS_FOLDER)
riot_account = get_riot_account(game_name, tag_line)
puuid = riot_account["puuid"]
match_ids = get_match_ids(puuid, (check_number_of_matches + 100)//100)
print(f"checking {len(match_ids)} matches")
matches = []
num_matches_gotten = 0
for match_id in match_ids[0:check_number_of_matches]:
    print(match_id)
    match = get_match_data_from_matchId(match_id)
    matches.append(match)
    num_matches_gotten += 1
    print(f"Done with {num_matches_gotten} out of {len(match_ids)}")
winning_champions = set(get_winning_champions_from_match_datas(matches))
print(f"Number of winning champions {len(winning_champions)}")
print(f"Winning champions: {sorted(winning_champions)}")
with open(file_path_output, 'w') as file:
    file.truncate(0)
    file.write(f"Total unique wins: {len(winning_champions)}\n")
    # Write each champion name to the file
    previous_champion = "Z"
    for champion in sorted(winning_champions):
        champion = champion if champion != "MonkeyKing" else "Wukong"
        if(previous_champion[0] != champion[0]):
            file.write("\n")
        else:
            file.write(", ")
        file.write(champion)
        previous_champion = champion
print("Sorted champions have been written to", file_path_output)
input("Press Enter to exit...")