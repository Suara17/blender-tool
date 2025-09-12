#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复路径问题 - 选项1：创建缺失文件夹
"""

import json
import os

def auto_fix_missing_pattern_folder():
    """自动修复缺失的图案文件夹"""
    print("=== 自动修复缺失的图案文件夹 ===")
    
    # 读取配置
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("成功加载配置文件")
    except Exception as e:
        print(f"加载配置失败: {e}")
        return False
    
    paths = config.get("paths", {})
    pattern_folder = paths.get("pattern_folder", "")
    
    if not pattern_folder:
        print("图案文件夹路径为空")
        return False
    
    print(f"图案文件夹: {pattern_folder}")
    
    if os.path.exists(pattern_folder):
        print("图案文件夹已存在，无需修复")
        return True
    
    # 创建缺失的图案文件夹
    try:
        os.makedirs(pattern_folder, exist_ok=True)
        print(f"[OK] 创建图案文件夹: {pattern_folder}")
        
        # 创建示例图案文件
        sample_files = [
            "pattern_001.png",
            "pattern_002.jpg", 
            "pattern_003.png",
            "grid_pattern.png",
            "stripe_pattern.jpg"
        ]
        
        created = 0
        for filename in sample_files:
            filepath = os.path.join(pattern_folder, filename)
            try:
                with open(filepath, 'w') as f:
                    f.write("")  # 创建空文件
                print(f"  [OK] 创建示例文件: {filename}")
                created += 1
            except Exception as e:
                print(f"  [WARN] 创建文件失败: {filename} - {e}")
        
        print(f"[OK] 创建了 {created} 个示例图案文件")
        
        # 保存配置
        save_config(config)
        return True
        
    except Exception as e:
        print(f"[ERROR] 创建图案文件夹失败: {e}")
        return False

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
        print("[OK] 配置文件已更新")
        
    except Exception as e:
        print(f"[ERROR] 保存配置失败: {e}")

def check_blender_installation():
    """检查并修复Blender路径"""
    print("\n=== 检查Blender安装 ===")
    
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        current_path = config.get("advanced", {}).get("blender_path", "")
        print(f"当前Blender路径: {current_path}")
        
        if os.path.exists(current_path):
            print("[OK] Blender路径有效")
            return True
        else:
            print("[WARN] Blender路径无效，正在查找...")
            
            # 常见Blender安装路径
            common_paths = [
                "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
                "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
                "D:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
                "D:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    print(f"[OK] 找到Blender: {path}")
                    config["advanced"]["blender_path"] = path
                    save_config(config)
                    return True
            
            print("[WARN] 未找到Blender，请确保Blender已安装")
            return False
    
    except Exception as e:
        print(f"[ERROR] 检查Blender路径失败: {e}")
        return False

def main():
    """主函数"""
    print("自动修复路径问题")
    print("=" * 30)
    
    # 1. 修复图案文件夹
    pattern_fixed = auto_fix_missing_pattern_folder()
    
    # 2. 检查Blender
    blender_fixed = check_blender_installation()
    
    print("\n" + "=" * 30)
    print("修复结果:")
    print(f"图案文件夹: {'已修复' if pattern_fixed else '修复失败'}")
    print(f"Blender路径: {'已修复' if blender_fixed else '修复失败'}")
    
    if pattern_fixed:
        print("\n[SUCCESS] 路径修复完成！")
        print("现在可以运行 blender_dataset_gui.py 了")
        print("\n注意:")
        print("- 图案文件夹已创建，包含示例文件")
        print("- 请确保Blender已正确安装")
        print("- 检查日志文件获取详细信息")
    else:
        print("\n[FAILED] 部分修复失败")
        print("请手动检查路径设置")

if __name__ == "__main__":
    main()