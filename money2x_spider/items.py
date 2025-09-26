import scrapy


class CopyTradeOverviewItem(scrapy.Item):
    """Snapshot of the lead trader level metrics for a scrape run."""

    lead_trader_id = scrapy.Field()
    scraped_date = scrapy.Field()
    scraped_at = scrapy.Field()
    copiers = scrapy.Field()
    aum_usdt = scrapy.Field()
    leading_balance_usdt = scrapy.Field()
    mock_copiers = scrapy.Field()


class CopyTradePerformanceItem(scrapy.Item):
    """Performance metrics for a specific lead trader time window."""

    lead_trader_id = scrapy.Field()
    scraped_date = scrapy.Field()
    scraped_at = scrapy.Field()
    performance_days = scrapy.Field()
    roi = scrapy.Field()
    pnl_usdt = scrapy.Field()
    copier_pnl_usdt = scrapy.Field()
    sharpe_ratio = scrapy.Field()
    mdd = scrapy.Field()
    win_rate = scrapy.Field()
    win_days = scrapy.Field()


class CopyTradeFollowerItem(scrapy.Item):
    """Single copy trader enrolment for the given lead trader."""

    lead_trader_id = scrapy.Field()
    duration = scrapy.Field()
    user_id = scrapy.Field()
    amount = scrapy.Field()
    total_pnl = scrapy.Field()
    total_roi = scrapy.Field()
    created_date = scrapy.Field()
