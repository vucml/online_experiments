const jsPsychSortableRank = (function(jspsych) {
  'use strict';

  const info = {
    name: 'sortable-rank',
    parameters: {
      items: {
        type: jspsych.ParameterType.ARRAY,
        pretty_name: 'Items',
        default: [],
        description: 'Array of HTML strings or elements to be rendered as items.'
      },
      labels: {
        type: jspsych.ParameterType.ARRAY,
        pretty_name: 'Labels',
        default: [],
        description: 'Array of labels (e.g., image filenames) corresponding to each item.'
      },
      instructions: {
        type: jspsych.ParameterType.STRING,
        pretty_name: 'Instructions',
        default: 'Drag and drop the items to rank them.',
        description: 'Instructions to show the participant at the top of the trial.'
      },
      animation_duration: {
        type: jspsych.ParameterType.INT,
        pretty_name: 'Animation Duration',
        default: 150,
        description: 'Duration of the animation in milliseconds for the sorting.'
      }
    }
  };

  class SortableRankPlugin {
    constructor(jsPsych) {
      this.jsPsych = jsPsych;
    }

    trial(displayElement, trial) {
      // Validate that labels array matches items array length
      if (trial.labels.length !== trial.items.length) {
        console.error('The length of the labels array does not match the length of the items array.');
        return;
      }

      // Clear display element
      displayElement.innerHTML = '';

      // Display instructions
      if (trial.instructions) {
        displayElement.innerHTML += `<p>${trial.instructions}</p>`;
      }

      // Create the list that will be sortable
      let listHtml = `<ul id="sortable-list" class="sortable-list">`;
      trial.items.forEach((itemHtml, index) => {
        listHtml += `
          <li class="sortable-item" data-id="${index}">
            <span class="rank-number">${index + 1}</span>
            ${itemHtml} <!-- Render HTML passed from the experiment -->
          </li>
        `;
      });
      listHtml += `</ul>`;
      displayElement.innerHTML += listHtml;

      // Function to update rank numbers
      function updateRankNumbers() {
        const items = document.querySelectorAll('.sortable-item');
        items.forEach((item, index) => {
          item.querySelector('.rank-number').textContent = index + 1;
        });
      }

      // Declare `sortable` outside of setTimeout so it can be accessed globally in this scope
      let sortable;

      // Check if the sortable list is ready before initializing Sortable.js
      setTimeout(() => {
        const listElement = document.getElementById('sortable-list');
        if (!listElement) {
          console.error('Sortable list element not found!');
          return;
        }

        // Initialize Sortable.js
        sortable = new Sortable(listElement, {
          animation: trial.animation_duration,
          onEnd: function(evt) {
            updateRankNumbers(); // Update the rank numbers after each sort
          }
        });

        console.log('Sortable.js initialized:', typeof sortable !== 'undefined');
      }, 100); // Wait 100ms to ensure DOM is ready

      // Initial rank numbers
      updateRankNumbers();

      // End trial button
      displayElement.innerHTML += '<p><button id="end-trial-btn">Submit</button></p>';
      document.getElementById('end-trial-btn').addEventListener('click', () => {
        const rankedOrder = sortable ? sortable.toArray() : []; // Capture the ranked order of items as IDs

        // Log and save both the ranked order, labels, and corresponding item content
        const trialData = {
          ranked_order: rankedOrder.map(id => ({
            index: id,  // The id of the item (which corresponds to the original index)
            label: trial.labels[id],  // Include the label (e.g., filename) for each item
            content: trial.items[id]  // Save the content of each item based on the index
          }))
        };

        console.log('Trial Data:', trialData); // Log the trial data for debugging

        // End trial and store data
        this.jsPsych.finishTrial(trialData);
      });
    }
  }

  SortableRankPlugin.info = info;
  return SortableRankPlugin;
})(jsPsychModule);