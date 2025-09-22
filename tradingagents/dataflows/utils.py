import os
import json
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Annotated

# 保存路径类型注解，用于指定数据保存的文件路径
SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]

def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    """保存数据到指定路径的CSV文件"""
    # 如果指定了保存路径，则将数据保存为CSV文件
    if save_path:
        data.to_csv(save_path)
        print(f"{tag} 已保存到 {save_path}")


def get_current_date():
    """获取当前日期，格式为YYYY-MM-DD"""
    return date.today().strftime("%Y-%m-%d")


def decorate_all_methods(decorator):
    """装饰器函数，用于将指定装饰器应用到类的所有方法上"""
    def class_decorator(cls):
        # 遍历类的所有属性
        for attr_name, attr_value in cls.__dict__.items():
            # 如果属性是可调用的（方法），则应用装饰器
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


def get_next_weekday(date):
    """获取下一个工作日的日期"""
    # 如果输入不是datetime对象，则转换为datetime对象
    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    # 如果是周末（周六或周日），计算到下一个周一的天数
    if date.weekday() >= 5:
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        # 如果是工作日，直接返回原日期
        return date