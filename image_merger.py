
# python .\image_merger.py --input-dir E:\workspace\3D\GaeaProj\G1-1\build\set2x2\output\green --recursive
import os
import re
import argparse
from PIL import Image
import numpy as np

def merge_image_chunks(directory):
    """
    将目录中的图片块拼接回原始图像

    Args:
        directory (str): 包含图片块的目录路径
    """
    # 确保目录存在
    if not os.path.exists(directory):
        raise ValueError(f"指定的目录不存在：{directory}")
    
    # 查找所有图片块并按原始图像名称分组
    chunk_pattern = re.compile(r'(.+)_chunk_y(\d+)_x(\d+)(?:-.*)?\.png')
    chunks_by_image = {}  # 添加字典初始化

    for filename in os.listdir(directory):
        match = chunk_pattern.match(filename)
        if match:
            base_name, y_pos, x_pos = match.groups()
            y_pos, x_pos = int(y_pos), int(x_pos)
            
            if base_name not in chunks_by_image:
                chunks_by_image[base_name] = []
            
            chunks_by_image[base_name].append({
                'filename': filename,
                'path': os.path.join(directory, filename),
                'x': x_pos,
                'y': y_pos
            })
    
    if not chunks_by_image:
        print(f"警告：在目录 {directory} 中没有找到符合命名规则的图片块")
        return
    
    # 处理每组图片块
    for base_name, chunks in chunks_by_image.items():
        try:
            # 确定原始图像的尺寸
            chunk_size = 1024  # 每个分块的大小（1K = 1024x1024）
            max_x = max(chunk['x'] for chunk in chunks)
            max_y = max(chunk['y'] for chunk in chunks)
            
            # 创建一个足够大的空白图像（恢复原始模式）
            width = (max_x + 1) * chunk_size
            height = (max_y + 1) * chunk_size
            merged_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # 恢复RGBA模式
            
            # 将每个分块放置到正确的位置
            for chunk_info in chunks:
                with Image.open(chunk_info['path']) as chunk:
                    x_offset = chunk_info['x'] * chunk_size
                    y_offset = chunk_info['y'] * chunk_size
                    merged_image.paste(chunk, (x_offset, y_offset))
            
            # 裁剪掉空白区域
            bbox = merged_image.getbbox()
            if bbox:
                merged_image = merged_image.crop(bbox)
            
            # 保存合并后的图像（简化保存参数）
            output_path = os.path.join(os.path.dirname(directory), f"{base_name}_merged.png")
            merged_image.save(output_path)
            print(f"成功合并图像：{base_name}，保存至：{output_path}")
            
        except Exception as e:
            print(f"合并图像 {base_name} 时出错：{str(e)}")

def process_directories(parent_dir):
    """
    处理父目录下的所有子目录中的图片块

    Args:
        parent_dir (str): 父目录路径
    """
    # 确保父目录存在
    if not os.path.exists(parent_dir):
        raise ValueError(f"指定的目录不存在：{parent_dir}")
    
    # 获取所有子目录
    subdirs = [d for d in os.listdir(parent_dir) 
              if os.path.isdir(os.path.join(parent_dir, d))]
    
    if not subdirs:
        # 如果没有子目录，尝试在当前目录中查找图片块
        try:
            merge_image_chunks(parent_dir)
        except Exception as e:
            print(f"处理目录 {parent_dir} 时出错：{str(e)}")
        return
    
    # 处理每个子目录
    for subdir in subdirs:
        subdir_path = os.path.join(parent_dir, subdir)
        try:
            merge_image_chunks(subdir_path)
        except Exception as e:
            print(f"处理目录 {subdir_path} 时出错：{str(e)}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将分割的图片块拼接回原始图像')
    parser.add_argument('--input-dir', '-i', 
                        type=str,
                        default=os.getcwd(),
                        help='包含图片块的目录路径（默认为当前工作目录）')
    parser.add_argument('--recursive', '-r',
                        action='store_true',
                        help='是否递归处理子目录')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理指定目录中的图片块
    try:
        if args.recursive:
            process_directories(args.input_dir)
        else:
            merge_image_chunks(args.input_dir)
    except Exception as e:
        print(f"处理过程中出错：{str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())