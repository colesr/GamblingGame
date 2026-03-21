# a simple slots game

import random
import colorama
from colorama import Fore, Back, Style
import sys


print("Welcome to Sam's Slots")
name = input("What is your name?")
print("Hello " + name)
print("Loading account information...")
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
    # Initialize magicNumber as None (Python's null) so we can safely check it later
    magicNumber = None
    addMagicNumber = input("Would you like to buy a magic number for $100 X your magic number? yes/no")
    if addMagicNumber == "yes":
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
    elif addMagicNumber == "no":
        print("You chose not to buy a magic number")

    while cashBal >= 0:

        bet = int(input("How much money do you want to bet?"))
        print("You bet " + str(bet))

        magicNumberChoice = input("Would you like to use your magic number mutlipier?")
        if magicNumberChoice == "yes":
            bet *= magicNumber
        # Example of checking for None (null in Python): only proceed if a magic number was chosen
        if magicNumber is not None:
            pass

        a = random.randint(1, 9)
        b = random.randint(1, 9)
        c = random.randint(1, 9)
        print(a, b, c)

        if a == b == c:
            print(Fore.GREEN + "You won BIG!")
            winnings = bet ** bet
            cashBal += bet ** bet
            print(Fore.GREEN + "You won " + sys.set_int_max_str_digits(winnings) + " and your new balance is " + str(cashBal))
            game = input("Play again? yes/no")
            if game == "yes":
                continue
            else:
                break
        elif a == b or a == c or b == c:
            print(Fore.GREEN + "You won!")
            winnings = bet ** bet
            cashBal += bet ** bet
            print(Fore.GREEN + "You won " + sys.set_int_max_str_digits(winnings) + " and your new balance is " + str(cashBal))
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

