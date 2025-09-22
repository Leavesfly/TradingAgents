import time
import json


def create_neutral_debator(llm):
    """创建中性风险辩论者节点函数
    
    参数:
        llm: 语言模型
        
    返回:
        中性风险辩论者节点函数
    """
    def neutral_node(state) -> dict:
        """中性风险辩论者节点，用于提出平衡的投资策略"""
        # 获取风险辩论状态和历史记录
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        # 获取其他分析师的当前响应
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        # 获取各种研究报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 获取交易员决策
        trader_decision = state["trader_investment_plan"]

        # 构建提示词
        prompt = f"""作为中性风险分析师，你的角色是提供一个平衡的视角，权衡交易员决策或计划的潜在收益和风险。你优先考虑全面的方法，评估利弊，同时考虑更广泛的市场趋势、潜在的经济变化和多样化策略。以下是交易员的决策：

{trader_decision}

你的任务是挑战激进和保守分析师，指出每种观点可能过于乐观或过于谨慎的地方。使用以下数据源的见解来支持一个适度、可持续的策略来调整交易员的决策：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务报告：{news_report}
公司基本面报告：{fundamentals_report}
这是当前的对话历史：{history} 这是激进分析师的最后回应：{current_risky_response} 这是保守分析师的最后回应：{current_safe_response}。如果没有其他观点的回应，不要臆测，只需提出你的观点。

通过批判性地分析双方来积极参与，解决激进和保守论点中的弱点，以倡导更平衡的方法。挑战他们的每一点，以说明为什么适度的风险策略可能提供两全其美的效果，既提供增长潜力，又防范极端波动。专注于辩论而不是简单地呈现数据，旨在展示平衡的观点如何带来最可靠的结果。以对话方式输出，就像你在说话一样，不要使用任何特殊格式。"""

        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 格式化论点
        argument = f"中性分析师: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node