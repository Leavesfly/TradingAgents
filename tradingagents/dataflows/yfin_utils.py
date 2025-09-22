# 获取数据/统计信息的工具模块

import yfinance as yf
from typing import Annotated, Callable, Any, Optional
from pandas import DataFrame
import pandas as pd
from functools import wraps

from .utils import save_output, SavePathType, decorate_all_methods


def init_ticker(func: Callable) -> Callable:
    """装饰器，用于初始化yf.Ticker并将其传递给函数。"""

    @wraps(func)
    def wrapper(symbol: Annotated[str, "ticker symbol"], *args, **kwargs) -> Any:
        # 创建yfinance Ticker对象
        ticker = yf.Ticker(symbol)
        # 调用被装饰的函数并返回结果
        return func(ticker, *args, **kwargs)

    return wrapper


@decorate_all_methods(init_ticker)
class YFinanceUtils:
    """YFinance工具类，提供获取股票数据和公司信息的方法"""

    def get_stock_data(
        symbol: Annotated[str, "ticker symbol"],
        start_date: Annotated[
            str, "start date for retrieving stock price data, YYYY-mm-dd"
        ],
        end_date: Annotated[
            str, "end date for retrieving stock price data, YYYY-mm-dd"
        ],
        save_path: SavePathType = None,
    ) -> DataFrame:
        """获取指定股票代码的股价数据"""
        ticker = symbol
        # 为确保数据范围包含结束日期，将结束日期加一天
        end_date = pd.to_datetime(end_date) + pd.DateOffset(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        # 使用yfinance获取历史股价数据
        stock_data = ticker.history(start=start_date, end=end_date)
        # save_output(stock_data, f"Stock data for {ticker.ticker}", save_path)
        return stock_data

    def get_stock_info(
        symbol: Annotated[str, "ticker symbol"],
    ) -> dict:
        """获取并返回最新的股票信息"""
        ticker = symbol
        # 获取股票信息字典
        stock_info = ticker.info
        return stock_info

    def get_company_info(
        symbol: Annotated[str, "ticker symbol"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """获取并以DataFrame形式返回公司信息"""
        ticker = symbol
        # 获取公司基本信息
        info = ticker.info
        # 提取关键公司信息字段
        company_info = {
            "公司名称": info.get("shortName", "N/A"),
            "行业": info.get("industry", "N/A"),
            "板块": info.get("sector", "N/A"),
            "国家": info.get("country", "N/A"),
            "网站": info.get("website", "N/A"),
        }
        # 将公司信息转换为DataFrame
        company_info_df = DataFrame([company_info])
        # 如果指定了保存路径，则保存到CSV文件
        if save_path:
            company_info_df.to_csv(save_path)
            print(f"公司信息 {ticker.ticker} 已保存到 {save_path}")
        return company_info_df

    def get_stock_dividends(
        symbol: Annotated[str, "ticker symbol"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """获取并以DataFrame形式返回最新的分红数据"""
        ticker = symbol
        # 获取分红数据
        dividends = ticker.dividends
        # 如果指定了保存路径，则保存到CSV文件
        if save_path:
            dividends.to_csv(save_path)
            print(f"分红数据 {ticker.ticker} 已保存到 {save_path}")
        return dividends

    def get_income_stmt(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """获取并以DataFrame形式返回公司的最新损益表"""
        ticker = symbol
        # 获取损益表数据
        income_stmt = ticker.financials
        return income_stmt

    def get_balance_sheet(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """获取并以DataFrame形式返回公司的最新资产负债表"""
        ticker = symbol
        # 获取资产负债表数据
        balance_sheet = ticker.balance_sheet
        return balance_sheet

    def get_cash_flow(symbol: Annotated[str, "ticker symbol"]) -> DataFrame:
        """获取并以DataFrame形式返回公司的最新现金流量表"""
        ticker = symbol
        # 获取现金流量表数据
        cash_flow = ticker.cashflow
        return cash_flow

    def get_analyst_recommendations(symbol: Annotated[str, "ticker symbol"]) -> tuple:
        """获取最新的分析师评级，并返回最常见的评级及其计数"""
        ticker = symbol
        # 获取分析师评级数据
        recommendations = ticker.recommendations
        # 如果没有评级数据，返回空值
        if recommendations.empty:
            return None, 0  # 没有可用的评级数据

        # 假设存在'period'列需要排除，获取第一行数据（排除period列）
        row_0 = recommendations.iloc[0, 1:]  # 如有必要，排除'period'列

        # 查找最大投票结果
        max_votes = row_0.max()
        majority_voting_result = row_0[row_0 == max_votes].index.tolist()

        # 返回最常见的评级结果和票数
        return majority_voting_result[0], max_votes