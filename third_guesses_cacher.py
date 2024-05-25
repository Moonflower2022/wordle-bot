from bot import get_best_guess, gen_mask, get_remaining, possible_answers
import itertools as it
import numpy as np
import json
import os

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)
    return default

def save_json(filename, data):
    with open(filename, "w+") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    second_guesses = load_json("second_guesses.json", {})
    third_guesses_base = load_json("third_guesses.json", {})

    first_guess = np.asarray(["r", "a", "i", "s", "e"])

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
        if str(first_info) in third_guesses_base:
            continue

        print(f"{i}/{len(first_infos)}")
        print(first_info)        

        third_guesses_top = {}

        second_guess = np.asarray(list(second_guesses[str(first_info)]["best"]))

        print(second_guess)

        all_info = it.product(*[[1, 2, 3] for _ in range(5)])
        second_infos = [
            second_info
            for second_info in all_info
            if len(
                get_remaining(
                    [(first_guess, first_info), (second_guess, second_info)],
                    np.asarray(possible_answers)
                )
            )
            != 0
        ]

        for second_info in second_infos:

            best, remaining, won = get_best_guess(
                        [(first_guess, first_info), (second_guess, second_info)],
                        np.asarray(possible_answers),
                    )
            third_guesses_top[str(second_info)] = {
                "best": "".join(list(best)),
                "remaining": ["".join(list(word)) for word in remaining],
                "won": won,
            }

        third_guesses_base[str(first_info)] = third_guesses_top

        # Save progress
        save_json("third_guesses.json", third_guesses_base)
