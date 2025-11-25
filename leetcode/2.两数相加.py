#
# @lc app=leetcode.cn id=2 lang=python3
#
# [2] 两数相加
#

# @lc code=start
from typing import Optional
# Definition for singly-linked list.
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode], carry: int = 0) -> Optional[ListNode]:
        if l1 is None and l2 is None and carry == 0:
            return None
        s = carry 
        if l1:
            s += l1.val
            l1 = l1.next
        if l2:
            s += l2.val
            l2 = l2.next

        return ListNode(s % 10, self.addTwoNumbers(l1, l2, s // 10))
# @lc code=end   