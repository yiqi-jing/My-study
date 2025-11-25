#
# @lc app=leetcode.cn id=9 lang=python3
#
# [9] 回文数
#

# @lc code=start
class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0 or x > 0 and x % 10 ==0:
            return False
        rev = 0
        while rev < x // 10:
            rev = rev * 10 + x % 10
            x //= 10
        return rev == x or rev ==x // 10
# @lc code=end

