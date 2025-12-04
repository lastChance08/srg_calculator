import pygad
import numpy as np
from scipy.integrate import quad
from scipy.integrate import solve_ivp
from scipy import interpolate
from scipy.ndimage import maximum
import json

input_file_name = "srg8.json"

r = 1
U1 = 24
U2 = 24

Rdson = 0.05 #Rdson of a MOSFET (excitation phase)
Ud = 0.3

strokes = 8
rpm = 600
omega = rpm * np.pi / 30

Imax = 2

num_genes = 3
step = 0.1
# Genes
# Gene 1 is theta1
# Gene 2 is theta2 - theta1
# Gene 3 is theta_end - theta2
gene_space = [{'low': -4, 'high': 4, "step": step}, {'low': 0, 'high': 12, "step": step}, {'low': 0, 'high': 15, "step": step}]

num_generations = 100 # Number of generations.
num_parents_mating = 5 # Number of solutions to be selected as parents in the mating pool.

sol_per_pop = 30 # Number of solutions in the population.

try:
    with open(input_file_name, 'r') as input_file:
        file_content = input_file.read()
        file_data = json.loads(file_content)
        theta_data = file_data["theta"]
        Ldata = file_data["inductance"]
except Exception as e:
    print(f"An error occurred: {e}")
    quit()

theta_rad = np.deg2rad(theta_data)

L = interpolate.make_splrep(theta_rad, Ldata, s=0) 

dLdTh = L.derivative()

def didtheta_excite(theta, i):
    return -(dLdTh(theta) * omega + r + Rdson * 2) / (L(theta) * omega) * i + U1 / (L(theta) * omega)

def didtheta_generate(theta, i):
    return -(dLdTh(theta) * omega + r) / (L(theta) * omega) * i - (U2 - 2 * Ud) / (L(theta) * omega)

def fitness_func(ga_instance, solution, solution_idx):
    theta1 = np.deg2rad(solution[0])
    theta2 = theta1 + np.deg2rad(solution[1])
    theta_end = theta2 + np.deg2rad(solution[2])

    i_excite = solve_ivp(didtheta_excite, [theta1, theta2], [0], method="Radau", dense_output=True)
    y, err = quad(i_excite.sol, theta1, theta2)
    exc_enegry = y * U1
    i_generate = solve_ivp(didtheta_generate, [theta2, theta_end], i_excite.sol(theta2), method="Radau",dense_output=True)
    y, err = quad(i_generate.sol, theta2, theta_end)
    gen_enegry = y * U2

    max_current = maximum(np.append(i_excite.y,  i_generate.y))
    power = (gen_enegry - exc_enegry) * strokes * rpm / 60
    if(max_current > Imax):
        power = power * 0.2
        #print(power)
    return power


last_fitness = 0

def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       parallel_processing=["process", 4],
                       sol_per_pop=sol_per_pop,
                       gene_space=gene_space,
                       num_genes=num_genes,
                       fitness_func=fitness_func,
                       on_generation=on_generation)

# Running the GA to optimize the parameters of the function.
ga_instance.run()

ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution(ga_instance.last_generation_fitness)

theta1 = solution[0] 
theta2 = theta1 + solution[1]
theta_end = theta2 + solution[2]
print("theta1 =", theta1)
print("theta2 =", theta2)
print("theta_end =", theta_end)
print("Power=", solution_fitness)



