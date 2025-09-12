
import bpy
import json
import os
import sys
from pathlib import Path

print("=== Blender Dataset Generation Started ===")
print(f"Python version: {{sys.version}}")
print(f"Blender version: {{bpy.app.version_string}}")

# Load configuration
config_path = r"C:\Users\sua\AppData\Local\Temp\tmp8cvr0a5r.json"
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Configuration loaded from: {{config_path}}")
except Exception as e:
    print(f"FATAL ERROR: Failed to load config from {{config_path}}: {{e}}")
    sys.exit(1)

# Get the directory of this script
this_script_dir = Path(__file__).parent
print(f"This script directory: {{this_script_dir}}")

# Handle script path from config
user_script_relative = r"D:\blender-tool\深度图数据集_v6.py"
user_script_path_obj = Path(user_script_relative)

if user_script_path_obj.is_absolute():
    # Absolute path
    script_dir_to_add = user_script_path_obj.parent.as_posix()
    module_name = user_script_path_obj.stem
else:
    # Relative path - try multiple locations
    possible_paths = [
        this_script_dir / user_script_relative,
        Path.cwd() / user_script_relative,
        Path(__file__).parent / user_script_relative
    ]
    
    script_dir_to_add = None
    module_name = user_script_path_obj.stem
    
    for possible_path in possible_paths:
        if possible_path.exists():
            script_dir_to_add = possible_path.parent.as_posix()
            print(f"Found script at: {{possible_path}}")
            break
    
    if script_dir_to_add is None:
        print(f"FATAL ERROR: Could not find script '{user_script_relative}' in any of these locations:")
        for p in possible_paths:
            print(f"  - {{p}}")
        sys.exit(1)

print(f"Script directory to add: {{script_dir_to_add}}")
print(f"Module name: {{module_name}}")

# Add script directory to Python path
if script_dir_to_add not in sys.path:
    sys.path.insert(0, script_dir_to_add)
print(f"Updated sys.path: {{sys.path}}")

try:
    # Dynamically import the module
    print(f"Attempting to import module: '{{module_name}}'")
    user_module = __import__(module_name)
    
    # Execute the main script logic with config path
    print("Executing main script logic with config path...")
    user_module.main_script_logic(config_path)

except ImportError as e:
    print(f"FATAL ERROR: Could not import module '{{module_name}}' from path '{{script_dir_to_add}}'.")
    print("Please ensure the 'Blender脚本路径' in the GUI's Advanced Settings is correct.")
    print(f"Current Blender sys.path: {{sys.path}}")
    print(f"Import error details: {{e}}")
    sys.exit(1)
except AttributeError as e:
    print(f"FATAL ERROR: A function was not found in the module '{{module_name}}'. {{e}}")
    print("Please ensure your script '深度图数据集_v6.py' contains all required functions.")
except Exception as e:
    print(f"Error during dataset generation: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

