# python .\sci_fi_terrain_visualizer.py E:\workspace\3D\GaeaProj\G1-1\build\Output.png
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import struct

# 绘制基础地形（修改数据源）
# 在函数开始处添加颜色配置表
COLOR_SCHEME = {
    'base': '#0F1A2F',         # 基础底色
    'contour': 'cyan',        # 普通等高线颜色
    'highlight': 'white',     # 高亮等高线颜色
    'grid': '#1A3A5A',        # 网格线颜色
    'text': '#FF7F00',        # 信息文本颜色
    'glow': (0, 255, 255),    # 光晕效果颜色
    'terrain_cmap': 'plasma',  # 使用传入的色图方案
}

# 在函数开始处添加颜色配置表
COLOR_SCHEME2 = {
    'base': '#FAF0E6',         # 米色底色
    'contour': '#8B4513',      # 棕色等高线
    'highlight': '#A52A2A',    # 深红色高亮等高线
    'grid': '#87CEEB',         # 淡蓝色网格线
    'text': '#2F4F4F',         # 深石板灰文本
    'glow': (255, 215, 0),     # 金色光晕
    'terrain_cmap': 'YlOrBr'   # 地形色图改为黄-橙-棕渐变
}


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
        img = Image.open(file_path)
        
        # 分离RGB通道处理
        if img.mode in ('RGB', 'RGBA'):
            bands = img.split()
            r_band = np.array(bands[0], dtype=np.uint16)
            g_band = np.array(bands[1], dtype=np.uint16)
            
            # 组合R和G通道为16位值 (R高8位 + G低8位)
            data = (r_band << 8) | g_band
            
            # 检测是否为错误处理的8位图像（G通道全0时回退）
            if np.all(g_band == 0):
                data = r_band * 256  # 回退到8位处理
                print("检测到8位PNG格式，已自动调整处理方式")
                
        # 处理16位灰度模式
        elif img.mode == 'I;16':
            data = np.frombuffer(img.tobytes(), dtype='<u2').reshape(img.height, img.width)
            
        # 处理8位灰度模式
        elif img.mode == 'L':
            data = np.array(img, dtype=np.uint16) * 256
            
        else:
            raise ValueError(f"不支持的图像模式: {img.mode}")

        # 验证高度范围
        min_val = np.min(data)
        max_val = np.max(data)
        print(f"高度数据范围验证: {min_val} - {max_val} ({(max_val - min_val)/65535*100:.1f}% 动态范围)")

        print(f"成功读取PNG高度图: {data.shape[0]}x{data.shape[1]}")
        return data
        
    except Exception as e:
        print(f"读取PNG高度图时出错: {e}")
        raise

