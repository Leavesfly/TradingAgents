import time
import json


def create_research_manager(llm, memory):
    """创建研究经理节点函数
    
    参数:
        llm: 语言模型
        memory: 记忆模块，用于存储和检索历史情境
        
    返回:
        研究经理节点函数
    """
    def research_manager_node(state) -> dict:
        """研究经理节点，用于评估辩论并做出投资决策"""
        # 获取辩论历史和各种研究报告
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 获取投资辩论状态
        investment_debate_state = state["investment_debate_state"]

        # 组合当前情境信息
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # 从记忆中获取类似情境
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 格式化历史记忆字符串
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 构建提示词
        prompt = f"""作为投资组合经理和辩论协调员，你的角色是批判性地评估这一轮辩论并做出明确的决定：支持空头分析师、多头分析师，或者只有在基于所呈现的论点强烈证明的情况下才选择持有。

简洁地总结双方的关键点，重点关注最令人信服的证据或推理。你的建议——买入、卖出或持有——必须明确且可操作。避免仅仅因为双方都有有效观点就默认选择持有；要基于辩论中最有力的论点坚定立场。

此外，为交易员制定详细的投资计划。这应包括：

你的建议：基于最令人信服的论点的明确立场。
理由：解释为什么这些论点导致你的结论。
战略行动：实施建议的具体步骤。
考虑到你在类似情况下的过去错误。利用这些见解来完善你的决策，确保你在学习和改进。以对话方式呈现你的分析，就像自然说话一样，不要使用特殊格式。

以下是你过去对错误的反思：
\"{past_memory_str}\"

以下是辩论：
辩论历史：
{history}"""
        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 更新投资辩论状态
        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        # 返回更新后的状态和投资计划
        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node