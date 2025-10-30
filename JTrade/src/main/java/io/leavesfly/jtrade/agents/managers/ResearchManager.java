package io.leavesfly.jtrade.agents.managers;

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
 * 研究经理
 * 
 * 综合多空双方观点，做出最终投资决策
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class ResearchManager implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public ResearchManager(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.6)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("研究经理开始综合决策：{}", state.getCompany());
        
        try {
            // 汇总所有观点
            String allViewpoints = String.join("\n\n", state.getResearcherViewpoints());
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), allViewpoints);
            
            // 调用LLM进行决策
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位经验丰富的研究经理，负责综合多空双方的观点做出最终投资决策。" +
                "你需要客观、理性地权衡双方论据，做出明确的投资建议。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String decision = response.getContent();
            
            log.info("研究经理决策完成，决策长度：{} 字符", decision.length());
            
            // 更新状态
            return state.toBuilder()
                    .researchManagerDecision(decision)
                    .build();
            
        } catch (Exception e) {
            log.error("研究经理决策失败", e);
            return state.toBuilder()
                    .researchManagerDecision(String.format("决策失败：%s", e.getMessage()))
                    .build();
        }
    }
    
    private String buildPrompt(String symbol, String researcherViewpoints) {
        StringBuilder sb = new StringBuilder();
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("研究员观点汇总：\n");
        sb.append(researcherViewpoints).append("\n\n");
        
        sb.append("作为研究经理，请：\n");
        sb.append("1. 客观评估多空双方的论据强度\n");
        sb.append("2. 权衡各种因素和风险\n");
        sb.append("3. 做出明确的投资方向决策（买入/卖出/观望）\n");
        sb.append("4. 如果决定买入或卖出，请给出建议的仓位大小（轻仓/中仓/重仓）\n");
        sb.append("5. 说明决策的核心依据和风险提示\n");
        sb.append("\n请提供清晰、果断的决策建议。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "研究经理";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.RESEARCH_MANAGER;
    }
}
