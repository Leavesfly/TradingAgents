package io.leavesfly.jtrade.agents.managers;

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
 * 风险管理器
 * 
 * 评估交易计划的风险，做出最终批准决策
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class RiskManager implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public RiskManager(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.5)
                .maxTokens(1500)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("风险管理器开始评估：{}", state.getCompany());
        
        try {
            // 获取交易计划和风险辩论
            String tradingPlan = state.getTradingPlan();
            RiskDebateState riskDebate = state.getRiskDebate();
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), tradingPlan, riskDebate);
            
            // 调用LLM做出最终决策
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位严谨的风险管理器，负责评估交易计划的风险并做出最终批准决策。" +
                "你需要权衡收益和风险，确保交易符合风险管理原则。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String decision = response.getContent();
            
            // 从决策中提取最终信号
            String finalSignal = extractSignal(decision);
            
            log.info("风险管理决策完成，最终信号：{}", finalSignal);
            
            // 更新状态
            return state.toBuilder()
                    .riskManagerDecision(decision)
                    .finalSignal(finalSignal)
                    .build();
            
        } catch (Exception e) {
            log.error("风险管理决策失败", e);
            return state.toBuilder()
                    .riskManagerDecision(String.format("决策失败：%s", e.getMessage()))
                    .finalSignal("HOLD")
                    .build();
        }
    }
    
    private String buildPrompt(String symbol, String tradingPlan, RiskDebateState riskDebate) {
        StringBuilder sb = new StringBuilder();
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("交易计划：\n");
        sb.append(tradingPlan).append("\n\n");
        
        if (riskDebate != null) {
            sb.append("风险辩论记录：\n");
            if (!riskDebate.getAggressiveStrategies().isEmpty()) {
                sb.append("激进观点：").append(String.join("; ", riskDebate.getAggressiveStrategies())).append("\n");
            }
            if (!riskDebate.getConservativeStrategies().isEmpty()) {
                sb.append("保守观点：").append(String.join("; ", riskDebate.getConservativeStrategies())).append("\n");
            }
            if (!riskDebate.getNeutralStrategies().isEmpty()) {
                sb.append("中立观点：").append(String.join("; ", riskDebate.getNeutralStrategies())).append("\n");
            }
            sb.append("\n");
        }
        
        sb.append("作为风险管理器，请：\n");
        sb.append("1. 评估交易计划的整体风险水平\n");
        sb.append("2. 检查止损和止盈设置是否合理\n");
        sb.append("3. 评估仓位配置是否符合风险管理原则\n");
        sb.append("4. 综合考虑风险辩论中的各方观点\n");
        sb.append("5. 做出最终决策：APPROVE（批准）、REJECT（拒绝）或 MODIFY（建议修改）\n");
        sb.append("6. 如果批准，明确最终交易信号：BUY、SELL 或 HOLD\n");
        sb.append("\n请提供清晰的风险评估和最终决策。");
        
        return sb.toString();
    }
    
    /**
     * 从决策文本中提取交易信号
     */
    private String extractSignal(String decision) {
        String upperDecision = decision.toUpperCase();
        
        if (upperDecision.contains("BUY") || upperDecision.contains("买入")) {
            return "BUY";
        } else if (upperDecision.contains("SELL") || upperDecision.contains("卖出")) {
            return "SELL";
        } else {
            return "HOLD";
        }
    }
    
    @Override
    public String getName() {
        return "风险管理器";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.RISK_MANAGER;
    }
}
