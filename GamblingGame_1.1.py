# A simple high/low gambling game

import random
import sys

myCash = int(1000)
startingCash = myCash  # track starting amount for net summary

print("WELCOME TO SAMS HIGH/LOW GAMBLING")
myName = input("What is your name? ").capitalize()
# create "loading/status" bar
print("Accessing profile for " + myName + "...")
print("Cash available to wager: ", myCash)

while myCash > 0:
    print("****************************************************************************")

    # collects adn validates bet amount
    myBet = int(input("How much money would you like to bet this round? "))
    if myBet > myCash:
        print("You do not have enough money to bet that amount. Please reduce bet amount.")
        myBet = myCash
    if myBet <= 0:
        print("Bet must be greater than $0. Please try again.")
        continue
    print("You have a cash balance of", myCash, "and are betting", myBet)

    # generates a random number
    firstNumber = random.randint(1, 7777777)
    print("Your FIRST NUMBER is", firstNumber)

    # generates a random magic number
    randNumber = (random.randint(1, 7 ** 7))  # generates a random number between 1 and 7^7
    digit_sum1 = sum(int(digit) for digit in str(randNumber))
    digit_sum2 = sum(int(digit) for digit in str(digit_sum1))
    MagicNumber = digit_sum2  # keep as int for multiplier
    print("Your MAGIC NUMBER: ")
    print(MagicNumber)

    # collects choice
    myGuess = input("high or low? ").strip().lower()
    print("Your GUESS is " + myGuess + "er.")

    # draws another random number
    secondNumber = random.randint(1, 7777777)
    print("Your SECOND NUMBER is", secondNumber)

    # checks if high/low guess is correct and updates cash

    if firstNumber < secondNumber and myGuess == "high":
        print("YOU WIN!", myBet)
        myCash += myBet
        print("Your NEW CASH BALANCE is", myCash)
        print("Net change from start: $", myCash - startingCash)
    if firstNumber < secondNumber and myGuess == "low":
        print("YOU LOSE!", myBet)
        myCash -= myBet
        print("Your NEW CASH BALANCE is", myCash)
        print("Net change from start: $", myCash - startingCash)
    if firstNumber > secondNumber and myGuess == "high":
        print("YOU LOSE!", myBet)
        myCash -= myBet
        print("Your NEW CASH BALANCE is", myCash)
        print("Net change from start: $", myCash - startingCash)
    if firstNumber > secondNumber and myGuess == "low":
        print("YOU WIN!", myBet)
        myCash += myBet
        print("Your NEW CASH BALANCE is", myCash)
        print("Net change from start: $", myCash - startingCash)
    if MagicNumber == abs(firstNumber - secondNumber):
        print("BONUS WIN")
        myCash += myBet * MagicNumber
        print("Your NEW CASH BALANCE + BONUS is", myCash)
        print("Net change from start: $", myCash - startingCash)
    addCash = input("Would you like to add cash? ")
    if addCash == "yes":
        addCashAmt = int(input("How much money would you like to add? $"))
        myCash += int(addCashAmt)
        #startingCash += addCashAmt  # adjust baseline so net stays accurate
        print("Your NEW CASH BALANCE is $", myCash)

    elif addCash == 'no':
        keepPlaying = input("Would you like to play again? ").strip().lower()
        if keepPlaying == "yes":
            continue
        elif keepPlaying == "no":
            print("Thank you for playing, ", myName + "! Final balance: $", myCash)
            sys.exit()
