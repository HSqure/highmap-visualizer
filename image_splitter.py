import os
import argparse
from PIL import Image

def split_image(image_path):
    """将图片分割成最多64个1K图片，边缘小于200像素的分块将被丢弃

    Args:
        image_path (str): 输入图片的路径
    """
    # 获取原始图片的文件名（不含扩展名）和扩展名
    base_name = os.path.basename(image_path)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # 读取图片
    with Image.open(image_path) as img:
        # 计算每个分块的大小（1K = 1024x1024）
        chunk_size = 1024
        chunks_per_side = 8  # 8x8网格
        
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(image_path), name_without_ext)
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取图片尺寸
        width, height = img.size
        
        # 分割图片
        for y in range(chunks_per_side):
            for x in range(chunks_per_side):
                # 计算当前分块的坐标
                left = x * chunk_size
                top = y * chunk_size
                right = min(left + chunk_size, width)
                bottom = min(top + chunk_size, height)
                
                # 如果分块超出图片范围，跳过
                if left >= width or top >= height:
                    continue
                
                # 计算分块的实际大小
                block_width = right - left
                block_height = bottom - top
                
                # 如果分块太小（小于200像素），跳过
                if block_width < 200 or block_height < 200:
                    continue
                
                # 裁剪图片
                chunk = img.crop((left, top, right, bottom))
                
                # 生成输出文件名
                chunk_name = f"{name_without_ext}_chunk_y{y}_x{x}.png"
                chunk_path = os.path.join(output_dir, chunk_name)
                
                # 保存分块
                chunk.save(chunk_path)

def process_directory(directory):
    """处理目录中的所有8K图片

    Args:
        directory (str): 包含8K图片的目录路径
    """
    # 确保目录存在
    if not os.path.exists(directory):
        raise ValueError(f"指定的目录不存在：{directory}")
    
    # 遍历目录中的所有PNG文件
    png_files = [f for f in os.listdir(directory) if f.endswith('.png')]
    if not png_files:
        print(f"警告：在目录 {directory} 中没有找到PNG文件")
        return
    
    for filename in png_files:
        image_path = os.path.join(directory, filename)
        try:
            split_image(image_path)
            print(f"成功处理图片：{filename}")
        except Exception as e:
            print(f"处理图片 {filename} 时出错：{str(e)}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='将8K图片分割成64个1K图片')
    parser.add_argument('--input-dir', '-i', 
                        type=str,
                        default=os.getcwd(),
                        help='输入图片所在的目录路径（默认为当前工作目录）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理指定目录中的图片
    try:
        process_directory(args.input_dir)
    except Exception as e:
        print(f"处理过程中出错：{str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())