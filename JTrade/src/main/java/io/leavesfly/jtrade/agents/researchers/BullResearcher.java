package io.leavesfly.jtrade.agents.researchers;

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
 * 多头研究员
 * 
 * 从看涨角度分析市场，提供买入建议
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class BullResearcher implements Agent {
    
    private final LlmClient llmClient;
    private final ModelConfig modelConfig;
    
    public BullResearcher(LlmClient llmClient) {
        this.llmClient = llmClient;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.8)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("多头研究员开始分析：{}", state.getCompany());
        
        try {
            // 汇总所有分析师报告
            String allReports = String.join("\n\n", state.getAnalystReports());
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), allReports);
            
            // 调用LLM进行分析
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system(
                "你是一位看涨的研究员，专注于寻找买入机会。" +
                "你需要从积极的角度分析市场数据，寻找支持看涨观点的证据。" +
                "但你也必须保持专业和客观，不能忽视明显的风险。"
            ));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String viewpoint = response.getContent();
            
            log.info("多头研究完成，观点长度：{} 字符", viewpoint.length());
            
            // 更新状态
            return state.addResearcherViewpoint(
                    String.format("【多头研究员】\n%s", viewpoint)
            );
            
        } catch (Exception e) {
            log.error("多头研究失败", e);
            return state.addResearcherViewpoint(
                    String.format("【多头研究员】分析失败：%s", e.getMessage())
            );
        }
    }
    
    private String buildPrompt(String symbol, String analystReports) {
        StringBuilder sb = new StringBuilder();
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("分析师报告汇总：\n");
        sb.append(analystReports).append("\n\n");
        
        sb.append("作为多头研究员，请从看涨角度分析：\n");
        sb.append("1. 找出所有支持看涨的积极因素和机会\n");
        sb.append("2. 分析为什么现在可能是买入的好时机\n");
        sb.append("3. 评估上涨潜力和目标价位\n");
        sb.append("4. 提出具体的买入建议和仓位配置\n");
        sb.append("5. 同时也要指出潜在风险（保持客观）\n");
        sb.append("\n请提供有说服力的多头观点。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "多头研究员";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.BULL_RESEARCHER;
    }
}
