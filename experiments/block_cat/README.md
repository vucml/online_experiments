# Mixed Cued & Free Recall Experiment

This codebase generates a design for a memory experiment that mixes free recall and category-cued recall trials. The final output is stored in a `.h5` data file along with corresponding stimulus and category pool text files. Below is a high-level overview of how the experiment is designed.

---

## Basic Structure

- **Subjects**: 300 total.  
- **Trials**: Each subject completes 20 trials, for a total of 6,000 trials across all subjects.  
- **List Length**: Each trial presents 6 items.  

A trial proceeds as follows:
1. The subject studies 6 items (one per serial position).
2. The subject attempts to recall them.  
   - Some trials are free recall only (no category cue).
   - Others include one or more category cues.

---

## Control vs. Cued Trials

- A fixed proportion (40%) of the trials use **only free recall**. These are referred to as “control” trials.  
- The remaining 60% are **cued recall** trials. In these, certain serial positions in the studied list are cued.  

In the code, cued recall positions and free recall events are stored in an array where:
- `-1` indicates a free recall event.
- A non-negative integer indicates the (0-based) position from the study list that is being cued.

---

## Targeted Positions & Spacing

- Only the “middle” portion of the list is eligible for cues (in this code, `cue_region_size=4` means positions 1–4 of the 6 are considered).  
- A minimum spacing of 2 ensures that cued positions are not chosen too close together.  
- A balancing procedure tracks how often each potential position is used. If one position has been underused relative to the others, it is more likely to get selected next.  

---

## Alternating Cued and Free Recalls

When a trial has category cues, the code places them at alternating recall events. For instance, if total recalls are 6, you might see a recall pattern like `[3, -1, 1, -1, -1, -1]`, meaning:
- First recall event is cued (the item that appeared in position 3 of the list).
- Second recall event is free recall.
- Third recall event is cued (the item from position 1), etc.

---

## Sampling Stimuli

- A set of categories (e.g., BIRDS, CLOTHES) each has its own stimulus pool.  
- Each trial’s 6 items are drawn in such a way that categories from the previous trial are avoided when possible.  
- Stimuli and categories are stored in corresponding text files, then combined into arrays.  
- Internally, item IDs are 1-indexed (i.e., 0 is reserved as a padding or placeholder).

---

## Data Structures in the Output

The `.h5` file contains several arrays, each with one row per trial (i.e., 6,000 rows total):

- **`subject`** `(n_trials, 1)`: Subject ID for each trial.  
- **`listLength`** `(n_trials, 1)`: Repeats 6 (the number of items per list).  
- **`pres_itemnos`** `(n_trials, 6)`: Array of 1 through 6, giving the position of each studied item.  
- **`pres_itemids`** `(n_trials, 6)`: The ID of each studied item in the order presented.  
- **`category_cues`** `(n_trials, total_recalls)`: The item IDs that are cued during recall. 0 values denote no cue for that recall event.  
- **`category_cue_indices`** `(n_trials, total_recalls)`: The 1-indexed positions of any cued item (or -1 if free recall).  
- **`category_cue_itemids`** `(n_trials, total_recalls)`: The actual item IDs corresponding to each cued position.

Additionally:
- **`cuefr_pool.txt`**: The list of all distinct stimuli in this experiment.  
- **`cuefr_labels.txt`**: The corresponding category label for each stimulus.  
- **`cuefr_category_pool.txt`**: The list of category names used.

---

## Summary

By integrating these steps—identifying which positions to cue, balancing their usage, alternating those cues with free recall events, and sampling items from a category pool—the code constructs a mixed free recall / category-cued recall experiment. The final `.h5` output can be used to run the experiment or to analyze the design prior to data collection.