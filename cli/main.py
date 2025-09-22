from typing import Optional
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *

# 创建控制台实例，用于输出到终端
console = Console()

# 创建Typer应用实例，配置CLI应用的基本信息
app = typer.Typer(
    name="TradingAgents",  # 应用名称
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",  # 帮助信息
    add_completion=True,  # 启用shell补全功能
)


# 创建消息缓冲区类，用于存储和管理分析过程中的消息
class MessageBuffer:
    """消息缓冲区类，用于存储和管理分析过程中的消息"""
    
    def __init__(self, max_length=100):
        """初始化消息缓冲区
        
        Args:
            max_length (int): 缓冲区最大长度，默认100条消息
        """
        self.messages = deque(maxlen=max_length)  # 存储消息的双端队列
        self.tool_calls = deque(maxlen=max_length)  # 存储工具调用的双端队列
        self.current_report = None  # 当前报告内容
        self.final_report = None  # 完整的最终报告
        # 初始化各智能体状态
        self.agent_status = {
            # 分析师团队
            "Market Analyst": "pending",      # 市场分析师
            "Social Analyst": "pending",      # 社交情绪分析师
            "News Analyst": "pending",        # 新闻分析师
            "Fundamentals Analyst": "pending", # 基本面分析师
            # 研究团队
            "Bull Researcher": "pending",     # 看多研究员
            "Bear Researcher": "pending",     # 看空研究员
            "Research Manager": "pending",    # 研究经理
            # 交易团队
            "Trader": "pending",              # 交易员
            # 风险管理团队
            "Risky Analyst": "pending",       # 激进分析师
            "Neutral Analyst": "pending",     # 中性分析师
            "Safe Analyst": "pending",        # 保守分析师
            # 投资组合管理团队
            "Portfolio Manager": "pending",   # 投资组合经理
        }
        self.current_agent = None  # 当前正在执行的智能体
        # 报告各部分的内容
        self.report_sections = {
            "market_report": None,           # 市场分析报告
            "sentiment_report": None,        # 社交情绪报告
            "news_report": None,             # 新闻分析报告
            "fundamentals_report": None,     # 基本面分析报告
            "investment_plan": None,         # 投资计划
            "trader_investment_plan": None,  # 交易员投资计划
            "final_trade_decision": None,    # 最终交易决策
        }

    def add_message(self, message_type, content):
        """添加消息到缓冲区
        
        Args:
            message_type (str): 消息类型
            content (str): 消息内容
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")  # 获取当前时间戳
        self.messages.append((timestamp, message_type, content))  # 添加消息到队列

    def add_tool_call(self, tool_name, args):
        """添加工具调用到缓冲区
        
        Args:
            tool_name (str): 工具名称
            args (dict): 工具参数
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")  # 获取当前时间戳
        self.tool_calls.append((timestamp, tool_name, args))  # 添加工具调用到队列

    def update_agent_status(self, agent, status):
        """更新智能体状态
        
        Args:
            agent (str): 智能体名称
            status (str): 状态值
        """
        if agent in self.agent_status:
            self.agent_status[agent] = status  # 更新智能体状态
            self.current_agent = agent  # 设置当前智能体

    def update_report_section(self, section_name, content):
        """更新报告部分
        
        Args:
            section_name (str): 报告部分名称
            content (str): 报告内容
        """
        if section_name in self.report_sections:
            self.report_sections[section_name] = content  # 更新报告部分内容
            self._update_current_report()  # 更新当前报告

    def _update_current_report(self):
        """更新当前报告，只显示最近更新的部分"""
        # 查找最近更新的报告部分
        latest_section = None
        latest_content = None

        # 查找最近更新的部分
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # 格式化当前部分用于显示
            section_titles = {
                "market_report": "Market Analysis",           # 市场分析
                "sentiment_report": "Social Sentiment",       # 社交情绪
                "news_report": "News Analysis",               # 新闻分析
                "fundamentals_report": "Fundamentals Analysis", # 基本面分析
                "investment_plan": "Research Team Decision",   # 研究团队决策
                "trader_investment_plan": "Trading Team Plan", # 交易团队计划
                "final_trade_decision": "Portfolio Management Decision", # 投资组合管理决策
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # 更新完整的最终报告
        self._update_final_report()

    def _update_final_report(self):
        """更新完整的最终报告"""
        report_parts = []

        # 分析师团队报告
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Analyst Team Reports")  # 分析师团队报告
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### Social Sentiment\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Fundamentals Analysis\n{self.report_sections['fundamentals_report']}"
                )

        # 研究团队报告
        if self.report_sections["investment_plan"]:
            report_parts.append("## Research Team Decision")  # 研究团队决策
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # 交易团队报告
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## Trading Team Plan")  # 交易团队计划
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # 投资组合管理决策
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Portfolio Management Decision")  # 投资组合管理决策
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


