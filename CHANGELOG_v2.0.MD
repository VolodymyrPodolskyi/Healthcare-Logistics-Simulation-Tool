Project Structure

Here's the proposed project structure:

css

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

1. entities.py

This module contains the Patient and StaffMember classes.

python

# entities.py

import random

class Patient:
    """Represents a patient with various attributes."""
    def __init__(self, patient_id, patient_type, severity_level, arrival_time):
        self.patient_id = patient_id
        self.patient_type = patient_type  # 'emergency', 'scheduled', 'walk-in'
        self.severity_level = severity_level  # 1 (low) to 5 (high)
        self.age = random.randint(1, 100)
        self.gender = random.choice(['Male', 'Female'])
        self.medical_history = random.choice(['None', 'Chronic Illness', 'Previous Surgery'])
        self.arrival_time = arrival_time

        # Determine if the patient needs surgery or diagnostics
        self.needs_surgery = False
        self.needs_diagnostics = False
        if self.patient_type == 'emergency' and self.severity_level >= 4:
            self.needs_surgery = True
        elif self.severity_level >= 3:
            self.needs_diagnostics = True

        # Code blue status
        self.code_blue = False
        if self.patient_type == 'emergency' and random.random() < 0.1:
            self.code_blue = True

        # Metrics
        self.timestamps = {}  # Dictionary to store timestamps of each process

class StaffMember:
    """Represents a staff member with shifts and breaks."""
    def __init__(self, env, role, name, shift_duration, break_duration):
        self.env = env
        self.role = role
        self.name = name
        self.shift_duration = shift_duration
        self.break_duration = break_duration
        self.is_available = True
        self.action = env.process(self.work())

    def work(self):
        while True:
            # Work shift
            shift_end = self.env.now + self.shift_duration
            while self.env.now < shift_end:
                # Take a break at a random time during the shift
                break_time = self.env.now + random.randint(60, self.shift_duration - 60)
                yield self.env.timeout(break_time - self.env.now)
                self.is_available = False
                print(f'{self.role} {self.name} is on break at {self.env.now:.2f}')
                yield self.env.timeout(self.break_duration)
                self.is_available = True
                print(f'{self.role} {self.name} returns from break at {self.env.now:.2f}')
            # Shift over
            self.is_available = False
            print(f'{self.role} {self.name} ends shift at {self.env.now:.2f}')
            # Hand over to next shift (simulate handover time)
            yield self.env.timeout(5)
            self.is_available = True
            print(f'{self.role} {self.name} starts new shift at {self.env.now:.2f}')

Explanation:

    Patient Class:
        Models patient attributes and determines if they need surgery or diagnostics.
        Includes a timestamps dictionary for recording process times.
    StaffMember Class:
        Simulates staff shifts and breaks using SimPy processes.
        The work method handles the staff member's availability.

2. hospital.py

This module contains the Hospital class, which manages resources and processes.

python

# hospital.py

import random
import simpy
from simpy.resources.resource import PriorityResource
from entities import StaffMember, Patient
from processes import patient_process

