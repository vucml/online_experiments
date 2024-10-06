function initializeExperiment(timeline) {
  // Prepare jsPsych initialization options
  let jsPsychInitOptions = {};

  if (typeof jatos !== 'undefined') {
      console.log('Running in JATOS');
      jsPsychInitOptions = {
          on_trial_start: jatos.addAbortButton,
          on_finish: () => jatos.endStudy(jsPsych.data.get().json())
      };
  } else {
      console.log('Running outside JATOS');
      jsPsychInitOptions = {
          on_finish: () => jsPsych.data.displayData()
      };
  }

  // Initialize jsPsych and run the experiment
  const jsPsych = initJsPsych(jsPsychInitOptions);
  jsPsych.run(timeline);
}