import json

def parse_app_data(input_data):
    """
    解析n8n中$input.first().json.__APP_DATA[0]字符串
    
    Args:
        input_data: 从n8n获取的包含__APP_DATA的JSON字符串
        
    Returns:
        dict: 解析后的数据，包含leadPortfolioId
    """
    try:
        # 如果input_data是字符串，则解析它
        if isinstance(input_data, str):
            app_data = json.loads(input_data)
        else:
            # 如果已经是字典对象，则直接使用
            app_data = input_data
            
        # 提取leadPortfolioId
        lead_portfolio_id = app_data.get('routeProps', {}).get('data', {}).get('leadPortfolioId')
        
        return {
            'leadPortfolioId': lead_portfolio_id,
            'appData': app_data
        }
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return None

# 示例用法
if __name__ == "__main__":
    # 模拟从n8n获取的数据
    # 你需要将这里替换为实际的$input.first().json.__APP_DATA[0]数据
    sample_data = {
        "routeProps": {
            "data": {
                "leadPortfolioId": "123456789",
                "otherData": "example"
            }
        }
    }
    
    result = parse_app_data(sample_data)
    if result:
        print(f"提取的leadPortfolioId: {result['leadPortfolioId']}")
    else:
        print("无法提取leadPortfolioId")