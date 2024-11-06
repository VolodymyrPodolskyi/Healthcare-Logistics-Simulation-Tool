# data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt

def analyze_data(hospital):
    """Analyzes collected data and generates reports."""
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
    
    # Calculate KPIs
    print("\nPerformance Metrics:")
    print("Average Total Time in System: {:.2f} minutes".format(df_patients['total_time_in_system'].mean()))
    print("Average Waiting Times:")
    wait_time_cols = [col for col in df_patients.columns if 'wait_time' in col]
    for col in wait_time_cols:
        avg_wait = df_patients[col].mean()
        print(f"  {col.replace('_wait_time', '').title()}: {avg_wait:.2f} minutes")
    print("Average Service Times:")
    service_time_cols = [col for col in df_patients.columns if 'service_time' in col]
    for col in service_time_cols:
        avg_service = df_patients[col].mean()
        print(f"  {col.replace('_service_time', '').title()}: {avg_service:.2f} minutes")
    
    # Resource Utilization
    df_resources = pd.DataFrame(hospital.resource_log)
    avg_utilization = df_resources.mean()
    print("\nAverage Resource Utilization:")
    for resource in ['doctor', 'nurse', 'bed', 'specialist', 'operating_room', 'lab', 'imaging_center', 'medical_equipment']:
        utilization = avg_utilization[f'{resource}_utilization'] * 100
        print(f"  {resource.title().replace('_', ' ')}: {utilization:.2f}%")
    
    # Bottleneck Identification
    print("\nBottleneck Analysis:")
    max_wait_time_cols = df_patients[wait_time_cols].max()
    for col in wait_time_cols:
        max_wait = max_wait_time_cols[col]
        print(f"  Maximum {col.replace('_wait_time', '').title()} Wait Time: {max_wait:.2f} minutes")
    
    # Visualizations
    # Plot resource utilization over time
    plt.figure(figsize=(10, 6))
    for resource in ['doctor', 'nurse', 'bed']:
        plt.plot(df_resources['time'], df_resources[f'{resource}_utilization'], label=f'{resource.title()}')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Utilization')
    plt.title('Resource Utilization Over Time')
    plt.legend()
    plt.show()
    
    # Histogram of total time in system
    plt.figure(figsize=(8, 5))
    plt.hist(df_patients['total_time_in_system'], bins=20, edgecolor='black')
    plt.xlabel('Total Time in System (minutes)')
    plt.ylabel('Number of Patients')
    plt.title('Distribution of Total Time in System')
    plt.show()