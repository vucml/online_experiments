import random
import numpy as np

def load_category_data(category_file, word_file, label_file):
    # Same as your original function (no changes needed)
    with open(category_file, 'r') as f:
        categories = [line.strip() for line in f.readlines()]
    with open(word_file, 'r') as f:
        words_list = [line.strip() for line in f.readlines()]
    with open(label_file, 'r') as f:
        word_categories = [line.strip() for line in f.readlines()]

    words = {cat: [] for cat in categories}
    for word, category in zip(words_list, word_categories):
        words[category].append(word)

    for category in words:
        random.shuffle(words[category])

    return categories, words

def generate_trial_data(num_trials, list_length, categories, words, block_trial_proportion):
    num_block_trials = int(num_trials * block_trial_proportion)
    num_unique_trials = num_trials - num_block_trials

    trial_types = ["block"] * num_block_trials + ["unique"] * num_unique_trials
    random.shuffle(trial_types)

    trial_categories = []
    trial_words = []
    previous_trial_categories = set()

    for trial_type in trial_types:
        if trial_type == "block":
            usable_categories = [cat for cat in categories if words.get(cat) and cat not in previous_trial_categories]

            if len(usable_categories) < list_length:
                usable_categories = [cat for cat in categories if words.get(cat)]

            random.shuffle(usable_categories)
            block_cat = random.choice(usable_categories)
            remaining_categories = [cat for cat in usable_categories if cat != block_cat]

            trial_category_list = [None] * list_length
            trial_category_list[3:6] = [block_cat] * 3  # Block 1
            trial_category_list[9:12] = [block_cat] * 3  # Block 2

            unique_positions = [i for i in range(list_length) if i not in range(3, 6) and i not in range(9, 12)]
            for i, pos in enumerate(unique_positions):
                trial_category_list[pos] = remaining_categories[i % len(remaining_categories)]

        elif trial_type == "unique":
            usable_categories = [cat for cat in categories if words.get(cat) and cat not in previous_trial_categories]

            if len(usable_categories) < list_length:
                usable_categories = [cat for cat in categories if words.get(cat)]

            random.shuffle(usable_categories)
            trial_category_list = usable_categories[:list_length]

        trial_word_list = []
        for category in trial_category_list:
            if not words.get(category):
                word = "NO_WORD_AVAILABLE"
            else:
                word = words[category].pop(0)
                if not words[category]:
                    del words[category]
            trial_word_list.append(word)

        previous_trial_categories = set(trial_category_list)

        trial_categories.append(trial_category_list)
        trial_words.append(trial_word_list)

    # Convert lists to NumPy arrays for structured data output
    trial_categories_np = np.array(trial_categories)
    trial_words_np = np.array(trial_words)

    return trial_categories_np, trial_words_np

# Define file paths
category_file = '/Users/roberttornatore/Desktop/JATOS/study_assets_root/online_experiments/experiments/category_targeting/assets/cuefr_category_pool.txt'
word_file = '/Users/roberttornatore/Desktop/JATOS/study_assets_root/online_experiments/experiments/category_targeting/assets/cuefr_pool.txt'
label_file = '/Users/roberttornatore/Desktop/JATOS/study_assets_root/online_experiments/experiments/category_targeting/assets/cuefr_labels.txt'

# Load data
categories, words = load_category_data(category_file, word_file, label_file)

# Trial parameters
block_trial_proportion = 0.60
assert block_trial_proportion == 1.0 - 0.40

# Generate trial data
trial_categories, trial_words = generate_trial_data(
    num_trials=15,
    list_length=15,
    categories=categories,
    words=words,
    block_trial_proportion=block_trial_proportion
)

# Print structured data for trial categories and words (NumPy arrays)
print("Trial Categories:")
print(trial_categories)
print("\nTrial Words:")
print(trial_words)




