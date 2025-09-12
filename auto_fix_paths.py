#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复路径问题
"""

import json
import os
import shutil
from pathlib import Path

def fix_missing_paths():
    """修复缺失的路径"""
    print("=== 自动修复路径问题 ===")
    
    # 读取当前配置
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ 成功加载当前配置")
    except Exception as e:
        print(f"✗ 加载配置失败: {e}")
        return False
    
    paths = config.get("paths", {})
    
    # 检查每个路径
    missing_paths = []
    for key, path in paths.items():
        if not os.path.exists(path):
            missing_paths.append((key, path))
            print(f"缺失: {key} - {path}")
    
    if not missing_paths:
        print("✓ 所有路径都存在，无需修复")
        return True
    
    print(f"\n发现 {len(missing_paths)} 个缺失路径")
    
    # 提供修复选项
    print("\n修复选项:")
    print("1. 自动创建缺失的文件夹")
    print("2. 手动选择现有文件夹")
    print("3. 使用相对路径方案")
    print("4. 取消")
    
    choice = input("\n请选择修复方式 (1-4): ").strip()
    
    if choice == "1":
        return auto_create_missing_folders(config, missing_paths)
    elif choice == "2":
        return manual_select_folders(config, missing_paths)
    elif choice == "3":
        return use_relative_paths(config)
    else:
        print("取消修复")
        return False

def auto_create_missing_folders(config, missing_paths):
    """自动创建缺失的文件夹"""
    print("\n=== 自动创建缺失文件夹 ===")
    
    created_count = 0
    
    for key, missing_path in missing_paths:
        try:
            # 创建文件夹
            os.makedirs(missing_path, exist_ok=True)
            print(f"✓ 创建: {missing_path}")
            created_count += 1
            
            # 根据文件夹类型创建示例文件
            if "pattern" in key.lower():
                create_sample_pattern_files(missing_path)
            elif "stl" in key.lower():
                create_sample_stl_files(missing_path)
            elif "output" in key.lower():
                print(f"  输出文件夹已准备就绪")
            elif "hdri" in key.lower():
                create_sample_hdri_file(missing_path)
                
        except Exception as e:
            print(f"✗ 创建失败: {missing_path} - {e}")
    
    print(f"\n创建了 {created_count} 个文件夹")
    
    # 保存更新后的配置
    if created_count > 0:
        save_updated_config(config)
        return True
    
    return False

def create_sample_pattern_files(pattern_folder):
    """创建示例图案文件"""
    print(f"  创建示例图案文件...")
    
    # 创建一些空的图像文件作为示例
    sample_files = [
        "pattern_001.png",
        "pattern_002.jpg", 
        "pattern_003.bmp",
        "grid_pattern.png",
        "stripe_pattern.jpg"
    ]
    
    created = 0
    for filename in sample_files:
        filepath = os.path.join(pattern_folder, filename)
        try:
            with open(filepath, 'w') as f:
                f.write("")  # 创建空文件
            created += 1
        except Exception as e:
            print(f"    警告: 创建 {filename} 失败: {e}")
    
    print(f"    创建了 {created} 个示例图案文件")

def create_sample_stl_files(stl_folder):
    """创建示例STL文件"""
    print(f"  注意: STL文件需要您提供实际的3D模型文件")
    print(f"  请在以下文件夹中添加 .stl 文件: {stl_folder}")

def create_sample_hdri_file(hdri_path):
    """创建示例HDRI文件"""
    print(f"  注意: HDRI文件需要您提供实际的环境贴图")
    print(f"  请确保以下文件存在: {hdri_path}")
    print(f"  您可以从以下网站下载免费HDRI:")
    print(f"  - https://hdri-haven.com/")
    print(f"  - https://polyhaven.com/hdris")

def manual_select_folders(config, missing_paths):
    """手动选择现有文件夹"""
    print("\n=== 手动选择文件夹 ===")
    print("此功能需要在GUI中手动选择文件夹")
    print("请运行GUI程序，然后手动浏览选择正确的文件夹")
    return False

def use_relative_paths(config):
    """使用相对路径方案"""
    print("\n=== 使用相对路径方案 ===")
    
    # 获取当前脚本目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"当前目录: {current_dir}")
    
    # 创建子目录
    subdirs = {
        "stl_folder": "data/stl_models",
        "pattern_folder": "data/patterns", 
        "output_folder": "data/output",
        "hdri_path": "data/HDRI/studio.hdr"
    }
    
    print("将创建以下子目录:")
    for key, rel_path in subdirs.items():
        full_path = os.path.join(current_dir, rel_path)
        print(f"  {key}: {full_path}")
        
        try:
            if key == "hdri_path":
                # HDRI是文件，创建目录即可
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            else:
                os.makedirs(full_path, exist_ok=True)
            print(f"    ✓ 已创建")
        except Exception as e:
            print(f"    ✗ 创建失败: {e}")
    
    # 更新配置
    config["paths"] = {key: os.path.join(current_dir, path) for key, path in subdirs.items()}
    
    save_updated_config(config)
    
    # 创建示例文件
    print("\n创建示例文件...")
    create_sample_pattern_files(subdirs["pattern_folder"])
    
    return True

def save_updated_config(config):
    """保存更新后的配置"""
    try:
        backup_file = "配置_备份.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ 备份配置已保存: {backup_file}")
        
        # 覆盖原配置文件
        with open('配置.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✓ 配置文件已更新")
        
    except Exception as e:
        print(f"✗ 保存配置失败: {e}")

def check_blender_installation():
    """检查Blender安装"""
    print("\n=== 检查Blender安装 ===")
    
    # 常见Blender安装路径
    common_paths = [
        "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
        "D:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
        "D:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
    ]
    
    found_blender = None
    for path in common_paths:
        if os.path.exists(path):
            print(f"✓ 找到Blender: {path}")
            found_blender = path
            break
    
    if found_blender:
        print(f"\n建议更新配置文件中的Blender路径为: {found_blender}")
        
        # 更新配置文件
        try:
            with open('配置.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config["advanced"]["blender_path"] = found_blender
            
            with open('配置.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✓ Blender路径已更新到配置文件")
            
        except Exception as e:
            print(f"✗ 更新配置文件失败: {e}")
    
    else:
        print("✗ 未找到Blender安装")
        print("请确保Blender已安装，或手动指定正确的Blender路径")

def main():
    """主函数"""
    print("Blender数据集生成器 - 自动修复工具")
    print("=" * 50)
    
    # 1. 修复路径问题
    path_fixed = fix_missing_paths()
    
    # 2. 检查Blender安装
    check_blender_installation()
    
    print("\n" + "=" * 50)
    if path_fixed:
        print("✓ 路径修复完成！")
        print("现在可以尝试运行GUI程序了")
    else:
        print("⚠ 路径修复被取消或失败")
        print("请手动检查路径设置")
    
    print("\n下一步建议:")
    print("1. 运行 blender_dataset_gui.py")
    print("2. 检查日志文件 logs/blender_dataset_gui.log")
    print("3. 如果仍有问题，查看详细的调试信息")

if __name__ == "__main__":
    main()