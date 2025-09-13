import bpy
import os
import math
import glob
from mathutils import Vector, Matrix, Quaternion
import traceback
import random
import json


# --- 预期的对象名称常量 ---
SCENE_CAMERA_NAME = "Camera"
PROJECTOR_PARENT_NAME = "Projector"
PROJECTOR_LIGHT_NAME = "Projector.Spot"
CURRENT_STL_TARGET_NAME = "Current_Imported_STL"
PROJECTOR_NODE_GROUP_DEFINITION_NAME = "_Projector.001"
PROJECTOR_NODE_GROUP_INSTANCE_NAME_IN_LIGHT = "_Projector.001"
PROJECTOR_IMAGE_TEXTURE_NODE_NAME = "Image Texture"
PROJECTOR_EMISSION_NODE_NAME = "Emission"
ADDON_PROJECTOR_OPERATOR_NAME = "projector.create"
REFERENCE_PLANE_NAME = "ReferencePlane"


# ############################################################################
# --- 【核心修改】所有长度单位已从米转换为厘米 (原数值 x 100) ---
# ############################################################################
CAMERA_DEFAULT_LOC = (-100, -300, 0) # 原: (-1, -3, 0)
CAMERA_DEFAULT_ROT_DEG = (90, 0, -17)
CAMERA_DEFAULT_SCALE = (1.0, 1.0, 1.0)
CAMERA_DEFAULT_TYPE = 'PERSP'
CAMERA_DEFAULT_LENS_UNIT = 'MILLIMETERS'
CAMERA_DEFAULT_FOCAL_LENGTH = 50.0
CAMERA_CLIP_START = 10.0 # 原: 0.1
CAMERA_CLIP_END = 1500.0 # 原: 15.0


PROJECTOR_PARENT_DEFAULT_LOC = (100, -300, 0) # 原: (1, -3, 0)
PROJECTOR_PARENT_DEFAULT_ROT_DEG = (90, 0, 2)
PROJECTOR_PARENT_DEFAULT_SCALE = (1.0, 1.0, 1.0)


STL_TARGET_LOCATION = (60, 0.0, 0.0) # 原: (0.6, 0.0, 0.0)
STL_TARGET_LARGEST_DIMENSION = 150.0 # 原: 1.5
# ############################################################################


# --- 配置参数 ---
output_dir = r"E:\zr_network\blender\output\pattern"
image_pattern_folder = r"E:\zr_network\blender\composite_pattern\1"
stl_model_folder = r"E:\zr_network\blender\Thingi10K\selectmodel"
depth_output_dir_abs = r"E:\zr_network\blender\output\depth"
HDRI_ENVIRONMENT_MAP_PATH = r"E:\zr_network\blender\HDRI\brown_photostudio_02_4k.hdr"
AMBIENT_RGB_OUTPUT_DIR = r"E:\zr_network\blender\output\ambient"
PARAMS_OUTPUT_FILE = os.path.join(os.path.dirname(output_dir), "scene_parameters.json")


# --- 核心修改：受控的随机化参数 ---
AMBIENT_STRENGTH_BASELINE = 0.5
AMBIENT_STRENGTH_VARIATION = 0.1


PROJECTOR_POWER_NOMINAL = 4.5
PROJECTOR_POWER_DRIFT = 0.5
PROJECTOR_POWER_LEVELS = [5.0, 8.0, 10.0]
USE_DISCRETE_POWER_LEVELS = False


# 以下参数将在每个STL处理时随机化
projector_emission_strength = 20.0
projector_pattern_rotation_z_deg = 0.0
PRJECTOR_PATTERN_ROTATION_Z_DEG = 0.0
PROJECTOR_FOCAL_LENGTH_FIXED = 0.7


render_width = 640
render_height = 640
render_samples = 512
use_cycles = True


dl_mode = False
dl_train_samples = 512
dl_filter_type = 'GAUSSIAN'
dl_filter_width = 1.5


# --- 全局变量 ---
g_projector_internal_mapping_node = None


# ############################################################################
# --- 【新增函数】设置场景单位为厘米 ---
# ############################################################################
def setup_scene_units():
    """Sets the scene units to Centimeters and adjusts the unit scale."""
    print("\n--- 设置场景单位为厘米 ---")
    scene = bpy.context.scene
    
    # 1. 设置单位系统为公制
    scene.unit_settings.system = 'METRIC'
    
    # 2. 设置长度显示单位为厘米
    scene.unit_settings.length_unit = 'CENTIMETERS'
    
    # 3. 设置全局单位比例 (1 Blender Unit = 0.01m = 1cm)
    scene.unit_settings.scale_length = 0.01
    
    print(" 场景单位已设置为厘米。")
    
    # 4. (可选但推荐) 调整3D视图网格以匹配新单位
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.grid_scale = 0.01
                    print(" 3D视图网格比例已调整。")
                    break
# ############################################################################


# --- 辅助函数 (保持不变) ---
def ensure_directory_exists(dir_path):
    if not dir_path:
        print("错误: 目录路径为空。")
        return False
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            print(f"已创建目录: {dir_path}")
        except Exception as e:
            print(f"创建目录 {dir_path} 时出错: {e}")
            return False
    return True


def setup_output_directory():
    if output_dir.startswith('//'):
        abs_output_dir = bpy.path.abspath(output_dir)
    else:
        abs_output_dir = output_dir
    if not ensure_directory_exists(abs_output_dir):
        print(f"创建主输出目录 {abs_output_dir} 时出错。")
        return None
    bpy.context.scene.render.filepath = os.path.join(abs_output_dir, "")
    return abs_output_dir


