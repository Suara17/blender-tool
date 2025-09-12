类别,参数名,默认值/设置值,描述
相机,SCENE_CAMERA_NAME,"""Camera""",相机对象的名称。
相机,CAMERA_DEFAULT_LOC,"(-1, -3, 0)","相机的默认位置坐标（X, Y, Z）。"
相机,CAMERA_DEFAULT_ROT_DEG,"(90, 0, -17)","相机的默认旋转角度（度，X, Y, Z轴）。"
相机,CAMERA_DEFAULT_SCALE,"(1.0, 1.0, 1.0)","相机的默认缩放比例（X, Y, Z）。"
相机,CAMERA_DEFAULT_TYPE,'PERSP',相机类型（透视 'PERSP' 或正交 'ORTHO'）。
相机,CAMERA_DEFAULT_LENS_UNIT,'MILLIMETERS',相机焦距单位（毫米）。
相机,CAMERA_DEFAULT_FOCAL_LENGTH,50.0,相机焦距（毫米）。
相机,CAMERA_CLIP_START,0.1,相机近裁剪平面距离（米）。
相机,CAMERA_CLIP_END,15.0,相机远裁剪平面距离（米）。
投影仪,PROJECTOR_PARENT_NAME,"""Projector""",投影仪父级对象的名称。
投影仪,PROJECTOR_LIGHT_NAME,"""Projector.Spot""",投影仪灯光对象的名称。
投影仪,PROJECTOR_PARENT_DEFAULT_LOC,"(1, -3, 0)","投影仪父级默认位置坐标（X, Y, Z）。"
投影仪,PROJECTOR_PARENT_DEFAULT_ROT_DEG,"(90, 0, 2)","投影仪父级默认旋转角度（度，X, Y, Z轴）。"
投影仪,PROJECTOR_PARENT_DEFAULT_SCALE,"(1.0, 1.0, 1.0)","投影仪父级默认缩放比例（X, Y, Z）。"
投影仪,PROJECTOR_NODE_GROUP_DEFINITION_NAME,"""_Projector.001""",投影仪节点组定义名称。
投影仪,PROJECTOR_NODE_GROUP_INSTANCE_NAME_IN_LIGHT,"""_Projector.001""",投影仪灯光中节点组实例名称。
投影仪,PROJECTOR_IMAGE_TEXTURE_NODE_NAME,"""Image Texture""",投影仪图像纹理节点名称。
投影仪,PROJECTOR_EMISSION_NODE_NAME,"""Emission""",投影仪发射节点名称。
投影仪,ADDON_PROJECTOR_OPERATOR_NAME,"""projector.create""",创建投影仪的Blender操作符名称。
投影仪,PROJECTOR_FOCAL_LENGTH_FIXED,0.7,投影仪固定焦距（纹理缩放值，较小值表示广角）。
投影仪,PROJECTOR_POWER_NOMINAL,4.5,投影仪标称功率（模式1使用）。
投影仪,PROJECTOR_POWER_DRIFT,0.5,投影仪功率漂移范围（模式1使用）。
投影仪,PROJECTOR_POWER_LEVELS,"[5.0, 8.0, 10.0]",投影仪功率离散档位（模式2使用）。
投影仪,USE_DISCRETE_POWER_LEVELS,False,是否使用离散功率档位（True为模式2，False为模式1）。
投影仪,projector_emission_strength,20.0,投影仪发射强度（初始值，但会被随机化覆盖）。
投影仪,projector_pattern_rotation_z_deg,0.0,投影仪图案Z轴旋转角度（度）。
投影仪,PRJECTOR_PATTERN_ROTATION_Z_DEG,0.0,投影仪图案Z轴旋转角度（度，可能为拼写错误，重复参数）。
物体,CURRENT_STL_TARGET_NAME,"""Current_Imported_STL""",当前导入STL对象的名称前缀。
物体,STL_TARGET_LOCATION,"(0.6, 0.0, 0.0)","STL物体目标位置坐标（X, Y, Z）。"
物体,STL_TARGET_LARGEST_DIMENSION,1.5,STL物体最大维度目标大小（用于缩放）。
物体,stl_model_folder,"""D:/深度学习资料/实验记录/blender/3D_Models/Thingi10K""",STL模型文件夹路径。
背景/环境,REFERENCE_PLANE_NAME,"""ReferencePlane""",参考平面对象的名称。
背景/环境,HDRI_ENVIRONMENT_MAP_PATH,"""D:/深度学习资料/实验记录/blender/HDRI/brown_photostudio_02_4k.hdr""",HDRI环境贴图路径（代码中被注释，实际使用纯黑背景）。
背景/环境,AMBIENT_STRENGTH_BASELINE,0.5,环境光基准强度。
背景/环境,AMBIENT_STRENGTH_VARIATION,0.1,环境光强度波动范围。
渲染设置,render_width,640,渲染分辨率宽度（像素）。
渲染设置,render_height,640,渲染分辨率高度（像素）。
渲染设置,render_samples,512,渲染采样数（非DL模式）。
渲染设置,use_cycles,True,是否使用Cycles渲染引擎（True为Cycles，False为Eevee）。
渲染设置,dl_mode,False,是否启用DL训练模式。
渲染设置,dl_train_samples,512,DL训练模式下的采样数。
渲染设置,dl_filter_type,'GAUSSIAN',DL模式像素过滤器类型。
渲染设置,dl_filter_width,1.5,DL模式像素过滤器宽度。
输出,output_dir,"""D:/深度学习资料/实验记录/blender/Output/pattern""",主输出目录路径（图案图像）。
输出,image_pattern_folder,"""D:/深度学习资料/实验记录/blender/CompositePattern""",投影图案图像文件夹路径。
输出,depth_output_dir_abs,"""D:/深度学习资料/实验记录/blender/Output/depth""",深度图输出目录路径。
输出,AMBIENT_RGB_OUTPUT_DIR,"""D:/深度学习资料/实验记录/blender/Output/ambient""",环境光RGB图像输出目录路径。
输出,PARAMS_OUTPUT_FILE,"os.path.join(os.path.dirname(output_dir), ""scene_parameters.json"")",场景参数JSON文件路径。