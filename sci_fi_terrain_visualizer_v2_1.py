"""
科幻地形可视化工具 v2.1
新增功能：
- 添加了交互式UI
- 可切换预设主题 (sci-fi/print)
- 支持自定义颜色配置
- 模块化数据处理流程
- 增强型错误处理
运行命令：
    python sci_fi_terrain_visualizer_v2.py E:\workspace\3D\GaeaProj\G1-1\build\Output.png -t sci-fi -o output_print.png

"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageFilter, ImageDraw
from typing import Tuple, Dict, Optional
from scipy.ndimage import zoom


class TerrainConfig:
    """地形可视化配置类"""
    PRESETS = {
        'sci-fi': {
            'base': '#0F1A2F',
            'contour': 'cyan',
            'highlight': 'white',
            'grid': '#1A3A5A',
            'text': '#FF7F00',
            'glow': (0, 255, 255),
            'cmap': 'plasma',
            'style': 'dark_background'
        },
        'print': {
            'base': '#FAF0E6',
            'contour': '#8B4513',
            'highlight': '#A52A2A',
            'grid': '#87CEEB',
            'text': '#2F4F4F',
            'glow': (255, 215, 0),
            'cmap': 'YlOrBr',
            'style': 'classic'
        }
    }

    def __init__(self, preset: str = 'sci-fi', custom: Optional[Dict] = None):
        self.config = self.PRESETS[preset].copy()
        if custom:
            self.config.update(custom)

    @property
    def colors(self) -> Dict:
        return {k: v for k, v in self.config.items() if k != 'style'}

    @property
    def style(self) -> str:
        return self.config['style']


class HeightmapProcessor:
    """高度图处理引擎"""
    
    @staticmethod
    def load(file_path: str) -> np.ndarray:
        """统一入口加载高度图"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.r16':
            return HeightmapProcessor._load_r16(file_path)
        if ext in ('.png', '.tif', '.tiff'):
            return HeightmapProcessor._load_png(file_path)
        raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _load_r16(file_path: str) -> np.ndarray:
        """加载r16格式高度图"""
        with open(file_path, 'rb') as f:
            width, height = struct.unpack('II', f.read(8))
            data = np.frombuffer(f.read(), dtype=np.uint16)
            return data.reshape((height, width))

    @staticmethod
    def _load_png(file_path: str) -> np.ndarray:
        """加载PNG格式高度图"""
        img = Image.open(file_path)
        try:
            if img.mode in ('RGB', 'RGBA'):
                r, g, *_ = img.split()
                data = (np.array(r, dtype=np.uint16) << 8) | np.array(g, dtype=np.uint16)
                if np.all(g == 0):
                    data = np.array(r) * 256
                    print("Detected 8-bit PNG, auto-adjusted processing")
            elif img.mode == 'I;16':
                data = np.frombuffer(img.tobytes(), dtype='<u2')
            elif img.mode == 'L':
                data = np.array(img, dtype=np.uint16) * 256
            else:
                raise ValueError(f"Unsupported PNG mode: {img.mode}")
            
            data = data.reshape(img.size[::-1])
            print(f"Height range: {np.min(data)}-{np.max(data)}")
            return data
        finally:
            img.close()


