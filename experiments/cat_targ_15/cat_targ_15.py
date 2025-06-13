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

def generate_recall_cue_indices() -> list[list[int]]:
    """
    Generate recall-event indices for each trial (2 events per trial) under the new design.
    Args:
        trial_count: Total number of trials.

    Returns:
        A list (length = trial_count) of lists (each of length 2):
          - For control trials => [0, 0]
          - For isolate-target => [some position in {2, 5, 8, 11, 14}, 0]
    """

    # let's directly define trial types by retrieval cues
    trial_types = (
        # control
        [[0, 0]] * 5
        # isolate
        + [[2,0], [5,0], [8,0], [11,0], [14,0]] * 2
    )
    random.shuffle(trial_types)
    return trial_types

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
    category_targets = np.zeros_like(cat_cue_indices)  # shape: (trial_count, 2)

    for i, j in itertools.product(range(num_trials), range(cue_count)):
        index = cat_cue_indices[i, j]
        if index != 0:  # index=0 means no cue; note we store -1 in python but fill with 0 after +1 offset
            # Subtract 1 to move from 1-based to 0-based indexing in pres_itemids
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
    
        A   B   C   D   E   F   G   H   I   J   K   L   M   N   O
      (positions 1-15, 1-indexed)
    
    In this structure:
      - There is no block-structure, all words are of unique categories.
    
    The function:
      1. Selects 15 distinct categories from `labels` (preferring those not used in the previous trial)
        to serve as the category label for each list-item.
      2. Fills a 15-element trial template:
         - All indices get a unique category.
      3. For each position, a stimulus is drawn (and removed) from the corresponding
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
    positions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # We need 10 distinct categories => 1 for block, 9 for non-block
    num_needed = 15
    all_label_indices = np.arange(len(labels))

    # Prefer categories not used in the previous trial
    preferred = [idx for idx in all_label_indices if idx not in last_trial_label_indices]
    if len(preferred) >= num_needed:
        candidate_pool = preferred
    else:
        candidate_pool = list(all_label_indices)

    chosen = random.sample(candidate_pool, num_needed)
    categories = [cat for cat in chosen]
    # Shuffle the 9 non-block categories.
    random.shuffle(categories)

    # Build trial label indices according to the fixed template.
    trial_label_indices = [None] * TOTAL_POSITIONS
    for pos, cat in zip(positions, categories):
        trial_label_indices[pos] = cat

    # Now, for each position, pop a stimulus from the corresponding subject's pool.
    stimulus_ids = np.zeros(TOTAL_POSITIONS, dtype=int)
    stimulus_strings = np.empty(TOTAL_POSITIONS, dtype=object)
    trial_subject_stimulus_pools = copy.deepcopy(subject_stimulus_pools)

    for pos, cat_idx in enumerate(trial_label_indices):
        pool = subject_stimulus_pools[cat_idx]
        if len(pool) == 0:
            raise ValueError(f"Stimulus pool for label {labels[cat_idx]} is empty.")

        stim = pool.pop(random.randrange(len(pool)))  # remove random stimulus

        try:
            stim_id = aggregated_stimulus_pool.index(stim) + 1
        except ValueError as e:
            raise ValueError(f"Stimulus {stim} not found in aggregated pool.") from e
        stimulus_ids[pos] = stim_id
        stimulus_strings[pos] = stim

    return (
        stimulus_ids,
        stimulus_strings,
        np.array(trial_label_indices)
    )
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
        if index != 0:  # Cued recall
            category_cues[cue_idx] = pres_itemids[trial_index, index-1]
            cat_cue_positions[cue_idx] = index

    return category_cues, cat_cue_positions


# %%

