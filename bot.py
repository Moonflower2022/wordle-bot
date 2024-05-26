import multiprocessing as mp
import itertools as it
import functools as ft
import numpy as np
import os
import argparse
import json

dirname = os.path.dirname(__file__)
answers_filename = os.path.join(dirname, "answers.txt")
guesses_filename = os.path.join(dirname, "guesses.txt")

answers_file = open(answers_filename, "r")
guesess_file = open(guesses_filename, "r")

answers_text = answers_file.read()
guesses_text = guesess_file.read()

possible_answers = [list(word) for word in answers_text.split("\n")]
possible_guesses = [list(word) for word in guesses_text.split("\n")]

words = np.asarray(possible_answers + possible_guesses)

answers_file.close()
guesess_file.close()


def gen_mask(guess, info, words):
    info = np.asarray(info)
    mask = np.ones(words.shape[0], dtype=bool)
    for i, (g, inf) in enumerate(zip(guess, info)):
        if inf == 1:
            if (
                np.count_nonzero(guess[info == 3] == g) >= 1
                or np.count_nonzero(guess[info == 2] == g) >= 1
            ):
                mask = np.logical_and(mask, words[:, i] != g)
            else:
                mask = np.logical_and(mask, np.all(words != g, axis=1))
        elif inf == 2:
            mask = np.logical_and(
                mask, np.logical_and(np.any(words == g, axis=1), words[:, i] != g)
            )
        elif inf == 3:
            mask = np.logical_and(mask, words[:, i] == g)
        else:
            raise Exception(f"Invalid information: {inf}")
    return mask


def get_remaining(guesses, words):
    remaining_words = np.copy(words)
    for guess, info in guesses:
        remaining_words = remaining_words[gen_mask(guess, info, remaining_words)]
    return remaining_words


def frac_remaining(guess, info, words):
    m = gen_mask(guess, info, words)
    return np.count_nonzero(m) / words.shape[0]


def avg_frac_remaining(guess, remaining_words):
    all_info = it.product(*[[1, 2, 3] for _ in range(5)])
    infos = [
        info
        for info in all_info
        if np.count_nonzero(gen_mask(guess, info, remaining_words)) != 0
    ]
    rem = [frac_remaining(guess, info, remaining_words) for info in infos]

    return np.mean(rem)  # np.sum(np.square(rem)) / np.sum(rem)


def score_word(guess, remaining_words=None):
    bonus = -0.001 if any(list(guess) == list(word) for word in remaining_words) else 0
    return avg_frac_remaining(guess, remaining_words) + bonus


def get_best_guess(guesses, words):
    remaining_words = get_remaining(guesses, words)
    if len(remaining_words) == 1:
        best_guess = remaining_words[0]
        won = True
    else:
        with mp.Pool(mp.cpu_count()) as pool:
            func = ft.partial(score_word, remaining_words=remaining_words)
            rem = pool.map(func, words)
        best_guess = words[np.argmin(rem)]
        won = False
    return "".join(list(best_guess)), remaining_words, won


def get_guess_from_tree(guesses, guess_tree):
    branch = guess_tree
    for i, (_, info) in enumerate(guesses):
        if i > 0:
            branch = branch["next"]
        branch = branch[str(info)]

    return branch["best"], branch["remaining"], branch["won"]


def guess_valid(new_guess, new_info, guesses, words):
    new_guesses = guesses + [(new_guess, new_info)]

    remaining_words = get_remaining(new_guesses, words)

    return len(remaining_words) != 0


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
    parser = argparse.ArgumentParser(description="wordle-bot")
    parser.add_argument(
        "-c",
        "--cached",
        action="store_true",
        help="use cached results stored in guess_tree.json",
    )
    parser.add_argument(
        "-o",
        "--obey",
        action="store_true",
        help="assume that user is following suggested guesses",
    )

    args = parser.parse_args()

    if args.cached:
        with open("guess_tree.json") as file:
            guess_tree = json.load(file)

    print('Use "trace" as your first word.')
    best_guess = "trace"
    guesses = []

    for i in range(5):
        guess_input_criteria = [
            (lambda word: len(word) == 5, "Input word is not 5 characters long."),
            (lambda word: word.isalpha(), "Input word is not all letters."),
            (
                lambda word: any(word == "".join(list_word) for list_word in words),
                "Input word is not in the available guesses list.",
            ),
        ]
        if not args.obey:
            guess_letters = prompt(
                f"What was your {nth[i + 1]} guess? ",
                lambda output: output.strip().lower(),
                guess_input_criteria,
            )
        guess = best_guess if args.obey else guess_letters
        info_input_criteria = [
            (lambda info: len(info) == 5, "Input info is not 5 characters long."),
            (
                lambda info: all([char in ["1", "2", "3"] for char in info]),
                "Input word has characters that are not in {1, 2, 3}.",
            ),
            (
                lambda info: guess_valid(
                    np.asarray(list(guess)),
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
                np.asarray(list(guess)),
                tuple(map(int, info)),
            )
        )

        if args.cached:
            best_guess, remaining, ended = get_guess_from_tree(guesses, guess_tree)
        else:
            best_guess, remaining, ended = get_best_guess(
                guesses, np.asarray(possible_answers)
            )

        if ended:
            print(f'The answer is "{best_guess}".')
            break
        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))
        print('The best guess right now is "' + best_guess + '".')
    print("Thank you for using SuperGoodWordleBot™")
