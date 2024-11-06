# processes.py

import random
from entities import Patient
import simpy


def patient_process(env: simpy.Environment, patient: Patient, hospital: 'Hospital'):
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

def patient_arrivals(env: simpy.Environment, hospital: 'Hospital', config: dict):
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