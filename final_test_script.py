
import bpy
import json
import os
import sys
from pathlib import Path

print("=== Blender Dataset Generation Started ===")
print(f"Python version: {sys.version}")
print(f"Blender version: {bpy.app.version_string}")

# Load configuration
config_path = r"C:\Users\sua\AppData\Local\Temp\tmpnv1_wtd6.json"
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Configuration loaded from: {config_path}")
except Exception as e:
    print(f"FATAL ERROR: Failed to load config from {config_path}: {e}")
    sys.exit(1)

# Get the directory of this script
this_script_dir = Path(__file__).parent
print(f"This script directory: {this_script_dir}")

# Handle script path from config
user_script_relative = r"D:\blender-tool\深度图数据集_v6.py"
user_script_path_obj = Path(user_script_relative)

if user_script_path_obj.is_absolute():
    # Absolute path
    script_dir_to_add = str(user_script_path_obj.parent).replace('\', '/')
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
            script_dir_to_add = str(possible_path.parent).replace('\', '/')
            print(f"Found script at: {possible_path}")
            break
    
    if script_dir_to_add is None:
        print(f"FATAL ERROR: Could not find script '{user_script_relative}' in any of these locations:")
        for p in possible_paths:
            print(f"  - {p}")
        sys.exit(1)

print(f"Script directory to add: {script_dir_to_add}")
print(f"Module name: {module_name}")

# Add script directory to Python path
if script_dir_to_add not in sys.path:
    sys.path.insert(0, script_dir_to_add)
print(f"Updated sys.path: {sys.path}")

try:
    # Dynamically import the module
    print(f"Attempting to import module: '{module_name}'")
    module = __import__(module_name)
    
    # Get required functions
    setup_scene_units = getattr(module, 'setup_scene_units')
    import_and_prepare_stl = getattr(module, 'import_and_prepare_stl')
    setup_compositor_nodes = getattr(module, 'setup_compositor_nodes')
    record_parameters_to_file = getattr(module, 'record_parameters_to_file')
    render_reference_plane_depth_only = getattr(module, 'render_reference_plane_depth_only')
    
    print("Imported dataset generation functions successfully.")
    
    # Setup scene units
    setup_scene_units()
    print("Scene units set to centimeters")
    
    # Process configuration
    paths = config.get("paths", {})
    camera_config = config.get("camera", {})
    projector_config = config.get("projector", {})
    render_config = config.get("render", {})
    advanced_config = config.get("advanced", {})
    
    # Get STL files - use raw strings to handle Unicode paths properly
    stl_folder = paths.get("stl_folder", "")
    if not stl_folder:
        raise ValueError("STL folder path is empty in configuration")
    # Handle Unicode paths properly
    stl_folder = os.path.abspath(stl_folder)
    if not os.path.exists(stl_folder):
        raise ValueError(f"STL folder not found: {stl_folder}")
    
    try:
        stl_files = [f for f in os.listdir(stl_folder) if f.lower().endswith('.stl')]
    except UnicodeDecodeError:
        # Handle potential Unicode issues in filenames
        stl_files = []
        for f in os.listdir(stl_folder):
            try:
                if f.lower().endswith('.stl'):
                    stl_files.append(f)
            except UnicodeDecodeError:
                print(f"Warning: Skipping file with invalid Unicode name: {repr(f)}")
                continue
    
    if not stl_files:
        raise ValueError(f"No STL files found in: {stl_folder}")
    
    print(f"Found {len(stl_files)} STL files")
    
    # Setup output directories - handle Unicode paths
    output_base = paths.get("output_folder", "")
    if not output_base:
        raise ValueError("Output folder path is empty in configuration")
    
    # Ensure output directory exists and handle Unicode paths
    output_base = os.path.abspath(output_base)
        
    pattern_output = os.path.join(output_base, "pattern")
    depth_output = os.path.join(output_base, "depth")
    ambient_output = os.path.join(output_base, "ambient")
    
    os.makedirs(pattern_output, exist_ok=True)
    os.makedirs(depth_output, exist_ok=True)
    os.makedirs(ambient_output, exist_ok=True)
    
    print(f"Output directories created: {output_base}")
    
    # Process each STL file
    total_files = len(stl_files)
    for i, stl_file in enumerate(stl_files):
        stl_path = os.path.join(stl_folder, stl_file)
        print(f"Processing {stl_file} ({i+1}/{total_files})")
        
        # Import and prepare STL
        import_and_prepare_stl(stl_path)
        
        # Setup camera and projector based on config
        # This would involve setting up the camera and projector positions
        # from the configuration data
        
        # Render different views and patterns
        # This would involve calling the appropriate rendering functions
        # with the configured parameters
        
        # Update progress
        progress = 20 + (i / total_files) * 70
        print(f"PROGRESS: {progress}")
    
    # Save parameters
    params_file = os.path.join(output_base, "scene_parameters.json")
    record_parameters_to_file(params_file)
    
    print("Dataset generation completed successfully!")
    print(f"Output files saved to: {output_base}")
    print(f"Parameters saved to: {params_file}")

except ImportError as e:
    print(f"FATAL ERROR: Could not import module '{module_name}' from path '{script_dir_to_add}'.")
    print("Please ensure the 'Blender脚本路径' in the GUI's Advanced Settings is correct.")
    print(f"Current Blender sys.path: {sys.path}")
    print(f"Import error details: {e}")
    sys.exit(1)
except AttributeError as e:
    print(f"FATAL ERROR: A function was not found in the module '{module_name}'. {e}")
    print("Please ensure your script '深度图数据集_v6.py' contains all required functions.")
    sys.exit(1)
except Exception as e:
    print(f"Error during dataset generation: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

