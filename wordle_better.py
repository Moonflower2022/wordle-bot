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

def gen_mask(guess,info,wl=wl):
    info = np.asarray(info)
    mask = np.ones(wl.shape[0], dtype=bool)
    for i,(g,inf) in enumerate(zip(guess,info)):
        if inf == 1:
            if np.count_nonzero(guess[info==3] == g) >= 1 or np.count_nonzero(guess[info==2] == g) >= 1:
                mask = np.logical_and(mask,wl[:,i] != g)
            else:
                mask = np.logical_and(mask,np.all(wl != g,axis=1))
        elif inf == 2:
            mask = np.logical_and(mask,np.logical_and(np.any(wl == g,axis=1),wl[:,i] != g))
        elif inf == 3:
            mask = np.logical_and(mask,wl[:,i] == g)
        else:
            raise Exception(f'Invalid information: {inf}')
    return mask

def get_remaining(guess,info,wl=wl):
    return wl[gen_mask(guess,info,wl=wl)]

def frac_remaining(guess,info,wl=wl):
    m = gen_mask(guess,info,wl=wl)
    return np.count_nonzero(m)/wl.shape[0]

import itertools as it
import functools as ft

def avg_frac_remaining(guess, wl=wl):
    info = it.product(*[[1,2,3] for i in range(5)])
    info = [x for x in info if np.count_nonzero(gen_mask(guess,x,wl=wl)) != 0]
    func = ft.partial(frac_remaining,guess,wl=wl)
    rem = [func(i) for i in info]
    return np.sum(np.square(rem))/np.sum(rem)

nth = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth"
}

conversion = {
    "n": 1,
    "y": 2,
    "g": 3
}

import multiprocessing as mp

def best_guess(guesses, wl):
    remaining_wl = np.copy(wl)
    for i in range(len(guesses)):
        remaining_wl = get_remaining(guesses[i][0], guesses[i][1], wl=remaining_wl)
    if len(remaining_wl) == 1:
        return remaining_wl[0], [], True
    with mp.Pool(mp.cpu_count()) as p:
        func = ft.partial(avg_frac_remaining, wl=remaining_wl)
        rem = p.map(func,wl)
    #ties = rem == rem[np.argmin(rem)]
    # maybe write the thing where all guesses that are in the remaining answer list get a boost
    return wl[np.argmin(rem)], remaining_wl, False

def y_n_prompt(prompt_text):
    answer = input(prompt_text)
    while not (answer == "y" or answer == "n"):
        answer = input(prompt_text)
    return answer == "y"
    
#numbers 1, 2, 3 for gray, orange, green.

if __name__ == '__main__':
    yes_listen = y_n_prompt("Will you listen to the commands? (y/n) ")

    print("Use \"lares\" as your first word.")
    suggested_guess = "lares"
    guesses = []
    for i in range(5):
        if not yes_listen:
            guess_letters = input(f"What was your {nth[i + 1]} guess? ").lower()
        guess_correctness = input("How correct was it? (for each letter, type 1 for gray, 2 for yellow, and 3 for green) ").lower()
        if not yes_listen:
            guesses.append((np.asarray(list(guess_letters)), tuple(map(int, guess_correctness))))
        elif yes_listen:
            guesses.append((np.asarray(list(suggested_guess)), tuple(map(int, guess_correctness))))
        guess, remaining, ended = best_guess(guesses, np.asarray(possible_answers)) # use possible_answers if we know the answer list, otherwise use wl

        suggested_guess = "".join(guess)
        if ended:
            print(f"The answer is \"{suggested_guess}\".")
            print("Thanks for using SuperGoodWordleBot™")
            break
        print("Remaining possible answers:")
        print(np.array(["".join(sub_array) for sub_array in remaining]))
        print("The best guess right now is \"" + suggested_guess + "\".")
        if i == 4:
            print("Thanks for using SuperGoodWordleBot™")