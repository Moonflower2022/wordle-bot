from bot import get_best_guess, gen_mask, get_remaining, possible_answers
import itertools as it
import numpy as np
import json
import os
import argparse


def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)
    return default


def save_json(filename, data):
    with open(filename, "w+") as file:
        json.dump(data, file, indent=4)


def recursive_fill(guess_history, remaining_answers):
    best_guess, score, remaining, won = get_best_guess(guess_history, remaining_answers)
    result = {
        "best": best_guess,
        "score": score,
        "remaining": ["".join(list(word)) for word in remaining],
        "won": won,
    }

    best_guess = np.asarray(list(best_guess))

    if not won:
        all_info = it.product(*[[1, 2, 3] for _ in range(5)])
        valid_infos = [
            info
            for info in all_info
            if len(
                get_remaining(guess_history + [(best_guess, info)], remaining_answers)
            )
            != 0
        ]

        next_layer = {}
        for info in valid_infos:
            next_guess_history = guess_history + [(best_guess, info)]
            next_layer[str(info)] = recursive_fill(
                next_guess_history, remaining_answers
            )

        result["next"] = next_layer

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="cacher")
    parser.add_argument(
        "first_guess", type=str, help="the first guess for all of the games"
    )

    args = parser.parse_args()

    filename = f"guess_trees/{args.first_guess}.json"
    guess_tree = load_json(filename, {})

    first_guess = np.asarray(list(args.first_guess))
    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    first_infos = [
        first_info
        for first_info in all_info
        if np.count_nonzero(
            gen_mask(first_guess, first_info, np.asarray(possible_answers))
        )
        != 0
    ]

    for i, first_info in enumerate(first_infos):
        print(f"{i+1}/{len(first_infos)}: {first_info}", end="\r")
        guess_history = [(first_guess, first_info)]
        if str(first_info) in guess_tree:
            continue
        guess_tree[str(first_info)] = recursive_fill(
            guess_history, np.asarray(possible_answers)
        )
        save_json(filename, guess_tree)
