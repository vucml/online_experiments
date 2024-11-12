import h5py
import numpy as np
import pandas as pd


def load_stimulus_pool(stimulus_pool_path: str) -> list[str]:
    """Load word pool from text file.

    Args:
        word_pool_path: The path to the word pool text file.

    Returns:
        The word pool as a list of strings.
    """
    with open(stimulus_pool_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def load_data(data_path: str) -> dict[str, np.ndarray]:
    """Load data from hdf5 file.

    Args:
        data_path: The path to the hdf5 file.

    Returns:
        The loaded data as a dictionary.
    """
    with h5py.File(data_path, "r") as f:
        return {key: f["/data"][key][()].T for key in f["/data"].keys()}  # type: ignore


def save_data(data: dict[str, np.ndarray], target_data_path: str):
    """Save EMBAM-formatted data to hdf5 file.

    Args:
        data: The data to save.
        target_data_path: The path to the hdf5 file.
    """
    with h5py.File(target_data_path, "w") as hdf:
        # Create a group named 'data'
        data_group = hdf.create_group("/data")

        # Loop through keys in result file and save them under the 'data' group
        for key, value in data.items():
            data_group.create_dataset(key, data=value.T)


def export_to_psifr_long_table(data: dict[str, np.ndarray]) -> pd.DataFrame:
    """Convert data in EMBAM format to long table psifr format.

    Args:
        data (dict[str, np.ndarray]): Data in EMBAM format. In EMBAM format, data is stored
        in a dictionary where each key corresponds to a different variable. The values are
        2-D numpy arrays where each row corresponds to a trial. Required fields in the EMBAM
        format are: 'subject', 'listLength', 'pres_itemnos', 'recalls'. Additional fields
        such as 'condition', 'pres_itemids', and 'rec_itemids' can identify details about
        the trial or each presented or recalled item.

    Returns:
        pd.DataFrame: A pandas DataFrame whose rows correspond to a single study or recall
        event. The required fields in each row are 'subject', 'list', 'trial_type', 'position',
        and 'item'. Additional fields can be included to describe events, e.g., 'condition'.
    """
    events = {
        "subject": [],
        "list": [],
        "trial_type": [],
        "position": [],
        "item": [],
        "condition": [],
        "target_success": [],
        "listLength": [],
        "trial_category_cue": [],
        "category": [],
    }

    # first all study events
    for trial_index, trial in enumerate(data["pres_itemids"]):
        for study_index, item in enumerate(trial):
            if item == 0:
                continue
            events["subject"].append(data["subject"][trial_index][0])
            events["list"].append(data["block"][trial_index][0])
            events["trial_type"].append("study")
            events["position"].append(study_index + 1)
            events["item"].append(item)
            events["condition"].append(data["condition"][trial_index][0])
            events["target_success"].append(data["target_success"][trial_index][0])
            events["listLength"].append(data["listLength"][trial_index][0])
            events["trial_category_cue"].append(data["category_cues"][trial_index][0])
            events["category"].append(
                data["pres_categoryids"][trial_index, study_index]
            )

    # then all recall events
    for trial_index, trial in enumerate(data["rec_itemids"]):
        for recall_index, item in enumerate(trial):
            if item == 0:
                continue
            events["subject"].append(data["subject"][trial_index][0])
            events["list"].append(data["block"][trial_index][0])
            events["trial_type"].append("recall")
            events["position"].append(recall_index + 1)
            events["item"].append(item)
            events["condition"].append(data["condition"][trial_index][0])
            events["target_success"].append(data["target_success"][trial_index][0])
            events["listLength"].append(data["listLength"][trial_index][0])
            events["trial_category_cue"].append(data["category_cues"][trial_index][0])
            events["category"].append(
                data["rec_categoryids"][trial_index, recall_index]
            )

    return pd.DataFrame.from_dict(events)
