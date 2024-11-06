# Healthcare Logistics Simulation Tool
# Simulates patient flow and resource allocation in hospitals with realistic operations

import simpy
import random
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
        
        # Code blue status
        self.code_blue = False
        if self.patient_type == 'emergency' and random.random() < 0.1:
            self.code_blue = True

class StaffMember:
    """Class to represent a staff member with shifts and breaks."""
    def __init__(self, env, role, name):
        self.env = env
        self.role = role
        self.name = name
        self.is_available = True
        self.action = env.process(self.work())

    def work(self):
        while True:
            # Work shift
            shift_end = self.env.now + SHIFT_DURATION
            while self.env.now < shift_end:
                # Take a break at a random time during the shift
                break_time = self.env.now + random.randint(60, SHIFT_DURATION - 60)
                yield self.env.timeout(break_time - self.env.now)
                self.is_available = False
                print(f'{self.role} {self.name} is on break at {self.env.now:.2f}')
                yield self.env.timeout(BREAK_DURATION)
                self.is_available = True
                print(f'{self.role} {self.name} returns from break at {self.env.now:.2f}')
            # Shift over
            self.is_available = False
            print(f'{self.role} {self.name} ends shift at {self.env.now:.2f}')
            # Hand over to next shift (simulate handover time)
            yield self.env.timeout(5)
            self.is_available = True
            print(f'{self.role} {self.name} starts new shift at {self.env.now:.2f}')

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
        
        # Staff members
        self.doctors = [StaffMember(env, 'Doctor', f'Doctor_{i+1}') for i in range(NUM_DOCTORS)]
        self.nurses = [StaffMember(env, 'Nurse', f'Nurse_{i+1}') for i in range(NUM_NURSES)]
        self.specialists = [StaffMember(env, 'Specialist', f'Specialist_{i+1}') for i in range(NUM_SPECIALISTS)]
        self.admin_staff_members = [StaffMember(env, 'AdminStaff', f'Admin_{i+1}') for i in range(NUM_ADMIN_STAFF)]
        self.support_staff_members = [StaffMember(env, 'SupportStaff', f'Support_{i+1}') for i in range(NUM_SUPPORT_STAFF)]
        
        # Dynamic resource allocation
        self.env.process(self.monitor_patient_influx())

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
            patient = Patient(patient_id, 'emergency', severity_level)
            self.env.process(patient_process(self.env, patient, self))
        
        # Adjust resource allocation if needed
        # For example, call in extra staff (not implemented here for simplicity)
        
    def monitor_patient_influx(self):
        """Monitors patient influx and triggers disaster response if needed."""
        while True:
            # Check every 60 minutes
            yield self.env.timeout(60)
            # Random chance of disaster occurring
            if random.random() < 0.05:  # 5% chance every hour
                yield self.env.process(self.disaster_response())

def patient_process(env, patient, hospital):
    """Simulates the process flow of a single patient."""
    arrival_time = env.now
    print(f'Patient {patient.patient_id} ({patient.patient_type}, Severity {patient.severity_level}) arrives at {env.now:.2f}')
    print(f'Attributes: Age {patient.age}, Gender {patient.gender}, Medical History {patient.medical_history}')
    
    # Handle Code Blue scenarios immediately
    if patient.code_blue:
        with hospital.doctor.request(priority=0) as doctor_request:
            yield doctor_request
            yield env.process(hospital.code_blue_response(patient))
        return  # After Code Blue, patient is stabilized and leaves or moves to next step as per policy
    
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
    
    # Patient discharge
    print(f'Patient {patient.patient_id} is discharged at {env.now:.2f}')

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
