from langchain_core.messages import AIMessage
import time
import json


def create_safe_debator(llm):
    """创建保守风险辩论者节点函数
    
    参数:
        llm: 语言模型
        
    返回:
        保守风险辩论者节点函数
    """
    def safe_node(state) -> dict:
        """保守风险辩论者节点，用于提出低风险的投资策略"""
        # 获取风险辩论状态和历史记录
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        # 获取其他分析师的当前响应
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 获取各种研究报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 获取交易员决策
        trader_decision = state["trader_investment_plan"]

        # 构建提示词
        prompt = f"""作为安全/保守风险分析师，你的主要目标是保护资产、最小化波动性并确保稳定、可靠的增长。你优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济衰退和市场波动性。在评估交易员的决策或计划时，批判性地检查高风险要素，指出决策可能使公司面临过度风险的地方，以及更谨慎的替代方案如何能够确保长期收益。以下是交易员的决策：

{trader_decision}

你的任务是积极反驳激进和中性分析师的论点，强调他们的观点可能忽视的潜在威胁或未能优先考虑可持续性的地方。直接回应他们的观点，从以下数据源中构建一个令人信服的案例，说明为什么低风险方法需要对交易员的决策进行调整：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务报告：{news_report}
公司基本面报告：{fundamentals_report}
这是当前的对话历史：{history} 这是激进分析师的最后回应：{current_risky_response} 这是中性分析师的最后回应：{current_neutral_response}。如果没有其他观点的回应，不要臆测，只需提出你的观点。

通过质疑他们的乐观情绪并强调他们可能忽视的潜在不利因素来参与辩论。解决他们的每个反驳点，以展示为什么保守立场最终是公司资产最安全的道路。专注于辩论和批评他们的论点，以证明低风险策略比他们的方法更强。以对话方式输出，就像你在说话一样，不要使用任何特殊格式。"""

        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 格式化论点
        argument = f"保守分析师: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    return safe_node