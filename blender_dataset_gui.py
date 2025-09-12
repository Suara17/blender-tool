import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import threading
import traceback
import logging
from pathlib import Path
from blender_mcp_integration import BlenderMCPIntegration

class BlenderDatasetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blender结构光数据集生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置日志
        self.setup_logging()
        
        # Initialize MCP integration
        self.mcp_integration = None
        self.generation_thread = None
        self.is_generating = False
        
        # Configure style
        self.setup_style()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_paths_tab()
        self.create_camera_tab()
        self.create_projector_tab()
        self.create_render_tab()
        self.create_advanced_tab()
        
        # Create control buttons
        self.create_control_frame()
        
        # Load default values
        self.load_defaults()
        
        # Try to load default configuration file
        self.load_default_config()
        
        # Test Blender connection on startup
        self.test_blender_connection()
    
    def setup_logging(self):
        """设置日志记录"""
        # 创建logs目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 设置日志文件
        log_file = os.path.join(log_dir, "blender_dataset_gui.log")
        
        # 配置日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Blender Dataset GUI 启动 ===")
        self.logger.info(f"日志文件: {log_file}")
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        
    def create_paths_tab(self):
        paths_frame = ttk.Frame(self.notebook)
        self.notebook.add(paths_frame, text="路径设置")
        
        # Input/Output paths
        ttk.Label(paths_frame, text="输入输出路径设置", style='Header.TLabel').grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
        
        # STL models folder
        ttk.Label(paths_frame, text="STL模型文件夹:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.stl_folder_var = tk.StringVar()
        ttk.Entry(paths_frame, textvariable=self.stl_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="浏览", command=lambda: self.browse_folder(self.stl_folder_var)).grid(row=1, column=2, padx=5, pady=5)
        
        # Pattern images folder
        ttk.Label(paths_frame, text="图案图像文件夹:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.pattern_folder_var = tk.StringVar()
        ttk.Entry(paths_frame, textvariable=self.pattern_folder_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="浏览", command=lambda: self.browse_folder(self.pattern_folder_var)).grid(row=2, column=2, padx=5, pady=5)
        
        # Output directories
        ttk.Label(paths_frame, text="输出文件夹:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.output_folder_var = tk.StringVar()
        ttk.Entry(paths_frame, textvariable=self.output_folder_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="浏览", command=lambda: self.browse_folder(self.output_folder_var)).grid(row=3, column=2, padx=5, pady=5)
        
        # HDRI environment map
        ttk.Label(paths_frame, text="HDRI环境贴图:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.hdri_path_var = tk.StringVar()
        ttk.Entry(paths_frame, textvariable=self.hdri_path_var, width=50).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(paths_frame, text="浏览", command=lambda: self.browse_file(self.hdri_path_var, "HDR文件", "*.hdr")).grid(row=4, column=2, padx=5, pady=5)
    
    def create_camera_tab(self):
        camera_frame = ttk.Frame(self.notebook)
        self.notebook.add(camera_frame, text="相机设置")
        
        ttk.Label(camera_frame, text="相机参数设置", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Camera position
        ttk.Label(camera_frame, text="相机位置 (cm):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        camera_pos_frame = ttk.Frame(camera_frame)
        camera_pos_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.camera_x_var = tk.StringVar(value="-100")
        self.camera_y_var = tk.StringVar(value="-300")
        self.camera_z_var = tk.StringVar(value="0")
        
        ttk.Label(camera_pos_frame, text="X:").pack(side='left', padx=2)
        ttk.Entry(camera_pos_frame, textvariable=self.camera_x_var, width=8).pack(side='left', padx=2)
        ttk.Label(camera_pos_frame, text="Y:").pack(side='left', padx=2)
        ttk.Entry(camera_pos_frame, textvariable=self.camera_y_var, width=8).pack(side='left', padx=2)
        ttk.Label(camera_pos_frame, text="Z:").pack(side='left', padx=2)
        ttk.Entry(camera_pos_frame, textvariable=self.camera_z_var, width=8).pack(side='left', padx=2)
        
        # Camera rotation
        ttk.Label(camera_frame, text="相机旋转 (度):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        camera_rot_frame = ttk.Frame(camera_frame)
        camera_rot_frame.grid(row=2, column=1, padx=5, pady=5)
        
        self.camera_rot_x_var = tk.StringVar(value="90")
        self.camera_rot_y_var = tk.StringVar(value="0")
        self.camera_rot_z_var = tk.StringVar(value="-17")
        
        ttk.Label(camera_rot_frame, text="X:").pack(side='left', padx=2)
        ttk.Entry(camera_rot_frame, textvariable=self.camera_rot_x_var, width=8).pack(side='left', padx=2)
        ttk.Label(camera_rot_frame, text="Y:").pack(side='left', padx=2)
        ttk.Entry(camera_rot_frame, textvariable=self.camera_rot_y_var, width=8).pack(side='left', padx=2)
        ttk.Label(camera_rot_frame, text="Z:").pack(side='left', padx=2)
        ttk.Entry(camera_rot_frame, textvariable=self.camera_rot_z_var, width=8).pack(side='left', padx=2)
        
        # Focal length
        ttk.Label(camera_frame, text="焦距 (mm):").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.focal_length_var = tk.StringVar(value="50.0")
        ttk.Entry(camera_frame, textvariable=self.focal_length_var, width=15).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Clip distances
        ttk.Label(camera_frame, text="裁剪距离:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        clip_frame = ttk.Frame(camera_frame)
        clip_frame.grid(row=4, column=1, padx=5, pady=5)
        
        self.clip_start_var = tk.StringVar(value="10.0")
        self.clip_end_var = tk.StringVar(value="1500.0")
        
        ttk.Label(clip_frame, text="起始:").pack(side='left', padx=2)
        ttk.Entry(clip_frame, textvariable=self.clip_start_var, width=8).pack(side='left', padx=2)
        ttk.Label(clip_frame, text="结束:").pack(side='left', padx=2)
        ttk.Entry(clip_frame, textvariable=self.clip_end_var, width=8).pack(side='left', padx=2)
    
    def create_projector_tab(self):
        projector_frame = ttk.Frame(self.notebook)
        self.notebook.add(projector_frame, text="投影仪设置")
        
        ttk.Label(projector_frame, text="投影仪参数设置", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Projector position
        ttk.Label(projector_frame, text="投影仪位置 (cm):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        proj_pos_frame = ttk.Frame(projector_frame)
        proj_pos_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.proj_x_var = tk.StringVar(value="100")
        self.proj_y_var = tk.StringVar(value="-300")
        self.proj_z_var = tk.StringVar(value="0")
        
        ttk.Label(proj_pos_frame, text="X:").pack(side='left', padx=2)
        ttk.Entry(proj_pos_frame, textvariable=self.proj_x_var, width=8).pack(side='left', padx=2)
        ttk.Label(proj_pos_frame, text="Y:").pack(side='left', padx=2)
        ttk.Entry(proj_pos_frame, textvariable=self.proj_y_var, width=8).pack(side='left', padx=2)
        ttk.Label(proj_pos_frame, text="Z:").pack(side='left', padx=2)
        ttk.Entry(proj_pos_frame, textvariable=self.proj_z_var, width=8).pack(side='left', padx=2)
        
        # Projector power
        ttk.Label(projector_frame, text="投影仪功率 (W):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        power_frame = ttk.Frame(projector_frame)
        power_frame.grid(row=2, column=1, padx=5, pady=5)
        
        self.proj_power_var = tk.StringVar(value="4.5")
        ttk.Label(power_frame, text="基准:").pack(side='left', padx=2)
        ttk.Entry(power_frame, textvariable=self.proj_power_var, width=8).pack(side='left', padx=2)
        
        self.proj_power_drift_var = tk.StringVar(value="0.5")
        ttk.Label(power_frame, text="变化范围:").pack(side='left', padx=2)
        ttk.Entry(power_frame, textvariable=self.proj_power_drift_var, width=8).pack(side='left', padx=2)
        
        # Discrete power levels
        self.use_discrete_power_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(projector_frame, text="使用离散功率级别", variable=self.use_discrete_power_var).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Field of view
        ttk.Label(projector_frame, text="视场角 (度):").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.fov_var = tk.StringVar(value="60")
        ttk.Entry(projector_frame, textvariable=self.fov_var, width=15).grid(row=4, column=1, padx=5, pady=5, sticky='w')
    
    def create_render_tab(self):
        render_frame = ttk.Frame(self.notebook)
        self.notebook.add(render_frame, text="渲染设置")
        
        ttk.Label(render_frame, text="渲染参数设置", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Resolution
        ttk.Label(render_frame, text="分辨率:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        res_frame = ttk.Frame(render_frame)
        res_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.render_width_var = tk.StringVar()
        self.render_height_var = tk.StringVar()
        
        ttk.Label(res_frame, text="宽度:").pack(side='left', padx=2)
        ttk.Entry(res_frame, textvariable=self.render_width_var, width=8).pack(side='left', padx=2)
        ttk.Label(res_frame, text="高度:").pack(side='left', padx=2)
        ttk.Entry(res_frame, textvariable=self.render_height_var, width=8).pack(side='left', padx=2)
        
        # Render engine
        ttk.Label(render_frame, text="渲染引擎:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.render_engine_var = tk.StringVar()
        engine_combo = ttk.Combobox(render_frame, textvariable=self.render_engine_var, values=["Cycles", "EEVEE"], width=15)
        engine_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Samples
        ttk.Label(render_frame, text="采样数:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.samples_var = tk.StringVar()
        ttk.Entry(render_frame, textvariable=self.samples_var, width=15).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Ambient lighting
        ttk.Label(render_frame, text="环境光照强度:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        ambient_frame = ttk.Frame(render_frame)
        ambient_frame.grid(row=4, column=1, padx=5, pady=5)
        
        self.ambient_base_var = tk.StringVar()
        self.ambient_var_var = tk.StringVar()
        
        ttk.Label(ambient_frame, text="基准:").pack(side='left', padx=2)
        ttk.Entry(ambient_frame, textvariable=self.ambient_base_var, width=8).pack(side='left', padx=2)
        ttk.Label(ambient_frame, text="变化:").pack(side='left', padx=2)
        ttk.Entry(ambient_frame, textvariable=self.ambient_var_var, width=8).pack(side='left', padx=2)
    
    def create_advanced_tab(self):
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="高级设置")
        
        ttk.Label(advanced_frame, text="高级参数设置", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # STL scaling
        ttk.Label(advanced_frame, text="STL最大尺寸 (cm):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.stl_max_size_var = tk.StringVar(value="150.0")
        ttk.Entry(advanced_frame, textvariable=self.stl_max_size_var, width=15).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Rotation angles
        ttk.Label(advanced_frame, text="旋转角度设置:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.rotation_angles_var = tk.StringVar(value="0,45,90,135,180,225,270,315")
        ttk.Entry(advanced_frame, textvariable=self.rotation_angles_var, width=40).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Blender executable path
        ttk.Label(advanced_frame, text="Blender可执行文件路径:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.blender_path_var = tk.StringVar(value="blender")
        ttk.Entry(advanced_frame, textvariable=self.blender_path_var, width=40).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(advanced_frame, text="浏览", command=lambda: self.browse_file(self.blender_path_var, "可执行文件", "*.exe")).grid(row=3, column=2, padx=5, pady=5)
        
        # Script path
        ttk.Label(advanced_frame, text="Blender脚本路径:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.script_path_var = tk.StringVar(value="深度图数据集_v6.py")
        ttk.Entry(advanced_frame, textvariable=self.script_path_var, width=40).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(advanced_frame, text="浏览", command=lambda: self.browse_file(self.script_path_var, "Python脚本", "*.py")).grid(row=4, column=2, padx=5, pady=5)
    
    def create_control_frame(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var, relief='sunken')
        self.status_label.pack(fill='x', padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="加载配置", command=self.load_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="重置默认值", command=self.reset_defaults).pack(side='left', padx=5)
        ttk.Button(button_frame, text="开始生成数据集", command=self.start_generation, style='Accent.TButton').pack(side='right', padx=5)
    
    def browse_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
    
    def browse_file(self, var, file_type, file_extension):
        file_path = filedialog.askopenfilename(filetypes=[(file_type, file_extension)])
        if file_path:
            var.set(file_path)
    
    def load_defaults(self):
        """Load default values from the original script"""
        # Paths (these would need to be adjusted based on user's system)
        self.stl_folder_var.set(r"E:\zr_network\blender\Thingi10K\selectmodel")
        self.pattern_folder_var.set(r"E:\zr_network\blender\composite_pattern\1")
        self.output_folder_var.set(r"E:\zr_network\blender\output")
        self.hdri_path_var.set(r"E:\zr_network\blender\HDRI\brown_photostudio_02_4k.hdr")
        
        # Set default render parameters
        self.render_width_var.set("640")
        self.render_height_var.set("640")
        self.render_engine_var.set("Cycles")
        self.samples_var.set("512")
        self.ambient_base_var.set("0.5")
        self.ambient_var_var.set("0.1")
        
        # Other default values
        self.stl_max_size_var.set("150.0")
        self.rotation_angles_var.set("0,45,90,135,180,225,270,315")
    
    def load_default_config(self):
        """Load default configuration from 配置.json if it exists"""
        try:
            config_file = "配置.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.apply_config(config)
                print(f"默认配置已加载: {config_file}")
            else:
                print(f"默认配置文件不存在: {config_file}")
        except Exception as e:
            print(f"加载默认配置失败: {e}")
            messagebox.showwarning("警告", f"加载默认配置失败: {e}\n使用内置默认值")
    
    def get_config_dict(self):
        """Get all configuration parameters as a dictionary"""
        # Parse rotation angles, handling potential errors
        rotation_angles_str = self.rotation_angles_var.get()
        try:
            rotation_angles = [float(x.strip()) for x in rotation_angles_str.split(',') if x.strip()]
        except ValueError:
            # Fallback to default if parsing fails
            rotation_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        
        return {
            "paths": {
                "stl_folder": self.stl_folder_var.get(),
                "pattern_folder": self.pattern_folder_var.get(),
                "output_folder": self.output_folder_var.get(),
                "hdri_path": self.hdri_path_var.get()
            },
            "camera": {
                "position": [float(self.camera_x_var.get()), float(self.camera_y_var.get()), float(self.camera_z_var.get())],
                "rotation": [float(self.camera_rot_x_var.get()), float(self.camera_rot_y_var.get()), float(self.camera_rot_z_var.get())],
                "focal_length": float(self.focal_length_var.get()),
                "clip_start": float(self.clip_start_var.get()),
                "clip_end": float(self.clip_end_var.get())
            },
            "projector": {
                "position": [float(self.proj_x_var.get()), float(self.proj_y_var.get()), float(self.proj_z_var.get())],
                "power": float(self.proj_power_var.get()),
                "power_drift": float(self.proj_power_drift_var.get()),
                "use_discrete_power": self.use_discrete_power_var.get(),
                "fov": float(self.fov_var.get())
            },
            "render": {
                "resolution": [int(self.render_width_var.get()), int(self.render_height_var.get())],
                "engine": self.render_engine_var.get(),
                "samples": int(self.samples_var.get()),
                "ambient_base": float(self.ambient_base_var.get()),
                "ambient_variation": float(self.ambient_var_var.get())
            },
            "advanced": {
                "stl_max_size": float(self.stl_max_size_var.get()),
                "rotation_angles": rotation_angles,
                "blender_path": self.blender_path_var.get(),
                "script_path": self.script_path_var.get()
            }
        }
    
    def save_config(self):
        """Save configuration to JSON file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json")])
        if file_path:
            try:
                config = self.get_config_dict()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", "配置已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON文件", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.apply_config(config)
                messagebox.showinfo("成功", "配置已加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败: {str(e)}")
    
    def apply_config(self, config):
        """Apply loaded configuration to GUI"""
        try:
            # Apply paths
            paths = config.get("paths", {})
            if "stl_folder" in paths:
                self.stl_folder_var.set(paths["stl_folder"])
            if "pattern_folder" in paths:
                self.pattern_folder_var.set(paths["pattern_folder"])
            if "output_folder" in paths:
                self.output_folder_var.set(paths["output_folder"])
            if "hdri_path" in paths:
                self.hdri_path_var.set(paths["hdri_path"])
            
            # Apply camera settings
            camera = config.get("camera", {})
            if "position" in camera and len(camera["position"]) == 3:
                self.camera_x_var.set(str(camera["position"][0]))
                self.camera_y_var.set(str(camera["position"][1]))
                self.camera_z_var.set(str(camera["position"][2]))
            if "rotation" in camera and len(camera["rotation"]) == 3:
                self.camera_rot_x_var.set(str(camera["rotation"][0]))
                self.camera_rot_y_var.set(str(camera["rotation"][1]))
                self.camera_rot_z_var.set(str(camera["rotation"][2]))
            if "focal_length" in camera:
                self.focal_length_var.set(str(camera["focal_length"]))
            if "clip_start" in camera:
                self.clip_start_var.set(str(camera["clip_start"]))
            if "clip_end" in camera:
                self.clip_end_var.set(str(camera["clip_end"]))
            
            # Apply projector settings
            projector = config.get("projector", {})
            if "position" in projector and len(projector["position"]) == 3:
                self.proj_x_var.set(str(projector["position"][0]))
                self.proj_y_var.set(str(projector["position"][1]))
                self.proj_z_var.set(str(projector["position"][2]))
            if "power" in projector:
                self.proj_power_var.set(str(projector["power"]))
            if "power_drift" in projector:
                self.proj_power_drift_var.set(str(projector["power_drift"]))
            if "use_discrete_power" in projector:
                self.use_discrete_power_var.set(bool(projector["use_discrete_power"]))
            if "fov" in projector:
                self.fov_var.set(str(projector["fov"]))
            
            # Apply render settings
            render = config.get("render", {})
            if "resolution" in render and len(render["resolution"]) == 2:
                self.render_width_var.set(str(render["resolution"][0]))
                self.render_height_var.set(str(render["resolution"][1]))
            if "engine" in render:
                self.render_engine_var.set(render["engine"])
            if "samples" in render:
                self.samples_var.set(str(render["samples"]))
            if "ambient_base" in render:
                self.ambient_base_var.set(str(render["ambient_base"]))
            if "ambient_variation" in render:
                self.ambient_var_var.set(str(render["ambient_variation"]))
            
            # Apply advanced settings
            advanced = config.get("advanced", {})
            if "stl_max_size" in advanced:
                self.stl_max_size_var.set(str(advanced["stl_max_size"]))
            if "rotation_angles" in advanced:
                angles = advanced["rotation_angles"]
                if isinstance(angles, list):
                    self.rotation_angles_var.set(",".join(map(str, angles)))
            if "blender_path" in advanced:
                self.blender_path_var.set(advanced["blender_path"])
            if "script_path" in advanced:
                self.script_path_var.set(advanced["script_path"])
                
        except Exception as e:
            print(f"应用配置失败: {e}")
            raise Exception(f"应用配置失败: {e}")
    
    def reset_defaults(self):
        """Reset all values to defaults"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            self.load_defaults()
    
    def test_blender_connection(self):
        """Test Blender connection in background"""
        def test_connection():
            try:
                self.status_var.set("正在测试Blender连接...")
                blender_path = self.blender_path_var.get()
                
                # Check if blender path exists
                if not os.path.exists(blender_path) and not self._is_blender_in_path():
                    self.status_var.set("Blender未找到，请检查路径设置")
                    messagebox.showwarning("警告", f"Blender可执行文件未找到: {blender_path}\n请在高级设置中配置正确的Blender路径")
                    return
                
                self.mcp_integration = BlenderMCPIntegration(blender_path)
                success, message = self.mcp_integration.test_blender_connection()
                if success:
                    self.status_var.set("Blender连接成功")
                else:
                    self.status_var.set(f"Blender连接失败: {message}")
                    messagebox.showwarning("警告", f"Blender连接测试失败: {message}")
            except Exception as e:
                self.status_var.set(f"连接测试错误: {str(e)}")
                print(f"Connection test error: {e}")
        
        # Run test in background thread
        test_thread = threading.Thread(target=test_connection)
        test_thread.daemon = True
        test_thread.start()
    
    def _is_blender_in_path(self):
        """Check if blender is available in system PATH"""
        try:
            subprocess.run(["blender", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def start_generation(self):
        """Start the dataset generation process with detailed logging"""
        self.logger.info("=== 开始数据集生成过程 ===")
        
        if self.is_generating:
            self.logger.warning("生成过程已在进行中")
            messagebox.showinfo("提示", "数据集生成正在进行中...")
            return
        
        try:
            # Validate inputs
            self.logger.info("验证输入参数...")
            if not self.validate_inputs():
                self.logger.error("输入验证失败")
                return
            
            # Get configuration
            self.logger.info("获取配置参数...")
            config = self.get_config_dict()
            self.logger.info(f"配置参数获取完成: {json.dumps(config, ensure_ascii=False)[:200]}...")
            
            # Check Blender connection
            self.logger.info("检查Blender连接...")
            if not self.mcp_integration:
                blender_path = self.blender_path_var.get()
                self.logger.info(f"创建Blender集成实例，路径: {blender_path}")
                self.mcp_integration = BlenderMCPIntegration(blender_path)
            
            # Start generation in background thread
            self.logger.info("启动后台生成线程...")
            self.is_generating = True
            self.generation_thread = threading.Thread(target=self._generate_dataset_thread, args=(config,))
            self.generation_thread.daemon = True
            self.generation_thread.start()
            self.logger.info("后台生成线程已启动")
            
        except Exception as e:
            self.logger.error(f"启动生成失败: {e}")
            self.logger.error(f"错误详情: {traceback.format_exc()}")
            messagebox.showerror("错误", f"启动生成失败: {str(e)}")
            self.status_var.set("就绪")
            self.is_generating = False
    
    def validate_inputs(self):
        """Validate all input fields with detailed logging"""
        self.logger.info("开始验证输入参数...")
        
        # Check required paths
        stl_folder = self.stl_folder_var.get()
        self.logger.info(f"STL文件夹路径: {stl_folder}")
        
        if not stl_folder:
            self.logger.error("STL模型文件夹路径为空")
            messagebox.showerror("错误", "STL模型文件夹路径不能为空")
            return False
        
        if not os.path.exists(stl_folder):
            self.logger.error(f"STL模型文件夹不存在: {stl_folder}")
            messagebox.showerror("错误", f"STL模型文件夹路径无效:\n{stl_folder}\n\n请检查路径是否存在")
            return False
        
        # 检查STL文件
        try:
            stl_files = [f for f in os.listdir(stl_folder) if f.lower().endswith('.stl')]
            self.logger.info(f"在STL文件夹中找到 {len(stl_files)} 个STL文件")
            if len(stl_files) == 0:
                self.logger.warning(f"STL文件夹中没有找到STL文件: {stl_folder}")
                messagebox.showwarning("警告", f"STL文件夹中没有找到STL文件:\n{stl_folder}")
        except Exception as e:
            self.logger.error(f"检查STL文件时出错: {e}")
            messagebox.showerror("错误", f"检查STL文件时出错: {e}")
            return False
        
        # 检查图案文件夹
        pattern_folder = self.pattern_folder_var.get()
        self.logger.info(f"图案文件夹路径: {pattern_folder}")
        
        if not pattern_folder:
            self.logger.error("图案图像文件夹路径为空")
            messagebox.showerror("错误", "图案图像文件夹路径不能为空")
            return False
        
        if not os.path.exists(pattern_folder):
            self.logger.error(f"图案图像文件夹不存在: {pattern_folder}")
            messagebox.showerror("错误", f"图案图像文件夹路径无效:\n{pattern_folder}\n\n请检查路径是否存在")
            return False
        
        # 检查图案文件
        try:
            pattern_files = [f for f in os.listdir(pattern_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            self.logger.info(f"在图案文件夹中找到 {len(pattern_files)} 个图像文件")
            if len(pattern_files) == 0:
                self.logger.warning(f"图案文件夹中没有找到图像文件: {pattern_folder}")
                messagebox.showwarning("警告", f"图案文件夹中没有找到图像文件:\n{pattern_folder}\n\n支持的格式: PNG, JPG, JPEG, BMP, TIFF")
        except Exception as e:
            self.logger.error(f"检查图案文件时出错: {e}")
            messagebox.showerror("错误", f"检查图案文件时出错: {e}")
            return False
        
        # 检查输出文件夹
        output_folder = self.output_folder_var.get()
        self.logger.info(f"输出文件夹路径: {output_folder}")
        
        if not output_folder:
            self.logger.error("输出文件夹路径为空")
            messagebox.showerror("错误", "输出文件夹路径不能为空")
            return False
        
        # 尝试创建输出文件夹（如果不存在）
        try:
            os.makedirs(output_folder, exist_ok=True)
            self.logger.info(f"输出文件夹已准备就绪: {output_folder}")
        except Exception as e:
            self.logger.error(f"创建输出文件夹失败: {e}")
            messagebox.showerror("错误", f"创建输出文件夹失败: {e}")
            return False
        
        # Validate numeric inputs
        try:
            float(self.camera_x_var.get())
            float(self.camera_y_var.get())
            float(self.camera_z_var.get())
            float(self.focal_length_var.get())
            float(self.proj_power_var.get())
            int(self.samples_var.get())
            self.logger.info("数值输入验证通过")
        except ValueError as e:
            self.logger.error(f"数值输入无效: {e}")
            messagebox.showerror("错误", f"数值输入无效: {e}")
            return False
        
        self.logger.info("所有输入验证通过")
        return True
    
    def _generate_dataset_thread(self, config):
        """Generate dataset in background thread with detailed logging"""
        self.logger.info("=== 后台生成线程启动 ===")
        try:
            def progress_callback(progress, message):
                # Update GUI in main thread
                self.logger.info(f"进度更新: {progress:.1f}% - {message}")
                self.root.after(0, self._update_progress, progress, message)
            
            # Generate dataset using MCP integration
            self.logger.info("调用MCP集成生成数据集...")
            result = self.mcp_integration.generate_dataset(config, progress_callback)
            
            self.logger.info(f"MCP集成返回结果: success={result.get('success')}, message={result.get('message')}")
            
            # Handle completion in main thread
            if result["success"]:
                self.logger.info("数据集生成成功，更新UI状态")
                self.root.after(0, self._generation_completed, result)
            else:
                self.logger.error(f"数据集生成失败: {result.get('message')}")
                self.root.after(0, self._generation_failed, result["message"])
                
        except Exception as e:
            self.logger.error(f"后台线程异常: {e}")
            self.logger.error(f"异常详情: {traceback.format_exc()}")
            self.root.after(0, self._generation_failed, str(e))
        finally:
            self.logger.info("后台生成线程结束")
            self.is_generating = False
    
    def _update_progress(self, progress, message):
        """Update progress bar and status (called from main thread)"""
        self.progress_var.set(progress)
        self.status_var.set(message)
    
    def _generation_completed(self, result):
        """Handle successful generation (called from main thread)"""
        self.logger.info("=== 数据集生成完成 ===")
        self.status_var.set("数据集生成完成！")
        self.progress_var.set(100)
        
        output_files = result.get('output_files', [])
        parameters_file = result.get('parameters_file', '')
        
        self.logger.info(f"生成完成 - 输出文件: {len(output_files)} 个")
        self.logger.info(f"参数文件: {parameters_file}")
        
        message = f"数据集生成完成！\n"
        message += f"输出文件: {len(output_files)} 个\n"
        if parameters_file:
            message += f"参数文件: {parameters_file}"
        
        # 显示详细的输出文件列表
        if output_files:
            message += f"\n\n输出文件列表:"
            for i, file in enumerate(output_files[:5]):  # 显示前5个文件
                message += f"\n  {os.path.basename(file)}"
            if len(output_files) > 5:
                message += f"\n  ... 还有 {len(output_files) - 5} 个文件"
        
        messagebox.showinfo("成功", message)
    
    def _generation_failed(self, error_message):
        """Handle failed generation (called from main thread)"""
        self.logger.error(f"=== 数据集生成失败 ===")
        self.logger.error(f"错误信息: {error_message}")
        self.status_var.set("生成失败")
        self.progress_var.set(0)
        
        # Enhanced error message with troubleshooting tips
        detailed_message = f"数据集生成失败: {error_message}\n\n"
        detailed_message += "故障排除建议:\n"
        detailed_message += "1. 检查Blender路径是否正确 (高级设置标签页)\n"
        detailed_message += "2. 确保Blender脚本路径指向有效的Python文件\n"
        detailed_message += "3. 验证所有输入文件夹路径是否存在\n"
        detailed_message += "4. 检查Blender是否支持Python脚本执行\n"
        detailed_message += "5. 查看日志文件获取详细错误信息\n"
        detailed_message += f"6. 日志文件位置: logs/blender_dataset_gui.log"
        
        self.logger.error(f"显示错误对话框: {detailed_message}")
        messagebox.showerror("错误", detailed_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = BlenderDatasetGUI(root)
    root.mainloop()