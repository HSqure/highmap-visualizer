/**
 * 地形渲染模块 - 使用Three.js渲染3D地形
 */

class TerrainRenderer {
  constructor(canvas, colorScheme, mapScale) {
    this.canvas = canvas;
    this.colorScheme = colorScheme;
    this.mapScale = mapScale;
    this.heightmap = null;
    
    // Three.js场景
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.terrain = null;
    this.contours = null;
    this.grid = null;
    
    // 渲染参数
    this.showGrid = true;
    this.showLabels = true;
    this.contourLevels = 20;
    this.resolution = 500;
    
    // 初始化渲染器
    this.init();
  }
  
  // 初始化Three.js场景
  init() {
    // 创建场景
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.colorScheme.background);
    
    // 创建相机
    this.camera = new THREE.PerspectiveCamera(45, this.canvas.clientWidth / this.canvas.clientHeight, 0.1, 1000);
    this.camera.position.set(0, 5, 10);
    this.camera.lookAt(0, 0, 0);
    
    // 创建渲染器
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    
    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);
    
    // 添加方向光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    this.scene.add(directionalLight);
    
    // 添加轨道控制器
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    
    // 开始动画循环
    this.animate();
    
    // 处理窗口大小变化
    window.addEventListener('resize', () => this.onWindowResize());
  }
  
  // 窗口大小变化处理
  onWindowResize() {
    this.camera.aspect = this.canvas.clientWidth / this.canvas.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
  }
  
  // 动画循环
  animate() {
    requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
  
  // 设置高度图
  setHeightmap(heightmap) {
    this.heightmap = heightmap;
    this.renderTerrain();
  }
  
  // 设置配色方案
  setColorScheme(colorScheme) {
    this.colorScheme = colorScheme;
    this.scene.background = new THREE.Color(this.colorScheme.background);
    this.renderTerrain();
  }
  
  // 设置地图比例尺
  setMapScale(mapScale) {
    this.mapScale = mapScale;
    this.renderTerrain();
  }
  
  // 设置渲染参数
  setRenderParams(params) {
    if (params.showGrid !== undefined) this.showGrid = params.showGrid;
    if (params.showLabels !== undefined) this.showLabels = params.showLabels;
    if (params.contourLevels !== undefined) this.contourLevels = params.contourLevels;
    if (params.resolution !== undefined) this.resolution = params.resolution;
    this.renderTerrain();
  }
  
  // 渲染地形
  renderTerrain() {
    if (!this.heightmap) return;
    
    // 清除现有地形
    if (this.terrain) this.scene.remove(this.terrain);
    if (this.contours) this.scene.remove(this.contours);
    if (this.grid) this.scene.remove(this.grid);
    
    // 创建地形几何体
    const geometry = new THREE.PlaneGeometry(
      this.mapScale.width_km, 
      this.mapScale.height_km, 
      this.heightmap.width - 1, 
      this.heightmap.height - 1
    );
    
    // 设置顶点高度
    const vertices = geometry.attributes.position.array;
    const maxElevation = this.mapScale.max_elevation_km;
    
    for (let i = 0; i < vertices.length / 3; i++) {
      const x = Math.floor(i % this.heightmap.width);
      const y = Math.floor(i / this.heightmap.width);
      const heightIndex = y * this.heightmap.width + x;
      
      if (heightIndex < this.heightmap.data.length) {
        vertices[i * 3 + 2] = this.heightmap.data[heightIndex] * maxElevation;
      }
    }
    
    geometry.computeVertexNormals();
    
    // 创建材质
    const material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      wireframe: false,
      flatShading: false,
      vertexColors: false
    });
    
    // 创建地形网格
    this.terrain = new THREE.Mesh(geometry, material);
    this.terrain.rotation.x = -Math.PI / 2;
    this.scene.add(this.terrain);
    
    // 添加等高线
    this.addContours();
    
    // 添加网格
    if (this.showGrid) {
      this.addGrid();
    }
    
    // 重置相机位置
    this.resetCamera();
    
    // 返回地形信息
    return this.getTerrainInfo();
  }
  
  // 添加等高线
  addContours() {
    if (!this.heightmap || this.contourLevels <= 0) return;
    
    const contourGroup = new THREE.Group();
    const maxElevation = this.mapScale.max_elevation_km;
    
    // 计算高度范围
    let minHeight = Infinity;
    let maxHeight = -Infinity;
    
    for (let i = 0; i < this.heightmap.data.length; i++) {
      minHeight = Math.min(minHeight, this.heightmap.data[i]);
      maxHeight = Math.max(maxHeight, this.heightmap.data[i]);
    }
    
    const heightRange = maxHeight - minHeight;
    
    if (heightRange > 0) {
      // 生成等高线级别
      const levels = [];
      for (let i = 0; i < this.contourLevels; i++) {
        levels.push(minHeight + (i / (this.contourLevels - 1)) * heightRange);
      }
      
      // 为每个等高线级别创建线条
      for (let level of levels) {
        const points = [];
        const scaledLevel = level * maxElevation;
        
        // 简化的等高线生成算法
        for (let y = 0; y < this.heightmap.height - 1; y++) {
          for (let x = 0; x < this.heightmap.width - 1; x++) {
            const idx = y * this.heightmap.width + x;
            const h00 = this.heightmap.data[idx] * maxElevation;
            const h10 = this.heightmap.data[idx + 1] * maxElevation;
            const h01 = this.heightmap.data[idx + this.heightmap.width] * maxElevation;
            const h11 = this.heightmap.data[idx + this.heightmap.width + 1] * maxElevation;
            
            // 检查是否与等高线相交
            if ((h00 <= scaledLevel && h10 > scaledLevel) || 
                (h00 > scaledLevel && h10 <= scaledLevel)) {
              const t = (scaledLevel - h00) / (h10 - h00);
              const px = x + t;
              const py = y;
              points.push(new THREE.Vector3(
                (px / this.heightmap.width - 0.5) * this.mapScale.width_km,
                scaledLevel,
                (py / this.heightmap.height - 0.5) * this.mapScale.height_km
              ));
            }
            
            if ((h00 <= scaledLevel && h01 > scaledLevel) || 
                (h00 > scaledLevel && h01 <= scaledLevel)) {
              const t = (scaledLevel - h00) / (h01 - h00);
              const px = x;
              const py = y + t;
              points.push(new THREE.Vector3(
                (px / this.heightmap.width - 0.5) * this.mapScale.width_km,
                scaledLevel,
                (py / this.heightmap.height - 0.5) * this.mapScale.height_km
              ));
            }
          }
        }
        
        if (points.length > 1) {
          const geometry = new THREE.BufferGeometry().setFromPoints(points);
          const material = new THREE.LineBasicMaterial({ 
            color: new THREE.Color(this.colorScheme.contour),
            opacity: 0.6,
            transparent: true
          });
          
          const line = new THREE.Line(geometry, material);
          line.rotation.x = -Math.PI / 2;
          contourGroup.add(line);
        }
      }
      
      this.scene.add(contourGroup);
      this.contours = contourGroup;
    }
  }
  
  // 添加网格
  addGrid() {
    const gridSize = Math.max(this.mapScale.width_km, this.mapScale.height_km);
    const gridDivisions = 10;
    
    const grid = new THREE.GridHelper(
      gridSize, 
      gridDivisions, 
      new THREE.Color(this.colorScheme.grid), 
      new THREE.Color(this.colorScheme.grid)
    );
    
    grid.material.opacity = 0.2;
    grid.material.transparent = true;
    
    this.scene.add(grid);
    this.grid = grid;
  }
  
  // 重置相机位置
  resetCamera() {
    const maxDimension = Math.max(this.mapScale.width_km, this.mapScale.height_km);
    const maxElevation = this.mapScale.max_elevation_km;
    
    this.camera.position.set(0, maxElevation * 2 + maxDimension * 0.5, maxDimension * 0.8);
    this.camera.lookAt(0, 0, 0);
    this.controls.update();
  }
  
  // 获取地形信息
  getTerrainInfo() {
    if (!this.heightmap) return null;
    
    // 计算高度范围
    let minHeight = Infinity;
    let maxHeight = -Infinity;
    
    for (let i = 0; i < this.heightmap.data.length; i++) {
      minHeight = Math.min(minHeight, this.heightmap.data[i]);
      maxHeight = Math.max(maxHeight, this.heightmap.data[i]);
    }
    
    const heightRange = maxHeight - minHeight;
    const maxElevation = this.mapScale.max_elevation_km;
    
    return {
      minElevation: minHeight * maxElevation * 1000, // 转换为米
      maxElevation: maxHeight * maxElevation * 1000,
      elevationRange: heightRange * maxElevation * 1000,
      mapWidth: this.mapScale.width_km,
      mapHeight: this.mapScale.height_km,
      resolution: this.resolution
    };
  }
  
  // 导出地形图像
  exportTerrainImage() {
    return new Promise((resolve) => {
      // 保存当前相机位置
      const currentPosition = this.camera.position.clone();
      const currentTarget = this.controls.target.clone();
      
      // 设置俯视图
      this.camera.position.set(0, this.mapScale.max_elevation_km * 3, 0);
      this.camera.lookAt(0, 0, 0);
      this.controls.update();
      
      // 渲染一帧
      this.renderer.render(this.scene, this.camera);
      
      // 获取图像数据
      const imageData = this.renderer.domElement.toDataURL('image/png');
      
      // 恢复相机位置
      this.camera.position.copy(currentPosition);
      this.controls.target.copy(currentTarget);
      this.controls.update();
      
      resolve(imageData);
    });
  }
}