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
import json
import numpy as np
from helpers import load_stimulus_pool, load_data, save_data


# %%
def load_jsonl(file_path: str) -> list[list[dict]]:
    """
    Load and parse a file where each line is a JSON-encoded string representing
    a participant's response data across trials.

    Args:
        file_path: Path to the file containing the data.

    Returns:
        participants_data: Inner lists contain recorded entries for a participant and trial.
    """
    participants_data = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                participant_data = json.loads(line.strip())
                participants_data.append(participant_data)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")
    return participants_data


# %%
def retrieve_study_items(participants_data: list[list[dict]]) -> list[list[str]]:
    """
    Extracts study items from item-presentation trials across all participants.

    Args:
        participants_data: List of lists of dictionaries, where each inner list contains recorded entries for a participant and trial.

    Returns:
        Inner lists contain study items for a participant and trial combination.
    """
    all_study_items = []
    for participant_data in participants_data:
        for entry in participant_data:
            if entry.get("trial_type") == "item-presentation":
                words = entry.get("word_list", [])
                all_study_items.append([w.strip() for w in words])
    return all_study_items


# %%
def retrieve_study_item_categories(
    participants_data, cat_pool
) -> tuple[list[list[str]], list[list[int]]]:
    """Extracts study item categories from item-presentation trials across all participants.


    Args:
        participants_data: List of lists of dictionaries, where each inner list contains recorded entries for a participant and trial.
        cat_pool: The complete list of category cues in the stimulus pool.

    Returns:
        tuple: A tuple containing:
            - List of lists of study item categories.
            - List of lists of indices of study item categories in the category pool.
    """
    all_study_categories = []
    all_study_category_indices = []
    for participant_data in participants_data:
        for entry in participant_data:
            if entry.get("trial_type") == "item-presentation":
                words = [w.strip() for w in entry.get("category_list", [])]
                all_study_categories.append(words)
                all_study_category_indices.append(
                    [cat_pool.index(w)+1 for w in words])
    return all_study_categories, all_study_category_indices


# %%
def generate_subject_ids(participants_data: list[list[dict]]) -> list[int]:
    """
    Selects unique subject id from item-presentation trials across all participants.

    Args:
        participants_data: List of lists of dictionaries, where each inner list contains recorded entries for a participant and trial.

    Returns:
        Contains subject id for a participant and trial combination.
    """
    subject_ids = []
    for subject_id, participant_data in enumerate(participants_data):
        subject_ids.extend(
            subject_id
            for entry in participant_data
            if entry.get("trial_type") == "item-presentation"
        )
    return subject_ids


# %%
def retrieve_block_indices(participants_data: list[list[dict]]) -> list[int]:
    """
    Tracks block index over item-presentation trials across all participants.

    Args:
        participants_data: List of lists of dictionaries, where each inner list contains recorded entries for a participant and trial.

    Returns:
        Contains block index for a participant and trial combination.
    """
    block_ids = []
    for participant_data in participants_data:
        block_index = 1
        for entry in participant_data:
            if entry.get("trial_type") == "item-presentation":
                block_ids.append(block_index)
                block_index += 1
    return block_ids


# %%
def retrieve_recall_words(participants_data: list[list[dict]]) -> list[list[str]]:
    """
    Extracts "recall_words" entry from trials across all participants.

    Args:
        participants_data: List of lists, where each inner list represents a participant's response data across trials.

    Returns:
        Inner lists contain recall words for a participant and trial combination.
    """
    all_recall_words = []
    for participant_data in participants_data:
        trial_index = 0
        words = []
        for entry in participant_data:
            if "word_list" in entry:
                if trial_index > 0:
                    all_recall_words.append(words)
                    words = []
                trial_index += 1
                continue
            if "recall_words" in entry:
                words += entry.get("recall_words", [])
        all_recall_words.append(words)
    return all_recall_words


