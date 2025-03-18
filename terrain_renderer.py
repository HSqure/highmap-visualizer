"""
地形渲染模块 - 将高度图渲染成科幻风格的地形图
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import os

def render_terrain_preview(heightmap, color_scheme, map_scale, resolution=500, 
                          contour_levels=20, show_grid=True, show_labels=True):
    """
    渲染地形预览图像
    
    参数:
        heightmap: 高度图数据
        color_scheme: 配色方案
        map_scale: 地图比例尺
        resolution: 输出分辨率
        contour_levels: 等高线数量
        show_grid: 是否显示网格
        show_labels: 是否显示高度标签
    
    返回:
        fig, ax: matplotlib图形和坐标轴对象
    """
    # 创建图形
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    
    # 设置科幻风格
    plt.style.use('dark_background')
    ax.set_facecolor(color_scheme["background"])
    
    # 调整数据大小
    if heightmap.shape[0] != resolution or heightmap.shape[1] != resolution:
        zoom_factor = (resolution / heightmap.shape[0], resolution / heightmap.shape[1])
        heightmap = zoom(heightmap, zoom_factor, order=1)
    
    # 计算高度范围并应用比例尺
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    height_range = max_height - min_height
    
    # 修复除零错误
    if height_range == 0:
        # 如果地形完全平坦，设置一个默认的高度范围
        height_scale = 1.0
        scaled_min_height = min_height * map_scale["max_elevation_km"] * 1000
        scaled_max_height = scaled_min_height
        scaled_height_range = 0
    else:
        # 应用比例尺 - 将高度值映射到实际高度（米）
        height_scale = map_scale["max_elevation_km"] * 1000 / height_range
        scaled_min_height = min_height * height_scale
        scaled_max_height = max_height * height_scale
        scaled_height_range = scaled_max_height - scaled_min_height
    
    # 绘制基础地形
    terrain = ax.imshow(heightmap, cmap=color_scheme["colormap"], alpha=0.7)
    
    # 添加等高线 - 修复等高线级别问题
    if height_range > 0:
        # 生成等高线级别
        contour_levels_array = np.linspace(min_height, max_height, contour_levels)
        
        # 确保等高线级别是唯一的
        contour_levels_array = np.unique(contour_levels_array)
        
        # 如果有足够的唯一级别，绘制等高线
        if len(contour_levels_array) > 1:
            contours = ax.contour(heightmap, levels=contour_levels_array, 
                                 colors=color_scheme["contour"], alpha=0.6, linewidths=0.5)
            
            # 添加高亮等高线（间隔较大）
            highlight_levels = np.unique(np.linspace(min_height, max_height, 5))
            if len(highlight_levels) > 1:
                highlight_contours = ax.contour(heightmap, levels=highlight_levels, 
                                              colors=color_scheme["highlight_contour"], alpha=0.8, linewidths=1.5)
                
                # 添加高度标签
                if show_labels:
                    plt.clabel(highlight_contours, inline=True, fontsize=8, 
                              fmt=lambda x: f"{x*height_scale:.0f}", 
                              colors=color_scheme["highlight_contour"])
        else:
            contours = None
            highlight_contours = None
    else:
        # 如果地形完全平坦，不绘制等高线
        contours = None
        highlight_contours = None
    
    # 添加网格
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        for x in x_grid:
            ax.axvline(x=x, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
    
    # 添加坐标轴标签和标题
    ax.set_title('SCI-FI 3D TERRAIN SCAN', fontsize=16, color=color_scheme["primary"], fontweight='bold')
    ax.set_xlabel(f'X COORDINATE ({map_scale["width_km"]:.2f} km)', color=color_scheme["primary"])
    ax.set_ylabel(f'Y COORDINATE ({map_scale["height_km"]:.2f} km)', color=color_scheme["primary"])
    
    # 添加颜色条
    cbar = plt.colorbar(terrain, ax=ax, pad=0.01)
    cbar.set_label('ELEVATION (m)', color=color_scheme["primary"])
    cbar.ax.yaxis.set_tick_params(color=color_scheme["primary"])
    for label in cbar.ax.get_yticklabels():
        label.set_color(color_scheme["primary"])
    
    # 添加科幻风格的装饰元素
    # 边框
    for spine in ax.spines.values():
        spine.set_edgecolor(color_scheme["primary"])
        spine.set_linewidth(2)
    
    # 设置刻度颜色
    ax.tick_params(axis='x', colors=color_scheme["primary"])
    ax.tick_params(axis='y', colors=color_scheme["primary"])
    
    # 添加扫描线效果
    for i in range(0, resolution, 50):
        ax.axhline(y=i, color=color_scheme["scan_line"], linestyle='-', alpha=0.1, linewidth=1)
    
    # 添加信息文本
    info_text = (f"MAX ELEVATION: {scaled_max_height:.1f}m\n"
                f"MIN ELEVATION: {scaled_min_height:.1f}m\n"
                f"ELEVATION RANGE: {scaled_height_range:.1f}m\n"
                f"MAP SIZE: {map_scale['width_km']:.2f}x{map_scale['height_km']:.2f} km\n"
                f"RESOLUTION: {resolution}x{resolution}")
    
    plt.figtext(0.02, 0.02, info_text, color=color_scheme["primary"], fontsize=8,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor=color_scheme["primary"]))
    
    # 添加扫描效果文本
    plt.figtext(0.75, 0.95, "TERRAIN SCAN COMPLETE", color=color_scheme["secondary"], fontsize=10,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor=color_scheme["primary"]))
    
    return fig, ax

def render_terrain_image(heightmap, output_path, color_scheme, map_scale, 
                        resolution=1000, contour_levels=20, show_grid=True, show_labels=True):
    """
    渲染高质量地形图像并保存
    
    参数:
        heightmap: 高度图数据
        output_path: 输出文件路径
        color_scheme: 配色方案
        map_scale: 地图比例尺
        resolution: 输出分辨率
        contour_levels: 等高线数量
        show_grid: 是否显示网格
        show_labels: 是否显示高度标签
    
    返回:
        output_path: 保存的文件路径
    """
    # 创建高质量图像
    fig = plt.figure(figsize=(12, 10), dpi=300)
    ax = fig.add_subplot(111)
    
    # 设置科幻风格
    plt.style.use('dark_background')
    ax.set_facecolor(color_scheme["background"])
    
    # 调整数据大小
    if heightmap.shape[0] != resolution or heightmap.shape[1] != resolution:
        zoom_factor = (resolution / heightmap.shape[0], resolution / heightmap.shape[1])
        heightmap = zoom(heightmap, zoom_factor, order=1)
    
    # 计算高度范围并应用比例尺
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    height_range = max_height - min_height
    
    # 修复除零错误
    if height_range == 0:
        # 如果地形完全平坦，设置一个默认的高度范围
        height_scale = 1.0
        scaled_min_height = min_height * map_scale["max_elevation_km"] * 1000
        scaled_max_height = scaled_min_height
        scaled_height_range = 0
    else:
        # 应用比例尺 - 将高度值映射到实际高度（米）
        height_scale = map_scale["max_elevation_km"] * 1000 / height_range
        scaled_min_height = min_height * height_scale
        scaled_max_height = max_height * height_scale
        scaled_height_range = scaled_max_height - scaled_min_height
    
    # 绘制基础地形
    terrain = ax.imshow(heightmap, cmap=color_scheme["colormap"], alpha=0.7)
    
    # 添加等高线 - 修复等高线级别问题
    if height_range > 0:
        # 生成等高线级别
        contour_levels_array = np.linspace(min_height, max_height, contour_levels)
        
        # 确保等高线级别是唯一的
        contour_levels_array = np.unique(contour_levels_array)
        
        # 如果有足够的唯一级别，绘制等高线
        if len(contour_levels_array) > 1:
            contours = ax.contour(heightmap, levels=contour_levels_array, 
                                 colors=color_scheme["contour"], alpha=0.6, linewidths=0.5)
            
            # 添加高亮等高线（间隔较大）
            highlight_levels = np.unique(np.linspace(min_height, max_height, 5))
            if len(highlight_levels) > 1:
                highlight_contours = ax.contour(heightmap, levels=highlight_levels, 
                                              colors=color_scheme["highlight_contour"], alpha=0.8, linewidths=1.5)
                
                # 添加高度标签
                if show_labels:
                    plt.clabel(highlight_contours, inline=True, fontsize=8, 
                              fmt=lambda x: f"{x*height_scale:.0f}", 
                              colors=color_scheme["highlight_contour"])
            else:
                highlight_contours = None
        else:
            contours = None
            highlight_contours = None
    else:
        # 如果地形完全平坦，不绘制等高线
        contours = None
        highlight_contours = None
    
    # 添加网格
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        for x in x_grid:
            ax.axvline(x=x, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
    
    # 添加坐标轴标签和标题
    ax.set_title('SCI-FI 3D TERRAIN SCAN', fontsize=16, color=color_scheme["primary"], fontweight='bold')
    ax.set_xlabel(f'X COORDINATE ({map_scale["width_km"]:.2f} km)', color=color_scheme["primary"])
    ax.set_ylabel(f'Y COORDINATE ({map_scale["height_km"]:.2f} km)', color=color_scheme["primary"])
    
    # 添加颜色条
    cbar = plt.colorbar(terrain, ax=ax, pad=0.01)
    cbar.set_label('ELEVATION (m)', color=color_scheme["primary"])
    cbar.ax.yaxis.set_tick_params(color=color_scheme["primary"])
    for label in cbar.ax.get_yticklabels():
        label.set_color(color_scheme["primary"])
    
    # 添加科幻风格的装饰元素
    # 边框
    for spine in ax.spines.values():
        spine.set_edgecolor(color_scheme["primary"])
        spine.set_linewidth(2)
    
    # 设置刻度颜色
    ax.tick_params(axis='x', colors=color_scheme["primary"])
    ax.tick_params(axis='y', colors=color_scheme["primary"])
    
    # 添加扫描线效果
    for i in range(0, resolution, 50):
        ax.axhline(y=i, color=color_scheme["scan_line"], linestyle='-', alpha=0.1, linewidth=1)
    
    # 添加信息文本
    info_text = (f"MAX ELEVATION: {scaled_max_height:.1f}m\n"
                f"MIN ELEVATION: {scaled_min_height:.1f}m\n"
                f"ELEVATION RANGE: {scaled_height_range:.1f}m\n"
                f"MAP SIZE: {map_scale['width_km']:.2f}x{map_scale['height_km']:.2f} km\n"
                f"RESOLUTION: {resolution}x{resolution}")
    
    plt.figtext(0.02, 0.02, info_text, color=color_scheme["primary"], fontsize=8,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor=color_scheme["primary"]))
    
    # 添加扫描效果文本
    plt.figtext(0.75, 0.95, "TERRAIN SCAN COMPLETE", color=color_scheme["secondary"], fontsize=10,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor=color_scheme["primary"]))
    
    # 保存图像
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return output_path