import math as m
import numpy as np

def calc_dP_b(H, rho, beta, dT):
    dT = max(dT, 0)  # Ensure no negative temperature difference

    # Calculate pressure difference due to buoyancy

    dP_b = 9.81*H*rho*beta*dT

    return dP_b

def calc_v(H, rho, beta, dT, L, D, f):
    # Calculate the volume flow velocity base on the Darcy-Weisbach equation

    dP = calc_dP_b(H, rho, beta, dT)
    v = m.sqrt((2*dP*D)/(f*L*rho))

    return v

def calc_dm(H, rho, beta, dT, L, D, f):
    # Calculate the mass flow rate of water due to thermosyphon

    v = calc_v(H, rho, beta, dT, L, D, f)

    # C-S area of pipe
    A = 0.25*m.pi*(D**2)

    dm = rho*v*A

    return dm

def calc_eta(eta_slope, eta_0, G, T_collector, T_amb):
    dT = T_collector - T_amb
    eta = eta_0 + (eta_slope * (dT / (G + 1e-6)))
    return max(eta, 0)  # Ensure eta is non-negative

def irradiance_data(season):
    # Determine hourly irradiance profile and T_amb based on the season selection
    # Cold = Jan, warm = April, hot = July
    # Latitude = 24.86, Longitude = -103.47

    T_amb = 0
    t_hr = np.arange(0,10,1)

    if season == 'a':
        #January 2nd, 2022, t = 900 - 1800
        T_amb = 7.5 #C
        GHI_hr = np.array([366, 555, 691, 770, 767, 692, 552, 358, 137, 0])
    elif season == 'b':
        #April 15th, 2022, t = 900 - 1800
        T_amb = 15 #C
        GHI_hr = np.array([696, 903, 1044, 1111, 1104, 1019, 865, 653, 403, 145])
    elif season == 'c':
        #Using the same GHI as April 15th as it's pretty similar
        #July is a rainy season so it can impact GHI
        T_amb = 20 #C
        GHI_hr = np.array([696, 903, 1044, 1111, 1104, 1019, 865, 653, 403, 145])

    # Find polynomial fit
    coeff = np.polyfit(t_hr, GHI_hr, 4)

    return coeff, T_amb