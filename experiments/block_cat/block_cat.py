# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: online_experiments
#     language: python
#     name: python3
# ---

# %%
import copy
import itertools
import random

import numpy as np
from helpers import load_data, load_stimulus_pool, save_data


# %%
def aggregate_stimulus_pools(
    stimulus_pools: list[list[str]], labels: list[str]
) -> tuple[list[str], list[str]]:
    """
    Combine multiple stimulus pools into a single list and associate each stimulus with its
    corresponding label.

    This function is useful for experiments or data processing tasks where stimuli (e.g., images,
    sounds, words) are grouped into categories. It flattens the stimulus pools into a single list
    and assigns each stimulus the appropriate label from its pool for further analysis.

    Args:
        stimulus_pools: A list of lists, where each sublist contains stimuli (e.g., words or
        images) in a specific category.
        labels: A list of labels, where each label corresponds to one stimulus pool. The number of
        labels must match the number of stimulus pools.

    Returns:
        A tuple with:
        - A list of all stimuli from the pools.
        - A list of labels, with each label corresponding to its respective stimulus.

    Example:
        For `stimulus_pools = [['A', 'B'], ['C']]` and `labels = ['Group 1', 'Group 2']`,
        the result will be (['A', 'B', 'C'], ['Group 1', 'Group 1', 'Group 2']).
    """
    stimulus_pool = []
    stimulus_labels = []
    for pool, label in zip(stimulus_pools, labels):
        stimulus_pool.extend(pool)
        stimulus_labels.extend([label] * len(pool))
    return stimulus_pool, stimulus_labels


# %%
def generate_alternating_recalls(
    cue_count: int, total_recalls: int, cued_indices: list[int]
) -> list[int]:
    """Create an alternating sequence of cued recall and free recall events.

    Args:
        cue_count: The number of cued recall events.
        total_recalls: The total number of recall events (both cued and free recall).
        cued_indices: A list of indices for cued recall events.

    Returns:
        A list of recall event indices where cued recall indices alternate with free recall events (-1).
    """
    alternating_indices = []
    cued_idx = 0
    for i in range(total_recalls):
        if i % 2 == 0 and cued_idx < cue_count:
            alternating_indices.append(cued_indices[cued_idx])
            cued_idx += 1
        else:
            alternating_indices.append(-1)  # Free recall event
    return alternating_indices


# %%
def calculate_balance_score(
    combo: tuple[int, ...],
    index_selection_count: dict[int, int],
    middle_indices: list[int],
) -> float:
    """
    Calculate a balance score for a given combination of indices based on current index selection counts.

    The goal is to balance how often each index is used across trials. This function calculates a score
    that reflects how well the provided combination of indices contributes to balancing index usage. The
    function prioritizes indices that are underrepresented and penalizes combinations that include
    overrepresented indices.

    Args:
        combo: A tuple of indices representing a potential combination of cued recall positions.
        index_selection_count: A dictionary where each key is an index and the value is the number of times
                               that index has been selected so far.
        middle_indices: A list of all possible indices from the middle region of the list.

    Returns:
        A float score indicating how well this combination balances index usage. Lower scores indicate
        that the combination better balances the underrepresented indices.
        - Negative values mean the combination includes more underrepresented indices.
        - Positive values penalize overrepresented indices to reduce bias.
    """
    # Total selections made so far
    current_total = sum(index_selection_count.values())

    # Calculate the ideal usage count for balancing
    ideal_count = current_total / len(middle_indices) if current_total > 0 else 1

    # Find the least-represented index count
    min_count = min(index_selection_count.values())

    # Initialize the score
    score = 0

    # Calculate the balance score by favoring underrepresented indices and penalizing overrepresented ones
    for idx in combo:
        if index_selection_count[idx] == min_count:
            score -= 1  # Favor combinations that include underrepresented indices
        else:
            score += abs(
                index_selection_count[idx] - ideal_count
            )  # Penalize overrepresented indices

    return score


