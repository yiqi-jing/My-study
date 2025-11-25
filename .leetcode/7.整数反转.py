#
# @lc app=leetcode.cn id=7 lang=python3
#
# [7] 整数反转
#

# @lc code=start
class Solution:
    def reverse(self, x: int) -> int:
        # INT_MIN, INT_MAX = -2**31, 2**31 - 1

        # rev = 0
        # while x != 0:
        #     if rev < INT_MIN // 10 + 1 or rev >INT_MAX // 10:
        #         return 0
        #     digit = x % 10
        #     if x < 0 and digit > 0:
        #         digit -= 10

        #     x = (x - digit) // 10
        #     rev = rev * 10 + digit
        # return rev
        chars = list(str(x))

        l = 1 if chars[0] == '-' else 0
        r = len(chars) - 1

        while l < r:
            chars[l], chars[r] = chars[r], chars[l]
            l += 1
            r -= 1

        reversed_int  = int(''.join(chars))

        if reversed_int < -2**31 or reversed_int > 2**31 - 1:
            return 0
        return reversed_int 
# @lc code=end

