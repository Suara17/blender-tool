with open('logs/blender_dataset_gui.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(''.join(lines[-20:]))