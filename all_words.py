import numpy as np
from bot import prompt, guess_valid, get_remaining, guess_input_criteria, nth
from english_words import get_english_words_set

english_words_set = get_english_words_set(["web2", "gcide"], lower=True)
possible_answers = [list(word) for word in english_words_set if len(word) == 5 and not " " in word]

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