import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """检查响应是否表示速率限制（状态码429）"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """使用重试逻辑进行请求，处理速率限制"""
    # 每次请求前随机延迟以避免被检测
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    为给定查询和日期范围抓取Google新闻搜索结果。
    
    参数:
        query: str - 搜索查询
        start_date: str - 开始日期，格式为 yyyy-mm-dd 或 mm/dd/yyyy
        end_date: str - 结束日期，格式为 yyyy-mm-dd 或 mm/dd/yyyy
    
    返回:
        包含新闻结果的列表
    """
    # 将日期格式转换为mm/dd/yyyy
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    # 设置请求头以模拟浏览器访问
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }

    # 存储新闻结果的列表
    news_results = []
    page = 0
    
    # 循环获取所有页面的结果
    while True:
        # 计算偏移量用于分页
        offset = page * 10
        # 构建Google新闻搜索URL
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            # 发起请求并解析响应
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            # 选择新闻结果元素
            results_on_page = soup.select("div.SoaBEf")

            # 如果没有更多结果，则退出循环
            if not results_on_page:
                break  # 未找到更多结果

            # 处理当前页面的每个结果
            for el in results_on_page:
                try:
                    # 提取链接、标题、摘要、日期和来源
                    link = el.find("a")["href"]
                    title = el.select_one("div.MBeuO").get_text()
                    snippet = el.select_one(".GI74Re").get_text()
                    date = el.select_one(".LfVVr").get_text()
                    source = el.select_one(".NUnG9d span").get_text()
                    
                    # 将结果添加到列表中
                    news_results.append(
                        {
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "date": date,
                            "source": source,
                        }
                    )
                except Exception as e:
                    print(f"处理结果时出错: {e}")
                    # 如果找不到某个字段，则跳过此结果
                    continue

            # 检查"下一页"链接（分页）
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"多次重试后失败: {e}")
            break

    return news_results