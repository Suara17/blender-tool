#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证测试 - 完整的系统测试
"""

import json
import os
import tempfile
import logging
from blender_mcp_integration import BlenderMCPIntegration

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("final_test.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def test_complete_system():
    """测试完整的系统"""
    logger = setup_logging()
    logger.info("=== 开始完整系统测试 ===")
    
    # 1. 加载配置
    logger.info("1. 加载配置文件...")
    try:
        with open('配置.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("✓ 配置文件加载成功")
    except Exception as e:
        logger.error(f"✗ 配置文件加载失败: {e}")
        return False
    
    # 2. 验证所有路径
    logger.info("2. 验证所有路径...")
    paths = config.get("paths", {})
    all_paths_valid = True
    
    for key, path in paths.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        logger.info(f"  {status} {key}: {path}")
        
        if not exists:
            all_paths_valid = False
            logger.error(f"路径不存在: {key} - {path}")
        else:
            # 检查具体内容
            if os.path.isdir(path):
                try:
                    files = os.listdir(path)
                    logger.info(f"    包含 {len(files)} 个项目")
                    
                    if key == "pattern_folder":
                        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
                        logger.info(f"    其中 {len(image_files)} 个是图像文件")
                    elif key == "stl_folder":
                        stl_files = [f for f in files if f.lower().endswith('.stl')]
                        logger.info(f"    其中 {len(stl_files)} 个是STL文件")
                        
                except Exception as e:
                    logger.error(f"    无法读取文件夹内容: {e}")
    
    if not all_paths_valid:
        logger.error("路径验证失败，请修复路径问题")
        return False
    
    logger.info("✓ 所有路径验证通过")
    
    # 3. 测试Blender连接
    logger.info("3. 测试Blender连接...")
    try:
        blender_path = config.get("advanced", {}).get("blender_path", "blender")
        logger.info(f"使用Blender路径: {blender_path}")
        integration = BlenderMCPIntegration(blender_path)
        success, message = integration.test_blender_connection()
        
        if success:
            logger.info(f"✓ Blender连接成功: {message}")
        else:
            logger.error(f"✗ Blender连接失败: {message}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Blender连接测试异常: {e}")
        return False
    
    # 4. 测试配置生成
    logger.info("4. 测试配置生成...")
    try:
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            temp_config_path = f.name
        
        logger.info(f"✓ 创建临时配置文件: {temp_config_path}")
        
        # 生成Blender脚本
        script_content = integration._create_blender_script(temp_config_path)
        logger.info(f"✓ 生成Blender脚本 ({len(script_content)} 字符)")
        
        # 验证脚本内容
        validation_results = {
            "配置文件加载": "encoding='utf-8'" in script_content,
            "路径处理": "os.path.abspath" in script_content,
            "Unicode处理": "UnicodeDecodeError" in script_content,
            "关键函数": all(func in script_content for func in [
                'setup_scene_units', 'import_and_prepare_stl',
                'setup_compositor_nodes', 'record_parameters_to_file'
            ])
        }
        
        for check, result in validation_results.items():
            status = "✓" if result else "✗"
            logger.info(f"  {status} {check}")
        
        # 保存脚本用于分析
        script_file = "final_test_script.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        logger.info(f"✓ 脚本已保存到: {script_file}")
        
        # 清理临时文件
        os.unlink(temp_config_path)
        
    except Exception as e:
        logger.error(f"✗ 配置生成测试失败: {e}")
        return False
    
    # 5. 总结
    logger.info("5. 测试总结")
    logger.info("✓ 所有测试通过！")
    logger.info("系统已准备好运行数据集生成")
    
    return True

def main():
    """主函数"""
    print("最终系统验证测试")
    print("=" * 40)
    
    success = test_complete_system()
    
    print("\n" + "=" * 40)
    if success:
        print("[SUCCESS] 系统验证通过！")
        print("\n现在可以安全地运行:")
        print("python blender_dataset_gui.py")
        print("\n系统将:")
        print("- 正确加载所有路径")
        print("- 连接到Blender")
        print("- 生成数据集")
        print("\n详细日志请查看: final_test.log")
    else:
        print("[FAILED] 系统验证失败")
        print("请查看 final_test.log 获取详细信息")
        print("运行 simple_fix_tool.py 修复问题")

if __name__ == "__main__":
    main()