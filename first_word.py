from bot import get_best_guess, all_words, possible_answers
import numpy as np
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="script to get the best word")
    parser.add_argument(
        "-t",
        "--top",
        type=int,
        default=None,
        help="number of best guesses to display",
    )

    args = parser.parse_args()

    best_guess, score, remaining, won = get_best_guess(
        [], np.asarray(possible_answers), np.asarray(all_words), top=args.top
    )
    if args.top:
        print(f"The top {args.top} starting guesses:")
        print("Guess\tScore")
        for i in range(args.top):
            print(f"{best_guess[i]}\t{score[i]}")
    else:
        print(f"The best guess starting guess is {best_guess} with a score of {score}.")
