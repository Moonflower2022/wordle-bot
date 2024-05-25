import sys

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

if __name__ == '__main__':
    print(get_info(sys.argv[1], sys.argv[2]))