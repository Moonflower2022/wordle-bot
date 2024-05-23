from bot import get_best_guess, gen_mask, wl
import itertools as it
import numpy as np
import json

if __name__ == '__main__':
    word = np.asarray(["l", "a", "r", "e", "s"])

    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    infos = [info for info in all_info if np.count_nonzero(gen_mask(word, info, wl)) != 0]

    first_layer = {}

    for i, info in enumerate(infos):
        print(f"{i}/{len(infos)}", end="\r")
        first_layer[info] = get_best_guess([(word, info)], wl)
                    
    with open("first_layer.txt") as file:
        json.dump(first_layer, file, indent=4)