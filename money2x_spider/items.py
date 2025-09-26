import scrapy


class CopyTraderSnapshotItem(scrapy.Item):
    """Represents a single copy trader snapshot for a lead trader window."""

    lead_trader_id = scrapy.Field()
    performance_days = scrapy.Field()
    time_range = scrapy.Field()
    copy_trader_id = scrapy.Field()
    copy_trader_nickname = scrapy.Field()
    roi = scrapy.Field()
    pnl_usdt = scrapy.Field()
    investment_usdt = scrapy.Field()
    copy_count = scrapy.Field()
    copied_at = scrapy.Field()
    scraped_at = scrapy.Field()
