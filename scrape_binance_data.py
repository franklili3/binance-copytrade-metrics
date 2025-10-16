import os
import asyncio
from dotenv import load_dotenv
import json
from brightdata import BrowserAPI

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取 API_TOKEN
api_token = os.getenv("brightdata_api_token")

# 定义目标 URL
url = "https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=180D"

async def interact_with_page(browser_api, tab_xpath):
    try:
        # 点击标签页 (使用BrowserAPI的CDP功能)
        await browser_api.cdp_send('Runtime.evaluate', {
            'expression': f'document.evaluate("{tab_xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()'
        })
        await asyncio.sleep(2)  # 等待加载

        # 滚动到页面底部以加载更多内容
        await browser_api.cdp_send('Runtime.evaluate', {
            'expression': 'window.scrollTo(0, document.body.scrollHeight)'
        })
        await asyncio.sleep(2)

        # 提取数据
        result = await browser_api.cdp_send('Runtime.evaluate', {
            'expression': 'document.documentElement.outerHTML'
        })
        return result.get('result', {}).get('value', '')
    except Exception as e:
        print(f"无法与页面交互: {e}")
        return "暂无数据"

async def main():
    if not api_token or api_token == 'SBR_USERNAME:SBR_PASSWORD':
        raise Exception("请在.env文件中提供完整的BrightData认证信息（格式：用户名:密码）")

    print("连接到 Browser...")
    
    # 使用BrightData BrowserAPI
    browser_api = BrowserAPI(api_token=api_token)
    
    try:
        print(f"已连接! 正在导航到 {url}...")
        await browser_api.navigate(url)
        print("导航完成! 正在抓取页面内容...")

        # 提取 Holdings 数据
        holdings_data = await interact_with_page(browser_api, "//*[@id='bn-tab-0']")

        # 提取 Trade History 数据
        trade_history_data = await interact_with_page(browser_api, "//*[@id='bn-tab-1']")

        # 提取 Balance History 数据
        balance_history_data = await interact_with_page(browser_api, "//*[@id='bn-tab-2']")

        # 提取 Copy Traders 数据
        copy_traders_data = await interact_with_page(browser_api, "//*[@id='bn-tab-3']")

        # 保存为 JSON 文件
        data = {
            "Holdings": holdings_data,
            "Trade History": trade_history_data,
            "Balance History": balance_history_data,
            "Copy Traders": copy_traders_data
        }

        with open("binance-copytrade-metrics3.json", "w") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            
        print("抓取完成! 数据已保存到 binance-copytrade-metrics3.json")

    finally:
        await browser_api.close()
        print("浏览器已关闭")

if __name__ == "__main__":
    asyncio.run(main())