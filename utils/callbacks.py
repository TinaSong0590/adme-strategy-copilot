"""
进度回调和事件系统 - 为 ADME Strategy Copilot 提供实时反馈

支持进度追踪、事件回调和异步通知。
"""

from __future__ import annotations

import time
import logging
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger("adme_callbacks")


class PipelineEvent(str, Enum):
    """管道事件类型"""
    START = "pipeline_start"
    SKILL_LOADED = "skill_loaded"
    CHEMISTRY_START = "chemistry_start"
    CHEMISTRY_COMPLETE = "chemistry_complete"
    METABOLISM_START = "metabolism_start"
    METABOLISM_COMPLETE = "metabolism_complete"
    LITERATURE_START = "literature_start"
    LITERATURE_COMPLETE = "literature_complete"
    LINKING_START = "linking_start"
    LINKING_COMPLETE = "linking_complete"
    PROTOCOL_START = "protocol_start"
    PROTOCOL_COMPLETE = "protocol_complete"
    SYNTHESIS_START = "synthesis_start"
    SYNTHESIS_COMPLETE = "synthesis_complete"
    REPORT_WRITE = "report_write"
    COMPLETE = "pipeline_complete"
    ERROR = "pipeline_error"


@dataclass
class PipelineProgress:
    """管道进度状态"""
    current_step: str = ""
    completed_steps: List[str] = field(default_factory=list)
    step_details: Dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    start_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    
    def update(self, event: PipelineEvent, details: Optional[Dict[str, Any]] = None):
        """更新进度"""
        self.current_step = event.value
        if event.value not in self.completed_steps:
            self.completed_steps.append(event.value)
        if details:
            self.step_details[event.value] = details
        if self.start_time:
            self.elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
    
    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        total_steps = len(PipelineEvent)
        completed = len(self.completed_steps)
        return (completed / total_steps) * 100


@dataclass
class PipelineEventData:
    """事件数据"""
    event: PipelineEvent
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None


class ProgressCallback:
    """进度回调接口"""
    
    def on_event(self, event: PipelineEvent, data: PipelineEventData):
        """处理管道事件"""
        raise NotImplementedError
    
    def on_progress(self, progress: PipelineProgress):
        """处理进度更新"""
        raise NotImplementedError


class ConsoleProgressCallback(ProgressCallback):
    """控制台进度回调"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.progress = PipelineProgress()
        self._step_times: Dict[str, float] = {}
    
    def on_event(self, event: PipelineEvent, data: PipelineEventData):
        """处理事件并输出到控制台"""
        step_start = time.time()
        
        if event == PipelineEvent.START:
            self.progress.start_time = data.timestamp
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"🚀 ADME Strategy Copilot 启动")
                print(f"{'='*60}\n")
        
        elif event == PipelineEvent.SKILL_LOADED:
            skills = data.details.get("skills", [])
            if self.verbose:
                print(f"📚 已加载 {len(skills)} 个技能文件")
        
        elif event == PipelineEvent.CHEMISTRY_COMPLETE:
            rdkit = data.details.get("rdkit_used", False)
            valid = data.details.get("smiles_valid", False)
            if self.verbose:
                status = "✓" if valid else "⚠"
                print(f"🧪 化学分析完成 [RDKit: {'是' if rdkit else '否'}] {status}")
        
        elif event == PipelineEvent.METABOLISM_COMPLETE:
            pathways = data.details.get("pathways", [])
            if self.verbose:
                print(f"⚗️  代谢预测完成 [{len(pathways)} 条途径]")
        
        elif event == PipelineEvent.LITERATURE_COMPLETE:
            count = data.details.get("count", 0)
            provider = data.details.get("provider", "mock")
            if self.verbose:
                print(f"📖 文献检索完成 [{count} 篇, 来源: {provider}]")
        
        elif event == PipelineEvent.LINKING_COMPLETE:
            hotspots = data.details.get("linked_hotspots", 0)
            if self.verbose:
                print(f"🔗 化学-文献链接完成 [{hotspots} 个热点]")
        
        elif event == PipelineEvent.PROTOCOL_COMPLETE:
            assays = data.details.get("in_vitro_count", 0)
            if self.verbose:
                print(f"📋 方案设计完成 [{assays} 项体外研究]")
        
        elif event == PipelineEvent.SYNTHESIS_COMPLETE:
            mode = data.details.get("mode", "scientist")
            if self.verbose:
                print(f"📝 报告合成完成 [模式: {mode}]")
        
        elif event == PipelineEvent.COMPLETE:
            elapsed = self.progress.elapsed_seconds
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"✅ 管道完成! 耗时: {elapsed:.2f}s")
                print(f"{'='*60}\n")
        
        elif event == PipelineEvent.ERROR:
            error = data.details.get("error", "未知错误")
            if self.verbose:
                print(f"\n❌ 错误: {error}\n")
    
    def on_progress(self, progress: PipelineProgress):
        """输出进度条"""
        if self.verbose:
            percentage = progress.get_progress_percentage()
            bar_length = 30
            filled = int(bar_length * percentage / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r[{bar}] {percentage:.1f}% - {progress.current_step}", end="", flush=True)


class CallbackManager:
    """回调管理器"""
    
    def __init__(self):
        self._callbacks: List[ProgressCallback] = []
        self._event_history: List[PipelineEventData] = []
    
    def add_callback(self, callback: ProgressCallback):
        """添加回调"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: ProgressCallback):
        """移除回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def emit(self, event: PipelineEvent, details: Optional[Dict[str, Any]] = None):
        """触发事件"""
        data = PipelineEventData(
            event=event,
            timestamp=datetime.now(),
            details=details or {}
        )
        self._event_history.append(data)
        
        for callback in self._callbacks:
            try:
                callback.on_event(event, data)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")
    
    def emit_progress(self, progress: PipelineProgress):
        """触发进度更新"""
        for callback in self._callbacks:
            try:
                callback.on_progress(progress)
            except Exception as e:
                logger.error(f"进度回调执行失败: {e}")
    
    def get_history(self) -> List[PipelineEventData]:
        """获取事件历史"""
        return self._event_history.copy()
    
    def clear_history(self):
        """清空事件历史"""
        self._event_history.clear()


# 便捷函数
def create_console_callback(verbose: bool = True) -> ConsoleProgressCallback:
    """创建控制台回调"""
    return ConsoleProgressCallback(verbose=verbose)


def create_callback_manager() -> CallbackManager:
    """创建回调管理器"""
    return CallbackManager()