class TerrainVisualizer:
    """地形可视化引擎"""
    
    def __init__(self, config: TerrainConfig):
        self.config = config
        plt.style.use(config.style)

    def visualize(self, 
                 heightmap: np.ndarray,
                 output_path: str,
                 resolution: int = 1000,
                 contour_levels: int = 20,
                 show_grid: bool = True,
                 show_labels: bool = True,
                 enhanced: bool = False) -> None:
        """主可视化流程"""
        heightmap = self._preprocess(heightmap, resolution)
        fig, ax = self._setup_canvas()
        self._plot_terrain(ax, heightmap)
        self._add_contours(ax, heightmap, contour_levels, show_labels)
        
        if show_grid:
            self._add_grid(ax, resolution)
        
        self._save_output(fig, output_path)
        
        if enhanced:
            self._apply_effects(output_path)

    def _preprocess(self, data: np.ndarray, target_res: int) -> np.ndarray:
        """数据预处理"""
        if data.shape != (target_res, target_res):
            return zoom(data, (target_res/data.shape[0], target_res/data.shape[1]), order=1)
        return data

    def _setup_canvas(self) -> Tuple[plt.Figure, plt.Axes]:
        """初始化画布"""
        fig = plt.figure(figsize=(12, 10), dpi=300, facecolor=self.config.colors['base'])
        ax = fig.add_axes([0, 0, 1, 1])  # 无边框全画布
        ax.set_axis_off()
        return fig, ax

    def _plot_terrain(self, ax: plt.Axes, data: np.ndarray) -> None:
        """绘制地形基底"""
        ax.imshow(data, cmap=self.config.colors['cmap'], alpha=0.7)

    def _add_contours(self, ax: plt.Axes, data: np.ndarray, levels: int, show_labels: bool) -> None:
        """添加等高线"""
        # 主等高线
        contours = ax.contour(data, levels=levels, 
                            colors=self.config.colors['contour'], 
                            alpha=0.6, linewidths=0.5)
        
        # 高亮等高线
        highlight_levels = np.linspace(np.min(data), np.max(data), 5)
        highlight_contours = ax.contour(data, levels=highlight_levels,
                                       colors=self.config.colors['highlight'],
                                       alpha=0.8, linewidths=1.5)
        
        # 添加标签
        if show_labels:
            font = FontProperties(weight='bold', size=5)
            plt.clabel(highlight_contours, inline=True, fmt='%1.0f m',
                      colors=self.config.colors['text'])

    def _add_grid(self, ax: plt.Axes, resolution: int) -> None:
        """添加参考网格"""
        step = resolution // 20
        for x in np.arange(0, resolution, step):
            ax.axvline(x=x, color=self.config.colors['grid'], alpha=0.2, linewidth=0.5)
        for y in np.arange(0, resolution, step):
            ax.axhline(y=y, color=self.config.colors['grid'], alpha=0.2, linewidth=0.5)

    def _save_output(self, fig: plt.Figure, path: str) -> None:
        """保存输出文件"""
        fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close()
        print(f"输出已保存至: {os.path.abspath(path)}")

    def _apply_effects(self, image_path: str) -> None:
        """应用后期效果"""
        from PIL import ImageFilter
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # 创建光效层
        glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow_layer)
        
        # 高级网格系统
        grid_size = 150
        margin = 80
        glow_color = self.config.colors['glow']
        
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
        print(f"增强后的图像已保存至: {os.path.abspath(enhanced_path)}")


