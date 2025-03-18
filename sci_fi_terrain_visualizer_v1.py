import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import struct

def read_r16_heightmap(file_path):
    """读取r16格式的高度图文件"""
    with open(file_path, 'rb') as f:
        # 读取文件头以确定宽度和高度
        # 注意：这里假设r16文件的前4个字节是宽度，接下来4个字节是高度
        # 如果实际格式不同，需要调整此部分
        width = struct.unpack('I', f.read(4))[0]
        height = struct.unpack('I', f.read(4))[0]
        
        # 读取高度数据
        data = np.zeros((height, width), dtype=np.uint16)
        for y in range(height):
            for x in range(width):
                # 每个高度值占2个字节
                value = struct.unpack('H', f.read(2))[0]
                data[y, x] = value
                
    return data

def read_png_heightmap(file_path):
    """读取16位PNG格式的高度图文件"""
    try:
        # 使用PIL打开PNG图像
        img = Image.open(file_path)
        
        # 检查图像模式，确保是16位图像
        if img.mode != 'I':
            # 如果不是16位图像，尝试转换
            print(f"警告: 图像不是16位格式 (当前模式: {img.mode})，尝试转换...")
            if img.mode == 'L':
                # 8位灰度图，转换为16位并拉伸值范围
                img = img.point(lambda i: i * 256)
                img = img.convert('I')
            elif img.mode == 'RGB' or img.mode == 'RGBA':
                # 彩色图像，转换为灰度再转16位
                img = img.convert('L').point(lambda i: i * 256)
                img = img.convert('I')
        
        # 转换为numpy数组
        data = np.array(img, dtype=np.uint16)
        
        print(f"成功读取PNG高度图: {data.shape[0]}x{data.shape[1]}")
        return data
        
    except Exception as e:
        print(f"读取PNG高度图时出错: {e}")
        raise

def generate_sci_fi_terrain(heightmap, output_path, resolution=1000, contour_levels=20, 
                           color_scheme='plasma', show_grid=True, show_labels=True):
    """生成科幻风格的3D扫描地形俯视图"""
    # 调整数据大小
    if heightmap.shape[0] != resolution or heightmap.shape[1] != resolution:
        from scipy.ndimage import zoom
        zoom_factor = (resolution / heightmap.shape[0], resolution / heightmap.shape[1])
        heightmap = zoom(heightmap, zoom_factor, order=1)
    
    # 创建图像
    fig, ax = plt.figure(figsize=(12, 10), dpi=300), plt.axes()
    
    # 设置科幻风格
    plt.style.use('dark_background')
    
    # 计算高度范围
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    height_range = max_height - min_height
    
    # 绘制基础地形
    terrain = ax.imshow(heightmap, cmap=color_scheme, alpha=0.7)
    
    # 添加等高线
    contours = ax.contour(heightmap, levels=contour_levels, 
                         colors='cyan', alpha=0.6, linewidths=0.5)
    
    # 添加高亮等高线（间隔较大）
    highlight_levels = np.linspace(min_height, max_height, 5)
    highlight_contours = ax.contour(heightmap, levels=highlight_levels, 
                                   colors='white', alpha=0.8, linewidths=1.5)
    
    # 添加高度标签
    if show_labels:
        plt.clabel(highlight_contours, inline=True, fontsize=8, fmt='%1.0f', colors='white')
    
    # 添加网格
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        for x in x_grid:
            ax.axvline(x=x, color='blue', linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color='blue', linestyle='-', alpha=0.2, linewidth=0.5)
    
    # 添加坐标轴标签和标题
    ax.set_title('SCI-FI 3D TERRAIN SCAN', fontsize=16, color='#FF7F00', fontweight='bold')
    ax.set_xlabel('X COORDINATE', color='#FF7F00')
    ax.set_ylabel('Y COORDINATE', color='#FF7F00')
    
    # 添加颜色条
    cbar = plt.colorbar(terrain, ax=ax, pad=0.01)
    cbar.set_label('ELEVATION', color='#FF7F00')
    cbar.ax.yaxis.set_tick_params(color='#FF7F00')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#FF7F00')
    
    # 添加科幻风格的装饰元素
    # 边框
    for spine in ax.spines.values():
        spine.set_edgecolor('#FF7F00')
        spine.set_linewidth(2)
    
    # 设置刻度颜色
    ax.tick_params(axis='x', colors='#FF7F00')
    ax.tick_params(axis='y', colors='#FF7F00')
    
    # 添加扫描线效果
    for i in range(0, resolution, 50):
        ax.axhline(y=i, color='#FF7F00', linestyle='-', alpha=0.1, linewidth=1)
    
    # 添加信息文本
    info_text = (f"MAX ELEVATION: {max_height:.1f}m\n"
                f"MIN ELEVATION: {min_height:.1f}m\n"
                f"ELEVATION RANGE: {height_range:.1f}m\n"
                f"RESOLUTION: {resolution}x{resolution}")
    
    plt.figtext(0.02, 0.02, info_text, color='#FF7F00', fontsize=8,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor='#FF7F00'))
    
    # 添加扫描效果文本
    plt.figtext(0.75, 0.95, "TERRAIN SCAN COMPLETE", color='#FF9F00', fontsize=10,
               bbox=dict(facecolor='black', alpha=0.7, edgecolor='#FF7F00'))
    
    # 保存图像
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"科幻地形图已保存至: {output_path}")
    
    # 添加后期处理效果
    add_postprocessing_effects(output_path)

