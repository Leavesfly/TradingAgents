import json
import os


def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):
    """
    获取保存在磁盘上并已处理的Finnhub数据。
    
    参数:
        start_date (str): 开始日期，格式为 YYYY-MM-DD。
        end_date (str): 结束日期，格式为 YYYY-MM-DD。
        data_type (str): 要获取的Finnhub数据类型。可以是 insider_trans, SEC_filings, news_data, insider_senti, 或 fin_as_reported。
        data_dir (str): 数据保存的目录。
        period (str): 默认为None，如果指定了周期，应为 annual 或 quarterly。
        
    返回:
        在指定日期范围内的过滤数据
    """

    # 根据是否指定周期构建数据路径
    if period:
        data_path = os.path.join(
            data_dir,
            "finnhub_data",
            data_type,
            f"{ticker}_{period}_data_formatted.json",
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    # 打开并加载JSON数据
    data = open(data_path, "r")
    data = json.load(data)

    # 根据日期范围过滤键（日期，格式为 YYYY-MM-DD 的字符串）
    filtered_data = {}
    for key, value in data.items():
        # 如果键在指定日期范围内且值不为空，则添加到过滤后的数据中
        if start_date <= key <= end_date and len(value) > 0:
            filtered_data[key] = value
    return filtered_data