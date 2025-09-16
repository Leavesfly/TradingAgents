# API参考

<cite>
**本文档中引用的文件**  
- [trading_graph.py](file://tradingagents/graph/trading_graph.py)
- [default_config.py](file://tradingagents/default_config.py)
- [propagation.py](file://tradingagents/graph/propagation.py)
- [reflection.py](file://tradingagents/graph/reflection.py)
- [signal_processing.py](file://tradingagents/graph/signal_processing.py)
- [memory.py](file://tradingagents/agents/utils/memory.py)
</cite>

## 目录
1. [构造函数](#构造函数)
2. [propagate方法](#propagate方法)
3. [reflect_and_remember方法](#reflect_and_remember方法)
4. [公共方法调用示例](#公共方法调用示例)
5. [生命周期管理与线程安全](#生命周期管理与线程安全)

## 构造函数

`TradingAgentsGraph`类的构造函数用于初始化交易代理图及其相关组件，支持自定义配置、调试模式和分析员选择。

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `selected_analysts` | List[str] | `["market", "social", "news", "fundamentals"]` | 指定要包含的分析员类型列表。可选值包括`market`（市场）、`social`（社交媒体）、`news`（新闻）和`fundamentals`（基本面）。这些分析员将参与决策流程。 |
| `debug` | bool | `False` | 是否启用调试模式。启用后，系统将输出详细的执行追踪信息，便于调试和分析流程。 |
| `config` | Dict[str, Any] | `None` | 自定义配置字典。若未提供，则使用`default_config.py`中定义的默认配置。配置项包括LLM提供商、模型名称、递归限制等。 |

### 配置项说明（config）

当`config`参数为`None`时，系统将加载`DEFAULT_CONFIG`作为默认配置。主要配置项如下：

- `"llm_provider"`: LLM服务提供商，支持`openai`、`anthropic`、`google`等。
- `"deep_think_llm"` 和 `"quick_think_llm"`: 分别用于深度思考和快速思考的模型名称。
- `"backend_url"`: LLM服务的API地址。
- `"max_debate_rounds"`: 投资辩论最大轮数。
- `"max_risk_discuss_rounds"`: 风险讨论最大轮数。
- `"max_recur_limit"`: 图执行的最大递归深度限制。

**Section sources**
- [trading_graph.py](file://tradingagents/graph/trading_graph.py#L31-L60)
- [default_config.py](file://tradingagents/default_config.py#L1-L22)

## propagate方法

该方法用于在指定日期对特定公司运行交易代理图，生成最终的投资决策。

### 输入参数

| 参数 | 类型 | 格式要求 | 说明 |
|------|------|----------|------|
| `company_name` | str | 有效的股票代码或公司名称（如`AAPL`、`Tesla`） | 指定要分析的目标公司。该名称将作为初始状态输入传递给图流程。 |
| `trade_date` | str 或 date | ISO日期格式（如`"2024-01-15"`）或`datetime.date`对象 | 指定分析的交易日期。该日期将记录在状态中并用于数据检索。 |

### 返回值结构

该方法返回一个元组，包含两个元素：

1. **完整状态对象**（`final_state`）：一个字典，包含整个决策流程的详细信息，字段包括：
   - `"company_of_interest"`: 目标公司名称
   - `"trade_date"`: 交易日期
   - `"market_report"`: 市场技术分析报告
   - `"sentiment_report"`: 情绪分析报告
   - `"news_report"`: 新闻摘要报告
   - `"fundamentals_report"`: 基本面分析报告
   - `"investment_debate_state"`: 投资辩论状态（含多头、空头、裁判决策）
   - `"risk_debate_state"`: 风险辩论状态
   - `"investment_plan"`: 投资计划
   - `"final_trade_decision"`: 最终交易决策文本

2. **处理后的信号**（`processed_signal`）：由`SignalProcessor`提取的简化决策，仅包含`BUY`、`SELL`或`HOLD`三种之一。

### 可能抛出的异常

- `ValueError`: 当配置中的`llm_provider`不被支持时抛出（如拼写错误或未实现的提供商）。
- `ConnectionError` 或 `TimeoutError`: 在调用外部工具（如Finnhub、Yahoo Finance）时网络异常。
- `KeyError`: 当配置字典缺少必要字段时（如`"deep_think_llm"`）。
- `json.JSONDecodeError`: 在日志写入过程中JSON序列化失败。

**Section sources**
- [trading_graph.py](file://tradingagents/graph/trading_graph.py#L131-L170)
- [propagation.py](file://tradingagents/graph/propagation.py#L10-L49)
- [signal_processing.py](file://tradingagents/graph/signal_processing.py#L10-L31)

## reflect_and_remember方法

该方法用于在交易结果产生后进行反思，并将经验存储到各代理的记忆系统中，以实现持续学习。

### 使用场景

通常在执行`propagate`方法并获得实际交易回报后调用。通过分析历史决策与实际收益/亏损的对比，系统能够识别成功或失败的原因，并更新记忆库，从而在未来的决策中避免重复错误或强化有效策略。

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `returns_losses` | float 或 str | 表示该次交易的实际收益或亏损（如`0.05`表示5%收益）。也可为描述性字符串（如`"profit of 3%"`），系统将自动解析。该值作为反思的依据，影响反思内容的生成方向。 |

### 内部机制

该方法通过`Reflector`组件对以下五个关键角色进行反思：
- 多头研究员（Bull Researcher）
- 空头研究员（Bear Researcher）
- 交易员（Trader）
- 投资裁判（Invest Judge）
- 风险经理（Risk Manager）

每个角色的分析历史和最终决策将与实际收益结合，生成反思文本，并通过`FinancialSituationMemory`类存储到向量数据库中，供未来相似市场情境检索使用。

**Section sources**
- [trading_graph.py](file://tradingagents/graph/trading_graph.py#L231-L253)
- [reflection.py](file://tradingagents/graph/reflection.py#L10-L121)
- [memory.py](file://tradingagents/agents/utils/memory.py#L1-L113)

## 公共方法调用示例

### 构造函数使用示例

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 使用默认配置和所有分析员
graph = TradingAgentsGraph(debug=True)

# 使用自定义配置
custom_config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4-turbo",
    "quick_think_llm": "gpt-3.5-turbo",
    "max_debate_rounds": 2,
}
graph = TradingAgentsGraph(
    selected_analysts=["market", "news"],
    debug=False,
    config=custom_config
)
```

### propagate方法调用示例

```python
# 运行分析流程
final_state, decision = graph.propagate("AAPL", "2024-01-15")
print(f"最终决策: {decision}")  # 输出: BUY / SELL / HOLD
```

### reflect_and_remember方法调用示例

```python
# 在交易周期结束后调用
graph.reflect_and_remember(returns_losses=0.03)  # 3% 收益
```

**执行时机说明**：
- `__init__`: 在应用启动时初始化一次。
- `propagate`: 每个交易日对目标股票调用一次。
- `reflect_and_remember`: 在持仓周期结束并计算出实际收益后调用。

**Section sources**
- [trading_graph.py](file://tradingagents/graph/trading_graph.py#L31-L253)

## 生命周期管理与线程安全

### 生命周期建议

- **初始化**：`TradingAgentsGraph`实例化开销较大（涉及LLM客户端、向量数据库、工具节点等），建议在应用生命周期内复用单个实例，避免频繁创建。
- **状态管理**：实例内部维护`curr_state`和`ticker`等状态变量，因此**不是无状态的**。在多任务场景下，应确保同一实例不被并发调用`propagate`。
- **资源释放**：当前未实现显式销毁方法。若需释放资源（如ChromaDB连接），可考虑扩展类以添加`close()`方法。

### 线程安全说明

- **非线程安全**：由于类内部维护共享状态（如`curr_state`、`log_states_dict`），`TradingAgentsGraph`实例**不支持多线程并发调用**。
- **推荐使用模式**：
  - 单线程顺序执行：适用于单账户、单策略场景。
  - 实例池模式：为每个工作线程分配独立的`TradingAgentsGraph`实例。
  - 异步隔离：在异步环境中，确保每个`propagate`调用之间有状态隔离。

**Section sources**
- [trading_graph.py](file://tradingagents/graph/trading_graph.py#L31-L253)
- [memory.py](file://tradingagents/agents/utils/memory.py#L1-L113)