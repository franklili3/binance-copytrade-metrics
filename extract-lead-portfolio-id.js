// 在n8n中，你需要使用HTML节点的"操作"选项设置为"使用表达式读取值"
// 然后使用以下表达式来提取leadPortfolioId：

/*
在n8n HTML节点中使用以下设置：

操作: 使用表达式读取值
选择器: script#__APP_DATA
属性: innerHTML
表达式: {{$input.json.$('script#__APP_DATA').innerHTML.match(/window.__APP_DATA__ = (.*?);/)[1]}}
然后在后续节点中使用 JSON 解析和表达式提取所需字段:
{{$json.parsedJson.routeProps.data.leadPortfolioId}}

或者，你可以使用一个函数节点来完成所有操作：
*/

// 函数节点代码：
function extractLeadPortfolioId(html) {
  // 从HTML中找到包含__APP_DATA的script标签
  const regex = /<script id="__APP_DATA"[^>]*>(.*?)<\/script>/s;
  const match = html.match(regex);
  
  if (match && match[1]) {
    try {
      // 解析JSON数据
      const appData = JSON.parse(match[1]);
      // 提取leadPortfolioId
      return appData.routeProps.data.leadPortfolioId;
    } catch (error) {
      console.error('解析JSON时出错:', error);
      return null;
    }
  }
  
  return null;
}

// 使用示例：
// const leadPortfolioId = extractLeadPortfolioId(items[0].json.html);
// return [{json: {leadPortfolioId}}];