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

How to Run the Simulation:

    Install SimPy:

    bash

pip install simpy

Run the Script:

bash

    python healthcare_simulation.py

Sample Output:

python

Patient 1 arrives at 1.03
Patient 1 starts registration at 1.03
Patient 1 finishes registration at 3.03
Patient 1 starts triage at 3.03
Patient 1 finishes triage at 9.03
Patient 1 starts treatment at 9.03
Patient 2 arrives at 3.62
Patient 2 starts registration at 3.62
