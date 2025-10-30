# JTrade - Java版多智能体交易系统

基于大语言模型的多智能体金融交易决策框架，使用Java 17和Spring Boot实现。

## 项目简介

JTrade是TradingAgents的Java重构版本，采用多智能体架构模拟真实交易公司的运作流程：
- **分析师团队**: 市场分析、新闻分析、社交媒体情绪分析、基本面分析
- **研究员团队**: 看涨/看跌研究员通过辩论评估市场方向
- **交易员**: 制定具体交易计划
- **风险管理**: 激进/保守/中立策略辩论并最终审批

## 技术栈

- **Java 17** - 现代Java特性
- **Spring Boot 3.2+** - 应用框架
- **OkHttp** - HTTP客户端
- **Jackson** - JSON处理
- **Maven** - 构建工具

## LLM支持

支持多种LLM提供商，通过配置轻松切换：
- **OpenAI**: gpt-4o-mini, o1-mini
- **通义千问**: qwen-plus, qwen-turbo
- **DeepSeek**: deepseek-chat
- **Ollama**: 本地模型支持

## 快速开始

### 环境要求

- JDK 17或更高版本
- Maven 3.8+
- 至少一个LLM API密钥（OpenAI/Qwen/DeepSeek）或本地Ollama

### 配置环境变量

```bash
export OPENAI_API_KEY=your_openai_key        # 使用OpenAI时
export DASHSCOPE_API_KEY=your_dashscope_key  # 使用通义千问时
export DEEPSEEK_API_KEY=your_deepseek_key    # 使用DeepSeek时
export FINNHUB_API_KEY=your_finnhub_key      # 数据源（必需）
```

### 构建项目

```bash
cd JTrade
mvn clean package
```

### 运行程序

```bash
# 命令行模式
java -jar target/jtrade-1.0.0.jar --company=NVDA --date=2024-05-10

# 交互式模式
java -jar target/jtrade-1.0.0.jar
```

## 配置说明

编辑 `src/main/resources/application.yml` 选择LLM提供商：

```yaml
jtrade:
  llm:
    provider: qwen  # 可选: openai, qwen, deepseek, ollama
```

## 项目结构

```
src/main/java/io/leavesfly/jtrade/
├── config/          # 配置类
├── core/            # 核心组件（状态机、工作流）
├── agents/          # 智能体实现
├── llm/             # LLM客户端
├── dataflow/        # 数据提供者
├── service/         # 业务服务
└── cli/             # 命令行界面
```

## 开发指南

### 新增LLM提供商

只需在 `application.yml` 添加配置即可支持任何OpenAI兼容的API。

### 新增智能体

1. 实现 `Agent` 接口
2. 在 `AgentFactory` 注册
3. 配置Prompt模板

## 许可证

MIT License

## 作者

山泽
