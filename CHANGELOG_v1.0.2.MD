1. Added New Constants

At the beginning of the code, we defined new constants for the additional resources:

NUM_SPECIALISTS = 2         # Number of specialists
NUM_ADMIN_STAFF = 3         # Number of administrative staff
NUM_SUPPORT_STAFF = 4       # Number of support personnel

NUM_OPERATING_ROOMS = 1     # Number of operating rooms
NUM_LABS = 2                # Number of labs
NUM_IMAGING_CENTERS = 1     # Number of imaging centers

NUM_MEDICAL_EQUIPMENT = 5   # Number of medical equipment units

2. Updated the Hospital Class

We expanded the Hospital class to include new staff, facilities, and equipment resources:

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

3. Expanded the Patient Class

We added attributes to determine if a patient needs surgery or diagnostics:

class Patient:
    def __init__(self, patient_id, patient_type, severity_level):
        # Existing attributes...
        # Determine if the patient needs surgery or diagnostics
        self.needs_surgery = False
        self.needs_diagnostics = False
        if self.patient_type == 'emergency' and self.severity_level >= 4:
            self.needs_surgery = True
        elif self.severity_level >= 3:
            self.needs_diagnostics = True

4. Introduced New Processes in the Hospital Class

We added diagnostics and surgery methods to simulate these processes:

def diagnostics(self, patient):
    """Diagnostics process conducted in lab or imaging center."""
    diagnostics_time = random.randint(10, 30)
    yield self.env.timeout(diagnostics_time)

def surgery(self, patient):
    """Surgery process conducted by a specialist in operating room."""
    surgery_time = random.randint(30, 90)
    yield self.env.timeout(surgery_time)

5. Updated Patient Process Flow

In the patient_process function, we included the new processes and updated resource requests:

    Registration: Now involves both administrative staff and nurse.

with hospital.admin_staff.request(priority=patient.severity_level) as admin_request, \
     hospital.nurse.request(priority=patient.severity_level) as nurse_request:
    yield admin_request & nurse_request
    # Registration process...

Diagnostics: If needed, the patient undergoes diagnostics in either a lab or imaging center.

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
        # Diagnostics process...

Surgery: If needed, the patient undergoes surgery conducted by a specialist in an operating room.

if patient.needs_surgery:
    with hospital.specialist.request(priority=patient.severity_level) as specialist_request, \
         hospital.operating_room.request(priority=patient.severity_level) as or_request, \
         hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
        yield specialist_request & or_request & equipment_request
        # Surgery process...
    # Recovery after surgery
    with hospital.bed.request(priority=patient.severity_level) as bed_request:
        yield bed_request
        # Recovery process...

Treatment: Patients who do not undergo surgery proceed to treatment as before, but now also request medical equipment.

    else:
        # Treatment (if no surgery)
        with hospital.doctor.request(priority=patient.severity_level) as doctor_request, \
             hospital.bed.request(priority=patient.severity_level) as bed_request, \
             hospital.medical_equipment.request(priority=patient.severity_level) as equipment_request:
            yield doctor_request & bed_request & equipment_request
            # Treatment process...

6. Adjusted Resource Requests and Prioritization

All resource requests now include priorities based on patient severity levels. Higher severity patients are given higher priority for resource allocation.
7. Included Medical Equipment in Processes

Medical equipment is now a required resource for diagnostics, surgery, and treatment processes. This simulates the allocation and availability of medical equipment.
Sample Output

When you run the updated simulation, you might see output similar to the following:


Patient 1 (walk-in, Severity 1) arrives at 5.04
Attributes: Age 82, Gender Female, Medical History None
Patient 1 starts registration at 5.04
Patient 1 finishes registration at 8.04
Patient 1 starts triage at 8.04
Patient 1 finishes triage at 13.04
Patient 1 starts treatment at 13.04
Patient 1 finishes treatment at 27.04
Patient 2 (scheduled, Severity 2) arrives at 8.53
Attributes: Age 15, Gender Female, Medical History None
Patient 2 starts registration at 13.04
Patient 2 finishes registration at 17.04
Patient 2 starts triage at 17.04
Patient 2 finishes triage at 22.04
Patient 2 starts diagnostics in lab at 22.04
Patient 2 finishes diagnostics at 47.04
Patient 2 starts treatment at 47.04
Patient 2 finishes treatment at 62.04
...


    Resource Contention: The inclusion of additional resources like operating rooms and equipment introduces more complexity in resource management and potential bottlenecks.
    Priority Handling: The use of PriorityResource ensures that higher severity patients are prioritized for critical resources.
    Process Flow Variability: Patients now have different process flows based on their needs, which adds realism to the simulation.
