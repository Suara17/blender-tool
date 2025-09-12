#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to run the Blender dataset generation with test configuration
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from blender_mcp_integration import BlenderMCPIntegration
    print("Successfully imported BlenderMCPIntegration")
except ImportError as e:
    print(f"Failed to import BlenderMCPIntegration: {e}")
    sys.exit(1)

def main():
    # Load test configuration
    config_path = current_dir / "test_config.json"
    if not config_path.exists():
        print(f"Test configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("Test configuration loaded successfully")
    except Exception as e:
        print(f"Failed to load test configuration: {e}")
        sys.exit(1)
    
    # Define progress callback
    def progress_callback(progress, message):
        print(f"[{progress:5.1f}%] {message}")
    
    # Initialize integration
    print("Initializing BlenderMCPIntegration...")
    integration = BlenderMCPIntegration()
    
    # Test Blender connection first
    print("Testing Blender connection...")
    success, message = integration.test_blender_connection()
    print(f"Connection test result: {success} - {message}")
    
    if not success:
        print("Blender connection test failed. Cannot proceed with dataset generation.")
        return
    
    # Generate dataset
    print("\nStarting dataset generation...")
    try:
        result = integration.generate_dataset(config, progress_callback)
        print("\nDataset generation completed!")
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if 'output_files' in result:
            print(f"Output files generated: {len(result['output_files'])}")
            for file in result['output_files'][:5]:  # Show first 5 files
                print(f"  - {file}")
            if len(result['output_files']) > 5:
                print(f"  ... and {len(result['output_files']) - 5} more files")
                
        if 'parameters_file' in result:
            print(f"Parameters file: {result['parameters_file']}")
            
        if 'error' in result:
            print(f"Error: {result['error']}")
            
        if 'traceback' in result:
            print("Traceback:")
            print(result['traceback'])
            
    except Exception as e:
        print(f"Dataset generation failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()