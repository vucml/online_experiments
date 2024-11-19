import * as hdf5 from "https://cdn.jsdelivr.net/npm/h5wasm@latest/dist/esm/hdf5_hl.js";

function transpose(matrix) {
  return matrix[0].map((col, i) => matrix.map(row => row[i]));
}

function unique_entries(array) {
  return [...new Set(array)];
}

function getEntriesBySubjectIndex(data, query, subjectID) {
  const subjectIndex = data.get("subject").to_array()[0];
  const queried_array = transpose(data.get(query).to_array());
  const entries = [];
  for (let i = 0; i < subjectIndex.length; i++) {
    if (subjectIndex[i] === subjectID) {
      entries.push(queried_array[i]);
    }
  }
  return entries;
}

async function loadH5Data(data_path) {
  await hdf5.ready;

  const data_response = await fetch(data_path);
  const data_ab = await data_response.arrayBuffer();

  hdf5.FS.writeFile('temp', new Uint8Array(data_ab));
  const f = new hdf5.File('temp', 'r');
  
  return f.get("data");
}

async function loadItemPool(pool_path) {
  const response = await fetch(pool_path);
  const text = await response.text();
  return text.split('\n');
}

function getAvailableSubjects(data, batchSession) {
  let subject = data.get("subject").to_array()[0];
  let subjectIds;
  if (!batchSession.defined('/subjectIds')) {
    subjectIds = [... new Set(subject)]
    batchSession.set('subjectIds', subjectIds)
  } else {
    subjectIds = batchSession.get('subjectIds');
  }
  return subjectIds;
}

function configureSubject(data, batchSession) {
  let subjectIds = getAvailableSubjects(data, batchSession);

  // set current subj_id to next available subject id
  if (subjectIds.length == 0) {
    throw new Error("Max number of subjects reached");
  }
  const subjectId = subjectIds.shift();

  // update batchsession to reflect used subject id
  batchSession.set('subjectIds', subjectIds);

  return subjectId;
}

function getTrialPresentations(data) {
  const trial_data = data.trials
  const trial_presentations = trial_data.filter(
    entry => entry.trial_type === "item-presentation");
  return trial_presentations[trial_presentations.length - 1].word_list;
}

function getAllPresentations(data) {
  const trial_data = data.trials;
  const trial_presentations = trial_data.filter(entry => entry.trial_type === "item-presentation");
  return trial_presentations.map(presentation => presentation.word_list);
}

function getTrialRecalls(data) {
  const trial_data = data.trials;

  // Find the index of the last "item-presentation"
  const last_presentation_index = trial_data.map(entry => entry.trial_type).lastIndexOf("item-presentation");

  // Collect all "free-recall" entries after the last "item-presentation"
  const trial_recalls = trial_data.filter((entry, idx) => 
    idx > last_presentation_index && entry.trial_type === "free-recall"
  );

  // Flatten the array of recall words into a single array of strings
  // Return an empty string if recall_words is missing or empty for each free-recall event
  return trial_recalls.map(recall => {
    if (!recall.recall_words || recall.recall_words.length === 0) {
      return "";  // If recall_words is empty or undefined, return an empty string
    }
    return recall.recall_words;  // Otherwise, return the recall_words as is
  }).flat();  // Flatten in case recall_words is an array (e.g., multiple words)
}

// Needs update before we can use this again due to possibility of 
// multiple free recall elements in timeline per trial
// function getTrialCues(data) {
//   const trial_data = data.trials
//   const trial_recalls = trial_data.filter(
//     entry => entry.trial_type === "free-recall");
//   return trial_recalls.map(recall => recall.category_cue);
// }

function getAllRecalls(data) {
  const trial_data = data.trials;

  // Find the indices of all "item-presentation" events
  const presentation_indices = trial_data
    .map((entry, idx) => entry.trial_type === "item-presentation" ? idx : null)
    .filter(idx => idx !== null);

  // Group the recalls that follow each item-presentation event
  const grouped_recalls = presentation_indices.map((pres_idx, i) => {
    const next_pres_idx = presentation_indices[i + 1] || trial_data.length;
    
    // Get the recall events that follow this presentation
    const trial_recalls = trial_data
      .slice(pres_idx + 1, next_pres_idx)  // All events after the presentation until the next one
      .filter(entry => entry.trial_type === "free-recall")
      .map(recall => {
        // If recall_words is missing or empty, return an empty string
        if (!recall.recall_words || recall.recall_words.length === 0) {
          return "";  // Return an empty string for missing or empty recall_words
        }
        return recall.recall_words;  // Otherwise, return recall_words as is
      });

    return trial_recalls.flat();  // Flatten in case recall_words contains multiple words
  });

  return grouped_recalls;
}

function stripAndLowerCase(str) {
  // This regex removes \r, \n, and spaces from both ends of the string
  return str.replace(/^[\r\n\s]+|[\r\n\s]+$/g, '').toLowerCase();
}

