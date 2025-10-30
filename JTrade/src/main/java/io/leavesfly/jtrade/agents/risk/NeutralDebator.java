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
 * 中立风险辩论者
 * 
 * 平衡风险与收益，提供折中的投资策略建议
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class NeutralDebator implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public NeutralDebator(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.5)  // 中等创造性
                .maxTokens(1000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("中立风险辩论者分析：{}", state.getCompany());
        
        try {
            String tradingPlan = state.getTradingPlan();
            RiskDebateState currentDebate = state.getRiskDebate();
            
            // 构建提示词
            String prompt = buildPrompt(state, tradingPlan, currentDebate);
            
            // 调用LLM
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位中立的风险分析师，善于平衡风险与收益。" +
                "你既不过分激进也不过分保守，寻找最优的风险收益比。" +
                "你的分析要客观公正，综合考虑各方观点。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String argument = "【中立观点】" + response.getContent();
            
            // 更新风险辩论状态
            RiskDebateState newDebate = RiskDebateState.builder()
                    .currentRound(currentDebate.getCurrentRound())
                    .maxRounds(currentDebate.getMaxRounds())
                    .aggressiveStrategies(currentDebate.getAggressiveStrategies())
                    .conservativeStrategies(currentDebate.getConservativeStrategies())
                    .neutralStrategies(addToList(currentDebate.getNeutralStrategies(), argument))
                    .lastSpeaker("NEUTRAL")
                    .build();
            
            log.info("中立观点已提出");
            
            return state.toBuilder()
                    .riskDebate(newDebate)
                    .build();
            
        } catch (Exception e) {
            log.error("中立辩论者执行失败", e);
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
        
        // 获取双方观点
        if (!debate.getAggressiveStrategies().isEmpty()) {
            sb.append("激进派观点：\n");
            sb.append(debate.getAggressiveStrategies().get(
                debate.getAggressiveStrategies().size() - 1)).append("\n\n");
        }
        
        if (!debate.getConservativeStrategies().isEmpty()) {
            sb.append("保守派观点：\n");
            sb.append(debate.getConservativeStrategies().get(
                debate.getConservativeStrategies().size() - 1)).append("\n\n");
        }
        
        sb.append("作为中立风险分析师，请提出你的观点：\n");
        sb.append("1. 客观评估激进派和保守派的论点\n");
        sb.append("2. 分析风险与收益的平衡点\n");
        sb.append("3. 提出折中的投资策略\n");
        sb.append("4. 指出双方观点的合理性和局限性\n");
        sb.append("5. 给出最优风险收益比的建议\n");
        sb.append("\n请用对话方式表达，综合双方观点。");
        
        return sb.toString();
    }
    
    private List<String> addToList(List<String> list, String item) {
        List<String> newList = new ArrayList<>(list);
        newList.add(item);
        return newList;
    }
    
    @Override
    public String getName() {
        return "中立风险辩论者";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.RISK_MANAGER;
    }
}
