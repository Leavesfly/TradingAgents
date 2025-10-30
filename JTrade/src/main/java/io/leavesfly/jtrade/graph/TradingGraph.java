package io.leavesfly.jtrade.graph;

import io.leavesfly.jtrade.agents.analysts.FundamentalsAnalyst;
import io.leavesfly.jtrade.agents.analysts.MarketAnalyst;
import io.leavesfly.jtrade.agents.analysts.NewsAnalyst;
import io.leavesfly.jtrade.agents.analysts.SocialMediaAnalyst;
import io.leavesfly.jtrade.agents.base.Agent;
import io.leavesfly.jtrade.agents.managers.ResearchManager;
import io.leavesfly.jtrade.agents.managers.RiskManager;
import io.leavesfly.jtrade.agents.researchers.BearResearcher;
import io.leavesfly.jtrade.agents.researchers.BullResearcher;
import io.leavesfly.jtrade.agents.risk.AggressiveDebator;
import io.leavesfly.jtrade.agents.risk.ConservativeDebator;
import io.leavesfly.jtrade.agents.risk.NeutralDebator;
import io.leavesfly.jtrade.agents.trader.Trader;
import io.leavesfly.jtrade.core.memory.MemoryService;
import io.leavesfly.jtrade.core.reflection.ReflectionService;
import io.leavesfly.jtrade.core.state.AgentState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * 交易图 - 协调所有智能体的主类
 * 
 * 对应 Python 版本的 TradingAgentsGraph
 * 负责编排完整的交易决策工作流
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class TradingGraph {
    
    // 分析师团队
    private final List<Agent> analysts = new ArrayList<>();
    
    // 研究员团队
    private final BullResearcher bullResearcher;
    private final BearResearcher bearResearcher;
    
    // 交易员
    private final Trader trader;
    
    // 风险辩论者
    private final AggressiveDebator aggressiveDebator;
    private final ConservativeDebator conservativeDebator;
    private final NeutralDebator neutralDebator;
    
    // 管理员
    private final ResearchManager researchManager;
    private final RiskManager riskManager;
    
    // 辅助服务
    private final ReflectionService reflectionService;
    private final MemoryService memoryService;
    
    // 条件逻辑
    private final ConditionalLogic conditionalLogic;
    
    // 配置
    private final int maxDebateRounds;
    private final int maxRiskDiscussRounds;
    
    public TradingGraph(
            MarketAnalyst marketAnalyst,
            FundamentalsAnalyst fundamentalsAnalyst,
            NewsAnalyst newsAnalyst,
            SocialMediaAnalyst socialMediaAnalyst,
            BullResearcher bullResearcher,
            BearResearcher bearResearcher,
            Trader trader,
            AggressiveDebator aggressiveDebator,
            ConservativeDebator conservativeDebator,
            NeutralDebator neutralDebator,
            ResearchManager researchManager,
            RiskManager riskManager,
            ReflectionService reflectionService,
            MemoryService memoryService) {
        
        // 初始化分析师团队
        this.analysts.add(marketAnalyst);
        this.analysts.add(fundamentalsAnalyst);
        this.analysts.add(newsAnalyst);
        this.analysts.add(socialMediaAnalyst);
        
        this.bullResearcher = bullResearcher;
        this.bearResearcher = bearResearcher;
        this.trader = trader;
        this.aggressiveDebator = aggressiveDebator;
        this.conservativeDebator = conservativeDebator;
        this.neutralDebator = neutralDebator;
        this.researchManager = researchManager;
        this.riskManager = riskManager;
        this.reflectionService = reflectionService;
        this.memoryService = memoryService;
        
        this.conditionalLogic = new ConditionalLogic();
        this.maxDebateRounds = 1;
        this.maxRiskDiscussRounds = 1;
    }
    
    /**
     * 执行完整的交易图流程
     * 
     * @param symbol 股票代码
     * @param date 交易日期
     * @return 最终状态
     */
    public AgentState propagate(String symbol, LocalDate date) {
        log.info("=====================================");
        log.info("启动交易图流程");
        log.info("股票: {} | 日期: {}", symbol, date);
        log.info("=====================================");
        
        // 初始化状态
        AgentState state = AgentState.builder()
                .company(symbol)
                .date(date)
                .build();
        
        try {
            // 阶段1: 分析师团队并行分析
            state = executeAnalysts(state);
            
            // 阶段2: 研究员辩论（带条件判断）
            state = executeDebate(state);
            
            // 阶段3: 研究经理决策
            state = researchManager.execute(state);
            
            // 阶段4: 交易员制定计划
            state = trader.execute(state);
            
            // 阶段5: 风险辩论（带条件判断）
            state = executeRiskDebate(state);
            
            // 阶段6: 风险管理审批
            state = riskManager.execute(state);
            
            // 阶段7: 反思与学习
            state = executeReflection(state);
            
            // 阶段8: 保存记忆
            memoryService.saveDecision(state);
            
            log.info("交易图流程完成，最终信号: {}", state.getFinalSignal());
            
            return state;
            
        } catch (Exception e) {
            log.error("交易图执行失败", e);
            return state.toBuilder().finalSignal("ERROR").build();
        }
    }
    
    /**
     * 执行分析师团队
     */
    private AgentState executeAnalysts(AgentState state) {
        log.info("\n【阶段1：分析师团队】");
        
        for (Agent analyst : analysts) {
            state = analyst.execute(state);
        }
        
        log.info("分析师报告: {} 份", state.getAnalystReports().size());
        return state;
    }
    
    /**
     * 执行研究员辩论（带条件判断）
     */
    private AgentState executeDebate(AgentState state) {
        log.info("\n【阶段2：研究员辩论】");
        
        int round = 0;
        while (round < maxDebateRounds * 2) {
            // 判断下一个发言者
            if (conditionalLogic.shouldContinueBullFirst(state)) {
                state = bullResearcher.execute(state);
                state = bearResearcher.execute(state);
            } else {
                state = bearResearcher.execute(state);
                state = bullResearcher.execute(state);
            }
            round += 2;
        }
        
        log.info("辩论完成，观点: {} 个", state.getResearcherViewpoints().size());
        return state;
    }
    
    /**
     * 执行风险辩论（带条件判断）
     */
    private AgentState executeRiskDebate(AgentState state) {
        log.info("\n【阶段5：风险辩论】");
        
        int round = 0;
        while (round < maxRiskDiscussRounds * 3) {
            // 按顺序：激进 -> 保守 -> 中立
            state = aggressiveDebator.execute(state);
            state = conservativeDebator.execute(state);
            state = neutralDebator.execute(state);
            round += 3;
        }
        
        log.info("风险辩论完成");
        return state;
    }
    
    /**
     * 执行反思
     */
    private AgentState executeReflection(AgentState state) {
        log.info("\n【阶段7：反思与学习】");
        
        state = reflectionService.reflectOnAnalysis(state);
        state = reflectionService.reflectOnDecision(state);
        state = reflectionService.comprehensiveReflection(state);
        
        log.info("反思完成: {} 条", state.getReflections().size());
        return state;
    }
    
    /**
     * 获取分析师列表（用于动态配置）
     */
    public List<Agent> getAnalysts() {
        return new ArrayList<>(analysts);
    }
    
    /**
     * 设置最大辩论轮数
     */
    public void setMaxDebateRounds(int rounds) {
        log.info("设置最大辩论轮数: {}", rounds);
    }
}
