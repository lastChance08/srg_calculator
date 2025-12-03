import pygad
import numpy as np
from scipy.integrate import quad
from scipy.integrate import solve_ivp
from scipy import interpolate
import json

inputFileName = "srg8.json"

r = 1
U1 = 24
U2 = 24

Usw = 0.1
Ud = 0.3

strokes = 8
rpm = 600
omega = rpm * np.pi / 30


num_genes = 3
step = 0.1
gene_space = [{'low': -3, 'high': 4, "step": step}, {'low': 0, 'high': 8, "step": step}, {'low': 0, 'high': 12, "step": step}]

num_generations = 30 # Number of generations.
num_parents_mating = 2 # Number of solutions to be selected as parents in the mating pool.

sol_per_pop = 20 # Number of solutions in the population.

try:
    with open(inputFileName, 'r') as inputFile:
        file_content = inputFile.read()
        file_data = json.loads(file_content)
        thetadata = file_data["theta"]
        Ldata = file_data["inductance"]
except Exception as e:
    print(f"An error occurred: {e}")
    quit()

theta_rad = np.deg2rad(thetadata)

L = interpolate.make_splrep(theta_rad, Ldata, s=0) 

dLdTh = L.derivative()

def didtheta_excite(theta, i):
    return -(dLdTh(theta) * omega + r) / (L(theta) * omega) * i + (U1 - 2 * Usw) / (L(theta) * omega)

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
    power = (gen_enegry - exc_enegry) * strokes * rpm / 60
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

#ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution(ga_instance.last_generation_fitness)

theta1 = solution[0] 
theta2 = theta1 + solution[1]
theta_end = theta2 + solution[2]
print("theta1 =", theta1)
print("theta2 =", theta2)
print("theta_end =", theta_end)
print("Power=", solution_fitness)



