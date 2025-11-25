#
# @lc app=leetcode.cn id=5 lang=python3
#
# [5] 最长回文子串
#

# @lc code=start
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        ans_left = ans_right = 0

        for i in range(n):
            l = r = i 
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            
            if r - l -1 > ans_right -ans_left:
                ans_left, ans_right = l +1, r
            
        for i in range(n - 1):
            l, r = i, i + 1
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 >ans_right -ans_left:
                ans_left, ans_right = l + 1, r
            
        return s [ans_left: ans_right]
# @lc code=end