def setup_world_background(hdri_filepath_abs, z_rotation_degrees, strength):
    world = bpy.context.scene.world
    if world is None:
        new_world = bpy.data.worlds.new("BackgroundWorld")
        bpy.context.scene.world = new_world
        world = new_world

    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links

    for node in list(nodes):
        nodes.remove(node)

    background_node = nodes.new(type='ShaderNodeBackground')
    background_node.location = (0, 0)
    world_output_node = nodes.new(type='ShaderNodeOutputWorld')
    world_output_node.location = (200, 0)

    # 将后备背景色改为纯黑，以消除环境光
    background_node.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    background_node.inputs['Strength'].default_value = strength
    
    # 只连接背景节点到世界输出
    links.new(background_node.outputs['Background'], world_output_node.inputs['Surface'])


def setup_render_settings():
    print("配置渲染设置...")
    scene = bpy.context.scene
    image_settings = scene.render.image_settings
    if use_cycles:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = dl_train_samples if dl_mode else render_samples
        scene.cycles.pixel_filter_type = dl_filter_type
        scene.cycles.filter_width = dl_filter_width
        prefs = bpy.context.preferences
        if hasattr(prefs, 'addons') and 'cycles' in prefs.addons and hasattr(prefs.addons['cycles'].preferences, 'compute_device_type'):
            cprefs = prefs.addons['cycles'].preferences
            if cprefs.get_devices_for_type('CUDA') or cprefs.get_devices_for_type('OPTIX') or cprefs.get_devices_for_type('HIP') or cprefs.get_devices_for_type('METAL') or cprefs.get_devices_for_type('ONEAPI'):
                scene.cycles.device = 'GPU'
                print("   已尝试将Cycles渲染设备设置为GPU。")
            else:
                scene.cycles.device = 'CPU'
                print("   未检测到Cycles可用的GPU计算设备，将使用CPU。")
        else:
            print("   无法访问Cycles首选项以设置设备，将使用默认设备 (通常CPU)。")
        active_view_layer = scene.view_layers[scene.view_layers.keys()[0]] if scene.view_layers else None
        if active_view_layer:
            active_view_layer.use_pass_z = True
        else:
            print("警告: 场景中没有视图层，无法启用Z通道。")
    else:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = render_width
    scene.render.resolution_y = render_height
    image_settings.file_format = 'PNG'
    image_settings.color_mode = 'RGB'
    image_settings.color_depth = '16'
    image_settings.compression = 15
    scene.render.use_file_extension = True
    scene.render.use_render_cache = False
    scene.render.use_overwrite = True
    scene.render.use_placeholder = False
    print("渲染设置配置完成。")


def setup_compositor_nodes(abs_depth_output_path):
    print("设置合成器节点 (强制将深度保存到 R 通道)...")
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    
    for node in list(tree.nodes):
        tree.nodes.remove(node)
        
    render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
    render_layers_node.location = (0, 200)
    
    composite_node = tree.nodes.new(type='CompositorNodeComposite')
    composite_node.location = (600, 200)
    
    sep_color_node = tree.nodes.new(type='CompositorNodeSepRGBA')
    sep_color_node.location = (200, 0)

    file_output_node_depth = tree.nodes.new(type='CompositorNodeOutputFile')
    file_output_node_depth.name = "DepthOutputNode"
    file_output_node_depth.location = (600, 0)
    
    if not ensure_directory_exists(abs_depth_output_path):
        print(f"警告：无法创建或访问深度图输出路径 '{abs_depth_output_path}'。")
        return

    file_output_node_depth.base_path = abs_depth_output_path
    
    file_output_node_depth.format.file_format = 'OPEN_EXR'
    file_output_node_depth.format.color_mode = 'BW'
    file_output_node_depth.format.color_depth = '32'
    file_output_node_depth.format.exr_codec = 'ZIP'
    
    file_output_node_depth.file_slots.clear()
    depth_slot = file_output_node_depth.file_slots.new("depth_R_")

    tree.links.new(render_layers_node.outputs['Image'], composite_node.inputs['Image'])
    
    if 'Depth' in render_layers_node.outputs:
        tree.links.new(render_layers_node.outputs['Depth'], sep_color_node.inputs['Image'])
        tree.links.new(sep_color_node.outputs['R'], depth_slot)
        print("   成功连接深度图输出：RenderLayers -> Separate Color -> R -> File Output")
        print(f"  现在深度数据将被明确地保存到 EXR 文件的 'R' 通道中。")
    else:
        print("   严重警告：渲染层节点缺少 'Depth' 输出。请在视图层属性中启用Z通道！")

    print("合成器节点设置完成。")


def get_or_create_camera(name, loc, rot_deg, scale_val, cam_type, lens_unit, focal_length, clip_start, clip_end):
    cam_obj = bpy.data.objects.get(name)
    if not (cam_obj and cam_obj.type == 'CAMERA'):
        if cam_obj:
            print(f"找到对象 '{name}'，但它不是相机或无效。将移除并重新创建。")
            try:
                bpy.data.objects.remove(cam_obj, do_unlink=True)
            except Exception as e:
                print(f"移除旧对象 '{name}' 时出错: {e}")
        print(f"未找到扫描仪相机 '{name}'，将创建一个新的。")
        rot_rad = tuple(math.radians(d) for d in rot_deg)
        try:
            bpy.ops.object.camera_add(location=loc, rotation=rot_rad)
            cam_obj = bpy.context.object
            cam_obj.name = name
            cam_obj.scale = scale_val
            cam_obj.rotation_mode = 'XYZ'
        except Exception as e:
            print(f"创建相机 '{name}' 时出错: {e}")
            return None
            
    if cam_obj:
        cam_data = cam_obj.data
        cam_data.type = cam_type
        if cam_type == 'PERSP':
            cam_data.lens_unit = lens_unit
            cam_data.lens = focal_length
        elif cam_type == 'ORTHO':
            cam_data.ortho_scale = 4.0
        
        cam_data.clip_start = clip_start
        cam_data.clip_end = clip_end
        
        bpy.context.scene.camera = cam_obj
    return cam_obj


