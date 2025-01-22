import random

def load_category_data(category_file, word_file, label_file):
    """
    Loads categories and words from the provided text files and maps words to their categories.
    Arguments:
        category_file (str): File containing category labels (cuefr_category_pool.txt).
        word_file (str): File containing words for the categories (cuefr_pool.txt).
        label_file (str): File that maps words to categories (cuefr_labels.txt).
    Returns:
        categories (list): List of category labels.
        words (dict): A dictionary where keys are category labels and values are lists of words.
    """
    # Read category labels from cuefr_category_pool.txt
    with open(category_file, 'r') as f:
        categories = [line.strip() for line in f.readlines()]

    # Read words from cuefr_pool.txt
    with open(word_file, 'r') as f:
        words_list = [line.strip() for line in f.readlines()]

    # Read the category labels associated with each word from cuefr_labels.txt
    with open(label_file, 'r') as f:
        word_categories = [line.strip() for line in f.readlines()]

    # Map words to their respective categories
    words = {cat: [] for cat in categories}
    for word, category in zip(words_list, word_categories):
        words[category].append(word)

    for category in words:
        random.shuffle(words[category])

    return categories, words

def generate_trial_data(num_trials, list_length, categories, words, block_trial_proportion):
    """
    Generates trial data with specified proportions for two trial types:
    1. Block trials: Includes two blocks of the same category within the list.
    2. Unique category trials: Each word comes from a different category.

    Arguments:
        num_trials (int): Number of trials in the session.
        list_length (int): Number of items per trial (e.g., 15).
        categories (list): List of available category labels.
        words (dict): A dictionary where keys are category labels and values are lists of words.
        block_trial_proportion (float): Proportion of trials that should be block trials.

    Returns:
        trial_categories (list of lists): Categories for each trial.
        trial_words (list of lists): Words for each trial.
    """
    # Calculate number of each trial type
    num_block_trials = int(num_trials * block_trial_proportion)
    num_unique_trials = num_trials - num_block_trials

    # Create a list of trial types and shuffle them
    trial_types = ["block"] * num_block_trials + ["unique"] * num_unique_trials
    random.shuffle(trial_types)

    trial_categories = []
    trial_words = []
    previous_trial_categories = set()  # Track categories used in the previous trial

    for trial_type in trial_types:
        if trial_type == "block":
            # Block Trial: Two blocks of the same category
            usable_categories = [cat for cat in categories if words.get(cat) and cat not in previous_trial_categories]

            # Ensure there are enough categories to fill the list
            if len(usable_categories) < list_length:
                usable_categories = [cat for cat in categories if words.get(cat)]  # Reset usable categories

            # Shuffle and pick a block category
            random.shuffle(usable_categories)
            block_cat = random.choice(usable_categories)
            remaining_categories = [cat for cat in usable_categories if cat != block_cat]

            # Assign categories
            trial_category_list = [None] * list_length
            trial_category_list[3:6] = [block_cat] * 3  # Block 1
            trial_category_list[9:12] = [block_cat] * 3  # Block 2

            # Fill remaining positions with unique categories
            unique_positions = [i for i in range(list_length) if i not in range(3, 6) and i not in range(9, 12)]
            for i, pos in enumerate(unique_positions):
                trial_category_list[pos] = remaining_categories[i % len(remaining_categories)]

        elif trial_type == "unique":
            # Unique Category Trial: Each word from a different category
            usable_categories = [cat for cat in categories if words.get(cat) and cat not in previous_trial_categories]

            # Ensure enough unique categories for the trial
            if len(usable_categories) < list_length:
                usable_categories = [cat for cat in categories if words.get(cat)]  # Reset usable categories

            # Shuffle and pick categories
            random.shuffle(usable_categories)
            trial_category_list = usable_categories[:list_length]  # Use only the first `list_length` categories

        # Assign words to the categories
        trial_word_list = []
        for category in trial_category_list:
            if not words.get(category):  # Handle missing categories
                word = "NO_WORD_AVAILABLE"
            else:
                word = words[category].pop(0)
                if not words[category]:
                    del words[category]  # Remove category if exhausted
            trial_word_list.append(word)

        previous_trial_categories = set(trial_category_list)  # Update previous trial categories

        trial_categories.append(trial_category_list)
        trial_words.append(trial_word_list)

    return trial_categories, trial_words

# Define the file paths
category_file = 'experiments/category_targeting/assets/cuefr_category_pool.txt'  # File with category labels
word_file = 'experiments/category_targeting/assets/cuefr_pool.txt'  # File with words
label_file = 'experiments/category_targeting/assets/cuefr_labels.txt'  # File that maps words to categories

# Load the category and word data
categories, words = load_category_data(category_file, word_file, label_file)

# Set up trial parameters
# Proportions for each trial type
block_trial_proportion = 0.60  # 60% block trials
isolate_trial_proportion = 0.40  # 40% unique category trials

# Ensure proportions add up to 1
assert block_trial_proportion + isolate_trial_proportion == 1.0

# Generate trial data
trial_categories, trial_words = generate_trial_data(
    num_trials=20,  # Total number of trials
    list_length=15,  # Number of items per trial
    categories=categories,
    words=words,
    block_trial_proportion=block_trial_proportion
)

# Print the trial categories and words in a structured format
for trial_idx in range(len(trial_categories)):
    print(f"Trial {trial_idx + 1}:")
    
    # Print categories and words for this trial
    for category, word in zip(trial_categories[trial_idx], trial_words[trial_idx]):
        print(f"  Category: {category} -> Word: {word}")
    
    print("\n")  # Add a newline for separation between trials

