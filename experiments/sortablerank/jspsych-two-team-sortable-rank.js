const jsPsychTwoTeamSortableRank = (function(jspsych) {
  'use strict';

  const info = {
    name: 'two-team-sortable-rank',
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
        default: 'Drag and drop the items to assign them to teams.',
        description: 'Instructions to show the participant at the top of the trial.'
      },
      animation_duration: {
        type: jspsych.ParameterType.INT,
        pretty_name: 'Animation Duration',
        default: 150,
        description: 'Duration of the animation in milliseconds for the sorting.'
      },
      team_labels: {
        type: jspsych.ParameterType.ARRAY,
        pretty_name: 'Team Labels',
        default: ['Team A', 'Team B'],
        description: 'Labels for the two teams.'
      },
      required_items_team_a: {
        type: jspsych.ParameterType.INT,
        pretty_name: 'Required Items in Team A',
        default: null,
        description: 'The required number of items that must be in Team A before submission is allowed.'
      },
      error_message: {
        type: jspsych.ParameterType.STRING,
        pretty_name: 'Error Message',
        default: 'Please assign the required number of items to Your Team before proceeding.',
        description: 'The error message to display when the participant tries to submit without the required number of items in Team A.'
      },
      lock_first_item: {
        type: jspsych.ParameterType.BOOL,
        pretty_name: 'Lock First Item',
        default: true,
        description: 'If true, the first item will be non-draggable.'
      }
    }
  };

  class TwoTeamSortableRankPlugin {
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

      // Adjust logic to handle odd number of items:
      const teamASize = Math.floor(trial.items.length / 2); // Team A gets fewer items if odd
      const teamBSize = trial.items.length - teamASize; // Team B gets the rest of the items

      const teamAItems = trial.items.slice(0, teamASize);
      const teamBItems = trial.items.slice(teamASize);

      // Keep track of the overall index
      let itemIndex = 0;

      // Create the two grid containers for teams
      let teamsHtml = `
        <div class="teams-container">
          <div class="team-column">
            <h3>${trial.team_labels[0]}</h3>
            <div id="team-a-grid" class="sortable-grid team-grid">
              ${teamAItems.map((itemHtml, index) => {
                const isFiltered = trial.lock_first_item && itemIndex === 0;
                const filteredClass = isFiltered ? ' filtered' : '';
                const html = `
                  <div class="sortable-item${filteredClass}" data-id="${itemIndex}">
                    <span class="rank-number"></span>
                    ${itemHtml}
                  </div>
                `;
                itemIndex++;
                return html;
              }).join('')}
            </div>
          </div>
          <div class="team-column">
            <h3>${trial.team_labels[1]}</h3>
            <div id="team-b-grid" class="sortable-grid team-grid">
              ${teamBItems.map((itemHtml, index) => {
                const isFiltered = trial.lock_first_item && itemIndex === 0;
                const filteredClass = isFiltered ? ' filtered' : '';
                const html = `
                  <div class="sortable-item${filteredClass}" data-id="${itemIndex}">
                    <span class="rank-number"></span>
                    ${itemHtml}
                  </div>
                `;
                itemIndex++;
                return html;
              }).join('')}
            </div>
          </div>
        </div>
      `;
      displayElement.innerHTML += teamsHtml;

      // Function to update rank numbers across both teams
      function updateRankNumbers() {
        const allItems = document.querySelectorAll('.sortable-item');
        allItems.forEach((item, index) => {
          const rankNumberElement = item.querySelector('.rank-number');
          rankNumberElement.textContent = `${index + 1}${getOrdinalSuffix(index + 1)} `;
        });
      }

      // Helper function to get ordinal suffix (e.g., "1st", "2nd")
      function getOrdinalSuffix(n) {
        const s = ["th", "st", "nd", "rd"],
              v = n % 100;
        return s[(v - 20) % 10] || s[v] || s[0];
      }

      // Initialize Sortable.js for both grids
      setTimeout(() => {
        const teamAGrid = document.getElementById('team-a-grid');
        const teamBGrid = document.getElementById('team-b-grid');

        if (!teamAGrid || !teamBGrid) {
          console.error('Team grid elements not found!');
          return;
        }

        const options = {
          group: 'shared', // Enable items to be moved between grids
          animation: trial.animation_duration,
          onAdd: updateRankNumbers,
          onRemove: updateRankNumbers,
          onUpdate: updateRankNumbers,
          onSort: updateRankNumbers,
          sort: true,
          multiDrag: false,
          swapThreshold: 0.65,
          chosenClass: 'chosen',
          ghostClass: 'ghost',
          filter: '.filtered', // Items with class 'filtered' are not draggable
        };

        const sortableA = new Sortable(teamAGrid, options);
        const sortableB = new Sortable(teamBGrid, options);

        // Initial rank numbers
        updateRankNumbers();

        console.log('Sortable.js initialized for both grids.');
      }, 100); // Wait 100ms to ensure DOM is ready

      // End trial button
      displayElement.innerHTML += '<p><button id="end-trial-btn">Submit</button></p>';
      document.getElementById('end-trial-btn').addEventListener('click', () => {
        // Get the items in each team
        const teamAItems = Array.from(document.querySelectorAll('#team-a-grid .sortable-item')).map(item => item.getAttribute('data-id'));
        const teamBItems = Array.from(document.querySelectorAll('#team-b-grid .sortable-item')).map(item => item.getAttribute('data-id'));

        // Validation check for required items in Team A
        if (trial.required_items_team_a !== null && teamAItems.length !== trial.required_items_team_a) {
          alert(trial.error_message);
          return; // Do not proceed if the condition is not met
        }

        // Prepare trial data
        const allItems = Array.from(document.querySelectorAll('.sortable-item'));
        const rankedOrder = allItems.map(item => item.getAttribute('data-id'));

        const teamAItemIds = teamAItems.map(id => parseInt(id));
        const teamBItemIds = teamBItems.map(id => parseInt(id));

        const trialData = {
          ranked_order: rankedOrder.map((id, index) => ({
            rank: index + 1,
            index: parseInt(id),
            label: trial.labels[id],
            content: trial.items[id],
            team: teamAItemIds.includes(parseInt(id)) ? trial.team_labels[0] : trial.team_labels[1]
          })),
          team_a: teamAItemIds.map(id => ({
            index: id,
            label: trial.labels[id],
            content: trial.items[id]
          })),
          team_b: teamBItemIds.map(id => ({
            index: id,
            label: trial.labels[id],
            content: trial.items[id]
          }))
        };

        console.log('Trial Data:', trialData); // Log the trial data for debugging

        // End trial and store data
        this.jsPsych.finishTrial(trialData);
      });
    }
  }

  TwoTeamSortableRankPlugin.info = info;
  return TwoTeamSortableRankPlugin;
})(jsPsychModule);