def generate_sci_fi_terrain(heightmap, output_path, resolution=1000, contour_levels=20, 
                           color_scheme='plasma', show_grid=True, show_labels=True, enhanced=False):
    """生成科幻风格的3D扫描地形俯视图"""
    # 调整数据大小
    if heightmap.shape[0] != resolution or heightmap.shape[1] != resolution:
        from scipy.ndimage import zoom
        zoom_factor = (resolution / heightmap.shape[0], resolution / heightmap.shape[1])
        heightmap = zoom(heightmap, zoom_factor, order=1)
    
    # # 创建图像时调整布局参数
    # # 修改底色和文本颜色
    # fig, ax = plt.figure(figsize=(12, 10), dpi=300, facecolor='white'), plt.axes()  # 修改底色为白色
    # # 设置科幻风格
    # plt.style.use('dark_background')
    
    # 修改绘图底色和风格
    fig, ax = plt.figure(figsize=(12, 10), dpi=300, facecolor=COLOR_SCHEME2['base']), plt.axes()
    plt.style.use('classic')  # 使用经典样式更接近纸质地图效果


    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)  # 移除所有边距

    # 计算高度范围
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    height_range = max_height - min_height
    
    # 绘制基础地形
    terrain = ax.imshow(heightmap, cmap=COLOR_SCHEME2['terrain_cmap'], alpha=0.7)
    
    # 添加等高线
    contours = ax.contour(heightmap, levels=contour_levels, 
                         colors=COLOR_SCHEME2['contour'], alpha=0.6, linewidths=0.5)
    
    # 换算实际高度（添加以下两行）
    heightmap_meters = np.interp(heightmap, (min_height, max_height), (0, 1300))  # 将原始数据映射到0-1300米
    actual_max_height = np.max(heightmap_meters)

    # 添加高亮等高线（间隔较大）
    highlight_levels = np.linspace(min_height, max_height, 10)
    highlight_contours = ax.contour(heightmap, levels=highlight_levels, 
                                  colors=COLOR_SCHEME2['highlight'], alpha=0.8, linewidths=1.5)

    # 添加等高线（修改高度级别计算）
    highlight_levels = np.linspace(0, 1300, 5)  # 固定高度范围
    
    # 添加高度标签（调整字体参数）
    if show_labels:
        plt.clabel(highlight_contours, inline=True, fontsize=6, fmt='%1.0f m', colors='white')  # 添加单位并调整样式

    # 更新信息文本（修改数值引用）
    info_text = (f"MAX: {actual_max_height:.0f}m\n"
                f"MIN: 0m\n"  # 由于线性映射最小值设为0
                f"RNG: 1300m\n"  # 固定范围
                f"RES: {resolution}x{resolution}")
    
    # 添加网格
    if show_grid:
        grid_step = resolution // 20
        x_grid = np.arange(0, resolution, grid_step)
        y_grid = np.arange(0, resolution, grid_step)
        
        for x in x_grid:
            ax.axvline(x=x, color='blue', linestyle='-', alpha=0.2, linewidth=0.5)
        for y in y_grid:
            ax.axhline(y=y, color='blue', linestyle='-', alpha=0.2, linewidth=0.5)
    
    # 删除坐标轴标签和标题设置（约3行）
    # ax.set_title('SCI-FI 3D TERRAIN SCAN', fontsize=16, color='#FF7F00', fontweight='bold')
    # ax.set_xlabel('X COORDINATE', color='#FF7F00')
    # ax.set_ylabel('Y COORDINATE', color='#FF7F00')
    
    # 强化裁剪设置（修改现有代码）
    ax.set_axis_off()
    plt.box(False)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)  # 确保边距归零
    
    # 修改保存参数（现有代码优化）
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
    plt.close()
    print(f"科幻地形图已保存至: {output_path}")
    
    # 添加后期处理效果
    if enhanced:
        add_postprocessing_effects(output_path)

def add_postprocessing_effects(image_path):
    """添加后期处理效果，带有光晕效果的网格系统"""
    # 移除边角装饰代码，只保留以下内容：
    from PIL import ImageFilter
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    # 创建光效层
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow_layer)
    
    # === 高级网格系统 ===
    grid_size = 150
    margin = 80  # 增大边距
    glow_color = (0, 255, 255)
    
    # 生成光晕路径
    for x in range(margin, width - margin, grid_size):
        draw.line([(x, margin), (x, height - margin)], fill=glow_color + (50,), width=5)
    for y in range(margin, height - margin, grid_size):
        draw.line([(margin, y), (width - margin, y)], fill=glow_color + (50,), width=5)
    
    # 应用高斯模糊
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, glow_layer)
    
    # 保存增强后的图像
    enhanced_path = os.path.splitext(image_path)[0] + "_enhanced.png"
    img.save(enhanced_path)
    print(f"增强后的图像已保存至: {enhanced_path}")

# 在main函数中添加enhanced参数
def main():
    parser = argparse.ArgumentParser(description='生成科幻风格的3D扫描地形俯视图')
    parser.add_argument('--enhanced', '-e', action='store_true', help='启用后期光效处理')
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
        enhanced=args.enhanced,
        resolution=args.resolution,
        contour_levels=args.contours,
        color_scheme=args.color,
        show_grid=args.grid,
        show_labels=args.labels
    )

if __name__ == "__main__":
    main()