1. Shift Scheduling

StaffMember Class

Introduced a StaffMember class to simulate staff shifts, breaks, and handovers:

python

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

    Shift Duration: Defined by SHIFT_DURATION (e.g., 4 hours).
    Breaks: Each staff member takes a break during the shift, randomly scheduled.
    Handovers: Simulated by a short delay (5 minutes) at the end of each shift.

Staff Initialization in Hospital Class

Created instances of StaffMember for each staff role:

python

self.doctors = [StaffMember(env, 'Doctor', f'Doctor_{i+1}') for i in range(NUM_DOCTORS)]
self.nurses = [StaffMember(env, 'Nurse', f'Nurse_{i+1}') for i in range(NUM_NURSES)]
self.specialists = [StaffMember(env, 'Specialist', f'Specialist_{i+1}') for i in range(NUM_SPECIALISTS)]
self.admin_staff_members = [StaffMember(env, 'AdminStaff', f'Admin_{i+1}') for i in range(NUM_ADMIN_STAFF)]
self.support_staff_members = [StaffMember(env, 'SupportStaff', f'Support_{i+1}') for i in range(NUM_SUPPORT_STAFF)]

Note: For simplicity, we haven't linked individual StaffMember availability to resource availability. In a more detailed model, you could adjust resource capacities based on the number of available staff.
2. Emergency Protocols

Code Blue Scenarios

In the Patient class, we added a code_blue attribute:

python

# Code blue status
self.code_blue = False
if self.patient_type == 'emergency' and random.random() < 0.1:
    self.code_blue = True

    Triggering Code Blue: A 10% chance that an emergency patient will require immediate attention.

Handling Code Blue in Patient Process

python

if patient.code_blue:
    with hospital.doctor.request(priority=0) as doctor_request:
        yield doctor_request
        yield env.process(hospital.code_blue_response(patient))
    return  # After Code Blue, patient is stabilized and leaves or moves to next step as per policy

    Priority Handling: Patients with code_blue status are given the highest priority (priority=0).
    Immediate Response: The code_blue_response method simulates the emergency intervention.

Code Blue Response Method

python

def code_blue_response(self, patient):
    """Handles code blue emergency situations."""
    print(f'Code Blue! Patient {patient.patient_id} requires immediate attention at {self.env.now:.2f}')
    response_time = random.randint(5, 15)
    yield self.env.timeout(response_time)
    print(f'Patient {patient.patient_id} stabilized after Code Blue at {self.env.now:.2f}')

Disaster Response

Added a method to simulate a disaster scenario:

python

def disaster_response(self):
    """Simulates a disaster scenario with sudden influx of patients."""
    print(f'Disaster occurred at {self.env.now:.2f}! Sudden influx of patients.')
    num_additional_patients = random.randint(5, 15)
    for _ in range(num_additional_patients):
        patient_id = 'D' + str(random.randint(1000, 9999))
        severity_level = random.randint(3, 5)
        patient = Patient(patient_id, 'emergency', severity_level)
        self.env.process(patient_process(self.env, patient, self))

Monitoring for Disasters

python

def monitor_patient_influx(self):
    """Monitors patient influx and triggers disaster response if needed."""
    while True:
        # Check every 60 minutes
        yield self.env.timeout(60)
        # Random chance of disaster occurring
        if random.random() < 0.05:  # 5% chance every hour
            yield self.env.process(self.disaster_response())

3. Dynamic Resource Allocation

    Dynamic Adjustment: The disaster_response method introduces a sudden influx of patients, simulating a scenario where resource demand increases sharply.
    System Adaptation: In a full implementation, the hospital could adjust resource capacities or call in additional staff. For simplicity, this code does not dynamically change resource capacities, but it sets the stage for such enhancements.

4. Minor Adjustments

    Patient Discharge: At the end of patient_process, we added a discharge message.

    python

print(f'Patient {patient.patient_id} is discharged at {env.now:.2f}')

Resource Requests: All resource requests maintain priorities based on patient severity.

Simulation Time: Kept at 480 minutes (8 hours) to observe shifts and potential disasters.
