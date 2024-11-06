# Healthcare Logistics Simulation Tool with Data Collection and Analysis
# Simulates patient flow and resource allocation in hospitals, tracking performance metrics

import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
from simpy.resources.resource import PriorityResource

RANDOM_SEED = 42

# Hospital resource quantities
NUM_DOCTORS = 3             # Number of doctors per shift
NUM_NURSES = 5              # Number of nurses per shift
NUM_BEDS = 10               # Number of beds

NUM_SPECIALISTS = 2         # Number of specialists per shift
NUM_ADMIN_STAFF = 3         # Number of administrative staff per shift
NUM_SUPPORT_STAFF = 4       # Number of support personnel per shift

NUM_OPERATING_ROOMS = 1     # Number of operating rooms
NUM_LABS = 2                # Number of labs
NUM_IMAGING_CENTERS = 1     # Number of imaging centers

NUM_MEDICAL_EQUIPMENT = 5   # Number of medical equipment units

SIM_TIME = 480              # Simulation time in minutes (e.g., 8 hours)

SHIFT_DURATION = 240        # Shift duration in minutes (e.g., 4 hours)
BREAK_DURATION = 15         # Break duration in minutes

class Patient:
    """Class to represent a patient with various attributes."""
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

class Hospital(object):
    def __init__(self, env):
        self.env = env
        # Staff resources
        self.doctor = PriorityResource(env, capacity=NUM_DOCTORS)
        self.nurse = PriorityResource(env, capacity=NUM_NURSES)
        self.specialist = PriorityResource(env, capacity=NUM_SPECIALISTS)
        self.admin_staff = PriorityResource(env, capacity=NUM_ADMIN_STAFF)
        self.support_staff = PriorityResource(env, capacity=NUM_SUPPORT_STAFF)
        
        # Facility resources
        self.bed = PriorityResource(env, capacity=NUM_BEDS)
        self.operating_room = PriorityResource(env, capacity=NUM_OPERATING_ROOMS)
        self.lab = PriorityResource(env, capacity=NUM_LABS)
        self.imaging_center = PriorityResource(env, capacity=NUM_IMAGING_CENTERS)
        
        # Equipment resources
        self.medical_equipment = PriorityResource(env, capacity=NUM_MEDICAL_EQUIPMENT)
        
        # Data collection
        self.patients = []  # List to store all patient objects for analysis
        self.resource_log = []  # Log for resource utilization

    # ... (Other methods remain the same)
    
    def collect_resource_utilization(self):
        """Collects data on resource utilization at each time step."""
        while True:
            # Record the utilization of each resource
            self.resource_log.append({
                'time': self.env.now,
                'doctor_utilization': self.doctor.count / NUM_DOCTORS,
                'nurse_utilization': self.nurse.count / NUM_NURSES,
                'bed_utilization': self.bed.count / NUM_BEDS,
                'specialist_utilization': self.specialist.count / NUM_SPECIALISTS,
                'operating_room_utilization': self.operating_room.count / NUM_OPERATING_ROOMS,
                'lab_utilization': self.lab.count / NUM_LABS,
                'imaging_center_utilization': self.imaging_center.count / NUM_IMAGING_CENTERS,
                'medical_equipment_utilization': self.medical_equipment.count / NUM_MEDICAL_EQUIPMENT
            })
            yield self.env.timeout(1)  # Collect data every 1 minute

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
            print(f'Patient {patient.patient_id} starts registration at {env.now:.2f}')
            yield env.process(hospital.registration(patient))
            patient.timestamps['registration_end'] = env.now
            print(f'Patient {patient.patient_id} finishes registration at {env.now:.2f}')
    
    # Triage
    with hospital.nurse.request(priority=patient.severity_level) as nurse_request:
        triage_start = env.now
        yield nurse_request
        wait_time = env.now - triage_start
        patient.timestamps['triage_wait'] = wait_time
        patient.timestamps['triage_start'] = env.now
        print(f'Patient {patient.patient_id} starts triage at {env.now:.2f}')
        yield env.process(hospital.triage(patient))
        patient.timestamps['triage_end'] = env.now
        print(f'Patient {patient.patient_id} finishes triage at {env.now:.2f}')
    
    # Diagnostics if needed
    if patient.needs_diagnostics:
        # Decide randomly between lab and imaging center
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
            print(f'Patient {patient.patient_id} starts diagnostics in {facility_name} at {env.now:.2f}')
            yield env.process(hospital.diagnostics(patient))
            patient.timestamps['diagnostics_end'] = env.now
            print(f'Patient {patient.patient_id} finishes diagnostics at {env.now:.2f}')
    
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
            print(f'Patient {patient.patient_id} starts surgery at {env.now:.2f}')
            yield env.process(hospital.surgery(patient))
            patient.timestamps['surgery_end'] = env.now
            print(f'Patient {patient.patient_id} finishes surgery at {env.now:.2f}')
        # Recovery after surgery
        with hospital.bed.request(priority=patient.severity_level) as bed_request:
            recov_start = env.now
            yield bed_request
            wait_time = env.now - recov_start
            patient.timestamps['recovery_wait'] = wait_time
            patient.timestamps['recovery_start'] = env.now
            print(f'Patient {patient.patient_id} is recovering after surgery at {env.now:.2f}')
            recovery_time = random.randint(30, 60)
            yield env.timeout(recovery_time)
            patient.timestamps['recovery_end'] = env.now
            print(f'Patient {patient.patient_id} finishes recovery at {env.now:.2f}')
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
            print(f'Patient {patient.patient_id} starts treatment at {env.now:.2f}')
            yield env.process(hospital.treatment(patient))
            patient.timestamps['treatment_end'] = env.now
            print(f'Patient {patient.patient_id} finishes treatment at {env.now:.2f}')
    
    # Patient discharge
    patient.timestamps['discharge'] = env.now
    hospital.patients.append(patient)
    print(f'Patient {patient.patient_id} is discharged at {env.now:.2f}')

def patient_arrivals(env, hospital):
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

def main():
    """Runs the simulation and performs data analysis."""
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(env)
    env.process(patient_arrivals(env, hospital))
    env.process(hospital.collect_resource_utilization())
    env.run(until=SIM_TIME)
    
    # Data Analysis
    analyze_data(hospital)

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
    
    # You can add more plots and analyses as needed

if __name__ == '__main__':
    main()
