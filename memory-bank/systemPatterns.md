# System Patterns

This file documents code patterns and best practices used in the project.

## 架构模式

### 1. 管理器模式（Manager Pattern）
**用途**: GUI模块化，将大型窗口类拆分为专注的管理器

**模式结构**:
```python
class ExampleManager:
    """功能管理器示例"""
    
    def __init__(self, parent: tk.Widget, config, dependencies):
        """初始化管理器"""
        self.parent = parent
        self.config = config
        self.widgets = {}  # 存储UI组件
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建UI组件（私有方法）"""
        pass
    
    def _setup_layout(self):
        """设置布局（私有方法）"""
        pass
    
    def grid(self, **kwargs):
        """放置管理器到指定位置"""
        self.main_frame.grid(**kwargs)
```

**应用实例**:
- `gui/managers/status_bar_manager.py` - 状态栏管理
- `gui/managers/preview_manager.py` - 图像预览管理

---

### 2. 单例模式（Singleton Pattern）
**用途**: 确保全局只有一个实例（日志管理器、缓存管理器）

**实现方式**:
```python
class LoggerManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LoggerManager._initialized:
            self._setup()
            LoggerManager._initialized = True
```

**应用实例**:
- `utils/logger.py` - LoggerManager
- `utils/image_cache.py` - 全局缓存实例

---

### 3. LRU缓存模式
**用途**: 管理有限资源，自动淘汰最久未使用的项

**实现方式**:
```python
from collections import OrderedDict

class ImageCache:
    def __init__(self, max_size: int = 50):
        self._cache: OrderedDict = OrderedDict()
    
    def get(self, key):
        if key in self._cache:
            self._cache.move_to_end(key)  # 标记为最近使用
            return self._cache[key]
        return None
    
    def put(self, key, value):
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # 移除最旧项
        self._cache[key] = value
```

**应用实例**:
- `utils/image_cache.py` - ImageCache

---

## 代码规范

### 日志使用规范
```python
from utils.logger import get_logger

logger = get_logger(__name__)

# 不同级别的使用场景
logger.debug("详细调试信息")
logger.info("重要业务流程")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 资源管理规范
```python
# 文件操作必须使用 with 语句
with open(file_path, 'rb') as f:
    data = f.read()

# 图像对象必须使用 with 语句
with Image.open(image_path) as img:
    img = img.resize((width, height))
    img.save(output_path)
```

### 错误处理规范
```python
try:
    result = process_image(path)
except FileNotFoundError as e:
    logger.error(f"文件未找到: {path}, 错误: {e}")
    return False
except ValueError as e:
    logger.error(f"无效参数: {e}")
    return False
except Exception as e:
    logger.exception(f"未知错误: {path}")
    return False
```

---

## 工具函数模式

### 公共工具函数
**位置**: `utils/common_utils.py`

**包含函数**:
- `format_file_size(size_bytes: int) -> str` - 格式化文件大小
- `get_image_info_text(processor, image_path: str) -> str` - 获取图像信息文本
- `calculate_thumbnail_size(...) -> Tuple[int, int]` - 计算缩略图尺寸

**使用示例**:
```python
from utils.common_utils import format_file_size, get_image_info_text

# 格式化文件大小
size_text = format_file_size(1024 * 1024)  # "1.0 MB"

# 获取图像信息
info = get_image_info_text(processor, "image.jpg")  # "1920 × 1080 | 2.5 MB"
```

---

## 配置管理模式

### 配置验证流程
```python
from core.config_validator import validate_config

# 在程序启动时验证配置
is_valid, summary = validate_config(config)
if not is_valid:
    logger.error(f"配置验证失败: {summary}")
    sys.exit(1)
```

---

## 性能优化模式

### 图像缓存使用
```python
from utils.image_cache import get_image_cache

cache = get_image_cache(max_size=50)

# 加载并缓存
photo = cache.load_and_cache(image_path, (300, 300))

# 使缓存失效
cache.invalidate(image_path)
```

### 批量处理分批
```python
def process_batch(file_paths: List[str], batch_size: int = 10):
    """分批处理避免内存溢出"""
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        for path in batch:
            process_single_image(path)
        # 可选：强制垃圾回收
        import gc
        gc.collect()
```

---

## 测试模式（待实现）

### 单元测试结构
```python
import unittest
from utils.common_utils import format_file_size

class TestCommonUtils(unittest.TestCase):
    def test_format_file_size(self):
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
```