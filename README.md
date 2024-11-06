# Healthcare-Logistics-Simulation-Tool
Healthcare Logistics Simulation Tool
This Python application uses the simpy library to simulate patient flow and resource allocation in a hospital setting. Here's how the simulation works:

    Resources:
        Doctors, Nurses, Beds: The hospital has a limited number of doctors, nurses, and beds, modeled using simpy.Resource.

    Processes:
        Patient Arrival: Patients arrive at the hospital based on an exponential distribution (on average, one every 10 minutes).
        Registration: Each patient goes through a registration process with a nurse, taking between 1 to 5 minutes.
        Triage: After registration, the patient undergoes triage with a nurse, taking between 5 to 10 minutes.
        Treatment: Finally, the patient receives treatment from a doctor while occupying a bed, taking between 15 to 45 minutes.

    Simulation Execution:
        The simulation runs for a total of 480 minutes (8 hours).
        It prints out timestamps for when each patient arrives, starts, and finishes each process, allowing you to trace the flow and identify potential bottlenecks.

Project Structure (from version 2.0 and higher)


healthcare_simulation/
├── main.py
├── entities.py
├── hospital.py
├── processes.py
├── data_analysis.py

    entities.py: Contains the Patient and StaffMember classes.
    hospital.py: Contains the Hospital class.
    processes.py: Contains functions related to patient processes.
    data_analysis.py: Contains functions for data analysis and visualization.
    main.py: The main script to run the simulation.



    The code is organized into modules, each handling specific functionalities.
 
    Classes (Patient, StaffMember, Hospital) encapsulate data and behavior.
    
    Different aspects of the simulation (entities, processes, analysis) are handled separately.
