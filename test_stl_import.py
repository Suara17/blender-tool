import bpy
import os

# 启用STL导入插件
try:
    bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    print("STL导入插件已启用")
except Exception as e:
    print(f"无法启用STL导入插件: {e}")

# 检查STL导入操作符是否可用
if hasattr(bpy.ops.import_mesh, 'stl'):
    print("STL导入操作符可用")
else:
    print("STL导入操作符不可用")

# 尝试导入STL文件（如果存在）
test_stl_path = r"D:\blender-tool\test_data\stl_models\example.stl"
if os.path.exists(test_stl_path):
    try:
        bpy.ops.import_mesh.stl(filepath=test_stl_path)
        print("STL文件导入成功")
    except Exception as e:
        print(f"STL文件导入失败: {e}")
else:
    print(f"测试STL文件不存在: {test_stl_path}")