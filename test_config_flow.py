import json
import os

def validate_config(config_path):
    """验证配置文件格式"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("配置文件加载成功")
        print(f"配置内容: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 验证必需的键
        required_keys = ['paths', 'camera', 'projector', 'render', 'advanced']
        for key in required_keys:
            if key not in config:
                print(f"错误: 缺少必需的键 '{key}'")
                return False
            print(f"找到键 '{key}': {type(config[key])}")
        
        # 验证路径
        paths = config.get('paths', {})
        path_keys = ['stl_folder', 'pattern_folder', 'output_folder']
        for key in path_keys:
            if key in paths:
                path = paths[key]
                print(f"路径 {key}: {path}")
                # 检查路径是否存在
                if os.path.exists(path):
                    print(f"  -> 路径存在")
                else:
                    print(f"  -> 路径不存在（这在测试环境中是正常的）")
        
        print("配置文件验证完成")
        return True
        
    except Exception as e:
        print(f"配置文件验证失败: {e}")
        return False

if __name__ == "__main__":
    config_path = "test_config.json"
    print(f"验证配置文件: {config_path}")
    validate_config(config_path)