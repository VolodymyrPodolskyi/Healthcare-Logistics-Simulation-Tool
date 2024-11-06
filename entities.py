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