import numpy as np

# Constants
T_initial = 40.5  # °C
T_ambient = 7.5  # °C
U_tank = 0.5  # W/m^2*K
A_tank = 3.213  # m^2
m_water = 300  # kg
cp = 4186  # J/kg*K
time = 12 * 3600  # 12 hours in seconds

# Exponential cooling formula
T_final = T_ambient + (T_initial - T_ambient) * np.exp(-U_tank * A_tank * time / (m_water * cp))

print(f"Final tank temperature after 12 hours: {T_final:.2f} °C")