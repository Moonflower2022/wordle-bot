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

def recursive_cache(guess_history, remaining_answers):
    # Find the best guess for the current state
    best_guess, remaining, won = get_best_guess(guess_history, remaining_answers)
    result = {
        "best": best_guess,
        "remaining": ["".join(list(word)) for word in remaining],
        "won": won,
    }

    best_guess = np.asarray(list(best_guess))

    if not won:
        # Generate all possible information patterns for the next guess
        all_info = it.product(*[[1, 2, 3] for _ in range(5)])
        valid_infos = [
            info
            for info in all_info
            if len(get_remaining(guess_history + [(best_guess, info)], remaining_answers)) != 0
        ]

        next_layer = {}
        for info in valid_infos:
            next_guess_history = guess_history + [(best_guess, info)]
            next_layer[str(info)] = recursive_cache(next_guess_history, remaining_answers)

        result["next"] = next_layer

    return result

if __name__ == "__main__":
    # Load existing data
    cache = load_json("guess_tree.json", {})

    first_guess = np.asarray(list("trace"))
    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    first_infos = [
        first_info
        for first_info in all_info
        if np.count_nonzero(gen_mask(first_guess, first_info, np.asarray(possible_answers))) != 0
    ]

    for i, first_info in enumerate(first_infos):
        print(f"Processing first info {i+1}/{len(first_infos)}: {first_info}", end="\r")
        guess_history = [(first_guess, first_info)]
        if str(first_info) in cache:
            continue
        cache[str(first_info)] = recursive_cache(guess_history, np.asarray(possible_answers))
        save_json("guess_tree.json", cache)
