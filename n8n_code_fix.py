import json
import re
from bs4 import BeautifulSoup

# 获取输入数据
input_data = _input[0] if _input else None

# 确保有输入数据
if not input_data or 'json' not in input_data:
    raise ValueError("输入数据中没有找到HTML内容")

# 从输入中提取HTML内容
# HTML内容已经在'site-content'中了
html_content = input_data['json']['site-content'][0]

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 找到etf表格（假设表格直接在HTML中，不需要再查找main#site-content）
etf_table = soup.find('table', class_='etf')

# 如果没有找到table.etf，尝试从main#site-content中查找
if not etf_table:
    site_content = soup.find('main', id='site-content')
    if site_content:
        etf_table = site_content.find('table', class_='etf')

# 确保找到了表格
if not etf_table:
    raise ValueError("未找到table.etf元素")

# 解析表格数据
table_data = []

# 获取表头
headers = []
header_rows = etf_table.find('thead').find_all('tr')
header_row = header_rows[-1]  # 获取最后一行表头（包含基金代码）
for th in header_row.find_all(['th', 'td']):
    text = th.get_text(strip=True)
    # 清理文本，移除多余的空白字符
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    headers.append(cleaned_text)

# 添加表头到结果
table_data.append(headers)

# 获取表格主体数据
tbody = etf_table.find('tbody')
if tbody:
    for row in tbody.find_all('tr'):
        row_data = []
        for cell in row.find_all(['td', 'th']):
            # 获取单元格文本并清理
            text = cell.get_text(strip=True)
            # 移除多余的空白字符
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            row_data.append(cleaned_text)
        
        # 只添加非空行
        if any(cell.strip() for cell in row_data):
            table_data.append(row_data)

# 输出结果
output = []
for i, row in enumerate(table_data):
    if i == 0:
        # 表头
        output.append({"type": "header", "data": row})
    else:
        # 数据行
        output.append({"type": "row", "data": row})

# 设置输出
return [{"json": item} for item in output]