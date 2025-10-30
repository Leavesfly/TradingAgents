package io.leavesfly.jtrade.agents.analysts;

import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.base.AgentType;
import io.leavesfly.jtrade.core.state.AgentState;
import io.leavesfly.jtrade.dataflow.model.FundamentalData;
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
 * 基本面分析师
 * 
 * 负责分析公司财务数据和基本面指标
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class FundamentalsAnalyst implements Agent {
    
    private final LlmClient llmClient;
    private final DataAggregator dataAggregator;
    private final ModelConfig modelConfig;
    
    public FundamentalsAnalyst(LlmClient llmClient, DataAggregator dataAggregator) {
        this.llmClient = llmClient;
        this.dataAggregator = dataAggregator;
        this.modelConfig = ModelConfig.builder()
                .temperature(0.7)
                .maxTokens(2000)
                .build();
    }
    
    @Override
    public AgentState execute(AgentState state) {
        log.info("基本面分析师开始分析：{}", state.getCompany());
        
        try {
            // 获取基本面数据
            FundamentalData fundamentals = dataAggregator.getFundamentalData(state.getCompany());
            
            // 构建提示词
            String prompt = buildPrompt(state.getCompany(), fundamentals);
            
            // 调用LLM进行分析
            List<LlmMessage> messages = new ArrayList<>();
            messages.add(LlmMessage.system("你是一位资深的基本面分析师，擅长分析公司财务数据和估值。"));
            messages.add(LlmMessage.user(prompt));
            
            LlmResponse response = llmClient.chat(messages, modelConfig);
            String analysis = response.getContent();
            
            log.info("基本面分析完成，分析长度：{} 字符", analysis.length());
            
            // 更新状态
            return state.addAnalystReport(
                    String.format("【基本面分析师】\n%s", analysis)
            );
            
        } catch (Exception e) {
            log.error("基本面分析失败", e);
            return state.addAnalystReport(
                    String.format("【基本面分析师】分析失败：%s", e.getMessage())
            );
        }
    }
    
    private String buildPrompt(String symbol, FundamentalData data) {
        StringBuilder sb = new StringBuilder();
        sb.append("请分析以下公司的基本面数据：\n\n");
        sb.append("公司名称：").append(data.getCompanyName()).append("\n");
        sb.append("股票代码：").append(symbol).append("\n\n");
        sb.append("财务指标：\n");
        
        if (data.getMarketCap() != null) {
            sb.append("- 市值：").append(data.getMarketCap()).append("\n");
        }
        if (data.getPeRatio() != null) {
            sb.append("- 市盈率 (P/E)：").append(data.getPeRatio()).append("\n");
        }
        if (data.getPbRatio() != null) {
            sb.append("- 市净率 (P/B)：").append(data.getPbRatio()).append("\n");
        }
        if (data.getEps() != null) {
            sb.append("- 每股收益 (EPS)：").append(data.getEps()).append("\n");
        }
        if (data.getDividendYield() != null) {
            sb.append("- 股息收益率：").append(data.getDividendYield()).append("%\n");
        }
        
        sb.append("\n请基于这些基本面数据：\n");
        sb.append("1. 评估公司的估值水平（高估/合理/低估）\n");
        sb.append("2. 分析公司的盈利能力和财务健康状况\n");
        sb.append("3. 识别潜在的投资风险和机会\n");
        sb.append("4. 给出基本面投资建议（买入/卖出/观望）\n");
        sb.append("\n请提供专业、简洁的分析报告。");
        
        return sb.toString();
    }
    
    @Override
    public String getName() {
        return "基本面分析师";
    }
    
    @Override
    public AgentType getType() {
        return AgentType.FUNDAMENTALS_ANALYST;
    }
}