# %%
def generate_valid_combinations(
    middle_indices: list[int], cue_count: int, spacing: int
) -> list[tuple[int, ...]]:
    """
    Generate all possible valid combinations of cued indices that satisfy the spacing constraint.

    Args:
        middle_indices: A list of indices from which the cues are drawn.
        cue_count: The number of cues required for each trial.
        spacing: The minimum spacing between cued indices.

    Returns:
        A list of tuples, each representing a valid combination of indices that satisfy the spacing constraint.
    """
    return [
        combo
        for combo in itertools.combinations(middle_indices, cue_count)
        if all(combo[i + 1] - combo[i] >= spacing + 1 for i in range(len(combo) - 1))
    ]


# %%
def select_best_combination(
    valid_combinations: list[tuple[int, ...]],
    index_selection_count: dict[int, int],
    middle_indices: list[int],
) -> tuple[int, ...]:
    """
    Select the combination that best balances the usage of indices by minimizing the balance score.

    Args:
        valid_combinations: A list of valid combinations of cued indices.
        index_selection_count: A dictionary tracking how often each index has been selected.
        middle_indices: The list of middle region indices used for cueing.

    Returns:
        A tuple representing the best combination of indices that helps balance underrepresented indices.
    """
    # Calculate balance scores for each combination
    scores = [
        (combo, calculate_balance_score(combo, index_selection_count, middle_indices))
        for combo in valid_combinations
    ]

    # Find the minimum score
    min_score = min(scores, key=lambda x: x[1])[1]

    # Select all combinations that have the minimum score
    best_combos = [combo for combo, score in scores if score == min_score]

    # Randomly choose one of the best combinations
    return random.choice(best_combos)


# %%
def generate_balanced_trials_with_priority(
    middle_indices: list[int], cue_count: int, spacing: int, total_trials: int
) -> list[list[int]]:
    """
    Generate a set of cued recall trials while balancing the usage of indices and enforcing a spacing constraint.

    This function creates trials where each trial is composed of cued recall events (selected from `middle_indices`).
    The goal is to ensure that indices are used as evenly as possible across trials, while also maintaining a
    minimum spacing between cued indices.

    Args:
        middle_indices: A list of indices from which cues can be drawn.
        cue_count: The number of category cues per trial.
        spacing: The minimum spacing between cued indices.
        total_trials: The total number of cued recall trials to generate.

    Returns:
        A list of valid cued recall trials, where each trial is a list of indices representing the cued positions.
        The function ensures that the trials are balanced and respect the spacing constraint.
    """
    # Step 1: Generate valid combinations that satisfy the spacing constraint
    valid_combinations = generate_valid_combinations(middle_indices, cue_count, spacing)

    # Step 2: Track how many times each index has been selected
    index_selection_count = {idx: 0 for idx in middle_indices}
    selected_combinations = []

    # Step 3: Iteratively select combinations that balance index usage
    while len(selected_combinations) < total_trials:
        chosen_combo = select_best_combination(
            valid_combinations, index_selection_count, middle_indices
        )

        # Add the chosen combination to the selected trials
        selected_combinations.append(chosen_combo)

        # Update the selection count for each index in the chosen combination
        for i in chosen_combo:
            index_selection_count[i] += 1

    return selected_combinations


# %%

# %%