def interactive_ui():
    """提供交互式终端UI界面"""
    import struct  # 确保struct模块被导入
    import os
    from colorama import init, Fore, Style
    
    # 初始化colorama
    init()
    
    print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}         地形可视化工具 v2.0    {Style.RESET_ALL}")
    print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    
    # 默认配置
    config = {
        'input_file': '',
        'output_file': 'terrain_output.png',
        'resolution': 1000,
        'contours': 20,
        'theme': 'sci-fi',
        'grid': True,
        'labels': True,
        'enhanced': False
    }
    
    # 步骤1: 选择输入文件
    print(f"\n{Fore.YELLOW}步骤 1: 选择输入文件{Style.RESET_ALL}")
    
    # 提供文件浏览功能
    def browse_files(start_dir='.', extensions=None):
        """简单的文件浏览器"""
        current_dir = os.path.abspath(start_dir)
        
        while True:
            print(f"\n当前目录: {current_dir}")
            items = os.listdir(current_dir)
            
            # 过滤文件
            dirs = [d for d in items if os.path.isdir(os.path.join(current_dir, d))]
            if extensions:
                files = [f for f in items if os.path.isfile(os.path.join(current_dir, f)) 
                        and any(f.lower().endswith(ext) for ext in extensions)]
            else:
                files = [f for f in items if os.path.isfile(os.path.join(current_dir, f))]
            
            # 显示目录
            print(f"\n{Fore.GREEN}目录:{Style.RESET_ALL}")
            for i, d in enumerate(dirs):
                print(f"{i+1}. {d}/")
            
            # 显示文件
            print(f"\n{Fore.GREEN}文件:{Style.RESET_ALL}")
            for i, f in enumerate(files):
                print(f"{len(dirs)+i+1}. {f}")
            
            # 导航选项
            print(f"\n{Fore.BLUE}导航选项:{Style.RESET_ALL}")
            print("0. 选择此目录")
            print("b. 返回上级目录")
            print("q. 退出浏览")
            print("m. 手动输入路径")
            
            choice = input("\n请选择 (输入数字或选项): ")
            
            if choice == 'q':
                return None
            elif choice == 'b':
                current_dir = os.path.dirname(current_dir)
            elif choice == 'm':
                manual_path = input("请输入完整路径: ")
                if os.path.exists(manual_path):
                    if os.path.isdir(manual_path):
                        current_dir = manual_path
                    else:
                        return manual_path
                else:
                    print(f"{Fore.RED}路径不存在!{Style.RESET_ALL}")
            elif choice == '0':
                path = input("请输入文件名: ")
                return os.path.join(current_dir, path)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(dirs):
                        current_dir = os.path.join(current_dir, dirs[idx])
                    elif len(dirs) <= idx < len(dirs) + len(files):
                        return os.path.join(current_dir, files[idx - len(dirs)])
                    else:
                        print(f"{Fore.RED}无效选择!{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}请输入有效选项!{Style.RESET_ALL}")
    
    print("请选择高度图文件 (支持 .png, .tif, .r16)")
    input_file = browse_files('.', ['.png', '.tif', '.tiff', '.r16'])
    
    if not input_file:
        print(f"{Fore.RED}未选择文件，退出程序{Style.RESET_ALL}")
        return
    
    config['input_file'] = input_file
    
    # 步骤2: 配置输出选项
    print(f"\n{Fore.YELLOW}步骤 2: 配置输出选项{Style.RESET_ALL}")
    
    # 输出文件
    default_output = os.path.splitext(os.path.basename(input_file))[0] + "_terrain.png"
    output_choice = input(f"输出文件名 [{default_output}]: ")
    config['output_file'] = output_choice if output_choice else default_output
    
    # 分辨率
    res_choice = input(f"输出分辨率 [{config['resolution']}]: ")
    if res_choice and res_choice.isdigit():
        config['resolution'] = int(res_choice)
    
    # 等高线数量
    contour_choice = input(f"等高线数量 [{config['contours']}]: ")
    if contour_choice and contour_choice.isdigit():
        config['contours'] = int(contour_choice)
    
    # 步骤3: 选择主题和效果
    print(f"\n{Fore.YELLOW}步骤 3: 选择主题和效果{Style.RESET_ALL}")
    
    # 主题选择
    print("可用主题:")
    print("1. 科幻风格 (sci-fi)")
    print("2. 印刷风格 (print)")
    theme_choice = input(f"选择主题 [1]: ")
    if theme_choice == '2':
        config['theme'] = 'print'
    
    # 网格显示
    grid_choice = input(f"显示网格? (y/n) [y]: ")
    if grid_choice.lower() == 'n':
        config['grid'] = False
    
    # 标签显示
    labels_choice = input(f"显示高度标签? (y/n) [y]: ")
    if labels_choice.lower() == 'n':
        config['labels'] = False
    
    # 增强效果
    enhanced_choice = input(f"应用后期增强效果? (y/n) [n]: ")
    if enhanced_choice.lower() == 'y':
        config['enhanced'] = True
    
    # 步骤4: 确认并执行
    print(f"\n{Fore.YELLOW}步骤 4: 确认配置{Style.RESET_ALL}")
    print("\n当前配置:")
    print(f"- 输入文件: {config['input_file']}")
    print(f"- 输出文件: {config['output_file']}")
    print(f"- 分辨率: {config['resolution']}")
    print(f"- 等高线数量: {config['contours']}")
    print(f"- 主题: {config['theme']}")
    print(f"- 显示网格: {'是' if config['grid'] else '否'}")
    print(f"- 显示标签: {'是' if config['labels'] else '否'}")
    print(f"- 增强效果: {'是' if config['enhanced'] else '否'}")
    
    confirm = input(f"\n确认执行? (y/n) [y]: ")
    if confirm.lower() in ('', 'y', 'yes'):
        try:
            # 加载数据
            print(f"\n{Fore.CYAN}正在加载高度图...{Style.RESET_ALL}")
            heightmap = HeightmapProcessor.load(config['input_file'])
            
            # 初始化可视化引擎
            print(f"{Fore.CYAN}正在初始化可视化引擎...{Style.RESET_ALL}")
            visualizer = TerrainVisualizer(TerrainConfig(preset=config['theme']))
            
            # 执行可视化
            print(f"{Fore.CYAN}正在生成地形图...{Style.RESET_ALL}")
            visualizer.visualize(
                heightmap=heightmap,
                output_path=config['output_file'],
                resolution=config['resolution'],
                contour_levels=config['contours'],
                show_grid=config['grid'],
                show_labels=config['labels'],
                enhanced=config['enhanced']
            )
            
            print(f"\n{Fore.GREEN}处理完成!{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"\n{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}建议操作:{Style.RESET_ALL}")
            print("- 检查输入文件格式是否支持")
            print("- 确认分辨率参数是否合理")
            print("- 尝试使用不同主题")
    else:
        print(f"{Fore.YELLOW}已取消操作{Style.RESET_ALL}")


def main():
    """命令行接口"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 使用传统命令行参数模式
        parser = argparse.ArgumentParser(prog='TerrainVisualizer v2', 
                                        description='科幻地形可视化工具')
        
        # 核心参数
        parser.add_argument('input', help='输入高度图文件路径')
        parser.add_argument('-o', '--output', default='terrain_output.png', 
                          help='输出文件路径')
        
        # 可视化参数
        parser.add_argument('-r', '--resolution', type=int, default=1000,
                          help='输出分辨率 (默认: 1000)')
        parser.add_argument('-c', '--contours', type=int, default=20,
                          help='等高线数量 (默认: 20)')
        parser.add_argument('-t', '--theme', choices=['sci-fi', 'print'], default='sci-fi',
                          help='配色主题 (默认: sci-fi)')
        
        # 功能开关
        parser.add_argument('--no-grid', dest='grid', action='store_false',
                          help='禁用参考网格')
        parser.add_argument('--no-labels', dest='labels', action='store_false', 
                          help='禁用高度标签')
        parser.add_argument('-e', '--enhanced', action='store_true',
                          help='启用后期特效')
        parser.add_argument('-i', '--interactive', action='store_true',
                          help='启用交互式界面')
        
        args = parser.parse_args()
        
        if args.interactive:
            interactive_ui()
            return
        
        try:
            # 加载数据
            heightmap = HeightmapProcessor.load(args.input)
            
            # 初始化可视化引擎
            visualizer = TerrainVisualizer(TerrainConfig(preset=args.theme))
            
            # 执行可视化
            visualizer.visualize(
                heightmap=heightmap,
                output_path=args.output,
                resolution=args.resolution,
                contour_levels=args.contours,
                show_grid=args.grid,
                show_labels=args.labels,
                enhanced=args.enhanced
            )
            
        except Exception as e:
            print(f"\n错误: {str(e)}")
            print("建议操作：")
            print("- 检查输入文件格式是否支持")
            print("- 确认分辨率参数是否合理")
            print("- 尝试使用 --theme print 切换主题")
            exit(1)
    else:
        # 无参数时启动交互式界面
        interactive_ui()


if __name__ == '__main__':
    import sys
    import struct  # 确保struct模块被导入
    main()