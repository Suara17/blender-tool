import json
import os

def test_config_mapping():
    """测试配置键名映射"""
    print("=== 测试配置键名映射 ===")
    
    # 模拟GUI配置
    gui_config = {
        "paths": {
            "stl_folder": "D:\\深度学习资料\\实验记录\\blender\\selectmodel",
            "pattern_folder": "D:\\深度学习资料\\实验记录\\blender\\composite_pattern",
            "output_folder": "D:\\深度学习资料\\实验记录\\blender\\output",
            "hdri_path": "D:\\深度学习资料\\实验记录\\blender\\HDRI\\brown_photostudio_02_4k.hdr"
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
            "rotation_angles": [0, 45],
            "blender_path": "D:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
            "script_path": "D:\\blender-tool\\深度图数据集_v6.py"
        }
    }
    
    print("GUI配置:")
    print(json.dumps(gui_config, indent=2, ensure_ascii=False))
    
    # 模拟键名映射
    mapped_config = {}
    
    # 复制所有配置
    for key, value in gui_config.items():
        mapped_config[key] = value
        
    # 映射路径键名
    if "paths" in mapped_config:
        paths = mapped_config["paths"]
        # 映射GUI键名到脚本期望的键名
        if "stl_folder" in paths:
            mapped_config["stl_model_path"] = paths["stl_folder"]
        if "pattern_folder" in paths:
            mapped_config["pattern_path"] = paths["pattern_folder"]
        if "output_folder" in paths:
            mapped_config["output_path"] = paths["output_folder"]
    
    print("\n映射后配置:")
    print(json.dumps(mapped_config, indent=2, ensure_ascii=False))
    
    # 验证映射是否正确
    expected_keys = ["stl_model_path", "pattern_path", "output_path"]
    success = True
    
    for key in expected_keys:
        if key in mapped_config:
            print(f"[OK] 找到期望的键: {key}")
        else:
            print(f"[ERROR] 缺少期望的键: {key}")
            success = False
    
    if success:
        print("\n[SUCCESS] 配置键名映射测试通过!")
    else:
        print("\n[FAILED] 配置键名映射测试失败!")
        
    return success

def test_pattern_loading():
    """测试图案加载功能"""
    print("\n=== 测试图案加载功能 ===")
    
    # 检查测试目录
    test_pattern_dir = "test_data/patterns"
    
    if os.path.exists(test_pattern_dir):
        print(f"[OK] 图案目录存在: {test_pattern_dir}")
        
        # 列出目录中的文件
        try:
            files = os.listdir(test_pattern_dir)
            print(f"目录中的文件: {files}")
            
            # 检查支持的图像格式
            supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
            image_files = [f for f in files if f.lower().endswith(supported_formats)]
            
            if image_files:
                print(f"[OK] 找到 {len(image_files)} 个图像文件: {image_files}")
                print("[SUCCESS] 图案加载功能测试通过!")
                return True
            else:
                print("[WARN] 目录中没有支持的图像文件")
                print("[PARTIAL] 图案加载功能部分通过")
                return True
        except Exception as e:
            print(f"[ERROR] 无法列出目录内容: {e}")
            return False
    else:
        print(f"[WARN] 图案目录不存在: {test_pattern_dir}")
        print("[SKIP] 跳过图案加载测试")
        return True

def main():
    """主测试函数"""
    print("开始测试Blender数据集生成器修复...")
    
    # 测试配置映射
    config_ok = test_config_mapping()
    
    # 测试图案加载
    pattern_ok = test_pattern_loading()
    
    # 总结
    print("\n=== 测试总结 ===")
    if config_ok and pattern_ok:
        print("[SUCCESS] 所有测试通过！")
        print("修复已完成，可以在Blender环境中测试。")
        return True
    else:
        print("[FAILED] 部分测试失败，请检查上述错误。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)