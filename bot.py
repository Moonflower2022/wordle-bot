import multiprocessing as mp
import itertools as it
import functools as ft
import numpy as np
import os

dirname = os.path.dirname(__file__)
answers_filename = os.path.join(dirname, "answers.txt")
guesses_filename = os.path.join(dirname, "guesses.txt")

answers_file = open(answers_filename, "r")
guesess_file = open(guesses_filename, "r")

answers_text = answers_file.read()
guesses_text = guesess_file.read()

possible_answers = [list(word) for word in answers_text.split("\n")]
possible_guesses = [list(word) for word in guesses_text.split("\n")]

wl = np.asarray(possible_answers + possible_guesses)

answers_file.close()
guesess_file.close()


def gen_mask(guess, info, wl):
    info = np.asarray(info)
    mask = np.ones(wl.shape[0], dtype=bool)
    for i, (g, inf) in enumerate(zip(guess, info)):
        if inf == 1:
            if (
                np.count_nonzero(guess[info == 3] == g) >= 1
                or np.count_nonzero(guess[info == 2] == g) >= 1
            ):
                mask = np.logical_and(mask, wl[:, i] != g)
            else:
                mask = np.logical_and(mask, np.all(wl != g, axis=1))
        elif inf == 2:
            mask = np.logical_and(
                mask, np.logical_and(np.any(wl == g, axis=1), wl[:, i] != g)
            )
        elif inf == 3:
            mask = np.logical_and(mask, wl[:, i] == g)
        else:
            raise Exception(f"Invalid information: {inf}")
    return mask


def get_remaining(guesses, wl):
    remaining_wl = np.copy(wl)
    for guess, info in guesses:
        remaining_wl = remaining_wl[gen_mask(guess, info, remaining_wl)]
    return remaining_wl


def frac_remaining(guess, info, wl):
    m = gen_mask(guess, info, wl)
    return np.count_nonzero(m) / wl.shape[0]


def avg_frac_remaining(guess, remaining_wl):
    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    infos = [
        info
        for info in all_info
        if np.count_nonzero(gen_mask(guess, info, remaining_wl)) != 0
    ]
    rem = [frac_remaining(guess, info, remaining_wl) for info in infos]

    return np.sum(np.square(rem)) / np.sum(rem)


def score_word(guess, remaining_wl=wl):
    bonus = -0.001 if any(list(guess) == list(word) for word in remaining_wl) else 0
    return avg_frac_remaining(guess, remaining_wl) + bonus


def get_best_guess(guesses, wl):
    remaining_wl = get_remaining(guesses, wl)
    if len(remaining_wl) == 1:
        return remaining_wl[0], [remaining_wl[0]], True
    with mp.Pool(mp.cpu_count()) as pool:
        func = ft.partial(score_word, remaining_wl=remaining_wl)
        rem = pool.map(func, wl)
    return wl[np.argmin(rem)], remaining_wl, False


def guess_valid(new_guess, new_info, guesses, wl):
    new_guesses = guesses + [(new_guess, new_info)]

    remaining_wl = get_remaining(new_guesses, wl)

    return len(remaining_wl) != 0


def prompt(prompt_text, output_conversion, output_criteria):
    while True:
        output = output_conversion(input(prompt_text))
        try:
            broken_criteria = False
            for criteria, message in output_criteria:
                if not criteria(output):
                    print(message)
                    broken_criteria = True
                    break

            if broken_criteria:
                continue
        except Exception as e:
            print(f"An error occured: {e}. Try again.")
        else:
            return output


# numbers 1, 2, 3 for gray, orange, green.

nth = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}

if __name__ == "__main__":
    obey = {"y": True, "n": False}[
        prompt(
            "Will you listen to the commands? (y/n) ",
            lambda output: output.strip().lower(),
            [
                (
                    lambda output: output == "y" or output == "n",
                    "Input is not 'y' or 'n'.",
                )
            ],
        )
    ]

    print('Use "raise" as your first word.')
    best_guess = "raise"
    guesses = []

    for i in range(5):
        guess_input_criteria = [
            (lambda word: len(word) == 5, "Input word is not 5 characters long."),
            (lambda word: word.isalpha(), "Input word is not all letters."),
            (
                lambda word: any(word == "".join(list_word) for list_word in wl),
                "Input word is not in the available guesses list.",
            ),
        ]
        if not obey:
            guess_letters = prompt(
                f"What was your {nth[i + 1]} guess? ",
                lambda output: output.strip().lower(),
                guess_input_criteria,
            )
        info_input_criteria = [
            (lambda info: len(info) == 5, "Input info is not 5 characters long."),
            (
                lambda info: all([char in ["1", "2", "3"] for char in info]),
                "Input word has characters that are not in {1, 2, 3}.",
            ),
            (
                lambda info: guess_valid(
                    np.asarray(list(best_guess if obey else guess_letters)),
                    tuple(map(int, info)),
                    guesses,
                    np.asarray(possible_answers),
                ),
                "The input info does not leave any possible answers remaining.",
            ),
        ]
        info = prompt(
            "How correct was it? (for each letter, gray: 1, yellow: 2, green: 3) ",
            lambda output: output.strip().lower(),
            info_input_criteria,
        )

        guesses.append(
            (
                np.asarray(list(best_guess if obey else guess_letters)),
                tuple(map(int, info)),
            )
        )
        # use possible_answers if we know the answer list, otherwise use wl
        guess, remaining, ended = get_best_guess(guesses, np.asarray(possible_answers))

        best_guess = "".join(guess)
        if ended:
            print(f'The answer is "{best_guess}".')
            break
        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))
        print('The best guess right now is "' + best_guess + '".')
    print("Thank you for using SuperGoodWordleBot™")
