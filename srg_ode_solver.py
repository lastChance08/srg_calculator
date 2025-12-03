import numpy as np
from scipy.integrate import quad
from scipy.integrate import solve_ivp
from scipy import interpolate
import matplotlib.pyplot as plt
import json

input_file_name = "srg8.json"

theta1 = np.deg2rad(1.3)
theta2 = np.deg2rad(9.2)
theta_end = np.deg2rad(16.3)

strokes = 8
rpm = 1200
omega = rpm * np.pi / 30
r =  1
U1 = 24
U2 = 24
Usw = 0.1 #Voltage drop on a MOSFET (excitation phase)
Ud = 0.3  #Diode forward volage (generation phase)
# Initial condition
i0 = 0

try:
    with open(input_file_name, 'r') as inputFile:
        file_content = inputFile.read()
        file_data = json.loads(file_content)
        theta_data = file_data["theta"]
        Ldata = file_data["inductance"]
except Exception as e:
    print(f"An error occurred: {e}")
    quit()

#quit()


# Interpolation
theta_rad = np.deg2rad(theta_data)

L = interpolate.make_splrep(theta_rad, Ldata, s=0) 

plt.plot(np.rad2deg(theta_rad), L(theta_rad) , '-', color="green")
plt.xlabel('Theta, deg')
plt.ylabel('L, H')
plt.show()
#quit()

dLdTh = L.derivative()

plt.plot(np.rad2deg(theta_rad), dLdTh(theta_rad) , '-', color="green")
plt.xlabel('Theta, deg')
plt.ylabel('dL/dTheta')
plt.show()
#quit()


def didtheta_excite(theta, i):
    return -(dLdTh(theta) * omega + r) / (L(theta) * omega) * i + (U1 - 2 * Usw) / (L(theta) * omega)

# Solve the ODE
i_excite = solve_ivp(didtheta_excite, [theta1, theta2], [0], method="RK23", dense_output=True)

y, err = quad(i_excite.sol, theta1, theta2)
exc_enegry = y * U1

theta_excite = np.linspace(theta1, theta2, 300)
current_excite = i_excite.sol(theta_excite)


#quit()

def didtheta_generate(theta, i):
    return -(dLdTh(theta) * omega + r) / (L(theta) * omega) * i - (U2 - 2 * Ud) / (L(theta) * omega)

# Solve the ODE
i_generate = solve_ivp(didtheta_generate, [theta2, theta_end], i_excite.sol(theta2), method="RK23", dense_output=True)
y, err = quad(i_generate.sol, theta2, theta_end)

gen_enegry = y * U2

power = (gen_enegry - exc_enegry) * strokes * rpm / 60
print("Power:", power)

theta_generate = np.linspace(theta2, theta_end, 300)
current_generate= i_generate.sol(theta_generate)
theta = np.append(theta_excite, theta_generate)
current = np.append(current_excite, current_generate)

plt.axvline(x=np.rad2deg(theta2), linewidth=1, color='r')

plt.plot(np.rad2deg(theta), current)
plt.xlabel('Theta, deg')
plt.ylabel('I, A')
plt.show()
