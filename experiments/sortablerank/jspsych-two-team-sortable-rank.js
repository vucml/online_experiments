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
  
        // Split items into two teams based on their index
        const half = Math.ceil(trial.items.length / 2);
        const teamAItems = trial.items.slice(0, half);
        const teamBItems = trial.items.slice(half);
  
        // Create the two grid containers for teams
        let teamsHtml = `
          <div class="teams-container">
            <div class="team-column">
              <h3>${trial.team_labels[0]}</h3>
              <div id="team-a-grid" class="sortable-grid team-grid">
                ${teamAItems.map((itemHtml, index) => `
                  <div class="sortable-item" data-id="${index}">
                    <span class="rank-number"></span>
                    ${itemHtml}
                  </div>
                `).join('')}
              </div>
            </div>
            <div class="team-column">
              <h3>${trial.team_labels[1]}</h3>
              <div id="team-b-grid" class="sortable-grid team-grid">
                ${teamBItems.map((itemHtml, index) => `
                  <div class="sortable-item" data-id="${index + half}">
                    <span class="rank-number"></span>
                    ${itemHtml}
                  </div>
                `).join('')}
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
            // Set the sorting in grid mode
            sort: true,
            // Define the grid layout
            multiDrag: false,
            swapThreshold: 0.65,
            // Enable grid layout by specifying the chosenClass and fallbackClass
            chosenClass: 'chosen',
            ghostClass: 'ghost',
          };
  
          const sortableA = new Sortable(teamAGrid, { ...options, direction: 'horizontal' });
          const sortableB = new Sortable(teamBGrid, { ...options, direction: 'horizontal' });
  
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
  
          // Prepare trial data
          const allItems = Array.from(document.querySelectorAll('.sortable-item'));
          const rankedOrder = allItems.map(item => item.getAttribute('data-id'));
  
          const trialData = {
            ranked_order: rankedOrder.map((id, index) => ({
              rank: index + 1,
              index: id,
              label: trial.labels[id],
              content: trial.items[id],
              team: teamAItems.includes(id) ? trial.team_labels[0] : trial.team_labels[1]
            })),
            team_a: teamAItems.map(id => ({
              index: id,
              label: trial.labels[id],
              content: trial.items[id]
            })),
            team_b: teamBItems.map(id => ({
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