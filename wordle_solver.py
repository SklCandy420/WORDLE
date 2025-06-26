import collections

# --- Configuration ---
WORD_LENGTH = 5
MAX_GUESSES = 6
WORD_LIST_FILE = 'words.txt'
FIRST_GUESS = 'slate' # A good starting word with common, unique letters

# --- ANSI Color Codes for Terminal Output ---
class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    GREY = '\033[90m'
    ENDC = '\033[0m'

def load_words(filename):
    """Loads 5-letter words from a text file."""
    try:
        with open(filename, 'r') as f:
            words = [line.strip().lower() for line in f if len(line.strip()) == WORD_LENGTH]
        print(f"Loaded {len(words)} words from '{filename}'.")
        return words
    except FileNotFoundError:
        print(f"{colors.GREY}Error: The word list file '{filename}' was not found.")
        print(f"Please download it or make sure it's in the same directory as the script.{colors.ENDC}")
        exit()

def get_feedback():
    """Gets guess result from the user and validates it."""
    while True:
        feedback = input("Enter the result (e.g., 'gyybb'): ").lower()
        if len(feedback) == WORD_LENGTH and all(c in 'gyb' for c in feedback):
            return feedback
        print(f"{colors.GREY}Invalid feedback. Please enter a 5-letter string using 'g' (green), 'y' (yellow), or 'b' (black/grey).{colors.ENDC}")

def filter_words(word_list, guess, feedback):
    """
    Filters the word list based on the feedback from a guess.
    This is the core logic of the solver.
    """
    green_letters = {i: char for i, char in enumerate(guess) if feedback[i] == 'g'}
    yellow_letters = {i: char for i, char in enumerate(guess) if feedback[i] == 'y'}
    
    # Correctly handle letter counts (e.g., if guess is 'LEVEL' and target is 'EERIE')
    # The minimum number of times a letter must appear.
    min_counts = collections.defaultdict(int)
    for char in green_letters.values():
        min_counts[char] += 1
    for char in yellow_letters.values():
        min_counts[char] += 1

    # Letters that are completely absent (black) unless they also appear as green/yellow
    present_letters = set(green_letters.values()) | set(yellow_letters.values())
    black_letters = {char for char in guess if char not in present_letters}

    # Start filtering
    possible_words = []
    for word in word_list:
        if word == guess:
            continue

        # Rule 1: Match all green letters
        if not all(word[i] == char for i, char in green_letters.items()):
            continue

        # Rule 2: Contain all yellow letters, but not in their guessed positions
        if not all(char in word for char in yellow_letters.values()):
            continue
        if any(word[i] == char for i, char in yellow_letters.items()):
            continue
        
        # Rule 3: Do not contain any purely black letters
        if any(char in word for char in black_letters):
            continue

        # Rule 4: Handle duplicate letter counts
        # e.g., if guess is 'ARRAY' -> 'bgyyb' on target 'RURAL', 'A' must appear exactly once.
        valid_count = True
        for char, count in min_counts.items():
            if word.count(char) < count:
                valid_count = False
                break
        
        # If a letter in the guess gave mixed feedback (e.g., one 'E' green, one 'E' black),
        # it means the word has *exactly* that many of that letter.
        guess_counts = collections.Counter(guess)
        for char in guess_counts:
            if char in min_counts and word.count(char) != min_counts[char]:
                # This check applies if a letter was marked black somewhere in the guess
                # indicating we have found all instances of it.
                if any(guess[i] == char and feedback[i] == 'b' for i in range(WORD_LENGTH)):
                     valid_count = False
                     break

        if not valid_count:
            continue

        possible_words.append(word)

    return possible_words

def print_suggestion(guess_num, suggestion, possible_count):
    """Prints the suggested guess to the user."""
    print("-" * 30)
    print(f"Guess #{guess_num}:")
    if suggestion:
        print(f"Suggested guess: {colors.GREEN}{suggestion.upper()}{colors.ENDC}")
        if possible_count > 1:
            print(f"({possible_count} possible words remaining)")
    else:
        print(f"{colors.GREY}No possible words found. Check your previous feedback for errors.{colors.ENDC}")

def main():
    """Main function to run the Wordle solver."""
    print("--- Wordle Solver Assistant ---")
    print("Instructions:")
    print("1. Enter the suggested word into Wordle.")
    print("2. Enter the 5-letter result using the following key:")
    print(f"   {colors.GREEN}g{colors.ENDC} for Green")
    print(f"   {colors.YELLOW}y{colors.ENDC} for Yellow")
    print(f"   {colors.GREY}b{colors.ENDC} for Black/Grey")
    print("-" * 30)

    possible_words = load_words(WORD_LIST_FILE)
    
    for i in range(1, MAX_GUESSES + 1):
        if i == 1:
            guess = FIRST_GUESS
        else:
            # Simple strategy: just pick the first word from the filtered list.
            # A more advanced strategy could analyze letter frequency in the remaining words.
            guess = possible_words[0] if possible_words else None

        if not guess:
            print_suggestion(i, None, 0)
            break
            
        print_suggestion(i, guess, len(possible_words))
        
        feedback = get_feedback()

        if feedback == 'ggggg':
            print(f"\nCongratulations! You solved it in {i} guesses.")
            print(f"The word was: {colors.GREEN}{guess.upper()}{colors.ENDC}")
            break
        
        possible_words = filter_words(possible_words, guess, feedback)
        
        if not possible_words and i < MAX_GUESSES:
            print(f"{colors.GREY}Uh oh! No words match the feedback you provided. Please double-check your entries.{colors.ENDC}")
            break

    else: # This 'else' belongs to the 'for' loop, it runs if the loop completes without a 'break'
        print("\nSolver finished. Either the word was not in the dictionary or there was an error in feedback.")

if __name__ == "__main__":
    main()