import json
import os

# 检查配置文件
config_file = "配置.json"
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("配置文件内容:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
else:
    print(f"配置文件不存在: {config_file}")

# 检查GUI默认值
print("\nGUI默认值检查:")
print("STL文件夹路径应该为: D:\\深度学习资料\\实验记录\\blender\\selectmodel")
print("图案文件夹路径应该为: D:\\深度学习资料\\实验记录\\blender\\composite_pattern")
print("输出文件夹路径应该为: D:\\深度学习资料\\实验记录\\blender\\output")