# highmap-visualizer

## HTML
# 地形扫描系统技术文档

## 概述
基于Web的高度图处理系统，可将PNG/R16格式的高度图数据转换为带等高线的可视化地形图，支持批量处理和原始分辨率输出。

## 主要功能
### 1. 核心功能
- 高度图格式支持：
  - **PNG**：8位灰度图（自动解析高度数据）
  - **R16**：16位原始高程数据（当前注释状态）
- 实时可视化：
  - 颜色方案选择（plasma等）
  - 动态高度缩放
  - 可调节等高线密度
  - 网格显示开关

### 2. 批量处理系统
- 目录结构保留
- 并行处理机制
- 错误统计功能
- 文件系统API集成

### 3. 交互功能
- 实时鼠标坐标跟踪
- 动态网格系统
- 十字准星定位
- 音频反馈

## 使用方法
### 1. 单文件处理
```javascript
// 加载文件示例
const fileInput = document.getElementById('heightmap-input');
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) loadHeightmap(file);
});
