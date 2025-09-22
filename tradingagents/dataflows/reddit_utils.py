import requests
import time
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Annotated, Optional
import os
import re

# 股票代码到公司名称的映射字典
ticker_to_company = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    "TSM": "Taiwan Semiconductor Manufacturing Company OR TSMC",
    "JPM": "JPMorgan Chase OR JP Morgan",
    "JNJ": "Johnson & Johnson OR JNJ",
    "V": "Visa",
    "WMT": "Walmart",
    "META": "Meta OR Facebook",
    "AMD": "AMD",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "BABA": "Alibaba",
    "ADBE": "Adobe",
    "NFLX": "Netflix",
    "CRM": "Salesforce",
    "PYPL": "PayPal",
    "PLTR": "Palantir",
    "MU": "Micron",
    "SQ": "Block OR Square",
    "ZM": "Zoom",
    "CSCO": "Cisco",
    "SHOP": "Shopify",
    "ORCL": "Oracle",
    "X": "Twitter OR X",
    "SPOT": "Spotify",
    "AVGO": "Broadcom",
    "ASML": "ASML ",
    "TWLO": "Twilio",
    "SNAP": "Snap Inc.",
    "TEAM": "Atlassian",
    "SQSP": "Squarespace",
    "UBER": "Uber",
    "ROKU": "Roku",
    "PINS": "Pinterest",
}


def fetch_top_from_category(
    category: Annotated[
        str, "要获取热门帖子的类别。子版块的集合。"
    ],
    date: Annotated[str, "要获取热门帖子的日期。"],
    max_limit: Annotated[int, "要获取的最大帖子数。"],
    query: Annotated[Optional[str], "要在子版块中搜索的可选查询。"] = None,
    data_path: Annotated[
        str,
        "数据文件夹的路径。默认为'reddit_data'。",
    ] = "reddit_data",
):
    """
    从指定类别中获取热门Reddit帖子
    
    参数:
        category: 要获取热门帖子的类别
        date: 要获取热门帖子的日期
        max_limit: 要获取的最大帖子数
        query: 要在子版块中搜索的可选查询
        data_path: 数据文件夹的路径
    
    返回:
        包含热门帖子的列表
    """
    # 基础路径
    base_path = data_path

    # 存储所有内容的列表
    all_content = []

    # 检查最大限制是否小于类别中的文件数
    if max_limit < len(os.listdir(os.path.join(base_path, category))):
        raise ValueError(
            "REDDIT FETCHING ERROR: max limit is less than the number of files in the category. Will not be able to fetch any posts"
        )

    # 计算每个子版块的限制
    limit_per_subreddit = max_limit // len(
        os.listdir(os.path.join(base_path, category))
    )

    # 遍历类别中的每个数据文件
    for data_file in os.listdir(os.path.join(base_path, category)):
        # 检查data_file是否为.jsonl文件
        if not data_file.endswith(".jsonl"):
            continue

        # 存储当前子版块所有内容的列表
        all_content_curr_subreddit = []

        # 打开并读取数据文件
        with open(os.path.join(base_path, category, data_file), "rb") as f:
            for i, line in enumerate(f):
                # 跳过空行
                if not line.strip():
                    continue

                # 解析行数据
                parsed_line = json.loads(line)

                # 选择指定日期的行
                post_date = datetime.utcfromtimestamp(
                    parsed_line["created_utc"]
                ).strftime("%Y-%m-%d")
                if post_date != date:
                    continue

                # 如果是公司新闻，检查标题或内容是否提到了公司名称(query)
                if "company" in category and query:
                    search_terms = []
                    # 如果公司名称包含OR，则分割为多个搜索词
                    if "OR" in ticker_to_company[query]:
                        search_terms = ticker_to_company[query].split(" OR ")
                    else:
                        search_terms = [ticker_to_company[query]]

                    # 添加股票代码作为搜索词
                    search_terms.append(query)

                    # 检查是否找到匹配项
                    found = False
                    for term in search_terms:
                        # 在标题或内容中搜索术语
                        if re.search(
                            term, parsed_line["title"], re.IGNORECASE
                        ) or re.search(term, parsed_line["selftext"], re.IGNORECASE):
                            found = True
                            break

                    if not found:
                        continue

                # 创建帖子对象
                post = {
                    "title": parsed_line["title"],
                    "content": parsed_line["selftext"],
                    "url": parsed_line["url"],
                    "upvotes": parsed_line["ups"],
                    "posted_date": post_date,
                }

                # 添加到当前子版块的内容列表
                all_content_curr_subreddit.append(post)

        # 按点赞数降序排序
        all_content_curr_subreddit.sort(key=lambda x: x["upvotes"], reverse=True)

        # 扩展所有内容列表，限制每个子版块的数量
        all_content.extend(all_content_curr_subreddit[:limit_per_subreddit])

    return all_content