#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的路径修复工具
"""

import json
import os

def simple_path_fix():
    """简单的路径修复"""
    print("=== 路径问题诊断和修复 ===")
    
    # 读取配置
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("成功加载配置文件")
    except Exception as e:
        print(f"加载配置失败: {e}")
        return
    
    paths = config.get("paths", {})
    
    print("\n当前配置的路径:")
    missing_paths = []
    
    for key, path in paths.items():
        exists = os.path.exists(path)
        status = "存在" if exists else "不存在"
        print(f"{key}: {path} - {status}")
        
        if not exists:
            missing_paths.append((key, path))
    
    if not missing_paths:
        print("\n所有路径都存在！")
    else:
        print(f"\n发现 {len(missing_paths)} 个缺失路径:")
        for key, path in missing_paths:
            print(f"  - {key}: {path}")
        
        # 提供简单的修复方案
        print("\n修复建议:")
        print("1. 创建缺失的文件夹")
        print("2. 使用相对路径方案")
        print("3. 手动选择正确路径")
        
        choice = input("\n选择修复方式 (1-3): ").strip()
        
        if choice == "1":
            create_missing_folders(config, missing_paths)
        elif choice == "2":
            use_relative_paths(config)
        elif choice == "3":
            print("请在GUI程序中手动选择正确路径")

def create_missing_folders(config, missing_paths):
    """创建缺失的文件夹"""
    print("\n创建缺失的文件夹...")
    
    created = 0
    for key, path in missing_paths:
        try:
            os.makedirs(path, exist_ok=True)
            print(f"[OK] 创建: {path}")
            created += 1
            
            # 为图案文件夹创建示例文件
            if "pattern" in key.lower():
                create_sample_files(path, ["pattern1.png", "pattern2.jpg"])
            
        except Exception as e:
            print(f"[ERROR] 创建失败: {path} - {e}")
    
    if created > 0:
        print(f"\n成功创建 {created} 个文件夹")
        save_config(config)

def create_sample_files(folder, filenames):
    """创建示例文件"""
    for filename in filenames:
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, 'w') as f:
                f.write("")
            print(f"  [OK] 创建示例文件: {filename}")
        except Exception as e:
            print(f"  [WARN] 创建示例文件失败: {filename} - {e}")

def use_relative_paths(config):
    """使用相对路径"""
    print("\n使用相对路径方案...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    new_paths = {
        "stl_folder": os.path.join(data_dir, "stl_models"),
        "pattern_folder": os.path.join(data_dir, "patterns"),
        "output_folder": os.path.join(data_dir, "output"),
        "hdri_path": os.path.join(data_dir, "HDRI", "studio.hdr")
    }
    
    print("将创建以下目录:")
    for key, path in new_paths.items():
        print(f"  {key}: {path}")
        
        try:
            if key == "hdri_path":
                os.makedirs(os.path.dirname(path), exist_ok=True)
            else:
                os.makedirs(path, exist_ok=True)
            print(f"    [OK] 已创建")
        except Exception as e:
            print(f"    [ERROR] 创建失败: {e}")
    
    config["paths"] = new_paths
    save_config(config)
    
    # 创建示例图案文件
    create_sample_files(new_paths["pattern_folder"], ["pattern1.png", "pattern2.jpg"])

def save_config(config):
    """保存配置"""
    try:
        # 备份原配置
        backup_file = "配置_备份.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"[OK] 备份配置: {backup_file}")
        
        # 保存新配置
        with open('配置.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("[OK] 配置已更新")
        
    except Exception as e:
        print(f"[ERROR] 保存配置失败: {e}")

def check_blender_path():
    """检查Blender路径"""
    print("\n=== 检查Blender路径 ===")
    
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        current_path = config.get("advanced", {}).get("blender_path", "")
        print(f"当前Blender路径: {current_path}")
        
        if os.path.exists(current_path):
            print("[OK] Blender路径有效")
        else:
            print("[WARN] Blender路径无效")
            
            # 常见路径
            common_paths = [
                "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
                "D:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    print(f"[OK] 找到Blender: {path}")
                    config["advanced"]["blender_path"] = path
                    save_config(config)
                    break
            else:
                print("[WARN] 未找到Blender，请手动指定正确路径")
    
    except Exception as e:
        print(f"[ERROR] 检查Blender路径失败: {e}")

def main():
    """主函数"""
    print("Blender数据集生成器 - 路径修复工具")
    print("=" * 40)
    
    # 1. 修复路径
    simple_path_fix()
    
    # 2. 检查Blender
    check_blender_path()
    
    print("\n" + "=" * 40)
    print("修复完成！")
    print("\n下一步:")
    print("1. 运行 blender_dataset_gui.py")
    print("2. 检查日志文件 logs/blender_dataset_gui.log")
    print("3. 确保所有路径都有效")

if __name__ == "__main__":
    main()