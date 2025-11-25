/*
 * @lc app=leetcode.cn id=12 lang=java
 *
 * [12] 整数转罗马数字
 */

// @lc code=start
class Solution {
    // 定义罗马数字的基本数值数组，按从大到小排序
    int[] values = {1000, 900,500, 400, 100, 90, 50, 40, 10, 9, 5, 4,1};
    // 对应的罗马数字符号数组
    String[] symbols = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};
    
    /**
     * 将整数转换为罗马数字
     * @param num 要转换的整数
     * @return 转换后的罗马数字字符串
     */
    public String intToRoman(int num) {
        // 使用 StringBuffer 来存储结果，因为会频繁进行字符串拼接
        StringBuffer roman = new StringBuffer();
        // 遍历所有可能的罗马数字值
        for (int i = 0; i < values.length; ++i) {
            int value = values[i];
            String symbol = symbols[i];
            // 当前数字大于等于当前罗马数字值时，需要使用当前的罗马数字符号
            while (num >= value) {
                num -= value;  // 减去已经转换的值
                roman.append(symbol);  // 添加对应的罗马数字符号
            }
            // 如果数字已经转换完毕，提前结束循环

            if (num == 0) {
                break;
            }
        }
        return roman.toString();
    }
}
// @lc code=end

