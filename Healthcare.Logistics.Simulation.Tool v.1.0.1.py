# Healthcare Logistics Simulation Tool
# Simulates patient flow and resource allocation in hospitals with patient complexity

import simpy
import random

RANDOM_SEED = 42
NUM_DOCTORS = 3         # Number of doctors in the hospital
NUM_NURSES = 5          # Number of nurses
NUM_BEDS = 10           # Number of beds
SIM_TIME = 480          # Simulation time in minutes (e.g., 8 hours)

class Patient:
    """Class to represent a patient with various attributes."""
    def __init__(self, patient_id, patient_type, severity_level):
        self.patient_id = patient_id
        self.patient_type = patient_type  # 'emergency', 'scheduled', 'walk-in'
        self.severity_level = severity_level  # 1 (low) to 5 (high)
        self.age = random.randint(1, 100)
        self.gender = random.choice(['Male', 'Female'])
        self.medical_history = random.choice(['None', 'Chronic Illness', 'Previous Surgery'])

class Hospital(object):
    def __init__(self, env, num_doctors, num_nurses, num_beds):
        self.env = env
        self.doctor = simpy.Resource(env, num_doctors)
        self.nurse = simpy.Resource(env, num_nurses)
        self.bed = simpy.Resource(env, num_beds)
        
    def triage(self, patient):
        """Triage process conducted by a nurse."""
        triage_time = random.randint(5, 10)  # Base triage time
        yield self.env.timeout(triage_time)
    
    def registration(self, patient):
        """Registration process conducted by a nurse."""
        registration_time = random.randint(1, 5)
        yield self.env.timeout(registration_time)
    
    def treatment(self, patient):
        """Treatment process conducted by a doctor."""
        # Treatment time varies based on severity level
        base_treatment_time = random.randint(15, 45)
        severity_factor = (6 - patient.severity_level)  # Higher severity, longer treatment
        treatment_time = base_treatment_time * severity_factor / 5
        yield self.env.timeout(treatment_time)

def patient_process(env, patient, hospital):
    """Simulates the process flow of a single patient."""
    arrival_time = env.now
    print(f'Patient {patient.patient_id} ({patient.patient_type}, Severity {patient.severity_level}) arrives at {env.now:.2f}')
    print(f'Attributes: Age {patient.age}, Gender {patient.gender}, Medical History {patient.medical_history}')

    # Registration (skip for emergency patients)
    if patient.patient_type != 'emergency':
        with hospital.nurse.request(priority=patient.severity_level) as request:
            yield request
            print(f'Patient {patient.patient_id} starts registration at {env.now:.2f}')
            yield env.process(hospital.registration(patient))
            print(f'Patient {patient.patient_id} finishes registration at {env.now:.2f}')
    
    # Triage
    with hospital.nurse.request(priority=patient.severity_level) as request:
        yield request
        print(f'Patient {patient.patient_id} starts triage at {env.now:.2f}')
        yield env.process(hospital.triage(patient))
        print(f'Patient {patient.patient_id} finishes triage at {env.now:.2f}')
    
    # Treatment
    with hospital.doctor.request(priority=patient.severity_level) as request_doctor, \
         hospital.bed.request(priority=patient.severity_level) as request_bed:
        yield request_doctor & request_bed
        print(f'Patient {patient.patient_id} starts treatment at {env.now:.2f}')
        yield env.process(hospital.treatment(patient))
        print(f'Patient {patient.patient_id} finishes treatment at {env.now:.2f}')

def patient_arrivals(env, hospital):
    """Generates patients arriving at the hospital."""
    patient_num = 0
    while True:
        # Determine patient type and arrival time based on type
        patient_type = random.choices(
            ['emergency', 'scheduled', 'walk-in'],
            weights=[1, 2, 7],  # Adjust weights as needed
            k=1
        )[0]
        
        if patient_type == 'emergency':
            inter_arrival_time = random.expovariate(1/30)  # On average, an emergency every 30 minutes
            severity_level = random.randint(4, 5)  # Higher severity
        elif patient_type == 'scheduled':
            inter_arrival_time = random.expovariate(1/15)  # On average, a scheduled patient every 15 minutes
            severity_level = random.randint(2, 3)
        else:  # walk-in
            inter_arrival_time = random.expovariate(1/10)  # On average, a walk-in every 10 minutes
            severity_level = random.randint(1, 4)
        
        yield env.timeout(inter_arrival_time)
        patient_num += 1
        patient = Patient(patient_num, patient_type, severity_level)
        env.process(patient_process(env, patient, hospital))

def main():
    """Runs the simulation."""
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(env, NUM_DOCTORS, NUM_NURSES, NUM_BEDS)
    env.process(patient_arrivals(env, hospital))
    env.run(until=SIM_TIME)

if __name__ == '__main__':
    main()
