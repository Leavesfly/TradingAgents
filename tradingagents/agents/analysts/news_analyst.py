from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    """创建新闻分析师节点函数
    
    参数:
        llm: 语言模型
        toolkit: 工具包，包含各种数据获取工具
        
    返回:
        新闻分析师节点函数
    """
    def news_analyst_node(state):
        """新闻分析师节点，用于分析最近的新闻和趋势"""
        # 获取当前日期和公司信息
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # 根据配置选择工具
        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        # 系统消息，指导分析师如何分析新闻
        system_message = (
            "你是一名新闻研究员，任务是分析过去一周的最新新闻和趋势。请撰写一份全面的报告，"
            "涵盖与交易和宏观经济相关的当前世界状况。查看来自EODHD和Finnhub的新闻以确保全面性。"
            "不要简单地说明趋势是混合的，要提供详细和细粒度的分析和见解，帮助交易员做出决策。"
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

        # 返回结果和新闻报告
        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node