def generate_recall_cue_indices(
    trial_count: int,
    control_proportion: float,
) -> list[list[int]]:
    """
    Generate recall-event indices for each trial (6 events per trial) based on a fixed study-list
    structure and fixed cue positions.

    The study list is assumed to have 15 items with the structure:
        A  B  C  D  D  D  E  F  G  D  D  D  H  I  J
    (using 1-indexed positions).

    In this design:
      - The block-presented category is D. Its cue is fixed at position 4.
      - The only possible isolate cues come from positions B, E, or I
        (i.e. positions 2, 7, and 14).

    For recall events:
      - Control (free recall) trials have all 6 events set to -1.
      - Cued trials have 3 cue events (at positions 1, 3, and 5 of the recall sequence)
        alternating with free recalls (positions 2, 4, and 6).
      - The first recall event (cue) is randomly determined for cued trials:
          • If it is block-first, the pattern is:
                [block, free, isolate, free, block, free]
                (i.e. [4, -1, X, -1, 4, -1])
          • If it is isolate-first, the pattern is:
                [isolate, free, block, free, isolate, free]
                (i.e. [X, -1, 4, -1, Y, -1])
        where the isolate cues (X and Y) are selected by shuffling the list [2, 7, 14].

    To ensure balance, we construct a trial type list that includes:
      - Exactly control_proportion * trial_count "control" trials.
      - The remaining trials are cued, split evenly between "block-first" and "isolate-first".
      - The overall trial order is then shuffled.

    Args:
        trial_count: Total number of trials.
        control_proportion: Proportion of trials that are control (free recall).

    Returns:
        A list (length = trial_count) of lists (each of length 6) of integers where:
          - -1 indicates a free recall event.
          - A positive integer indicates the 1-indexed study position for a cued recall.
    """
    # Determine number of control and cued trials.
    num_control = int(round(trial_count * control_proportion))
    num_cued = trial_count - num_control

    # For cued trials, create a list that is half "block-first" and half "isolate-first".
    cued_trial_types = []
    half = num_cued // 2
    remainder = num_cued - 2 * half
    cued_trial_types.extend(["block-first"] * half)
    cued_trial_types.extend(["isolate-first"] * half)
    # If there's an extra cued trial, assign it randomly.
    for _ in range(remainder):
        cued_trial_types.append(random.choice(["block-first", "isolate-first"]))

    # Combine control and cued trial types into one list.
    trial_types = ["control"] * num_control + cued_trial_types
    random.shuffle(trial_types)

    # Fixed cue definitions (1-indexed):
    block_cue = 4  # For block cues (category D)
    isolate_options = [2, 7, 14]  # Possible positions for isolate cues (B, E, I)

    all_trials = []
    for ttype in trial_types:
        if ttype == "control":
            # Control trial: all recall events are free recall (-1)
            trial_recall = [-1] * 4
        elif ttype == "block-first":
            # Pattern: [block, free, isolate, free, block, free]
            isolates = isolate_options[:]  # Copy list for shuffling.
            random.shuffle(isolates)
            trial_recall = [block_cue, -1, isolates[0], -1]
        elif ttype == "isolate-first":
            # Pattern: [isolate, free, block, free, isolate, free]
            isolates = isolate_options[:]  # Copy list for shuffling.
            random.shuffle(isolates)
            trial_recall = [isolates[0], -1, block_cue, -1]
        else:
            # Fallback (should not occur)
            raise ValueError(f"Invalid trial type: {ttype}")
        all_trials.append(trial_recall)

    return all_trials


# %%
def retrieve_cue_target_items(
    cat_cue_indices: np.ndarray, pres_itemids: np.ndarray
) -> np.ndarray:
    """Retrieve stimulus IDs for category cues based on indices provided for each trial.

    Args:
        cat_cue_indices: Array containing the serial position indices for each cue.
        pres_itemids: Array containing the stimulus IDs presented in each trial.

    Returns:
        An array containing the stimulus IDs corresponding to the category cues.
    """
    num_trials, cue_count = cat_cue_indices.shape
    category_targets = np.zeros_like(cat_cue_indices)  # Initialize the result array

    for i, j in itertools.product(range(num_trials), range(cue_count)):
        index = cat_cue_indices[i, j]
        if index != 0:  # If index is not zero (0 indicates no cue)
            # Subtract 1 to adjust to 0-based indexing
            category_targets[i, j] = pres_itemids[i][index - 1]

    return category_targets


# %%
def validate_stimulus_pool_size(
    labels: list[str], stimulus_pools: list[list[str]], trial_count: int
) -> None:
    """Ensure that each stimulus pool has enough items to handle the number of trials.

    Args:
        labels: The list of category labels.
        stimulus_pools: The list of stimulus pools corresponding to each label.
        trial_count: The total number of trials each subject will participate in.

    Raises:
        AssertionError: If a category does not have enough stimuli to support the required number of trials.
    """
    for label_index, _ in enumerate(labels):
        assert len(stimulus_pools[label_index]) >= (trial_count / 2), (
            f"Not enough stimuli in pool for label: {labels[label_index]}"
        )


