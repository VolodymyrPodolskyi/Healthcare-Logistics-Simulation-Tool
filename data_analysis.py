# data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def analyze_data_streamlit(hospital):
    # Similar to analyze_data but using st.write and st.pyplot
    # Create DataFrame from patient data
    patient_data = []
    for patient in hospital.patients:
        data = {
            'patient_id': patient.patient_id,
            'patient_type': patient.patient_type,
            'severity_level': patient.severity_level,
            'arrival_time': patient.arrival_time,
            'total_time_in_system': patient.timestamps['discharge'] - patient.arrival_time
        }
        # Calculate wait times and service times
        for key in ['registration', 'triage', 'diagnostics', 'surgery', 'treatment', 'recovery']:
            wait_key = f'{key}_wait'
            start_key = f'{key}_start'
            end_key = f'{key}_end'
            data[f'{key}_wait_time'] = patient.timestamps.get(wait_key, 0)
            if start_key in patient.timestamps and end_key in patient.timestamps:
                data[f'{key}_service_time'] = patient.timestamps[end_key] - patient.timestamps[start_key]
            else:
                data[f'{key}_service_time'] = 0
        patient_data.append(data)
    
    df_patients = pd.DataFrame(patient_data)
    st.subheader('Performance Metrics')
    st.write("Average Total Time in System: {:.2f} minutes".format(df_patients['total_time_in_system'].mean()))
    
    # Display dataframes
    st.subheader('Patient Data')
    st.dataframe(df_patients)
    
    # Resource Utilization
    df_resources = pd.DataFrame(hospital.resource_log)
    st.subheader('Resource Utilization Over Time')
    st.line_chart(df_resources.set_index('time'))
    
    # Histogram of total time in system
    st.subheader('Distribution of Total Time in System')
    st.bar_chart(df_patients['total_time_in_system'])

    # You can add more interactive visualizations as needed