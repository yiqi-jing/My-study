#
# @lc app=leetcode.cn id=19 lang=python3
#
# [19] 删除链表的倒数第 N 个结点
#

# @lc code=start
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

# 定义链表节点类
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        # 创建虚拟头节点
        dummy = ListNode(0, head)
        fast = slow = dummy
        
        # 快指针先移动n步
        for _ in range(n):
            fast = fast.next
        
        # 快慢指针同时移动，直到快指针到达末尾
        while fast.next:
            fast = fast.next
            slow = slow.next
        
        # 删除目标节点
        slow.next = slow.next.next
        
        # 返回新的头节点（虚拟头节点的下一个节点）
        return dummy.next   
# @lc code=end

