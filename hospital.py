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
        yield self.env.timeout(0)

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