# %%
def sample_stimuli_for_trial(
    labels: list[str],
    subject_stimulus_pools: list[list[str]],
    last_trial_label_indices: np.ndarray,
    aggregated_stimulus_pool: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Samples stimuli for a trial with a fixed study-list structure:
    
        A   B   C   D   D   D   E   F   G   D   D   D   H   I   J
      (positions 1-15, 1-indexed)
    
    In this structure:
      - The block-presented category occupies positions 4-6 and 10-12 (0-indexed: [3,4,5] and [9,10,11]).
      - The remaining 9 positions are assigned distinct non-block categories.
    
    The function:
      1. Selects 10 distinct categories from `labels` (preferring those not used in the previous trial)
         to serve as the 1 block category and 9 non-block categories.
      2. Randomly designates one as the block category and shuffles the remaining 9.
      3. Fills a 15-element trial template:
         - Block positions (indices 3,4,5,9,10,11) get the block category.
         - Non-block positions ([0,1,2,6,7,8,12,13,14]) get the 9 shuffled non-block categories.
      4. For each position, a stimulus is drawn (and removed) from the corresponding
         subject_stimulus_pools. The aggregated_stimulus_pool is used to determine the
         1-indexed stimulus ID.
    
    Args:
        labels: List of all category labels.
        subject_stimulus_pools: List of stimulus pools for each label (order matches `labels`).
        last_trial_label_indices: 1D array of label indices used in the previous trial.
        aggregated_stimulus_pool: Aggregated list of all stimuli (used for lookup of stimulus IDs).
        
    Returns:
        A tuple of three numpy arrays:
          - stimulus_ids: (15,) array of 1-indexed stimulus IDs.
          - stimulus_strings: (15,) array of the stimulus strings.
          - trial_label_indices: (15,) array of the label indices assigned to each study position.
    """
    TOTAL_POSITIONS = 15
    # Fixed positions (0-indexed)
    block_positions = [3, 4, 5, 9, 10, 11]           # positions for block category
    non_block_positions = [0, 1, 2, 6, 7, 8, 12, 13, 14]  # remaining positions

    # We need 10 distinct categories: 1 for block, 9 for non-block.
    num_needed = 10
    all_label_indices = np.arange(len(labels))
    # Prefer categories not used in the previous trial.
    preferred = [idx for idx in all_label_indices if idx not in last_trial_label_indices]
    candidate_pool = preferred if len(preferred) >= num_needed else list(all_label_indices)
    
    # Randomly select 10 distinct categories.
    chosen = random.sample(candidate_pool, num_needed)
    # Randomly designate one as the block category.
    block_category = random.choice(chosen)
    non_block_categories = [cat for cat in chosen if cat != block_category]
    # If needed, fill in to reach 9 non-block categories.
    if len(non_block_categories) < 9:
        remaining = [idx for idx in all_label_indices if idx != block_category and idx not in non_block_categories]
        needed = 9 - len(non_block_categories)
        non_block_categories.extend(random.sample(remaining, needed))
    
    # Shuffle the 9 non-block categories.
    random.shuffle(non_block_categories)
    
    # Build trial label indices according to the fixed template.
    trial_label_indices = [None] * TOTAL_POSITIONS
    for pos in block_positions:
        trial_label_indices[pos] = block_category
    for pos, cat in zip(non_block_positions, non_block_categories):
        trial_label_indices[pos] = cat
    
    # Now, for each position, pop a stimulus from the corresponding subject's pool.
    stimulus_ids = np.zeros(TOTAL_POSITIONS, dtype=int)
    stimulus_strings = np.empty(TOTAL_POSITIONS, dtype=object)
    trial_subject_stimulus_pools = copy.deepcopy(subject_stimulus_pools)
    for pos, cat_idx in enumerate(trial_label_indices):
        before_length = len(subject_stimulus_pools[cat_idx])
        pool = trial_subject_stimulus_pools[cat_idx]
        if len(pool) == 0:
            raise ValueError(f"Stimulus pool for label {labels[cat_idx]} is empty.")

        stim = pool.pop(random.randrange(len(pool)))
        after_length = len(subject_stimulus_pools[cat_idx])
        assert before_length == after_length, "Stimulus pool was not modified in place."
        # Determine the 1-indexed stimulus ID from the aggregated pool.
        try:
            stim_id = aggregated_stimulus_pool.index(stim) + 1
        except ValueError:
            raise ValueError(f"Stimulus {stim} not found in aggregated stimulus pool.")
        stimulus_ids[pos] = stim_id
        stimulus_strings[pos] = stim

    return stimulus_ids, stimulus_strings, np.array(trial_label_indices)



# %%
def assign_cue_stimuli(
    trial_index: int,
    category_cue_indices: list[int],  # Now expects a list of indices for each trial
    pres_itemids: np.ndarray,
    total_recalls: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Assign multiple category cues for a trial based on the cue indices provided.

    Args:
        trial_index: The index of the current trial.
        category_cue_indices: List containing the serial position indices for each category cue.
        pres_itemids: 2D array of stimulus IDs presented in each trial.
        total_recalls: Total number of recall events per trial.

    Returns:
        The stimulus IDs for the category cues and the serial position indices of the category cues (1-indexed).
    """
    category_cues = np.zeros(total_recalls, dtype=int)
    cat_cue_positions = np.zeros(total_recalls, dtype=int)

    for cue_idx in range(total_recalls):
        index = category_cue_indices[cue_idx]
        if index != -1:  # Cued recall
            category_cues[cue_idx] = pres_itemids[trial_index, index]
            cat_cue_positions[cue_idx] = index + 1  # Convert to 1-indexed

    return category_cues, cat_cue_positions


# %%

def construct_study_lists(
    labels: list[str],
    stimulus_pools: list[list[str]],
    trial_count: int,
    subject_count: int,
    control_proportion: float,
    aggregated_stimulus_pool: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct study lists according to design of cued / free recall experiment.

    Args:
        labels: Category labels for each stimulus in the stimulus pool.
        stimulus_pools: The stimulus pools corresponding to each label.
        trial_count: The number of trials per subject.
        subject_count: The number of subjects.
        list_length: The number of presentations per trial.
        control_proportion: The proportion of trials with no category cues.
        aggregated_stimulus_pool: The aggregated stimulus pool.

    Returns:
        A tuple containing:
        - An array of stimulus IDs for each presentation (1-indexed).
        - An array of stimulus strings for each presentation (1-indexed).
        - An array of stimulus IDs for the category cues.
        - An array of serial position indices for the category cues.
        - An array of stimulus IDs for the category cue targets.
    """
    list_length = 15
    total_recalls = 4

    pres_itemids = np.zeros((trial_count * subject_count, list_length), dtype=int)
    pres_itemstrs = np.zeros((trial_count * subject_count, list_length), dtype=object)
    category_cues = np.zeros((trial_count * subject_count, total_recalls), dtype=int)
    cat_cue_indices = np.zeros((trial_count * subject_count, total_recalls), dtype=int)

    for s in range(subject_count):
        subject_stimulus_pools = copy.deepcopy(stimulus_pools)
        last_trial_label_indices = np.array([])

        category_cue_indices = generate_recall_cue_indices(
            trial_count, control_proportion
        )
        validate_stimulus_pool_size(labels, subject_stimulus_pools, trial_count)

        for t in range(trial_count):
            trial_stimulus_indices, trial_stimulus_strings, last_trial_label_indices = (
                sample_stimuli_for_trial(
                    labels,
                    subject_stimulus_pools,
                    last_trial_label_indices,
                    aggregated_stimulus_pool,
                )
            )

            # add trial to study lists
            trial_index = s * trial_count + t
            pres_itemids[trial_index, :] = trial_stimulus_indices
            pres_itemstrs[trial_index, :] = trial_stimulus_strings

            # Assign category cues
            trial_category_cues, trial_cat_cue_indices = assign_cue_stimuli(
                trial_index, category_cue_indices[t], pres_itemids, total_recalls
            )
            category_cues[trial_index, :] = trial_category_cues
            cat_cue_indices[trial_index, :] = trial_cat_cue_indices

    cat_cue_itemids = retrieve_cue_target_items(cat_cue_indices, pres_itemids)
    return pres_itemids, pres_itemstrs, category_cues, cat_cue_indices, cat_cue_itemids

# %%
if __name__ == "__main__":
    # EMBAM format:
    # entries are always 2D arrays, with column arrays used for 1D data
    # row count for each entry equals the number of trials across all subjects
    # column count for 2D entries equals the number of presentations per trial
    # minimally includes:
    # - 1D array of subject IDs ('subject')
    # - 1D array of list lengths ('listLength')
    # - 2D array of stimulus IDs ('pres_itemids'; trial index by presentation index; 1-indexed)
    # - 2D array of presentation indices ('pres_itemnos'; trial index by presentation index; 1-indexed)
    #
    # also include a 1D array specifying a pres_id whose corresponding category label will be used for cued recall ('category_cue')

    subject_count = 300
    trial_count = 20
    list_length = 15
    total_recalls = 4
    control_proportion = 4 / 10
    target_data_path = "experiments/block_cat/block_cat.h5"
    target_stimulus_pool_path = "experiments/block_cat/assets/cuefr_pool.txt"
    target_stimulus_labels_path = "experiments/block_cat/assets/cuefr_labels.txt"
    target_category_pool_path = "experiments/block_cat/assets/cuefr_category_pool.txt"
    source_pools_path = "experiments/block_cat/assets/asymfr"
    total_trials = trial_count * subject_count

    # construct stimulus pool across specified category labels
    labels = [
        "birds",
        "body parts",
        "building parts",
        "car models",
        "carpentry tools",
        "cities",
        "clothes",
        "colors",
        "countries",
        "dwellings",
        "elements",
        "fabrics",
        "fish",
        "four-footed animals",
        "fruit",
        "furniture",
        "geography terms",
        "insects",
        "instruments",
        "kitchen tools",
        "occupations",
        "reading materials",
        "seasonings",
        "ships",
        "sports",
        "states",
        "trees",
        "vegetables",
        "weather terms",
        "flowers",
        "military titles",
        "beverages",
    ]
    labels = [label.upper() for label in labels]

    stimulus_pools: list[list[str]] = [
        load_stimulus_pool(f"{source_pools_path}/{label}.txt") for label in labels
    ]
    aggregated_stimulus_pool, aggregated_stimulus_labels = aggregate_stimulus_pools(
        stimulus_pools, labels
    )

    (
        pres_itemids,
        pres_itemstrs,
        category_cues,
        category_cue_indices,
        category_cue_itemids,
    ) = construct_study_lists(
        labels,
        stimulus_pools,
        trial_count,
        subject_count,
        control_proportion,
        aggregated_stimulus_pool,
    )

    # construct data dict
    result: dict[str, np.ndarray] = {
        "subject": np.repeat(np.arange(subject_count), trial_count)[:, np.newaxis],
        "listLength": np.repeat(list_length, subject_count * trial_count)[
            :, np.newaxis
        ],
        "pres_itemnos": np.tile(
            np.arange(1, list_length + 1), (subject_count * trial_count, 1)
        ),
        "pres_itemids": pres_itemids,
        "category_cues": category_cues,
        "category_cue_indices": category_cue_indices,
        "category_cue_itemids": category_cue_itemids,
    }

    save_data(result, target_data_path)

    # tests:
    # load result file
    loaded_result = load_data(target_data_path)

    # confirm shapes
    assert loaded_result["subject"].shape == (subject_count * trial_count, 1)
    assert loaded_result["listLength"].shape == (subject_count * trial_count, 1)
    assert loaded_result["pres_itemnos"].shape == (
        subject_count * trial_count,
        list_length,
    )
    assert loaded_result["pres_itemids"].shape == (
        subject_count * trial_count,
        list_length,
    )
    assert loaded_result["category_cues"].shape == (
        subject_count * trial_count,
        total_recalls,
    )
    assert loaded_result["category_cue_indices"].shape == (
        subject_count * trial_count,
        total_recalls,
    )

    # confirm pres_itemids and pres_itemnos are 1-indexed
    # (we reserve 0 for padding when list lengths vary)
    assert np.min(loaded_result["pres_itemids"]) == 1
    assert np.max(loaded_result["pres_itemids"]) > list_length
    assert np.min(loaded_result["pres_itemnos"]) == 1

    # also save constructed stimulus pools and labels
    with open(target_stimulus_pool_path, "w") as f:
        f.write("\n".join(aggregated_stimulus_pool))
    with open(target_stimulus_labels_path, "w") as f:
        f.write("\n".join(aggregated_stimulus_labels))
    with open(target_category_pool_path, "w") as f:
        f.write("\n".join(labels))
