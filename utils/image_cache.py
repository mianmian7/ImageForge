"""
图像缓存管理器模块
提供图像缓存功能，避免重复加载
"""

from PIL import Image, ImageTk
from typing import Dict, Tuple, Optional
from collections import OrderedDict
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageCache:
    """
    图像缓存管理器类
    使用LRU策略管理缓存
    """
    
    def __init__(self, max_cache_size: int = 50):
        """
        初始化图像缓存管理器
        
        Args:
            max_cache_size: 最大缓存数量
        """
        self.max_cache_size = max_cache_size
        self._cache: OrderedDict[str, ImageTk.PhotoImage] = OrderedDict()
        self._cache_info: Dict[str, dict] = {}
        logger.info(f"图像缓存管理器已初始化，最大缓存数量: {max_cache_size}")
    
    def get_thumbnail(self, image_path: str, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
        """
        获取缓存的缩略图
        
        Args:
            image_path: 图像文件路径
            size: 缩略图尺寸 (width, height)
            
        Returns:
            ImageTk.PhotoImage: 缓存的图像对象，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(image_path, size)
        
        if cache_key in self._cache:
            # 移动到末尾（表示最近使用）
            self._cache.move_to_end(cache_key)
            logger.debug(f"缓存命中: {cache_key}")
            return self._cache[cache_key]
        
        logger.debug(f"缓存未命中: {cache_key}")
        return None
    
    def put_thumbnail(self, image_path: str, size: Tuple[int, int], 
                     photo_image: ImageTk.PhotoImage):
        """
        将缩略图放入缓存
        
        Args:
            image_path: 图像文件路径
            size: 缩略图尺寸 (width, height)
            photo_image: 要缓存的图像对象
        """
        cache_key = self._generate_cache_key(image_path, size)
        
        # 如果缓存已满，删除最旧的项
        if len(self._cache) >= self.max_cache_size and cache_key not in self._cache:
            oldest_key = next(iter(self._cache))
            self._remove_from_cache(oldest_key)
            logger.debug(f"缓存已满，移除最旧项: {oldest_key}")
        
        self._cache[cache_key] = photo_image
        self._cache_info[cache_key] = {
            'image_path': image_path,
            'size': size
        }
        logger.debug(f"添加到缓存: {cache_key}")
    
    def load_and_cache(self, image_path: str, size: Tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
        """
        加载图像并缓存（如果缓存中没有）
        
        Args:
            image_path: 图像文件路径
            size: 缩略图最大尺寸 (max_width, max_height)
            
        Returns:
            ImageTk.PhotoImage: 图像对象
        """
        # 先尝试从缓存获取
        cached_image = self.get_thumbnail(image_path, size)
        if cached_image:
            return cached_image
        
        # 缓存中没有，加载并缓存
        try:
            with Image.open(image_path) as img:
                # 创建副本以避免文件保持打开
                img_copy = img.copy()
                
                # 计算缩略图尺寸
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 转换为 PhotoImage
                photo = ImageTk.PhotoImage(img_copy)
                
                # 放入缓存
                self.put_thumbnail(image_path, size, photo)
                
                logger.debug(f"加载并缓存图像: {image_path}")
                return photo
                
        except Exception as e:
            logger.error(f"加载图像失败: {image_path}, 错误: {e}")
            return None
    
    def invalidate(self, image_path: str):
        """
        使指定图像的所有缓存失效
        
        Args:
            image_path: 图像文件路径
        """
        keys_to_remove = [
            key for key, info in self._cache_info.items()
            if info['image_path'] == image_path
        ]
        
        for key in keys_to_remove:
            self._remove_from_cache(key)
            logger.debug(f"使缓存失效: {key}")
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._cache_info.clear()
        logger.info("已清空所有图像缓存")
    
    def get_cache_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        return {
            'current_size': len(self._cache),
            'max_size': self.max_cache_size,
            'usage_percentage': (len(self._cache) / self.max_cache_size) * 100
        }
    
    def _generate_cache_key(self, image_path: str, size: Tuple[int, int]) -> str:
        """
        生成缓存键
        
        Args:
            image_path: 图像文件路径
            size: 缩略图尺寸
            
        Returns:
            str: 缓存键
        """
        return f"{image_path}_{size[0]}x{size[1]}"
    
    def _remove_from_cache(self, cache_key: str):
        """
        从缓存中移除项
        
        Args:
            cache_key: 缓存键
        """
        if cache_key in self._cache:
            del self._cache[cache_key]
        if cache_key in self._cache_info:
            del self._cache_info[cache_key]


# 全局缓存实例（单例模式）
_global_cache: Optional[ImageCache] = None


def get_image_cache(max_size: int = 50) -> ImageCache:
    """
    获取全局图像缓存实例
    
    Args:
        max_size: 最大缓存数量
        
    Returns:
        ImageCache: 图像缓存管理器实例
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache(max_size)
    return _global_cache
