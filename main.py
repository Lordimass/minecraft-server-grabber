from requests import get
from colorama import Fore, Back, Style
from threading import Thread
import json
import time

IP          = "77.86.35.231:25580"
PORT        = "25580"
SOCKET      = IP + ":" + PORT
API_PREFIX  = "https://api.mcsrvstat.us"
API_VERSION = 3
API_URL     = API_PREFIX + "/" + str(API_VERSION) + "/" + SOCKET

CPM         = 0.2 # Coins per minute
DAILY_BONUS = 10
DAILY_MULTIPLIER = 1.3

keep_checking = True

online = []


def api_call(): # Returns a JSON of data from the server API
    response = get(API_URL)
    data = response.text
    return json.loads(data)

def get_player_list(): # Returns a list of currently online players
    data = api_call()
    if data["players"]["online"] == 0 or data["online"] == False: # Handling case where the list of players doesn't exist or the server is offline.
        return []
    return data["players"]["list"]
        
def log_off(player): # Calculates Crazy Coins to award and removes player from list of online players
    online.pop(online.index(player))
    time_played = time.time() - player["log_on_time"]
    coins = int((time_played/60) * CPM)
    tprint(f"{player['name']} has left the game. Earning {coins} Crazy Coins")
    give_coins(player["name"], coins)

def give_coins(name, amount): # Gives coins to a specified player
    amount = int(amount)
    tprint(f"Giving {amount}CC to {name}")

def tprint(message): # Prefixes print message with a timestamp
    now = time.strftime("[%H:%M:%S]")
    print(Fore.GREEN + Style.BRIGHT + now, Style.RESET_ALL + message)

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
            tprint(f"{record['name']} has joined the game")
            record["log_on_time"] = time.time()
            online.append(record)
    
    update_streaks()

def days_since(timestamp): # Calculates how many full days it has been since a given timestamp
    S = 86400
    epoch_daystamp = timestamp//S
    epoch_todaystamp = time.time()//S
    return epoch_todaystamp - epoch_daystamp

def update_streaks(): # Updates user log on streaks 
    j = open("streaks.json")
    streaks = json.load(j)["players"]
    j.close()

    for player in online:
        found = False
        for entry in streaks:
            if player["name"] == entry["name"]:
                found = True
                break
        if not found:
            new_entry = player.copy()
            del new_entry["log_on_time"]
            new_entry["last_log_in"] = time.time()
            new_entry["streak"] = 1
            streaks.append(new_entry)
            give_coins(new_entry["name"], DAILY_BONUS)
        if found:
            days = days_since(entry["last_log_in"])
            if days == 1:
                entry["streak"] += 1
            elif days > 1:
                entry["streak"] = 1

            entry["last_log_in"] = time.time()
            give_coins(entry["name"], DAILY_BONUS*DAILY_MULTIPLIER**(entry["streak"]-1))

    j = open("streaks.json", "w")
    json.dump({"players": streaks}, j)
    j.close()
    
def mainloop():
    tprint("Started checking for players")
    start_time = time.time()
    while keep_checking:
        update_player_list()
        time.sleep(30)
    tprint(f"Stopped checking for players. The function was checking for {round((time.time() - start_time)/60)} minute(s).")


thread = Thread(name="mainloop", target=mainloop)
thread.start()
input()
tprint("Process interrupted, finishing cycle")
keep_checking = False