const jsPsychSortableRank = (function(jspsych) {
  'use strict';

  const info = {
    name: 'sortable-rank',
    parameters: {
      items: {
        type: jspsych.ParameterType.ARRAY,
        pretty_name: 'Items',
        default: [],
        description: 'Array of objects, each representing an item with image URL and details.'
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
      // Clear display element
      displayElement.innerHTML = '';

      // Display instructions
      if (trial.instructions) {
        displayElement.innerHTML += `<p>${trial.instructions}</p>`;
      }

      // Create the list that will be sortable
      let listHtml = `<ul id="sortable-list" class="sortable-list">`;
      trial.items.forEach((item, index) => {
        listHtml += `
          <li class="sortable-item" data-id="${index}">
            <span class="rank-number">${index + 1}</span>
            <img src="${item.imageUrl}" alt="Character ${index + 1}" />
            <div>
              <p>Race: ${item.race}</p>
              <p>Sex: ${item.sex}</p>
              <p>Age: ${item.age}</p>
            </div>
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
            const order = sortable.toArray(); // Get new order after drag and drop
            console.log('New order:', order); // Log the new order of the items
          }
        });

        console.log('Sortable.js initialized:', typeof sortable !== 'undefined');
      }, 100); // Wait 100ms to ensure DOM is ready

      // Initial rank numbers
      updateRankNumbers();

      // End trial button
      displayElement.innerHTML += '<button id="end-trial-btn">Submit</button>';
      document.getElementById('end-trial-btn').addEventListener('click', () => {
        const rankedOrder = sortable ? sortable.toArray() : []; // Capture the ranked order of items
        const trialData = {
          ranked_order: rankedOrder
        };

        // End trial and store data
        this.jsPsych.finishTrial(trialData);
      });
    }
  }

  SortableRankPlugin.info = info;
  return SortableRankPlugin;
})(jsPsychModule);