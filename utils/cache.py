"""
缓存模块 - 为 ADME Strategy Copilot 提供结果缓存

避免重复的 API 调用和计算，提升性能。
"""

from __future__ import annotations

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import pickle

logger = logging.getLogger("adme_cache")

T = TypeVar('T')


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self) -> Any:
        """访问缓存并增加命中计数"""
        self.hit_count += 1
        return self.value


class Cache:
    """内存缓存"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Args:
            default_ttl: 默认过期时间（秒）
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        self._hits += 1
        return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        expires_at = None
        if ttl is None:
            ttl = self._default_ttl
        if ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "entries": len(self._cache)
        }


class DiskCache:
    """磁盘缓存"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 86400):
        """
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
        """
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._default_ttl = default_ttl
        self._memory_cache = Cache(default_ttl=3600)  # 内存缓存1小时
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{hash_key}.cache"
    
    def _load_from_disk(self, path: Path) -> Optional[CacheEntry]:
        """从磁盘加载缓存"""
        try:
            with open(path, 'rb') as f:
                entry = pickle.load(f)
                if entry.is_expired():
                    path.unlink(missing_ok=True)
                    return None
                return entry
        except Exception as e:
            logger.warning(f"加载缓存失败 {path}: {e}")
            return None
    
    def _save_to_disk(self, key: str, entry: CacheEntry) -> None:
        """保存缓存到磁盘"""
        try:
            path = self._get_cache_path(key)
            with open(path, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.warning(f"保存缓存失败 {key}: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # 先检查内存缓存
        value = self._memory_cache.get(key)
        if value is not None:
            return value
        
        # 再检查磁盘缓存
        path = self._get_cache_path(key)
        if path.exists():
            entry = self._load_from_disk(path)
            if entry:
                self._memory_cache.set(key, entry.value)  # 回填内存缓存
                return entry.access()
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self._default_ttl
        
        expires_at = None
        if ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        # 保存到内存和磁盘
        self._memory_cache.set(key, value, ttl)
        self._save_to_disk(key, entry)
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        self._memory_cache.delete(key)
        path = self._get_cache_path(key)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._memory_cache.clear()
        for path in self._cache_dir.glob("*.cache"):
            path.unlink(missing_ok=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        disk_entries = len(list(self._cache_dir.glob("*.cache")))
        return {
            "memory_cache": self._memory_cache.get_stats(),
            "disk_entries": disk_entries
        }


def cached(
    cache: Cache,
    ttl: int = 3600,
    key_func: Optional[Callable[..., str]] = None
):
    """
    缓存装饰器
    
    Args:
        cache: 缓存实例
        ttl: 过期时间（秒）
        key_func: 生成缓存键的函数
    
    Example:
        @cached(cache, ttl=3600)
        def expensive_function(arg1, arg2):
            return result
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = "|".join(key_parts)
            
            # 尝试获取缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存结果
            cache.set(cache_key, result, ttl)
            logger.debug(f"缓存存储: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# 便捷函数
def create_memory_cache(ttl: int = 3600) -> Cache:
    """创建内存缓存"""
    return Cache(default_ttl=ttl)


def create_disk_cache(cache_dir: str = ".cache", ttl: int = 86400) -> DiskCache:
    """创建磁盘缓存"""
    return DiskCache(cache_dir=cache_dir, default_ttl=ttl)


# 全局缓存实例
_global_cache: Optional[Cache] = None


def get_global_cache() -> Cache:
    """获取全局缓存"""
    global _global_cache
    if _global_cache is None:
        _global_cache = create_disk_cache()
    return _global_cache