def get_pattern_images(folder_path):
    abs_folder_path = bpy.path.abspath(folder_path)
    if not os.path.isdir(abs_folder_path):
        print(f"错误：在 '{abs_folder_path}' 未找到图案图像文件夹")
        return []
    supported_extensions = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff"]
    image_files = []
    for ext in supported_extensions:
        image_files.extend(glob.glob(os.path.join(abs_folder_path, ext)))
    image_files.sort()
    if not image_files:
        print(f"在 '{abs_folder_path}' 中未找到具有支持扩展名的图像图案。")
    return image_files


def project_and_render_via_nodes(image_texture_node, emission_node, pattern_image_filepath, output_filename_base, current_output_dir_abs):
    if not image_texture_node or not emission_node:
        print("错误：未提供用于渲染的图像纹理节点或发射节点。")
        return False
    if pattern_image_filepath:
        try:
            image_data_block = bpy.data.images.load(pattern_image_filepath, check_existing=True)
            image_texture_node.image = image_data_block
        except RuntimeError as e:
            print(f"错误：加载图像 '{pattern_image_filepath}' 到图像纹理节点时出错：{e}")
            if emission_node.inputs['Strength'].default_value > 0:
                return False
    elif emission_node.inputs['Strength'].default_value > 0:
        print(f"错误: 投影仪发射强度 > 0 但未提供 pattern_image_filepath。")
        return False
    render_filepath_full_base = os.path.join(current_output_dir_abs, output_filename_base)
    bpy.context.scene.render.filepath = render_filepath_full_base
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print(f"渲染到 '{render_filepath_full_base}' 时发生严重错误: {e}")
        print(traceback.format_exc())
        return False
    return True


def get_stl_files_from_folder(folder_path):
    abs_folder_path = bpy.path.abspath(folder_path)
    if not os.path.isdir(abs_folder_path):
        print(f"错误：STL模型文件夹 '{abs_folder_path}' 未找到或不是一个有效文件夹。")
        return []
    stl_files = glob.glob(os.path.join(abs_folder_path, "*.stl"))
    stl_files.sort()
    if not stl_files:
        print(f"在文件夹 '{abs_folder_path}' 中未找到任何STL文件。")
    return stl_files


def clear_object_by_name(object_name):
    obj_to_delete = bpy.data.objects.get(object_name)
    if obj_to_delete:
        try:
            bpy.data.objects.remove(obj_to_delete, do_unlink=True)
            return True
        except (ReferenceError, Exception) as e:
            print(f"   删除对象 '{object_name}' 时发生错误: {e}")
            return False
    return False


def import_and_prepare_stl(stl_filepath, desired_object_name_base, target_location_center, target_largest_dimension):
    print(f"正在导入STL文件: {os.path.basename(stl_filepath)}...")
    try:
        bpy.ops.wm.stl_import(filepath=stl_filepath)
    except Exception as e:
        print(f"错误：无法导入STL文件 '{stl_filepath}': {e}")
        print(traceback.format_exc())
        return None
    
    if not bpy.context.selected_objects:
        print(f"错误：导入STL '{stl_filepath}' 后没有选中任何对象。")
        return None

    temp_imported_objects = list(bpy.context.selected_objects)
    all_imported_meshes = [obj for obj in temp_imported_objects if obj.type == 'MESH']
    
    if not all_imported_meshes:
        print(f"错误：STL '{stl_filepath}' 未包含任何有效网格数据。")
        return None

    parent_empty = bpy.data.objects.new(f"{desired_object_name_base}_ROOT", None)
    bpy.context.collection.objects.link(parent_empty)

    for i, mesh_obj in enumerate(all_imported_meshes):
        mesh_obj.name = f"{desired_object_name_base}_part{i}"
        mesh_obj.parent = parent_empty
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        mesh_obj.location = (0,0,0)

    bpy.context.view_layer.update()

    min_overall_local = Vector((float('inf'), float('inf'), float('inf')))
    max_overall_local = Vector((float('-inf'), float('-inf'), float('-inf')))
    
    for mesh_obj_child in parent_empty.children:
        if mesh_obj_child.type == 'MESH' and mesh_obj_child.data and mesh_obj_child.data.vertices:
            for corner_local_to_mesh in mesh_obj_child.bound_box:
                corner_in_parent_space = mesh_obj_child.matrix_basis @ Vector(corner_local_to_mesh)
                min_overall_local = Vector(min(c1, c2) for c1, c2 in zip(min_overall_local, corner_in_parent_space))
                max_overall_local = Vector(max(c1, c2) for c1, c2 in zip(max_overall_local, corner_in_parent_space))

    center_of_geometry_local_to_parent = (min_overall_local + max_overall_local) / 2.0
    for mesh_obj_child in parent_empty.children:
        if mesh_obj_child.type == 'MESH':
            mesh_obj_child.location -= center_of_geometry_local_to_parent
    
    bpy.context.view_layer.update()

    # Re-calculate bounds after centering
    min_overall_local = Vector((float('inf'), float('inf'), float('inf')))
    max_overall_local = Vector((float('-inf'), float('-inf'), float('-inf')))
    for mesh_obj_child in parent_empty.children:
        if mesh_obj_child.type == 'MESH' and mesh_obj_child.data and mesh_obj_child.data.vertices:
            for corner_local_to_mesh in mesh_obj_child.bound_box:
                corner_in_parent_space = mesh_obj_child.matrix_basis @ Vector(corner_local_to_mesh)
                min_overall_local = Vector(min(c1, c2) for c1, c2 in zip(min_overall_local, corner_in_parent_space))
                max_overall_local = Vector(max(c1, c2) for c1, c2 in zip(max_overall_local, corner_in_parent_space))

    dims_local_centered = max_overall_local - min_overall_local
    largest_dim_local = max(dims_local_centered) if any(d > 1e-7 for d in dims_local_centered) else 0

    if largest_dim_local > 1e-7:
        scale_factor = target_largest_dimension / largest_dim_local
        parent_empty.scale = (scale_factor, scale_factor, scale_factor)
    else:
        print(f"警告：对象 '{parent_empty.name}' 的维度过小或为零。不进行缩放。")
        parent_empty.scale = (1.0, 1.0, 1.0)

    parent_empty.location = target_location_center
    parent_empty.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

    mat_name = f"Mat_{desired_object_name_base}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    
    if not mat.use_nodes:
        mat.use_nodes = True
        mat.node_tree.nodes.clear()
        bsdf_node = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        output_node = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    bsdf_node = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    
    random_gray_color = random.uniform(0.1, 0.9)
    bsdf_node.inputs['Base Color'].default_value = (random_gray_color, random_gray_color, random_gray_color, 1.0)
    bsdf_node.inputs['Roughness'].default_value = random.uniform(0.4, 1.0)
    bsdf_node.inputs['Specular IOR Level'].default_value = random.uniform(0.0, 0.5)
    bsdf_node.inputs['Metallic'].default_value = 0.0

    for mesh_obj_child in parent_empty.children:
        if mesh_obj_child.type == 'MESH':
            if not mesh_obj_child.data.materials:
                mesh_obj_child.data.materials.append(mat)
            else:
                mesh_obj_child.data.materials[0] = mat
                
    return parent_empty


