# a simple slots game

import random
import colorama
from colorama import Fore, Back, Style
import sys


print("Welcome to Sam's Slots")
name = input("What is your name?")
print(Fore.CYAN + "Hello " + name)
print(Fore.YELLOW + "Loading account information...")
cashBal = 1000
print(Fore.GREEN + "Account balance: ", cashBal)


# play = input("What slot would you like to play 1, 2 3?")
# print("You chose " + play)

def slots(cashBal):
    addCash = input("Would you like to add cash? yes/no")
    if addCash == "yes":
        addCashAmt = int(input("How much would you like to add?"))
        cashBal += addCashAmt
        print(Fore.GREEN + "You chose to add " + str(addCashAmt) + " and you have a total balance of " + str(cashBal) + "")
    else:
        addCashAmt = 0
        print(Fore.RED +"You chose not to add cash")

    while cashBal >= 0:

        bet = int(input("How much money do you want to bet?"))
        print("You bet " + str(bet))

        a = random.randint(1, 9)
        b = random.randint(1, 9)
        c = random.randint(1, 9)
        print(a, b, c)

        if a == b == c:
            print(Fore.GREEN + "You won BIG!")
            winnings = bet ** bet
            cashBal += bet ** bet
            print(Fore.GREEN + "You won " + str(winnings) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game == "yes":
                continue
            else:
                break
        elif a == b or a == c or b == c:
            print(Fore.GREEN + "You won!")
            winnings = bet ** bet
            cashBal += bet ** bet
            print(Fore.GREEN + "You won " + str(winnings) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game == "yes":
                continue
            else:
                break
        else:
            print("You lost!")
            cashBal -= bet
            print(Fore.RED + "You lost " + str(bet) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game == "yes":
                continue
            else:
                break
print(slots(cashBal))

