import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main script
import 深度图数据集_v6 as dataset_script

# Test the main script logic with our test config
if __name__ == "__main__":
    config_path = "test_config.json"
    print(f"Testing with config: {config_path}")
    
    # Run the main script logic
    dataset_script.main_script_logic(config_path)
    
    print("Test completed.")