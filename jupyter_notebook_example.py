"""
BGA to PCB Model Creation Example for AEDT Jupyter Notebook

This script demonstrates how to create a BGA to PCB transition model
using the pyaedt_model_create_classes library within an AEDT Jupyter notebook.

Instructions:
1. Update the repo_path variable below to point to your pyaedt_model_create_classes directory
2. Run this cell to execute the model creation
3. Check the project_path directory for the generated .aedb file

"""

import os
import sys
from pyaedt import Edb

# ==============================================================================
# SETUP: Configure the path to pyaedt_model_create_classes repository
# ==============================================================================

# Option 1: Direct path (recommended)
# Update this path to match your actual repository location
repo_path = r"C:\Users\ewanlle\Documents\martin_wrappers\pyaedt_model_create_classes"

# Option 2: Relative path (if notebook is in a predictable location)
# Uncomment and modify as needed:
# repo_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "pyaedt_model_create_classes"))

# Option 3: Auto-detect in common locations (Windows)
# Uncomment to try automatic detection:
# common_paths = [
#     r"C:\Users\{}\Documents\pyaedt_model_create_classes".format(os.getenv('USERNAME')),
#     r"C:\Users\{}\Desktop\pyaedt_model_create_classes".format(os.getenv('USERNAME')),
#     r"C:\PyAEDT\pyaedt_model_create_classes"
# ]
# for path in common_paths:
#     if os.path.exists(path):
#         repo_path = path
#         break

print(f"Looking for repository at: {repo_path}")
print(f"Current working directory: {os.getcwd()}")

# Check if the repository path exists
if not os.path.exists(repo_path):
    raise FileNotFoundError(f"""
    Repository not found at: {repo_path}
    
    Please update the 'repo_path' variable above to point to your 
    pyaedt_model_create_classes repository location.
    
    You can check your current working directory with: os.getcwd()
    """)

# Verify repository structure
print("Checking repository structure...")
expected_dirs = [
    "create_solder_ball_transition_models",
    "create_pcb_models"
]

for dir_name in expected_dirs:
    dir_path = os.path.join(repo_path, dir_name)
    if os.path.exists(dir_path):
        print(f"✓ Found: {dir_name}")
    else:
        print(f"✗ Missing: {dir_name}")

# Check for specific files we need
package2pcb_path = os.path.join(repo_path, "create_solder_ball_transition_models", "package2pcbBall.py")
stackup_path = os.path.join(repo_path, "create_pcb_models", "stackup_definitions", "pcbStackUpDefinitions.py")

print(f"Package2pcbBall.py exists: {os.path.exists(package2pcb_path)}")
print(f"StackUp definitions exists: {os.path.exists(stackup_path)}")

# Add to Python path
if repo_path not in sys.path:
    sys.path.insert(0, repo_path)  # Insert at beginning for priority
    print(f"Added {repo_path} to Python path")

# Also add subdirectories to path as fallback
subdirs_to_add = [
    os.path.join(repo_path, "create_solder_ball_transition_models"),
    os.path.join(repo_path, "create_pcb_models"),
    os.path.join(repo_path, "create_pcb_models", "stackup_definitions"),
    os.path.join(repo_path, "pyaedt_wrapper_classes")
]

for subdir in subdirs_to_add:
    if os.path.exists(subdir) and subdir not in sys.path:
        sys.path.insert(0, subdir)
        print(f"Added {subdir} to Python path")

print(f"\nCurrent Python path (first 5 entries):")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

# ==============================================================================
# IMPORTS: Import the required modules with multiple fallback methods
# ==============================================================================

