# a simple slots game

import random
import colorama
from colorama import Fore, Back, Style
import sys
import json
import os

# File to store player data
SAVE_FILE = "player_data.json"

# """Load player data from file, or create new player"""

def load_player_data(name):
    """Load player data from file, or create new player"""
    all_players = {}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    all_players = json.loads(content)
                else:
                    all_players = {}
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file; start fresh in-memory
            all_players = {}
    if name in all_players:
        return all_players[name]
    # Return new player data if not found
    return {
        "name": name,
        "balance": 1000,
        "wins": 0,
        "losses": 0,
        "high_score": 0,
        "games_played": 0
    }

def save_player_data(player_data):
    """Save player data to file"""
    all_players = {}

# Load existing data first
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            all_players = json.load(f)

    # Update with current player
    all_players[player_data["name"]] = player_data

    # Save back to file
    with open(SAVE_FILE, 'w') as f:
        json.dump(all_players, f, indent=4)

print("Welcome to Sam's Slots")
name = input("What is your name?")
print("Hello " + name)
print("Loading account information...")
# cashBal = 1000
# print(Fore.GREEN + "Account balance: ", cashBal)

# Load or create player
player = load_player_data(name)
print(f"\nWelcome back, {name}!")
print(f"Balance: ${player['balance']}")
print(f"Win/Loss Record: {player['wins']}W - {player['losses']}L")
print(f"High Score: ${player['high_score']}")

# play = input("What slot would you like to play 1, 2 3?")
# print("You chose " + play)

def slots(player):
    # Work with the player's current balance and stats
    cashBal = player.get("balance", 1000)

    addCash = input("Would you like to add cash? yes/no")
    if addCash.lower() == "yes":
        addCashAmt = int(input("How much would you like to add?"))
        cashBal += addCashAmt
        print(Fore.GREEN + "You chose to add " + str(addCashAmt) + " and you have a total balance of " + str(cashBal))
        # Persist balance change
        player["balance"] = cashBal
        save_player_data(player)
    else:
        addCashAmt = 0
        print(Fore.RED + "You chose not to add cash")

    # Initialize magicNumber as None (Python's null) so we can safely check it later
    magicNumber = None
    addMagicNumber = input("Would you like to buy a magic number for $100 X your magic number? yes/no")
    if addMagicNumber.lower() == "yes":
        magicNumber = int(input("What is your magic number? 1-7"))
        # Deduct cost based on chosen magic number
        if magicNumber == 1:
            cashBal -= 100
        elif magicNumber == 2:
            cashBal -= 200
        elif magicNumber == 3:
            cashBal -= 300
        elif magicNumber == 4:
            cashBal -= 400
        elif magicNumber == 5:
            cashBal -= 500
        elif magicNumber == 6:
            cashBal -= 600
        elif magicNumber == 7:
            cashBal -= 700
        # Persist balance change after purchasing magic number
        player["balance"] = cashBal
        save_player_data(player)
    elif addMagicNumber.lower() == "no":
        print("You chose not to buy a magic number")

    while cashBal >= 0:

        bet = int(input("How much money do you want to bet?"))
        print("You bet " + str(bet))

        magicNumberChoice = input("Would you like to use your magic number mutlipier?")
        if magicNumberChoice.lower() == "yes":
            if magicNumber is not None:
                bet *= magicNumber
            else:
                print(Fore.YELLOW + "No magic number purchased; multiplier not applied.")
        # Example of checking for None (null in Python): only proceed if a magic number was chosen
        if magicNumber is not None:
            pass

        a = random.randint(1, 9)
        b = random.randint(1, 9)
        c = random.randint(1, 9)
        print(a, b, c)

        if a == b == c:
            print(Fore.GREEN + "You won BIG!")
            winnings = bet * 10  # big win multiplier
            cashBal += winnings
            # Update player stats
            player["wins"] = player.get("wins", 0) + 1
            player["games_played"] = player.get("games_played", 0) + 1
            player["balance"] = cashBal
            if cashBal > player.get("high_score", 0):
                player["high_score"] = cashBal
            save_player_data(player)
            print(Fore.GREEN + "You won " + str(winnings) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game.lower() == "yes":
                continue
            else:
                break
        elif a == b or a == c or b == c:
            print(Fore.GREEN + "You won!")
            winnings = bet * 3  # small win multiplier
            cashBal += winnings
            # Update player stats
            player["wins"] = player.get("wins", 0) + 1
            player["games_played"] = player.get("games_played", 0) + 1
            player["balance"] = cashBal
            if cashBal > player.get("high_score", 0):
                player["high_score"] = cashBal
            save_player_data(player)
            print(Fore.GREEN + "You won " + str(winnings) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game.lower() == "yes":
                continue
            else:
                break
        else:
            print("You lost!")
            cashBal -= bet
            # Update player stats
            player["losses"] = player.get("losses", 0) + 1
            player["games_played"] = player.get("games_played", 0) + 1
            player["balance"] = cashBal
            if cashBal > player.get("high_score", 0):
                player["high_score"] = cashBal
            save_player_data(player)
            print(Fore.RED + "You lost " + str(bet) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game.lower() == "yes":
                continue
            else:
                break


slots(player)

