with open('blender_mcp_integration.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    replace_lines = [i+1 for i, line in enumerate(lines) if 'replace' in line]
    print("Lines containing 'replace':", replace_lines)
    
    for line_num in replace_lines:
        print(f"Line {line_num}: {lines[line_num-1].strip()}")