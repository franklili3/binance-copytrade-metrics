import csv
import os
from dotenv import load_dotenv
from brightdata import MCP

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取 API_TOKEN
api_token = os.getenv("brightdata_api_token")

# 初始化 MCP 客户端
mcp = MCP(api_token=api_token)

# 定义目标 URL
url = "https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=180D"

# 执行爬取任务
response = mcp.browser(url)

# 解析数据（假设返回 JSON 格式）
data = response.json()

# 定义 CSV 文件的列名
columns = [
    "leadPortfolioId", "favoriteCount", "currentCopyCount", "maxCopyCount", "totalCopyCount",
    "walletBalanceAmount", "walletBalanceAsset", "currentInvestAmount", "currentAvailableAmount",
    "aumAmount", "aumAsset", "badgeName", "badgeCopierCount", "tagName", "tag_days",
    "tag_ranking", "tag_sort", "copyMockCount", "dataUpdatedAt", "datetime"
]

# 保存数据到 CSV 文件
with open("binance_copy_trade_overview.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)

print("数据已保存到 binance_copy_trade_overview.csv")