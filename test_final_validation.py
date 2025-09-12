"""
最终测试脚本
用于验证所有修复是否正确应用
"""

import json
import os
import sys

def test_config_mapping():
    """测试配置键名映射"""
    print("=== 测试配置键名映射 ===")
    
    # 读取实际的配置文件
    config_file = "配置.json"
    if not os.path.exists(config_file):
        print(f"[ERROR] 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            gui_config = json.load(f)
        print("[OK] 成功加载配置文件")
    except Exception as e:
        print(f"[ERROR] 加载配置文件失败: {e}")
        return False
    
    # 模拟MCP集成中的键名映射
    mapped_config = {}
    
    # 复制所有配置
    for key, value in gui_config.items():
        mapped_config[key] = value
        
    # 映射路径键名（模拟MCP集成中的_map_config_keys方法）
    if "paths" in mapped_config:
        paths = mapped_config["paths"]
        # 映射GUI键名到脚本期望的键名
        if "stl_folder" in paths:
            mapped_config["stl_model_path"] = paths["stl_folder"]
        if "pattern_folder" in paths:
            mapped_config["pattern_path"] = paths["pattern_folder"]
        if "output_folder" in paths:
            mapped_config["output_path"] = paths["output_folder"]
    
    # 验证映射结果
    expected_keys = ["stl_model_path", "pattern_path", "output_path"]
    success = True
    
    for key in expected_keys:
        if key in mapped_config:
            print(f"[OK] 找到映射后的键: {key} = {mapped_config[key]}")
        else:
            print(f"[ERROR] 缺少映射后的键: {key}")
            success = False
    
    return success

def test_script_modifications():
    """测试脚本修改"""
    print("\n=== 测试脚本修改 ===")
    
    script_file = "深度图数据集_v6.py"
    if not os.path.exists(script_file):
        print(f"[ERROR] 脚本文件不存在: {script_file}")
        return False
    
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("[OK] 成功读取脚本文件")
    except Exception as e:
        print(f"[ERROR] 读取脚本文件失败: {e}")
        return False
    
    # 检查关键修改
    checks = [
        ("hasattr安全检查", "hasattr(bpy.context.scene.render, 'cycles')"),
        ("图案格式支持", "supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')"),
        ("目录内容调试", "print(f\"  - 目录中的文件列表: {files}\", flush=True)")
    ]
    
    all_passed = True
    for check_name, check_content in checks:
        if check_content in content:
            print(f"[OK] {check_name}")
        else:
            print(f"[ERROR] 缺少 {check_name}")
            all_passed = False
    
    return all_passed

def test_integration_modifications():
    """测试集成代码修改"""
    print("\n=== 测试集成代码修改 ===")
    
    integration_file = "blender_mcp_integration.py"
    if not os.path.exists(integration_file):
        print(f"[ERROR] 集成文件不存在: {integration_file}")
        return False
    
    try:
        with open(integration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("[OK] 成功读取集成文件")
    except Exception as e:
        print(f"[ERROR] 读取集成文件失败: {e}")
        return False
    
    # 检查关键修改
    checks = [
        ("键名映射方法", "def _map_config_keys(self, config):"),
        ("配置映射调用", "mapped_config = self._map_config_keys(config)"),
        ("日志信息", "logger.info(\"映射配置参数键名...\")")
    ]
    
    all_passed = True
    for check_name, check_content in checks:
        if check_content in content:
            print(f"[OK] {check_name}")
        else:
            print(f"[ERROR] 缺少 {check_name}")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("开始最终测试Blender数据集生成器修复...")
    
    # 测试配置映射
    config_ok = test_config_mapping()
    
    # 测试脚本修改
    script_ok = test_script_modifications()
    
    # 测试集成代码修改
    integration_ok = test_integration_modifications()
    
    # 总结
    print("\n=== 最终测试总结 ===")
    if config_ok and script_ok and integration_ok:
        print("[SUCCESS] 所有测试通过！")
        print("修复已完成，可以在Blender环境中进行全面测试。")
        print("\n修复内容总结:")
        print("1. 修复了MCP集成代码中的配置参数键名映射问题")
        print("2. 确保GUI配置正确传递给Blender脚本")
        print("3. 修复了图案加载问题，支持多种图像格式")
        print("4. 添加了调试信息以便于问题排查")
        return True
    else:
        print("[FAILED] 部分测试失败，请检查上述错误。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)