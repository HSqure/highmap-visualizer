/**
 * 主应用程序 - 科幻地形可视化器
 */

document.addEventListener('DOMContentLoaded', () => {
  // 初始化应用
  const app = new TerrainVisualizerApp();
  app.init();
});

class TerrainVisualizerApp {
  constructor() {
    // 应用状态
    this.heightmap = null;
    this.colorSchemes = null;
    this.currentScheme = 'cyberpunk';
    this.mapScale = null;
    
    // DOM元素
    this.canvas = null;
    this.terrainInfo = null;
    this.fileInput = null;
    
    // 渲染器
    this.terrainRenderer = null;
  }
  
  // 初始化应用
  init() {
    console.log('初始化科幻地形可视化器...');
    
    // 获取DOM元素
    this.canvas = document.getElementById('terrainCanvas');
    this.terrainInfo = document.getElementById('terrainInfo');
    this.fileInput = document.getElementById('heightmapFileInput');
    
    // 加载配色方案
    const { colorSchemes, mapScale } = loadColorSchemes();
    this.colorSchemes = colorSchemes;
    this.mapScale = mapScale;
    
    // 初始化渲染器
    this.initRenderer();
    
    // 绑定事件处理程序
    this.bindEvents();
    
    // 生成演示高度图
    this.generateDemoHeightmap();
    
    console.log('科幻地形可视化器初始化完成');
  }
  
  // 初始化渲染器
  initRenderer() {
    // 确保Three.js已加载
    if (!window.THREE) {
      console.error('Three.js未加载');
      return;
    }
    
    // 创建地形渲染器
    this.terrainRenderer = new TerrainRenderer(
      this.canvas,
      this.colorSchemes[this.currentScheme],
      this.mapScale
    );
  }
  
  // 绑定事件处理程序
  bindEvents() {
    // 文件操作按钮
    document.getElementById('loadHeightmapBtn').addEventListener('click', () => this.loadHeightmap());
    document.getElementById('generateRandomBtn').addEventListener('click', () => this.generateRandomHeightmap());
    document.getElementById('saveImageBtn').addEventListener('click', () => this.saveTerrainImage());
    
    // 地图比例尺
    document.getElementById('applyScaleBtn').addEventListener('click', () => this.applyMapScale());
    
    // 渲染参数
    document.getElementById('applyRenderBtn').addEventListener('click', () => this.applyRenderParams());
    
    // 配色方案
    document.getElementById('colorScheme').addEventListener('change', (e) => this.changeColorScheme(e.target.value));
    document.getElementById('editColorsBtn').addEventListener('click', () => this.openColorEditor());
    document.getElementById('newColorSchemeBtn').addEventListener('click', () => this.createNewColorScheme());
    
    // 预览操作
    document.getElementById('refreshBtn').addEventListener('click', () => this.refreshPreview());
    document.getElementById('fullscreenBtn').addEventListener('click', () => this.toggleFullscreen());
    
    // 模态框
    document.getElementById('closeColorEditorBtn').addEventListener('click', () => this.closeColorEditor());
    document.getElementById('cancelColorEditBtn').addEventListener('click', () => this.closeColorEditor());
    document.getElementById('saveColorEditBtn').addEventListener('click', () => this.saveColorScheme());
    
    // 文件输入
    this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
    
    // 窗口大小变化
    window.addEventListener('resize', () => this.handleResize());
  }
  
  // 生成演示高度图
  generateDemoHeightmap() {
    console.log('生成演示高度图...');
    const heightmap = generateRandomHeightmap(256, 256);
    this.setHeightmap(heightmap);
  }
  
程度  // 设置高度图
  setHeightmap(heightmap) {
    this.heightmap = heightmap;
    
    // 更新渲染器
    if (this.terrainRenderer) {
      this.terrainRenderer.setHeightmap(heightmap);
      
      // 更新地形信息
      const info = this.terrainRenderer.getTerrainInfo();
      if (info) {
        this.updateTerrainInfo(info);
      }
    }
  }
  
