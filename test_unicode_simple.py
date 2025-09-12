#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试Unicode路径处理
"""

import json
import os
import tempfile
from blender_mcp_integration import BlenderMCPIntegration

def test_unicode_script_generation():
    """测试Unicode路径的Blender脚本生成"""
    print("=== 测试Unicode路径的Blender脚本生成 ===")
    
    # 创建测试配置，包含中文字符路径
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
    
    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
            temp_config_path = f.name
        print(f"[OK] 创建临时配置文件: {temp_config_path}")
        
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
        
        # 检查脚本是否包含正确的路径处理
        if "os.path.abspath" in script_content:
            print("[OK] 脚本包含绝对路径处理")
        
        if "UnicodeDecodeError" in script_content:
            print("[OK] 脚本包含Unicode错误处理")
        
        # 保存生成的脚本用于检查
        script_test_file = "test_generated_script.py"
        with open(script_test_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"[OK] 生成的脚本已保存到: {script_test_file}")
        
        # 清理临时文件
        os.unlink(temp_config_path)
        print("[OK] 临时配置文件已清理")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始Unicode路径处理测试...")
    
    success = test_unicode_script_generation()
    
    if success:
        print("\n[SUCCESS] Unicode路径处理测试通过！")
    else:
        print("\n[FAILED] Unicode路径处理测试失败。")