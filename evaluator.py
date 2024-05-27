import json
from bot import get_guess_from_tree, possible_answers
import numpy as np
from info_getter import get_info
import argparse


def num_guesses(answer, guess_tree, first_guess):
    best_guess = first_guess
    guesses = []

    for i in range(10):
        info = get_info(best_guess, answer)

        guesses.append(
            (
                np.asarray(list(best_guess)),
                tuple(map(int, info)),
            )
        )
        best_guess, _, _, won = get_guess_from_tree(guesses, guess_tree)

        if won:
            return i + 2


def main():
    parser = argparse.ArgumentParser(description="cacher")
    parser.add_argument(
        "first_guess", type=str, help="the first guess for all of the games"
    )

    args = parser.parse_args()

    filename = f"guess_trees/{args.first_guess}.json"

    with open(filename) as file:
        guess_tree = json.load(file)

    num_guesses_map = {}

    for i, answer in enumerate(possible_answers):
        print(f"{i}/{len(possible_answers)}", end="\r")
        num_guesses_map["".join(list(answer))] = num_guesses(
            answer, guess_tree, args.first_guess
        )

    average = sum(num_guesses_map.values()) / len(possible_answers)

    print("Average # of guesses:", average)

    with open(f"guess_counts/{args.first_guess}.json", "w+") as file:
        json.dump(num_guesses_map, file)


if __name__ == "__main__":
    main()
