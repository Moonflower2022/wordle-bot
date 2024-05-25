from bot import get_best_guess, prompt, nth, wl, guess_valid, possible_answers
import numpy as np
import json

if __name__ == "__main__":
    with open("second_guesses.json") as file:
        second_guesses = json.load(file)

    with open("third_guesses.json") as file:
        third_guesses = json.load(file)

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
        if obey and i == 0: 
            result_dict = second_guesses[str(guesses[0][1])]
            best_guess = result_dict["best"]
            remaining = np.array(result_dict["remaining"])
            won = result_dict["won"]
        elif obey and i == 1:
            result_dict = third_guesses[str(guesses[0][1])][str(guesses[1][1])]
            best_guess = result_dict["best"]
            remaining = np.array(result_dict["remaining"])
            won = result_dict["won"]
        else:
            best, remaining_split, won = get_best_guess(guesses, np.asarray(possible_answers))
            remaining = np.array(["".join(sub_array) for sub_array in remaining_split])
            best_guess = "".join(best)

        if won:
            print(f'The answer is "{best_guess}".')
            break
        print("Remaining possible answers:")
        print(remaining)
        print('The best guess right now is "' + best_guess + '".')

        
    print("Thank you for using SuperGoodWordleBot™")
