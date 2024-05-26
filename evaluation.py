import json
from bot import get_best_guess, possible_answers
import numpy as np
from get_info import get_info

def num_guesses(answer, second_guesses, third_guesses):
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
        if i == 0:
            result_dict = second_guesses[str(guesses[0][1])]
            best_guess = result_dict["best"]
            won = result_dict["won"]
        elif i == 1:
            result_dict = third_guesses[str(guesses[0][1])][str(guesses[1][1])]
            best_guess = result_dict["best"]
            won = result_dict["won"]
        else:
            best, _, won = get_best_guess(guesses, np.asarray(possible_answers))
            best_guess = "".join(best)

        if won:
            return i + 2


def main():
    with open("second_guesses.json") as file:
        second_guesses = json.load(file)

    with open("third_guesses.json") as file:
        third_guesses = json.load(file)

    num_guesses_map = {}

    for i, answer in enumerate(possible_answers):
        print(f"{i}/{len(possible_answers)}", end="\r")
        num_guesses_map["".join(list(answer))] = num_guesses(answer, second_guesses, third_guesses)

    average = sum(num_guesses_map.values()) / len(possible_answers)

    print("Average # of guesses:", average)

    with open("answer_num_guesses.json", "w+") as file:
        json.dump(num_guesses_map, file)

def test():
    assert get_info("raise", np.asarray(list("lares"))) == (2, 3, 1, 2, 2)
    assert get_info("sands", np.asarray(list("brass"))) == (2, 2, 1, 1, 3)
    assert get_info("turns", np.asarray(list("brass"))) == (1, 1, 2, 1, 3)
    assert get_info("super", np.asarray(list("brass"))) == (2, 1, 1, 1, 2)
    assert get_info("carbs", np.asarray(list("brass"))) == (1, 2, 2, 2, 3)
    assert get_info("barbs", np.asarray(list("brass"))) == (3, 2, 2, 1, 3)

if __name__ == "__main__":
    main()
