/**
 * 将时间戳转换为日期时间格式
 * @param {number} timestamp - 时间戳（毫秒或秒）
 * @returns {string} 格式化的日期时间字符串
 */
function convertTimestampToDateTime(timestamp) {
    // 检查时间戳单位，如果小于1e12则认为是秒单位，否则是毫秒单位
    const date = timestamp < 1e12 ? new Date(timestamp * 1000) : new Date(timestamp);
    
    // 转换为本地时间格式字符串
    return date.toLocaleString();
}

/**
 * 将时间戳转换为ISO格式的日期时间
 * @param {number} timestamp - 时间戳（毫秒或秒）
 * @returns {string} ISO格式的日期时间字符串
 */
function convertTimestampToISO(timestamp) {
    const date = timestamp < 1e12 ? new Date(timestamp * 1000) : new Date(timestamp);
    return date.toISOString();
}

/**
 * 将时间戳转换为自定义格式的日期时间
 * @param {number} timestamp - 时间戳（毫秒或秒）
 * @returns {string} 自定义格式的日期时间字符串 (YYYY-MM-DD HH:mm:ss)
 */
function convertTimestampToCustomFormat(timestamp) {
    const date = timestamp < 1e12 ? new Date(timestamp * 1000) : new Date(timestamp);
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 使用示例
// const timestamp = 1678886400; // 示例时间戳
// console.log(convertTimestampToDateTime(timestamp));
// console.log(convertTimestampToISO(timestamp));
// console.log(convertTimestampToCustomFormat(timestamp));

module.exports = {
    convertTimestampToDateTime,
    convertTimestampToISO,
    convertTimestampToCustomFormat
};