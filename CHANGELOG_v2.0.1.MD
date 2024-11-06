1. Command-Line Interface (CLI)
a. Argument Parsing with argparse



Usage Example:

Run the simulation with custom parameters from the command line:


python main.py --doctors 5 --nurses 8 --beds 15 --sim_time 600

b. Interactive Prompts

For users who prefer not to use command-line arguments, you can provide interactive prompts using the input() function.

Implementing Interactive Prompts:

Modify the main function to ask users for input if no command-line arguments are provided.


Usage:

    If no arguments are provided, the program will prompt the user:


python main.py

mathematica

    Enter the number of doctors: 5
    Enter the number of nurses: 8

    If some arguments are provided, the program will prompt for the missing ones.

2. Graphical User Interface (GUI)

a. Web-Based Dashboard with Streamlit

Running the Streamlit App:

From the command line, run:

streamlit run app.py

This will start a local web server and open the app in your default web browser.
b. Desktop Application with Tkinter

    The GUI allows the user to input simulation parameters.
    When the "Run Simulation" button is clicked, the simulation runs with the provided parameters.
    The output is displayed in the text area at the bottom.

Running the Tkinter Application:

From the command line, run:

python gui.py



    CLI: Suitable for advanced users who prefer command-line operations and scripting.
    GUI: Ideal for users who prefer graphical interfaces and interactive exploration.


