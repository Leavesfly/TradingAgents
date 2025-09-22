import tradingagents.default_config as default_config
from typing import Dict, Optional

# 使用默认配置但允许被覆盖
# 配置字典，初始为None
_config: Optional[Dict] = None
# 数据目录路径，初始为None
DATA_DIR: Optional[str] = None


def initialize_config():
    """使用默认值初始化配置"""
    global _config, DATA_DIR
    # 如果配置尚未初始化，则使用默认配置进行初始化
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
        DATA_DIR = _config["data_dir"]


def set_config(config: Dict):
    """使用自定义值更新配置"""
    global _config, DATA_DIR
    # 如果配置尚未初始化，则先使用默认配置进行初始化
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    # 更新配置
    _config.update(config)
    # 更新数据目录路径
    DATA_DIR = _config["data_dir"]


def get_config() -> Dict:
    """获取当前配置"""
    # 如果配置尚未初始化，则先初始化
    if _config is None:
        initialize_config()
    # 返回配置的副本
    return _config.copy()


# 使用默认配置进行初始化
initialize_config()