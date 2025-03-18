"""
高度图读取模块 - 处理不同格式的高度图文件
"""

import os
import numpy as np
from PIL import Image

def read_r16_heightmap(file_path):
    """
    读取R16格式的高度图文件
    R16是16位原始高度图格式，每个像素用2个字节表示高度
    """
    try:
        # 获取文件大小以确定图像尺寸
        file_size = os.path.getsize(file_path)
        width = height = int(np.sqrt(file_size / 2))
        
        # 读取二进制数据
        with open(file_path, 'rb') as f:
            data = np.fromfile(f, dtype=np.uint16)
        
        # 重塑为二维数组
        heightmap = data.reshape((height, width))
        return heightmap
    except Exception as e:
        print(f"读取R16高度图时出错: {e}")
        raise

def read_png_heightmap(file_path):
    """
    读取PNG/TIFF格式的高度图文件
    支持8位和16位图像
    """
    try:
        # 使用PIL读取图像
        img = Image.open(file_path)
        
        # 转换为灰度图
        if img.mode != 'L' and img.mode != 'I':
            img = img.convert('L')
        
        # 转换为numpy数组
        heightmap = np.array(img)
        
        # 如果是8位图像，转换为16位范围
        if heightmap.dtype == np.uint8:
            heightmap = heightmap.astype(np.uint16) * 257  # 缩放到0-65535范围
        
        return heightmap
    except Exception as e:
        print(f"读取PNG/TIFF高度图时出错: {e}")
        raise

def generate_random_heightmap(width, height):
    """
    生成随机高度图用于测试
    """
    # 使用柏林噪声或分形噪声生成更自然的地形
    from scipy.ndimage import gaussian_filter
    
    # 生成随机噪声
    noise = np.random.rand(height, width)
    
    # 应用高斯滤波使其更平滑
    smoothed = gaussian_filter(noise, sigma=5.0)
    
    # 缩放到16位范围
    heightmap = (smoothed * 65535).astype(np.uint16)
    
    return heightmap