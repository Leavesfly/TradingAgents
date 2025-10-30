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
 * 激进风险辩论者
 * 
 * 倡导高风险高回报的投资策略，挑战保守观点
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class AggressiveDebator implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public AggressiveDebator(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.8)  // 更高的创造性
                .maxTokens(1000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("激进风险辩论者分析：{}", state.getCompany());
        
        try {
            String tradingPlan = state.getTradingPlan();
            RiskDebateState currentDebate = state.getRiskDebate();
            
            // 构建提示词
            String prompt = buildPrompt(state, tradingPlan, currentDebate);
            
            // 调用LLM
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位激进的风险分析师，善于发现高收益机会。" +
                "你主张承担合理的风险以获取更高回报，敢于挑战保守观点。" +
                "你的分析要有说服力，用数据支持你的激进观点。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String argument = "【激进观点】" + response.getContent();
            
            // 更新风险辩论状态
            RiskDebateState newDebate = RiskDebateState.builder()
                    .currentRound(currentDebate.getCurrentRound())
                    .maxRounds(currentDebate.getMaxRounds())
                    .aggressiveStrategies(addToList(currentDebate.getAggressiveStrategies(), argument))
                    .conservativeStrategies(currentDebate.getConservativeStrategies())
                    .neutralStrategies(currentDebate.getNeutralStrategies())
                    .lastSpeaker("AGGRESSIVE")
                    .build();
            
            log.info("激进观点已提出");
            
            return state.toBuilder()
                    .riskDebate(newDebate)
                    .build();
            
        } catch (Exception e) {
            log.error("激进辩论者执行失败", e);
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
        if (!debate.getConservativeStrategies().isEmpty()) {
            sb.append("保守派观点：\n");
            sb.append(debate.getConservativeStrategies().get(
                debate.getConservativeStrategies().size() - 1)).append("\n\n");
        }
        
        if (!debate.getNeutralStrategies().isEmpty()) {
            sb.append("中立派观点：\n");
            sb.append(debate.getNeutralStrategies().get(
                debate.getNeutralStrategies().size() - 1)).append("\n\n");
        }
        
        sb.append("作为激进风险分析师，请提出你的观点：\n");
        sb.append("1. 识别高收益机会和增长潜力\n");
        sb.append("2. 分析为什么现在值得承担风险\n");
        sb.append("3. 反驳保守派的过度谨慎\n");
        sb.append("4. 用数据支持你的激进策略\n");
        sb.append("5. 提出具体的高风险高回报建议\n");
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
        return "激进风险辩论者";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.RISK_MANAGER;
    }
}
