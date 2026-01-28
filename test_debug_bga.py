#!/usr/bin/env python3
"""
Debug Test Script for BGA to PCB Model Creation
This script runs the BGA model creation with comprehensive debugging
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    try:
        # Import the required modules
        from create_solder_ball_transition_models.package2pcbBall import bga_2_pcb_diff
        from solderBallStackUpDefinitions import stackup_Bga2L_viaInPadL_Pcb2L_viaInPad
        
        # Configuration
        project_path = r'C:\Users\ewanlle\Documents\Ansoft\new_project'
        edb_version = "2024.1"
        design_name_suffix = "DebugTest"
        ball_pitch = '500um'
        
        # Ball pattern: 4x10 grid with differential pairs
        ball_pattern = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, -1, 0, 0, 1, -1, 0],
            [0, 1, -1, 0, 0, 1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        print("🔍 Running BGA to PCB model creation with debugging...")
        print(f"Project path: {project_path}")
        print(f"Design suffix: {design_name_suffix}")
        print(f"Ball pitch: {ball_pitch}")
        print(f"EDB version: {edb_version}")
        print(f"Ball pattern dimensions: {len(ball_pattern)}x{len(ball_pattern[0])}")
        print("=" * 60)
        
        # Run the function to create the model
        design_name = bga_2_pcb_diff(
            prjPath=project_path,
            stackup=stackup_Bga2L_viaInPadL_Pcb2L_viaInPad,
            ballPattern=ball_pattern,
            ballPitch=ball_pitch,
            designNameSuffix=design_name_suffix,
            edbversion=edb_version
        )
        
        print("=" * 60)
        print(f"✅ Model creation completed!")
        print(f"Design name: {design_name}")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 