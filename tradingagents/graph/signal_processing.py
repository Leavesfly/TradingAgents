# TradingAgents/graph/signal_processing.py
# 信号处理模块，用于处理交易信号以提取可操作的决策

from langchain_openai import ChatOpenAI


class SignalProcessor:
    """处理交易信号以提取可操作的决策"""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """使用语言模型初始化信号处理器
        
        参数:
            quick_thinking_llm: 快速思考的语言模型
        """
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        处理完整的交易信号以提取核心决策
        
        参数:
            full_signal: 完整的交易信号文本
            
        返回:
            提取的决策（买入、卖出或持有）
        """
        messages = [
            (
                "system",
                "你是一个高效的助手，专门设计用于分析由一组分析师提供的段落或财务报告。你的任务是提取投资决策：卖出、买入或持有。仅提供提取的决策（卖出、买入或持有）作为输出，不要添加任何额外的文本或信息。",
            ),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content