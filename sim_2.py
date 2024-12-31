import numpy as np
import thermal_func as tf
import matplotlib.pyplot as plt
import os
import pandas as pd

#collects user imputs
#collects 
print("###########################################################")
dm_str = input("Define a pump flow rate (kg/s): ")
name = dm_str
dm = float(dm_str)

#Determine ambient temperature and irradiance data
print('Select what type of season to analyze:')
print("a. cold \nb. warm \nc. hot")
season_selection = input('Make your selection: ')
valid_seaons = ['a', 'b', 'c']
while season_selection not in valid_seaons:
    season_selection = input("Invalid selection. Please pick a valid collector type (a, b, c, d): ").lower()

coeff, T_ambient = tf.irradiance_data(season_selection)


# List of collector areas to test
collector_areas = np.arange(1, 15, 0.5)

user_input_dir = '/home/wen-gu/solar_design/' + name
#user_input_dir = 'D:\my files\skule\solar_design' + name
os.makedirs(user_input_dir, exist_ok=True)
user_input_file = name + '.csv'

#combine directory and file name to create the full path
file_path = os.path.join(user_input_dir, user_input_file)

#initialize csv file
headers = ['Area [m^2]', 'Final Collector Temperature [C]', 'Final Tank Water Temperature [C]']
df = pd.DataFrame(columns=headers)
df.to_csv(file_path, index=False)

# Define parameters, subject to changes
m_water = 300  # kg
cp = 4186  # J/kg*K
D_tank = 0.85  # m Diameter of tank
H_tank = 0.99  # m
U_tank = 0.5  # W/m^2*K Taken from excel sheet 'Cooling in Heater Insulation'
time_step = 60  # seconds
total_time = 10 * 3600  # 7 hrs in seconds
rho = 1000  # kg/m^3
beta = 0.000214  # 1/K thermal expansion coefficient of water
tank_area = np.pi * D_tank * H_tank + np.pi * (D_tank / 2)**2
H = 0.5  # m (height difference)
L = 5  # m (Pipe length)
D = 0.02  # m (diameter)
f = 0.02  # friction factor

#data of solar collector
eta_slope = -6.08
eta_0 = 0.726
U_collector = 4 #W/m2*k

# Simulation for each collector area
for area in collector_areas:
    V_collector = 0.02 * area  # assume effective thickness is 2cm
    m_collector = V_collector * rho  # kg
    T_tank = T_ambient  # °C
    T_collector = T_tank + 0  # °C (slightly higher to kickstart the process)
    temperature_tank = []
    temperature_collector = []
    time = np.arange(0, total_time + time_step, time_step)
    
    # Initialize previous tank temperature and collector status
    T_tank_previous = T_tank
    collector_empty = False  # Flag to track if the collector is empty

    for t in time:
        # Calculate irradiance
        t_h = t / 3600
        G = coeff[0] * (t_h**4) + coeff[1] * (t_h**3) + coeff[2] * (t_h**2) + coeff[3] * (t_h**1) + coeff[4]

        if not collector_empty:
            # Update collector efficiency
            eta = max(tf.calc_eta(eta_slope, eta_0, G, T_collector, T_ambient), 0)

            # Calculate absorbed heat
            Q_absorbed = eta * G * area

            # Calculate energy exchange with the tank
            Q_exchange = dm * cp * (T_collector - T_tank) if dm > 0 else 0

            # Calculate heat loss from surface of collector
            Q_loss_c = area * U_collector * (T_collector - T_ambient)

            # Net energy in the collector
            Q_net = Q_absorbed - Q_exchange - Q_loss_c

            # Update collector temperature
            delta_T_collector = Q_net * time_step / (m_collector * cp)
            T_collector += delta_T_collector
            T_collector = min(T_collector, 100)  # Cap at boiling point

        else:
            # If the collector is empty, set flow rate and heat transfer to 0
            dm = 0
            T_collector = T_ambient
            Q_exchange = 0
            m_collector = 0

        # Update tank temperature
        Q_loss = U_tank * tank_area * max(T_tank - T_ambient, 0)
        dT_tank = (Q_exchange - Q_loss) * time_step / ((m_water - m_collector) * cp)
        T_tank += dT_tank

        # Check if tank temperature is dropping
        if T_tank < T_tank_previous and not collector_empty:
            # Pump water from collector back to tank
            # T_tank = 0.8*(T_tank * m_water + T_collector * m_collector) / (m_water + m_collector)
            heat_loss_fraction = 0.05
            Q_transfer = m_collector * cp * T_collector * (1 - heat_loss_fraction)
            T_tank = (T_tank * (m_water-m_collector) * cp + Q_transfer) / (m_water * cp)
            T_collector = T_ambient  # Reset collector to ambient after emptying
            collector_empty = True  # Mark collector as empty

        # Update previous tank temperature
        T_tank_previous = T_tank

        # Store results
        temperature_tank.append(T_tank)
        temperature_collector.append(T_collector)

    output = np.array([area, T_collector, T_tank]).reshape(1, -1)
    df_to_append = pd.DataFrame(output, columns=['Area [m^2]', 'Final Collector Temperature [C]', 'Final Tank Water Temperature [C]'])
    df_to_append.to_csv(file_path, mode='a', index=False, header=False)

    # Plot results
    plt.figure()
    plt.plot(time / 3600, temperature_tank, label="Tank Temperature (°C)")
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
