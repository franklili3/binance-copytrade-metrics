# 解决n8n中提取leadPortfolioId的问题

## 问题分析

你遇到的错误是因为在n8n的HTML节点中使用了不正确的CSS选择器语法：
```
('script#__APP_DATA').innerHTML).routeProps.data.leadPortfolioId
```

n8n的HTML节点不支持直接使用JavaScript表达式作为选择器，它只支持标准的CSS选择器。

## 解决方案

正确的做法是分步骤提取和处理数据：

### 步骤1：使用HTML节点提取script标签内容

在HTML节点中使用以下配置：
- 操作：使用表达式读取值
- 选择器：`script#__APP_DATA`
- 属性：`innerHTML`

### 步骤2：解析JSON数据

根据你提供的信息，你已经从HTML节点解析了JSON字符串，存储在`$input.first().json.__APP_DATA[0]`中。在这种情况下，你可以直接使用Function节点来提取所需字段：

```javascript
return items.map(item => {
  try {
    // 直接从已解析的数据中获取JSON
    const appData = item.json.__APP_DATA[0];
    
    // 提取leadPortfolioId
    const leadPortfolioId = appData.routeProps.data.leadPortfolioId;
    
    return {
      json: {
        ...item.json,
        leadPortfolioId
      }
    };
  } catch (error) {
    console.error('Error extracting leadPortfolioId:', error);
    return {
      json: {
        ...item.json,
        leadPortfolioId: null
      }
    };
  }
});
```

### 步骤3：提取所需字段

经过步骤2的处理，你现在可以直接使用Set节点提取最终需要的字段：
- 字段名：`leadPortfolioId`
- 值表达式：`={{$json.leadPortfolioId}}`

## 替代方案

如果你发现上述方法仍存在问题，可以尝试使用表达式直接在Set节点中提取数据：

- 字段名：`leadPortfolioId`
- 值表达式：`={{$input.first().json.__APP_DATA[0].routeProps.data.leadPortfolioId}}`

## 总结

关键是要理解n8n HTML节点的限制，它不能直接执行JavaScript表达式，需要分步骤处理：
1. 首先使用CSS选择器提取数据
2. 然后使用其他节点解析和处理提取的数据
3. 最后提取所需的字段