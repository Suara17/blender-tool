#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify the complete dataset generation workflow
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path to import the integration module
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from blender_mcp_integration import BlenderMCPIntegration, create_sample_dataset
    print("Successfully imported BlenderMCPIntegration")
except ImportError as e:
    print(f"Failed to import BlenderMCPIntegration: {e}")
    sys.exit(1)

def test_blender_connection():
    """Test if Blender is accessible"""
    print("Testing Blender connection...")
    integration = BlenderMCPIntegration()
    success, message = integration.test_blender_connection()
    print(f"Blender connection test result: {success}")
    print(f"Message: {message}")
    return success

def create_test_config():
    """Create a test configuration"""
    # Create temporary directories for testing
    temp_dir = Path(tempfile.gettempdir()) / "blender_dataset_test"
    temp_dir.mkdir(exist_ok=True)
    
    stl_folder = temp_dir / "stl_models"
    pattern_folder = temp_dir / "patterns"
    output_folder = temp_dir / "output"
    
    # Create directories
    stl_folder.mkdir(exist_ok=True)
    pattern_folder.mkdir(exist_ok=True)
    output_folder.mkdir(exist_ok=True)
    
    # Create a simple test configuration
    config = {
        "paths": {
            "stl_folder": str(stl_folder),
            "pattern_folder": str(pattern_folder),
            "output_folder": str(output_folder),
            "hdri_path": ""
        },
        "camera": {
            "position": [-100, -300, 0],
            "rotation": [90, 0, -17],
            "focal_length": 50.0,
            "clip_start": 10.0,
            "clip_end": 1500.0
        },
        "projector": {
            "position": [100, -300, 0],
            "power": 4.5,
            "power_drift": 0.5,
            "use_discrete_power": False,
            "fov": 60.0
        },
        "render": {
            "resolution": [640, 640],
            "engine": "Cycles",
            "samples": 64,  # Use fewer samples for testing
            "ambient_base": 0.5,
            "ambient_variation": 0.1
        },
        "advanced": {
            "stl_max_size": 150.0,
            "rotation_angles": [0, 45],
            "blender_path": "blender",
            "script_path": "深度图数据集_v6.py"
        }
    }
    
    return config

def test_dataset_generation():
    """Test the complete dataset generation workflow"""
    print("Creating test configuration...")
    config = create_test_config()
    
    print("Configuration created:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    def progress_callback(progress, message):
        print(f"Progress: {progress:.1f}% - {message}")
    
    print("Initializing BlenderMCPIntegration...")
    integration = BlenderMCPIntegration()
    
    print("Generating dataset...")
    try:
        result = integration.generate_dataset(config, progress_callback)
        print(f"Dataset generation completed with result: {result}")
        return result
    except Exception as e:
        print(f"Dataset generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print("=" * 50)
    print("Blender Dataset Generation Test")
    print("=" * 50)
    
    # Test Blender connection
    if not test_blender_connection():
        print("Blender connection test failed. Exiting.")
        return
    
    # Test dataset generation
    result = test_dataset_generation()
    
    if result and result.get("success"):
        print("\n" + "=" * 50)
        print("TEST PASSED: Dataset generation completed successfully!")
        print("=" * 50)
        print(f"Output files: {result.get('output_files', [])}")
        print(f"Parameters file: {result.get('parameters_file', '')}")
    else:
        print("\n" + "=" * 50)
        print("TEST FAILED: Dataset generation failed!")
        print("=" * 50)
        if result:
            print(f"Error: {result.get('message', 'Unknown error')}")
            if 'error' in result:
                print(f"Details: {result['error']}")
            if 'traceback' in result:
                print("Traceback:")
                print(result['traceback'])

if __name__ == "__main__":
    main()