def add_reference_plane_world_position(camera_obj):
    if REFERENCE_PLANE_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[REFERENCE_PLANE_NAME], do_unlink=True)
        print(f"已移除旧的参考平面 '{REFERENCE_PLANE_NAME}'。")

    print("正在创建具有固定变换的参考平面...")
    
    try:
        # --- 【核心修改】平面尺寸和位置已转换为厘米 ---
        size = 1000.0 # 原: 10.0
        verts = [(-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0)]
        faces = [(0, 1, 2, 3)]
        plane_mesh = bpy.data.meshes.new(name=f"Mesh_{REFERENCE_PLANE_NAME}")
        plane_obj = bpy.data.objects.new(REFERENCE_PLANE_NAME, plane_mesh)
        plane_mesh.from_pydata(verts, [], faces)
        plane_mesh.update()
        bpy.context.scene.collection.objects.link(plane_obj)
        
        plane_obj.location = (100, 300, 0) # 原: (1, 3, 0)
        plane_obj.rotation_mode = 'XYZ'
        plane_obj.rotation_euler = (math.radians(90), 0, 0)
        plane_obj.scale = (1.0, 1.0, 1.0)

        print(f"   已将参考平面的位置设置为: {plane_obj.location}")
        print(f"   已将参考平面的旋转(度)设置为: (90, 0, 0)")

    except Exception as e:
        print(f"创建或设置参考平面时出错: {e}")
        traceback.print_exc()
        return None

    mat_name = f"Mat_{REFERENCE_PLANE_NAME}"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        nt.nodes.clear()
        bsdf = nt.nodes.new(type='ShaderNodeBsdfPrincipled')
        output_node = nt.nodes.new(type='ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 1.0
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Specular IOR Level'].default_value = 0.0

    if not plane_obj.data.materials:
        plane_obj.data.materials.append(mat)
    else:
        plane_obj.data.materials[0] = mat

    print(f"参考平面 '{plane_obj.name}' 已创建并设置固定变换。")
    return plane_obj


def place_object_on_plane(target_obj_root, reference_plane_obj):
    if not target_obj_root or not reference_plane_obj:
        print("错误 (place_object_on_plane): 传入的对象无效。")
        return

    print("   正在计算物体位置以放置在参考平面上...")
        
    plane_location = reference_plane_obj.location
    plane_normal = reference_plane_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    plane_normal.normalize()

    world_corners = []
    bpy.context.view_layer.update()
    
    mesh_children = [child for child in target_obj_root.children if child.type == 'MESH' and child.data and child.data.vertices]
    if not mesh_children:
        print("   警告：当前对象没有可计算的几何体子节点，跳过放置步骤。")
        return

    for mesh_child in mesh_children:
        for corner_local in mesh_child.bound_box:
            world_corners.append(mesh_child.matrix_world @ Vector(corner_local))

    min_projection = min(corner.dot(plane_normal) for corner in world_corners)
    
    plane_point_projection = plane_location.dot(plane_normal)
    
    # --- 【核心修改】偏移量已从米转换为厘米 ---
    z_offset = 0.1 # 原: 0.001
    
    offset_distance = plane_point_projection - min_projection + z_offset
    translation_vector = offset_distance * plane_normal
    
    target_obj_root.location += translation_vector
    bpy.context.view_layer.update()
    print(f"   物体已移动以放置在平面上 (沿法线移动距离: {offset_distance:.4f})。")


def rename_files_sequentially(folder_path, base_name_prefix="image"):
    print(f"\n--- 尝试在文件夹中重命名文件: {folder_path} 使用前缀 '{base_name_prefix}' ---")
    if not (folder_path and os.path.isdir(folder_path)):
        print(f"错误: 文件夹 '{folder_path}' 无效。跳过 '{base_name_prefix}' 的重命名。")
        return
    
    image_extensions = ('.png', '.jpg', '.jpeg', '.exr', '.tif', '.tiff', '.bmp')
    try:
        image_files_to_rename = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)])
    except Exception as e:
        print(f"错误: 列出目录 '{folder_path}' 时发生错误: {e}")
        return

    if not image_files_to_rename:
        print(f"在 '{folder_path}' 中未找到图像文件进行 '{base_name_prefix}' 重命名。")
        return

    print(f"找到 {len(image_files_to_rename)} 个图像文件，准备在 '{folder_path}' 中进行 '{base_name_prefix}' 重命名。")
    renamed_count = 0
    padding_digits = 6
    for i, original_filename in enumerate(image_files_to_rename):
        old_filepath = os.path.join(folder_path, original_filename)
        _, extension = os.path.splitext(original_filename)
        new_indexed_filename = f"{base_name_prefix}_{i + 1:0{padding_digits}d}{extension}"
        new_filepath = os.path.join(folder_path, new_indexed_filename)
        
        if old_filepath == new_filepath:
            renamed_count +=1
            continue
        if os.path.exists(new_filepath):
            print(f"   警告: 目标文件 '{new_indexed_filename}' 已存在。跳过对 '{original_filename}' 的重命名。")
            continue
        try:
            os.rename(old_filepath, new_filepath)
            renamed_count += 1
        except Exception as e:
            print(f"   重命名 '{original_filename}' 到 '{new_indexed_filename}' 时发生错误: {e}")
    print(f"在 '{folder_path}' ({base_name_prefix}): 成功重命名/确认 {renamed_count} 个文件。")


