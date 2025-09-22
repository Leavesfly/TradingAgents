from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    """创建空头研究员节点函数
    
    参数:
        llm: 语言模型
        memory: 记忆模块，用于存储和检索历史情境
        
    返回:
        空头研究员节点函数
    """
    def bear_node(state) -> dict:
        """空头研究员节点，用于提出不投资股票的论点"""
        # 获取投资辩论状态和历史记录
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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
        prompt = f"""你是一名空头分析师，正在提出不投资该股票的论点。你的目标是提出一个论证充分的论点，强调风险、挑战和负面指标。利用提供的研究和数据来突出潜在的不利因素并有效反驳多头论点。

需要关注的关键点：

- 风险和挑战：突出市场饱和、财务不稳定或宏观经济威胁等因素，这些因素可能阻碍股票表现。
- 竞争劣势：强调脆弱性，如较弱的市场定位、创新能力下降或来自竞争对手的威胁。
- 负面指标：使用财务数据、市场趋势或最近的不利新闻等证据来支持你的立场。
- 多头反驳点：用具体数据和合理推理批判性地分析多头论点，揭示弱点或过于乐观的假设。
- 参与度：以对话方式呈现你的论点，直接与多头分析师的观点互动并有效辩论，而不是简单地列举事实。

可用资源：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的多头论点：{current_response}
类似情境的反思和学到的经验：{past_memory_str}
使用这些信息来提供一个令人信服的空头论点，反驳多头的主张，并参与一场动态辩论，展示投资该股票的风险和弱点。你还必须处理反思并从过去的经验和错误中学习。
"""

        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 格式化论点
        argument = f"空头分析师: {response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"investment_debate_state": new_investment_debate_state}

    return bear_node