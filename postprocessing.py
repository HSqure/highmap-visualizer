"""
后期处理模块 - 为渲染的地形图像添加科幻风格的后期效果
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
from config import hex_to_rgba

def add_postprocessing_effects(image_path, output_path=None):
    """
    为地形图像添加科幻风格的后期处理效果
    
    参数:
        image_path: 输入图像路径
        output_path: 输出图像路径，如果为None则覆盖原图像
    
    返回:
        output_path: 处理后的图像路径
    """
    if output_path is None:
        # 如果没有指定输出路径，则在原文件名基础上添加后缀
        filename, ext = os.path.splitext(image_path)
        output_path = f"{filename}_enhanced{ext}"
    
    # 打开图像
    img = Image.open(image_path)
    
    # 1. 添加扫描线效果
    scan_lines = create_scan_lines(img.width, img.height)
    img = Image.alpha_composite(img.convert("RGBA"), scan_lines)
    
    # 2. 添加噪点效果
    noise = create_noise(img.width, img.height, alpha=10)
    img = Image.alpha_composite(img, noise)
    
    # 3. 添加边框效果
    border = create_border(img.width, img.height)
    img = Image.alpha_composite(img, border)
    
    # 4. 添加角落装饰
    corners = create_corners(img.width, img.height)
    img = Image.alpha_composite(img, corners)
    
    # 5. 添加十字准线
    crosshair = create_crosshair(img.width, img.height)
    img = Image.alpha_composite(img, crosshair)
    
    # 6. 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # 7. 锐化图像
    img = img.filter(ImageFilter.SHARPEN)
    
    # 保存图像
    img.save(output_path)
    
    return output_path

def add_postprocessing_effects_with_color(image_path, color_scheme, output_path=None):
    """
    使用指定配色方案为地形图像添加科幻风格的后期处理效果
    
    参数:
        image_path: 输入图像路径
        color_scheme: 配色方案
        output_path: 输出图像路径，如果为None则覆盖原图像
    
    返回:
        output_path: 处理后的图像路径
    """
    if output_path is None:
        # 如果没有指定输出路径，则在原文件名基础上添加后缀
        filename, ext = os.path.splitext(image_path)
        output_path = f"{filename}_enhanced{ext}"
    
    # 打开图像
    img = Image.open(image_path)
    
    # 1. 添加扫描线效果
    scan_lines = create_scan_lines(img.width, img.height, color=color_scheme["scan_line"])
    img = Image.alpha_composite(img.convert("RGBA"), scan_lines)
    
    # 2. 添加噪点效果
    noise = create_noise(img.width, img.height, alpha=10)
    img = Image.alpha_composite(img, noise)
    
    # 3. 添加边框效果
    border = create_border(img.width, img.height, color=color_scheme["primary"])
    img = Image.alpha_composite(img, border)
    
    # 4. 添加角落装饰
    corners = create_corners(img.width, img.height, color=color_scheme["corner"])
    img = Image.alpha_composite(img, corners)
    
    # 5. 添加十字准线
    crosshair = create_crosshair(img.width, img.height, color=color_scheme["cross"])
    img = Image.alpha_composite(img, crosshair)
    
    # 6. 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # 7. 锐化图像
    img = img.filter(ImageFilter.SHARPEN)
    
    # 保存图像
    img.save(output_path)
    
    return output_path

def create_scan_lines(width, height, color="#00FFFF", spacing=4, alpha=30):
    """创建扫描线效果"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    r, g, b, _ = hex_to_rgba(color)
    
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=(r, g, b, alpha))
    
    return img

def create_noise(width, height, alpha=20):
    """创建噪点效果"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = img.load()
    
    for x in range(width):
        for y in range(height):
            if np.random.random() < 0.05:  # 5%的像素添加噪点
                intensity = np.random.randint(0, 255)
                pixels[x, y] = (intensity, intensity, intensity, alpha)
    
    return img

def create_border(width, height, color="#00FFFF", thickness=4):
    """创建边框效果"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    r, g, b, _ = hex_to_rgba(color)
    
    # 外边框
    for i in range(thickness):
        draw.rectangle(
            [(i, i), (width - i - 1, height - i - 1)],
            outline=(r, g, b, 255 - i * 40)
        )
    
    return img

def create_corners(width, height, color="#00FFFF", size=50):
    """创建角落装饰"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    r, g, b, _ = hex_to_rgba(color)
    
    # 左上角
    draw.line([(0, size), (0, 0), (size, 0)], fill=(r, g, b, 200), width=2)
    draw.line([(10, 10), (40, 10)], fill=(r, g, b, 200), width=2)
    draw.line([(10, 10), (10, 40)], fill=(r, g, b, 200), width=2)
    
    # 右上角
    draw.line([(width - size, 0), (width, 0), (width, size)], fill=(r, g, b, 200), width=2)
    draw.line([(width - 10, 10), (width - 40, 10)], fill=(r, g, b, 200), width=2)
    draw.line([(width - 10, 10), (width - 10, 40)], fill=(r, g, b, 200), width=2)
    
    # 左下角
    draw.line([(0, height - size), (0, height), (size, height)], fill=(r, g, b, 200), width=2)
    draw.line([(10, height - 10), (40, height - 10)], fill=(r, g, b, 200), width=2)
    draw.line([(10, height - 10), (10, height - 40)], fill=(r, g, b, 200), width=2)
    
    # 右下角
    draw.line([(width - size, height), (width, height), (width, height - size)], fill=(r, g, b, 200), width=2)
    draw.line([(width - 10, height - 10), (width - 40, height - 10)], fill=(r, g, b, 200), width=2)
    draw.line([(width - 10, height - 10), (width - 10, height - 40)], fill=(r, g, b, 200), width=2)
    
    return img

def create_crosshair(width, height, color="#00FFFF", size=20):
    """创建十字准线效果"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    r, g, b, _ = hex_to_rgba(color)
    
    # 中心点
    center_x, center_y = width // 2, height // 2
    
    # 水平线
    draw.line([(center_x - size, center_y), (center_x + size, center_y)], fill=(r, g, b, 150), width=1)
    
    # 垂直线
    draw.line([(center_x, center_y - size), (center_x, center_y + size)], fill=(r, g, b, 150), width=1)
    
    # 中心圆
    draw.ellipse([(center_x - 5, center_y - 5), (center_x + 5, center_y + 5)], outline=(r, g, b, 150))
    
    return img