def add_postprocessing_effects(image_path):
    """添加后期处理效果，如扫描线和辉光"""
    img = Image.open(image_path)
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    # 添加扫描线效果
    scan_line_spacing = 10
    for y in range(0, height, scan_line_spacing):
        draw.line([(0, y), (width, y)], fill=(0, 255, 255, 20), width=1)
    
    # 添加网格交叉点
    grid_size = 50
    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            # 绘制小十字
            draw.line([(x-3, y), (x+3, y)], fill=(0, 255, 255, 100), width=1)
            draw.line([(x, y-3), (x, y+3)], fill=(0, 255, 255, 100), width=1)
    
    # 添加边角装饰
    corner_size = 30
    # 左上角
    draw.line([(0, corner_size), (0, 0), (corner_size, 0)], fill=(0, 255, 255), width=2)
    # 右上角
    draw.line([(width-corner_size, 0), (width, 0), (width, corner_size)], fill=(0, 255, 255), width=2)
    # 左下角
    draw.line([(0, height-corner_size), (0, height), (corner_size, height)], fill=(0, 255, 255), width=2)
    # 右下角
    draw.line([(width-corner_size, height), (width, height), (width, height-corner_size)], fill=(0, 255, 255), width=2)
    
    # 添加科幻风格的文本
    try:
        # 尝试加载字体，如果失败则使用默认字体
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((width-200, 20), "TERRAIN SCAN", fill=(0, 255, 255), font=font)
    draw.text((20, height-40), f"RES: {width}x{height}", fill=(0, 255, 255), font=font)
    
    # 保存增强后的图像
    enhanced_path = os.path.splitext(image_path)[0] + "_enhanced.png"
    img.save(enhanced_path)
    print(f"增强后的图像已保存至: {enhanced_path}")

def main():
    parser = argparse.ArgumentParser(description='生成科幻风格的3D扫描地形俯视图')
    parser.add_argument('input_file', help='输入的高度图文件路径 (支持r16和PNG格式)')
    parser.add_argument('--output', '-o', default='sci_fi_terrain.png', help='输出图像的文件路径')
    parser.add_argument('--resolution', '-r', type=int, default=1000, help='输出图像的分辨率')
    parser.add_argument('--contours', '-c', type=int, default=20, help='等高线的数量')
    parser.add_argument('--color', choices=['plasma', 'viridis', 'inferno', 'magma', 'cividis'], 
                        default='plasma', help='颜色方案')
    parser.add_argument('--no-grid', action='store_false', dest='grid', help='不显示网格')
    parser.add_argument('--no-labels', action='store_false', dest='labels', help='不显示高度标签')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在")
        return
    
    # 根据文件扩展名选择适当的读取函数
    file_ext = os.path.splitext(args.input_file)[1].lower()
    
    # 读取高度图
    try:
        if file_ext == '.r16':
            heightmap = read_r16_heightmap(args.input_file)
        elif file_ext in ['.png', '.tif', '.tiff']:
            heightmap = read_png_heightmap(args.input_file)
        else:
            print(f"不支持的文件格式: {file_ext}")
            print("使用随机数据进行演示...")
            heightmap = np.random.randint(0, 65535, size=(args.resolution, args.resolution), dtype=np.uint16)
    except Exception as e:
        print(f"读取高度图时出错: {e}")
        # 如果读取失败，尝试使用随机数据进行演示
        print("使用随机数据进行演示...")
        heightmap = np.random.randint(0, 65535, size=(args.resolution, args.resolution), dtype=np.uint16)
    
    # 生成地形图
    generate_sci_fi_terrain(
        heightmap, 
        args.output, 
        resolution=args.resolution,
        contour_levels=args.contours,
        color_scheme=args.color,
        show_grid=args.grid,
        show_labels=args.labels
    )

if __name__ == "__main__":
    main()