def get_second_mapping_node_in_projector_group(projector_light_obj, group_node_instance_name_in_light, group_definition_name_fallback):
    if not (projector_light_obj and projector_light_obj.type == 'LIGHT' and projector_light_obj.data and projector_light_obj.data.use_nodes):
        print("错误 (get_second_mapping): 投影仪灯光无效或未使用节点。")
        return None
    
    main_light_material_tree = projector_light_obj.data.node_tree
    if not main_light_material_tree: return None

    node_group_instance = main_light_material_tree.nodes.get(group_node_instance_name_in_light)
    if not node_group_instance:
        for node in main_light_material_tree.nodes:
            if node.type == 'GROUP' and node.node_tree and node.node_tree.name == group_definition_name_fallback:
                node_group_instance = node
                break
    
    if not (node_group_instance and node_group_instance.type == 'GROUP' and node_group_instance.node_tree):
        return None

    internal_projector_node_tree = node_group_instance.node_tree
    mapping_nodes_in_group = sorted([node for node in internal_projector_node_tree.nodes if node.type == 'MAPPING'], key=lambda node: node.location.x)
    
    return mapping_nodes_in_group[1] if len(mapping_nodes_in_group) >= 2 else None


def adjust_projector_texture_scale_x(mapping_node_ref, scale_x_value):
    if not (mapping_node_ref and mapping_node_ref.type == 'MAPPING'): return False
    try:
        mapping_node_ref.inputs['Scale'].default_value.x = scale_x_value
        return True
    except Exception as e:
        print(f"错误: 调整Mapping节点 '{mapping_node_ref.name}' 的Scale X时发生错误: {e}")
        return False


def adjust_projector_texture_rotation_z(mapping_node_ref, angle_degrees):
    if not (mapping_node_ref and mapping_node_ref.type == 'MAPPING'): return False
    try:
        mapping_node_ref.inputs['Rotation'].default_value.z = math.radians(angle_degrees)
        return True
    except Exception as e:
        print(f"错误: 调整Mapping节点 '{mapping_node_ref.name}' 的Rotation Z时发生错误: {e}")
        return False


def record_parameters_to_file(filepath, camera_obj, projector_light_obj):
    print(f"\n--- 正在记录场景参数到: {filepath} ---")
    if not (camera_obj and camera_obj.type == 'CAMERA'):
        print("错误：无效的相机对象，无法记录参数。")
        return False
    if not (projector_light_obj and projector_light_obj.type == 'LIGHT'):
        print("错误：无效的投影仪灯光对象，无法记录参数。")
        return False

    bpy.context.view_layer.update()
    params = {}
    scene = bpy.context.scene
    cam_data = camera_obj.data
    
    sensor_width_mm = cam_data.sensor_width
    sensor_height_mm = cam_data.sensor_height
    focal_length_mm = cam_data.lens
    
    fx = (focal_length_mm / sensor_width_mm) * scene.render.resolution_x
    fy = (focal_length_mm / sensor_height_mm) * scene.render.resolution_y
    cx = scene.render.resolution_x / 2.0 + cam_data.shift_x * scene.render.resolution_x
    cy = scene.render.resolution_y / 2.0 + cam_data.shift_y * scene.render.resolution_y
    
    cam_extrinsic_matrix = camera_obj.matrix_world.inverted()
    
    k1_distortion = 0.0
    if scene.render.engine == 'CYCLES' and hasattr(scene.cycles, 'lens_distortion'):
        k1_distortion = scene.cycles.lens_distortion

    params['camera'] = {
        'name': camera_obj.name,
        'intrinsics': {
            'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy, 'skew': 0.0,
            'resolution_x': scene.render.resolution_x,
            'resolution_y': scene.render.resolution_y,
            'focal_length_mm': focal_length_mm,
            'sensor_width_mm': sensor_width_mm,
            'sensor_height_mm': sensor_height_mm,
            'clip_start': cam_data.clip_start,
            'clip_end': cam_data.clip_end,
        },
        'extrinsics': {'world_to_cam_matrix': [list(row) for row in cam_extrinsic_matrix]},
        'distortion': {'k1': k1_distortion, 'k2': 0.0, 'k3': 0.0, 'p1': 0.0, 'p2': 0.0}
    }
    
    proj_data = projector_light_obj.data
    projector_fov_deg = math.degrees(proj_data.spot_size)
    proj_extrinsic_matrix = projector_light_obj.matrix_world.inverted()
    params['projector'] = {
        'name': projector_light_obj.name,
        'parent_name': projector_light_obj.parent.name if projector_light_obj.parent else None,
        'intrinsics_equivalent': {
            'spot_angle_degrees': projector_fov_deg,
            'pattern_texture_folder': image_pattern_folder,
        },
        'extrinsics': {'world_to_proj_matrix': [list(row) for row in proj_extrinsic_matrix]}
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=4)
        print(f"场景参数已成功保存到: {filepath}")
        return True
    except Exception as e:
        print(f"错误：保存参数到 '{filepath}' 时失败: {e}")
        traceback.print_exc()
        return False


