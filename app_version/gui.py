"""
图形用户界面模块 - 实现扁平化设计风格的交互界面
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import numpy as np

from config import load_color_schemes, save_color_schemes, DEFAULT_COLOR_SCHEME, DEFAULT_MAP_SCALE
from heightmap import read_r16_heightmap, read_png_heightmap, generate_random_heightmap
from terrain_renderer import render_terrain_preview, render_terrain_image
from postprocessing import add_postprocessing_effects_with_color

class ModernStyle:
    """现代扁平化界面样式"""
    BACKGROUND = "#2D2D30"
    FOREGROUND = "#FFFFFF"
    ACCENT = "#007ACC"
    BUTTON_BG = "#3E3E42"
    BUTTON_FG = "#FFFFFF"
    ENTRY_BG = "#1E1E1E"
    ENTRY_FG = "#FFFFFF"
    BORDER = "#555555"
    HIGHLIGHT = "#007ACC"
    
    @staticmethod
    def apply_style():
        """应用现代扁平化样式到ttk部件"""
        style = ttk.Style()
        
        # 确保使用正确的主题
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        elif 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # 配置ttk主题
        style.configure(".", background=ModernStyle.BACKGROUND, foreground=ModernStyle.FOREGROUND)
        style.configure("TFrame", background=ModernStyle.BACKGROUND)
        style.configure("TLabel", background=ModernStyle.BACKGROUND, foreground=ModernStyle.FOREGROUND)
        style.configure("TButton", background=ModernStyle.BUTTON_BG, foreground=ModernStyle.BUTTON_FG,
                       borderwidth=0)
        style.map("TButton",
                 background=[("active", ModernStyle.ACCENT), ("pressed", ModernStyle.HIGHLIGHT)],
                 foreground=[("active", ModernStyle.FOREGROUND), ("pressed", ModernStyle.FOREGROUND)])
        
        # 配置LabelFrame
        style.configure("TLabelframe", background=ModernStyle.BACKGROUND)
        style.configure("TLabelframe.Label", background=ModernStyle.BACKGROUND, foreground=ModernStyle.FOREGROUND)
        
        # 配置Entry
        style.configure("TEntry", fieldbackground=ModernStyle.ENTRY_BG, foreground=ModernStyle.ENTRY_FG)
        
        # 配置Combobox
        style.configure("TCombobox", fieldbackground=ModernStyle.ENTRY_BG, foreground=ModernStyle.ENTRY_FG)
        style.map("TCombobox",
                 fieldbackground=[("readonly", ModernStyle.ENTRY_BG)],
                 foreground=[("readonly", ModernStyle.ENTRY_FG)])
        
        # 配置Checkbutton
        style.configure("TCheckbutton", background=ModernStyle.BACKGROUND, foreground=ModernStyle.FOREGROUND)
        
        # 配置自定义样式
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground=ModernStyle.ACCENT)
        style.configure("Header.TLabel", font=("Arial", 12, "bold"), foreground=ModernStyle.ACCENT)
        style.configure("Primary.TButton", background=ModernStyle.ACCENT, foreground=ModernStyle.FOREGROUND)
        style.map("Primary.TButton",
                 background=[("active", ModernStyle.HIGHLIGHT), ("pressed", "#005999")])

class TerrainVisualizerApp:
    """科幻地形可视化器应用"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("科幻地形可视化器")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernStyle.BACKGROUND)
        
        # 应用现代扁平化样式
        ModernStyle.apply_style()
        
        # 初始化变量
        self.heightmap = None
        self.color_schemes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "color_schemes.yaml")
        self.color_schemes, self.map_scale = load_color_schemes(self.color_schemes_path)
        
        # 创建界面
        self.create_ui()
        
        # 更新界面
        self.update_scheme_list()
        
        # 生成随机高度图用于演示
        self.generate_demo_heightmap()
    
    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 创建右侧预览面板
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置控制面板
        self.setup_control_panel(control_frame)
        
        # 设置预览面板
        self.setup_preview_panel(preview_frame)
    
    def setup_control_panel(self, parent):
        """设置控制面板"""
        # 标题
        ttk.Label(parent, text="科幻地形可视化器", style="Title.TLabel").pack(pady=(0, 20))
        
        # 文件操作区域
        file_frame = ttk.LabelFrame(parent, text="文件操作")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="加载高度图", command=self.load_heightmap).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(file_frame, text="生成随机高度图", command=self.generate_random_heightmap).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(file_frame, text="保存地形图像", command=self.save_terrain_image, style="Primary.TButton").pack(fill=tk.X, padx=5, pady=5)
        
        # 地图比例尺区域
        scale_frame = ttk.LabelFrame(parent, text="地图比例尺")
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 宽度
        width_frame = ttk.Frame(scale_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(width_frame, text="宽度 (km):").pack(side=tk.LEFT)
        self.width_km = tk.DoubleVar(value=self.map_scale["width_km"])
        ttk.Entry(width_frame, textvariable=self.width_km, width=10).pack(side=tk.RIGHT)
        
        # 高度
        height_frame = ttk.Frame(scale_frame)
        height_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(height_frame, text="高度 (km):").pack(side=tk.LEFT)
        self.height_km = tk.DoubleVar(value=self.map_scale["height_km"])
        ttk.Entry(height_frame, textvariable=self.height_km, width=10).pack(side=tk.RIGHT)
        
        # 最大海拔
        elevation_frame = ttk.Frame(scale_frame)
        elevation_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(elevation_frame, text="最大海拔 (km):").pack(side=tk.LEFT)
        self.max_elevation_km = tk.DoubleVar(value=self.map_scale["max_elevation_km"])
        ttk.Entry(elevation_frame, textvariable=self.max_elevation_km, width=10).pack(side=tk.RIGHT)
        
        # 应用比例尺按钮
        ttk.Button(scale_frame, text="应用比例尺", command=self.apply_map_scale).pack(fill=tk.X, padx=5, pady=5)
        
        # 渲染参数区域
        render_frame = ttk.LabelFrame(parent, text="渲染参数")
        render_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 分辨率
        resolution_frame = ttk.Frame(render_frame)
        resolution_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(resolution_frame, text="分辨率:").pack(side=tk.LEFT)
        self.resolution = tk.IntVar(value=500)
        ttk.Combobox(resolution_frame, textvariable=self.resolution, 
                    values=[250, 500, 1000, 2000, 4000], width=8).pack(side=tk.RIGHT)
        
        # 等高线数量
        contour_frame = ttk.Frame(render_frame)
        contour_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(contour_frame, text="等高线数量:").pack(side=tk.LEFT)
        self.contour_levels = tk.IntVar(value=20)
        ttk.Combobox(contour_frame, textvariable=self.contour_levels, 
                    values=[10, 15, 20, 30, 50], width=8).pack(side=tk.RIGHT)
        
        # 显示网格
        grid_frame = ttk.Frame(render_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(grid_frame, text="显示网格:").pack(side=tk.LEFT)
        self.show_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid_frame, variable=self.show_grid, command=self.render_preview).pack(side=tk.RIGHT)
        
        # 显示高度标签
        labels_frame = ttk.Frame(render_frame)
        labels_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(labels_frame, text="显示高度标签:").pack(side=tk.LEFT)
        self.show_labels = tk.BooleanVar(value=True)
        ttk.Checkbutton(labels_frame, variable=self.show_labels, command=self.render_preview).pack(side=tk.RIGHT)
        
        # 应用渲染参数按钮
        ttk.Button(render_frame, text="应用渲染参数", command=self.render_preview).pack(fill=tk.X, padx=5, pady=5)
        
        # 配色方案区域
        color_frame = ttk.LabelFrame(parent, text="配色方案")
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配色方案选择
        scheme_frame = ttk.Frame(color_frame)
        scheme_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(scheme_frame, text="配色方案:").pack(side=tk.LEFT)
        self.current_scheme_name = tk.StringVar()
        self.scheme_combo = ttk.Combobox(scheme_frame, textvariable=self.current_scheme_name, width=15)
        self.scheme_combo.pack(side=tk.RIGHT)
        self.scheme_combo.bind("<<ComboboxSelected>>", lambda e: self.render_preview())
        
        # 配色方案操作按钮
        ttk.Button(color_frame, text="编辑配色方案", command=self.edit_colors).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(color_frame, text="新建配色方案", command=self.new_color_scheme).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(color_frame, text="导入配色方案", command=self.load_scheme).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(color_frame, text="导出配色方案", command=self.save_scheme).pack(fill=tk.X, padx=5, pady=5)
    
    def setup_preview_panel(self, parent):
        """设置预览面板"""
        # 创建matplotlib图形
        self.figure = plt.figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 添加工具栏
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)
        
        ttk.Button(toolbar_frame, text="刷新预览", command=self.render_preview).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar_frame, text="导出高质量图像", command=self.save_terrain_image, 
                  style="Primary.TButton").pack(side=tk.RIGHT, padx=5, pady=5)
    
    def update_scheme_list(self):
        """更新配色方案列表"""
        scheme_names = list(self.color_schemes.keys())
        self.scheme_combo['values'] = scheme_names
        
        if scheme_names and not self.current_scheme_name.get():
            self.current_scheme_name.set(scheme_names[0])
    
    def generate_demo_heightmap(self):
        """生成演示用的随机高度图"""
        self.heightmap = generate_random_heightmap(500, 500)
        self.render_preview()
    
    def load_heightmap(self):
        """加载高度图文件"""
        file_path = filedialog.askopenfilename(
            title="选择高度图文件",
            filetypes=[
                ("所有支持的格式", "*.r16;*.png;*.tif;*.tiff"),
                ("R16高度图", "*.r16"),
                ("PNG图像", "*.png"),
                ("TIFF图像", "*.tif;*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件扩展名选择读取方法
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.r16':
                self.heightmap = read_r16_heightmap(file_path)
            elif file_ext in ['.png', '.tif', '.tiff']:
                self.heightmap = read_png_heightmap(file_path)
            else:
                messagebox.showerror("错误", f"不支持的文件格式: {file_ext}")
                return
            
            # 更新窗口标题
            self.root.title(f"科幻地形可视化器 - {os.path.basename(file_path)}")
            
            # 渲染预览
            self.render_preview()
            
            messagebox.showinfo("成功", "高度图加载成功")
        except Exception as e:
            messagebox.showerror("错误", f"加载高度图失败: {e}")
    
    def generate_random_heightmap(self):
        """生成随机高度图"""
        try:
            resolution = self.resolution.get()
            self.heightmap = generate_random_heightmap(resolution, resolution)
            self.render_preview()
            messagebox.showinfo("成功", "随机高度图生成成功")
        except Exception as e:
            messagebox.showerror("错误", f"生成随机高度图失败: {e}")
    
    def apply_map_scale(self):
        """应用地图比例尺设置"""
        try:
            # 更新地图比例尺
            self.map_scale = {
                "width_km": self.width_km.get(),
                "height_km": self.height_km.get(),
                "max_elevation_km": self.max_elevation_km.get()
            }
            
            # 重新渲染预览
            self.render_preview()
            
            messagebox.showinfo("成功", "地图比例尺已更新")
        except Exception as e:
            messagebox.showerror("错误", f"应用地图比例尺失败: {e}")
    
    def render_preview(self):
        """渲染地形预览"""
        if self.heightmap is None:
            return
        
        try:
            # 获取当前配色方案
            scheme_name = self.current_scheme_name.get()
            if scheme_name in self.color_schemes:
                color_scheme = self.color_schemes[scheme_name]
            else:
                color_scheme = DEFAULT_COLOR_SCHEME
            
            # 清除当前图形
            self.ax.clear()
            
            # 渲染地形预览
            render_terrain_preview(
                self.heightmap, 
                color_scheme, 
                self.map_scale,
                resolution=min(500, self.resolution.get()),  # 预览使用较低分辨率
                contour_levels=self.contour_levels.get(),
                show_grid=self.show_grid.get(),
                show_labels=self.show_labels.get()
            )
            
            # 更新画布
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("错误", f"渲染预览失败: {e}")
    
    def save_terrain_image(self):
        """保存高质量地形图像"""
        if self.heightmap is None:
            messagebox.showerror("错误", "没有加载高度图")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存地形图像",
            defaultextension=".png",
            filetypes=[
                ("PNG图像", "*.png"),
                ("JPEG图像", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # 显示进度对话框
            progress_window = tk.Toplevel(self.root)
            progress_window.title("渲染中...")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="正在渲染高质量地形图像...").pack(pady=10)
            progress = ttk.Progressbar(progress_window, mode="indeterminate")
            progress.pack(fill=tk.X, padx=20, pady=10)
            progress.start()
            
            # 获取当前配色方案
            scheme_name = self.current_scheme_name.get()
            if scheme_name in self.color_schemes:
                color_scheme = self.color_schemes[scheme_name]
            else:
                color_scheme = DEFAULT_COLOR_SCHEME
            
            # 在后台线程中渲染
            def render_thread():
                try:
                    # 渲染高质量图像
                    output_path = render_terrain_image(
                        self.heightmap,
                        file_path,
                        color_scheme,
                        self.map_scale,
                        resolution=self.resolution.get(),
                        contour_levels=self.contour_levels.get(),
                        show_grid=self.show_grid.get(),
                        show_labels=self.show_labels.get()
                    )
                    
                    # 添加后期处理效果
                    enhanced_path = add_postprocessing_effects_with_color(output_path, color_scheme)
                    
                    # 在主线程中显示完成消息
                    self.root.after(0, lambda: messagebox.showinfo("成功", f"地形图像已保存到: {enhanced_path}"))
                    
                    # 打开生成的图像
                    self.root.after(0, lambda: os.startfile(enhanced_path) if os.name == 'nt' else None)
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("错误", f"渲染地形图像失败: {e}"))
                finally:
                    # 关闭进度对话框
                    self.root.after(0, progress_window.destroy)
            
            # 启动渲染线程
            thread = threading.Thread(target=render_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存地形图像失败: {e}")
    
    def edit_colors(self):
        """编辑当前配色方案"""
        scheme_name = self.current_scheme_name.get()
        if scheme_name not in self.color_schemes:
            messagebox.showerror("错误", f"配色方案 '{scheme_name}' 不存在")
            return
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"编辑配色方案: {scheme_name}")
        edit_window.geometry("400x500")
        edit_window.configure(bg=ModernStyle.BACKGROUND)
        
        # 获取当前方案
        current_scheme = self.color_schemes[scheme_name].copy()
        color_vars = {}
        
        # 创建颜色选择器
        for i, (key, value) in enumerate(current_scheme.items()):
            if key != "colormap":  # 颜色映射单独处理
                frame = ttk.Frame(edit_window)
                frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(frame, text=f"{key}:").pack(side=tk.LEFT, padx=5)
                color_vars[key] = tk.StringVar(value=value)
                entry = ttk.Entry(frame, textvariable=color_vars[key], width=10)
                entry.pack(side=tk.LEFT, padx=5)
                
                # 颜色选择按钮
                def make_color_chooser(k):
                    return lambda: self.choose_color(color_vars[k])
                
                ttk.Button(frame, text="选择", command=make_color_chooser(key)).pack(side=tk.LEFT, padx=5)
        
        # 颜色映射选择
        colormap_frame = ttk.Frame(edit_window)
        colormap_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(colormap_frame, text="colormap:").pack(side=tk.LEFT, padx=5)
        colormap_var = tk.StringVar(value=current_scheme.get("colormap", "plasma"))
        colormap_combo = ttk.Combobox(colormap_frame, textvariable=colormap_var, 
                                     values=["plasma", "viridis", "inferno", "magma", "cividis"])
        colormap_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 保存按钮
        def save_edited_scheme():
            # 更新配色方案
            for key, var in color_vars.items():
                current_scheme[key] = var.get()
            
            current_scheme["colormap"] = colormap_var.get()
            self.color_schemes[scheme_name] = current_scheme
            
            # 更新预览
            self.render_preview()
            edit_window.destroy()
            messagebox.showinfo("成功", f"配色方案 '{scheme_name}' 已更新")
        
        ttk.Button(edit_window, text="保存更改", command=save_edited_scheme).pack(pady=20)
    
    def choose_color(self, color_var):
        """打开颜色选择器"""
        color = colorchooser.askcolor(color_var.get())[1]
        if color:
            color_var.set(color)
    
    def new_color_scheme(self):
        """创建新的配色方案"""
        # 创建输入对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("新建配色方案")
        dialog.geometry("300x120")
        dialog.configure(bg=ModernStyle.BACKGROUND)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="配色方案名称:").pack(padx=10, pady=(10, 5))
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(padx=10, pady=5)
        name_entry.focus_set()
        
        # 基于现有方案选择
        ttk.Label(dialog, text="基于现有方案:").pack(padx=10, pady=(10, 5))
        
        base_scheme_var = tk.StringVar(value=list(self.color_schemes.keys())[0])
        base_scheme_combo = ttk.Combobox(dialog, textvariable=base_scheme_var, 
                                        values=list(self.color_schemes.keys()))
        base_scheme_combo.pack(padx=10, pady=5)
        
        def create_scheme():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入配色方案名称")
                return
            
            if name in self.color_schemes:
                messagebox.showerror("错误", f"配色方案 '{name}' 已存在")
                return
            
            # 复制基础方案
            base_scheme = self.color_schemes[base_scheme_var.get()].copy()
            self.color_schemes[name] = base_scheme
            
            # 更新界面
            self.update_scheme_list()
            self.current_scheme_name.set(name)
            self.render_preview()
            
            dialog.destroy()
            
            # 打开编辑器
            self.edit_colors()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="创建", command=create_scheme).pack(side=tk.RIGHT, padx=5)
    
    def save_scheme(self):
        """保存配色方案到文件"""
        # 更新地图比例尺
        self.map_scale = {
            "width_km": self.width_km.get(),
            "height_km": self.height_km.get(),
            "max_elevation_km": self.max_elevation_km.get()
        }
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存配色方案",
            defaultextension=".yaml",
            filetypes=[("YAML文件", "*.yaml"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        # 保存到YAML文件
        if save_color_schemes(self.color_schemes, self.map_scale, file_path):
            messagebox.showinfo("成功", "配色方案和地图比例尺已保存")
        else:
            messagebox.showerror("错误", "保存配色方案失败")
    
    def load_scheme(self):
        """从文件加载配色方案"""
        file_path = filedialog.askopenfilename(
            title="加载配色方案",
            filetypes=[("YAML文件", "*.yaml"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            color_schemes, map_scale = load_color_schemes(file_path)
            self.color_schemes = color_schemes
            self.map_scale = map_scale
            
            # 更新界面
            self.update_scheme_list()
            self.width_km.set(map_scale["width_km"])
            self.height_km.set(map_scale["height_km"])
            self.max_elevation_km.set(map_scale["max_elevation_km"])
            
            messagebox.showinfo("成功", "配色方案和地图比例尺已加载")
            self.render_preview()
        except Exception as e:
            messagebox.showerror("错误", f"加载配色方案失败: {e}")