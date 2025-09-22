from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):
    """创建市场分析师节点函数
    
    参数:
        llm: 语言模型
        toolkit: 工具包，包含各种数据获取工具
        
    返回:
        市场分析师节点函数
    """

    def market_analyst_node(state):
        """市场分析师节点，用于分析金融市场"""
        # 获取当前日期和公司信息
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # 根据配置选择工具
        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        # 系统消息，指导分析师如何分析市场
        system_message = (
            """你是一名交易助理，任务是分析金融市场。你的角色是从以下列表中为给定的市场状况或交易策略选择**最相关的指标**。目标是选择最多**8个指标**，这些指标提供互补的见解而没有冗余。类别和每个类别的指标如下：

移动平均线:
- close_50_sma: 50 SMA: 中期趋势指标。用途: 识别趋势方向并作为动态支撑/阻力。提示: 它滞后于价格; 与更快的指标结合使用以获得及时信号。
- close_200_sma: 200 SMA: 长期趋势基准。用途: 确认整体市场趋势并识别金叉/死叉设置。提示: 反应缓慢; 最适合战略趋势确认而不是频繁交易入场。
- close_10_ema: 10 EMA: 响应迅速的短期平均线。用途: 捕捉动量的快速变化和潜在入场点。提示: 在震荡市场中容易受到噪声影响; 与较长的平均线结合使用以过滤虚假信号。

MACD相关:
- macd: MACD: 通过EMA差异计算动量。用途: 寻找交叉和背离作为趋势变化的信号。提示: 在低波动性或横盘市场中与其他指标确认。
- macds: MACD信号线: MACD线的EMA平滑。用途: 与MACD线交叉触发交易。提示: 应该是更广泛策略的一部分以避免误报。
- macdh: MACD柱状图: 显示MACD线与其信号线之间的差距。用途: 可视化动量强度并及早发现背离。提示: 可能波动较大; 在快速变动的市场中与额外过滤器结合使用。

动量指标:
- rsi: RSI: 测量动量以标记超买/超卖条件。用途: 应用70/30阈值并观察背离以发出反转信号。提示: 在强劲趋势中，RSI可能保持极端值; 始终与趋势分析交叉检查。

波动率指标:
- boll: 布林带中轨: 作为布林带基础的20 SMA。用途: 作为价格变动的动态基准。提示: 与上下轨结合使用以有效识别突破或反转。
- boll_ub: 布林带上轨: 通常在中轨上方2个标准差。用途: 发出潜在超买条件和突破区域信号。提示: 与其他工具确认信号; 在强劲趋势中价格可能沿着轨道运行。
- boll_lb: 布林带下轨: 通常在中轨下方2个标准差。用途: 指示潜在超卖条件。提示: 使用额外分析以避免虚假反转信号。
- atr: ATR: 平均真实波幅以测量波动率。用途: 根据当前市场波动率设置止损水平和调整头寸规模。提示: 这是一个反应性指标，因此将其作为更广泛风险管理策略的一部分使用。

基于成交量的指标:
- vwma: VWMA: 按成交量加权的移动平均线。用途: 通过整合价格行为与成交量数据来确认趋势。提示: 注意成交量激增导致的偏差结果; 与其他成交量分析结合使用。

- 选择提供多样化和互补信息的指标。避免冗余(例如，不要同时选择rsi和stochrsi)。还要简要解释为什么它们适合给定的市场环境。当你调用工具时，请使用上面提供的指标的确切名称作为定义参数，否则你的调用将失败。请确保首先调用get_YFin_data以获取生成指标所需的CSV。撰写一份非常详细和细致的趋势报告。不要简单地说明趋势是混合的，要提供详细和细粒度的分析和见解，帮助交易员做出决策。"""
            + """ 确保在报告末尾附加一个Markdown表格，以组织报告中的要点，使其易于阅读和理解。"""
        )

        # 创建聊天提示模板
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有帮助的AI助手，与其他助手协作。"
                    "使用提供的工具来推进回答问题。"
                    "如果你无法完全回答，没关系；另一个拥有不同工具的助手"
                    "会在你停下的地方继续。执行你能做的来取得进展。"
                    "如果你或任何其他助手有最终交易建议：**买入/持有/卖出**或可交付成果，"
                    "请在你的回复前加上FINAL TRANSACTION PROPOSAL: **买入/持有/卖出**，以便团队知道停止。"
                    "你可以使用以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期是{current_date}。我们要查看的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # 部分填充提示模板
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        # 创建处理链
        chain = prompt | llm.bind_tools(tools)

        # 调用链并获取结果
        result = chain.invoke(state["messages"])

        # 初始化报告
        report = ""

        # 如果没有工具调用，直接使用内容作为报告
        if len(result.tool_calls) == 0:
            report = result.content
       
        # 返回结果和市场报告
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node