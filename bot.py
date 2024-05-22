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


def gen_mask(guess, info, wl=wl):
    info = np.asarray(info)
    mask = np.ones(wl.shape[0], dtype=bool)
    for i, (g, inf) in enumerate(zip(guess, info)):
        if inf == 1:
            if np.count_nonzero(guess[info == 3] == g) >= 1 or np.count_nonzero(guess[info == 2] == g) >= 1:
                mask = np.logical_and(mask, wl[:, i] != g)
            else:
                mask = np.logical_and(mask, np.all(wl != g, axis=1))
        elif inf == 2:
            mask = np.logical_and(mask, np.logical_and(
                np.any(wl == g, axis=1), wl[:, i] != g))
        elif inf == 3:
            mask = np.logical_and(mask, wl[:, i] == g)
        else:
            raise Exception(f'Invalid information: {inf}')
    return mask


def get_remaining(guess, info, wl=wl):
    return wl[gen_mask(guess, info, wl=wl)]


def frac_remaining(guess, info, wl=wl):
    m = gen_mask(guess, info, wl=wl)
    return np.count_nonzero(m)/wl.shape[0]


def avg_frac_remaining(guess, wl=wl):
    info = it.product(*[[1, 2, 3] for _ in range(5)])
    info = [x for x in info if np.count_nonzero(
        gen_mask(guess, x, wl=wl)) != 0]
    func = ft.partial(frac_remaining, guess, wl=wl)
    rem = [func(i) for i in info]
    return np.sum(np.square(rem))/np.sum(rem)


nth = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth"
}

def get_best_guess(guesses, wl):
    remaining_wl = np.copy(wl)
    for i in range(len(guesses)):
        remaining_wl = get_remaining(
            guesses[i][0], guesses[i][1], wl=remaining_wl)
    if len(remaining_wl) == 1:
        return remaining_wl[0], [remaining_wl[0]], True
    with mp.Pool(mp.cpu_count()) as p:
        func = ft.partial(avg_frac_remaining, wl=remaining_wl)
        rem = p.map(func, wl)
    # ties = rem == rem[np.argmin(rem)]
    # maybe write the thing where all guesses that are in the remaining answer list get a boost
    return wl[np.argmin(rem)], remaining_wl, False


def prompt(prompt_text, output_conversion, output_criteria):
    while True:
        output = output_conversion(input(prompt_text))
        try:
            if not output_criteria(output):
                print("Invalid input. Try again.")
                continue
        except Exception as e:
            print(f"An error occured: {e}. Try again.")
        else:
            return output

# numbers 1, 2, 3 for gray, orange, green.


if __name__ == '__main__':
    obey = {'y': True, 'n': False}[prompt("Will you listen to the commands? (y/n) ",
                                          lambda output: output.strip().lower(), lambda output: output == 'y' or output == 'n')]

    print("Use \"lares\" as your first word.")
    best_guess = "lares"
    guesses = []

    for i in range(5):
        if not obey:
            guess_letters = prompt(f"What was your {nth[i + 1]} guess? ", lambda output: output.strip(
            ).lower(), lambda word: len(word) == 5 and word.isalpha() and word in wl)
        info = prompt("How correct was it? (for each letter, type 1 for gray, 2 for yellow, and 3 for green) ",
                      lambda output: output.strip().lower(), lambda info: len(info) == 5 and info.isnumeric())

        guesses.append((np.asarray(list(best_guess if obey else guess_letters)), tuple(map(int, info))))
        # use possible_answers if we know the answer list, otherwise use wl
        guess, remaining, ended = get_best_guess(
            guesses, np.asarray(possible_answers))

        best_guess = "".join(guess)
        if ended:
            print(f"The answer is \"{best_guess}\".")
            break
        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))
        print("The best guess right now is \"" + best_guess + "\".")
    print("Thanks for using SuperGoodWordleBot™")
