import os
import sys


BOT_NAME = "money2x_spider"

SPIDER_MODULES = ["money2x_spider.spiders"]
NEWSPIDER_MODULE = "money2x_spider.spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 0.5
RETRY_TIMES = 2

# 在Windows上为Python 3.8+设置事件循环策略
if sys.platform == "win32" and sys.version_info >= (3, 8):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
_launch_options = {"headless": True}
_headless_flag = os.environ.get("PLAYWRIGHT_HEADLESS_FLAG", "--headless=new")
if _headless_flag:
    existing_args = list(_launch_options.get("args", []))
    existing_args.append(_headless_flag)
    existing_args.append("--ignore-certificate-errors")
    _launch_options["args"] = existing_args
_executable_path = os.environ.get("PLAYWRIGHT_EXECUTABLE_PATH")
if _executable_path:
    _launch_options["executable_path"] = _executable_path
PLAYWRIGHT_LAUNCH_OPTIONS = _launch_options

ITEM_PIPELINES = {"money2x_spider.pipelines.ValidationPipeline": 300}

LOG_LEVEL = "INFO"