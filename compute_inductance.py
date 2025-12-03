import subprocess
import numpy as np
import shutil
import json

inputPrj = "srg8"
resultFileName = inputPrj + ".json"
tmpPrj = inputPrj + "_tmp"
inputFileName = inputPrj + ".fem"
tmpFileName = tmpPrj + ".fem"

startAngle = -25
endAngle = 25
points = 60

#That's bad but innerangle doesn't affect non-airgap boundaries
def setInnerAngle(angle):
    try:
        # Read the file content
        with open(inputFileName, 'r') as inputFile:
            file_content = inputFile.read()

        # Perform the string replacement
        modified_content = file_content.replace("<innerangle> = 0", "<innerangle> = " + angle)

        # Write the modified content back to the file
        with open(tmpFileName, 'w') as tmpFile:
            tmpFile.write(modified_content)

    except FileNotFoundError:
        print(f"Error: File not found '{inputFileName}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


shutil.copy(inputFileName, tmpFileName)
thetaArray = np.linspace(startAngle, endAngle, points)
inductanceArray = np.array([])

for theta in np.nditer(thetaArray):
    theta_str = f"{theta:.3f}" 
    setInnerAngle(theta_str)
    subprocess.run(["./fmesher", tmpFileName])
    subprocess.run(["./fsolver", tmpPrj], check=False)
    inductance = float(subprocess.run(["./fpproc-test", tmpPrj+".ans"], capture_output=True, text=True, check=False).stdout)
    inductanceArray = np.append(inductanceArray, inductance, axis=None)

data = {
  "theta": thetaArray.tolist(),
  "inductance": inductanceArray.tolist()
}

try:
    with open(resultFileName, 'w') as resultFile:
        resultFile.write(json.dumps(data))
except Exception as e:
    print(f"An error occurred: {e}")

