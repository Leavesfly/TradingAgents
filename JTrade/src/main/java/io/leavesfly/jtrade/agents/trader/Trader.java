package io.leavesfly.jtrade.agents.trader;

import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.base.AgentType;
import io.leavesfly.jtrade.core.state.AgentState;
import io.leavesfly.jtrade.llm.client.LlmClient;
import io.leavesfly.jtrade.llm.model.LlmMessage;
import io.leavesfly.jtrade.llm.model.LlmResponse;
import io.leavesfly.jtrade.llm.model.ModelConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * 交易员
 * 
 * 基于研究经理的决策制定具体交易计划
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class Trader implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public Trader(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.5)
                .maxTokens(1500)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("交易员开始制定交易计划：{}", state.getCompany());
        
        try {
            // 获取研究经理决策
            String managerDecision = state.getResearchManagerDecision();
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), managerDecision);
            
            // 调用LLM制定交易计划
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位专业的交易员，负责将投资决策转化为具体的交易计划。" +
                "你需要明确交易的时机、价格、数量等细节。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String tradingPlan = response.getContent();
            
            log.info("交易计划制定完成，计划长度：{} 字符", tradingPlan.length());
            
            // 更新状态
            return state.toBuilder()
                    .tradingPlan(tradingPlan)
                    .build();
            
        } catch (Exception e) {
            log.error("交易计划制定失败", e);
            return state.toBuilder()
                    .tradingPlan(String.format("计划制定失败：%s", e.getMessage()))
                    .build();
        }
    }
    
    private String buildPrompt(String symbol, String managerDecision) {
        StringBuilder sb = new StringBuilder();
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("研究经理决策：\n");
        sb.append(managerDecision).append("\n\n");
        
        sb.append("作为交易员，请制定具体的交易计划：\n");
        sb.append("1. 明确交易方向（买入/卖出/观望）\n");
        sb.append("2. 建议的交易时机（立即/等待回调/观察确认）\n");
        sb.append("3. 建议的仓位配置（具体百分比）\n");
        sb.append("4. 入场价格区间或条件\n");
        sb.append("5. 止损位和止盈位\n");
        sb.append("6. 仓位管理策略（分批建仓/一次性等）\n");
        sb.append("\n请提供详细、可执行的交易计划。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "交易员";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.TRADER;
    }
}
