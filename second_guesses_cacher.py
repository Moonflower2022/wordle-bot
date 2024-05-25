from bot import get_best_guess, gen_mask, possible_answers
import itertools as it
import numpy as np
import json

if __name__ == "__main__":
    first_guess = np.asarray(["r", "a", "i", "s", "e"])

    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    first_infos = [
        first_info
        for first_info in all_info
        if np.count_nonzero(gen_mask(first_guess, first_info, np.asarray(possible_answers)))
        != 0
    ]

    second_guesses = {}

    for i, first_info in enumerate(first_infos):
        print(f"{i}/{len(first_infos)}")
        print(first_info)
        best, remaining, won = get_best_guess(
            [(first_guess, first_info)], np.asarray(possible_answers)
        )
        second_guesses[str(first_info)] = {
            "best": "".join(list(best)),
            "remaining": ["".join(list(word)) for word in remaining],
            "won": won,
        }

    with open("second_guesses.json", "w+") as file:
        json.dump(second_guesses, file, indent=4)