def import_with_fallbacks():
    """Try multiple import methods to handle different repository structures"""
    
    # Method 1: Standard package import
    try:
        from pyaedt_model_create_classes.create_solder_ball_transition_models.package2pcbBall import bga_2_pcb_diff
        from pyaedt_model_create_classes.create_pcb_models.stackup_definitions.pcbStackUpDefinitions import StackUp_7_2_7_77PP_75C_25Cu
        print("✓ Method 1: Successfully imported using standard package structure")
        return bga_2_pcb_diff, StackUp_7_2_7_77PP_75C_25Cu
    except ImportError as e:
        print(f"✗ Method 1 failed: {e}")
    
    # Method 2: Direct file import
    try:
        import importlib.util
        
        # Import package2pcbBall.py directly
        package2pcb_spec = importlib.util.spec_from_file_location(
            "package2pcbBall", 
            os.path.join(repo_path, "create_solder_ball_transition_models", "package2pcbBall.py")
        )
        package2pcb_module = importlib.util.module_from_spec(package2pcb_spec)
        
        # Before loading, we need to make sure edb_wrapper_class is importable
        edb_wrapper_spec = importlib.util.spec_from_file_location(
            "edb_wrapper_class",
            os.path.join(repo_path, "pyaedt_wrapper_classes", "edb_wrapper_class.py")
        )
        edb_wrapper_module = importlib.util.module_from_spec(edb_wrapper_spec)
        sys.modules['pyaedt_wrapper_classes.edb_wrapper_class'] = edb_wrapper_module
        sys.modules['edb_wrapper_class'] = edb_wrapper_module
        edb_wrapper_spec.loader.exec_module(edb_wrapper_module)
        
        # Now load the main module
        package2pcb_spec.loader.exec_module(package2pcb_module)
        
        # Import stackup definitions directly
        stackup_spec = importlib.util.spec_from_file_location(
            "pcbStackUpDefinitions",
            os.path.join(repo_path, "create_pcb_models", "stackup_definitions", "pcbStackUpDefinitions.py")
        )
        stackup_module = importlib.util.module_from_spec(stackup_spec)
        stackup_spec.loader.exec_module(stackup_module)
        
        print("✓ Method 2: Successfully imported using direct file import")
        return package2pcb_module.bga_2_pcb_diff, stackup_module.StackUp_7_2_7_77PP_75C_25Cu
        
    except Exception as e:
        print(f"✗ Method 2 failed: {e}")
    
    # Method 3: Add parent directory and try relative imports
    try:
        parent_dir = os.path.dirname(repo_path)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from pyaedt_model_create_classes.create_solder_ball_transition_models.package2pcbBall import bga_2_pcb_diff
        from pyaedt_model_create_classes.create_pcb_models.stackup_definitions.pcbStackUpDefinitions import StackUp_7_2_7_77PP_75C_25Cu
        print("✓ Method 3: Successfully imported using parent directory")
        return bga_2_pcb_diff, StackUp_7_2_7_77PP_75C_25Cu
        
    except ImportError as e:
        print(f"✗ Method 3 failed: {e}")
    
    # Method 4: Try importing from subdirectories directly
    try:
        from package2pcbBall import bga_2_pcb_diff
        from pcbStackUpDefinitions import StackUp_7_2_7_77PP_75C_25Cu
        print("✓ Method 4: Successfully imported from subdirectories")
        return bga_2_pcb_diff, StackUp_7_2_7_77PP_75C_25Cu
        
    except ImportError as e:
        print(f"✗ Method 4 failed: {e}")
    
    # Method 5: Manual sys.modules manipulation
    try:
        import importlib.util
        
        # Manually add modules to sys.modules
        edb_wrapper_spec = importlib.util.spec_from_file_location(
            "edb_wrapper_class",
            os.path.join(repo_path, "pyaedt_wrapper_classes", "edb_wrapper_class.py")
        )
        edb_wrapper_module = importlib.util.module_from_spec(edb_wrapper_spec)
        edb_wrapper_spec.loader.exec_module(edb_wrapper_module)
        sys.modules['pyaedt_wrapper_classes'] = type('Module', (), {})()
        sys.modules['pyaedt_wrapper_classes'].edb_wrapper_class = edb_wrapper_module
        sys.modules['pyaedt_wrapper_classes.edb_wrapper_class'] = edb_wrapper_module
        
        # Now try importing the main modules
        package2pcb_spec = importlib.util.spec_from_file_location(
            "package2pcbBall", 
            os.path.join(repo_path, "create_solder_ball_transition_models", "package2pcbBall.py")
        )
        package2pcb_module = importlib.util.module_from_spec(package2pcb_spec)
        package2pcb_spec.loader.exec_module(package2pcb_module)
        
        stackup_spec = importlib.util.spec_from_file_location(
            "pcbStackUpDefinitions",
            os.path.join(repo_path, "create_pcb_models", "stackup_definitions", "pcbStackUpDefinitions.py")
        )
        stackup_module = importlib.util.module_from_spec(stackup_spec)
        stackup_spec.loader.exec_module(stackup_module)
        
        print("✓ Method 5: Successfully imported using manual sys.modules manipulation")
        return package2pcb_module.bga_2_pcb_diff, stackup_module.StackUp_7_2_7_77PP_75C_25Cu
        
    except Exception as e:
        print(f"✗ Method 5 failed: {e}")
    
    raise ImportError("All import methods failed. Please check repository structure and paths.")

