package io.leavesfly.jtrade.agents.analysts;

import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.base.AgentType;
import io.leavesfly.jtrade.core.state.AgentState;
import io.leavesfly.jtrade.dataflow.model.NewsData;
import io.leavesfly.jtrade.dataflow.provider.DataAggregator;
import io.leavesfly.jtrade.llm.client.LlmClient;
import io.leavesfly.jtrade.llm.model.LlmMessage;
import io.leavesfly.jtrade.llm.model.LlmResponse;
import io.leavesfly.jtrade.llm.model.ModelConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * 新闻分析师
 * 
 * 负责分析市场新闻和事件影响
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class NewsAnalyst implements Agent {
    
    private final LlmClient llmClient;
    private final DataAggregator dataAggregator;
    private final ModelConfig modelConfig;
    
    public NewsAnalyst(LlmClient llmClient, DataAggregator dataAggregator) {
        this.llmClient = llmClient;
        this.dataAggregator = dataAggregator;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("新闻分析师开始分析：{}", state.getCompany());
        
        try {
            // 获取新闻数据
            List<NewsData> newsList = dataAggregator.getNewsData(state.getCompany(), 10);
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), newsList);
            
            // 调用LLM进行分析
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system("你是一位资深的新闻分析师，擅长解读市场新闻和事件对股价的影响。"));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String analysis = response.getContent();
            
            log.info("新闻分析完成，分析长度：{} 字符", analysis.length());
            
            // 更新状态
            return state.addAnalystReport(
                    String.format("【新闻分析师】\n%s", analysis)
            );
            
        } catch (Exception e) {
            log.error("新闻分析失败", e);
            return state.addAnalystReport(
                    String.format("【新闻分析师】分析失败：%s", e.getMessage())
            );
        }
    }
    
    private String buildPrompt(String symbol, List<NewsData> newsList) {
        StringBuilder sb = new StringBuilder();
        sb.append("请分析以下关于 ").append(symbol).append(" 的最新新闻：\n\n");
        
        int count = 1;
        for (NewsData news : newsList) {
            sb.append(count++).append(". ");
            sb.append("【").append(news.getSource()).append("】");
            sb.append(news.getTitle()).append("\n");
            if (news.getSummary() != null) {
                sb.append("   摘要：").append(news.getSummary()).append("\n");
            }
            if (news.getSentimentScore() != null) {
                sb.append("   情绪分数：").append(news.getSentimentScore()).append("\n");
            }
            sb.append("\n");
        }
        
        sb.append("请基于这些新闻：\n");
        sb.append("1. 分析新闻的整体情绪倾向（积极/消极/中性）\n");
        sb.append("2. 识别可能影响股价的重要事件或趋势\n");
        sb.append("3. 评估新闻对公司短期和中期走势的影响\n");
        sb.append("4. 给出基于新闻的投资建议（买入/卖出/观望）\n");
        sb.append("\n请提供专业、简洁的分析报告。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "新闻分析师";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.NEWS_ANALYST;
    }
}
