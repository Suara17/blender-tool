import shutil
import os

# 源文件和目标文件路径
src = r"D:\blender-tool\深度图数据集_v6.py"
dst = r"D:\blender-tool\深度图数据集_v6.py.bak"

# 复制文件
if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"文件已备份: {dst}")
else:
    print(f"源文件不存在: {src}")