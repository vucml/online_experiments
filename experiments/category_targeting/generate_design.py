import numpy as np
import copy
import itertools
import random
import math
from helpers import load_stimulus_pool, load_data, save_data


def middle_half_indices(n: int) -> list[int]:
    """Calculate start and end indices for the middle half of a list.

    Args:
        n: Length of the list.

    Returns:
        Indices corresponding to the middle half of the list.
    """
    # Calculate start and end indices of the middle half
    start = math.ceil(n / 4)
    end = math.floor(3 * n / 4)

    # Generate the list of indices for the middle half
    return list(range(start, end))


def aggregate_stimulus_pools(
    stimulus_pools: list[list[str]], labels: list[str]
) -> tuple[list[str], list[str]]:
    """Aggregate stimulus pools and track the labels for each stimulus.

    Args:
        stimulus_pools: List of stimulus pools.
        labels: List of labels corresponding to each stimulus pool.

    Returns:
        A list of all stimuli and a list of labels for each stimulus.
    """
    stimulus_pool = []
    stimulus_labels = []
    for pool, label in zip(stimulus_pools, labels):
        stimulus_pool.extend(pool)
        stimulus_labels.extend([label] * len(pool))
    return stimulus_pool, stimulus_labels


def generate_category_cue_indices(
    trial_count: int, list_length: int, control_proportion: float, cue_count: int, total_recalls: int
) -> list[list[int]]:
    """
    Generate indices for category cues and free recall events, alternating between them.
    Free recall events are marked with [-1].

    Args:
        trial_count: The number of trials for which to generate indices.
        list_length: The length of the list from which to sample indices.
        control_proportion: The proportion of trials with no category cue.
        cue_count: The number of category cues per trial.
        total_recalls: The total number of recall events (cued + free recall) per trial.

    Returns:
        A list of indices for each recall event per trial, with [-1] marking free recall events.
    """
    control_count = int(trial_count * control_proportion)
    indices = [[-1] * total_recalls for _ in range(control_count)]  # Control trials have only free recall
    trial_count -= control_count

    while trial_count > 0:
        serial_positions = middle_half_indices(list_length)
        random.shuffle(serial_positions)

        # Ensure we don't exceed the available positions
        needed_trials = min(trial_count, len(serial_positions) // cue_count)

        for _ in range(needed_trials):
            cued_indices = serial_positions[:cue_count]

            # Create alternating pattern of cued and free recalls
            alternating_indices = []
            cued_idx = 0
            for i in range(total_recalls):
                if i % 2 == 0 and cued_idx < cue_count:  # Cued recall at even indices
                    alternating_indices.append(cued_indices[cued_idx])
                    cued_idx += 1
                else:  # Free recall at odd indices
                    alternating_indices.append(-1)

            indices.append(alternating_indices)
            serial_positions = serial_positions[cue_count:]  # Remove used positions
            trial_count -= 1

    random.shuffle(indices)  # Shuffle to randomize control and cued trials
    return indices


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
        assert len(stimulus_pools[label_index]) >= (
            trial_count / 2
        ), f"Not enough stimuli in pool for label: {labels[label_index]}"


def sample_stimuli_for_trial(
    labels: list[str],
    subject_stimulus_pools: list[list[str]],
    last_trial_label_indices: np.ndarray,
    aggregated_stimulus_pool: list[str],
    list_length: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Samples stimuli for a trial, ensuring no category from previous trial is reused.

    Args:
        labels: List of category labels.
        subject_stimulus_pools: Stimulus pools for each subject, which are modified during sampling.
        last_trial_label_indices: Indices of labels used in the previous trial to avoid reusing them.
        aggregated_stimulus_pool: The aggregated list of all available stimuli.
        list_length: The number of stimuli to sample for the trial.

    Returns:
        A tuple containing the indices of the sampled stimuli, the strings of the sampled stimuli,
        and the indices of the category labels used in this trial.
    """
    applicable_label_indices = np.arange(len(labels))[
        ~np.isin(np.arange(len(labels)), last_trial_label_indices)
    ]
    np.random.shuffle(applicable_label_indices)

    trial_stimulus_indices = np.zeros(list_length, dtype=int)
    trial_stimulus_strings = np.zeros(list_length, dtype=object)
    trial_label_indices = []

    study_index = 0
    for label_index in applicable_label_indices:
        stimulus_pool = subject_stimulus_pools[label_index]
        stimulus_string = stimulus_pool.pop(np.random.randint(len(stimulus_pool)))

        trial_stimulus_indices[study_index] = (
            aggregated_stimulus_pool.index(stimulus_string) + 1
        )
        trial_stimulus_strings[study_index] = stimulus_string

        trial_label_indices.append(label_index)
        study_index += 1
        if study_index == list_length:
            break

    assert len(trial_label_indices) == list_length
    return trial_stimulus_indices, trial_stimulus_strings, np.array(trial_label_indices)


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


def construct_study_lists(
    labels: list[str],
    stimulus_pools: list[list[str]],
    trial_count: int,
    subject_count: int,
    list_length: int,
    cue_count: int,
    total_recalls: int,
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
        cue_count: The number of category cues per trial.
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
    pres_itemids = np.zeros((trial_count * subject_count, list_length), dtype=int)
    pres_itemstrs = np.zeros((trial_count * subject_count, list_length), dtype=object)
    category_cues = np.zeros((trial_count * subject_count, total_recalls), dtype=int)
    cat_cue_indices = np.zeros((trial_count * subject_count, total_recalls), dtype=int)

    # Loop through each subject
    for s in range(subject_count):
        subject_stimulus_pools = copy.deepcopy(stimulus_pools)
        last_trial_label_indices = np.array([])

        category_cue_indices = generate_category_cue_indices(
            trial_count, list_length, control_proportion, cue_count, total_recalls
        )
        validate_stimulus_pool_size(labels, subject_stimulus_pools, trial_count)

        # Loop through each trial
        for t in range(trial_count):
            trial_stimulus_indices, trial_stimulus_strings, last_trial_label_indices = (
                sample_stimuli_for_trial(
                    labels,
                    subject_stimulus_pools,
                    last_trial_label_indices,
                    aggregated_stimulus_pool,
                    list_length,
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

    list_length = 12
    subject_count = 300
    trial_count = 20
    control_proportion = 4 / 10
    cue_count = 3
    total_recalls = 6
    target_data_path = "experiments/category_targeting/cuefr.h5"
    target_stimulus_pool_path = "experiments/category_targeting/assets/cuefr_pool.txt"
    target_stimulus_labels_path = "experiments/category_targeting/assets/cuefr_labels.txt"
    target_category_pool_path = "experiments/category_targeting/assets/cuefr_category_pool.txt"
    source_pools_path = "experiments/category_targeting/assets/asymfr"
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
        list_length,
        cue_count,
        total_recalls,
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
