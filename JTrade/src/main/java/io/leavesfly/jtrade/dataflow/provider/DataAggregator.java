package io.leavesfly.jtrade.dataflow.provider;

import io.leavesfly.jtrade.dataflow.model.FundamentalData;
import io.leavesfly.jtrade.dataflow.model.MarketData;
import io.leavesfly.jtrade.dataflow.model.NewsData;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 数据聚合器
 * 
 * 从多个数据源聚合数据，提供统一的数据访问接口
 * 
 * @author 山泽
 */
@Slf4j
@Component
public class DataAggregator {
    
    private final List<DataProvider> dataProviders;
    private final FinnhubDataProvider finnhubDataProvider;
    
    public DataAggregator(List<DataProvider> dataProviders, 
                         FinnhubDataProvider finnhubDataProvider) {
        this.dataProviders = dataProviders;
        this.finnhubDataProvider = finnhubDataProvider;
    }
    
    /**
     * 获取市场数据
     */
    public List<MarketData> getMarketData(String symbol, LocalDate startDate, LocalDate endDate) {
        for (DataProvider provider : dataProviders) {
            if (provider.isEnabled()) {
                try {
                    List<MarketData> data = provider.fetchMarketData(symbol, startDate, endDate);
                    if (!data.isEmpty()) {
                        log.info("从 {} 成功获取市场数据", provider.getProviderName());
                        return data;
                    }
                } catch (Exception e) {
                    log.error("从 {} 获取数据失败", provider.getProviderName(), e);
                }
            }
        }
        
        log.warn("未能从任何数据源获取到市场数据");
        return new ArrayList<>();
    }
    
    /**
     * 获取基本面数据（模拟）
     */
    public FundamentalData getFundamentalData(String symbol) {
        log.info("获取 {} 的基本面数据", symbol);
        
        // TODO: 实际实现需要调用真实API
        return FundamentalData.builder()
                .symbol(symbol)
                .companyName(symbol + " Inc.")
                .marketCap(new BigDecimal("1000000000"))
                .peRatio(new BigDecimal("25.5"))
                .pbRatio(new BigDecimal("3.2"))
                .dividendYield(new BigDecimal("2.5"))
                .eps(new BigDecimal("6.0"))
                .build();
    }
    
    /**
     * 获取新闻数据（真实API）
     */
    public List<NewsData> getNewsData(String symbol, int limit) {
        log.info("获取 {} 的新闻数据，限制 {} 条", symbol, limit);
        
        // 先尝试使用Finnhub获取真实新闻
        if (finnhubDataProvider.isEnabled()) {
            try {
                LocalDate toDate = LocalDate.now();
                LocalDate fromDate = toDate.minusDays(7); // 过去7天
                List<NewsData> news = finnhubDataProvider.fetchNews(symbol, fromDate, toDate);
                
                if (!news.isEmpty()) {
                    // 限制数量
                    return news.stream()
                            .limit(limit)
                            .collect(java.util.stream.Collectors.toList());
                }
            } catch (Exception e) {
                log.error("从Finnhub获取新闻失败", e);
            }
        }
        
        // 如果真实API失败，使用模拟数据
        log.info("使用模拟新闻数据");
        List<NewsData> newsList = new ArrayList<>();
        
        for (int i = 0; i < limit; i++) {
            NewsData news = NewsData.builder()
                    .title(symbol + " 股价波动分析")
                    .source("财经新闻")
                    .url("https://example.com/news/" + i)
                    .publishedAt(LocalDate.now().atStartOfDay())
                    .summary("这是一条关于 " + symbol + " 的模拟新闻")
                    .sentimentScore(0.5)
                    .build();
            newsList.add(news);
        }
        
        return newsList;
    }
    
    /**
     * 获取社交媒体情绪数据（模拟）
     */
    public Map<String, Object> getSocialMediaSentiment(String symbol) {
        log.info("获取 {} 的社交媒体情绪数据", symbol);
        
        // TODO: 实际实现需要调用Reddit/Twitter API
        Map<String, Object> sentiment = new HashMap<>();
        sentiment.put("symbol", symbol);
        sentiment.put("overall_sentiment", 0.6);
        sentiment.put("positive_ratio", 0.65);
        sentiment.put("negative_ratio", 0.35);
        sentiment.put("post_count", 150);
        
        return sentiment;
    }
    
    /**
     * 获取技术指标数据（模拟）
     */
    public Map<String, Double> getTechnicalIndicators(String symbol) {
        log.info("获取 {} 的技术指标数据", symbol);
        
        // TODO: 实际实现需要计算真实技术指标
        Map<String, Double> indicators = new HashMap<>();
        indicators.put("RSI", 55.0);
        indicators.put("MACD", 1.5);
        indicators.put("SMA_20", 150.0);
        indicators.put("SMA_50", 148.0);
        indicators.put("BB_UPPER", 160.0);
        indicators.put("BB_LOWER", 140.0);
        
        return indicators;
    }
}