class Hospital:
    """Manages hospital resources and processes."""
    def __init__(self, env, config):
        self.env = env
        self.config = config
        # Staff resources
        self.doctor = PriorityResource(env, capacity=config['NUM_DOCTORS'])
        self.nurse = PriorityResource(env, capacity=config['NUM_NURSES'])
        self.specialist = PriorityResource(env, capacity=config['NUM_SPECIALISTS'])
        self.admin_staff = PriorityResource(env, capacity=config['NUM_ADMIN_STAFF'])
        self.support_staff = PriorityResource(env, capacity=config['NUM_SUPPORT_STAFF'])
        
        # Facility resources
        self.bed = PriorityResource(env, capacity=config['NUM_BEDS'])
        self.operating_room = PriorityResource(env, capacity=config['NUM_OPERATING_ROOMS'])
        self.lab = PriorityResource(env, capacity=config['NUM_LABS'])
        self.imaging_center = PriorityResource(env, capacity=config['NUM_IMAGING_CENTERS'])
        
        # Equipment resources
        self.medical_equipment = PriorityResource(env, capacity=config['NUM_MEDICAL_EQUIPMENT'])
        
        # Staff members
        self.initialize_staff()

        # Data collection
        self.patients = []  # List to store all patient objects for analysis
        self.resource_log = []  # Log for resource utilization

        # Dynamic processes
        env.process(self.collect_resource_utilization())
        env.process(self.monitor_patient_influx())

    def initialize_staff(self):
        """Initializes staff members based on the configuration."""
        c = self.config
        self.doctors = [StaffMember(self.env, 'Doctor', f'Doctor_{i+1}', c['SHIFT_DURATION'], c['BREAK_DURATION']) for i in range(c['NUM_DOCTORS'])]
        self.nurses = [StaffMember(self.env, 'Nurse', f'Nurse_{i+1}', c['SHIFT_DURATION'], c['BREAK_DURATION']) for i in range(c['NUM_NURSES'])]
        self.specialists = [StaffMember(self.env, 'Specialist', f'Specialist_{i+1}', c['SHIFT_DURATION'], c['BREAK_DURATION']) for i in range(c['NUM_SPECIALISTS'])]
        self.admin_staff_members = [StaffMember(self.env, 'AdminStaff', f'Admin_{i+1}', c['SHIFT_DURATION'], c['BREAK_DURATION']) for i in range(c['NUM_ADMIN_STAFF'])]
        self.support_staff_members = [StaffMember(self.env, 'SupportStaff', f'Support_{i+1}', c['SHIFT_DURATION'], c['BREAK_DURATION']) for i in range(c['NUM_SUPPORT_STAFF'])]

    def registration(self, patient):
        """Registration process conducted by administrative staff and nurse."""
        registration_time = random.randint(1, 5)
        yield self.env.timeout(registration_time)
    
    def triage(self, patient):
        """Triage process conducted by a nurse."""
        triage_time = random.randint(5, 10)
        yield self.env.timeout(triage_time)

    def diagnostics(self, patient):
        """Diagnostics process conducted in lab or imaging center."""
        diagnostics_time = random.randint(10, 30)
        yield self.env.timeout(diagnostics_time)

    def surgery(self, patient):
        """Surgery process conducted by a specialist in operating room."""
        surgery_time = random.randint(30, 90)
        yield self.env.timeout(surgery_time)

    def treatment(self, patient):
        """Treatment process conducted by a doctor."""
        base_treatment_time = random.randint(15, 45)
        severity_factor = (6 - patient.severity_level)
        treatment_time = base_treatment_time * severity_factor / 5
        yield self.env.timeout(treatment_time)

    def code_blue_response(self, patient):
        """Handles code blue emergency situations."""
        print(f'Code Blue! Patient {patient.patient_id} requires immediate attention at {self.env.now:.2f}')
        response_time = random.randint(5, 15)
        yield self.env.timeout(response_time)
        print(f'Patient {patient.patient_id} stabilized after Code Blue at {self.env.now:.2f}')

    def disaster_response(self):
        """Simulates a disaster scenario with sudden influx of patients."""
        print(f'Disaster occurred at {self.env.now:.2f}! Sudden influx of patients.')
        num_additional_patients = random.randint(5, 15)
        for _ in range(num_additional_patients):
            patient_id = 'D' + str(random.randint(1000, 9999))
            severity_level = random.randint(3, 5)
            patient = Patient(patient_id, 'emergency', severity_level, self.env.now)
            self.env.process(patient_process(self.env, patient, self))

    def monitor_patient_influx(self):
        """Monitors patient influx and triggers disaster response if needed."""
        while True:
            yield self.env.timeout(60)
            if random.random() < 0.05:
                yield self.env.process(self.disaster_response())

    def collect_resource_utilization(self):
        """Collects data on resource utilization at each time step."""
        while True:
            # Record the utilization of each resource
            self.resource_log.append({
                'time': self.env.now,
                'doctor_utilization': self.doctor.count / self.config['NUM_DOCTORS'],
                'nurse_utilization': self.nurse.count / self.config['NUM_NURSES'],
                'bed_utilization': self.bed.count / self.config['NUM_BEDS'],
                'specialist_utilization': self.specialist.count / self.config['NUM_SPECIALISTS'],
                'operating_room_utilization': self.operating_room.count / self.config['NUM_OPERATING_ROOMS'],
                'lab_utilization': self.lab.count / self.config['NUM_LABS'],
                'imaging_center_utilization': self.imaging_center.count / self.config['NUM_IMAGING_CENTERS'],
                'medical_equipment_utilization': self.medical_equipment.count / self.config['NUM_MEDICAL_EQUIPMENT']
            })
            yield self.env.timeout(1)  # Collect data every 1 minute

