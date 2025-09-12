#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径检查和修复工具
"""

import os
import json
import sys
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_paths_in_config():
    """检查配置文件中的路径"""
    print("=== 检查配置文件中的路径 ===")
    
    # 读取配置文件
    config_file = "配置.json"
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"成功加载配置文件: {config_file}")
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return
    
    paths = config.get("paths", {})
    print("\n检查路径:")
    
    missing_paths = []
    existing_paths = []
    
    for key, path in paths.items():
        print(f"\n{key}: {path}")
        
        if os.path.exists(path):
            print(f"  ✓ 存在")
            existing_paths.append(key)
            
            # 提供更多详细信息
            if os.path.isdir(path):
                try:
                    files = os.listdir(path)
                    print(f"  📁 文件夹，包含 {len(files)} 个项目")
                    
                    # 显示前几个文件
                    if files:
                        print(f"  📄 前几个项目: {', '.join(files[:3])}")
                        if len(files) > 3:
                            print(f"  📄 ... 还有 {len(files) - 3} 个")
                    
                except Exception as e:
                    print(f"  ❌ 无法读取文件夹内容: {e}")
            else:
                print(f"  📄 文件，大小: {os.path.getsize(path)} 字节")
                
        else:
            print(f"  ❌ 不存在")
            missing_paths.append(key)
    
    print(f"\n总结:")
    print(f"  存在路径: {len(existing_paths)} 个")
    print(f"  缺失路径: {len(missing_paths)} 个")
    
    if missing_paths:
        print(f"  缺失的路径: {', '.join(missing_paths)}")
    
    return missing_paths, existing_paths

def suggest_path_fixes():
    """建议路径修复方案"""
    print("\n=== 建议路径修复方案 ===")
    
    # 常见路径建议
    suggestions = {
        "stl_folder": [
            "D:\\blender_data\\stl_models",
            "D:\\blender_data\\Thingi10K\\selectmodel", 
            "C:\\Users\\Public\\Documents\\Blender\\STL"
        ],
        "pattern_folder": [
            "D:\\blender_data\\patterns",
            "D:\\blender_data\\composite_pattern",
            "C:\\Users\\Public\\Documents\\Blender\\Patterns"
        ],
        "output_folder": [
            "D:\\blender_data\\output",
            "D:\\blender_output",
            "C:\\Users\\Public\\Documents\\Blender\\Output"
        ],
        "hdri_path": [
            "D:\\blender_data\\HDRI\\brown_photostudio_02_4k.hdr",
            "C:\\Users\\Public\\Documents\\Blender\\HDRI\\studio.hdr"
        ]
    }
    
    print("建议的路径设置:")
    for key, suggested_paths in suggestions.items():
        print(f"\n{key}:")
        for i, path in enumerate(suggested_paths, 1):
            print(f"  建议{i}: {path}")
            # 检查建议路径是否存在
            if os.path.exists(path):
                print(f"    ✓ 此路径存在")
            else:
                print(f"    - 此路径不存在，需要创建")

def create_sample_directories():
    """创建示例目录结构"""
    print("\n=== 创建示例目录结构 ===")
    
    base_dir = input("请输入基础目录路径 (例如 D:\\blender_data): ").strip()
    
    if not base_dir:
        print("未提供基础目录路径，取消创建")
        return
    
    try:
        # 创建目录结构
        directories = [
            "selectmodel",      # STL模型
            "composite_pattern", # 图案图像
            "output",           # 输出
            "HDRI"              # 环境贴图
        ]
        
        created_dirs = []
        for dir_name in directories:
            dir_path = os.path.join(base_dir, dir_name)
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)
                print(f"✓ 创建目录: {dir_path}")
            except Exception as e:
                print(f"❌ 创建目录失败: {dir_path} - {e}")
        
        # 创建示例文件
        print("\n创建示例文件...")
        
        # 在图案文件夹中创建示例图像文件
        pattern_dir = os.path.join(base_dir, "composite_pattern")
        if os.path.exists(pattern_dir):
            # 创建空的示例图像文件
            sample_images = ["pattern1.png", "pattern2.jpg", "pattern3.bmp"]
            for img_name in sample_images:
                img_path = os.path.join(pattern_dir, img_name)
                try:
                    with open(img_path, 'w') as f:
                        f.write("")  # 创建空文件
                    print(f"✓ 创建示例图像: {img_name}")
                except Exception as e:
                    print(f"❌ 创建示例图像失败: {img_name} - {e}")
        
        # 在HDRI文件夹中创建示例HDR文件
        hdri_dir = os.path.join(base_dir, "HDRI")
        if os.path.exists(hdri_dir):
            sample_hdri = "studio.hdr"
            hdri_path = os.path.join(hdri_dir, sample_hdri)
            try:
                with open(hdri_path, 'w') as f:
                    f.write("")  # 创建空文件
                print(f"✓ 创建示例HDRI: {sample_hdri}")
            except Exception as e:
                print(f"❌ 创建示例HDRI失败: {sample_hdri} - {e}")
        
        print(f"\n✓ 示例目录结构创建完成！")
        print(f"基础目录: {base_dir}")
        print(f"创建目录: {len(created_dirs)} 个")
        
        # 生成新的配置文件
        print("\n生成新的配置文件...")
        new_config = {
            "paths": {
                "stl_folder": os.path.join(base_dir, "selectmodel"),
                "pattern_folder": os.path.join(base_dir, "composite_pattern"),
                "output_folder": os.path.join(base_dir, "output"),
                "hdri_path": os.path.join(base_dir, "HDRI", "studio.hdr")
            }
        }
        
        config_file = "配置_建议.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            print(f"✓ 新配置文件已生成: {config_file}")
            print("请使用这个新的配置文件路径")
        except Exception as e:
            print(f"❌ 生成配置文件失败: {e}")
        
    except Exception as e:
        print(f"创建目录结构失败: {e}")

def main():
    """主函数"""
    print("Blender数据集生成器 - 路径检查和修复工具")
    print("=" * 50)
    
    # 1. 检查当前路径
    missing_paths, existing_paths = check_paths_in_config()
    
    # 2. 如果有缺失路径，提供建议
    if missing_paths:
        suggest_path_fixes()
        
        print(f"\n缺失的路径: {', '.join(missing_paths)}")
        choice = input("\n是否要创建示例目录结构? (y/n): ").strip().lower()
        
        if choice == 'y':
            create_sample_directories()
    else:
        print("\n✓ 所有路径都存在！")
        print("如果仍然遇到问题，请检查:")
        print("1. Blender是否正确安装")
        print("2. 文件权限是否正确")
        print("3. 路径中是否包含特殊字符")

if __name__ == "__main__":
    main()