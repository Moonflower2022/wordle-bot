from bot import get_best_guess, possible_answers
import numpy as np

if __name__ == '__main__':
    best_guess = "".join(get_best_guess([], np.asarray(possible_answers))[0])
    print(f"The best guess from the start is \"{best_guess}\"")