import json
from bot import get_guess_from_tree, possible_answers
import numpy as np
from get_info import get_info

def num_guesses(answer, guess_tree):
    best_guess = "trace"
    guesses = []

    for i in range(10):
        info = get_info(best_guess, answer)

        guesses.append(
            (
                np.asarray(list(best_guess)),
                tuple(map(int, info)),
            )
        )
        best_guess, _, won = get_guess_from_tree(guesses, guess_tree)

        if won:
            return i + 2


def main():
    with open("guess_tree.json") as file:
        guess_tree = json.load(file)

    num_guesses_map = {}

    for i, answer in enumerate(possible_answers):
        print(f"{i}/{len(possible_answers)}", end="\r")
        num_guesses_map["".join(list(answer))] = num_guesses(answer, guess_tree)

    average = sum(num_guesses_map.values()) / len(possible_answers)

    print("Average # of guesses:", average)

    with open("num_guesses.json", "w+") as file:
        json.dump(num_guesses_map, file)

if __name__ == "__main__":
    main()
