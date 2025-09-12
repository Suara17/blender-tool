import bpy
import os
import json
import math
import sys
import traceback

# --- Utility Functions ---

def load_config(config_path):
    """从JSON文件加载配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"成功加载并解析配置文件: {config_path}", flush=True)
        return config
    except Exception as e:
        print(f"错误: 加载或解析配置文件失败: {config_path}", flush=True)
        print(str(e), flush=True)
        return {}

def cleanup_scene():
    """清理场景中的所有网格对象、灯光和相机"""
    print("开始清理场景...", flush=True)
    bpy.ops.object.select_all(action='DESELECT')
    # 删除所有网格
    if bpy.data.meshes:
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
    # 删除所有灯光
    if bpy.data.lights:
        bpy.ops.object.select_by_type(type='LIGHT')
        bpy.ops.object.delete()
    # 删除所有相机
    if bpy.data.cameras:
        bpy.ops.object.select_by_type(type='CAMERA')
        bpy.ops.object.delete()
    print("场景清理完毕。", flush=True)


def setup_camera(camera_config):
    """根据配置设置相机"""
    print("设置相机...", flush=True)
    
    position = camera_config.get('position', [0, -5, 2])
    rotation = camera_config.get('rotation', [80, 0, 0])
    focal_length = camera_config.get('focal_length', 50.0)
    clip_start = camera_config.get('clip_start', 0.1)
    clip_end = camera_config.get('clip_end', 1000)

    # 角度转弧度
    rotation_rad = [math.radians(angle) for angle in rotation]

    bpy.ops.object.camera_add(location=position, rotation=rotation_rad)
    camera = bpy.context.object
    camera.name = "MyCamera"
    camera.data.lens = focal_length
    camera.data.clip_start = clip_start
    camera.data.clip_end = clip_end
    
    bpy.context.scene.camera = camera
    print("相机设置完毕。", flush=True)
    return camera

def setup_projector(projector_config):
    """根据配置设置投影仪"""
    print("设置投影仪...", flush=True)
    
    position = projector_config.get('position', [0, 0, 5])
    energy = projector_config.get('power', 1000)
    fov = projector_config.get('fov', 40)

    # 检查是否已存在名为'Projector'的灯光
    if 'Projector' in bpy.data.objects:
        projector = bpy.data.objects['Projector']
        print("  - 找到现有投影仪。", flush=True)
    else:
        bpy.ops.object.light_add(type='SPOT', location=position)
        projector = bpy.context.object
        projector.name = 'Projector'
        print("  - 创建新投影仪。", flush=True)

    # 基本属性
    projector.data.energy = energy
    projector.data.spot_size = math.radians(fov)
    projector.data.shadow_soft_size = 0 # 硬阴影
    projector.data.show_cone = True
    print(f"  - 功率设置为: {energy}", flush=True)
    print(f"  - 视场角设置为: {fov}", flush=True)

    # 使用节点
    projector.data.use_nodes = True
    node_tree = projector.data.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    
    # 清理现有节点
    for node in nodes:
        nodes.remove(node)

    # 创建节点
    output_node = nodes.new(type='ShaderNodeOutputLight')
    emission_node = nodes.new(type='ShaderNodeEmission')
    tex_image_node = nodes.new(type='ShaderNodeTexImage')
    tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
    mapping_node = nodes.new(type='ShaderNodeMapping')

    # 布局节点
    output_node.location = (400, 0)
    emission_node.location = (200, 0)
    tex_image_node.location = (0, 0)
    mapping_node.location = (-200, 0)
    tex_coord_node.location = (-400, 0)
    
    # 设置映射
    mapping_node.vector_type = 'TEXTURE'
    mapping_node.inputs['Scale'].default_value.x = 1.0
    mapping_node.inputs['Scale'].default_value.y = 1.0
    mapping_node.inputs['Scale'].default_value.z = 1.0

    # 连接节点
    links.new(tex_coord_node.outputs['Normal'], mapping_node.inputs['Vector'])
    links.new(mapping_node.outputs['Vector'], tex_image_node.inputs['Vector'])
    links.new(tex_image_node.outputs['Color'], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
    
    print("  - 投影仪节点设置完成。", flush=True)
    return projector

def load_patterns(pattern_path):
    """从指定路径加载所有图像作为投影图案"""
    print(f"从路径加载投影图案: {pattern_path}", flush=True)
    pattern_images = []
    if not os.path.isdir(pattern_path):
        print(f"错误: 投影图案路径不存在或不是一个目录: {pattern_path}", flush=True)
        return pattern_images
        
    # 支持多种图像格式
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
    
    for img_name in sorted(os.listdir(pattern_path)):
        if img_name.lower().endswith(supported_formats):
            try:
                img_path = os.path.join(pattern_path, img_name)
                # 检查图像是否已加载
                img = bpy.data.images.get(img_name)
                if not img:
                    img = bpy.data.images.load(img_path)
                else:
                    img.reload() # 重新加载以确保是最新版本
                pattern_images.append(img)
                print(f"  - 成功加载图案: {img_name}", flush=True)
            except Exception as e:
                print(f"警告: 加载投影图案失败: {img_name}. 错误: {e}", flush=True)
    
    if not pattern_images:
        # 如果没有找到支持格式的图像，尝试列出目录内容进行调试
        try:
            files = os.listdir(pattern_path)
            print(f"  - 目录中的文件列表: {files}", flush=True)
        except Exception as e:
            print(f"  - 无法列出目录内容: {e}", flush=True)
            
    print(f"共加载 {len(pattern_images)} 个图案。", flush=True)
    return pattern_images

def load_stl(stl_path):
    """加载单个STL文件"""
    print(f"加载STL文件: {stl_path}", flush=True)
    if not os.path.exists(stl_path):
        print(f"错误: STL文件不存在: {stl_path}", flush=True)
        return None
    
    bpy.ops.wm.stl_import(filepath=stl_path)
    print(f"  - 成功导入: {os.path.basename(stl_path)}", flush=True)
    return bpy.context.selected_objects[0]

def setup_object(obj):
    """设置导入的物体"""
    print(f"设置物体: {obj.name}", flush=True)
    # 确保物体在原点
    obj.location = (0, 0, 0)
    # 添加平滑着色
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    print("  - 应用平滑着色。", flush=True)
    # 可以添加或修改材质
    mat = bpy.data.materials.new(name="DefaultMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
        bsdf.inputs['Roughness'].default_value = 0.7
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat
    print("  - 设置默认材质。", flush=True)

def render_ambient(obj, output_path, stl_file):
    """渲染环境光"""
    print("开始渲染环境光...", flush=True)
    # 隐藏投影仪
    if 'Projector' in bpy.data.objects:
        bpy.data.objects['Projector'].hide_render = True
    
    # 设置输出文件名
    base_name = os.path.splitext(stl_file)[0]
    filename = f"{base_name}_ambient.png"
    filepath = os.path.join(output_path, filename)
    bpy.context.scene.render.filepath = filepath
    
    # 渲染
    print(f"  - 正在渲染环境光到: {filepath}", flush=True)
    bpy.ops.render.render(write_still=True)
    print(f"  - 环境光渲染完成。", flush=True)


def render_projection(obj, projector, pattern_images, output_path, stl_file, angle):
    """为单个物体在特定角度下渲染所有投影图案"""
    print(f"    开始渲染投影，角度: {angle}", flush=True)
    projector.hide_render = False
    
    base_name = os.path.splitext(stl_file)[0]
    
    for i, pattern_image in enumerate(pattern_images):
        # 设置投影图案
        node_tree = projector.data.node_tree
        tex_image_node = node_tree.nodes.get('Image Texture')
        if tex_image_node:
            tex_image_node.image = pattern_image
            print(f"      - 应用图案: {pattern_image.name}", flush=True)

        # 设置输出文件名
        # 文件名格式: 模型名_角度_图案序号_pattern.png
        filename = f"{base_name}_{angle:03d}_{i+1:06d}_pattern.png"
        filepath = os.path.join(output_path, filename)
        bpy.context.scene.render.filepath = filepath
        
        # 渲染
        print(f"      - 正在渲染到: {filepath}", flush=True)
        bpy.ops.render.render(write_still=True)
        print(f"      - 渲染完成。", flush=True)

    projector.hide_render = True
    print(f"    投影渲染完成。", flush=True)


# --- Main Logic ---

def main_script_logic(config_path):
    try:
        print(f"开始执行Blender脚本...", flush=True)
        config = load_config(config_path)
        print(f"成功加载配置文件: {config_path}", flush=True)

        # --- 1. 从配置中读取所有参数 ---
        print("--- 开始解析配置参数 ---", flush=True)
        paths = config.get("paths", {})
        stl_model_path = paths.get('stl_folder', "D:/blender-tool/test_data/stl_models")
        pattern_path = paths.get('pattern_folder', "D:/blender-tool/test_data/patterns")
        output_path = paths.get('output_folder', "D:/blender-tool/test_data/output")
        
        camera_config = config.get("camera", {})
        projector_config = config.get("projector", {})
        render_config = config.get("render", {})
        advanced_config = config.get("advanced", {})

        rotation_angles = advanced_config.get('rotation_angles', [0, 45, 90])
        render_samples = render_config.get('samples', 128)
        resolution = render_config.get('resolution', [1920, 1080])
        resolution_x, resolution_y = resolution
        render_engine = render_config.get('engine', 'CYCLES')

        print(f"  - STL模型路径: {stl_model_path}", flush=True)
        print(f"  - 投影图案路径: {pattern_path}", flush=True)
        print(f"  - 输出路径: {output_path}", flush=True)
        print(f"  - 旋转角度: {rotation_angles}", flush=True)
        print(f"  - 渲染采样数: {render_samples}", flush=True)
        print(f"  - 分辨率: {resolution_x}x{resolution_y}", flush=True)
        print("--- 参数解析完成 ---", flush=True)

        # --- 2. 设置渲染和场景 ---
        print("--- 开始设置渲染和场景 ---", flush=True)
        # 设置渲染引擎
        bpy.context.scene.render.engine = render_engine
        bpy.context.view_layer.update()

        if bpy.context.scene.render.engine == 'CYCLES':
            print("  - 渲染引擎成功设置为 CYCLES", flush=True)
            try:
                if hasattr(bpy.context.scene.render, 'cycles'):
                    bpy.context.scene.render.cycles.device = 'GPU'
                    print("  - 渲染设备设置为 GPU", flush=True)
                else:
                    print("  - 警告：Cycles属性不可用，将使用默认设置", flush=True)
            except AttributeError as e:
                print(f"  - 警告：无法设置GPU渲染，可能是因为Blender版本或GPU不支持，将使用CPU渲染: {e}", flush=True)
                if hasattr(bpy.context.scene.render, 'cycles'):
                    bpy.context.scene.render.cycles.device = 'CPU'
            
            if hasattr(bpy.context.scene.render, 'cycles'):
                bpy.context.scene.render.cycles.samples = render_samples
        else:
            print(f"  - 警告：渲染引擎未能设置为CYCLES，当前引擎：{bpy.context.scene.render.engine}", flush=True)
            
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_depth = '8'
        print(f"  - 渲染采样数设置为: {render_samples}", flush=True)
        print(f"  - 分辨率设置为: {resolution_x}x{resolution_y}", flush=True)
        
        cleanup_scene()
        
        camera = setup_camera(camera_config)
        projector = setup_projector(projector_config)
        print("--- 渲染和场景设置完成 ---", flush=True)

        # --- 3. 加载资产 ---
        print("--- 开始加载资产 ---", flush=True)
        pattern_images = load_patterns(pattern_path)
        if not pattern_images:
            print("错误：未能加载任何投影图案，脚本终止。", flush=True)
            return

        stl_files = [f for f in os.listdir(stl_model_path) if f.endswith('.stl')]
        if not stl_files:
            print("错误：在指定路径下未找到STL文件，脚本终止。", flush=True)
            return
        print(f"  - 找到 {len(stl_files)} 个STL文件待处理。", flush=True)
        print("--- 资产加载完成 ---", flush=True)

        # --- 4. 主循环 ---
        print("--- 开始进入主渲染循环 ---", flush=True)
        total_files = len(stl_files)
        for i, stl_file in enumerate(stl_files):
            print(f"--- 开始处理文件 {i+1}/{total_files}: {stl_file} ---", flush=True)
            obj = load_stl(os.path.join(stl_model_path, stl_file))
            if not obj:
                print(f"  警告：加载STL文件失败: {stl_file}，跳过此文件。", flush=True)
                continue
            
            setup_object(obj)

            # 渲染环境光 (每个模型一次)
            render_ambient(obj, output_path, stl_file)

            # 遍历旋转角度
            for angle in rotation_angles:
                print(f"  -- 开始处理旋转角度: {angle} 度 --", flush=True)
                obj.rotation_euler.z = math.radians(angle)
                bpy.context.view_layer.update()
                print(f"    - 物体Z轴旋转设置为 {angle} 度", flush=True)

                # 渲染投影
                render_projection(obj, projector, pattern_images, output_path, stl_file, angle)
            
            # 循环结束后重置旋转
            obj.rotation_euler.z = 0
            
            # 清理加载的物体
            bpy.data.objects.remove(obj)
            # 清理关联的网格数据
            bpy.data.meshes.remove(obj.data)
            print(f"  - 已清理加载的物体和网格数据。", flush=True)
            print(f"--- 文件 {stl_file} 处理完毕 ---", flush=True)

        print("--- 所有渲染任务完成 ---", flush=True)

    except Exception as e:
        print(f"脚本执行过程中发生严重错误: {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)


# --- Script Entry Point ---

if __name__ == "__main__":
    try:
        # 获取传递的配置文件路径
        config_file_path = ""
        if "--" in sys.argv:
            config_file_path = sys.argv[sys.argv.index("--") + 1]
        else:
            # Fallback for testing directly in Blender
            print("警告：未通过命令行 '--' 传入配置文件路径。", flush=True)
            print("将使用默认路径 'D:/blender-tool/配置.json'", flush=True)
            config_file_path = "D:/blender-tool/配置.json"

        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"配置文件不存在: {config_file_path}")

        main_script_logic(config_file_path)

    except Exception as e:
        error_message = f"""启动脚本时发生致命错误: {e}
{traceback.format_exc()}"""
        print(error_message, flush=True)
        # 在Blender环境中，可能需要不同的方式来记录顶层错误
        log_dir = "D:/blender-tool/logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "fatal_error.log"), "w") as f:
            f.write(error_message)