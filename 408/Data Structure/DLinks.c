#include <stdio.h>
#include <stdlib.h>

// 定义双链表节点结构
typedef struct Node {
    int data;
    struct Node *prior;
    struct Node *next;
} Node, *DLinkList;

// 初始化循环双链表（带头结点）
int InitList(DLinkList *L) {
    *L = (DLinkList)malloc(sizeof(Node));
    if (*L == NULL) return 0; // 内存分配失败
    
    (*L)->prior = *L; // 头结点的prior指向自己
    (*L)->next = *L;  // 头结点的next指向自己
    return 1;
}

// 在第i个位置插入元素e
int ListInsert(DLinkList L, int i, int e) {
    if (i < 1) return 0; // 位置不合法
    
    DLinkList p = L;
    int j = 0;
    
    // 找到第i-1个节点
    while (p->next != L && j < i - 1) {
        p = p->next;
        j++;
    }
    
    if (j < i - 1) return 0; // i超过表长
    
    // 创建新节点
    DLinkList s = (DLinkList)malloc(sizeof(Node));
    if (s == NULL) return 0; // 内存分配失败
    
    s->data = e;
    s->prior = p;
    s->next = p->next;
    p->next->prior = s;
    p->next = s;
    
    return 1;
}

// 删除第i个位置的元素，并用e返回其值
int ListDelete(DLinkList L, int i, int *e) {
    if (i < 1) return 0; // 位置不合法
    
    DLinkList p = L;
    int j = 0;
    
    // 找到第i个节点
    while (p->next != L && j < i) {
        p = p->next;
        j++;
    }
    
    if (j < i) return 0; // i超过表长
    
    *e = p->data;
    p->prior->next = p->next;
    p->next->prior = p->prior;
    free(p);
    
    return 1;
}

// 打印循环双链表
void PrintList(DLinkList L) {
    DLinkList p = L->next; // 跳过头结点
    
    printf("循环双链表: ");
    while (p != L) {
        printf("%d ", p->data);
        p = p->next;
    }
    printf("\n");
}

// 销毁循环双链表
void DestroyList(DLinkList *L) {
    DLinkList p = (*L)->next;
    DLinkList q;
    
    while (p != *L) {
        q = p->next;
        free(p);
        p = q;
    }
    
    free(*L);
    *L = NULL;
}

int main() {
    DLinkList L;
    
    // 初始化
    if (InitList(&L)) {
        printf("循环双链表初始化成功\n");
    } else {
        printf("初始化失败\n");
        return 0;
    }
    
    // 插入元素
    ListInsert(L, 1, 10);
    ListInsert(L, 2, 20);
    ListInsert(L, 3, 30);
    ListInsert(L, 2, 15); // 在第2个位置插入15
    
    // 打印链表
    PrintList(L);
    
    // 删除元素
    int e;
    if (ListDelete(L, 2, &e)) {
        printf("删除的元素: %d\n", e);
    } else {
        printf("删除失败\n");
    }
    
    // 再次打印链表
    PrintList(L);
    
    // 销毁链表
    DestroyList(&L);
    
    return 0;
}
