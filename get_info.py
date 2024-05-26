import sys
import numpy as np

def get_info(guess, answer):
    info = [0, 0, 0, 0, 0]

    answer = list(answer)

    greens = {}

    for i, letter in enumerate(guess):
        if guess[i] == answer[i]:
            info[i] = 3
            if letter not in greens:
                greens[letter] = 1
            else:
                greens[letter] += 1

    for i, letter in enumerate(guess):
        if info[i] == 3:
            continue
        if letter in answer and (not letter in greens or answer.count(letter) > greens[letter]):
            info[i] = 2
        else:
            info[i] = 1

    return tuple(info)

def test():
    assert get_info("raise", np.asarray(list("lares"))) == (2, 3, 1, 2, 2)
    assert get_info("sands", np.asarray(list("brass"))) == (2, 2, 1, 1, 3)
    assert get_info("turns", np.asarray(list("brass"))) == (1, 1, 2, 1, 3)
    assert get_info("super", np.asarray(list("brass"))) == (2, 1, 1, 1, 2)
    assert get_info("carbs", np.asarray(list("brass"))) == (1, 2, 2, 2, 3)
    assert get_info("barbs", np.asarray(list("brass"))) == (3, 2, 2, 1, 3)

if __name__ == '__main__':
    test()
    print(get_info(sys.argv[1], sys.argv[2]))