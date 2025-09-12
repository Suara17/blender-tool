# Blender结构光数据集生成器使用说明

## 系统要求

- Windows 10或更高版本
- Python 3.7或更高版本
- Blender 3.0或更高版本

## 安装步骤

1. **安装Blender**：
   - 访问 https://www.blender.org/download/ 下载Blender
   - 运行安装程序并按照提示完成安装
   - 记住安装路径，通常为 `C:\Program Files\Blender Foundation\Blender 4.4\`

2. **配置环境**：
   - 确保Python已安装并添加到系统PATH
   - 安装所需的Python包：
     ```
     pip install -r requirements.txt
     ```

3. **配置Blender路径**：
   - 运行 `blender_dataset_gui.py`
   - 在GUI的"高级设置"标签页中，设置正确的Blender可执行文件路径

## 使用方法

1. **启动GUI**：
   ```
   python blender_dataset_gui.py
   ```

2. **配置参数**：
   - 在GUI中设置STL模型文件夹、图案图像文件夹和输出文件夹路径
   - 根据需要调整相机、投影仪和渲染设置
   - 在"高级设置"中确认Blender可执行文件路径正确

3. **生成数据集**：
   - 点击"开始生成数据集"按钮
   - 等待生成过程完成
   - 检查输出文件夹中的结果

## 故障排除

1. **Blender未找到**：
   - 检查"高级设置"中的Blender路径是否正确
   - 确认Blender已正确安装

2. **STL文件导入失败**：
   - 检查STL文件是否损坏
   - 确认文件格式正确

3. **其他问题**：
   - 查看日志文件 `logs/blender_dataset_gui.log` 获取详细错误信息
   - 检查 `FIXES_SUMMARY.md` 了解已知问题和修复情况