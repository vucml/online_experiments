function initializeExperiment() {
    // Prepare jsPsych initialization options
    let jsPsychInitOptions = {};
    let prolific_id = '';
  
    if (typeof jatos !== 'undefined') {
        console.log('Running in JATOS');
        prolific_id = jatos.urlQueryParameters.PROLIFIC_ID || '';
        jsPsychInitOptions = {
            on_finish: (jsPsychInstance) => jatos.endStudy(jsPsychInstance.data.get().json())
        };
    } else {
        console.log('Running outside JATOS');
        prolific_id = new URLSearchParams(window.location.search).get('PROLIFIC_ID') || '';
        jsPsychInitOptions = {
            on_finish: (jsPsychInstance) => jsPsychInstance.data.displayData()
        };
    }
  
    console.log('PROLIFIC_ID:', prolific_id);
    const jsPsych = initJsPsych(jsPsychInitOptions);
    jsPsych.data.addProperties({ prolific_id });
    return jsPsych;
  }