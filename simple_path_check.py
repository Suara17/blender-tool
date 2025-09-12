#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

# 读取配置文件
with open('配置.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

paths = config.get('paths', {})
print('配置文件中的路径:')
for key, path in paths.items():
    exists = '存在' if os.path.exists(path) else '不存在'
    print(f'{key}: {path} - {exists}')