def render_reference_plane_depth_only(depth_output_path):
    print("\n" + "="*20 + " 开始渲染参考平面深度图 " + "="*20)
    
    stl_root_object = bpy.data.objects.get(f"{CURRENT_STL_TARGET_NAME}_ROOT")
    was_stl_root_hidden = False
    if stl_root_object:
        was_stl_root_hidden = stl_root_object.hide_render
        stl_root_object.hide_render = True
        print(f"   已临时隐藏STL对象: '{stl_root_object.name}'")

    ref_plane_obj = bpy.data.objects.get(REFERENCE_PLANE_NAME)
    if not ref_plane_obj:
        print("   严重错误：在场景中找不到参考平面，无法渲染其深度图。")
        if stl_root_object: stl_root_object.hide_render = was_stl_root_hidden
        return False
        
    was_plane_hidden = ref_plane_obj.hide_render
    ref_plane_obj.hide_render = False

    depth_output_node = bpy.context.scene.node_tree.nodes.get("DepthOutputNode")
    if not depth_output_node:
        print("   严重错误：找不到名为 'DepthOutputNode' 的合成器节点。")
        if stl_root_object: stl_root_object.hide_render = was_stl_root_hidden
        ref_plane_obj.hide_render = was_plane_hidden
        return False
        
    original_slot_path = depth_output_node.file_slots[0].path
    depth_output_node.file_slots[0].path = "depth_reference_plane"

    print("   准备渲染...")
    try:
        bpy.ops.render.render(write_still=True)
        print(f"   成功渲染参考平面深度图到: {os.path.join(depth_output_path, 'depth_reference_plane0001.exr')}")
    except Exception as e:
        print(f"   渲染参考平面时发生严重错误: {e}")
        traceback.print_exc()
    
    print("   正在恢复场景设置...")
    depth_output_node.file_slots[0].path = original_slot_path

    if stl_root_object:
        stl_root_object.hide_render = was_stl_root_hidden
        print(f"   已恢复STL对象 '{stl_root_object.name}' 的可见性。")
        
    ref_plane_obj.hide_render = was_plane_hidden
    
    print("="*24 + " 参考平面渲染结束 " + "="*24 + "\n")
    return True


