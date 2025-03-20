"""
科幻地形可视化工具 v2.0
新增功能：
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
        # 实现后期处理效果...
        pass


def main():
    """命令行接口"""
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
    
    args = parser.parse_args()

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


if __name__ == '__main__':
    main()