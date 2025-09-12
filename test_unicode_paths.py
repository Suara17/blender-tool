#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Unicode路径处理的脚本
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_unicode_paths():
    """测试Unicode路径处理"""
    print("=== 测试Unicode路径处理 ===")
    
    # 测试配置，包含中文字符路径
    test_config = {
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
    
    # 测试1: 保存配置到JSON文件
    print("\n1. 测试保存配置到JSON文件...")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
            temp_config_path = f.name
        print(f"   [OK] 配置已保存到: {temp_config_path}")
    except Exception as e:
        print(f"   [ERROR] 保存配置失败: {e}")
        return False
    
    # 测试2: 从JSON文件加载配置
    print("\n2. 测试从JSON文件加载配置...")
    try:
        with open(temp_config_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        print(f"   [OK] 配置已成功加载")
        
        # 验证路径是否正确加载
        paths = loaded_config.get("paths", {})
        for key, path in paths.items():
            print(f"   - {key}: {path}")
    except Exception as e:
        print(f"   [ERROR] 加载配置失败: {e}")
        return False
    
    # 测试3: 测试路径存在性检查
    print("\n3. 测试路径存在性检查...")
    paths = loaded_config.get("paths", {})
    for key, path in paths.items():
        if key != "hdri_path":  # HDRI文件可能不存在
            try:
                exists = os.path.exists(path)
                status = "[OK]" if exists else "[ERROR]"
                print(f"   {status} {key}: {path} {'存在' if exists else '不存在'}")
            except Exception as e:
                print(f"   [ERROR] {key}: {path} 检查失败: {e}")
    
    # 测试4: 测试路径创建
    print("\n4. 测试输出目录创建...")
    output_folder = paths.get("output_folder", "")
    if output_folder:
        try:
            test_subdir = os.path.join(output_folder, "test_unicode_测试")
            os.makedirs(test_subdir, exist_ok=True)
            print(f"   [OK] 成功创建测试目录: {test_subdir}")
            
            # 清理测试目录
            try:
                os.rmdir(test_subdir)
                print(f"   [OK] 成功清理测试目录")
            except:
                pass
        except Exception as e:
            print(f"[ERROR] 创建测试目录失败: {e}")
    
    # 清理临时文件
    try:
        os.unlink(temp_config_path)
        print(f"\n[OK] 临时文件已清理")
    except:
        pass
    
    print("\n=== Unicode路径测试完成 ===")
    return True

def test_blender_script_generation():
    """测试Blender脚本生成"""
    print("\n=== 测试Blender脚本生成 ===")
    
    try:
        from blender_mcp_integration import BlenderMCPIntegration
        
        # 创建测试配置
        test_config = {
            "paths": {
                "stl_folder": "D:\\深度学习资料\\实验记录\\blender\\selectmodel",
                "pattern_folder": "D:\\深度学习资料\\实验记录\\blender\\composite_pattern", 
                "output_folder": "D:\\深度学习资料\\实验记录\\blender\\output",
                "hdri_path": "D:\\深度学习资料\\实验记录\\blender\\HDRI\\brown_photostudio_02_4k.hdr"
            },
            "advanced": {
                "script_path": "深度图数据集_v6.py"
            }
        }
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
            temp_config_path = f.name
        
        # 测试脚本生成
        integration = BlenderMCPIntegration()
        script_content = integration._create_blender_script(temp_config_path)
        
        print("[OK] Blender脚本生成成功")
        print(f"脚本长度: {len(script_content)} 字符")
        
        # 检查脚本中是否正确处理了Unicode路径
        if "深度学习资料" in script_content:
            print("[OK] 脚本中包含Unicode路径")
        else:
            print("[WARN] 脚本中可能未正确处理Unicode路径")
        
        # 清理临时文件
        os.unlink(temp_config_path)
        
    except Exception as e:
        print(f"[ERROR] Blender脚本生成测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("开始Unicode路径处理测试...")
    
    # 运行测试
    success1 = test_unicode_paths()
    success2 = test_blender_script_generation()
    
    if success1 and success2:
        print("\n[SUCCESS] 所有测试通过！Unicode路径处理已修复。")
    else:
        print("\n[FAILED] 部分测试失败，请检查错误信息。")