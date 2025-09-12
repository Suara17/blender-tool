from blender_mcp_integration import BlenderMCPIntegration
import json
import tempfile
import os

# 创建一个简单的测试配置
config = {
    'paths': {
        'stl_folder': 'D:\\深度学习资料\\实验记录\\blender\\selectmodel', 
        'pattern_folder': 'D:\\深度学习资料\\实验记录\\blender\\composite_pattern', 
        'output_folder': 'D:\\深度学习资料\\实验记录\\blender\\output'
    }, 
    'advanced': {
        'script_path': 'D:\\blender-tool\\深度图数据集_v6.py'
    }
}

# 创建临时配置文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    temp_config_path = f.name

try:
    integration = BlenderMCPIntegration()
    
    # 测试Blender连接
    print("测试Blender连接...")
    result = integration.test_blender_connection()
    print(f"Blender连接测试结果: {result}")
    
    # 测试脚本生成（不实际执行）
    print("测试脚本生成...")
    script = integration._create_blender_script(temp_config_path)
    print(f"脚本生成成功，长度: {len(script)} 字符")
    
    # 检查是否包含正确的字符串转义
    if "replace('\\\\', '/')" in script:
        print("OK 字符串转义正确")
    else:
        print("ERROR 字符串转义问题仍存在")
        
    print("测试完成！")
    
finally:
    # 清理临时文件
    if os.path.exists(temp_config_path):
        os.unlink(temp_config_path)