# %%
def retrieve_recall_cues(
    participants_data: list[list[dict]], cat_pool: list[str]
) -> tuple[list[str], list[int]]:
    """
    Extracts "category_cue" entry from trials across all participants and index in cat_pool.

    Args:
        participants_data: List of lists, where each inner list represents a participant's response data across trials.
        cat_pool: The complete list of category cues in the stimulus pool.

    Returns:
        tuple: A tuple containing:
            - Recall cues.
            - Indices of recall cues in the category pool.
    """
    all_recall_cues = []
    all_recall_cue_indices = []
    for participant_data in participants_data:
        trial_index = 0
        recall_cues = []
        recall_cue_indices = []
        for entry in participant_data:
            if "word_list" in entry:
                if trial_index > 0:
                    all_recall_cues.append(recall_cues)
                    all_recall_cue_indices.append(recall_cue_indices)
                    recall_cues = []
                    recall_cue_indices = []
                trial_index += 1
                continue
            if "category_cue" in entry:
                cue = entry.get("category_cue", "").strip()
                recall_cues.append(cue)
                if cue:
                    recall_cue_indices.append(cat_pool.index(cue) + 1)
                else:
                    recall_cue_indices.append(0)
        all_recall_cues.append(recall_cues)
        all_recall_cue_indices.append(recall_cue_indices)
                
    return all_recall_cues, all_recall_cue_indices


# %%
def pad_lists(lists, minimum_length):
    """
    Pad the input lists with zeros to at least a specified length.

    Args:
        lists: The input lists to be padded.
        minimum_length: The minimum desired length of the padded lists.

    Returns:
        The padded lists.
    """
    padded_lists = []
    max_length = max(len(lst) for lst in lists)
    minimum_length = max(minimum_length, max_length)
    padded_lists.extend(lst + [0] * (minimum_length - len(lst)) for lst in lists)
    return padded_lists