  // 更新地形信息显示
  updateTerrainInfo(info) {
    if (!this.terrainInfo || !info) return;
    
    this.terrainInfo.innerHTML = `
      MAX ELEVATION: ${info.maxElevation.toFixed(1)}m<br>
      MIN ELEVATION: ${info.minElevation.toFixed(1)}m<br>
      ELEVATION RANGE: ${info.elevationRange.toFixed(1)}m<br>
      MAP SIZE: ${info.mapWidth.toFixed(2)}x${info.mapHeight.toFixed(2)} km<br>
      RESOLUTION: ${info.resolution}x${info.resolution}
    `;
  }
  
  // 加载高度图
  loadHeightmap() {
    this.fileInput.click();
  }
  
  // 处理文件选择
  async handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
      let heightmap;
      
      // 根据文件类型处理
      if (file.name.endsWith('.r16')) {
        heightmap = await readR16Heightmap(file);
      } else if (file.name.endsWith('.png') || file.name.endsWith('.jpg') || file.name.endsWith('.jpeg')) {
        heightmap = await readPngHeightmap(file);
      } else {
        alert('不支持的文件格式。请使用.r16、.png、.jpg或.jpeg文件。');
        return;
      }
      
      this.setHeightmap(heightmap);
      console.log(`已加载高度图: ${file.name} (${heightmap.width}x${heightmap.height})`);
    } catch (error) {
      console.error('加载高度图失败:', error);
      alert(`加载高度图失败: ${error.message}`);
    }
    
    // 重置文件输入
    this.fileInput.value = '';
  }
  
  // 生成随机高度图
  generateRandomHeightmap() {
    const resolution = parseInt(document.getElementById('resolution').value) || 500;
    const heightmap = generateRandomHeightmap(resolution, resolution);
    this.setHeightmap(heightmap);
    console.log(`已生成随机高度图 (${resolution}x${resolution})`);
  }
  
  // 保存地形图像
  async saveTerrainImage() {
    if (!this.terrainRenderer) return;
    
    try {
      const imageData = await this.terrainRenderer.exportTerrainImage();
      
      // 创建下载链接
      const a = document.createElement('a');
      a.href = imageData;
      a.download = 'terrain_' + new Date().toISOString().replace(/[:.]/g, '-') + '.png';
      a.click();
      
      console.log('已保存地形图像');
    } catch (error) {
      console.error('保存地形图像失败:', error);
      alert(`保存地形图像失败: ${error.message}`);
    }
  }
  
  // 应用地图比例尺
  applyMapScale() {
    const widthKm = parseFloat(document.getElementById('widthKm').value) || 10;
    const heightKm = parseFloat(document.getElementById('heightKm').value) || 10;
    const maxElevationKm = parseFloat(document.getElementById('maxElevationKm').value) || 5;
    
    this.mapScale = {
      width_km: widthKm,
      height_km: heightKm,
      max_elevation_km: maxElevationKm
    };
    
    // 更新渲染器
    if (this.terrainRenderer) {
      this.terrainRenderer.setMapScale(this.mapScale);
      
      // 更新地形信息
      const info = this.terrainRenderer.getTerrainInfo();
      if (info) {
        this.updateTerrainInfo(info);
      }
    }
    
    // 保存到本地存储
    saveColorSchemes(this.colorSchemes, this.mapScale);
    
    console.log(`已应用地图比例尺: ${widthKm}x${heightKm} km, 最大海拔: ${maxElevationKm} km`);
  }
  
  // 应用渲染参数
  applyRenderParams() {
    const resolution = parseInt(document.getElementById('resolution').value) || 500;
    const contourLevels = parseInt(document.getElementById('contourLevels').value) || 20;
    const showGrid = document.getElementById('showGrid').checked;
    const showLabels = document.getElementById('showLabels').checked;
    
    // 更新渲染器
    if (this.terrainRenderer) {
      this.terrainRenderer.setRenderParams({
        resolution,
        contourLevels,
        showGrid,
        showLabels
      });
    }
    
    console.log(`已应用渲染参数: 分辨率=${resolution}, 等高线=${contourLevels}, 网格=${showGrid}, 标签=${showLabels}`);
  }
  
  // 更改配色方案
  changeColorScheme(schemeName) {
    if (!this.colorSchemes[schemeName]) return;
    
    this.currentScheme = schemeName;
    
    // 更新渲染器
    if (this.terrainRenderer) {
      this.terrainRenderer.setColorScheme(this.colorSchemes[schemeName]);
    }
    
    console.log(`已切换配色方案: ${schemeName}`);
  }
  
  // 打开配色方案编辑器
  openColorEditor() {
    const modal = document.getElementById('colorEditorModal');
    const colorEditor = document.querySelector('.color-editor');
    
    // 清空编辑器
    colorEditor.innerHTML = '';
    
    // 获取当前配色方案
    const scheme = this.colorSchemes[this.currentScheme];
    
    // 创建颜色编辑器界面
    for (const [key, value] of Object.entries(scheme)) {
      if (key === 'colormap') {
        // 创建下拉选择框
        const colormapOptions = ['viridis', 'plasma', 'inferno', 'magma', 'cividis'];
        
        const colormapDiv = document.createElement('div');
        colormapDiv.className = 'color-item';
        
        const label = document.createElement('label');
        label.textContent = key;
        
        const select = document.createElement('select');
        select.id = `color-${key}`;
        select.className = 'select-field';
        
        colormapOptions.forEach(option => {
          const optionEl = document.createElement('option');
          optionEl.value = option;
          optionEl.textContent = option;
          if (option === value) {
            optionEl.selected = true;
          }
          select.appendChild(optionEl);
        });
        
        colormapDiv.appendChild(label);
        colormapDiv.appendChild(select);
        colorEditor.appendChild(colormapDiv);
      } else {
        // 创建颜色选择器
        const colorDiv = document.createElement('div');
        colorDiv.className = 'color-item';
        
        const label = document.createElement('label');
        label.textContent = key;
        
        const colorPreview = document.createElement('div');
        colorPreview.className = 'color-preview';
        colorPreview.style.backgroundColor = value;
        
        const input = document.createElement('input');
        input.type = 'color';
        input.id = `color-${key}`;
        input.value = value;
        input.addEventListener('input', () => {
          colorPreview.style.backgroundColor = input.value;
        });
        
        colorDiv.appendChild(label);
        colorDiv.appendChild(colorPreview);
        colorDiv.appendChild(input);
        colorEditor.appendChild(colorDiv);
      }
    }
    
    // 显示模态框
    modal.classList.add('active');
  }
  
  // 关闭配色方案编辑器
  closeColorEditor() {
    const modal = document.getElementById('colorEditorModal');
    modal.classList.remove('active');
  }
  
  // 保存配色方案
  saveColorScheme() {
    // 获取当前配色方案
    const scheme = this.colorSchemes[this.currentScheme];
    
    // 更新配色方案
    for (const [key, value] of Object.entries(scheme)) {
      const input = document.getElementById(`color-${key}`);
      if (input) {
        scheme[key] = input.value;
      }
    }
    
    // 更新渲染器
    if (this.terrainRenderer) {
      this.terrainRenderer.setColorScheme(scheme);
    }
    
    // 保存到本地存储
    saveColorSchemes(this.colorSchemes, this.mapScale);
    
    // 关闭编辑器
    this.closeColorEditor();
    
    console.log(`已保存配色方案: ${this.currentScheme}`);
  }
  
  // 创建新配色方案
  createNewColorScheme() {
    const name = prompt('请输入新配色方案名称:');
    if (!name) return;
    
    // 检查名称是否已存在
    if (this.colorSchemes[name]) {
      alert(`配色方案 "${name}" 已存在`);
      return;
    }
    
    // 复制当前配色方案
    this.colorSchemes[name] = JSON.parse(JSON.stringify(this.colorSchemes[this.currentScheme]));
    
    // 更新下拉菜单
    const select = document.getElementById('colorScheme');
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
    
    // 切换到新配色方案
    select.value = name;
    this.changeColorScheme(name);
    
    // 打开编辑器
    this.openColorEditor();
    
    console.log(`已创建新配色方案: ${name}`);
  }
  
  // 刷新预览
  refreshPreview() {
    if (this.terrainRenderer && this.heightmap) {
      this.terrainRenderer.renderTerrain();
    }
  }
  
  // 切换全屏
  toggleFullscreen() {
    const previewCard = document.querySelector('.preview-card');
    
    if (!document.fullscreenElement) {
      if (previewCard.requestFullscreen) {
        previewCard.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }
  
  // 处理窗口大小变化
  handleResize() {
    if (this.terrainRenderer) {
      // 重新调整渲染器大小
      this.terrainRenderer.onWindowResize();
    }
  }
}