Explanation:

    Hospital Class:
        Manages all resources and processes within the hospital.
        Contains methods for each process (e.g., registration, triage, treatment).
        Handles emergency situations like code blue and disaster response.
        Collects resource utilization data for analysis.

3. processes.py

This module contains functions for patient processes and arrivals.

python

# processes.py

import random
from entities import Patient
from hospital import Hospital

def patient_process(env, patient, hospital):
    """Simulates the process flow of a single patient."""
    arrival_time = env.now
    patient.timestamps['arrival'] = arrival_time
    print(f'Patient {patient.patient_id} ({patient.patient_type}, Severity {patient.severity_level}) arrives at {env.now:.2f}')
    
    # Handle Code Blue scenarios immediately
    if patient.code_blue:
        with hospital.doctor.request(priority=0) as doctor_request:
            yield doctor_request
            yield env.process(hospital.code_blue_response(patient))
        patient.timestamps['discharge'] = env.now
        hospital.patients.append(patient)
        return
    
    # Registration (skip for emergency patients)
    if patient.patient_type != 'emergency':
        with hospital.admin_staff.request(priority=patient.severity_level) as admin_request, \
             hospital.nurse.request(priority=patient.severity_level) as nurse_request:
            reg_start = env.now
            yield admin_request & nurse_request
            wait_time = env.now - reg_start
            patient.timestamps['registration_wait'] = wait_time
            patient.timestamps['registration_start'] = env.now
            yield env.process(hospital.registration(patient))
            patient.timestamps['registration_end'] = env.now
    
    # Triage
    with hospital.nurse.request(priority=patient.severity_level) as nurse_request:
        triage_start = env.now
        yield nurse_request
        wait_time = env.now - triage_start
        patient.timestamps['triage_wait'] = wait_time
        patient.timestamps['triage_start'] = env.now
        yield env.process(hospital.triage(patient))
        patient.timestamps['triage_end'] = env.now
    
    # Diagnostics if needed
    if patient.needs_diagnostics:
        if random.choice(['lab', 'imaging_center']) == 'lab':
            facility = hospital.lab
            facility_name = 'lab'
        else:
            facility = hospital.imaging_center
            facility_name = 'imaging center'
        with hospital.support_staff.request(priority=patient.severity_level) as support_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request, \
             facility.request(priority=patient.severity_level) as facility_request:
            diag_start = env.now
            yield support_request & equipment_request & facility_request
            wait_time = env.now - diag_start
            patient.timestamps['diagnostics_wait'] = wait_time
            patient.timestamps['diagnostics_start'] = env.now
            yield env.process(hospital.diagnostics(patient))
            patient.timestamps['diagnostics_end'] = env.now
    
    # Surgery if needed
    if patient.needs_surgery:
        with hospital.specialist.request(priority=patient.severity_level) as specialist_request, \
             hospital.operating_room.request(priority=patient.severity_level) as or_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
            surg_start = env.now
            yield specialist_request & or_request & equipment_request
            wait_time = env.now - surg_start
            patient.timestamps['surgery_wait'] = wait_time
            patient.timestamps['surgery_start'] = env.now
            yield env.process(hospital.surgery(patient))
            patient.timestamps['surgery_end'] = env.now
        # Recovery after surgery
        with hospital.bed.request(priority=patient.severity_level) as bed_request:
            recov_start = env.now
            yield bed_request
            wait_time = env.now - recov_start
            patient.timestamps['recovery_wait'] = wait_time
            patient.timestamps['recovery_start'] = env.now
            recovery_time = random.randint(30, 60)
            yield env.timeout(recovery_time)
            patient.timestamps['recovery_end'] = env.now
    else:
        # Treatment (if no surgery)
        with hospital.doctor.request(priority=patient.severity_level) as doctor_request, \
             hospital.bed.request(priority=patient.severity_level) as bed_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
            treat_start = env.now
            yield doctor_request & bed_request & equipment_request
            wait_time = env.now - treat_start
            patient.timestamps['treatment_wait'] = wait_time
            patient.timestamps['treatment_start'] = env.now
            yield env.process(hospital.treatment(patient))
            patient.timestamps['treatment_end'] = env.now
    
    # Patient discharge
    patient.timestamps['discharge'] = env.now
    hospital.patients.append(patient)

