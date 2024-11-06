# Healthcare Logistics Simulation Tool
# Simulates patient flow and resource allocation in hospitals

import simpy
import random

RANDOM_SEED = 42
NUM_DOCTORS = 3         # Number of doctors in the hospital
NUM_NURSES = 5          # Number of nurses
NUM_BEDS = 10           # Number of beds
SIM_TIME = 480          # Simulation time in minutes (e.g., 8 hours)

class Hospital(object):
    def __init__(self, env, num_doctors, num_nurses, num_beds):
        self.env = env
        self.doctor = simpy.Resource(env, num_doctors)
        self.nurse = simpy.Resource(env, num_nurses)
        self.bed = simpy.Resource(env, num_beds)
        
    def triage(self, patient):
        """Triage process conducted by a nurse."""
        yield self.env.timeout(random.randint(5, 10))  # Triage takes 5-10 minutes

    def registration(self, patient):
        """Registration process conducted by a nurse."""
        yield self.env.timeout(random.randint(1, 5))  # Registration takes 1-5 minutes

    def treatment(self, patient):
        """Treatment process conducted by a doctor."""
        yield self.env.timeout(random.randint(15, 45))  # Treatment takes 15-45 minutes

def patient_process(env, patient, hospital):
    """Simulates the process flow of a single patient."""
    arrival_time = env.now
    print(f'Patient {patient} arrives at {env.now:.2f}')

    # Registration
    with hospital.nurse.request() as request:
        yield request
        print(f'Patient {patient} starts registration at {env.now:.2f}')
        yield env.process(hospital.registration(patient))
        print(f'Patient {patient} finishes registration at {env.now:.2f}')

    # Triage
    with hospital.nurse.request() as request:
        yield request
        print(f'Patient {patient} starts triage at {env.now:.2f}')
        yield env.process(hospital.triage(patient))
        print(f'Patient {patient} finishes triage at {env.now:.2f}')

    # Treatment
    with hospital.doctor.request() as request_doctor, hospital.bed.request() as request_bed:
        yield request_doctor & request_bed
        print(f'Patient {patient} starts treatment at {env.now:.2f}')
        yield env.process(hospital.treatment(patient))
        print(f'Patient {patient} finishes treatment at {env.now:.2f}')

def patient_arrivals(env, hospital):
    """Generates patients arriving at the hospital."""
    patient_num = 0
    while True:
        yield env.timeout(random.expovariate(1/10))  # On average, a new patient every 10 minutes
        patient_num += 1
        env.process(patient_process(env, patient_num, hospital))

def main():
    """Runs the simulation."""
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(env, NUM_DOCTORS, NUM_NURSES, NUM_BEDS)
    env.process(patient_arrivals(env, hospital))
    env.run(until=SIM_TIME)

if __name__ == '__main__':
    main()