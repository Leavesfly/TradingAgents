import time
import json


def create_risky_debator(llm):
    """创建激进风险辩论者节点函数
    
    参数:
        llm: 语言模型
        
    返回:
        激进风险辩论者节点函数
    """
    def risky_node(state) -> dict:
        """激进风险辩论者节点，用于提出高风险高回报的投资策略"""
        # 获取风险辩论状态和历史记录
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        # 获取其他分析师的当前响应
        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 获取各种研究报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 获取交易员决策
        trader_decision = state["trader_investment_plan"]

        # 构建提示词
        prompt = f"""作为激进风险分析师，你的角色是积极倡导高回报、高风险的机会，强调大胆的策略和竞争优势。在评估交易员的决策或计划时，要密切关注潜在的上行空间、增长潜力和创新优势——即使这些伴随着较高的风险。使用提供的市场数据和情绪分析来加强你的论点并挑战对立观点。具体来说，直接回应保守和中性分析师提出的每一点，用数据驱动的反驳和有说服力的推理来反驳。强调他们的谨慎可能会错失关键机会，或者他们的假设可能过于保守。以下是交易员的决策：

{trader_decision}

你的任务是通过质疑和批评保守和中性立场来为交易员的决策创造一个令人信服的案例，以证明为什么你的高回报观点提供了最佳的前进道路。将以下来源的见解融入你的论点中：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务报告：{news_report}
公司基本面报告：{fundamentals_report}
这是当前的对话历史：{history} 这是保守分析师的最后论点：{current_safe_response} 这是中性分析师的最后论点：{current_neutral_response}。如果没有其他观点的回应，不要臆测，只需提出你的观点。

通过解决提出的任何具体担忧，反驳他们逻辑中的弱点，并断言承担风险以超越市场规范的好处，积极参与辩论。专注于辩论和说服，而不仅仅是呈现数据。挑战每个反驳点，以强调为什么高风险方法是最佳的。以对话方式输出，就像你在说话一样，不要使用任何特殊格式。"""

        # 调用语言模型获取响应
        response = llm.invoke(prompt)

        # 格式化论点
        argument = f"激进分析师: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    return risky_node