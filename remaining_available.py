import os
import numpy as np
import random

dirname = os.path.dirname(__file__)
answers_filename = os.path.join(dirname, "answers.txt")
guesses_filename = os.path.join(dirname, "guesses.txt")

answers_file = open(answers_filename, "r")
guesess_file = open(guesses_filename, "r")

answers_text = answers_file.read()
guesses_text = guesess_file.read()

possible_answers = [word for word in answers_text.split("\n")]
possible_guesses = [word for word in guesses_text.split("\n")]

conversion = {
    0: "g",
    1: "y",
    2: "n"
}

def top_ten(word_list):
    scores = []
    for i in range(len(possible_guesses)):
        scores.append(evauluate_word(possible_guesses[i], word_list))

    # Step 1: Create pairs of elements from both lists using zip.
    zipped_lists = zip(scores, word_list)

    sorted_list = sorted(zipped_lists, key=lambda x: x[0], reverse=True)

    return sorted_list[:10]

def evauluate_word(word, word_list):
    probabilities = []
    infos = []
    for i in range(243):
        correctness = conversion[i % 3] + conversion[(i // 3) % 3] + conversion[(i // 9) % 3] + conversion[(i // 27) % 3] + conversion[(i // 81) % 3]
        if len(get_available_words([(word, correctness)], word_list)) == 0:
            continue
        probabilities.append(probability([(word, correctness)], word_list))
        infos.append(info([(word, correctness)], word_list))
    return np.array(infos).dot(np.array(probabilities))

def info(guess, word_list):
    return -np.log2(len(get_available_words(guess, word_list)) / len(word_list))

def probability(guess, word_list):
    return len(get_available_words(guess, word_list)) / len(word_list)

#({word}, {correctness})
def get_available_words(guesses, word_list):
    for i in range(len(guesses)):
        for j in range(5):
            if guesses[i][j][1] == "g":
                word_list = list(filter(lambda word : word[j] == guesses[i][j][0], word_list))
            elif guesses[i][j][1] == "y":
                word_list = list(filter(lambda word : word[j] != guesses[i][j][0] and guesses[i][j][0] in word, word_list))
            elif guesses[i][j][1] == "n":
                word_list = list(filter(lambda word : guesses[i][j][0] not in word, word_list))
    return word_list
nth = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth"
}

#print(get_available_words([("crane", "nnnng")], possible_answers))

letter_num = 5

guesses = []

guess_mode = str(input("Are you at the start of your wordle or the middle? (start/middle) "))
while not (guess_mode == "start" or guess_mode == "middle"):
    guess_mode = input("Are you at the start of your wordle or the middle? (start/middle) ")

if guess_mode == "start":
    print("Your first guess doesn't matter that much. Either pick one yourself, or use a common one such as arise, audio, or crane.")
    for i in range(5):
        guess_letters = input(f"What was your {nth[i + 1]} guess? ").lower()
        guess_correctness = input("How correct was it? (for each letter, type g for green, y for yellow, and n for gray) ")
        guess_row = []
        for j in range(letter_num):
            guess_row.append((guess_letters[j], guess_correctness[j]))
        guesses.append(guess_row)
        print("Here is an array of words that are still possible: ")
        print(get_available_words(guesses, possible_answers))
else:
    guess_num = int(input("How many guesses have you made so far? "))
    for i in range(5):
        guess_letters = input(f"What was your {nth[i + 1]} guess? ").lower()
        guess_correctness = input("How correct was it? (for each letter, type g for green, y for yellow, and n for gray) ")
        guess_row = []
        for j in range(letter_num):
            guess_row.append((guess_letters[j], guess_correctness[j]))
        guesses.append(guess_row)
        if i + 1 > guess_num:
            print("Here is an array of words that are still possible: ")
            print(get_available_words(guesses, possible_answers))