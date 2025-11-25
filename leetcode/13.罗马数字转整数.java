/*
 * @lc app=leetcode.cn id=13 lang=java
 *
 * [13] 罗马数字转整数
 */

// @lc code=start
class Solution {
    // 单个罗马数字到整数的映射
    private static final Map<Character, Integer> ROMAN = Map.of(
        'I', 1,
        'V', 5,
        'X', 10,
        'L', 50,
        'C', 100,
        'D', 500,
        'M', 1000
    );

    public int romanToInt(String S) {
        char[] s = S.toCharArray(); // 也可以下面用 charAt，从而保证空间复杂度是 O(1)
        int n = s.length;
        int ans = 0;
        for (int i = 0; i < n - 1; i++) { // 遍历 s
            int x = ROMAN.get(s[i]);
            int y = ROMAN.get(s[i + 1]);
            ans += x < y ? -x : x; // 累加 x 的数值，y 只是用来辅助判断 x 的正负
        }
        return ans + ROMAN.get(s[n - 1]); // 加上最后一个罗马数字
    }
}
// @lc code=end

