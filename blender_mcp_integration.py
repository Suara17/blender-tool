"""
Blender MCP Integration Module
Handles communication between GUI and Blender MCP tools
"""

import subprocess
import json
import os
import tempfile
import time
import traceback
from pathlib import Path


class BlenderMCPIntegration:
    """Handles integration with Blender MCP tools"""
    
    def __init__(self, blender_path="blender"):
        self.blender_path = blender_path
        self.temp_config_file = None
    
    def _check_blender_executable(self):
        """Check if Blender executable exists and is accessible"""
        try:
            # Check if it's a full path
            if os.path.isabs(self.blender_path):
                return os.path.exists(self.blender_path) and os.path.isfile(self.blender_path)
            
            # Check if it's in system PATH
            result = subprocess.run([self.blender_path, "--version"], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception as e:
            print(f"Error checking Blender executable: {e}")
            return False
    
    def generate_dataset(self, config, progress_callback=None):
        """
        Generate dataset using Blender MCP tools
        
        Args:
            config: Configuration dictionary with all parameters
            progress_callback: Function to call with progress updates
        
        Returns:
            dict: Results and status information
        """
        import logging
        import sys  # 添加sys模块导入
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("=== 开始生成数据集 ===")
            logger.info(f"配置参数: {json.dumps(config, ensure_ascii=False, indent=2)}")
            
            # Map GUI config keys to Blender script expected keys
            logger.info("映射配置参数键名...")
            mapped_config = self._map_config_keys(config)
            logger.info(f"映射后配置参数: {json.dumps(mapped_config, ensure_ascii=False, indent=2)}")
            
            # Create temporary config file with UTF-8 encoding
            logger.info("创建临时配置文件...")
            self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
            json.dump(mapped_config, self.temp_config_file, indent=2, ensure_ascii=False)
            self.temp_config_file.close()
            logger.info(f"临时配置文件已创建: {self.temp_config_file.name}")
            
            if progress_callback:
                progress_callback(10, "正在准备Blender环境...")
            
            # Prepare Blender script that uses MCP tools
            logger.info("生成Blender脚本...")
            blender_script = self._create_blender_script(self.temp_config_file.name)
            logger.info(f"Blender脚本生成完成 ({len(blender_script)} 字符)")
            
            # 保存生成的脚本用于调试
            script_debug_path = "debug_generated_script.py"
            with open(script_debug_path, 'w', encoding='utf-8') as f:
                f.write(blender_script)
            logger.info(f"生成的脚本已保存到: {script_debug_path}")
            
            if progress_callback:
                progress_callback(20, "正在启动Blender...")
            
            # Execute Blender with the script
            logger.info("执行Blender脚本...")
            result = self._execute_blender_script(blender_script, progress_callback)
            
            logger.info(f"Blender执行结果: {result}")
            
            return {
                "success": True,
                "message": "数据集生成完成",
                "output_files": result.get("output_files", []),
                "parameters_file": result.get("parameters_file", "")
            }
            
        except Exception as e:
            # 确保traceback在当前作用域中可用
            import traceback
            logger.error(f"数据集生成失败: {e}")
            try:
                logger.error(f"错误详情: {traceback.format_exc()}")
            except Exception as tb_error:
                logger.error(f"获取错误详情失败: {tb_error}")
            return {
                "success": False,
                "message": f"生成失败: {str(e)}",
                "error": str(e),
                "traceback": traceback.format_exc() if hasattr(traceback, 'format_exc') else str(e)
            }
        finally:
            # Clean up temporary file
            if self.temp_config_file and os.path.exists(self.temp_config_file.name):
                os.unlink(self.temp_config_file.name)
                logger.info("临时配置文件已清理")

    def _map_config_keys(self, config):
        """Map GUI config keys to Blender script expected keys"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Create a copy of the config to avoid modifying the original
        mapped_config = {}
        
        # Copy all sections as-is first
        for key, value in config.items():
            mapped_config[key] = value
            
        # Map paths section keys
        if "paths" in mapped_config:
            paths = mapped_config["paths"]
            # Map GUI keys to script expected keys
            if "stl_folder" in paths:
                mapped_config["stl_model_path"] = paths["stl_folder"]
            if "pattern_folder" in paths:
                mapped_config["pattern_path"] = paths["pattern_folder"]
            if "output_folder" in paths:
                mapped_config["output_path"] = paths["output_folder"]
                
            logger.info("路径键名映射完成")
        
        # Map camera parameters
        if "camera" in mapped_config:
            camera = mapped_config["camera"]
            if "position" in camera and len(camera["position"]) == 3:
                mapped_config["camera_x"] = camera["position"][0]
                mapped_config["camera_y"] = camera["position"][1]
                mapped_config["camera_z"] = camera["position"][2]
            if "rotation" in camera and len(camera["rotation"]) == 3:
                mapped_config["camera_rot_x"] = camera["rotation"][0]
                mapped_config["camera_rot_y"] = camera["rotation"][1]
                mapped_config["camera_rot_z"] = camera["rotation"][2]
            if "focal_length" in camera:
                mapped_config["focal_length"] = camera["focal_length"]
            if "clip_start" in camera:
                mapped_config["clip_start"] = camera["clip_start"]
            if "clip_end" in camera:
                mapped_config["clip_end"] = camera["clip_end"]
        
        # Map projector parameters
        if "projector" in mapped_config:
            projector = mapped_config["projector"]
            if "position" in projector and len(projector["position"]) == 3:
                mapped_config["proj_x"] = projector["position"][0]
                mapped_config["proj_y"] = projector["position"][1]
                mapped_config["proj_z"] = projector["position"][2]
            if "power" in projector:
                mapped_config["projector_energy"] = projector["power"]
            if "power_drift" in projector:
                mapped_config["proj_power_drift"] = projector["power_drift"]
            if "use_discrete_power" in projector:
                mapped_config["use_discrete_power"] = projector["use_discrete_power"]
            if "fov" in projector:
                mapped_config["fov"] = projector["fov"]
        
        # Map render parameters
        if "render" in mapped_config:
            render = mapped_config["render"]
            if "resolution" in render and len(render["resolution"]) == 2:
                mapped_config["resolution_x"] = render["resolution"][0]
                mapped_config["resolution_y"] = render["resolution"][1]
            if "engine" in render:
                mapped_config["render_engine"] = render["engine"]
            if "samples" in render:
                mapped_config["render_samples"] = render["samples"]
            if "ambient_base" in render:
                mapped_config["ambient_base"] = render["ambient_base"]
            if "ambient_variation" in render:
                mapped_config["ambient_variation"] = render["ambient_variation"]
        
        # Map advanced parameters
        if "advanced" in mapped_config:
            advanced = mapped_config["advanced"]
            if "stl_max_size" in advanced:
                mapped_config["stl_max_size"] = advanced["stl_max_size"]
            if "rotation_angles" in advanced:
                mapped_config["rotation_angles"] = advanced["rotation_angles"]
            # Also map blender_path and script_path for reference
            if "blender_path" in advanced:
                mapped_config["blender_path"] = advanced["blender_path"]
            if "script_path" in advanced:
                mapped_config["script_path"] = advanced["script_path"]
        
        logger.info("所有参数键名映射完成")
        return mapped_config
    
    def _create_blender_script(self, config_file_path):
        """Create a Blender script that dynamically uses the user-provided script_path."""
        
        # Step 1: Pre-read the configuration to get the user's script path.
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        user_script_path_str = config.get("advanced", {}).get("script_path", "深度图数据集_v6.py")
        
        # Step 2: Use pathlib to safely extract the script's directory and module name.
        user_script_path = Path(user_script_path_str)
        script_directory = str(user_script_path.parent).replace('\\', '/')
        module_name = user_script_path.stem

        # Step 3: Extract paths from config for proper escaping
        paths = config.get("paths", {})
        stl_folder = paths.get("stl_folder", "")
        pattern_folder = paths.get("pattern_folder", "")
        output_folder = paths.get("output_folder", "")
        hdri_path = paths.get("hdri_path", "")

        # Step 4: Generate the script content that will be executed by Blender.
        # Note the use of double curly braces {{...}} for nested f-strings.
        script_content = f'''
import bpy
import json
import os
import sys
from pathlib import Path

print("=== Blender Dataset Generation Started ===")
print(f"Python version: {{{{sys.version}}}}")
print(f"Blender version: {{{{bpy.app.version_string}}}}")

# Load configuration
config_path = r"{config_file_path}"
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Configuration loaded from: {{{{config_path}}}}")
except Exception as e:
    print(f"FATAL ERROR: Failed to load config from {{{{config_path}}}}: {{{{e}}}}")
    sys.exit(1)

# Get the directory of this script
this_script_dir = Path(__file__).parent
print(f"This script directory: {{{{this_script_dir}}}}")

# Handle script path from config
user_script_relative = r"{user_script_path_str}"
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
            print(f"Found script at: {{{{possible_path}}}}")
            break
    
    if script_dir_to_add is None:
        print(f"FATAL ERROR: Could not find script '{{user_script_relative}}' in any of these locations:")
        for p in possible_paths:
            print(f"  - {{{{p}}}}")
        sys.exit(1)

print(f"Script directory to add: {{{{script_dir_to_add}}}}")
print(f"Module name: {{{{module_name}}}}")

# Add script directory to Python path
if script_dir_to_add not in sys.path:
    sys.path.insert(0, script_dir_to_add)
print(f"Updated sys.path: {{{{sys.path}}}}")

try:
    # Dynamically import the module
    print(f"Attempting to import module: '{{{{module_name}}}}'")
    user_module = __import__(module_name)
    
    # Execute the main script logic with config path
    print("Executing main script logic with config path...")
    user_module.main_script_logic(config_path)

except ImportError as e:
    print(f"FATAL ERROR: Could not import module '{{{{module_name}}}}' from path '{{{{script_dir_to_add}}}}'.")
    print("Please ensure the 'Blender脚本路径' in the GUI's Advanced Settings is correct.")
    print(f"Current Blender sys.path: {{{{sys.path}}}}")
    print(f"Import error details: {{{{e}}}}")
    sys.exit(1)
except AttributeError as e:
    print(f"FATAL ERROR: A function was not found in the module '{{{{module_name}}}}'. {{{{e}}}}")
    print("Please ensure your script '深度图数据集_v6.py' contains all required functions.")
except Exception as e:
    print(f"Error during dataset generation: {{{{str(e)}}}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

'''
        return script_content
    
    def _execute_blender_script(self, script_content, progress_callback=None):
        """Execute Blender with the given script with detailed logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("开始执行Blender脚本...")
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            script_path = f.name
        logger.info(f"临时脚本文件已创建: {script_path}")
        
        try:
            # Verify Blender executable exists
            logger.info(f"检查Blender可执行文件: {self.blender_path}")
            if not self._check_blender_executable():
                raise FileNotFoundError(f"Blender executable not found: {self.blender_path}")
            logger.info("Blender可执行文件检查通过")
            
            # Test if Blender can be executed
            try:
                test_process = subprocess.run([self.blender_path, "--version"], 
                                            capture_output=True, text=True, timeout=10)
                if test_process.returncode != 0:
                    logger.warning(f"Blender版本检查返回非零代码: {test_process.returncode}")
                    logger.warning(f"stderr输出: {test_process.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning("Blender版本检查超时")
            except Exception as test_e:
                logger.warning(f"Blender版本检查失败: {test_e}")
            
            # Prepare command
            cmd = [
                self.blender_path,
                "--background",  # Run in background mode
                "--python", script_path
                # Removed --factory-startup to allow loading of user addons
            ]
            
            logger.info(f"执行Blender命令: {' '.join(cmd)}")
            
            if progress_callback:
                progress_callback(30, "正在执行Blender脚本...")
            
            # Execute Blender
            logger.info("启动Blender进程...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,  # Use text mode
                encoding='utf-8',  # Specify UTF-8 encoding to avoid decode errors
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor progress
            output_files = []
            parameters_file = ""
            
            logger.info("开始监控Blender输出...")
            while True:
                output_line = process.stdout.readline()
                if output_line == '' and process.poll() is not None:
                    break
                if output_line:
                    output_line = output_line.strip()
                    logger.info(f"Blender输出: {output_line}")
                    print(f"Blender: {output_line}")
                    
                    # Parse progress information
                    if "PROGRESS:" in output_line:
                        try:
                            progress = float(output_line.split("PROGRESS:")[1].strip())
                            if progress_callback:
                                progress_callback(progress, f"处理进度: {progress:.1f}%")
                        except Exception as e:
                            logger.warning(f"解析进度信息失败: {e}")
                    
                    # Parse output file information
                    elif "Output files saved to:" in output_line:
                        output_dir = output_line.split("Output files saved to:")[1].strip()
                        logger.info(f"检测到输出目录: {output_dir}")
                        # Collect generated files
                        if os.path.exists(output_dir):
                            for root, dirs, files in os.walk(output_dir):
                                for file in files:
                                    if file.endswith(('.png', '.exr', '.json')):
                                        full_path = os.path.join(root, file)
                                        output_files.append(full_path)
                                        logger.info(f"发现输出文件: {full_path}")
                    
                    elif "Parameters saved to:" in output_line:
                        parameters_file = output_line.split("Parameters saved to:")[1].strip()
                        logger.info(f"检测到参数文件: {parameters_file}")
            
            # Get remaining output and error messages
            try:
                remaining_output = process.stdout.read()
                if remaining_output:
                    for line in remaining_output.split('\n'):
                        if line.strip():
                            logger.info(f"Blender剩余输出: {line.strip()}")
                            
                stderr_output = process.stderr.read()
                if stderr_output:
                    for line in stderr_output.split('\n'):
                        if line.strip():
                            logger.error(f"Blender错误输出: {line.strip()}")
                            
            except Exception as e:
                logger.warning(f"读取剩余输出时出错: {e}")
            
            # Get return code - ensure process has finished
            try:
                return_code = process.wait(timeout=10)  # Wait for process to finish
            except subprocess.TimeoutExpired:
                logger.error("Blender进程超时")
                process.kill()
                return_code = -1
            
            logger.info(f"Blender进程返回码: {return_code}")
            
            if return_code != 0:
                error_msg = f"Blender execution failed with return code {return_code}"
                # 获取stderr输出，如果可用的话
                try:
                    stderr_output = process.stderr.read()
                    if stderr_output.strip():
                        error_msg += f": {stderr_output.strip()}"
                except Exception:
                    pass  # 如果无法读取stderr，就忽略
                    
                logger.error(f"Blender执行失败: {error_msg}")
                # Check for specific error patterns and provide better guidance
                if "bpy.ops.projector.create" in error_msg and "not found" in error_msg:
                    error_msg += "\n\n检测到投影仪插件错误。请确保已安装并启用了 'Projectors' 插件。"
                    error_msg += "\n访问 https://github.com/eliemichel/Projectors 获取插件安装说明。"
                elif "投影仪插件不可用" in error_msg:
                    error_msg += "\n\n检测到投影仪插件不可用错误。请确保已安装并启用了 'Projectors' 插件。"
                    error_msg += "\n访问 https://github.com/eliemichel/Projectors 获取插件安装说明。"
                raise Exception(error_msg)
            
            logger.info(f"Blender执行完成，发现 {len(output_files)} 个输出文件")
            logger.info(f"参数文件: {parameters_file}")
            
            if progress_callback:
                progress_callback(95, "正在完成...")
            
            return {
                "output_files": output_files,
                "parameters_file": parameters_file
            }
            
        except FileNotFoundError as e:
            logger.error(f"Blender可执行文件未找到: {e}")
            raise FileNotFoundError(f"Blender executable not found: {self.blender_path}. Please check the path in Advanced Settings.")
        except subprocess.SubprocessError as e:
            logger.error(f"Blender进程执行错误: {e}")
            raise Exception(f"Blender execution error: {e}. Please check if Blender is properly installed and accessible.")
        except Exception as e:
            # 确保traceback在当前作用域中可用
            import traceback
            logger.error(f"执行Blender脚本时出错: {e}")
            try:
                logger.error(f"错误详情: {traceback.format_exc()}")
            except Exception as tb_error:
                logger.error(f"获取错误详情失败: {tb_error}")
            raise
        finally:
            # Clean up temporary script file
            if os.path.exists(script_path):
                try:
                    os.unlink(script_path)
                    logger.info("临时脚本文件已清理")
                except Exception as e:
                    logger.warning(f"清理临时脚本文件失败: {e}")
    
    def test_blender_connection(self):
        """Test if Blender is accessible and working"""
        script_path = '' # Initialize to ensure it exists for the 'finally' block
        try:
            # This is the simple script that Blender will execute
            test_script = '''import bpy
import sys
print("Blender version:", bpy.app.version_string)
print("Python version:", sys.version)
print("Connection test successful")
'''
            
            # Create a temporary file to hold the script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(test_script)
                script_path = f.name
            
            # Prepare the command to run Blender in the background with the script
            cmd = [self.blender_path, "--background", "--python", script_path]
            
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Check the result
            if result.returncode == 0 and "Connection test successful" in result.stdout:
                return True, "Blender connection successful"
            else:
                error_message = result.stderr if result.stderr else "Unknown error during script execution."
                return False, f"Blender test failed: {error_message}"
                
        except subprocess.TimeoutExpired:
            return False, "Blender test timed out"
        except FileNotFoundError:
            return False, f"Blender executable not found. Please check the path in 'Advanced Settings': {self.blender_path}"
        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}"
        finally:
            # Clean up the temporary script file
            if script_path and os.path.exists(script_path):
                os.unlink(script_path)

# Example usage function
def create_sample_dataset():
    """Example function to demonstrate usage"""
    
    # Configuration similar to what the GUI would generate
    config = {
        "paths": {
            "stl_folder": r"E:\\zr_network\\blender\\Thingi10K\\selectmodel",
            "pattern_folder": r"E:\\zr_network\\blender\\composite_pattern\\1",
            "output_folder": r"E:\\zr_network\\blender\\output",
            "hdri_path": r"E:\\zr_network\\blender\\HDRI\\brown_photostudio_02_4k.hdr"
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
            "samples": 512,
            "ambient_base": 0.5,
            "ambient_variation": 0.1
        },
        "advanced": {
            "stl_max_size": 150.0,
            "rotation_angles": [0, 45, 90, 135, 180, 225, 270, 315],
            "blender_path": "blender",
            "script_path": "深度图数据集_v6.py"
        }
    }
    
    def progress_callback(progress, message):
        print(f"Progress: {progress:.1f}% - {message}")
    
    # Create integration instance
    integration = BlenderMCPIntegration()
    
    # Test connection first
    success, message = integration.test_blender_connection()
    print(f"Connection test: {message}")
    
    if success:
        # Generate dataset
        result = integration.generate_dataset(config, progress_callback)
        print(f"Dataset generation result: {result}")
    
if __name__ == "__main__":
    create_sample_dataset()