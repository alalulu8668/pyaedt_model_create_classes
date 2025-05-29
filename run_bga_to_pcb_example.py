import os
import sys
from pyaedt import Edb

# Add the repository path to Python path for imports
# Adjust this path to match where your pyaedt_model_create_classes repository is located
repo_path = r"/path/to/your/pyaedt_model_create_classes"  # Update this path!

# Alternative: use relative path if notebook is in a known location relative to repo
# repo_path = os.path.abspath(os.path.join(os.getcwd(), "..", "pyaedt_model_create_classes"))

if repo_path not in sys.path:
    sys.path.append(repo_path)

# Now import from the repository
from pyaedt_model_create_classes.create_solder_ball_transition_models.package2pcbBall import bga_2_pcb_diff
from pyaedt_model_create_classes.create_pcb_models.stackup_definitions.pcbStackUpDefinitions import StackUp_7_2_7_77PP_75C_25Cu

# Define project path and create the directory if it doesn't exist
current_dir = os.getcwd()  # Use the current working directory
project_path = os.path.join(current_dir, "new_project")
os.makedirs(project_path, exist_ok=True)

# Initialize the Edb object
edb = Edb(project_path, edbversion="2022.2")

# Initialize the stackup with the Edb object
stackup = StackUp_7_2_7_77PP_75C_25Cu(edb)

# Define ball pattern and other parameters
ball_pattern = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
    [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
ball_pitch = '500um'
design_name_suffix = 'Example'
edb_version = "2022.2"

# Run the function to create the model
bga_2_pcb_diff(
    prjPath=project_path,
    stackup=stackup,
    ballPattern=ball_pattern,
    ballPitch=ball_pitch,
    designNameSuffix=design_name_suffix,
    edbversion=edb_version
) 
# check if the model is created
if os.path.exists(os.path.join(project_path, "new_project.aedt")):
    print("Model created successfully")
else:
    print("Model not created")