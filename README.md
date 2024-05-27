# wordle-bot

A bot that finds the best wordle guess(es).

## files

`bot.py` is the bot that tells you the best word to guess in terms of expected information elimnation.  

`first_word.py` tells you the best first word to guess.  

`cacher.py` caches results for the `-c` flag on `bot.py` (it takes really long).

`evaluator.py` evaluates the bot in terms of average number of guesses to win a game using cached results.

`info_getter.py` tells you the information that you would get given a guess and an answer.  

## Usage

  1. download the code (if you are using git just do `git clone https://github.com/Moonflower2022/wordle-bot`)
  2. cd to the directory (if you are using git, skip this step)
  3. download the requirements (`pip install -r requirements.txt`)  
  4. run the file (ex: `python bot.py` or `python bot_cached.py`)
  5. follow the instructions, for most scripts adding `-h` to the end of the python command gives you instructions on command line flags.

Feel free to send any unexpected bugs or comments to [dumbderivatives@gmail.com](mailto:dumbderivatives@gmail.com)
