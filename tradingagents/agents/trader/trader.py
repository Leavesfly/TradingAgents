import functools
import time
import json


def create_trader(llm, memory):
    """创建交易员节点函数
    
    参数:
        llm: 语言模型
        memory: 记忆模块，用于存储和检索历史情境
        
    返回:
        交易员节点函数
    """
    def trader_node(state, name):
        """交易员节点，用于根据投资计划做出交易决策"""
        # 获取公司名称和投资计划
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        # 获取各种研究报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 组合当前情境信息
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # 从记忆中获取类似情境
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 格式化历史记忆字符串
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "未找到过去记忆。"

        # 构建上下文信息
        context = {
            "role": "user",
            "content": f"基于分析师团队的全面分析，这里是一个为{company_name}量身定制的投资计划。该计划结合了当前技术市场趋势、宏观经济指标和社交媒体情绪的见解。使用此计划作为评估下一个交易决策的基础。\n\n提议的投资计划: {investment_plan}\n\n利用这些见解做出明智和战略性的决策。",
        }

        # 构建消息列表
        messages = [
            {
                "role": "system",
                "content": f"""你是一个交易代理，正在分析市场数据以做出投资决策。基于你的分析，提供一个具体的买入、卖出或持有的建议。以坚定的决策结束，并始终在你的回复结尾加上'FINAL TRANSACTION PROPOSAL: **买入/持有/卖出**'来确认你的建议。不要忘记利用过去决策的经验教训来从错误中学习。以下是你在类似情况下交易的一些反思和学到的教训: {past_memory_str}""",
            },
            context,
        ]

        # 调用语言模型获取结果
        result = llm.invoke(messages)

        # 返回结果和交易员投资计划
        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    # 使用functools.partial创建部分应用函数，固定name参数为"Trader"
    return functools.partial(trader_node, name="Trader")