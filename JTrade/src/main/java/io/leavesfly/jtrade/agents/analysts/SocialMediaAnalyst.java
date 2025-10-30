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
 * 社交媒体分析师
 * 
 * 负责分析社交媒体情绪和舆论
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class SocialMediaAnalyst implements Agent {
    
    private final LlmClient llmClient;
    private final DataAggregator dataAggregator;
    private final ModelConfig modelConfig;
    
    public SocialMediaAnalyst(LlmClient llmClient, DataAggregator dataAggregator) {
        this.llmClient = llmClient;
        this.dataAggregator = dataAggregator;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("社交媒体分析师开始分析：{}", state.getCompany());
        
        try {
            // 获取社交媒体情绪数据
            Map<String, Object> sentiment = dataAggregator.getSocialMediaSentiment(state.getCompany());
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), sentiment);
            
            // 调用LLM进行分析
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system("你是一位资深的社交媒体分析师，擅长分析散户情绪和市场舆论。"));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String analysis = response.getContent();
            
            log.info("社交媒体分析完成，分析长度：{} 字符", analysis.length());
            
            // 更新状态
            return state.addAnalystReport(
                    String.format("【社交媒体分析师】\n%s", analysis)
            );
            
        } catch (Exception e) {
            log.error("社交媒体分析失败", e);
            return state.addAnalystReport(
                    String.format("【社交媒体分析师】分析失败：%s", e.getMessage())
            );
        }
    }
    
    private String buildPrompt(String symbol, Map<String, Object> sentiment) {
        StringBuilder sb = new StringBuilder();
        sb.append("请分析以下关于 ").append(symbol).append(" 的社交媒体情绪数据：\n\n");
        
        sb.append("情绪指标：\n");
        sentiment.forEach((key, value) -> 
            sb.append("- ").append(key).append(": ").append(value).append("\n")
        );
        
        sb.append("\n请基于这些社交媒体数据：\n");
        sb.append("1. 分析散户投资者的整体情绪倾向\n");
        sb.append("2. 评估社交媒体热度和关注度的变化趋势\n");
        sb.append("3. 识别可能影响股价的舆论热点\n");
        sb.append("4. 判断散户情绪是否可能引发短期价格波动\n");
        sb.append("5. 给出基于情绪分析的投资建议（买入/卖出/观望）\n");
        sb.append("\n请提供专业、简洁的分析报告。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "社交媒体分析师";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.SOCIAL_MEDIA_ANALYST;
    }
}
