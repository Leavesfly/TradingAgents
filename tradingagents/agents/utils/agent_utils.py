from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage


def create_msg_delete():
    """创建消息删除函数"""
    def delete_messages(state):
        """清除消息并添加占位符以确保与Anthropic兼容"""
        messages = state["messages"]
        
        # 移除所有消息
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # 添加一个最小的占位符消息
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class Toolkit:
    """工具包类，提供各种金融数据获取工具"""
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """更新类级别的配置"""
        cls._config.update(config)

    @property
    def config(self):
        """访问配置"""
        return self._config

    def __init__(self, config=None):
        """初始化工具包"""
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_reddit_news(
        curr_date: Annotated[str, "您想要获取新闻的日期，格式为 yyyy-mm-dd"],
    ) -> str:
        """
        在指定时间范围内从Reddit获取全球新闻
        
        参数:
            curr_date (str): 您想要获取新闻的日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含指定时间范围内最新全球新闻的格式化数据框
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "公司的搜索查询，例如 'AAPL, TSM, 等'",
        ],
        start_date: Annotated[str, "开始日期，格式为 yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为 yyyy-mm-dd"],
    ):
        """
        在日期范围内从Finnhub获取给定股票的最新新闻
        
        参数:
            ticker (str): 公司的股票代码，例如 AAPL, TSM
            start_date (str): 开始日期，格式为 yyyy-mm-dd
            end_date (str): 结束日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含公司在start_date到end_date日期范围内新闻的格式化数据框
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "公司的股票代码，例如 AAPL, TSM",
        ],
        curr_date: Annotated[str, "您想要获取新闻的当前日期"],
    ) -> str:
        """
        根据当前日期从Reddit获取给定股票的最新新闻
        
        参数:
            ticker (str): 公司的股票代码，例如 AAPL, TSM
            curr_date (str): 获取新闻的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含给定日期公司最新新闻的格式化数据框
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    def get_YFin_data(
        symbol: Annotated[str, "公司的股票代码"],
        start_date: Annotated[str, "开始日期，格式为 yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为 yyyy-mm-dd"],
    ) -> str:
        """
        从Yahoo Finance获取给定股票代码的股价数据
        
        参数:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            start_date (str): 开始日期，格式为 yyyy-mm-dd
            end_date (str): 结束日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含指定股票代码在指定日期范围内股价数据的格式化数据框
        """

        result_data = interface.get_YFin_data(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_YFin_data_online(
        symbol: Annotated[str, "公司的股票代码"],
        start_date: Annotated[str, "开始日期，格式为 yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为 yyyy-mm-dd"],
    ) -> str:
        """
        从Yahoo Finance获取给定股票代码的股价数据
        
        参数:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            start_date (str): 开始日期，格式为 yyyy-mm-dd
            end_date (str): 结束日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含指定股票代码在指定日期范围内股价数据的格式化数据框
        """

        result_data = interface.get_YFin_data_online(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "公司的股票代码"],
        indicator: Annotated[
            str, "要获取分析和报告的技术指标"
        ],
        curr_date: Annotated[
            str, "您交易的当前日期，格式为 YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "回 look back 的天数"] = 30,
    ) -> str:
        """
        获取给定股票代码和技术指标的股票统计数据
        
        参数:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            indicator (str): 要获取分析和报告的技术指标
            curr_date (str): 您交易的当前日期，格式为 YYYY-mm-dd
            look_back_days (int): 回 look back 的天数，默认为30
            
        返回:
            str: 包含指定股票代码和技术指标的股票统计数据的格式化数据框
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "公司的股票代码"],
        indicator: Annotated[
            str, "要获取分析和报告的技术指标"
        ],
        curr_date: Annotated[
            str, "您交易的当前日期，格式为 YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "回 look back 的天数"] = 30,
    ) -> str:
        """
        获取给定股票代码和技术指标的股票统计数据
        
        参数:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            indicator (str): 要获取分析和报告的技术指标
            curr_date (str): 您交易的当前日期，格式为 YYYY-mm-dd
            look_back_days (int): 回 look back 的天数，默认为30
            
        返回:
            str: 包含指定股票代码和技术指标的股票统计数据的格式化数据框
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[
            str,
            "您交易的当前日期，格式为 yyyy-mm-dd",
        ],
    ):
        """
        获取公司内部人士情绪信息（从公开的SEC信息中获取）过去30天的数据
        
        参数:
            ticker (str): 公司的股票代码
            curr_date (str): 您交易的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含从curr_date开始过去30天情绪的报告
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "股票代码"],
        curr_date: Annotated[
            str,
            "您交易的当前日期，格式为 yyyy-mm-dd",
        ],
    ):
        """
        获取公司内部人士交易信息（从公开的SEC信息中获取）过去30天的数据
        
        参数:
            ticker (str): 公司的股票代码
            curr_date (str): 您交易的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含公司过去30天内部人士交易/交易信息的报告
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您交易的当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        获取公司的最新资产负债表
        
        参数:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度 / 季度
            curr_date (str): 您交易的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含公司最新资产负债表的报告
        """

        data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)

        return data_balance_sheet

    @staticmethod
    @tool
    def get_simfin_cashflow(
        ticker: Annotated[str, "股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您交易的当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        获取公司的最新现金流量表
        
        参数:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度 / 季度
            curr_date (str): 您交易的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含公司最新现金流量表的报告
        """

        data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)

        return data_cashflow

    @staticmethod
    @tool
    def get_simfin_income_stmt(
        ticker: Annotated[str, "股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您交易的当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        获取公司的最新损益表
        
        参数:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度 / 季度
            curr_date (str): 您交易的当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含公司最新损益表的报告
        """

        data_income_stmt = interface.get_simfin_income_statements(
            ticker, freq, curr_date
        )

        return data_income_stmt

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "要搜索的查询"],
        curr_date: Annotated[str, "当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        根据查询和日期范围从Google新闻获取最新新闻
        
        参数:
            query (str): 要搜索的查询
            curr_date (str): 当前日期，格式为 yyyy-mm-dd
            look_back_days (int): 回 look back 的天数
            
        返回:
            str: 包含基于查询和日期范围的最新Google新闻的格式化字符串
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    def get_stock_news_openai(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[str, "当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        使用OpenAI的新闻API获取给定股票的最新新闻
        
        参数:
            ticker (str): 公司的股票代码，例如 AAPL, TSM
            curr_date (str): 当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含给定日期公司最新新闻的格式化字符串
        """

        openai_news_results = interface.get_stock_news_openai(ticker, curr_date)

        return openai_news_results

    @staticmethod
    @tool
    def get_global_news_openai(
        curr_date: Annotated[str, "当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        使用OpenAI的宏观经济新闻API获取给定日期的最新宏观经济新闻
        
        参数:
            curr_date (str): 当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含给定日期最新宏观经济新闻的格式化字符串
        """

        openai_news_results = interface.get_global_news_openai(curr_date)

        return openai_news_results

    @staticmethod
    @tool
    def get_fundamentals_openai(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[str, "当前日期，格式为 yyyy-mm-dd"],
    ):
        """
        使用OpenAI的新闻API获取给定日期给定股票的最新基本面信息
        
        参数:
            ticker (str): 公司的股票代码，例如 AAPL, TSM
            curr_date (str): 当前日期，格式为 yyyy-mm-dd
            
        返回:
            str: 包含给定日期公司最新基本面信息的格式化字符串
        """

        openai_fundamentals_results = interface.get_fundamentals_openai(
            ticker, curr_date
        )

        return openai_fundamentals_results