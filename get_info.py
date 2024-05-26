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

    yellows = {}

    for i, letter in enumerate(guess):
        if info[i] == 3:
            continue
        if (
            letter in answer
            and (not letter in greens or answer.count(letter) > greens[letter])
            and (not letter in yellows or answer.count(letter) > yellows[letter])
        ):
            info[i] = 2
            if letter not in yellows:
                yellows[letter] = 1
            else:
                yellows[letter] += 1
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
    assert get_info("speed", np.asarray(list("abide"))) == (1, 1, 2, 1, 2)
    assert get_info("speed", np.asarray(list("erase"))) == (2, 1, 2, 2, 1)
    assert get_info("speed", np.asarray(list("steal"))) == (3, 1, 3, 1, 1)
    assert get_info("speed", np.asarray(list("crepe"))) == (1, 2, 3, 2, 1)


if __name__ == "__main__":
    test()
    print(get_info(sys.argv[1], sys.argv[2]))
