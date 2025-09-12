# 投影仪插件安装说明

本工具需要安装 "Projectors" 插件才能正常工作。如果遇到 "bpy.ops.projector.create" 错误，请按照以下步骤安装插件：

## 安装步骤

### 方法1：通过GitHub下载安装（推荐）

1. 访问插件GitHub页面：https://github.com/eliemichel/Projectors
2. 点击绿色的 "Code" 按钮，选择 "Download ZIP"
3. 解压下载的ZIP文件
4. 打开Blender，进入 `Edit` → `Preferences` → `Add-ons`
5. 点击 "Install..." 按钮
6. 浏览到解压的文件夹，选择 `Projectors.py` 文件
7. 点击 "Install Add-on"
8. 在插件列表中找到 "Projectors" 并勾选启用

### 方法2：手动复制文件

1. 下载并解压插件文件
2. 将 `Projectors.py` 文件复制到Blender的插件目录：
   - Windows: `C:\Users\[用户名]\AppData\Roaming\Blender Foundation\Blender\[版本]\scripts\addons\`
   - macOS: `/Users/[用户名]/Library/Application Support/Blender/[版本]/scripts/addons/`
   - Linux: `/home/[用户名]/.config/blender/[版本]/scripts/addons/`
3. 重启Blender
4. 进入 `Edit` → `Preferences` → `Add-ons`
5. 搜索 "Projectors" 并勾选启用

## 验证安装

安装完成后，您应该能够在Blender中看到投影仪相关的功能，并且本工具不再报 "bpy.ops.projector.create" 错误。

## 常见问题

如果仍然遇到问题，请检查：
1. Blender版本兼容性（插件可能需要特定版本的Blender）
2. 插件是否正确启用（在Addon列表中应显示为已勾选状态）
3. 是否有其他插件冲突

## 更多信息

有关插件的详细使用说明，请参考：https://github.com/eliemichel/Projectors