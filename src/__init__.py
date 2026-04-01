"""
七政四余排盘工具
七政：日月金水木火土
四余：紫炁/月孛/罗睺/计都
"""

from .core import calculate_qizheng
from .output import to_json

__version__ = "0.1.0"
__all__ = ["calculate_qizheng", "to_json"]
