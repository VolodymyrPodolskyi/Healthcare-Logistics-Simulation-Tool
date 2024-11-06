# main.py

import simpy
import random
from hospital import Hospital
from processes import patient_arrivals
from data_analysis import analyze_data

def main():
    """Runs the simulation and performs data analysis."""
    # Simulation configuration
    RANDOM_SEED = 42
    SIM_TIME = 480  # Simulation time in minutes (e.g., 8 hours)
    
    # Hospital resource quantities
    config = {
        'NUM_DOCTORS': 3,
        'NUM_NURSES': 5,
        'NUM_BEDS': 10,
        'NUM_SPECIALISTS': 2,
        'NUM_ADMIN_STAFF': 3,
        'NUM_SUPPORT_STAFF': 4,
        'NUM_OPERATING_ROOMS': 1,
        'NUM_LABS': 2,
        'NUM_IMAGING_CENTERS': 1,
        'NUM_MEDICAL_EQUIPMENT': 5,
        'SHIFT_DURATION': 240,  # 4 hours
        'BREAK_DURATION': 15,   # 15 minutes
    }
    
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(env, config)
    env.process(patient_arrivals(env, hospital, config))
    env.run(until=SIM_TIME)
    
    # Data Analysis
    analyze_data(hospital)

if __name__ == '__main__':
    main()