# 创建全局消息缓冲区实例
message_buffer = MessageBuffer()


def create_layout():
    """创建布局结构
    
    Returns:
        Layout: 布局对象
    """
    layout = Layout()  # 创建布局实例
    # 将布局分为三列：头部、主体、底部
    layout.split_column(
        Layout(name="header", size=3),    # 头部区域，高度3行
        Layout(name="main"),              # 主体区域
        Layout(name="footer", size=3),    # 底部区域，高度3行
    )
    # 主体区域分为上下两部分
    layout["main"].split_column(
        Layout(name="upper", ratio=3),    # 上部区域，占比3
        Layout(name="analysis", ratio=5), # 分析区域，占比5
    )
    # 上部区域分为左右两部分
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), # 进度区域，占比2
        Layout(name="messages", ratio=3), # 消息区域，占比3
    )
    return layout


def update_display(layout, spinner_text=None):
    """更新显示界面
    
    Args:
        layout (Layout): 布局对象
        spinner_text (str, optional): 旋转加载文本
    """
    # 头部区域显示欢迎信息
    layout["header"].update(
        Panel(
            "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="Welcome to TradingAgents",  # 面板标题
            border_style="green",              # 边框样式
            padding=(1, 2),                    # 内边距
            expand=True,                       # 扩展填充
        )
    )

    # 进度面板显示智能体状态
    progress_table = Table(
        show_header=True,                      # 显示表头
        header_style="bold magenta",           # 表头样式
        show_footer=False,                     # 不显示表尾
        box=box.SIMPLE_HEAD,                   # 使用简单表头样式
        title=None,                            # 移除冗余的进度标题
        padding=(0, 2),                        # 添加水平内边距
        expand=True,                           # 表格扩展填充可用空间
    )
    # 添加表格列
    progress_table.add_column("Team", style="cyan", justify="center", width=20)      # 团队列
    progress_table.add_column("Agent", style="green", justify="center", width=20)    # 智能体列
    progress_table.add_column("Status", style="yellow", justify="center", width=20)  # 状态列

    # 按团队分组智能体
    teams = {
        "Analyst Team": [                     # 分析师团队
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],  # 研究团队
        "Trading Team": ["Trader"],                                                   # 交易团队
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],      # 风险管理团队
        "Portfolio Management": ["Portfolio Manager"],                                # 投资组合管理团队
    }

    # 为每个团队添加智能体状态
    for team, agents in teams.items():
        # 添加第一个智能体并显示团队名称
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            # 如果状态为进行中，显示旋转加载动画
            spinner = Spinner(
                "dots", text="[blue]in_progress[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            # 根据状态设置不同的颜色
            status_color = {
                "pending": "yellow",    # 等待状态为黄色
                "completed": "green",   # 完成状态为绿色
                "error": "red",         # 错误状态为红色
            }.get(status, "white")     # 默认状态为白色
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # 添加团队中的其他智能体
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                # 如果状态为进行中，显示旋转加载动画
                spinner = Spinner(
                    "dots", text="[blue]in_progress[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                # 根据状态设置不同的颜色
                status_color = {
                    "pending": "yellow",    # 等待状态为黄色
                    "completed": "green",   # 完成状态为绿色
                    "error": "red",         # 错误状态为红色
                }.get(status, "white")     # 默认状态为白色
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # 在每个团队后添加水平分隔线
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    # 更新进度面板
    layout["progress"].update(
        Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))
    )

    # 消息面板显示最近的消息和工具调用
    messages_table = Table(
        show_header=True,                      # 显示表头
        header_style="bold magenta",           # 表头样式
        show_footer=False,                     # 不显示表尾
        expand=True,                           # 表格扩展填充可用空间
        box=box.MINIMAL,                       # 使用最小化的边框样式
        show_lines=True,                       # 保持水平线
        padding=(0, 1),                        # 添加列间内边距
    )
    # 添加表格列
    messages_table.add_column("Time", style="cyan", width=8, justify="center")       # 时间列
    messages_table.add_column("Type", style="green", width=10, justify="center")     # 类型列
    messages_table.add_column(
        "Content", style="white", no_wrap=False, ratio=1
    )  # 内容列，可扩展

    # 合并工具调用和消息
    all_messages = []

    # 添加工具调用
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # 如果工具调用参数过长则截断
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "Tool", f"{tool_name}: {args}"))

    # 添加常规消息
    for timestamp, msg_type, content in message_buffer.messages:
        # 将内容转换为字符串
        content_str = content
        if isinstance(content, list):
            # 处理内容块列表（Anthropic格式）
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        # 如果消息内容过长则截断
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # 按时间戳排序
    all_messages.sort(key=lambda x: x[0])

    # 计算可显示的消息数量
    max_messages = 12  # 增加到12条以更好地填充空间

    # 获取最后N条可显示的消息
    recent_messages = all_messages[-max_messages:]

    # 添加消息到表格
    for timestamp, msg_type, content in recent_messages:
        # 格式化内容并添加自动换行
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    # 如果有旋转加载文本则添加
    if spinner_text:
        messages_table.add_row("", "Spinner", spinner_text)

    # 添加页脚显示消息截断信息
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Showing last {max_messages} of {len(all_messages)} messages[/dim]"
        )

    # 更新消息面板
    layout["messages"].update(
        Panel(
            messages_table,
            title="Messages & Tools",          # 面板标题
            border_style="blue",               # 边框样式
            padding=(1, 2),                    # 内边距
        )
    )

    # 分析面板显示当前报告
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),  # 使用Markdown格式显示报告
                title="Current Report",                   # 面板标题
                border_style="green",                     # 边框样式
                padding=(1, 2),                           # 内边距
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]Waiting for analysis report...[/italic]",  # 等待分析报告
                title="Current Report",                             # 面板标题
                border_style="green",                               # 边框样式
                padding=(1, 2),                                     # 内边距
            )
        )

    # 底部区域显示统计信息
    tool_calls_count = len(message_buffer.tool_calls)  # 工具调用次数
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )  # LLM调用次数
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )  # 生成的报告数量

    # 创建统计信息表格
    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        f"Tool Calls: {tool_calls_count} | LLM Calls: {llm_calls_count} | Generated Reports: {reports_count}"
    )

    # 更新底部面板
    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """获取用户选择项
    
    Returns:
        dict: 包含所有用户选择的字典
    """
    # 显示ASCII艺术欢迎信息
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # 创建欢迎框内容
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]Workflow Steps:[/bold]\n"
    welcome_content += "I. Analyst Team → II. Research Team → III. Trader → IV. Risk Management → V. Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # 创建并居中欢迎框
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="Welcome to TradingAgents",
        subtitle="Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()  # 在欢迎框后添加空行

    # 为每个步骤创建问题框
    def create_question_box(title, prompt, default=None):
        """创建问题框
        
        Args:
            title (str): 标题
            prompt (str): 提示信息
            default (str, optional): 默认值
            
        Returns:
            Panel: 问题面板
        """
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # 步骤1: 股票代码
    console.print(
        create_question_box(
            "Step 1: Ticker Symbol", "Enter the ticker symbol to analyze", "SPY"
        )
    )
    selected_ticker = get_ticker()

    # 步骤2: 分析日期
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Step 2: Analysis Date",
            "Enter the analysis date (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # 步骤3: 选择分析师
    console.print(
        create_question_box(
            "Step 3: Analysts Team", "Select your LLM analyst agents for the analysis"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]Selected analysts:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # 步骤4: 研究深度
    console.print(
        create_question_box(
            "Step 4: Research Depth", "Select your research depth level"
        )
    )
    selected_research_depth = select_research_depth()

    # 步骤5: OpenAI后端
    console.print(
        create_question_box(
            "Step 5: OpenAI backend", "Select which service to talk to"
        )
    )
    selected_llm_provider, backend_url = select_llm_provider()
    
    # 步骤6: 思考智能体
    console.print(
        create_question_box(
            "Step 6: Thinking Agents", "Select your thinking agents for analysis"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    # 返回所有用户选择
    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def get_ticker():
    """从用户输入获取股票代码
    
    Returns:
        str: 股票代码
    """
    return typer.prompt("", default="SPY")


def get_analysis_date():
    """从用户输入获取分析日期
    
    Returns:
        str: 分析日期字符串
    """
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # 验证日期格式并确保不是未来日期
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]Error: Analysis date cannot be in the future[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]Error: Invalid date format. Please use YYYY-MM-DD[/red]"
            )


def display_complete_report(final_state):
    """显示完整的分析报告，按团队分组显示面板
    
    Args:
        final_state (dict): 最终状态字典
    """
    console.print("\n[bold green]Complete Analysis Report[/bold green]\n")

    # I. 分析师团队报告
    analyst_reports = []

    # 市场分析师报告
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title="Market Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 社交情绪分析师报告
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title="Social Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 新闻分析师报告
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title="News Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 基本面分析师报告
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title="Fundamentals Analyst",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 如果有分析师报告则显示
    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. Analyst Team Reports",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. 研究团队报告
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # 看多研究员分析
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title="Bull Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 看空研究员分析
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title="Bear Researcher",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 研究经理决策
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="Research Manager",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 如果有研究报告则显示
        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title="II. Research Team Decision",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. 交易团队报告
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title="Trader",
                    border_style="blue",
                    padding=(1, 2),
                ),
                title="III. Trading Team Plan",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. 风险管理团队报告
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # 激进（风险）分析师分析
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title="Aggressive Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 保守（安全）分析师分析
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title="Conservative Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 中性分析师分析
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="Neutral Analyst",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 如果有风险报告则显示
        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title="IV. Risk Management Team Decision",
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. 投资组合经理决策
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title="Portfolio Manager",
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title="V. Portfolio Manager Decision",
                    border_style="green",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """更新研究团队和交易员的状态
    
    Args:
        status (str): 状态值
    """
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """从各种消息格式中提取字符串内容
    
    Args:
        content: 消息内容
        
    Returns:
        str: 提取的字符串内容
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # 处理Anthropic的列表格式
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def run_analysis():
    """运行分析流程"""
    # 首先获取所有用户选择
    selections = get_user_selections()

    # 使用选定的研究深度创建配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()

    # 初始化图计算
    graph = TradingAgentsGraph(
        [analyst.value for analyst in selections["analysts"]], config=config, debug=True
    )

    # 创建结果目录
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    def save_message_decorator(obj, func_name):
        """保存消息装饰器
        
        Args:
            obj: 对象
            func_name (str): 函数名称
            
        Returns:
            function: 装饰器函数
        """
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # 将换行符替换为空格
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        """保存工具调用装饰器
        
        Args:
            obj: 对象
            func_name (str): 函数名称
            
        Returns:
            function: 装饰器函数
        """
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        """保存报告部分装饰器
        
        Args:
            obj: 对象
            func_name (str): 函数名称
            
        Returns:
            function: 装饰器函数
        """
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)
        return wrapper

    # 应用装饰器到消息缓冲区方法
    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # 现在开始显示布局
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # 初始显示
        update_display(layout)

        # 添加初始消息
        message_buffer.add_message("System", f"Selected ticker: {selections['ticker']}")
        message_buffer.add_message(
            "System", f"Analysis date: {selections['analysis_date']}"
        )
        message_buffer.add_message(
            "System",
            f"Selected analysts: {', '.join(analyst.value for analyst in selections['analysts'])}",
        )
        update_display(layout)

        # 重置智能体状态
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "pending")

        # 重置报告部分
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None

        # 将第一个分析师状态更新为进行中
        first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout)

        # 创建旋转加载文本
        spinner_text = (
            f"Analyzing {selections['ticker']} on {selections['analysis_date']}..."
        )
        update_display(layout, spinner_text)

        # 初始化状态并获取图计算参数
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args()

        # 流式分析
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            if len(chunk["messages"]) > 0:
                # 获取块中的最后一条消息
                last_message = chunk["messages"][-1]

                # 提取消息内容和类型
                if hasattr(last_message, "content"):
                    content = extract_content_string(last_message.content)  # 使用辅助函数
                    msg_type = "Reasoning"
                else:
                    content = str(last_message)
                    msg_type = "System"

                # 将消息添加到缓冲区
                message_buffer.add_message(msg_type, content)                

                # 如果是工具调用，将其添加到工具调用列表
                if hasattr(last_message, "tool_calls"):
                    for tool_call in last_message.tool_calls:
                        # 处理字典和对象形式的工具调用
                        if isinstance(tool_call, dict):
                            message_buffer.add_tool_call(
                                tool_call["name"], tool_call["args"]
                            )
                        else:
                            message_buffer.add_tool_call(tool_call.name, tool_call.args)

                # 根据块内容更新报告和智能体状态
                # 分析师团队报告
                if "market_report" in chunk and chunk["market_report"]:
                    message_buffer.update_report_section(
                        "market_report", chunk["market_report"]
                    )
                    message_buffer.update_agent_status("Market Analyst", "completed")
                    # 将下一个分析师状态设置为进行中
                    if "social" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Social Analyst", "in_progress"
                        )

                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    message_buffer.update_report_section(
                        "sentiment_report", chunk["sentiment_report"]
                    )
                    message_buffer.update_agent_status("Social Analyst", "completed")
                    # 将下一个分析师状态设置为进行中
                    if "news" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "News Analyst", "in_progress"
                        )

                if "news_report" in chunk and chunk["news_report"]:
                    message_buffer.update_report_section(
                        "news_report", chunk["news_report"]
                    )
                    message_buffer.update_agent_status("News Analyst", "completed")
                    # 将下一个分析师状态设置为进行中
                    if "fundamentals" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Fundamentals Analyst", "in_progress"
                        )

                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    message_buffer.update_report_section(
                        "fundamentals_report", chunk["fundamentals_report"]
                    )
                    message_buffer.update_agent_status(
                        "Fundamentals Analyst", "completed"
                    )
                    # 将所有研究团队成员状态设置为进行中
                    update_research_team_status("in_progress")

                # 研究团队 - 处理投资辩论状态
                if (
                    "investment_debate_state" in chunk
                    and chunk["investment_debate_state"]
                ):
                    debate_state = chunk["investment_debate_state"]

                    # 更新看多研究员状态和报告
                    if "bull_history" in debate_state and debate_state["bull_history"]:
                        # 保持所有研究团队成员进行中状态
                        update_research_team_status("in_progress")
                        # 提取最新的看多响应
                        bull_responses = debate_state["bull_history"].split("\n")
                        latest_bull = bull_responses[-1] if bull_responses else ""
                        if latest_bull:
                            message_buffer.add_message("Reasoning", latest_bull)
                            # 更新研究报告中的看多最新分析
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"### Bull Researcher Analysis\n{latest_bull}",
                            )

                    # 更新看空研究员状态和报告
                    if "bear_history" in debate_state and debate_state["bear_history"]:
                        # 保持所有研究团队成员进行中状态
                        update_research_team_status("in_progress")
                        # 提取最新的看空响应
                        bear_responses = debate_state["bear_history"].split("\n")
                        latest_bear = bear_responses[-1] if bear_responses else ""
                        if latest_bear:
                            message_buffer.add_message("Reasoning", latest_bear)
                            # 更新研究报告中的看空最新分析
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"{message_buffer.report_sections['investment_plan']}\n\n### Bear Researcher Analysis\n{latest_bear}",
                            )

                    # 更新研究经理状态和最终决策
                    if (
                        "judge_decision" in debate_state
                        and debate_state["judge_decision"]
                    ):
                        # 保持所有研究团队成员进行中状态直到最终决策
                        update_research_team_status("in_progress")
                        message_buffer.add_message(
                            "Reasoning",
                            f"Research Manager: {debate_state['judge_decision']}",
                        )
                        # 更新研究报告中的最终决策
                        message_buffer.update_report_section(
                            "investment_plan",
                            f"{message_buffer.report_sections['investment_plan']}\n\n### Research Manager Decision\n{debate_state['judge_decision']}",
                        )
                        # 将所有研究团队成员标记为已完成
                        update_research_team_status("completed")
                        # 将第一个风险分析师状态设置为进行中
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )

                # 交易团队
                if (
                    "trader_investment_plan" in chunk
                    and chunk["trader_investment_plan"]
                ):
                    message_buffer.update_report_section(
                        "trader_investment_plan", chunk["trader_investment_plan"]
                    )
                    # 将第一个风险分析师状态设置为进行中
                    message_buffer.update_agent_status("Risky Analyst", "in_progress")

                # 风险管理团队 - 处理风险辩论状态
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]

                    # 更新风险分析师状态和报告
                    if (
                        "current_risky_response" in risk_state
                        and risk_state["current_risky_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Risky Analyst: {risk_state['current_risky_response']}",
                        )
                        # 仅更新风险报告中的风险分析师最新分析
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Risky Analyst Analysis\n{risk_state['current_risky_response']}",
                        )

                    # 更新安全分析师状态和报告
                    if (
                        "current_safe_response" in risk_state
                        and risk_state["current_safe_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Safe Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Safe Analyst: {risk_state['current_safe_response']}",
                        )
                        # 仅更新风险报告中的安全分析师最新分析
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Safe Analyst Analysis\n{risk_state['current_safe_response']}",
                        )

                    # 更新中性分析师状态和报告
                    if (
                        "current_neutral_response" in risk_state
                        and risk_state["current_neutral_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Neutral Analyst: {risk_state['current_neutral_response']}",
                        )
                        # 仅更新风险报告中的中性分析师最新分析
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Neutral Analyst Analysis\n{risk_state['current_neutral_response']}",
                        )

                    # 更新投资组合经理状态和最终决策
                    if "judge_decision" in risk_state and risk_state["judge_decision"]:
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "in_progress"
                        )
                        message_buffer.add_message(
                            "Reasoning",
                            f"Portfolio Manager: {risk_state['judge_decision']}",
                        )
                        # 仅更新风险报告中的最终决策
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Portfolio Manager Decision\n{risk_state['judge_decision']}",
                        )
                        # 将风险分析师标记为已完成
                        message_buffer.update_agent_status("Risky Analyst", "completed")
                        message_buffer.update_agent_status("Safe Analyst", "completed")
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "completed"
                        )

                # 更新显示
                update_display(layout)

            trace.append(chunk)

        # 获取最终状态和决策
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # 将所有智能体状态更新为已完成
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            "Analysis", f"Completed analysis for {selections['analysis_date']}"
        )

        # 更新最终报告部分
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        # 显示完整的最终报告
        display_complete_report(final_state)

        update_display(layout)


# 定义analyze命令
@app.command()
def analyze():
    """分析命令"""
    run_analysis()


# 程序入口点
if __name__ == "__main__":
    app()
