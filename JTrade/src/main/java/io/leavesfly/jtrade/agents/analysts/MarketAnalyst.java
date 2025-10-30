package io.leavesfly.jtrade.agents.analysts;

import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.base.AgentType;
import io.leavesfly.jtrade.core.state.AgentState;
import io.leavesfly.jtrade.dataflow.provider.DataAggregator;
import io.leavesfly.jtrade.llm.client.LlmClient;
import io.leavesfly.jtrade.llm.model.LlmMessage;
import io.leavesfly.jtrade.llm.model.LlmResponse;
import io.leavesfly.jtrade.llm.model.ModelConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 市场分析师
 * 
 * 负责分析技术指标和市场趋势
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class MarketAnalyst implements Agent {
    
    private final LlmClient llmClient;
    private final DataAggregator dataAggregator;
    private final ModelConfig modelConfig;
    
    public MarketAnalyst(LlmClient llmClient, DataAggregator dataAggregator) {
        this.llmClient = llmClient;
        this.dataAggregator = dataAggregator;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("市场分析师开始分析：{}", state.getCompany());
        
        try {
            // 获取技术指标数据
            Map<String, Double> indicators = dataAggregator.getTechnicalIndicators(state.getCompany());
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), indicators);
            
            // 调用LLM进行分析
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system("你是一位资深的技术分析师，擅长分析市场趋势和技术指标。"));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String analysis = response.getContent();
            
            log.info("市场分析完成，分析长度：{} 字符", analysis.length());
            
            // 更新状态
            return state.addAnalystReport(
                    String.format("【市场分析师】\n%s", analysis)
            );
            
        } catch (Exception e) {
            log.error("市场分析失败", e);
            return state.addAnalystReport(
                    String.format("【市场分析师】分析失败：%s", e.getMessage())
            );
        }
    }
    
    private String buildPrompt(String symbol, Map<String, Double> indicators) {
        StringBuilder sb = new StringBuilder();
        sb.append("请分析以下股票的技术指标：\n\n");
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("技术指标：\n");
        
        indicators.forEach((key, value) -> 
            sb.append("- ").append(key).append(": ").append(value).append("\n")
        );
        
        sb.append("\n请基于这些技术指标：\n");
        sb.append("1. 分析当前市场趋势（上涨/下跌/横盘）\n");
        sb.append("2. 评估技术面强弱\n");
        sb.append("3. 识别关键支撑位和阻力位\n");
        sb.append("4. 给出技术面建议（买入/卖出/观望）\n");
        sb.append("\n请提供专业、简洁的分析报告。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "市场分析师";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.MARKET_ANALYST;
    }
}
