## 1.用brightdata-unlocker-mcp server 爬取币安现货带单项目主要数据，保存为markdown文件
URL：https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=180D
### 1.1 爬取概览信息
data schema: 
table name:binance_copy_trade_overview
columns:leadPortfolioId	favoriteCount	currentCopyCount	maxCopyCount	totalCopyCount	walletBalanceAmount	walletBalanceAsset	currentInvestAmount	currentAvailableAmount	aumAmount	aumAsset	badgeName	badgeCopierCount	tagName	tag_days	tag_ranking	tag_sort	copyMockCount	dataUpdatedAt	datetime
### 1.2 爬取180天业绩信息
data schema:
table name:binance_copy_trade_performance
columns:leadPortfolioId	timeRange	roi	pnl	mdd	copierPnl	winRate	winDays	sharpRatio	dataUpdatedAt	datetime
### 1.3 爬取持仓信息
点击 Holdings ，获取持仓信息
data schema:
table name:binance_copy_trade_holdings
columns:leadPortfolioId	Assets	Time_Updated	Remain_Amount	Buy_Amount	Avg_Buy_Price	Last_Price	Unrealized_PNL	Realized_PNL
### 1.4 爬取交易信息
点击 Trade History ，获取交易信息
data schema:
table name:binance_copy_trade_history
columns:leadPortfolioId	Time	Pair	Side	Executed	Role	Total
### 1.5 爬取余额信息
点击 Balance History ，获取余额信息
data schema:
table name:binance_copy_trade_balances_history
columns:leadPortfolioId	Coin	Time	Amount	From	To
### 1.6 爬取跟单者信息
点击 Copy Traders , 获取跟单者信息
data schema:
table name:binance_copy_traders
columns:leadPortfolioId	User_ID	Amount	Total_PNL	Total_ROI	Duration
## 2.用brightdata browser api 爬取币安带单项目90天业绩数据
URL：https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=90D
### 2.1 爬取90天业绩信息
data schema:
table name:binance_copy_trade_performance
columns:leadPortfolioId	timeRange	roi	pnl	mdd	copierPnl	winRate	winDays	sharpRatio	dataUpdatedAt	datetime
## 3.用brightdata browser api 爬取币安带单项目30天业绩数据
URL：https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=30D
### 3.1 爬取30天业绩信息
data schema:
table name:binance_copy_trade_performance
columns:leadPortfolioId	timeRange	roi	pnl	mdd	copierPnl	winRate	winDays	sharpRatio	dataUpdatedAt	datetime
## 4.用brightdata browser api 爬取币安带单项目7天业绩数据
URL：https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=7D
### 4.1 爬取7天业绩信息
data schema:
table name:binance_copy_trade_performance
columns:leadPortfolioId	timeRange	roi	pnl	mdd	copierPnl	winRate	winDays	sharpRatio	dataUpdatedAt	datetime

