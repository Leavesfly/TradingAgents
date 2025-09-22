from typing import Annotated, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
from tradingagents.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# 研究团队状态
class InvestDebateState(TypedDict):
    """投资辩论状态，用于跟踪多头和空头分析师之间的讨论"""
    bull_history: Annotated[
        str, "多头观点对话历史"
    ]  # 多头观点对话历史
    bear_history: Annotated[
        str, "空头观点对话历史"
    ]  # 空头观点对话历史
    history: Annotated[str, "对话历史"]  # 对话历史
    current_response: Annotated[str, "最新回应"]  # 最新回应
    judge_decision: Annotated[str, "最终评委决定"]  # 最终评委决定
    count: Annotated[int, "当前对话的长度"]  # 对话长度


# 风险管理团队状态
class RiskDebateState(TypedDict):
    """风险辩论状态，用于跟踪不同风险偏好分析师之间的讨论"""
    risky_history: Annotated[
        str, "激进代理人的对话历史"
    ]  # 激进代理人的对话历史
    safe_history: Annotated[
        str, "保守代理人的对话历史"
    ]  # 保守代理人的对话历史
    neutral_history: Annotated[
        str, "中性代理人的对话历史"
    ]  # 中性代理人的对话历史
    history: Annotated[str, "对话历史"]  # 对话历史
    latest_speaker: Annotated[str, "最后发言的分析师"]
    current_risky_response: Annotated[
        str, "激进分析师的最新回应"
    ]  # 激进分析师的最新回应
    current_safe_response: Annotated[
        str, "保守分析师的最新回应"
    ]  # 保守分析师的最新回应
    current_neutral_response: Annotated[
        str, "中性分析师的最新回应"
    ]  # 中性分析师的最新回应
    judge_decision: Annotated[str, "评委的决定"]
    count: Annotated[int, "当前对话的长度"]  # 对话长度


class AgentState(MessagesState):
    """代理状态，包含交易代理所需的所有状态信息"""
    company_of_interest: Annotated[str, "我们感兴趣的交易公司"]
    trade_date: Annotated[str, "我们交易的日期"]

    sender: Annotated[str, "发送此消息的代理"]

    # 研究步骤
    market_report: Annotated[str, "市场分析师的报告"]
    sentiment_report: Annotated[str, "社交媒体分析师的报告"]
    news_report: Annotated[
        str, "新闻研究员关于当前世界事务的报告"
    ]
    fundamentals_report: Annotated[str, "基本面研究员的报告"]

    # 研究团队讨论步骤
    investment_debate_state: Annotated[
        InvestDebateState, "关于是否投资的辩论当前状态"
    ]
    investment_plan: Annotated[str, "分析师生成的计划"]

    trader_investment_plan: Annotated[str, "交易员生成的计划"]

    # 风险管理团队讨论步骤
    risk_debate_state: Annotated[
        RiskDebateState, "评估风险的辩论当前状态"
    ]
    final_trade_decision: Annotated[str, "风险分析师做出的最终决定"]