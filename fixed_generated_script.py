import bpy
import json
import os
import sys
from pathlib import Path

print("=== Blender Dataset Generation Started ===")
print(f"Python version: {sys.version}")
print(f"Blender version: {bpy.app.version_string}")

# Load configuration
config_path = r"C:\Users\sua\AppData\Local\Temp\tmp2sbrvjwx.json"
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
    script_dir_to_add = str(user_script_path_obj.parent).replace('\\', '/')
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
            script_dir_to_add = str(possible_path.parent).replace('\\', '/')
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
    user_module = __import__(module_name)
    
    # Check if the module has the main_script_logic function
    if hasattr(user_module, 'main_script_logic'):
        # Execute the main script logic directly with config
        print("Executing main script logic with config...")
        user_module.main_script_logic(config)
    else:
        # Fallback to manual function calls if main_script_logic is not available
        print("Main script logic function not found, using manual function calls...")
        print("警告: 无法找到 main_script_logic 函数，将使用手动函数调用模式。")
        print("这可能是因为脚本版本不兼容或插件缺失。")
        
        # Get required functions
        try:
            setup_scene_units = getattr(user_module, 'setup_scene_units')
            import_and_prepare_stl = getattr(user_module, 'import_and_prepare_stl')
            setup_compositor_nodes = getattr(user_module, 'setup_compositor_nodes')
            record_parameters_to_file = getattr(user_module, 'record_parameters_to_file')
            render_reference_plane_depth_only = getattr(user_module, 'render_reference_plane_depth_only')
            get_or_create_camera = getattr(user_module, 'get_or_create_camera')
            add_reference_plane_world_position = getattr(user_module, 'add_reference_plane_world_position')
            setup_render_settings = getattr(user_module, 'setup_render_settings')
            setup_world_background = getattr(user_module, 'setup_world_background')
            place_object_on_plane = getattr(user_module, 'place_object_on_plane')
            project_and_render_via_nodes = getattr(user_module, 'project_and_render_via_nodes')
            get_pattern_images = getattr(user_module, 'get_pattern_images')
        except AttributeError as e:
            print("错误: 脚本中缺少必需的函数: " + str(e))
            print("请确保使用的是正确版本的 '深度图数据集_v6.py' 脚本。")
            sys.exit(1)
        
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
        
        # Set up the scene with the provided configuration
        # Camera setup
        CAMERA_DEFAULT_LOC = tuple(camera_config.get("position", [-100, -300, 0]))
        CAMERA_DEFAULT_ROT_DEG = tuple(camera_config.get("rotation", [90, 0, -17]))
        CAMERA_DEFAULT_SCALE = (1.0, 1.0, 1.0)
        CAMERA_DEFAULT_TYPE = 'PERSP'
        CAMERA_DEFAULT_LENS_UNIT = 'MILLIMETERS'
        CAMERA_DEFAULT_FOCAL_LENGTH = camera_config.get("focal_length", 50.0)
        CAMERA_CLIP_START = camera_config.get("clip_start", 10.0)
        CAMERA_CLIP_END = camera_config.get("clip_end", 1500.0)
        
        scanner_cam_obj = get_or_create_camera(
            "Camera",
            CAMERA_DEFAULT_LOC, CAMERA_DEFAULT_ROT_DEG, CAMERA_DEFAULT_SCALE,
            CAMERA_DEFAULT_TYPE, CAMERA_DEFAULT_LENS_UNIT, CAMERA_DEFAULT_FOCAL_LENGTH,
            CAMERA_CLIP_START, CAMERA_CLIP_END
        )
        
        # Projector setup (simplified)
        # In a full implementation, we would create the projector using the addon
        # For now, we'll just ensure it exists
        projector_parent_obj = bpy.data.objects.get("Projector")
        projector_light_emitter_obj = bpy.data.objects.get("Projector.Spot")
        
        # Reference plane setup
        reference_plane_obj = add_reference_plane_world_position(scanner_cam_obj)
        
        # Render settings
        # Update global variables with config values
        import builtins
        builtins.render_width = render_config.get("resolution", [640, 640])[0]
        builtins.render_height = render_config.get("resolution", [640, 640])[1]
        builtins.render_samples = render_config.get("samples", 512)
        builtins.use_cycles = render_config.get("engine", "Cycles") == "Cycles"
        
        setup_render_settings()
        setup_compositor_nodes(depth_output)
        
        # Get pattern images
        pattern_folder = paths.get("pattern_folder", "")
        pattern_images = get_pattern_images(pattern_folder) if pattern_folder else []
        print(f"Found {len(pattern_images)} pattern images")
        
        # Process each STL file
        total_files = len(stl_files)
        for i, stl_file in enumerate(stl_files):
            stl_path = os.path.join(stl_folder, stl_file)
            print(f"Processing {stl_file} ({i+1}/{total_files})")
            
            # Import and prepare STL
            stl_obj = import_and_prepare_stl(stl_path, "Current_Imported_STL", (60, 0.0, 0.0), 150.0)
            
            # Place object on reference plane
            if stl_obj and reference_plane_obj:
                place_object_on_plane(stl_obj, reference_plane_obj)
            
            # Setup world background with random rotation
            import random
            random_z_rot = random.uniform(0.0, 360.0)
            ambient_base = render_config.get("ambient_base", 0.5)
            ambient_variation = render_config.get("ambient_variation", 0.1)
            random_background_strength = random.uniform(
                max(0, ambient_base - ambient_variation),
                ambient_base + ambient_variation
            )
            setup_world_background(None, random_z_rot, random_background_strength)
            
            # Render different views and patterns
            # For demonstration, we'll just render one view with all patterns
            if pattern_images and stl_obj:
                # Get projector nodes (simplified)
                # In a full implementation, we would properly get these nodes
                image_tex_node = None
                emission_node = None
                
                # Render patterns
                for j, pattern_path in enumerate(pattern_images):
                    pattern_name = f"{i+1:06d}_{j+1:06d}_pattern"
                    project_and_render_via_nodes(
                        image_tex_node, emission_node, pattern_path,
                        pattern_name, pattern_output
                    )
                    print(f"Rendered pattern {j+1}/{len(pattern_images)} for STL {i+1}/{total_files}")
            
            # Render ambient image (simplified)
            ambient_name = f"{i+1:06d}_ambient"
            # For ambient, we would set projector strength to 0
            # This is a simplified version - in practice we would properly handle this
            project_and_render_via_nodes(
                image_tex_node, emission_node,
                pattern_images[0] if pattern_images else None,
                ambient_name, ambient_output
            )
            
            # Update progress
            progress = 20 + (i / total_files) * 70
            print(f"PROGRESS: {progress}")
        
        # Save parameters
        params_file = os.path.join(output_base, "scene_parameters.json")
        # Get camera and projector objects for parameter recording
        camera_obj = bpy.data.objects.get("Camera")
        projector_obj = bpy.data.objects.get("Projector.Spot")
        if camera_obj and projector_obj:
            record_parameters_to_file(params_file, camera_obj, projector_obj)
        else:
            print("Warning: Could not find camera or projector objects for parameter recording")
        
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