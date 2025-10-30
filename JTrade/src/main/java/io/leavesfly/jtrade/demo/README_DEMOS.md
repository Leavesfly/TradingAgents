# JTrade 演示程序说明

本目录包含多个演示程序，展示JTrade系统的不同功能和使用场景。

## 演示程序列表

### 1. AgentPerformanceDemo - 智能体性能分析
**运行命令：**
```bash
mvn spring-boot:run -Dspring-boot.run.main-class=io.leavesfly.jtrade.demo.AgentPerformanceDemo
```

**功能：**
- 测试所有智能体的执行性能
- 统计每个智能体的执行时间
- 分析系统整体性能指标
- 计算成功率和平均响应时间

**适用场景：**
- 系统性能调优
- 智能体效率评估
- 瓶颈识别

---

### 2. InteractiveDemo - 交互式演示
**运行命令：**
```bash
mvn spring-boot:run -Dspring-boot.run.main-class=io.leavesfly.jtrade.demo.InteractiveDemo
```

**功能：**
- 提供友好的命令行交互界面
- 支持用户自定义输入股票代码和日期
- 实时显示分析进度
- 格式化输出分析结果

**适用场景：**
- 日常交易分析
- 新用户学习使用
- 快速查询单只股票

**使用提示：**
- 输入股票代码（如：AAPL、TSLA）
- 输入分析日期或直接回车使用今天
- 输入 'exit' 退出程序

---

### 3. WorkflowVisualizationDemo - 工作流可视化
**运行命令：**
```bash
mvn spring-boot:run -Dspring-boot.run.main-class=io.leavesfly.jtrade.demo.WorkflowVisualizationDemo
```

**功能：**
- 图形化展示完整工作流程
- 分阶段显示智能体执行过程
- 实时显示每个阶段的进度
- 输出各阶段的统计信息

**适用场景：**
- 系统架构演示
- 工作流理解
- 教学和培训

**特点：**
- 清晰的阶段划分
- 直观的进度展示
- 详细的执行统计

---

### 4. BatchTestDemo - 批量测试
**运行命令：**
```bash
mvn spring-boot:run -Dspring-boot.run.main-class=io.leavesfly.jtrade.demo.BatchTestDemo
```

**功能：**
- 批量分析多只股票
- 生成汇总统计报告
- 计算整体性能指标
- 识别系统稳定性

**测试股票：**
- AAPL (苹果)
- TSLA (特斯拉)
- NVDA (英伟达)
- MSFT (微软)
- GOOGL (谷歌)

**适用场景：**
- 系统压力测试
- 稳定性验证
- 性能基准测试

---

### 5. ComparativeAnalysisDemo - 对比分析
**运行命令：**
```bash
mvn spring-boot:run -Dspring-boot.run.main-class=io.leavesfly.jtrade.demo.ComparativeAnalysisDemo
```

**功能：**
- 多股票横向对比
- 交易信号分组统计
- 投资建议排名
- 组合配置建议

**分析维度：**
- 交易信号对比
- 分析深度评估
- 风险提示
- 投资组合优化

**适用场景：**
- 选股决策
- 投资组合构建
- 风险分散策略

**输出内容：**
- 买入/卖出/持有分组
- 推荐买入顺序
- 仓位配置建议
- 风险警示

---

## 运行前准备

1. **设置环境变量**
```bash
# 通义千问（推荐）
export DASHSCOPE_API_KEY=your_api_key

# 或 OpenAI
export OPENAI_API_KEY=your_api_key
```

2. **编译项目**
```bash
cd JTrade
mvn clean compile -DskipTests
```

3. **修改配置（可选）**
编辑 `src/main/resources/application.yml`
```yaml
jtrade:
  llm:
    provider: qwen  # 可选: openai, qwen, deepseek, ollama
```

## 演示程序对比

| 演示程序 | 复杂度 | 执行时间 | 适用场景 | 教育价值 |
|---------|-------|---------|---------|---------|
| InteractiveDemo | 低 | 快 | 日常使用 | ⭐⭐⭐⭐⭐ |
| AgentPerformanceDemo | 中 | 中 | 性能调优 | ⭐⭐⭐⭐ |
| WorkflowVisualizationDemo | 中 | 中 | 系统理解 | ⭐⭐⭐⭐⭐ |
| BatchTestDemo | 高 | 慢 | 压力测试 | ⭐⭐⭐ |
| ComparativeAnalysisDemo | 高 | 慢 | 投资决策 | ⭐⭐⭐⭐ |

## 注意事项

1. **API调用限制**
   - 批量测试和对比分析会调用较多API
   - 注意API配额和费用
   - 建议先使用单股票演示

2. **执行时间**
   - 每个智能体调用需要几秒钟
   - 完整流程约需1-2分钟
   - 批量测试时间更长

3. **网络要求**
   - 需要稳定的网络连接
   - 访问LLM API服务
   - 建议在网络良好时运行

4. **资源消耗**
   - 建议JVM内存 >= 512MB
   - 多线程并发可能占用更多资源

## 故障排查

### 问题：编译失败
**解决：**
```bash
# 确保使用JDK 17
java -version

# 设置JAVA_HOME
export JAVA_HOME=/path/to/jdk-17

# 清理并重新编译
mvn clean compile
```

### 问题：API调用失败
**解决：**
```bash
# 检查环境变量是否设置
echo $DASHSCOPE_API_KEY

# 检查网络连接
ping dashscope.aliyuncs.com

# 查看application.yml配置
cat src/main/resources/application.yml
```

### 问题：程序无响应
**原因：**
- LLM调用超时
- 网络连接问题
- API限流

**解决：**
- 检查日志输出
- 稍后重试
- 更换LLM提供商

## 贡献

欢迎提交新的演示程序！请确保：
1. 具有教育价值
2. 代码清晰易懂
3. 包含详细注释
4. 添加使用说明

---

**作者：** 山泽  
**更新时间：** 2025-10-30