def construct_study_lists(
    labels: list[str],
    stimulus_pools: list[list[str]],
    trial_count: int,
    subject_count: int,
    aggregated_stimulus_pool: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct study lists according to design of cued / free recall experiment.

    Args:
        labels: Category labels for each stimulus in the stimulus pool.
        stimulus_pools: The stimulus pools corresponding to each label.
        trial_count: The number of trials per subject.
        subject_count: The number of subjects.
        list_length: The number of presentations per trial.
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
    # Now we only want 2 recall events (e.g., [cue, -1]) or [-1, -1]
    total_recalls = 2  

    # Allocate arrays to store all subjects x trials
    pres_itemids = np.zeros((trial_count * subject_count, list_length), dtype=int)
    pres_itemstrs = np.zeros((trial_count * subject_count, list_length), dtype=object)
    category_cues = np.zeros((trial_count * subject_count, total_recalls), dtype=int)
    cat_cue_indices = np.zeros((trial_count * subject_count, total_recalls), dtype=int)

    for s in range(subject_count):
        subject_stimulus_pools = copy.deepcopy(stimulus_pools)
        last_trial_label_indices = np.array([])

        # Generate the new 2-element recall arrays
        recall_index_arrays = generate_recall_cue_indices()
        validate_stimulus_pool_size(labels, subject_stimulus_pools, trial_count)

        for t in range(trial_count):
            trial_stim_ids, trial_stim_strs, last_trial_label_indices = sample_stimuli_for_trial(
                labels,
                subject_stimulus_pools,
                last_trial_label_indices,
                aggregated_stimulus_pool,
            )

            # add trial to study lists
            trial_index = s * trial_count + t
            pres_itemids[trial_index, :] = trial_stim_ids
            pres_itemstrs[trial_index, :] = trial_stim_strs

            # Assign the single category cue (if any)
            trial_cue_array = recall_index_arrays[t]
            trial_category_cues, trial_cat_cue_indices = assign_cue_stimuli(
                trial_index, trial_cue_array, pres_itemids, total_recalls
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

    subject_count = 1000
    trial_count = 15
    list_length = 15
    # Now each trial has exactly 2 recall events: [cue, free] or [no_cue, free].
    total_recalls = 2
    # 40% of trials are "control" => [-1, -1].

    target_data_path = "experiments/cat_targ_15/cat_targ_15.h5"
    target_stimulus_pool_path = "experiments/cat_targ_15/assets/cuefr_pool.txt"
    target_stimulus_labels_path = "experiments/cat_targ_15/assets/cuefr_labels.txt"
    target_category_pool_path = "experiments/cat_targ_15/assets/cuefr_category_pool.txt"
    source_pools_path = "experiments/cat_targ_15/assets/asymfr"

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

    # Load the pools
    stimulus_pools: list[list[str]] = [
        load_stimulus_pool(f"{source_pools_path}/{label}.txt") for label in labels
    ]
    # Flatten/aggregate
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
        aggregated_stimulus_pool,
    )

    # Construct final data dict
    result: dict[str, np.ndarray] = {
        "subject": np.repeat(np.arange(subject_count), trial_count)[:, np.newaxis],
        "listLength": np.repeat(list_length, subject_count * trial_count)[:, np.newaxis],
        "pres_itemnos": np.tile(
            np.arange(1, list_length + 1), (subject_count * trial_count, 1)
        ),
        "pres_itemids": pres_itemids,
        # Now each trial has 2 recall events
        "category_cues": category_cues,
        "category_cue_indices": category_cue_indices,
        "category_cue_itemids": category_cue_itemids,
    }

    # Save results
    save_data(result, target_data_path)

    # Basic sanity checks
    loaded_result = load_data(target_data_path)
    assert loaded_result["subject"].shape == (subject_count * trial_count, 1)
    assert loaded_result["listLength"].shape == (subject_count * trial_count, 1)
    assert loaded_result["pres_itemnos"].shape == (subject_count * trial_count, list_length)
    assert loaded_result["pres_itemids"].shape == (subject_count * trial_count, list_length)
    # Only 2 columns for cues:
    assert loaded_result["category_cues"].shape == (subject_count * trial_count, 2)
    assert loaded_result["category_cue_indices"].shape == (subject_count * trial_count, 2)
    assert loaded_result["category_cue_itemids"].shape == (subject_count * trial_count, 2)

    assert np.min(loaded_result["pres_itemids"]) == 1
    assert np.max(loaded_result["pres_itemids"]) > list_length
    assert np.min(loaded_result["pres_itemnos"]) == 1

    # Save stimulus pools and labels
    with open(target_stimulus_pool_path, "w") as f:
        f.write("\n".join(aggregated_stimulus_pool))
    with open(target_stimulus_labels_path, "w") as f:
        f.write("\n".join(aggregated_stimulus_labels))
    with open(target_category_pool_path, "w") as f:
        f.write("\n".join(labels))
