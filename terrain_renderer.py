"""
地形渲染模块 - 将高度图渲染成科幻风格的地形图
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import os
import argparse
from pathlib import Path
from PIL import Image  # 添加PIL库用于处理图像文件

def render_terrain_preview(heightmap, color_scheme, map_scale, resolution=500, 
                          contour_levels=20, show_grid=True, show_labels=True, show_frame=True):
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
    
    # 添加网格和光晕效果
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        # 绘制网格线
        for x in x_grid:
            ax.axvline(x=x, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
            
        # 在网格交叉点添加光晕效果
        for x in x_grid:
            for y in y_grid:
                # 生成随机强度的光晕
                glow_intensity = np.random.uniform(0.3, 0.8)
                glow_size = np.random.uniform(30, 50)
                
                # 创建光晕效果
                glow = plt.Circle((x, y), glow_size/resolution, 
                                 color=color_scheme["highlight_contour"],
                                 alpha=glow_intensity * 0.3,
                                 transform=ax.transData)
                ax.add_artist(glow)
                
                # 添加中心亮点
                center_point = plt.Circle((x, y), glow_size/(resolution*4),
                                        color=color_scheme["highlight_contour"],
                                        alpha=glow_intensity,
                                        transform=ax.transData)
                ax.add_artist(center_point)
    
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
    if show_frame:
        for spine in ax.spines.values():
            spine.set_edgecolor(color_scheme["primary"])
            spine.set_linewidth(2)
    else:
        for spine in ax.spines.values():
            spine.set_visible(False)
    
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
                        resolution=1000, contour_levels=20, show_grid=True, show_labels=True, show_frame=True):
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
    
    # 添加网格和光晕效果
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        # 绘制网格线
        for x in x_grid:
            ax.axvline(x=x, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color=color_scheme["grid"], linestyle='-', alpha=0.2, linewidth=0.5)
            
        # 在网格交叉点添加光晕效果
        for x in x_grid:
            for y in y_grid:
                # 生成随机强度的光晕
                glow_intensity = np.random.uniform(0.3, 0.8)
                glow_size = np.random.uniform(30, 50)
                
                # 创建光晕效果
                glow = plt.Circle((x, y), glow_size/resolution, 
                                 color=color_scheme["highlight_contour"],
                                 alpha=glow_intensity * 0.3,
                                 transform=ax.transData)
                ax.add_artist(glow)
                
                # 添加中心亮点
                center_point = plt.Circle((x, y), glow_size/(resolution*4),
                                        color=color_scheme["highlight_contour"],
                                        alpha=glow_intensity,
                                        transform=ax.transData)
                ax.add_artist(center_point)
    
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
    if show_frame:
        for spine in ax.spines.values():
            spine.set_edgecolor(color_scheme["primary"])
            spine.set_linewidth(2)
    else:
        for spine in ax.spines.values():
            spine.set_visible(False)
    
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


def main():
    """
    主函数 - 当脚本直接运行时执行
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='渲染科幻风格地形图')
    parser.add_argument('--input', '-i', type=str, required=True, help='输入高度图文件路径 (numpy .npy 或 16位 PNG 格式)')
    parser.add_argument('--output', '-o', type=str, help='输出图像文件路径')
    parser.add_argument('--resolution', '-r', type=int, default=1000, help='输出图像分辨率')
    parser.add_argument('--contour-levels', '-c', type=int, default=20, help='等高线数量')
    parser.add_argument('--no-grid', action='store_true', help='不显示网格')
    parser.add_argument('--no-labels', action='store_true', help='不显示高度标签')
    parser.add_argument('--no-frame', action='store_true', help='不显示边框')
    parser.add_argument('--max-elevation', '-e', type=float, default=5.0, help='最大海拔高度(km)')
    parser.add_argument('--width', '-w', type=float, default=100.0, help='地图宽度(km)')
    # 修改这一行，将 -h 改为 -H 避免与 --help 冲突
    parser.add_argument('--height', '-H', type=float, default=100.0, help='地图高度(km)')
    parser.add_argument('--preview', '-p', action='store_true', help='显示预览窗口')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 '{args.input}' 不存在")
        return 1
    
    # 加载高度图数据
    input_path = Path(args.input)
    file_extension = input_path.suffix.lower()
    
    try:
        if file_extension == '.npy':
            # 加载NumPy格式的高度图
            heightmap = np.load(args.input)
        elif file_extension in ['.png', '.tif', '.tiff']:
            # 加载16位PNG或TIFF格式的高度图
            img = Image.open(args.input)
            
            # 检查图像模式
            if img.mode == 'I':  # 32位整数
                heightmap = np.array(img)
            elif img.mode == 'F':  # 32位浮点数
                heightmap = np.array(img)
            elif img.mode == 'L':  # 8位灰度
                heightmap = np.array(img)
                print("警告: 检测到8位灰度图像，高度精度可能受限")
            elif img.mode == 'RGB' or img.mode == 'RGBA':
                # 对于RGB图像，转换为灰度
                img_gray = img.convert('L')
                heightmap = np.array(img_gray)
                print("警告: 检测到彩色图像，已转换为灰度，高度精度可能受限")
            else:
                # 尝试转换为灰度
                img_gray = img.convert('L')
                heightmap = np.array(img_gray)
                print(f"警告: 未知图像模式 '{img.mode}'，已尝试转换为灰度")
            
            # 如果是16位PNG，确保正确处理数据范围
            if img.mode == 'I' or (hasattr(img, 'bits') and img.bits == 16):
                # 将数据归一化到0-1范围
                heightmap = heightmap.astype(np.float32) / np.iinfo(np.uint16).max
            else:
                # 8位图像归一化
                heightmap = heightmap.astype(np.float32) / 255.0
        else:
            print(f"错误: 不支持的文件格式 '{file_extension}'，请使用.npy或.png文件")
            return 1
    except Exception as e:
        print(f"错误: 无法加载高度图文件: {e}")
        return 1
    
    # 设置默认输出路径（如果未指定）
    if args.output is None:
        args.output = str(input_path.parent / f"{input_path.stem}_terrain.png")
    
    # 设置配色方案
    color_scheme = {
        "background": "#000010",
        "colormap": "viridis",
        "contour": "#00FFFF",
        "highlight_contour": "#00FFAA",
        "grid": "#4040FF",
        "primary": "#00FFFF",
        "secondary": "#FF00FF",
        "scan_line": "#0088FF"
    }
    
    # 设置地图比例尺
    map_scale = {
        "width_km": args.width,
        "height_km": args.height,
        "max_elevation_km": args.max_elevation
    }
    
    # 渲染预览（如果需要）
    if args.preview:
        fig, ax = render_terrain_preview(
            heightmap, 
            color_scheme, 
            map_scale, 
            resolution=min(args.resolution, 500),  # 预览使用较低分辨率
            contour_levels=args.contour_levels,
            show_grid=not args.no_grid,
            show_labels=not args.no_labels,
            show_frame=not args.no_frame
        )
        plt.show()
    
    # 渲染并保存高质量图像
    output_path = render_terrain_image(
        heightmap, 
        args.output, 
        color_scheme, 
        map_scale, 
        resolution=args.resolution,
        contour_levels=args.contour_levels,
        show_grid=not args.no_grid,
        show_labels=not args.no_labels,
        show_frame=not args.no_frame
    )
    
    print(f"地形图已保存至: {output_path}")
    return 0

# 当脚本直接运行时执行main函数
if __name__ == "__main__":
    exit(main())
