# TradingAgents/graph/conditional_logic.py
# 条件逻辑模块，用于确定图流程的条件判断

from tradingagents.agents.utils.agent_states import AgentState


class ConditionalLogic:
    """处理确定图流程的条件逻辑"""

    def __init__(self, max_debate_rounds=1, max_risk_discuss_rounds=1):
        """使用配置参数初始化
        
        参数:
            max_debate_rounds: 最大辩论轮数
            max_risk_discuss_rounds: 最大风险讨论轮数
        """
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    def should_continue_market(self, state: AgentState):
        """确定市场分析是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果有工具调用则返回"tools_market"，否则返回"Msg Clear Market"
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_market"
        return "Msg Clear Market"

    def should_continue_social(self, state: AgentState):
        """确定社交媒体分析是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果有工具调用则返回"tools_social"，否则返回"Msg Clear Social"
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_social"
        return "Msg Clear Social"

    def should_continue_news(self, state: AgentState):
        """确定新闻分析是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果有工具调用则返回"tools_news"，否则返回"Msg Clear News"
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_news"
        return "Msg Clear News"

    def should_continue_fundamentals(self, state: AgentState):
        """确定基本面分析是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果有工具调用则返回"tools_fundamentals"，否则返回"Msg Clear Fundamentals"
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_fundamentals"
        return "Msg Clear Fundamentals"

    def should_continue_debate(self, state: AgentState) -> str:
        """确定辩论是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果达到最大辩论轮数则返回"Research Manager"，否则根据当前响应决定下一个发言人
        """

        if (
            state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds
        ):  # 3轮两位代理之间的来回辩论
            return "Research Manager"
        if state["investment_debate_state"]["current_response"].startswith("Bull"):
            return "Bear Researcher"
        return "Bull Researcher"

    def should_continue_risk_analysis(self, state: AgentState) -> str:
        """确定风险分析是否应继续
        
        参数:
            state: 代理状态
            
        返回:
            如果达到最大风险讨论轮数则返回"Risk Judge"，否则根据最后发言者决定下一个发言人
        """
        if (
            state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds
        ):  # 3轮三位代理之间的来回讨论
            return "Risk Judge"
        if state["risk_debate_state"]["latest_speaker"].startswith("Risky"):
            return "Safe Analyst"
        if state["risk_debate_state"]["latest_speaker"].startswith("Safe"):
            return "Neutral Analyst"
        return "Risky Analyst"