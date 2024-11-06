# main.py

import simpy
import random
import argparse
from hospital import Hospital
from processes import patient_arrivals
from data_analysis import analyze_data

def main():
    """Runs the simulation and performs data analysis."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Healthcare Logistics Simulation Tool')
    parser.add_argument('--doctors', type=int, default=3, help='Number of doctors')
    parser.add_argument('--nurses', type=int, default=5, help='Number of nurses')
    parser.add_argument('--beds', type=int, default=10, help='Number of beds')
    parser.add_argument('--specialists', type=int, default=2, help='Number of specialists')
    parser.add_argument('--admin_staff', type=int, default=3, help='Number of administrative staff')
    parser.add_argument('--support_staff', type=int, default=4, help='Number of support personnel')
    parser.add_argument('--operating_rooms', type=int, default=1, help='Number of operating rooms')
    parser.add_argument('--labs', type=int, default=2, help='Number of labs')
    parser.add_argument('--imaging_centers', type=int, default=1, help='Number of imaging centers')
    parser.add_argument('--medical_equipment', type=int, default=5, help='Number of medical equipment units')
    parser.add_argument('--sim_time', type=int, default=480, help='Simulation time in minutes')
    parser.add_argument('--random_seed', type=int, default=42, help='Random seed for reproducibility')
    parser.add_argument('--shift_duration', type=int, default=240, help='Shift duration in minutes')
    parser.add_argument('--break_duration', type=int, default=15, help='Break duration in minutes')
    args = parser.parse_args()

    # Simulation configuration
    config = {
        'NUM_DOCTORS': args.doctors,
        'NUM_NURSES': args.nurses,
        'NUM_BEDS': args.beds,
        'NUM_SPECIALISTS': args.specialists,
        'NUM_ADMIN_STAFF': args.admin_staff,
        'NUM_SUPPORT_STAFF': args.support_staff,
        'NUM_OPERATING_ROOMS': args.operating_rooms,
        'NUM_LABS': args.labs,
        'NUM_IMAGING_CENTERS': args.imaging_centers,
        'NUM_MEDICAL_EQUIPMENT': args.medical_equipment,
        'SHIFT_DURATION': args.shift_duration,
        'BREAK_DURATION': args.break_duration,
    }

    random.seed(args.random_seed)
    env = simpy.Environment()
    hospital = Hospital(env, config)
    env.process(patient_arrivals(env, hospital, config))
    env.run(until=args.sim_time)

    # Data Analysis
    analyze_data(hospital)

if __name__ == '__main__':
    main()