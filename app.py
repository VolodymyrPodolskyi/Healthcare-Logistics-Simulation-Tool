# app.py

import streamlit as st
import simpy
import random
from hospital import Hospital
from processes import patient_arrivals
from data_analysis import analyze_data

def run_simulation(config):
    random.seed(config['RANDOM_SEED'])
    env = simpy.Environment()
    hospital = Hospital(env, config)
    env.process(patient_arrivals(env, hospital, config))
    env.run(until=config['SIM_TIME'])
    return hospital

def main():
    st.title('Healthcare Logistics Simulation Tool')

    st.sidebar.header('Simulation Parameters')
    NUM_DOCTORS = st.sidebar.number_input('Number of Doctors', min_value=1, value=3)
    NUM_NURSES = st.sidebar.number_input('Number of Nurses', min_value=1, value=5)
    NUM_BEDS = st.sidebar.number_input('Number of Beds', min_value=1, value=10)
    SIM_TIME = st.sidebar.number_input('Simulation Time (minutes)', min_value=1, value=480)
    RANDOM_SEED = st.sidebar.number_input('Random Seed', min_value=1, value=42)
    SHIFT_DURATION = st.sidebar.number_input('Shift Duration (minutes)', min_value=1, value=240)
    BREAK_DURATION = st.sidebar.number_input('Break Duration (minutes)', min_value=1, value=15)
    # Add more parameters as needed

    if st.button('Run Simulation'):
        config = {
            'NUM_DOCTORS': NUM_DOCTORS,
            'NUM_NURSES': NUM_NURSES,
            'NUM_BEDS': NUM_BEDS,
            'NUM_SPECIALISTS': 2,  # You can add inputs for these as well
            'NUM_ADMIN_STAFF': 3,
            'NUM_SUPPORT_STAFF': 4,
            'NUM_OPERATING_ROOMS': 1,
            'NUM_LABS': 2,
            'NUM_IMAGING_CENTERS': 1,
            'NUM_MEDICAL_EQUIPMENT': 5,
            'SHIFT_DURATION': SHIFT_DURATION,
            'BREAK_DURATION': BREAK_DURATION,
            'SIM_TIME': SIM_TIME,
            'RANDOM_SEED': RANDOM_SEED,
        }

        st.write('Running simulation...')
        hospital = run_simulation(config)
        st.write('Simulation completed.')

        # Data Analysis
        from data_analysis import analyze_data_streamlit
        analyze_data_streamlit(hospital)

if __name__ == '__main__':
    main()