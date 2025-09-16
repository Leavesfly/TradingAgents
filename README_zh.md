<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="README.md">English</a>
</div>

---

# TradingAgents: 多智能体大语言模型金融交易框架

> 🎉 **TradingAgents** 正式发布！我们收到了众多关于该项目的询问，在此感谢社区的热情关注。
>
> 因此，我们决定完全开源这个框架。期待与您一起构建有影响力的项目！

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents 框架](#tradingagents-框架) | ⚡ [安装与CLI](#安装与cli) | 🎬 [演示视频](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Python API使用](#tradingagents-包) | 🤝 [贡献指南](#贡献指南) | 📄 [引用](#引用)

</div>

## TradingAgents 框架

TradingAgents 是一个多智能体交易框架，模拟真实交易公司的运作动态。通过部署由大语言模型驱动的专业智能体——从基本面分析师、情绪专家、技术分析师到交易员、风险管理团队，该平台协同评估市场状况并制定交易决策。此外，这些智能体通过动态讨论来确定最优策略。

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents 框架专为研究目的设计。交易性能可能受多种因素影响，包括所选的基础语言模型、模型温度、交易周期、数据质量等非确定性因素。[这不构成任何金融、投资或交易建议。](https://tauric.ai/disclaimer/)

我们的框架将复杂的交易任务分解为专业化角色。这确保了系统实现稳健、可扩展的市场分析和决策方法。

### 分析师团队
- **基本面分析师**：评估公司财务和业绩指标，识别内在价值和潜在风险信号。
- **情绪分析师**：使用情绪评分算法分析社交媒体和公众情绪，判断短期市场情绪。
- **新闻分析师**：监控全球新闻和宏观经济指标，解读事件对市场状况的影响。
- **技术分析师**：利用技术指标（如MACD和RSI）检测交易模式并预测价格走势。

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### 研究员团队
- 由看多和看空研究员组成，他们批判性地评估分析师团队提供的见解。通过结构化辩论，他们平衡潜在收益与固有风险。

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 交易员智能体
- 整合分析师和研究员的报告做出明智的交易决策。基于全面的市场洞察确定交易时机和规模。

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 风险管理与投资组合经理
- 通过评估市场波动性、流动性和其他风险因素持续评估投资组合风险。风险管理团队评估并调整交易策略，向投资组合经理提供评估报告以做出最终决策。
- 投资组合经理批准/拒绝交易提案。如果批准，订单将发送到模拟交易所执行。

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## 安装与CLI

### 安装

克隆 TradingAgents：
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

在您喜欢的环境管理器中创建虚拟环境：
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

安装依赖：
```bash
pip install -r requirements.txt
```

### 必需的API

您需要 FinnHub API 来获取金融数据。我们所有的代码都基于免费层实现。
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

您需要 OpenAI API 为所有智能体提供服务。
```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

### CLI 使用

您可以通过运行以下命令直接试用CLI：
```bash
python -m cli.main
```
您将看到一个界面，可以在其中选择所需的股票代码、日期、LLM、研究深度等。

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

将出现一个界面显示加载结果，让您跟踪智能体运行时的进度。

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

## TradingAgents 包

### 实现细节

我们使用 LangGraph 构建 TradingAgents，以确保灵活性和模块化。我们在实验中使用 `o1-preview` 和 `gpt-4o` 作为深度思考和快速思考的LLM。但是，为了测试目的，我们推荐您使用 `gpt-4o-mini` 和 `gpt-4-turbo` 来节省成本，因为我们的框架会进行**大量**API调用。

### Python 使用

要在您的代码中使用 TradingAgents，您可以导入 `tradingagents` 模块并初始化 `TradingAgentsGraph()` 对象。`.propagate()` 函数将返回一个决策。您可以运行 `main.py`，这里也有一个快速示例：

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 前向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

您也可以调整默认配置来设置您自己选择的LLM、辩论轮次等。

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建自定义配置
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # 使用不同的模型
config["quick_think_llm"] = "gpt-4o-mini"  # 使用不同的模型
config["max_debate_rounds"] = 1  # 增加辩论轮次
config["online_tools"] = True # 使用在线工具或缓存数据

# 使用自定义配置初始化
ta = TradingAgentsGraph(debug=True, config=config)

# 前向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> 对于 `online_tools`，我们建议在实验中启用它们，因为它们提供对实时数据的访问。智能体的离线工具依赖于我们 **Tauric TradingDB** 的缓存数据，这是我们用于回测的精选数据集。我们目前正在完善这个数据集，计划很快与我们即将推出的项目一起发布。敬请期待！

您可以在 `tradingagents/default_config.py` 中查看完整的配置列表。

## 贡献指南

我们欢迎社区的贡献！无论是修复错误、改进文档还是建议新功能，您的输入都有助于改善这个项目。如果您对这一研究领域感兴趣，请考虑加入我们的开源金融AI研究社区 [Tauric Research](https://tauric.ai/)。

## 引用

如果 *TradingAgents* 对您有所帮助，请引用我们的工作 :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```