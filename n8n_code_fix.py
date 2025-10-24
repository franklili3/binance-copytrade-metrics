import json

# 获取输入数据
input_data = _input.first().json.__APP_DATA[0]

try:
    # 如果input_data是字符串，则解析它
    if isinstance(input_data, str):
        app_data = json.loads(input_data)
    else:
        # 如果已经是字典对象，则直接使用
        app_data = input_data
        
    # 提取leadPortfolioId
    lead_portfolio_id = app_data.get('routeProps', {}).get('data', {}).get('leadPortfolioId')
    
    # 创建输出数据
    output_items = []
    for item in _input.all():
        # 复制原始项目
        new_item = item.clone()
        # 添加新字段
        new_item.json['leadPortfolioId'] = lead_portfolio_id
        output_items.append(new_item)
    
    return output_items
    
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
    return _input.all()
except Exception as e:
    print(f"处理数据时出错: {e}")
    return _input.all()