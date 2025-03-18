"""
科幻地形可视化器 - 主程序入口
"""

import os
import sys
import tkinter as tk
from gui import TerrainVisualizerApp

def main():
    """主程序入口"""
    print("启动科幻地形可视化器...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("科幻地形可视化器")
    
    # 设置图标（如果有）
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    
    # 确保窗口在屏幕中央显示
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    print("创建应用实例...")
    # 创建应用
    app = TerrainVisualizerApp(root)
    
    print("启动主循环...")
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"程序启动失败: {e}")
        traceback.print_exc()