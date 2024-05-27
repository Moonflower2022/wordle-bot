import multiprocessing as mp
import itertools as it
import functools as ft
import numpy as np
import os
import argparse
import json
from info_getter import get_info

dirname = os.path.dirname(__file__)
answers_filename = os.path.join(dirname, "answers.txt")
guess_history_filename = os.path.join(dirname, "guesses.txt")

answers_file = open(answers_filename, "r")
guesess_file = open(guess_history_filename, "r")

answers_text = answers_file.read()
guess_history_text = guesess_file.read()

possible_answers = [list(word) for word in answers_text.split("\n")]
possible_guess_history = [list(word) for word in guess_history_text.split("\n")]

words = np.asarray(possible_answers + possible_guess_history)

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


def get_remaining(guess_history, words):
    remaining_words = np.copy(words)
    for guess, info in guess_history:
        remaining_words = remaining_words[gen_mask(guess, info, remaining_words)]
    return remaining_words


def entropy(guess, info, words):
    m = gen_mask(guess, info, words)
    return np.log2(np.count_nonzero(m))


def weighted_entropy(guess, remaining_words):
    occurences = {}

    for word in remaining_words:
        info = get_info(guess, word)
        if not info in occurences:
            occurences[info] = 1
        else:
            occurences[info] += 1

    valid_infos = list(occurences.keys())

    count = sum(list(occurences.values()))
    probabilities = np.array(list(occurences.values())) / count

    entropies = np.array(
        [entropy(guess, info, remaining_words) for info in valid_infos]
    )

    return np.dot(entropies, probabilities)


def score_word(guess, remaining_words=None):
    score = weighted_entropy(guess, remaining_words)
    bonus = -0.001 if any(list(guess) == list(word) for word in remaining_words) else 0
    return score + bonus


def get_best_guess(guess_history, words, top=None):
    remaining_words = get_remaining(guess_history, words)
    if len(remaining_words) == 1:
        return "".join(remaining_words[0]), 0, [], True
    else:
        with mp.Pool(mp.cpu_count()) as pool:
            scorer = ft.partial(score_word, remaining_words=remaining_words)
            scores = np.asarray(pool.map(scorer, words))
        if top:
            sorted_indicies = np.argsort(scores)
            bottom_sorted_indicies = sorted_indicies[:top]
            best_guess_history = words[bottom_sorted_indicies]
            best_scores = scores[bottom_sorted_indicies]
        else:
            best_guess = words[np.argmin(scores)]
            best_score = np.min(scores)
        won = False
    return (
        (
            ["".join(list(guess)) for guess in best_guess_history]
            if top
            else "".join(list(best_guess))
        ),
        best_scores if top else best_score,
        remaining_words,
        won,
    )


def get_guess_from_tree(guess_history, guess_tree):
    branch = guess_tree
    for i, (_, info) in enumerate(guess_history):
        if i > 0:
            branch = branch["next"]
        branch = branch[str(info)]

    return branch["best"], branch["score"], branch["remaining"], branch["won"]


def guess_valid(new_guess, new_info, guess_history, words):
    new_guess_history = guess_history + [(new_guess, new_info)]

    remaining_words = get_remaining(new_guess_history, words)

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


def main():
    if args.cached:
        with open(f"guess_trees/{args.cached}.json") as file:
            guess_tree = json.load(file)

    if args.cached:
        args.obey = True

    best_guess = args.cached if args.cached else "trace"
    print(f'Use "{best_guess}" as your first word.')

    guess_history = []

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
            user_guess = prompt(
                f"What was your {nth[i + 1]} guess? ",
                lambda output: output.strip().lower(),
                guess_input_criteria,
            )
        guess = best_guess if args.obey else user_guess
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
                    guess_history,
                    np.asarray(possible_answers),
                ),
                "The input info does not leave any possible answers remaining.",
            ),
        ]
        info = prompt(
            "How correct was it? (gray: 1, yellow: 2, green: 3) ",
            lambda output: output.strip().lower(),
            info_input_criteria,
        )

        guess_history.append(
            (
                np.asarray(list(guess)),
                tuple(map(int, info)),
            )
        )

        if args.cached:
            best_guess, score, remaining, ended = get_guess_from_tree(
                guess_history, guess_tree
            )
        else:
            best_guess, score, remaining, ended = get_best_guess(
                guess_history, np.asarray(possible_answers), top=args.top
            )

        if ended:
            print(f'The answer is "{best_guess}".')
            break
        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))
        if not args.cached and args.top:
            print(f"The top {args.top} guesses right now:")
            print("Guess\tExpected Info")
            for i in range(args.top):
                print(f"{best_guess[i]}\t{score[i]}")
        else:
            print(
                f'The best guess right now is "{best_guess}" with an expected information of {score}.'
            )

    print("Thank you for using SuperGoodWordleBot™")


def main_remaining():
    i = 0
    guess_history = []
    while True:

        guess = prompt(
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
                    np.asarray(list(guess)),
                    tuple(map(int, info)),
                    guess_history,
                    np.asarray(possible_answers),
                ),
                "The input info does not leave any possible answers remaining.",
            ),
        ]

        info = prompt(
            "How correct was it? (gray: 1, yellow: 2, green: 3) ",
            lambda output: output.strip().lower(),
            info_input_criteria,
        )

        guess_history.append(
            (
                np.asarray(list(guess)),
                tuple(map(int, info)),
            )
        )

        remaining = get_remaining(guess_history, np.asarray(possible_answers))

        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))

        i += 1


if __name__ == "__main__":
    nth = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}

    parser = argparse.ArgumentParser(description="wordle-bot")

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-c",
        "--cached",
        type=str,
        dest="cached",
        help="use cached results stored in guess_trees",
    )
    group.add_argument(
        "-t",
        "--top",
        type=int,
        default=None,
        help="number of best guesses to display",
    )
    group.add_argument(
        "-r",
        "--remaining",
        action="store_true",
        help="if true, does not compute best guess(es) and just shows remaining possible answers",
    )

    parser.add_argument(
        "-o",
        "--obey",
        action="store_true",
        help="assume that user is following suggested guesses",
    )

    args = parser.parse_args()

    print(args.cached, args.obey, args.remaining, args.top)

    guess_input_criteria = [
        (lambda word: len(word) == 5, "Input word is not 5 characters long."),
        (lambda word: word.isalpha(), "Input word is not all letters."),
        (
            lambda word: any(word == "".join(list_word) for list_word in words),
            "Input word is not in the available guesses list.",
        ),
    ]

    if args.remaining:
        main_remaining()
    else:
        main()
