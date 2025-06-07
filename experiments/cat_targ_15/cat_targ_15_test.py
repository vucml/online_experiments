""" Purpose: Take data in h5 file to create a new text file that:
    - Generates what each trial actually looks like
    - We want to confirm that:
        -Each trial has no repeated categories
        -No category repeats between trials
        -Specific word that is cued does not get repeated, it is ok if category is repeated across cues
    - Some general math: We have 15 trials with 15 words each, therefore:
        -We need at least 30 unique categories so they don't repeat between trials
        -We need at least 15 words per category so a word is not cued multiple times
        -This seems doable, but this code will check

    What the code needs to do:
        1) Open cat_targ_15.h5 and word pool text files
        2) Loop through each trial in presitemds
            3) For each pres itemid, pull the corresponding text from the word pool file
        4) Loop through each trial in category cue indices
            5) For each serial position cued, find some way to indicate when a cueing event occurs and at what position
        6) Take this information (text string for item and cat label along with pos. cued, and spit out a text file)
    
    Target Text file format:
    TRIAL 1/ SUBJ1:
        1) Label : Item
        2) Label : Item
        3) Label : Item
        4) Label : Item
        5) Label : Item 
        6) Label : Item
        7) Label : Item 
        8) Label : Item
        9) Label : Item 
        10)Label : Item
        11)Label : Item 
        12)Label : Item
        13)Label : Item
        14)Label : Item
        15)Label : Item
    Cued position: Control
    TRIAL 2/ SUBJ1:
        -etc. . . . 
        
"""
import numpy as np
import h5py

# Load from HDF5 in read only mode "r"
with h5py.File("experiments/cat_targ_15/cat_targ_15.h5", "r") as f:
    #Loads the important data sets needed, pres_itemids, cat_cue_indices, and subject
    pres_itemids = f["/data/pres_itemids"][:]
    category_cue_indices = f["/data/category_cue_indices"][:]
    subject_ids = f["/data/subject"][:].flatten()

pres_itemids = pres_itemids.T
category_cue_indices = category_cue_indices.T
subject_ids = subject_ids.T

# Load stimulus text pool
with open("experiments/cat_targ_15/assets/cuefr_pool.txt") as f:
    stimulus_pool = [line.strip() for line in f]

# Load stimulus labels (category for each word)
with open("experiments/cat_targ_15/assets/cuefr_labels.txt") as f:
    aggregated_stimulus_labels = [line.strip() for line in f]

# Pull strings from txt files

#Create empty arrays with the same shape as pres_itemids to store the words presented and their respective labels
pres_itemstrs = np.empty_like(pres_itemids, dtype=object)
pres_itemcats = np.empty_like(pres_itemids, dtype=object)

#now, loop through every trial (i) and position (j) to convert the stimID into the word
#then, grab the label
for i in range(pres_itemids.shape[0]):
    for j in range(pres_itemids.shape[1]):
        stim_id = pres_itemids[i, j]
        pres_itemstrs[i, j] = stimulus_pool[stim_id - 1]
        pres_itemcats[i, j] = aggregated_stimulus_labels[stim_id - 1]

#now, making the desired text file
with open("experiments/cat_targ_15/trial_summary.txt", "w") as f:
    
    #the number of trials is the number of rows in the transposed pres_itemids array
    n_trials = pres_itemids.shape[0]

    #for each trial, create the header indicating trial no. and subj id
    for trial_idx in range(n_trials):
        subject_id = subject_ids[trial_idx]
        f.write(f"TRIAL {trial_idx + 1} / SUBJECT {subject_id}:\n")

        #for each serial position in pres_itemids (1-15), write its category label and item name
        for pos in range(pres_itemids.shape[1]):
            label = pres_itemcats[trial_idx, pos]
            item = pres_itemstrs[trial_idx, pos]
            f.write(f"  {pos + 1:2}) {label} : {item}\n")

        #show what position is cued in each trial using category_cue_indices
        cue_indices = category_cue_indices[trial_idx]
        cued_positions = [str(idx) for idx in cue_indices if idx > 0]
        #checks to see if there is a cue in a trial, if not, then it's a control
        if cued_positions:
            f.write(f"  Cued position(s): {', '.join(cued_positions)}\n")
        else:
            f.write("  Cued position(s): Control\n")

        f.write("\n")