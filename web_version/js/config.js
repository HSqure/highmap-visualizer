/**
 * 配置模块 - 管理配色方案和地图比例尺
 */

// 默认配色方案
const DEFAULT_COLOR_SCHEMES = {
  "cyberpunk": {
    "background": "#000000",
    "primary": "#00FFFF",
    "secondary": "#FF2E93",
    "tertiary": "#00FF85",
    "contour": "#00FFFF",
    "highlight_contour": "#FF2E93",
    "grid": "#00FFFF",
    "scan_line": "#00FFFF",
    "colormap": "plasma"
  },
  "neon": {
    "background": "#000000",
    "primary": "#7DF9FF",
    "secondary": "#FF00FF",
    "tertiary": "#39FF14",
    "contour": "#7DF9FF",
    "highlight_contour": "#FF00FF",
    "grid": "#39FF14",
    "scan_line": "#7DF9FF",
    "colormap": "viridis"
  },
  "holo": {
    "background": "#000000",
    "primary": "#00BFFF",
    "secondary": "#FF6347",
    "tertiary": "#FFD700",
    "contour": "#00BFFF",
    "highlight_contour": "#FF6347",
    "grid": "#FFD700",
    "scan_line": "#00BFFF",
    "colormap": "inferno"
  },
  "military": {
    "background": "#000000",
    "primary": "#00FF00",
    "secondary": "#FF0000",
    "tertiary": "#FFFF00",
    "contour": "#00FF00",
    "highlight_contour": "#FF0000",
    "grid": "#FFFF00",
    "scan_line": "#00FF00",
    "colormap": "cividis"
  },
  "alien": {
    "background": "#000000",
    "primary": "#39FF14",
    "secondary": "#9D00FF",
    "tertiary": "#FF7F00",
    "contour": "#39FF14",
    "highlight_contour": "#9D00FF",
    "grid": "#FF7F00",
    "scan_line": "#39FF14",
    "colormap": "magma"
  }
};

// 默认地图比例尺
const DEFAULT_MAP_SCALE = {
  "width_km": 10,
  "height_km": 10,
  "max_elevation_km": 5
};

// 加载配色方案
function loadColorSchemes() {
  const storedSchemes = localStorage.getItem('colorSchemes');
  const storedScale = localStorage.getItem('mapScale');
  
  let colorSchemes = DEFAULT_COLOR_SCHEMES;
  let mapScale = DEFAULT_MAP_SCALE;
  
  if (storedSchemes) {
    try {
      colorSchemes = JSON.parse(storedSchemes);
    } catch (e) {
      console.error('Failed to parse stored color schemes:', e);
    }
  }
  
  if (storedScale) {
    try {
      mapScale = JSON.parse(storedScale);
    } catch (e) {
      console.error('Failed to parse stored map scale:', e);
    }
  }
  
  return { colorSchemes, mapScale };
}

// 保存配色方案
function saveColorSchemes(colorSchemes, mapScale) {
  try {
    localStorage.setItem('colorSchemes', JSON.stringify(colorSchemes));
    localStorage.setItem('mapScale', JSON.stringify(mapScale));
    return true;
  } catch (e) {
    console.error('Failed to save color schemes:', e);
    return false;
  }
}

// 导出配色方案到文件
function exportColorSchemes(colorSchemes, mapScale) {
  const data = JSON.stringify({ colorSchemes, mapScale }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = 'color_schemes.json';
  a.click();
  
  URL.revokeObjectURL(url);
}

// 从文件导入配色方案
async function importColorSchemes(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        resolve(data);
      } catch (e) {
        reject(new Error('Invalid JSON file'));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    
    reader.readAsText(file);
  });
}