function levenshteinDistance(s1, s2) {
  if (s1.length === 0) return s2.length;
  if (s2.length === 0) return s1.length;

  const matrix = [];

  // Increment along the first column of each row
  for (let i = 0; i <= s2.length; i++) {
      matrix[i] = [i];
  }

  // Increment each column in the first row
  for (let j = 0; j <= s1.length; j++) {
      matrix[0][j] = j;
  }

  // Fill in the rest of the matrix
  for (let i = 1; i <= s2.length; i++) {
      for (let j = 1; j <= s1.length; j++) {
          if (s2.charAt(i - 1) === s1.charAt(j - 1)) {
              matrix[i][j] = matrix[i - 1][j - 1];
          } else {
              matrix[i][j] = Math.min(
                  matrix[i - 1][j - 1] + 1, // substitution
                  matrix[i][j - 1] + 1, // insertion
                  matrix[i - 1][j] + 1 // deletion
              );
          }
      }
  }

  return matrix[s2.length][s1.length];
}

function findClosestPresentation(str, presentationSet, threshold) {
  let closestPresentation = null;
  let minDistance = Infinity;

  for (const presentation of presentationSet) {
    const distance = levenshteinDistance(str, presentation);
    if (distance <= threshold && distance < minDistance) {
      closestPresentation = presentation;
      minDistance = distance;
    }
  }

  return closestPresentation;
}

function getTrialTargetSuccess(data, category_target_string, recall_index, threshold = 2) {
  const trial_recalls = getTrialRecalls(data);  // Collect all recalls after last "item-presentation"
  
  // Get the recall event specified by recall_index
  const selected_recall = stripAndLowerCase(trial_recalls[recall_index]);
  if (!selected_recall || !category_target_string) {
    return false;
  }

  // Compare the first recall word with the category target
  const distance = levenshteinDistance(stripAndLowerCase(category_target_string), selected_recall);

  return distance <= threshold;
}

function getTotalTargetSuccess(data, category_targets, threshold = 2) {
    const allRecalls = getAllRecalls(data); // Get all recall events
    let totalSuccessCount = 0;
  
    // Iterate over each trial's recalls
    for (let i = 0; i < allRecalls.length; i++) {
      const trial_recalls = allRecalls[i].flat().map(element => stripAndLowerCase(element)); // Get all recalls for this trial
  
      // Iterate over each recall event (up to 6 in this case)
      for (let j = 0; j < category_targets[i].length; j++) {
        const target = category_targets[i][j]; // Get the category target for this recall event
  
        // Skip if no recall was made or no category target exists for this event
        if (!trial_recalls[j] || !target) {
          continue;
        }
  
        // Check the Levenshtein distance between the recalled word and the category target
        const distance = levenshteinDistance(stripAndLowerCase(target), trial_recalls[j]);
        if (distance <= threshold) {
          totalSuccessCount++; // Count as a successful recall if distance is within threshold
        }
      }
    }
  
    return totalSuccessCount;
  }

function getRecallMatches(recalls, presentations, threshold) {
  // NOTE: this doesn't care if category cues are correctly answered
  let matchCount = 0;
  const matchedPresentations = new Set(); // Keep track of matched recalls

  recalls.forEach(recall => {
    const closestPresentation = findClosestPresentation(recall, presentations, threshold);
    if (closestPresentation && !matchedPresentations.has(closestPresentation)) {
      matchCount++;
      matchedPresentations.add(closestPresentation);
    }
  });
  return matchCount; // Only returning matchCount since matchedPresentations is modified in place
}

function getTrialPerformance(data, threshold = 2) {
  const trial_presentations = getTrialPresentations(data).map(element => stripAndLowerCase(element));
  const trial_recalls = getTrialRecalls(data).map(element => stripAndLowerCase(element));
  return getRecallMatches(trial_recalls, trial_presentations, threshold);
}

function getTotalPerformance(data, threshold = 2) {
  const allPresentations = getAllPresentations(data);
  const allRecalls = getAllRecalls(data);
  let totalMatchCount = 0;

  // Iterate through each trial
  for (let i = 0; i < allPresentations.length; i++) {
    // Retrieve presentations and recalls for the current trial
    const trialPresentations = allPresentations[i].flat().map(stripAndLowerCase);
    const trialRecalls = allRecalls[i].flat().map(stripAndLowerCase);
    totalMatchCount += getRecallMatches(trialRecalls, trialPresentations, threshold);
  }

  // Return the total number of matches found
  return totalMatchCount;
}

function calculateBonus(data, category_targets, threshold = 2, bonusPerTrial = 0.03125, target_bonus_multiple = 5, maximumBonus = 10.0) {
  const targetPerformance = getTotalTargetSuccess(data, category_targets, threshold);  // Successes for cued targets
  const basePerformance = getTotalPerformance(data, threshold) - targetPerformance;    // Non-cued recalls
  const base_bonus = basePerformance * bonusPerTrial;
  const target_bonus = targetPerformance * bonusPerTrial * target_bonus_multiple;

    console.log("Base performance: " + basePerformance);
    console.log("Target performance: " + targetPerformance);
    console.log("Base bonus: " + base_bonus);
    console.log("Target bonus: " + target_bonus);
    console.log("Total bonus: " + Math.min(base_bonus + target_bonus, maximumBonus));
    
  return Math.min(base_bonus + target_bonus, maximumBonus);
}

export { transpose, unique_entries, getEntriesBySubjectIndex, loadH5Data, loadItemPool, getAvailableSubjects, configureSubject, getTrialPresentations, getTrialRecalls, getAllPresentations, getAllRecalls, getTrialPerformance, getTotalPerformance, calculateBonus, getTrialTargetSuccess };