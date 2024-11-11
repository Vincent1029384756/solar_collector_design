import numpy as np
import thermal_func as tf
import matplotlib.pyplot as plt
import os
import pandas as pd

# Collect user inputs
print("###########################################################")
print("Pick a solar collector type")
print("a. Fafco Unglazed, plastic")
print("b. Heliodyne Single glazed, copper, black paint")
print("c. Heliodyne Single glazed, copper, selective absorber")
print("d. Seido Evacuated glass tube, copper selective abs")
collector = input("Make your selection: ").lower()
valid_collectors = ['a', 'b', 'c', 'd']
while collector not in valid_collectors:
    collector = input("Invalid selection. Please pick a valid collector type (a, b, c, d): ").lower()

if collector == 'a':
    eta_slope = -15.47
    eta_0 = 0.8216
    U_collector = 8  # W/m²*K
    name = 'unglazed'

elif collector == 'b':
    eta_slope = -6.08
    eta_0 = 0.726
    U_collector = 4  # W/m²*K
    name = 'glazed_black'

elif collector == 'c':
    eta_slope = -4.57
    eta_0 = 0.737
    U_collector = 3  # W/m²*K
    name = 'glazed_selective'

elif collector == 'd':
    eta_slope = -1.70
    eta_0 = 0.529
    U_collector = 1  # W/m²*K
    name = 'evacuated_tube'

# Determine ambient temperature and irradiance data
print('Select what type of season to analyze:')
print("a. cold \nb. warm \nc.hot")
season_selection = input('Make your selection: ').lower()
valid_seasons = ['a', 'b', 'c']
while season_selection not in valid_seasons:
    season_selection = input("Invalid selection. Please pick a valid season type (a, b, c): ").lower()

coeff, T_ambient = tf.irradiance_data(season_selection)

# List of collector areas to test
collector_areas = np.arange(100, 120)

# Output directory
user_input_dir = f'D:\\my_files\\skule\\solar_design\\collector_{name}'
os.makedirs(user_input_dir, exist_ok=True)
user_input_file = name + '_collector_only.csv'

# Combine directory and file name to create the full path
file_path = os.path.join(user_input_dir, user_input_file)

# Initialize CSV file
headers = ['Area [m^2]', 'Final Collector Temperature [C]']
df = pd.DataFrame(columns=headers)
df.to_csv(file_path, index=False)

# Define simulation parameters
time_step = 60  # seconds
total_time = 6 * 3600  # 10 hours in seconds
rho = 1000  # kg/m³
cp = 4186  # J/kg*K

# Simulation for each collector area
for area in collector_areas:
    V_collector = 0.3  # Assume effective thickness is 2 cm
    m_collector = V_collector * rho  # Mass of water in kg
    T_collector = T_ambient  # Initialize collector temperature to ambient
    temperature_collector = []
    time = np.arange(0, total_time + time_step, time_step)

    for t in time:
        # Calculate irradiance
        t_h = t / 3600
        G = coeff[0] * (t_h**4) + coeff[1] * (t_h**3) + coeff[2] * (t_h**2) + coeff[3] * (t_h**1) + coeff[4]

        # Update collector efficiency
        eta = max(tf.calc_eta(eta_slope, eta_0, G, T_collector, T_ambient), 0)

        # Calculate absorbed heat
        Q_absorbed = eta * G * area

        # Calculate heat loss from surface of collector
        Q_loss_c = area * U_collector * (T_collector - T_ambient)

        # Net energy in the collector
        Q_net = Q_absorbed - Q_loss_c

        # Update collector temperature
        delta_T_collector = Q_net * time_step / (m_collector * cp)
        T_collector += delta_T_collector
        T_collector = min(T_collector, 100)  # Cap at boiling point

        # Store results
        temperature_collector.append(T_collector)

    output = np.array([area, T_collector]).reshape(1, -1)
    df_to_append = pd.DataFrame(output, columns=['Area [m^2]', 'Final Collector Temperature [C]'])
    df_to_append.to_csv(file_path, mode='a', index=False, header=False)

    # Plot results
    plt.figure()
    plt.plot(time / 3600, temperature_collector, label="Collector Temperature (°C)")
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Collector Area: {area} m^2")
    plt.grid()
    plt.legend()
    plot_file = os.path.join(user_input_dir, f"plot_{area}m2.png")
    plt.savefig(plot_file)
    plt.close()

print(f"Simulation complete. Results saved in {user_input_dir}.")
print("###########################################################")
