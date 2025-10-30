package io.leavesfly.jtrade.dataflow.provider;

import io.leavesfly.jtrade.config.DataSourceConfig;
import io.leavesfly.jtrade.dataflow.model.MarketData;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Yahoo Finance数据提供者
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class YahooFinanceDataProvider implements DataProvider {
    
    private final DataSourceConfig config;
    
    public YahooFinanceDataProvider(DataSourceConfig config) {
        this.config = config;
    }
    
    @Override
    public List<MarketData> fetchMarketData(String symbol, LocalDate startDate, LocalDate endDate) {
        if (!isEnabled()) {
            log.warn("Yahoo Finance数据源未启用");
            return new ArrayList<>();
        }
        
        log.info("从Yahoo Finance获取 {} 的市场数据，时间范围：{} 至 {}", symbol, startDate, endDate);
        
        // TODO: 实际实现需要调用Yahoo Finance API
        // 这里返回模拟数据
        List<MarketData> dataList = new ArrayList<>();
        
        // 示例：生成一些模拟数据
        for (LocalDate date = startDate; !date.isAfter(endDate); date = date.plusDays(1)) {
            MarketData data = MarketData.builder()
                    .symbol(symbol)
                    .date(date)
                    .open(new BigDecimal("150.00"))
                    .high(new BigDecimal("155.00"))
                    .low(new BigDecimal("148.00"))
                    .close(new BigDecimal("152.00"))
                    .volume(1000000L)
                    .adjustedClose(new BigDecimal("152.00"))
                    .build();
            dataList.add(data);
        }
        
        return dataList;
    }
    
    @Override
    public boolean isEnabled() {
        return config.getYahooFinance().isEnabled();
    }
    
    @Override
    public String getProviderName() {
        return "Yahoo Finance";
    }
}
