"""
配置管理模块 - 处理配色方案和地图比例尺的加载与保存
"""

import os
import yaml

# 默认配色方案
DEFAULT_COLOR_SCHEME = {
    "background": "#000000",
    "primary": "#00FFFF",
    "secondary": "#FF7F00",
    "contour": "#00FFFF",
    "highlight_contour": "#FFFFFF",
    "grid": "#0000FF",
    "scan_line": "#00FFFF",
    "cross": "#00FFFF",
    "corner": "#00FFFF",
    "colormap": "plasma"
}

# 默认地图比例尺 - 根据实际地图比例设置
DEFAULT_MAP_SCALE = {
    "width_km": 10.61,
    "height_km": 10.61,
    "max_elevation_km": 1.33
}

def load_color_schemes(file_path):
    """从YAML文件加载配色方案和地图比例尺"""
    # 如果文件不存在，创建默认配置
    if not os.path.exists(file_path):
        color_schemes = {
            "默认": DEFAULT_COLOR_SCHEME,
            "赛博朋克": {
                "background": "#000000",
                "primary": "#FF00FF",
                "secondary": "#00FFFF",
                "contour": "#FF00FF",
                "highlight_contour": "#FFFFFF",
                "grid": "#FF00FF",
                "scan_line": "#00FFFF",
                "cross": "#FF00FF",
                "corner": "#00FFFF",
                "colormap": "inferno"
            },
            "军事风格": {
                "background": "#000000",
                "primary": "#00FF00",
                "secondary": "#FFFF00",
                "contour": "#00FF00",
                "highlight_contour": "#FFFFFF",
                "grid": "#003300",
                "scan_line": "#00FF00",
                "cross": "#00FF00",
                "corner": "#FFFF00",
                "colormap": "viridis"
            }
        }
        
        # 保存默认配置
        save_color_schemes(color_schemes, DEFAULT_MAP_SCALE, file_path)
        return color_schemes, DEFAULT_MAP_SCALE
    
    # 加载现有配置
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        color_schemes = data.get("color_schemes", {"默认": DEFAULT_COLOR_SCHEME})
        map_scale = data.get("map_scale", DEFAULT_MAP_SCALE)
        
        return color_schemes, map_scale
    except Exception as e:
        print(f"加载配色方案时出错: {e}")
        return {"默认": DEFAULT_COLOR_SCHEME}, DEFAULT_MAP_SCALE

def save_color_schemes(color_schemes, map_scale, file_path):
    """保存配色方案和地图比例尺到YAML文件"""
    data = {
        "color_schemes": color_schemes,
        "map_scale": map_scale
    }
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"保存配色方案时出错: {e}")
        return False

def hex_to_rgba(hex_color, alpha=255):
    """将十六进制颜色转换为RGBA元组"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, alpha)
    elif len(hex_color) == 3:
        r, g, b = tuple(int(hex_color[i] + hex_color[i], 16) for i in range(3))
        return (r, g, b, alpha)
    else:
        return (0, 0, 0, alpha)