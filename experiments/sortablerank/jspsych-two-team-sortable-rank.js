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
        default: ['Team A', 'Unsorted Items', 'Team B'],
        description: 'Labels for the left, middle, and right columns.'
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
      unsorted_items_error_message: {
        type: jspsych.ParameterType.STRING,
        pretty_name: 'Unsorted Items Error Message',
        default: 'Please assign all items to a team before proceeding.',
        description: 'The error message to display when there are unsorted items upon submission.'
      },
      lock_first_item: {
        type: jspsych.ParameterType.BOOL,
        pretty_name: 'Lock First Item',
        default: true,
        description: 'If true, the first item will be non-draggable and placed in Team A.'
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

      // Validate that team_labels has exactly three labels
      if (!Array.isArray(trial.team_labels) || trial.team_labels.length !== 3) {
        console.error('team_labels must be an array of three labels for the left, middle, and right columns.');
        return;
      }

      // Clear display element
      displayElement.innerHTML = '';

      // Display instructions
      if (trial.instructions) {
        const instructionsEl = document.createElement('p');
        instructionsEl.innerHTML = trial.instructions;
        displayElement.appendChild(instructionsEl);
      }

      // Create container for the columns
      const containerDiv = document.createElement('div');
      containerDiv.className = 'sortable-container';

      // Left column
      const leftColumn = document.createElement('div');
      leftColumn.className = 'sortable-column';
      const leftHeader = document.createElement('h3');
      leftHeader.textContent = trial.team_labels[0];
      const leftList = document.createElement('ul');
      leftList.id = 'team-left';
      leftList.className = 'sortable-list';
      leftColumn.appendChild(leftHeader);
      leftColumn.appendChild(leftList);

      // Middle column (unsorted items)
      const middleColumn = document.createElement('div');
      middleColumn.className = 'sortable-column';
      const middleHeader = document.createElement('h3');
      middleHeader.textContent = trial.team_labels[1];
      const middleList = document.createElement('ul');
      middleList.id = 'unsorted-items';
      middleList.className = 'sortable-list';
      middleColumn.appendChild(middleHeader);
      middleColumn.appendChild(middleList);

      // Right column
      const rightColumn = document.createElement('div');
      rightColumn.className = 'sortable-column';
      const rightHeader = document.createElement('h3');
      rightHeader.textContent = trial.team_labels[2];
      const rightList = document.createElement('ul');
      rightList.id = 'team-right';
      rightList.className = 'sortable-list';
      rightColumn.appendChild(rightHeader);
      rightColumn.appendChild(rightList);

      // Append columns to container
      containerDiv.appendChild(leftColumn);
      containerDiv.appendChild(middleColumn);
      containerDiv.appendChild(rightColumn);

      displayElement.appendChild(containerDiv);

      // Add items to lists
      // If lock_first_item is true, initialize it in Team A
      if (trial.lock_first_item) {
        const lockedItem = this.createItemElement(0, trial.items[0], true);
        leftList.appendChild(lockedItem);
      }

      // Initialize the middle column with the rest of the items
      trial.items.forEach((itemHtml, index) => {
        if (trial.lock_first_item && index === 0) return; // Skip the first item if locked

        const itemElement = this.createItemElement(index, itemHtml, false);
        middleList.appendChild(itemElement);
      });

      // Add CSS styles (with ID check to prevent duplicates)
      if (!document.getElementById('sortable-rank-styles')) {
        const style = document.createElement('style');
        style.type = 'text/css';
        style.id = 'sortable-rank-styles';
        style.innerHTML = `
          .sortable-container {
            display: flex;
            justify-content: space-between;
          }
          .sortable-column {
            width: 32%;
            box-sizing: border-box;
          }
          .sortable-list {
            min-height: 200px;
            border: 1px solid #ccc;
            padding: 5px;
            list-style-type: none;
          }
          .sortable-item {
            margin: 5px;
            padding: 5px;
            border: 1px solid #aaa;
            background-color: #f9f9f9;
            cursor: move;
            display: flex;
            align-items: center;
          }
          .sortable-item.locked-item {
            background-color: #e0e0e0;
            cursor: default;
          }
          .sortable-item.locked-item .lock-icon {
            margin-right: 5px;
          }
          .rank-number {
            font-weight: bold;
            margin-right: 5px;
          }
        `;
        document.head.appendChild(style);
      }

      // Function to update global rank numbers only for sorted items
      function updateRankNumbers() {
        let globalRank = 1;
        [leftList, rightList].forEach(list => {
          const items = list.querySelectorAll('.sortable-item');
          items.forEach(item => {
            const rankNumberEl = item.querySelector('.rank-number');
            rankNumberEl.textContent = globalRank++;
          });
        });

        // Clear rank for items in the unsorted list
        middleList.querySelectorAll('.sortable-item .rank-number').forEach(el => {
          el.textContent = '';
        });
      }

      // Initialize Sortable.js for each list after ensuring the DOM is ready
      setTimeout(() => {
        const sortableOptions = {
          group: {
            name: 'shared',
            pull: function(to, from, dragEl) {
              return !dragEl.classList.contains('locked-item');
            },
            put: true
          },
          animation: trial.animation_duration,
          onEnd: function() {
            updateRankNumbers();
          }
        };

        // Apply sortable to each list
        [middleList, leftList, rightList].forEach(list => {
          new Sortable(list, sortableOptions);
        });
      }, 100); // Wait 100ms to ensure DOM is ready

      // Initial rank numbers
      updateRankNumbers();

      // End trial button
      const endTrialBtn = document.createElement('button');
      endTrialBtn.id = 'end-trial-btn';
      endTrialBtn.textContent = 'Submit';
      displayElement.appendChild(endTrialBtn);

      // Event listener for end trial button
      endTrialBtn.addEventListener('click', () => {
        // Collect the items from each list
        const getListData = (list) => {
          const items = Array.from(list.querySelectorAll('.sortable-item'));
          return items.map(item => {
            const idAttr = item.getAttribute('data-id');
            if (idAttr === 'locked') {
              return { index: 'locked', label: 'locked', content: item.innerHTML };
            }
            const id = parseInt(idAttr, 10);
            return { index: id, label: trial.labels[id], content: trial.items[id] };
          });
        };

        const unsortedItems = getListData(middleList);
        const teamLeftItems = getListData(leftList);
        const teamRightItems = getListData(rightList);

        // Validation: Check that there are no unsorted items
        if (unsortedItems.length > 0) {
          alert(trial.unsorted_items_error_message);
          return;
        }

        // Validation: Check required_items_team_a
        if (trial.required_items_team_a !== null) {
          const numItemsInTeamA = teamLeftItems.length;
          if (numItemsInTeamA !== trial.required_items_team_a) {
            alert(trial.error_message);
            return;
          }
        }

        // Prepare trial data
        const trialData = {
          unsorted_items: unsortedItems,
          team_left_items: teamLeftItems,
          team_right_items: teamRightItems
        };

        // End trial and store data
        this.jsPsych.finishTrial(trialData);
      });
    }

    // Helper function to create item element
    createItemElement(index, itemHtml, isLocked) {
      const li = document.createElement('li');
      li.className = 'sortable-item';
      if (isLocked) {
        li.classList.add('locked-item');
        li.setAttribute('data-id', 'locked');
      } else {
        li.setAttribute('data-id', index);
      }

      // Rank number (initially empty for unsorted items)
      const rankNumber = document.createElement('span');
      rankNumber.className = 'rank-number';
      rankNumber.textContent = ''; // No rank displayed initially
      li.appendChild(rankNumber);

      // Lock icon if locked
      if (isLocked) {
        const lockIcon = document.createElement('span');
        lockIcon.className = 'lock-icon';
        lockIcon.textContent = '🔒';
        li.appendChild(lockIcon);
      }

      // Item content
      const contentDiv = document.createElement('div');
      contentDiv.innerHTML = itemHtml;
      li.appendChild(contentDiv);

      return li;
    }
  }

  SortableRankPlugin.info = info;
  return SortableRankPlugin;
})(jsPsychModule);