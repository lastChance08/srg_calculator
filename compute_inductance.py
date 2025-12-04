import subprocess
import numpy as np
import shutil
import json

input_prj = "srg8"
result_file_name = input_prj + ".json"
tmp_prj = input_prj + "_tmp"
input_file_mame = input_prj + ".fem"
tmp_file_name = tmp_prj + ".fem"

start_angle = -25
end_angle = 25
points = 60

#That's bad but innerangle doesn't affect non-airgap boundaries
def set_inner_angle(angle):
    try:
        # Read the file content
        with open(input_file_mame, 'r') as inputFile:
            file_content = inputFile.read()

        # Perform the string replacement
        modified_content = file_content.replace("<innerangle> = 0", "<innerangle> = " + angle)

        # Write the modified content back to the file
        with open(tmp_file_name, 'w') as tmp_file:
            tmp_file.write(modified_content)

    except FileNotFoundError:
        print(f"Error: File not found '{input_file_mame}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


shutil.copy(input_file_mame, tmp_file_name)
theta_array = np.linspace(start_angle, end_angle, points)
inductance_array = np.array([])

for theta in np.nditer(theta_array):
    theta_str = f"{theta:.3f}" 
    set_inner_angle(theta_str)
    subprocess.run(["./fmesher", tmp_file_name])
    subprocess.run(["./fsolver", tmp_prj], check=False)
    inductance = float(subprocess.run(["./fpproc-test", tmp_prj+".ans"], capture_output=True, text=True, check=False).stdout)
    inductance_array = np.append(inductance_array, inductance, axis=None)

data = {
  "theta": theta_array.tolist(),
  "inductance": inductance_array.tolist()
}

try:
    with open(result_file_name, 'w') as result_file:
        result_file.write(json.dumps(data))
except Exception as e:
    print(f"An error occurred: {e}")

