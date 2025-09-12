#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试BlenderMCPIntegration导入
"""

try:
    from blender_mcp_integration import BlenderMCPIntegration
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()