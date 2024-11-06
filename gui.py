# gui.py

import tkinter as tk
from tkinter import ttk
import simpy
import random
import pandas as pd  # Import Pandas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading  # For running the simulation in a separate thread
from hospital import Hospital
from processes import patient_arrivals
from data_analysis import analyze_data

def run_simulation(config):
    def simulation_thread():
        global hospital  # Declare hospital as global
        random.seed(config['RANDOM_SEED'])
        env = simpy.Environment()
        hospital = Hospital(env, config, update_gui_callback=update_plots)
        env.process(patient_arrivals(env, hospital, config))
        env.run(until=config['SIM_TIME'])
        output_text.insert(tk.END, 'Simulation completed.\n')
        # After simulation, perform post-simulation analysis
        analyze_data_tkinter(hospital)
    threading.Thread(target=simulation_thread).start()

def start_simulation():
    config = {
        'NUM_DOCTORS': int(doctors_entry.get()),
        'NUM_NURSES': int(nurses_entry.get()),
        'NUM_BEDS': int(beds_entry.get()),
        'NUM_SPECIALISTS': 2,
        'NUM_ADMIN_STAFF': 3,
        'NUM_SUPPORT_STAFF': 4,
        'NUM_OPERATING_ROOMS': 1,
        'NUM_LABS': 2,
        'NUM_IMAGING_CENTERS': 1,
        'NUM_MEDICAL_EQUIPMENT': 5,
        'SHIFT_DURATION': 240,
        'BREAK_DURATION': 15,
        'SIM_TIME': int(sim_time_entry.get()),
        'RANDOM_SEED': int(random_seed_entry.get()),
    }
    output_text.insert(tk.END, 'Running simulation...\n')
    run_simulation(config)
    # Data Analysis
    analyze_data_tkinter(hospital)

def analyze_data_tkinter(hospital):
    # Similar to analyze_data but output results to the Tkinter text widget
    patient_data = []
    for patient in hospital.patients:
        data = {
            'patient_id': patient.patient_id,
            'patient_type': patient.patient_type,
            'severity_level': patient.severity_level,
            'arrival_time': patient.arrival_time,
            'total_time_in_system': patient.timestamps['discharge'] - patient.arrival_time
        }
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
    output_text.insert(tk.END, "\nPerformance Metrics:\n")
    output_text.insert(tk.END, "Average Total Time in System: {:.2f} minutes\n".format(df_patients['total_time_in_system'].mean()))
def update_plots():
    # Clear the axes
    ax.clear()
    # Extract data
    times = [entry['time'] for entry in hospital.resource_log]
    doctor_utilization = [entry['doctor_utilization'] for entry in hospital.resource_log]
    nurse_utilization = [entry['nurse_utilization'] for entry in hospital.resource_log]
    bed_utilization = [entry['bed_utilization'] for entry in hospital.resource_log]
    # Plot data
    ax.plot(times, doctor_utilization, label='Doctors')
    ax.plot(times, nurse_utilization, label='Nurses')
    ax.plot(times, bed_utilization, label='Beds')
    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Utilization')
    ax.set_title('Resource Utilization Over Time')
    ax.legend()
    ax.set_ylim(0, 1)  # Utilization ranges from 0 to 1
    # Refresh canvas
    canvas.draw()
def analyze_data_tkinter(hospital):
    # Similar to analyze_data but output results to the Tkinter text widget
    patient_data = []
    for patient in hospital.patients:
        data = {
            'patient_id': patient.patient_id,
            'patient_type': patient.patient_type,
            'severity_level': patient.severity_level,
            'arrival_time': patient.arrival_time,
            'total_time_in_system': patient.timestamps['discharge'] - patient.arrival_time
        }
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
    
    # Display performance metrics in the output text area
    avg_total_time = df_patients['total_time_in_system'].mean()
    output_text.insert(tk.END, f"\nAverage Total Time in System: {avg_total_time:.2f} minutes\n")
    
    # Generate a histogram of total time in system
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.hist(df_patients['total_time_in_system'], bins=20, edgecolor='black')
    ax2.set_xlabel('Total Time in System (minutes)')
    ax2.set_ylabel('Number of Patients')
    ax2.set_title('Distribution of Total Time in System')
    canvas2 = FigureCanvasTkAgg(fig2, master=root)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=8, column=0, columnspan=2)
    
    # Generate a heatmap of resource utilization
    import seaborn as sns
    sns.set()
    df_resources = pd.DataFrame(hospital.resource_log)
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    sns.heatmap(df_resources.drop('time', axis=1).T, ax=ax3)
    ax3.set_title('Resource Utilization Heatmap')
    canvas3 = FigureCanvasTkAgg(fig3, master=root)
    canvas3.draw()
    canvas3.get_tk_widget().grid(row=9, column=0, columnspan=2)
    # You can add more outputs or open new windows with detailed results

# Create the main window
root = tk.Tk()
root.title("Healthcare Logistics Simulation Tool")

# Create input fields
tk.Label(root, text="Number of Doctors:").grid(row=0, column=0)
doctors_entry = tk.Entry(root)
doctors_entry.insert(0, "3")
doctors_entry.grid(row=0, column=1)

tk.Label(root, text="Number of Nurses:").grid(row=1, column=0)
nurses_entry = tk.Entry(root)
nurses_entry.insert(0, "5")
nurses_entry.grid(row=1, column=1)

tk.Label(root, text="Number of Beds:").grid(row=2, column=0)
beds_entry = tk.Entry(root)
beds_entry.insert(0, "10")
beds_entry.grid(row=2, column=1)

tk.Label(root, text="Simulation Time (minutes):").grid(row=3, column=0)
sim_time_entry = tk.Entry(root)
sim_time_entry.insert(0, "480")
sim_time_entry.grid(row=3, column=1)

tk.Label(root, text="Random Seed:").grid(row=4, column=0)
random_seed_entry = tk.Entry(root)
random_seed_entry.insert(0, "42")
random_seed_entry.grid(row=4, column=1)

# Start button
start_button = tk.Button(root, text="Run Simulation", command=start_simulation)
start_button.grid(row=5, column=0, columnspan=2)

# Output text area
output_text = tk.Text(root, height=15, width=80)
output_text.grid(row=6, column=0, columnspan=2)


# Create the main window
root = tk.Tk()
root.title("Healthcare Logistics Simulation Tool")

# ... (input fields and start button)

# Output text area
output_text = tk.Text(root, height=10, width=80)
output_text.grid(row=6, column=0, columnspan=2)

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=7, column=0, columnspan=2)

# Initialize plot lines
lines = {}

root.mainloop()