# %%
def levenshtein(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1: The first string.
        s2: The second string.

    Returns:
        The Levenshtein distance between the two strings.
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


# %%
def match_recall_word(
    recall_word: str, study_items: list[str], threshold: float
) -> int:
    """
    Match a recall word to study items based on their similarity using the Levenshtein distance.

    Args:
        recall_word: The recall word.
        study_items: A list of study items.
        threshold: The maximum allowed distance for a match.

    Returns:
        int: The index indicating the best match for the recall word. If no match is found within the threshold, -1 is returned.
    """
    best_match = {"index": None, "distance": float("inf")}
    for index, study_word in enumerate(study_items):
        distance = levenshtein(recall_word.lower(), study_word.lower().strip())
        if distance < best_match["distance"]:
            best_match = {"index": index, "distance": distance}
    # If the best match is within the threshold, return the index
    return best_match["index"] if best_match["distance"] <= threshold else -1


# %%
def retrieve_recall_pres_positions(
    participants_data: list[list[dict]],
    threshold: float,
    include_intrusions: bool = False,
) -> list[list[int]]:
    """
    Extracts recall indices from trials across all participants.

    Args:
        participants_data: List of lists, where each inner list represents a participant's response data across trials.
        threshold: The maximum allowed distance for a match.
        include_intrusions: Whether to include intrusions in the recall indices. Defaults to False.

    Returns:
        A list of lists of indices where inner lists contain 1-indexed recall indices for a participant and trial.
    """
    all_recall_indices = []
    study_items = retrieve_study_items(participants_data)
    recall_words = retrieve_recall_words(participants_data)
    for participant_study_items, participant_recall_words in zip(
        study_items, recall_words
    ):
        participant_recall_indices = [
            match_recall_word(recall_word, participant_study_items, threshold)
            for recall_word in participant_recall_words
        ]
        participant_recall_indices = [
            p for p in participant_recall_indices if (p != -1 or include_intrusions)
        ]
        participant_recall_indices = [
            (p + 1 if p != -1 else -1) for p in participant_recall_indices
        ]
        all_recall_indices.append(participant_recall_indices)
    return all_recall_indices


# %%
def retrieve_recall_pres_ids(
    participants_data: list[list[dict]],
    threshold: float,
    word_pool: list[str],
    include_intrusions: bool = False,
) -> list[list[int]]:
    """
    Finds the index of recalled non-intrusion items in the word pool.

    Intrusions may occur in the word pool, so the index of the first match is returned.
    -1 is returned for items unmatched to any word in the word pool.

    Args:
        participants_data: List of lists, where each inner list represents a participant's response data across trials.
        threshold: The maximum allowed distance for a match.
        word_pool: The complete list of words in the stimulus pool.
        include_intrusions: Flag indicating whether to include intrusion items in the recall list. Defaults to False.

    Returns:
        list of lists of indices in the word pool for applicable recalled items.
    """
    word_pool_indices = []
    study_items = retrieve_study_items(participants_data)
    recalls = retrieve_recall_pres_positions(
        participants_data, threshold, include_intrusions
    )
    for participant_study_items, participant_recalls in zip(study_items, recalls):
        participant_recids = []
        for index in participant_recalls:
            study_word = participant_study_items[index - 1]
            word_pool_index = word_pool.index(study_word)
            if word_pool_index != -1:
                participant_recids.append(word_pool_index + 1)
            else:
                participant_recids.append(-1)
        word_pool_indices.append(participant_recids)
    return word_pool_indices


# %%
def retrieve_recall_item_categories(
    participants_data: list[list[dict]], cat_pool: list[str], threshold: float, include_intrusions: bool = False
) -> tuple[list[list[str]], list[list[int]]]:
    """
    Extracts recall item categories from free-recall trials across all participants.

    Args:
        participants_data: List of lists of dictionaries, where each inner list contains recorded entries for a participant and trial.
        cat_pool: The complete list of category cues in the stimulus pool.
        threshold: The maximum allowed distance for a match.
        include_intrusions: Flag indicating whether to include intrusion items in the recall list. Defaults to False.

    Returns:
        tuple: A tuple containing:
            - List of lists of recall item categories.
            - List of lists of indices of recall item categories in the category pool.
    """
    study_cats, study_cat_ids = retrieve_study_item_categories(
        participants_data, cat_pool)
    recalls = retrieve_recall_pres_positions(
        participants_data, threshold, include_intrusions
    )
    all_recall_categories = []
    all_recall_category_indices = []
    for participant_study_cats, participant_study_catids, participant_recalls in zip(study_cats, study_cat_ids, recalls):
        participant_recall_cats = []
        participant_recall_cat_ids = []
        for index in participant_recalls:
            participant_recall_cats.append(participant_study_cats[index - 1])
            participant_recall_cat_ids.append(participant_study_catids[index - 1])
        all_recall_categories.append(participant_recall_cats)
        all_recall_category_indices.append(participant_recall_cat_ids)
    return all_recall_categories, all_recall_category_indices


# %%
def retrieve_pres_itemids(
    participants_data: list[list[dict]], word_pool: list[str]
) -> list[list[int]]:
    """
    Finds the index of presented items in the word pool.

    Args:
        participants_data: List of lists, where each inner list represents a participant's response data across trials.
        word_pool: The complete list of words in the stimulus pool.

    Returns:
        list of lists of indices in the word pool for applicable presented items.
    """
    word_pool_indices = []
    study_items = retrieve_study_items(participants_data)
    for participant_study_items in study_items:
        participant_word_pool_indices = []
        for study_word in participant_study_items:
            word_pool_index = word_pool.index(study_word)
            assert word_pool_index != -1, f"Word {study_word} not found in word pool"
            participant_word_pool_indices.append(word_pool_index + 1)
        word_pool_indices.append(participant_word_pool_indices)
    return word_pool_indices


# %%
if __name__ == "__main__":
    jatos_data_path = "experiments/cat_target_short/pooled.jsonl"
    stimulus_pool_path = "experiments/cat_target_short/assets/cuefr_pool.txt"
    category_pool_path = "experiments/cat_target_short/assets/cuefr_category_pool.txt"
    target_data_path = "experiments/cat_target_short/expt_milind_pooled.h5"
    include_intrusions = False
    distance_threshold = 2

    data = load_jsonl(jatos_data_path)
    word_pool = load_stimulus_pool(stimulus_pool_path)
    cat_pool = load_stimulus_pool(category_pool_path)
    study_items = retrieve_study_items(data)
    study_item_categories, study_category_ids = retrieve_study_item_categories(data, cat_pool)
    recall_words = retrieve_recall_words(data)
    subject_ids = np.array(generate_subject_ids(data))
    block_indices = np.array(retrieve_block_indices(data))
    category_cues, category_ids = retrieve_recall_cues(data, cat_pool)
    recall_item_categories, recall_category_ids = retrieve_recall_item_categories(data, cat_pool, distance_threshold, include_intrusions)
    category_ids = np.array(category_ids)

    pres_itemids = np.array(retrieve_pres_itemids(data, word_pool))
    assert np.sum(pres_itemids == 0) == 0, "Variable list length across study lists"
    study_category_ids = np.array(study_category_ids)
    list_length = max(len(lst) for lst in study_items)
    list_lengths = np.array([list_length] * len(pres_itemids))

    recalls = np.array(
        pad_lists(
            retrieve_recall_pres_positions(
                data, distance_threshold, include_intrusions
            ),
            list_length,
        )
    )
    rec_itemids = np.array(
        pad_lists(
            retrieve_recall_pres_ids(
                data, distance_threshold, word_pool, include_intrusions
            ),
            list_length,
        )
    )
    rec_categoryids = np.array(pad_lists(recall_category_ids, list_length))

    # if category_ids second dimension length is not same as recall_category_ids second dimension length, then pad the category_ids with zeros to match
    if category_ids.shape[1] != rec_categoryids.shape[1]:
        reference_array = np.zeros_like(rec_categoryids)
        reference_array[:, :category_ids.shape[1]] = category_ids
        category_ids = reference_array


    for (
        participant_study_items,
        participant_study_ids,
        participant_study_item_categories,
        participant_study_category_ids,
        participant_cues,
        participant_cue_ids,
        participant_recall_words,
        participant_recalls,
        participant_recids,
        participant_rec_cat_ids,
        participant_recall_categorys,
        participant_subjectids,
        participant_blockids,
    ) in zip(
        study_items,
        pres_itemids,
        study_item_categories,
        study_category_ids,
        category_cues,
        category_ids,
        recall_words,
        recalls,
        rec_itemids,
        rec_categoryids,
        recall_item_categories,
        subject_ids,
        block_indices,
    ):
        print("Study items:", participant_study_items)
        print("Study IDs:", participant_study_ids)
        print("Study item categories:", participant_study_item_categories)
        print("Study item category ids:", participant_study_category_ids)
        print("Category cue:", participant_cues)
        print("Category cue ID:", participant_cue_ids)
        print("Recall words:", participant_recall_words)
        print("Recall word categories:", participant_recall_categorys)
        print("Recall Presentation Positions:", participant_recalls)
        print("Recall Presentation IDs:", participant_recids)
        print("Recall category ids:", participant_rec_cat_ids)
        print("Subject ID:", participant_subjectids)
        print("Block ID:", participant_blockids)
        print()

    control_condition = category_ids == 0
    targetting_condition = category_ids != 0
    successful_targetting = np.logical_and(targetting_condition, category_ids == rec_categoryids)
    three_conditions = targetting_condition.astype(int) + successful_targetting
    print(np.sum(successful_targetting)/np.sum(targetting_condition))

    # construct data dict
    result: dict[str, np.ndarray] = {
        "condition": three_conditions,
        "target_success": successful_targetting,
        "listLength": list_lengths[:, np.newaxis],
        "category_cues": category_ids,
        "pres_itemids": pres_itemids,
        "pres_categoryids": study_category_ids,
        "pres_itemnos": np.tile(np.arange(1, list_length + 1), (len(pres_itemids), 1)),
        "subject": subject_ids[:, np.newaxis],
        "rec_itemids": rec_itemids,
        "rec_categoryids": rec_categoryids,
        "recalls": recalls,
        "block": block_indices[:, np.newaxis],
    }

    save_data(result, target_data_path)
    loaded_result = load_data(target_data_path)

    assert np.min(loaded_result["pres_itemids"]) > 0
    assert np.max(loaded_result["pres_itemids"]) > list_length
    assert np.min(loaded_result["pres_itemnos"]) == 1

    for key, value in loaded_result.items():
        assert np.ndim(value) == 2

# %%
