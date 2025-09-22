"""
TradingAgents包的安装脚本。
"""

from setuptools import setup, find_packages

setup(
    name="tradingagents",                            # 包名称
    version="0.1.0",                                 # 版本号
    description="Multi-Agents LLM Financial Trading Framework",  # 描述
    author="TradingAgents Team",                     # 作者
    author_email="yijia.xiao@cs.ucla.edu",          # 作者邮箱
    url="https://github.com/TauricResearch",        # 项目URL
    packages=find_packages(),                       # 自动查找包
    install_requires=[                              # 依赖包列表
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langchain-experimental>=0.0.40",
        "langgraph>=0.0.20",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "praw>=7.7.0",
        "stockstats>=0.5.4",
        "yfinance>=0.2.31",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "questionary>=2.0.1",
    ],
    python_requires=">=3.10",                       # Python版本要求
    entry_points={                                  # 入口点配置
        "console_scripts": [
            "tradingagents=cli.main:app",           # CLI命令行工具
        ],
    },
    classifiers=[                                   # 分类器
        "Development Status :: 3 - Alpha",          # 开发状态
        "Intended Audience :: Financial and Trading Industry",  # 目标受众
        "License :: OSI Approved :: Apache Software License",   # 许可证
        "Programming Language :: Python :: 3",      # 编程语言
        "Programming Language :: Python :: 3.10",   # Python版本
        "Topic :: Office/Business :: Financial :: Investment",  # 主题
    ],
)
