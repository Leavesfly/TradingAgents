# TradingAgents/graph/propagation.py
# 状态传播模块，用于处理图中的状态初始化和传播

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class Propagator:
    """处理图中状态的初始化和传播"""

    def __init__(self, max_recur_limit=100):
        """使用配置参数初始化
        
        参数:
            max_recur_limit: 最大递归限制
        """
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """创建代理图的初始状态
        
        参数:
            company_name: 公司名称
            trade_date: 交易日期
            
        返回:
            包含初始状态的字典
        """
        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            "investment_debate_state": InvestDebateState(
                {
                    "bull_history": "",
                    "bear_history": "",
                    "history": "",
                    "current_response": "",
                    "judge_decision": "",
                    "count": 0
                }
            ),
            "risk_debate_state": RiskDebateState(
                {
                    "risky_history": "",
                    "safe_history": "",
                    "neutral_history": "",
                    "history": "",
                    "latest_speaker": "",
                    "current_risky_response": "",
                    "current_safe_response": "",
                    "current_neutral_response": "",
                    "judge_decision": "",
                    "count": 0,
                }
            ),
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
        }

    def get_graph_args(self) -> Dict[str, Any]:
        """获取图调用的参数
        
        返回:
            包含图调用参数的字典
        """
        return {
            "stream_mode": "values",
            "config": {"recursion_limit": self.max_recur_limit},
        }