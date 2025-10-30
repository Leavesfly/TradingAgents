package io.leavesfly.jtrade.agents.risk;

import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.base.AgentType;
import io.leavesfly.jtrade.core.state.AgentState;
import io.leavesfly.jtrade.core.state.RiskDebateState;
import io.leavesfly.jtrade.llm.client.LlmClient;
import io.leavesfly.jtrade.llm.model.LlmMessage;
import io.leavesfly.jtrade.llm.model.LlmResponse;
import io.leavesfly.jtrade.llm.model.ModelConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * 保守风险辩论者
 * 
 * 倡导低风险稳健的投资策略，强调资产保护
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class ConservativeDebator implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public ConservativeDebator(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.3)  // 更保守的输出
                .maxTokens(1000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("保守风险辩论者分析：{}", state.getCompany());
        
        try {
            String tradingPlan = state.getTradingPlan();
            RiskDebateState currentDebate = state.getRiskDebate();
            
            // 构建提示词
            String prompt = buildPrompt(state, tradingPlan, currentDebate);
            
            // 调用LLM
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位保守的风险分析师，擅长识别潜在风险。" +
                "你主张稳健的投资策略，优先保护资产，避免过度冒险。" +
                "你的分析要严谨，善于发现激进策略中的隐患。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String argument = "【保守观点】" + response.getContent();
            
            // 更新风险辩论状态
            RiskDebateState newDebate = RiskDebateState.builder()
                    .currentRound(currentDebate.getCurrentRound())
                    .maxRounds(currentDebate.getMaxRounds())
                    .aggressiveStrategies(currentDebate.getAggressiveStrategies())
                    .conservativeStrategies(addToList(currentDebate.getConservativeStrategies(), argument))
                    .neutralStrategies(currentDebate.getNeutralStrategies())
                    .lastSpeaker("CONSERVATIVE")
                    .build();
            
            log.info("保守观点已提出");
            
            return state.toBuilder()
                    .riskDebate(newDebate)
                    .build();
            
        } catch (Exception e) {
            log.error("保守辩论者执行失败", e);
            return state;
        }
    }
    
    private String buildPrompt(AgentState state, String tradingPlan, RiskDebateState debate) {
        StringBuilder sb = new StringBuilder();
        
        sb.append("股票代码：").append(state.getCompany()).append("\n\n");
        
        sb.append("市场分析摘要：\n");
        if (!state.getAnalystReports().isEmpty()) {
            sb.append(state.getAnalystReports().get(0)).append("\n\n");
        }
        
        sb.append("交易计划：\n");
        sb.append(tradingPlan).append("\n\n");
        
        // 获取对手观点
        if (!debate.getAggressiveStrategies().isEmpty()) {
            sb.append("激进派观点：\n");
            sb.append(debate.getAggressiveStrategies().get(
                debate.getAggressiveStrategies().size() - 1)).append("\n\n");
        }
        
        if (!debate.getNeutralStrategies().isEmpty()) {
            sb.append("中立派观点：\n");
            sb.append(debate.getNeutralStrategies().get(
                debate.getNeutralStrategies().size() - 1)).append("\n\n");
        }
        
        sb.append("作为保守风险分析师，请提出你的观点：\n");
        sb.append("1. 识别潜在风险和隐患\n");
        sb.append("2. 分析激进策略可能带来的损失\n");
        sb.append("3. 强调资产保护和稳健增长的重要性\n");
        sb.append("4. 提出更安全的替代方案\n");
        sb.append("5. 反驳激进派的过度乐观\n");
        sb.append("\n请用对话方式表达，直接回应对手观点。");
        
        return sb.toString();
    }
    
    private List<String> addToList(List<String> list, String item) {
        List<String> newList = new ArrayList<>(list);
        newList.add(item);
        return newList;
    }
    
    @Override
    public String getName() {
        return "保守风险辩论者";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.RISK_MANAGER;
    }
}