def patient_arrivals(env, hospital, config):
    """Generates patients arriving at the hospital."""
    patient_num = 0
    while True:
        # Determine patient type and arrival time based on type
        patient_type = random.choices(
            ['emergency', 'scheduled', 'walk-in'],
            weights=[1, 2, 7],
            k=1
        )[0]
        
        if patient_type == 'emergency':
            inter_arrival_time = random.expovariate(1/30)
            severity_level = random.randint(4, 5)
        elif patient_type == 'scheduled':
            inter_arrival_time = random.expovariate(1/15)
            severity_level = random.randint(2, 3)
        else:  # walk-in
            inter_arrival_time = random.expovariate(1/10)
            severity_level = random.randint(1, 4)
        
        yield env.timeout(inter_arrival_time)
        patient_num += 1
        arrival_time = env.now
        patient = Patient(patient_num, patient_type, severity_level, arrival_time)
        env.process(patient_process(env, patient, hospital))

Explanation:

    patient_process Function:
        Manages the journey of a patient through the hospital.
        Records timestamps for each process for later analysis.
    patient_arrivals Function:
        Simulates patient arrivals based on defined probabilities.
        Creates Patient instances and initiates their processes.

4. data_analysis.py

This module contains the analyze_data function for data analysis and visualization.

python

# data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

def analyze_data(hospital):
    """Analyzes collected data and generates reports."""
    # Create DataFrame from patient data
    patient_data = []
    for patient in hospital.patients:
        data = {
            'patient_id': patient.patient_id,
            'patient_type': patient.patient_type,
            'severity_level': patient.severity_level,
            'arrival_time': patient.arrival_time,
            'total_time_in_system': patient.timestamps['discharge'] - patient.arrival_time
        }
        # Calculate wait times and service times
        for key in ['registration', 'triage', 'diagnostics', 'surgery', 'treatment', 'recovery']:
            wait_key = f'{key}_wait'
            start_key = f'{key}_start'
            end_key = f'{key}_end'
            data[f'{key}_wait_time'] = patient.timestamps.get(wait_key, 0)
            if start_key in patient.timestamps and end_key in patient.timestamps:
                data[f'{key}_service_time'] = patient.timestamps[end_key] - patient.timestamps[start_key]
            else:
                data[f'{key}_service_time'] = 0
        patient_data.append(data)
    
    df_patients = pd.DataFrame(patient_data)
    
    # Calculate KPIs
    print("\nPerformance Metrics:")
    print("Average Total Time in System: {:.2f} minutes".format(df_patients['total_time_in_system'].mean()))
    print("Average Waiting Times:")
    wait_time_cols = [col for col in df_patients.columns if 'wait_time' in col]
    for col in wait_time_cols:
        avg_wait = df_patients[col].mean()
        print(f"  {col.replace('_wait_time', '').title()}: {avg_wait:.2f} minutes")
    print("Average Service Times:")
    service_time_cols = [col for col in df_patients.columns if 'service_time' in col]
    for col in service_time_cols:
        avg_service = df_patients[col].mean()
        print(f"  {col.replace('_service_time', '').title()}: {avg_service:.2f} minutes")
    
    # Resource Utilization
    df_resources = pd.DataFrame(hospital.resource_log)
    avg_utilization = df_resources.mean()
    print("\nAverage Resource Utilization:")
    for resource in ['doctor', 'nurse', 'bed', 'specialist', 'operating_room', 'lab', 'imaging_center', 'medical_equipment']:
        utilization = avg_utilization[f'{resource}_utilization'] * 100
        print(f"  {resource.title().replace('_', ' ')}: {utilization:.2f}%")
    
    # Bottleneck Identification
    print("\nBottleneck Analysis:")
    max_wait_time_cols = df_patients[wait_time_cols].max()
    for col in wait_time_cols:
        max_wait = max_wait_time_cols[col]
        print(f"  Maximum {col.replace('_wait_time', '').title()} Wait Time: {max_wait:.2f} minutes")
    
    # Visualizations
    # Plot resource utilization over time
    plt.figure(figsize=(10, 6))
    for resource in ['doctor', 'nurse', 'bed']:
        plt.plot(df_resources['time'], df_resources[f'{resource}_utilization'], label=f'{resource.title()}')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Utilization')
    plt.title('Resource Utilization Over Time')
    plt.legend()
    plt.show()
    
    # Histogram of total time in system
    plt.figure(figsize=(8, 5))
    plt.hist(df_patients['total_time_in_system'], bins=20, edgecolor='black')
    plt.xlabel('Total Time in System (minutes)')
    plt.ylabel('Number of Patients')
    plt.title('Distribution of Total Time in System')
    plt.show()