# Try to import the modules
try:
    bga_2_pcb_diff, StackUp_7_2_7_77PP_75C_25Cu = import_with_fallbacks()
    print("✓ Successfully imported all required modules")
except Exception as e:
    print(f"✗ All import methods failed: {e}")
    print("\nDebugging information:")
    print(f"Repository path: {repo_path}")
    print(f"Repository exists: {os.path.exists(repo_path)}")
    print(f"Repository contents: {os.listdir(repo_path) if os.path.exists(repo_path) else 'N/A'}")
    raise

# ==============================================================================
# MODEL CREATION: Set up and run the BGA to PCB model creation
# ==============================================================================

# Define project path - this will be created in your current working directory
current_dir = os.getcwd()
project_path = os.path.join(current_dir, "bga_pcb_model_project")
os.makedirs(project_path, exist_ok=True)

print(f"Project will be created in: {project_path}")

# Initialize the Edb object
print("Initializing EDB object...")
edb = Edb(project_path, edbversion="2022.2")

# Initialize the stackup with the Edb object
print("Setting up stackup...")
stackup = StackUp_7_2_7_77PP_75C_25Cu(edb)

# Define ball pattern and other parameters
# Pattern: 0 = ground, 1 = positive signal, -1 = negative signal
ball_pattern = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
    [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
ball_pitch = '500um'
design_name_suffix = 'JupyterExample'
edb_version = "2022.2"

print(f"Ball pattern: {len([x for row in ball_pattern for x in row if x != 0])} signal balls")
print(f"Ball pitch: {ball_pitch}")
print(f"Design suffix: {design_name_suffix}")

# ==============================================================================
# RUN MODEL CREATION
# ==============================================================================

print("\nStarting BGA to PCB model creation...")
print("This may take a few minutes...")

try:
    # Run the function to create the model
    design_name = bga_2_pcb_diff(
        prjPath=project_path,
        stackup=stackup,
        ballPattern=ball_pattern,
        ballPitch=ball_pitch,
        designNameSuffix=design_name_suffix,
        edbversion=edb_version
    )
    
    print(f"✓ Model creation completed successfully!")
    print(f"Design name: {design_name}")
    
    # Check if files were created
    expected_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.aedb') or file.endswith('.aedt'):
                expected_files.append(os.path.join(root, file))
    
    if expected_files:
        print(f"\nGenerated files:")
        for file in expected_files:
            print(f"  - {file}")
    else:
        print("\nWarning: No .aedb or .aedt files found in project directory")
        print("Model may have been created but files might be in a different location")
    
    print(f"\nProject directory: {project_path}")
    print("You can now open the generated .aedb file in AEDT Electronics Desktop")

except Exception as e:
    print(f"✗ Error during model creation: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    print(f"Full traceback:\n{traceback.format_exc()}")
    raise

print("\n" + "="*50)
print("BGA to PCB Model Creation Complete!")
print("="*50) 