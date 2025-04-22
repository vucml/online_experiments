Check sidebar for main experiment demo.

# online_experiments

This repository attempts to streamline the process of creating and running browser-based experiments using JavaScript, HTML, and CSS. We try to:

- Provide a simple template and workflow for creating experiments.
- Host demos of experiments to showcase the capabilities of the template and provide examples for customization.
- Highlight resources and tutorials for learning more about experiment design and coding and accelerating the development process.

Check our [experiments directory](experiments/) for a list of examples of experiments that can be previewed.

## Overview

You can think of this repository as a thin guide and set of examples for getting started using two libraries to create and run experiments online. The two libraries are jsPsych and JATOS.

- [jsPsych](https://www.jspsych.org/): A JavaScript library for creating behavioral experiments that run in a web browser. Experiments in jsPsych are created using plugins. Each plugin defines different kinds of events, like showing an image on the screen, and collects different kinds of data, like recording which key was pressed at which time. You can use the plugins that are included with jsPsych, use plugins that are developed by community members or the lab, or create your own plugins. By assembling different plugins together into a timeline, it is possible to create a wide range of experiments.
- [JATOS](https://www.jatos.org/): If jsPsych is for creating experiments, JATOS is for running them. JATOS is a server that runs on your computer or on a server. It manages the participants, the study assets, and the data. It also provides a web-based user interface for researchers to manage their studies and participants.

It's useful to read the documentation and tutorials for both libraries to understand how they work and how to use them. They are probably higher quality and more up-to-date than the information provided here.

## Uses for Experienced Developers

If you already know how to create experiments using jsPsych and how to run them using JATOS, this repository and README still provides a useful framework for organizing your experiments and sharing them with others. 

- **Using JATOS without locking out useful tools.** The main feature we showcase is how to implement your jsPsych experiment so that it can be demoed neatly using VSCode's Live Server extension and Github Pages, facilitating the development process and making it easier to share in-progress experiments with others. The current instructions for interfacing jsPsych with JATOS tend to make this impossible by creating a dependency on the JATOS server. Our template sidesteps this issue by providing an `initializeExperiment` function that works differently depending on whether the experiment is being run in JATOS or not.

- **Configuring behavior between conditions/subjects across hosting platforms.** In our more detailed experiment examples, we also show how to configure experiments in a separate config file that can be dynamically updated to change the experiment's behavior without updates to experiment code. This is a useful feature for running multiple versions of an experiment or for running an experiment with different conditions, or where study sequences presented to different subjects must be carefully controlled based on subject ID or other factors. The documentation for JATOS shows how to do this within their system, but our template provides for flexibility across different hosting environments.

- **Basic and detailed experiment implementation archive.** We provide basic examples of experiments that can be run using Github Pages or JATOS or Live Server. These examples can be used as a starting point for creating your own experiments. We also provide more detailed examples that show how to configure experiments to run in different conditions or with different sequences of stimuli.

## Some Basics

### HTML, CSS, and JavaScript

HTML, CSS, and JavaScript are the three core technologies for creating web pages.

- **HTML** (HyperText Markup Language) is the standard markup language for documents designed to be displayed in a web browser. Think of it as the skeleton of a web page. It consists of a series of elements that you use to enclose, or wrap, different parts of the content to make it appear a certain way or act a certain way.
- **CSS** (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML. It controls the layout of multiple web pages all at once. With CSS, you can control the color, font, the size of text, the spacing between elements, how elements are positioned and laid out, what background images or colors are used, and much more.
- **JavaScript** is a programming language that enables you to create dynamically updating content, control multimedia, animate images, and much more. It is the programming language of the web. It is used to make web pages interactive and provide online programs, including video games. 

### Git and GitHub

Git is a distributed version control system that allows you to track changes in your code and collaborate with others. GitHub is a web-based platform that hosts Git repositories and provides tools for collaboration.

You are probably used to collaborating on documents using Google Docs or Microsoft Word. Git is like that, but for code. It allows you to keep track of changes you make to your code, revert to previous versions, and collaborate with others on the same codebase.

At the same time, it has some limitations that make it different from Google Docs. For example, you can't edit the same file at the same time as someone else. You have to take turns. This is because Git is designed to prevent conflicts between different versions of the same file, as well as to track who made what changes and when so that you can revert to or just look at a previous version if necessary.

Github is a platform that hosts Git repositories. It provides a web-based interface for managing your repositories, as well as tools for collaboration, like issues, pull requests, and project boards. It also provides a way to host static websites, including demo versions of your experiments.

### Recommended Tools and Software

Here are some tools we recommend. If you are code-savvy, you can decide for yourself which tools you want to use. If you are new to coding, we recommend using the tools listed below.

- Visual Studio Code: A popular and fre code editor. It has a massive extensions marketplace that can help you with stuff like syntax highlighting, code completion, and debugging. It is available for Windows, macOS, and Linux. You can download it [here](https://code.visualstudio.com/).
- GitHub Desktop: A graphical user interface for GitHub. This will make it easy for you to copy the files from this repository to your computer and to upload your changes back to GitHub. It is available for Windows and macOS. You can download it [here](https://desktop.github.com/).
- JATOS: A server that runs on your computer or on a server. It manages the participants, the study assets, and the data. It also provides a web-based user interface for researchers to manage their studies and participants. You can download it [here](https://www.jatos.org/Installation.html).
- Java: To run JATOS, you might need Java. At the moment, I recommend installing the JRE appropriate for your operating system from [here](https://adoptium.net/temurin/archive/?version=11). This has been tricky to set up for students despite JATOS's detailed installation instructions, so I recommend this route for now. If you are having trouble, please let me know.

In Visual Studio Code, you can install extensions that will help you with coding and debugging. Honestly, they are a game-changer. In particular, I recommend the following extensions for experiment development:

- Live Server: This extension launches a development local server with live reload feature for static and dynamic pages. It feels great getting feedback on a change to your code in real-time. This is especially useful for debugging experiments. You can install it [here](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer).
- Github Copilot: This extension provides AI-powered code completions in your editor. It's a pretty powerful Microsoft product. It is a paid service, but it's free for academics. You can install it [here](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot).
- Live Share: This extension allows you to share your code with others and collaborate in real-time. It's a great way to get help with your code. You can install it [here](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare).
- Prettier: This extension formats your code automatically. It's a great way to keep your code clean and readable. You can install it [here](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode).

## A Bird's Eye View of the Workflow for Creating and Running Experiments

### 1. Install and Initialize JATOS

Install [JATOS](https://www.jatos.org/) and initialize by following [these](https://www.jatos.org/Installation.html) instructions.

JATOS is a bit weird when it comes to playing nice with GitHub repositories, so we have to set it up first. The installation instructions for JATOS describe how to start the server and access the web interface; the precise way is specific to your OS. You can find the instructions [here](https://www.jatos.org/Installation.html). 

Once you log in, click "New Study" in the top left of the JATOS UI. Use any name for the experiment (e.g., "My Experiment") and confirm.  

On the management page for the study, click "Properties" to access study properties. We want to update your "Study assets' directory name" to the name of the repository you will be using for your study. For example, when using this repository (which we recommend when getting sarted!), you'd use its name. This will create an empty folder in the JATOS directory where you can store your study assets. 

### 2. Clone the Repository

Next, we want to clone your experiment repository (usually *this* repository!) to your computer at the JATOS study assets directory you just created. 

You might not know what cloning is: it's a way to copy the files from this repository to your computer. If you are new to git and Github, I suggest using Github Desktop. [This page](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop) should provide the most up-to-date instructions for cloning a repository using GitHub Desktop. 

The right place to clone your repository is inside the JATOS folder you created. If your JATOS is installed at the path `/jatos/` and your repository is named `my_experiment`, you should clone the repository to `/jatos/study_assets_root/my_experiment`. 

**IMPORTANT**: Make sure you don't accidentally clone to `/jatos/study_assets_root/my_experiment/my_experiment`. You want to replace the pre-existing `my_experiment` folder with the contents of the repository you are cloning.

If you've cloned using Github Desktop, you should be able to open your project in Visual Studio Code by clicking "Repository" menu option and then the "Open in Visual Studio Code" button in the Github Desktop interface. 

You can similarly open the project in your file explorer by clicking the "Show in Explorer/Finder" button.

### Optional: Make a New Branch (or Experiment Directory)

If you want to make changes to the repository, it's a good idea to create a new branch. A branch is a version of the repository that extends from and exists alongside the main version. You can make changes to the branch without affecting the main version. Once you are happy with the changes, you can merge the branch back into the main version.

[Here's](https://docs.github.com/en/desktop/making-changes-in-a-branch/managing-branches-in-github-desktop) the documentation for managing branches in Github Desktop.

[Here's](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository) the documentation for managing branches right on Github.

Another less robust but understandably popular way to manage different versions of your experiment is to create a new directory in the `experiments` directory for each new experiment you want to create. This is a good way to keep experiments separate from each other and to avoid conflicts between different versions of the same experiment. For new developers, branch management is maybe a bit more complicated than it needs to be. A new directory for each experiment should be sufficient for most purposes.

### 3. Add An Experiment's HTML file to JATOS
Not every html file in your repository is automatically associated with an experiment in JATOS. You have to manually add the file to JATOS as an experiment **Component**.

Go to the JATOS web interface and click on the study you created. Click on the "+ New Component" button. Give the component a name and also the file path for the HTML file you want associated with the experiment. 

Once you do this, as long as the HTML file is in the study assets directory and has no errors, you can click "Run" to start the experiment.

### 4. Updating Your Experiment

We've organized this repository to categorize code you shouldn't have to change (like the jsPsych library) and code you should change (like the experiment's HTML file) in order to make an experiment unique to your research.

Core files are located in the `core` directory. These files are the same for every experiment you create. You shouldn't have to change them, but sometimes you might want to, particularly if implementing a custom plugin or feature.

The `experiments` directory is where you will create your experiments. Each experiment should have its own directory. Inside the experiment directory, you should have an HTML file that contains the experiment code. You can also have a CSS file and a JavaScript file if you want to separate the code into different files. When getting started, just stick to a single HTML file and don't worry about the CSS and JavaScript files.

At this point, you need to get familiar with the documentation for jsPsych to understand how to create experiments. You can find the documentation [here](https://www.jspsych.org/). Its tutorials are pretty beautiful; there's no point in me trying to outdo them here.

You can find an example experiment in the `experiments` directory. You can copy this directory and rename it to create a new experiment. You can then edit the HTML file to create your experiment.

### 5. Previewing Changes As You Code Using Live Server

We've provided functions that make it normally easy to preview your experiment without having to run it in JATOS as you code. This is the `initializeExperiment` function you see in most of the pre-existing experiment html files in the `experiments` directory. 

If you've installed the Live Server extension in Visual Studio Code, you can right-click on the HTML file you want to preview and select "Open with Live Server". 

This will open a new tab in your browser with the experiment. Every time you save the HTML file, the changes will be reflected in the browser. This is a great way to see how your experiment looks as you code, streamlining the development process.

When you run an experiment outside of JATOS using our template, the data will be presented to you at the end of the experiment within your browser in the JSON format (by default) or whatever format you've configured it to be in. 

While running an experiment this way, the default is usually to display arbitrary stimuli, not specific to any particular subject or condition. Managing the selection of a subject ID so that you don't repeat the same subject across different runs of the experiment requires interaction with previous runs of the experiment. This is where a backend tool like JATOS comes in. However, the exact details of how stimuli are presented/assigned and how data is saved can be customized in the experiment's JavaScript code. For your purposes, it's possible that you won't even need JATOS to run your experiment, especially if you're just testing ideas or running an in-person pilot study.

### 6. Debugging Your Experiment

In VSCode, you can use the debugger to set breakpoints in your code and step through it line by line. This is a great way to figure out what's going wrong in your experiment. It's best to rely on VSCode's [documentation](https://code.visualstudio.com/docs/editor/debugging) for how to use the debugger.

Sometimes it can be hard to tell where your breakpoints should go! When previewing an experiment, whether using Live Server or in JATOS, you can use the browser's developer tools to inspect the HTML, CSS, and JavaScript of the page. You usually can do this by right-clicking on the page and selecting "Inspect" or by pressing `Ctrl+Shift+I`. You usually also want to go to the "Console" tab to see any errors that are occurring. This will identify the number and an error code that you can use to debug your code. 

Setting breakpoints near where the error is occurring can help you figure out what's going wrong. AI tools like ChatGPT can also sometimes interpret the error code and provide a solution, particularly if you share your code with them and if the error is common.

### 7. Previewing Changes in JATOS

When you are ready to test your experiment in JATOS, use the "Run" button in the JATOS web interface. This will start the experiment in your same browser tab. If anything in your code uses JATOS-specific functions, like saving data, you will need to test it in JATOS.

If the experiment is configured properly to run in JATOS, you should see the experiment run as it would in a real study. Once the experiment finishes, the "Results" panel in JATOS for your study should include a row for the run you just completed. Under the "State" column, it should be marked as "FINISHED", rather than "FAIL" or "DATA_RETRIEVED" or something else. Clicking a dropdown arrow for your run should show you the data that was collected during the experiment.

An "Export Results" button at the top of the "Results" panel will allow you to download the data across runs in a variety of formats.

### Sharing Your Experiment Using GitHub Pages

While developing your experiment, you may want to share it with others to get feedback or to run a pilot study. You can use GitHub Pages to host your experiment online, though you won't have a JATOS backend to manage participants and data. This is usually insufficient for a real study, but it's great for testing ideas or running in-person pilot studies.

To host your experiment on GitHub Pages, first commit and then push your changes to your repository on GitHub. Here's a [guide](https://docs.github.com/en/desktop/making-changes-in-a-branch/pushing-changes-to-github-from-github-desktop) on how to do that.

This next stuff has already been done for this repository. Once your changes are on GitHub, go to the repository on GitHub and click on the "Settings" tab. Then on the left, find the "Pages" tab. You can then select the branch you want to host your site from. Usually, you want to select the `main` or `master` branch. Click "Save" and your site should be live at the URL provided, though it may take a few minutes to update.

The URL for your experiment will be `https://<your-username-or-organization-name>.github.io/<repository-name>/<path-to-your-experiment-html>`. For example, `https://githubpsyche.github.io/jspsych2150/free_recall.html` is the URL for a free recall experiment in the `jspsych2150` repository owned by `githubpsyche` located at the file path `free_recall.html` in said repository.

### 9. Sharing Your Experiment using JATOS

Once you are happy with your experiment, you can share it with others. Unless you're running experiments in person, you will need to host your experiment on a JATOS server instance that is accessible to others. 

JATOS has documentation for how to do this. You can find it [here](https://www.jatos.org/Bring-your-JATOS-online.html). Most of the solutions are kind of complicated for a first-timer, but you can always ask for help.

However, the creators of JATOS have also provided their own JATOS server that makes it especially easy to host experiments online. This service is called MindProbe and can be found [here](https://mindprobe.eu/). To host an experiment on MindProbe, you first create an account and log-in.  You'll then see a JATOS interface just like the one you have on your computer. This one is hosted on the web, and so can serve links to your experiments to anyone with the link.

To host your experiment here instead of locally, first go back to your local JATOS interface and click "Export Study" for the study you want to host. This will download a `.jzip` file that contains all your study assets and key information about your study.

Then go to the MindProbe interface and click "Import Study". You can then upload the `.jzip` file you just downloaded. This will create a study on the MindProbe server that you can run and share with others.

Now to actually share your experiment, go to "Study Links" in the MindProbe interface for your study. What to do next depends on how you want to serve your experiment. There are different options depending on if you're using MTurk or Prolific or just want to share a link. The right link also depends on whether you want the link to be reusable or not, or if you want the link to only work for one participant or an unlimited number of participants. At this point, you should consult the JATOS documentation for how to share your experiment for sure. Or talk to someone who knows how to do it!

Just as in our description of local JATOS-based development, once the experiment finishes, the "Results" panel in JATOS for your study should include a row for the run you just completed. Under the "State" column, it should be marked as "FINISHED", rather than "FAIL" or "DATA_RETRIEVED" or something else. Clicking a dropdown arrow for your run should show you the data that was collected during the experiment. An "Export Results" button at the top of the "Results" panel will allow you to download the data across runs in a variety of formats.

