from bot import possible_answers

for word in possible_answers:
    if word[4] == "s":
        print("".join(word))