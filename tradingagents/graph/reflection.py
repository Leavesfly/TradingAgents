# TradingAgents/graph/reflection.py
# 反思模块，用于处理决策反思和更新记忆

from typing import Dict, Any
from langchain_openai import ChatOpenAI


class Reflector:
    """处理决策反思和更新记忆"""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """使用语言模型初始化反思器
        
        参数:
            quick_thinking_llm: 快速思考的语言模型
        """
        self.quick_thinking_llm = quick_thinking_llm
        self.reflection_system_prompt = self._get_reflection_prompt()

    def _get_reflection_prompt(self) -> str:
        """获取反思的系统提示词
        
        返回:
            反思的系统提示词字符串
        """
        return """
你是一名专业的金融分析师，任务是审查交易决策/分析并提供全面的逐步分析。
你的目标是提供关于投资决策的详细见解，并突出改进的机会，严格遵守以下准则：

1. 推理：
   - 对于每个交易决策，确定它是正确还是错误。正确的决策会带来收益的增加，而错误的决策则相反。
   - 分析每个成功或错误的贡献因素。考虑：
     - 市场情报。
     - 技术指标。
     - 技术信号。
     - 价格变动分析。
     - 整体市场数据分析 
     - 新闻分析。
     - 社交媒体和情绪分析。
     - 基本面数据分析。
     - 权衡决策过程中每个因素的重要性。

2. 改进：
   - 对于任何错误的决策，提出修订以最大化收益。
   - 提供详细的纠正行动或改进建议列表，包括具体建议（例如，在特定日期将决策从持有改为买入）。

3. 总结：
   - 总结从成功和错误中学到的经验教训。
   - 强调如何将这些经验教训应用到未来的交易场景中，并在类似情况之间建立联系以应用所获得的知识。

4. 查询：
   - 将总结中的关键见解提取为不超过1000个标记的简洁句子。
   - 确保压缩的句子捕捉到经验和推理的精髓，以便于参考。

严格遵守这些指示，确保你的输出详细、准确且可操作。你还将获得从价格变动、技术指标、新闻和情绪角度对市场的客观描述，以提供更多分析背景。
"""

    def _extract_current_situation(self, current_state: Dict[str, Any]) -> str:
        """从状态中提取当前市场情况
        
        参数:
            current_state: 当前状态字典
            
        返回:
            当前市场情况的字符串
        """
        curr_market_report = current_state["market_report"]
        curr_sentiment_report = current_state["sentiment_report"]
        curr_news_report = current_state["news_report"]
        curr_fundamentals_report = current_state["fundamentals_report"]

        return f"{curr_market_report}\n\n{curr_sentiment_report}\n\n{curr_news_report}\n\n{curr_fundamentals_report}"

    def _reflect_on_component(
        self, component_type: str, report: str, situation: str, returns_losses
    ) -> str:
        """为组件生成反思
        
        参数:
            component_type: 组件类型
            report: 报告内容
            situation: 当前情况
            returns_losses: 收益/损失
            
        返回:
            反思结果字符串
        """
        messages = [
            ("system", self.reflection_system_prompt),
            (
                "human",
                f"收益: {returns_losses}\n\n分析/决策: {report}\n\n参考的客观市场报告: {situation}",
            ),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        return result

    def reflect_bull_researcher(self, current_state, returns_losses, bull_memory):
        """反思多头研究员的分析并更新记忆
        
        参数:
            current_state: 当前状态
            returns_losses: 收益/损失
            bull_memory: 多头记忆
        """
        situation = self._extract_current_situation(current_state)
        bull_debate_history = current_state["investment_debate_state"]["bull_history"]

        result = self._reflect_on_component(
            "BULL", bull_debate_history, situation, returns_losses
        )
        bull_memory.add_situations([(situation, result)])

    def reflect_bear_researcher(self, current_state, returns_losses, bear_memory):
        """反思空头研究员的分析并更新记忆
        
        参数:
            current_state: 当前状态
            returns_losses: 收益/损失
            bear_memory: 空头记忆
        """
        situation = self._extract_current_situation(current_state)
        bear_debate_history = current_state["investment_debate_state"]["bear_history"]

        result = self._reflect_on_component(
            "BEAR", bear_debate_history, situation, returns_losses
        )
        bear_memory.add_situations([(situation, result)])

    def reflect_trader(self, current_state, returns_losses, trader_memory):
        """反思交易员的决策并更新记忆
        
        参数:
            current_state: 当前状态
            returns_losses: 收益/损失
            trader_memory: 交易员记忆
        """
        situation = self._extract_current_situation(current_state)
        trader_decision = current_state["trader_investment_plan"]

        result = self._reflect_on_component(
            "TRADER", trader_decision, situation, returns_losses
        )
        trader_memory.add_situations([(situation, result)])

    def reflect_invest_judge(self, current_state, returns_losses, invest_judge_memory):
        """反思投资评委的决策并更新记忆
        
        参数:
            current_state: 当前状态
            returns_losses: 收益/损失
            invest_judge_memory: 投资评委记忆
        """
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["investment_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "INVEST JUDGE", judge_decision, situation, returns_losses
        )
        invest_judge_memory.add_situations([(situation, result)])

    def reflect_risk_manager(self, current_state, returns_losses, risk_manager_memory):
        """反思风险经理的决策并更新记忆
        
        参数:
            current_state: 当前状态
            returns_losses: 收益/损失
            risk_manager_memory: 风险经理记忆
        """
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["risk_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "RISK JUDGE", judge_decision, situation, returns_losses
        )
        risk_manager_memory.add_situations([(situation, result)])