import os

# 默认配置字典，包含项目运行所需的各种配置参数
DEFAULT_CONFIG = {
    # 项目目录路径
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    # 结果存储目录，可通过环境变量TRADINGAGENTS_RESULTS_DIR设置，默认为"./results"
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    # 数据目录路径
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    # 数据缓存目录路径
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM设置
    # 默认LLM提供商
    "llm_provider": "openai",
    # 深度思考LLM模型
    "deep_think_llm": "o4-mini",
    # 快速思考LLM模型
    "quick_think_llm": "gpt-4o-mini",
    # 后端API URL
    "backend_url": "https://api.openai.com/v1",
    # 辩论和讨论设置
    # 最大辩论轮数
    "max_debate_rounds": 1,
    # 最大风险讨论轮数
    "max_risk_discuss_rounds": 1,
    # 最大递归限制
    "max_reduc_limit": 100,
    # 工具设置
    # 是否启用在线工具
    "online_tools": True,
}