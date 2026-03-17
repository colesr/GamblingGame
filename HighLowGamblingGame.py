
# A simple high/low gambling game

import random
import sys

MAX_NUMBER = 7_777_777
STARTING_CASH = 1000
SEPARATOR = "*" * 76


def generate_magic_number() -> int:
    """Generate a magic number by reducing a large random number to its iterated digit sum."""
    rand_number = random.randint(1, 7 ** 7)
    digit_sum1 = sum(int(d) for d in str(rand_number))
    digit_sum2 = sum(int(d) for d in str(digit_sum1))
    return digit_sum2


def get_bet(cash: int) -> int:
    """Prompt the player for a valid bet amount."""
    while True:
        try:
            bet = int(input("How much money would you like to bet on this round? "))
        except ValueError:
            print("Please enter a valid whole number.")
            continue
        if bet <= 0:
            print("Bet must be greater than $0. Please try again.")
        elif bet > cash:
            print(f"You only have ${cash}. Please enter a bet within your balance.")
        else:
            return bet


def print_round_result(outcome: str, bet: int, cash: int, starting_cash: int) -> None:
    """Print the result of a round including the updated cash balance and net change."""
    net_change = cash - starting_cash
    print(f"{outcome} ${bet}")
    print(f"Your NEW CASH BALANCE is ${cash}")
    print(f"Net change from start: ${net_change:+}")


def play_round(cash: int, starting_cash: int) -> tuple[int, int]:
    """
    Play a single round of the high/low game.
    Returns updated (cash, starting_cash).
    """
    print(SEPARATOR)
    bet = get_bet(cash)
    print(f"You have a cash balance of ${cash} and are betting ${bet}.")

    first_number = random.randint(1, MAX_NUMBER)
    print(f"Your FIRST NUMBER is {first_number}")

    magic_number = generate_magic_number()
    print(f"Your MAGIC NUMBER: {magic_number}")

    guess = input("high or low? ").strip().lower()
    while guess not in ("high", "low"):
        print("Please enter 'high' or 'low'.")
        guess = input("high or low? ").strip().lower()
    print(f"Your GUESS is {guess}er.")

    second_number = random.randint(1, MAX_NUMBER)
    print(f"Your SECOND NUMBER is {second_number}")

    # Determine win/loss
    player_wins = (
        (first_number < second_number and guess == "high") or
        (first_number > second_number and guess == "low")
    )

    if first_number == second_number:
        # Push — neither win nor loss on the base bet
        print("PUSH — numbers are equal! No change to balance.")
    elif player_wins:
        cash += bet
        print_round_result("YOU WIN!", bet, cash, starting_cash)
    else:
        cash -= bet
        print_round_result("YOU LOSE!", bet, cash, starting_cash)

    # Bonus win check
    if magic_number == abs(first_number - second_number):
        bonus = bet * magic_number
        cash += bonus
        print(f"BONUS WIN! +${bonus}")
        print(f"Your NEW CASH BALANCE + BONUS is ${cash}")
        print(f"Net change from start: ${cash - starting_cash:+}")

    return cash, starting_cash


def add_cash_prompt(cash: int, starting_cash: int) -> tuple[int, int]:
    """Ask the player if they want to add cash. Returns updated (cash, starting_cash)."""
    response = input("Would you like to add cash? ").strip().lower()
    if response == "yes":
        try:
            amount = int(input("How much money would you like to add? $"))
            if amount > 0:
                cash += amount
                starting_cash += amount  # Adjust baseline so net stays accurate
                print(f"Your NEW CASH BALANCE is ${cash}")
            else:
                print("Amount must be positive. No cash added.")
        except ValueError:
            print("Invalid amount. No cash added.")
    return cash, starting_cash


def main() -> None:
    cash = STARTING_CASH
    starting_cash = cash

    print("WELCOME TO SAM'S HIGH/LOW GAMBLING")
    player_name = input("What is your name? ").capitalize()
    print(f"Accessing profile for {player_name}...")
    print(f"Cash available to wager: ${cash}")

    while cash > 0:
        cash, starting_cash = play_round(cash, starting_cash)

        if cash <= 0:
            print(f"You've run out of money. Game over, {player_name}!")
            break

        cash, starting_cash = add_cash_prompt(cash, starting_cash)

        keep_playing = input("Would you like to play again? ").strip().lower()
        if keep_playing == "no":
            print(f"Thank you for playing, {player_name}! Final balance: ${cash}")
            sys.exit()


if __name__ == "__main__":
    main()
