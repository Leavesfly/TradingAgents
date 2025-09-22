from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    """创建多头研究员节点函数
    
    参数:
        llm: 语言模型
        memory: 记忆模块，用于存储和检索历史情境
        
    返回:
        多头研究员节点函数
    """
    def bull_node(state) -> dict:
        """多头研究员节点，用于提出投资股票的论点"""
        # 获取投资辩论状态和历史记录
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        # 获取当前响应和其他研究报告
        current_response = investment_debate_state.get("current_response", "")
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
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 构建提示词
        prompt = f"""你是一名多头分析师，主张投资该股票。你的任务是建立一个强有力的、基于证据的论点，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据来解决担忧并有效反驳空头论点。

需要关注的关键点：
- 增长潜力：突出公司的市场机会、收入预测和可扩展性。
- 竞争优势：强调独特产品、强大品牌或主导市场地位等因素。
- 积极指标：使用财务健康状况、行业趋势和最近的积极新闻作为证据。
- 空头反驳点：用具体数据和合理推理批判性地分析空头论点，彻底解决担忧并说明为什么多头观点具有更强的优势。
- 参与度：以对话方式呈现你的论点，直接与空头分析师的观点互动并有效辩论，而不是仅仅列举数据。

可用资源：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的空头论点：{current_response}
类似情境的反思和学到的经验：{past_memory_str}
使用这些信息来提供一个令人信服的多头论点，反驳空头的担忧，并参与一场动态辩论，展示多头立场的优势。你还必须处理反思并从过去的经验和错误中学习。
"""

        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 格式化论点
        argument = f"多头分析师: {response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"investment_debate_state": new_investment_debate_state}

    return bull_node