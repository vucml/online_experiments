function initializeExperiment() {
  // Prepare jsPsych initialization options
  let jsPsychInitOptions = {};

  if (typeof jatos !== 'undefined') {
      console.log('Running in JATOS');
      jsPsychInitOptions = {
          on_finish: () => jatos.endStudy(jsPsych.data.get().json())
      };
  } else {
      console.log('Running outside JATOS');
      jsPsychInitOptions = {
          on_finish: () => jsPsych.data.displayData()
      };
  }

  // return jsPsych object
  return initJsPsych(jsPsychInitOptions);
}