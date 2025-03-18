/**
 * 高度图处理模块 - 读取和生成高度图
 */

// 读取PNG高度图
async function readPngHeightmap(file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const heightmap = new Float32Array(canvas.width * canvas.height);
      
      // 从灰度图像中提取高度值
      for (let i = 0; i < heightmap.length; i++) {
        // 使用红色通道作为高度值
        heightmap[i] = imageData.data[i * 4] / 255;
      }
      
      resolve({
        data: heightmap,
        width: canvas.width,
        height: canvas.height
      });
    };
    
    img.onerror = () => {
      reject(new Error('Failed to load image'));
    };
    
    img.src = URL.createObjectURL(file);
  });
}

// 读取R16高度图
async function readR16Heightmap(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const buffer = event.target.result;
        const dataView = new DataView(buffer);
        
        // 读取R16文件头
        const width = dataView.getUint32(0, true);
        const height = dataView.getUint32(4, true);
        
        // 检查文件大小是否正确
        if (buffer.byteLength !== 8 + width * height * 2) {
          reject(new Error('Invalid R16 file size'));
          return;
        }
        
        const heightmap = new Float32Array(width * height);
        
        // 读取高度数据
        for (let i = 0; i < width * height; i++) {
          // R16格式存储16位无符号整数，需要归一化到0-1范围
          heightmap[i] = dataView.getUint16(8 + i * 2, true) / 65535;
        }
        
        resolve({
          data: heightmap,
          width: width,
          height: height
        });
      } catch (e) {
        reject(new Error('Failed to parse R16 file: ' + e.message));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    
    reader.readAsArrayBuffer(file);
  });
}

// 生成随机高度图
function generateRandomHeightmap(width, height) {
  // 使用柏林噪声生成自然地形
  const heightmap = new Float32Array(width * height);
  
  // 简单的随机地形生成
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const index = y * width + x;
      
      // 使用简化的噪声函数
      const nx = x / width - 0.5;
      const ny = y / height - 0.5;
      
      // 多层噪声叠加
      let value = 0;
      let amplitude = 1.0;
      let frequency = 1.0;
      
      for (let i = 0; i < 6; i++) {
        value += amplitude * simplex2D(nx * frequency, ny * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
      }
      
      // 归一化到0-1范围
      heightmap[index] = (value + 1) * 0.5;
    }
  }
  
  return {
    data: heightmap,
    width: width,
    height: height
  };
}

// 简化的2D柏林噪声实现
function simplex2D(x, y) {
  // 这是一个简化版本，实际应用中应使用更完整的柏林噪声库
  const dot = (g, x, y) => g[0] * x + g[1] * y;
  const grad3 = [
    [1, 1], [-1, 1], [1, -1], [-1, -1],
    [1, 0], [-1, 0], [0, 1], [0, -1]
  ];
  
  // 伪随机梯度
  const getGradient = (ix, iy) => {
    const random = Math.sin(ix * 12.9898 + iy * 78.233) * 43758.5453;
    const index = Math.abs(Math.floor(random * 8)) % 8;
    return grad3[index];
  };
  
  // 计算贡献
  const contribution = (ix, iy, x, y) => {
    const g = getGradient(ix, iy);
    const dx = x - ix;
    const dy = y - iy;
    const t = 0.5 - dx * dx - dy * dy;
    
    if (t < 0) return 0;
    
    const t2 = t * t;
    const t4 = t2 * t2;
    return t4 * dot(g, dx, dy);
  };
  
  // 计算整数坐标
  const ix0 = Math.floor(x);
  const iy0 = Math.floor(y);
  const ix1 = ix0 + 1;
  const iy1 = iy0 + 1;
  
  // 计算分数部分
  const fx = x - ix0;
  const fy = y - iy0;
  
  // 计算四个角的贡献
  const n00 = contribution(ix0, iy0, x, y);
  const n10 = contribution(ix1, iy0, x, y);
  const n01 = contribution(ix0, iy1, x, y);
  const n11 = contribution(ix1, iy1, x, y);
  
  // 插值并返回结果
  return (n00 + n10 + n01 + n11) * 70.0;
}