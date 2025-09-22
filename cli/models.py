from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class AnalystType(str, Enum):
    """分析师类型枚举，定义可用的分析师类型"""
    MARKET = "market"          # 市场分析师
    SOCIAL = "social"          # 社交媒体分析师
    NEWS = "news"              # 新闻分析师
    FUNDAMENTALS = "fundamentals"  # 基本面分析师