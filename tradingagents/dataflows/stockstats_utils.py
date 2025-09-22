import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config


class StockstatsUtils:
    """股票统计工具类，用于获取股票技术指标"""
    
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "公司股票代码"],
        indicator: Annotated[
            str, "基于公司股票数据的量化指标"
        ],
        curr_date: Annotated[
            str, "获取股票价格数据的当前日期，格式YYYY-mm-dd"
        ],
        data_dir: Annotated[
            str,
            "存储股票数据的目录。",
        ],
        online: Annotated[
            bool,
            "是否使用在线工具获取数据。如果为True，将使用在线工具。",
        ] = False,
    ):
        """
        获取股票的技术指标值
        
        参数:
            symbol: 公司股票代码
            indicator: 技术指标名称
            curr_date: 当前日期
            data_dir: 数据目录路径
            online: 是否在线获取数据
            
        返回:
            指定日期的技术指标值
        """
        # 初始化数据框和数据变量
        df = None
        data = None

        # 如果不使用在线模式
        if not online:
            try:
                # 从本地文件读取数据
                data = pd.read_csv(
                    os.path.join(
                        data_dir,
                        f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                    )
                )
                # 使用stockstats包装数据
                df = wrap(data)
            except FileNotFoundError:
                # 如果文件未找到，抛出异常
                raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
        else:
            # 使用在线模式获取数据
            # 获取今天的日期作为YYYY-mm-dd格式用于缓存
            today_date = pd.Timestamp.today()
            curr_date = pd.to_datetime(curr_date)

            # 设置开始和结束日期
            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            # 获取配置并确保缓存目录存在
            config = get_config()
            os.makedirs(config["data_cache_dir"], exist_ok=True)

            # 构建数据文件路径
            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-YFin-data-{start_date}-{end_date}.csv",
            )

            # 如果数据文件存在，则从文件读取，否则从网络下载
            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
                data["Date"] = pd.to_datetime(data["Date"])
            else:
                # 从Yahoo Finance下载数据
                data = yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    multi_level_index=False,
                    progress=False,
                    auto_adjust=True,
                )
                # 重置索引并保存到CSV文件
                data = data.reset_index()
                data.to_csv(data_file, index=False)

            # 使用stockstats包装数据
            df = wrap(data)
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            curr_date = curr_date.strftime("%Y-%m-%d")

        # 触发stockstats计算指标
        df[indicator]
        # 查找匹配日期的行
        matching_rows = df[df["Date"].str.startswith(curr_date)]

        # 如果找到匹配行，返回指标值，否则返回提示信息
        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"