Explanation:

    analyze_data Function:
        Processes the collected data to compute performance metrics.
        Generates visualizations for resource utilization and patient time in the system.

5. main.py

This is the main script to run the simulation.

python

# main.py

import simpy
import random
from hospital import Hospital
from processes import patient_arrivals
from data_analysis import analyze_data

def main():
    """Runs the simulation and performs data analysis."""
    # Simulation configuration
    RANDOM_SEED = 42
    SIM_TIME = 480  # Simulation time in minutes (e.g., 8 hours)
    
    # Hospital resource quantities
    config = {
        'NUM_DOCTORS': 3,
        'NUM_NURSES': 5,
        'NUM_BEDS': 10,
        'NUM_SPECIALISTS': 2,
        'NUM_ADMIN_STAFF': 3,
        'NUM_SUPPORT_STAFF': 4,
        'NUM_OPERATING_ROOMS': 1,
        'NUM_LABS': 2,
        'NUM_IMAGING_CENTERS': 1,
        'NUM_MEDICAL_EQUIPMENT': 5,
        'SHIFT_DURATION': 240,  # 4 hours
        'BREAK_DURATION': 15,   # 15 minutes
    }
    
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(env, config)
    env.process(patient_arrivals(env, hospital, config))
    env.run(until=SIM_TIME)
    
    # Data Analysis
    analyze_data(hospital)

if __name__ == '__main__':
    main()

Explanation:

    main Function:
        Sets up the simulation environment and configurations.
        Initializes the hospital and starts the patient arrivals process.
        Runs the simulation and calls the data analysis function after completion.

Summary of Refactoring and OOP Implementation

    Modular Design:
        The code is organized into modules, each handling specific functionalities.
        Enhances readability and makes the codebase easier to navigate.
    Object-Oriented Programming:
        Classes (Patient, StaffMember, Hospital) encapsulate data and behavior.
        Promotes code reuse and simplifies maintenance.
    Separation of Concerns:
        Different aspects of the simulation (entities, processes, analysis) are handled separately.
        Makes it easier to modify or extend specific parts without affecting others.
    Maintainability and Scalability:
        The modular, OOP approach makes it straightforward to add new features or resources.
        Enhances collaboration among multiple developers.

Next Steps

    Unit Testing:
        Implement unit tests for each module to ensure code reliability.
    Documentation:
        Add comprehensive docstrings and comments to explain code functionality.
    Error Handling:
        Include exception handling to manage unexpected scenarios gracefully.
    Logging:
        Replace print statements with a logging framework for better control over output levels.

By refactoring your code into a modular design and applying OOP principles, you've significantly improved the code structure and quality of your simulation tool. This foundation will make future development more efficient and your open-source project more accessible to contributors.

Feel free to ask if you have any questions or need further assistance with specific parts of the code!
