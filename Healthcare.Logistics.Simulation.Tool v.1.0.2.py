# Healthcare Logistics Simulation Tool
# Simulates patient flow and resource allocation in hospitals with expanded resources

import simpy
import random
from simpy.resources.resource import PriorityResource

RANDOM_SEED = 42

# Hospital resource quantities
NUM_DOCTORS = 3             # Number of doctors
NUM_NURSES = 5              # Number of nurses
NUM_BEDS = 10               # Number of beds

NUM_SPECIALISTS = 2         # Number of specialists
NUM_ADMIN_STAFF = 3         # Number of administrative staff
NUM_SUPPORT_STAFF = 4       # Number of support personnel

NUM_OPERATING_ROOMS = 1     # Number of operating rooms
NUM_LABS = 2                # Number of labs
NUM_IMAGING_CENTERS = 1     # Number of imaging centers

NUM_MEDICAL_EQUIPMENT = 5   # Number of medical equipment units

SIM_TIME = 480              # Simulation time in minutes (e.g., 8 hours)

class Patient:
    """Class to represent a patient with various attributes."""
    def __init__(self, patient_id, patient_type, severity_level):
        self.patient_id = patient_id
        self.patient_type = patient_type  # 'emergency', 'scheduled', 'walk-in'
        self.severity_level = severity_level  # 1 (low) to 5 (high)
        self.age = random.randint(1, 100)
        self.gender = random.choice(['Male', 'Female'])
        self.medical_history = random.choice(['None', 'Chronic Illness', 'Previous Surgery'])
        
        # Determine if the patient needs surgery or diagnostics
        self.needs_surgery = False
        self.needs_diagnostics = False
        if self.patient_type == 'emergency' and self.severity_level >= 4:
            self.needs_surgery = True
        elif self.severity_level >= 3:
            self.needs_diagnostics = True

class Hospital(object):
    def __init__(self, env):
        self.env = env
        # Staff resources
        self.doctor = PriorityResource(env, NUM_DOCTORS)
        self.nurse = PriorityResource(env, NUM_NURSES)
        self.bed = PriorityResource(env, NUM_BEDS)
        self.specialist = PriorityResource(env, NUM_SPECIALISTS)
        self.admin_staff = PriorityResource(env, NUM_ADMIN_STAFF)
        self.support_staff = PriorityResource(env, NUM_SUPPORT_STAFF)
        
        # Facility resources
        self.operating_room = PriorityResource(env, NUM_OPERATING_ROOMS)
        self.lab = PriorityResource(env, NUM_LABS)
        self.imaging_center = PriorityResource(env, NUM_IMAGING_CENTERS)
        
        # Equipment resources
        self.medical_equipment = PriorityResource(env, NUM_MEDICAL_EQUIPMENT)
        
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
        with hospital.admin_staff.request(priority=patient.severity_level) as admin_request, \
             hospital.nurse.request(priority=patient.severity_level) as nurse_request:
            yield admin_request & nurse_request
            print(f'Patient {patient.patient_id} starts registration at {env.now:.2f}')
            yield env.process(hospital.registration(patient))
            print(f'Patient {patient.patient_id} finishes registration at {env.now:.2f}')
    
    # Triage
    with hospital.nurse.request(priority=patient.severity_level) as nurse_request:
        yield nurse_request
        print(f'Patient {patient.patient_id} starts triage at {env.now:.2f}')
        yield env.process(hospital.triage(patient))
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
            yield support_request & equipment_request & facility_request
            print(f'Patient {patient.patient_id} starts diagnostics in {facility_name} at {env.now:.2f}')
            yield env.process(hospital.diagnostics(patient))
            print(f'Patient {patient.patient_id} finishes diagnostics at {env.now:.2f}')
    
    # Surgery if needed
    if patient.needs_surgery:
        with hospital.specialist.request(priority=patient.severity_level) as specialist_request, \
             hospital.operating_room.request(priority=patient.severity_level) as or_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
            yield specialist_request & or_request & equipment_request
            print(f'Patient {patient.patient_id} starts surgery at {env.now:.2f}')
            yield env.process(hospital.surgery(patient))
            print(f'Patient {patient.patient_id} finishes surgery at {env.now:.2f}')
        # Recovery after surgery
        with hospital.bed.request(priority=patient.severity_level) as bed_request:
            yield bed_request
            print(f'Patient {patient.patient_id} is recovering after surgery at {env.now:.2f}')
            recovery_time = random.randint(30, 60)
            yield env.timeout(recovery_time)
            print(f'Patient {patient.patient_id} finishes recovery at {env.now:.2f}')
    else:
        # Treatment (if no surgery)
        with hospital.doctor.request(priority=patient.severity_level) as doctor_request, \
             hospital.bed.request(priority=patient.severity_level) as bed_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
            yield doctor_request & bed_request & equipment_request
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
    hospital = Hospital(env)
    env.process(patient_arrivals(env, hospital))
    env.run(until=SIM_TIME)

if __name__ == '__main__':
    main()
