# wordle-bot

A bot that plays wordle

`available_remaining.py` is a version that just tells you all of the remaining words that are possible.  

`bot.py` is a the optimized version that tells you the best word to guess in terms of expected remaining number of guesses. Inspired by [this article](https://ben.land/post/2022/02/11/optimal-wordle-solution/).

`bot_cached.py` is the same thing as `bot.py` but it uses cached information written by `second_guesses_cacher.py` and `third_guesses_cacher.py` for speed.  

## Usage

  1. download the code (if you are using git just do `git clone https://github.com/Moonflower2022/wordle-bot`)
  2. cd to the directory  
  3. download the requirements (`pip install -r requirements.txt`)  
  4. run the file (ex: `python bot.py` or `python bot_cached.py`)  
  5. follow the instructions  

Feel free to send any unexpected bugs or comments to [dumbderivatives@gmail.com](mailto:dumbderivatives@gmail.com)
