# a simple slots game

import random
import colorama
from colorama import Fore, Back, Style
import sys
import json
import os

colorama.init(autoreset=True)

# File to store player data
SAVE_FILE = "player_data.json"

# Simple safe integer input helper

def prompt_int(prompt, min_val=None, max_val=None):
    while True:
        raw = input(prompt)
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(Fore.YELLOW + f"Please enter a number >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(Fore.YELLOW + f"Please enter a number <= {max_val}.")
                continue
            return val
        except ValueError:
            print(Fore.YELLOW + "Please enter a valid whole number.")

# Utility: load all players safely

def load_all_players():
    """Load all player records from disk safely. Returns dict[name] -> data."""
    all_players = {}
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    all_players = json.loads(content)
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file; start fresh in-memory
            all_players = {}
    return all_players

# Leaderboard helpers

def get_leaderboard(top_n=10):
    """Return a list of (name, high_score, wins, games_played) sorted by high_score desc."""
    players = load_all_players()
    items = []
    for name, data in players.items():
        items.append((name, int(data.get("high_score", 0)), int(data.get("wins", 0)), int(data.get("games_played", 0))))
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top_n]


def print_leaderboard(top_n=10):
    board = get_leaderboard(top_n)
    print("\n=== LEADERBOARD (Top {} by High Score) ===".format(top_n))
    if not board:
        print("No scores yet. Be the first to play!")
        return
    for idx, (pname, score, wins, games) in enumerate(board, start=1):
        print(f"{idx}. {pname:15}  High Score: ${score:<8}  W:{wins}  G:{games}")
    print("=== End Leaderboard ===\n")

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
    """Save player data to file safely, merging with existing players."""
    # Load existing data first (safe)
    all_players = load_all_players()

    # Update with current player
    all_players[player_data.get("name", "Unknown")] = player_data

    # Save back to file
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(all_players, f, indent=4)
    except OSError:
        # As a fallback, try to at least write the single player entry
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump({player_data.get("name", "Unknown"): player_data}, f, indent=4)
        except OSError:
            pass

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

# Offer to show leaderboard
view = input("Would you like to view the LEADERBOARD? yes/no ")
if view.strip().lower().startswith('y'):
    print_leaderboard(10)

# play = input("What slot would you like to play 1, 2 3?")
# print("You chose " + play)

def slots(player):
    # Work with the player's current balance and stats
    cashBal = player.get("balance", 1000)

    addCash = input("Would you like to add cash? yes/no ")
    if addCash.strip().lower().startswith("y"):
        addCashAmt = prompt_int("How much would you like to add? ", min_val=1)
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
    addMagicNumber = input("Would you like to buy a magic number for $100 X your magic number? yes/no ")
    if addMagicNumber.strip().lower().startswith("y"):
        magicNumber = prompt_int("What is your magic number? 1-7 ", min_val=1, max_val=7)
        cost = magicNumber * 100
        if cashBal < cost:
            print(Fore.YELLOW + f"Insufficient funds for magic number {magicNumber}. Cost is ${cost}, balance is ${cashBal}. Skipping purchase.")
            magicNumber = None
        else:
            cashBal -= cost
            # Persist balance change after purchasing magic number
            player["balance"] = cashBal
            save_player_data(player)
    else:
        print("You chose not to buy a magic number")

    while cashBal > 0:

        print(Fore.CYAN + f"Current balance: ${cashBal}")
        bet = prompt_int("How much money do you want to bet? ", min_val=1, max_val=cashBal)
        print("You bet " + str(bet))

        magicNumberChoice = input("Would you like to use your magic number multiplier? yes/no ")
        if magicNumberChoice.strip().lower().startswith("y"):
            if magicNumber is not None:
                if bet * magicNumber <= cashBal:
                    bet *= magicNumber
                    print(Fore.MAGENTA + f"Magic multiplier x{magicNumber} applied. New bet: ${bet}")
                else:
                    print(Fore.YELLOW + f"Not enough balance to apply x{magicNumber}. Bet remains ${bet}.")
            else:
                print(Fore.YELLOW + "No magic number purchased; multiplier not applied.")

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

    # Notify if out of funds
    if cashBal <= 0:
        print(Fore.RED + "You're out of funds. Add cash to keep playing next time.")

    # After session ends, persist final balance and offer leaderboard
    player["balance"] = cashBal
    if cashBal > player.get("high_score", 0):
        player["high_score"] = cashBal
    save_player_data(player)
    print(f"\nSession ended. Final balance: ${cashBal}")
    see = input("View the LEADERBOARD now? yes/no ")
    if see.strip().lower().startswith('y'):
        print_leaderboard(10)


slots(player)

