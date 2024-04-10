from requests import get
from colorama import Fore, Back, Style
import json
import time

IP          = "77.86.35.231:25580"
PORT        = "25580"
SOCKET      = IP + ":" + PORT
API_PREFIX  = "https://api.mcsrvstat.us"
API_VERSION = 3
API_URL     = API_PREFIX + "/" + str(API_VERSION) + "/" + SOCKET
CPM         = 0.2 # Coins per minute

online = []


def api_call(): # Returns a JSON of data from the server API
    response = get(API_URL)
    data = response.text
    return json.loads(data)

def get_player_list(): # Returns a list of currently online players
    data = api_call()
    if data["players"]["online"] == 0: # Handling case where the list of players doesn't exist
        return []
    return data["players"]["list"]
        
def log_off(player): # Calculates Crazy Coins to award and removes player from list of online players
    online.pop(online.index(player))
    coins = 0
    time_played = time.time() - player["log_on_time"]
    coins += int(time_played * CPM)
    tprint(f"{player["name"]} has left the game. Earning {coins} Crazy Coins")

def tprint(message):
    now = time.strftime("[%H:%M:%S]")
    print(Fore.GREEN + now, Style.RESET_ALL + message)


def update_player_list(): # Updates the array of currently online players.
    fetch = get_player_list()

    cache = online
    for player in cache: # Logging off players
        found = False
        for record in fetch: # Linear search to try to find player in fetched list
            if record["name"] == player["name"]:
                found = True
                break

        if not found:
            log_off(player)

    for record in fetch: # Logging on players
        found = False
        for player in online: # Linear search to try to find record in player list
            if record["name"] == player["name"]:
                found = True
                break

        if not found:
            tprint(f"{record["name"]} has joined the game")
            record["log_on_time"] = time.time()
            online.append(record)


while True:
    update_player_list()
    time.sleep(30)