# --- 主脚本执行 ---
def main_script_logic():
    global g_projector_internal_mapping_node
    global projector_texture_scale_x, projector_pattern_rotation_z_deg

    print("开始结构光脚本 (STL批量处理模式)...")
    
    # --- 【核心修改】在脚本开始时调用新函数以设置单位 ---
    setup_scene_units()
    
    clear_object_by_name(REFERENCE_PLANE_NAME)

    abs_main_output_dir = setup_output_directory()
    if not abs_main_output_dir:
        print("严重错误: 无法设置主输出目录。脚本终止。")
        return

    ensure_directory_exists(depth_output_dir_abs)
    ensure_directory_exists(AMBIENT_RGB_OUTPUT_DIR)

    pattern_image_files = get_pattern_images(image_pattern_folder)
    if not pattern_image_files:
        print("在图案文件夹中没有找到投影图案图像。脚本终止。")
        return

    stl_file_paths = get_stl_files_from_folder(stl_model_folder)
    if not stl_file_paths:
        print("在指定的STL模型文件夹中没有找到STL模型。脚本终止。")
        return

    print(f"找到 {len(pattern_image_files)} 个图案图像 和 {len(stl_file_paths)} 个STL模型。")

    print("\n--- 设置固定的相机和投影仪位置 ---")
    scanner_cam_obj = get_or_create_camera(
        SCENE_CAMERA_NAME,
        CAMERA_DEFAULT_LOC, CAMERA_DEFAULT_ROT_DEG, CAMERA_DEFAULT_SCALE,
        CAMERA_DEFAULT_TYPE, CAMERA_DEFAULT_LENS_UNIT, CAMERA_DEFAULT_FOCAL_LENGTH,
        CAMERA_CLIP_START, CAMERA_CLIP_END
    )
    if not scanner_cam_obj:
        print("严重错误：无法解析或创建扫描仪相机。脚本终止。")
        return
    
    projector_parent_obj = bpy.data.objects.get(PROJECTOR_PARENT_NAME)
    projector_light_emitter_obj = None
    image_tex_node = None
    emission_node = None
    
    if projector_parent_obj:
        potential_light_obj = bpy.data.objects.get(PROJECTOR_LIGHT_NAME)
        if (potential_light_obj and potential_light_obj.parent == projector_parent_obj and
                potential_light_obj.type == 'LIGHT' and potential_light_obj.data and
                potential_light_obj.data.type == 'SPOT' and potential_light_obj.data.node_tree):
            projector_light_emitter_obj = potential_light_obj
            node_tree = projector_light_emitter_obj.data.node_tree
            image_tex_node = node_tree.nodes.get(PROJECTOR_IMAGE_TEXTURE_NODE_NAME)
            emission_node = node_tree.nodes.get(PROJECTOR_EMISSION_NODE_NAME)

    if not (projector_light_emitter_obj and image_tex_node and emission_node):
        try:
            op_module_str, op_name_str = ADDON_PROJECTOR_OPERATOR_NAME.split('.', 1)
            getattr(getattr(bpy.ops, op_module_str), op_name_str)()
            bpy.context.view_layer.update()
            
            projector_parent_obj = bpy.data.objects.get(PROJECTOR_PARENT_NAME)
            if projector_parent_obj:
                projector_parent_obj.location = PROJECTOR_PARENT_DEFAULT_LOC
                projector_parent_obj.rotation_euler = tuple(math.radians(d) for d in PROJECTOR_PARENT_DEFAULT_ROT_DEG)
                
                light_children = [c for c in projector_parent_obj.children if c.type == 'LIGHT']
                if light_children:
                    projector_light_emitter_obj = light_children[0]
                    node_tree = projector_light_emitter_obj.data.node_tree
                    image_tex_node = next((n for n in node_tree.nodes if n.type == 'TEX_IMAGE'), None)
                    emission_node = next((n for n in node_tree.nodes if n.type == 'EMISSION'), None)

        except Exception as e_op:
            print(f"创建插件投影仪期间发生严重错误: {e_op}")
    
    if not (projector_parent_obj and projector_light_emitter_obj and image_tex_node and emission_node):
        print("\n严重失败：无法解析或创建相机或投影仪组件。脚本终止。")
        return
        
    print(f"相机 '{scanner_cam_obj.name}' 和投影仪 '{projector_parent_obj.name}' 位置已固定。")

    reference_plane_obj = add_reference_plane_world_position(scanner_cam_obj)
    if not reference_plane_obj:
        print("严重错误: 未能创建参考平面，无法进行物体放置。脚本终止。")
        return

    setup_render_settings()
    setup_compositor_nodes(depth_output_dir_abs)
    
    if not record_parameters_to_file(PARAMS_OUTPUT_FILE, scanner_cam_obj, projector_light_emitter_obj):
        print("严重警告：未能记录场景参数。后续的三维重建可能无法进行。")

    node_tree_to_modify = projector_light_emitter_obj.data.node_tree
    links_collection = node_tree_to_modify.links
    from_socket = image_tex_node.outputs.get('Color')
    to_socket = emission_node.inputs.get('Color')
    if from_socket and to_socket:
        for link in list(links_collection):
            if link.to_socket == to_socket:
                links_collection.remove(link)
        links_collection.new(from_socket, to_socket)
    
    if projector_light_emitter_obj.data.type == 'SPOT':
        projector_light_emitter_obj.data.spot_size = math.radians(60.0)
        projector_light_emitter_obj.data.show_cone = True

    g_projector_internal_mapping_node = get_second_mapping_node_in_projector_group(
        projector_light_emitter_obj,
        PROJECTOR_NODE_GROUP_INSTANCE_NAME_IN_LIGHT,
        PROJECTOR_NODE_GROUP_DEFINITION_NAME
    )
    if g_projector_internal_mapping_node:
        print(f"使用固定的投影仪焦距 (缩放X值): {PROJECTOR_FOCAL_LENGTH_FIXED}")
        adjust_projector_texture_scale_x(g_projector_internal_mapping_node, PROJECTOR_FOCAL_LENGTH_FIXED)
        adjust_projector_texture_rotation_z(g_projector_internal_mapping_node, projector_pattern_rotation_z_deg)
    else:
        print(f"警告: 未能找到投影仪节点组内部的目标Mapping节点。")
            
    render_reference_plane_depth_only(depth_output_dir_abs)

    pattern_render_id_counter = 0
    ambient_render_id_counter = 0
    current_stl_object_ref = None

    for stl_idx, stl_file_path in enumerate(stl_file_paths):
        print(f"\n--- 开始处理STL模型 {stl_idx + 1}/{len(stl_file_paths)}: {os.path.basename(stl_file_path)} ---")

        projector_texture_scale_x = PROJECTOR_FOCAL_LENGTH_FIXED
        projector_pattern_rotation_z_deg = PRJECTOR_PATTERN_ROTATION_Z_DEG
        
        min_strength = max(0, AMBIENT_STRENGTH_BASELINE - AMBIENT_STRENGTH_VARIATION)
        max_strength = AMBIENT_STRENGTH_BASELINE + AMBIENT_STRENGTH_VARIATION
        random_background_strength = random.uniform(min_strength, max_strength)
        
        if USE_DISCRETE_POWER_LEVELS:
            current_projector_power = random.choice(PROJECTOR_POWER_LEVELS)
        else:
            min_power = max(0, PROJECTOR_POWER_NOMINAL - PROJECTOR_POWER_DRIFT)
            max_power = PROJECTOR_POWER_NOMINAL + PROJECTOR_POWER_DRIFT
            current_projector_power = random.uniform(min_power, max_power)
            
        print(f"   本轮随机参数: 投影仪功率={current_projector_power:.2f}, 环境光强度={random_background_strength:.2f}")

        random_z_rot_env_map = random.uniform(0.0, 360.0)

        if current_stl_object_ref:
            clear_object_by_name(current_stl_object_ref.name)
        clear_object_by_name(f"{CURRENT_STL_TARGET_NAME}_ROOT")

        target_obj_root = import_and_prepare_stl(stl_file_path,
                                                 CURRENT_STL_TARGET_NAME,
                                                 STL_TARGET_LOCATION,
                                                 STL_TARGET_LARGEST_DIMENSION)
        if not target_obj_root:
            print(f"错误：无法导入或准备STL模型 '{os.path.basename(stl_file_path)}'。跳过。")
            continue
        current_stl_object_ref = target_obj_root
        
        if g_projector_internal_mapping_node:
            adjust_projector_texture_scale_x(g_projector_internal_mapping_node, projector_texture_scale_x)
            adjust_projector_texture_rotation_z(g_projector_internal_mapping_node, projector_pattern_rotation_z_deg)
        
        setup_world_background(None, random_z_rot_env_map, random_background_strength)

        initial_target_obj_matrix_world = target_obj_root.matrix_world.copy()
        #y_angle_orientations_deg = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        #z_angle_orientations_deg = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        y_angle_orientations_deg = [0.0, 45.0]
        z_angle_orientations_deg = [0.0]
        total_views_for_model = len(y_angle_orientations_deg) * len(z_angle_orientations_deg)
        current_view_count_for_model = 0

        for y_rot_deg in y_angle_orientations_deg:
            for z_rot_deg in z_angle_orientations_deg:
                current_view_count_for_model += 1
                print(f"\n   --- 模型 '{current_stl_object_ref.name}' - 视角 {current_view_count_for_model}/{total_views_for_model} (Y:{y_rot_deg}°, Z:{z_rot_deg}°) ---")

                loc, rot_quat, scale = initial_target_obj_matrix_world.decompose()
                mat_rot_Y_world = Matrix.Rotation(math.radians(y_rot_deg), 4, 'Y')
                mat_rot_Z_world = Matrix.Rotation(math.radians(z_rot_deg), 4, 'Z')
                target_obj_root.matrix_world = (Matrix.Translation(loc) @
                                                mat_rot_Z_world @ mat_rot_Y_world @
                                                rot_quat.to_matrix().to_4x4() @
                                                Matrix.Diagonal(scale).to_4x4())
                bpy.context.view_layer.update()

                place_object_on_plane(target_obj_root, reference_plane_obj)

                for pattern_idx, pattern_filepath in enumerate(pattern_image_files):
                    pattern_render_id_counter += 1
                    bpy.context.scene.frame_set(pattern_render_id_counter)
                    output_filename_base_pattern = f"{pattern_render_id_counter:06d}_pattern"

                    if bpy.context.scene.node_tree:
                        depth_out_node = bpy.context.scene.node_tree.nodes.get("DepthOutputNode")
                        if depth_out_node: depth_out_node.mute = False
                    
                    emission_node.inputs['Strength'].default_value = current_projector_power
                    if projector_light_emitter_obj:
                        projector_light_emitter_obj.hide_render = False

                    project_and_render_via_nodes(
                        image_tex_node, emission_node, pattern_filepath,
                        output_filename_base_pattern,
                        abs_main_output_dir
                    )

                ambient_render_id_counter += 1
                bpy.context.scene.frame_set(ambient_render_id_counter)
                output_filename_base_ambient = f"{ambient_render_id_counter:06d}_ambient"
                
                original_projector_strength = emission_node.inputs['Strength'].default_value
                emission_node.inputs['Strength'].default_value = 0.0
                
                if projector_light_emitter_obj:
                    projector_light_emitter_obj.hide_render = True
                    
                if bpy.context.scene.node_tree:
                    depth_out_node = bpy.context.scene.node_tree.nodes.get("DepthOutputNode")
                    if depth_out_node: depth_out_node.mute = True
                            
                project_and_render_via_nodes(
                    image_tex_node, emission_node,
                    pattern_image_files[0],
                    output_filename_base_ambient,
                    AMBIENT_RGB_OUTPUT_DIR
                )
                
                emission_node.inputs['Strength'].default_value = original_projector_strength
                if projector_light_emitter_obj:
                    projector_light_emitter_obj.hide_render = False
                if bpy.context.scene.node_tree:
                    depth_out_node = bpy.context.scene.node_tree.nodes.get("DepthOutputNode")
                    if depth_out_node: depth_out_node.mute = False

    if current_stl_object_ref:
        print(f"\n处理完所有STL，正在清理最后一个导入的模型: {current_stl_object_ref.name}")
        clear_object_by_name(current_stl_object_ref.name)

    print("\n--- 所有STL模型处理完毕。 ---")
    
    print("\n开始对输出文件夹中的图像进行重命名...")
    if abs_main_output_dir:
        rename_files_sequentially(abs_main_output_dir, "pattern")
    if depth_output_dir_abs:
        print(f"提醒：深度图文件夹 '{depth_output_dir_abs}' 的重命名操作已跳过，以保留 'depth_reference_plane.exr'。")
    if AMBIENT_RGB_OUTPUT_DIR:
        rename_files_sequentially(AMBIENT_RGB_OUTPUT_DIR, "ambient")

    print("\n--- 脚本执行完毕。 ---")


# --- 脚本入口点 ---
if __name__ == "__main__":
    try:
        main_script_logic()
    except Exception as e:
        print("\n" + "="*30 + " SCRIPT ERROR " + "="*30)
        print(f"脚本执行过程中发生未处理的错误: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()
        print("="*74)
    finally:
        print("脚本主要逻辑执行完成或因错误中止。")
