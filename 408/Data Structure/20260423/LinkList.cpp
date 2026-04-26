// 创建一个单链表
# include<stdio.h>
# include<stdlib.h>

typedef struct LNode{
    int data;
    struct LNode * next;
}LNode, *LinkList;

// 初始化一个不带头结点
LinkList InitList(LinkList *L){
    *L = NULL;
    return *L;
}

// 头插法创建单链表
LinkList List_HeadInsert(LinkList *L){
    InitList(L);
    int x;
    scanf("%d", &x);
    while(x != 9999){
        LNode *s = (LNode *)malloc(sizeof(LNode));
        s->data = x;
        s->next = *L;
        *L = s;
        scanf("%d", &x);
    }
    return *L;
}

// 尾插法创建单链表
LinkList List_TailInsert(LinkList *L){
    InitList(L);
    int x;
    scanf("%d", &x);
    LNode *r = *L;
    while(x != 9999){
        LNode *s = (LNode *)malloc(sizeof(LNode));
        s->data = x;
        if(*L == NULL){
            *L = s;
            r = s;
        } else {
            r->next = s;
            r = s;
        }
        r->next = NULL;
        scanf("%d", &x);
    }
    return *L;
}

// 按位序插入
int ListInsert(LinkList *L, int i, int e){
    if(i < 1) return 0;
    if(i == 1){
        LNode *s = (LNode *)malloc(sizeof(LNode));
        s->data = e;
        s->next = *L;
        *L = s;
        return 1;
    }
    LNode *p = *L;
    int j = 1;
    while(p != NULL && j < i - 1){
        p = p->next;
        j++;
    }
    if(p == NULL) return 0;
    LNode *s = (LNode *)malloc(sizeof(LNode));
    s->data = e;
    s->next = p->next;
    p->next = s;
    return 1;
}

// 按位序删除
int ListDelete(LinkList *L, int i, int *e){
    if(i < 1) return 0;
    if(i == 1){
        if(*L == NULL) return 0;
        LNode *q = *L;
        *e = q->data;
        *L = q->next;
        free(q);
        return 1;
    }
    LNode *p = *L;
    int j = 1;
    while(p != NULL && j < i - 1){
        p = p->next;
        j++;
    }
    if(p == NULL || p->next == NULL) return 0;
    LNode *q = p->next;
    *e = q->data;
    p->next = q->next;
    free(q);
    return 1;
}

// 按值查找
LNode * LocateElem(LinkList L, int e){
    LNode *p = L;
    while(p != NULL && p->data != e){
        p = p->next;
    }
    return p;
}

// 按位查找
LNode * GetElem(LinkList L, int i){
    if(i < 1) return NULL;
    LNode *p = L;
    int j = 1;
    while(p != NULL && j < i){
        p = p->next;
        j++;
    }
    return p;
}

// 求表长
int Length(LinkList L){
    int len = 0;
    LNode *p = L;
    while(p != NULL){
        p = p->next;
        len++;
    }
    return len;
}

// 打印链表
void PrintList(LinkList L){
    LNode *p = L;
    printf("链表元素: ");
    while(p != NULL){
        printf("%d ", p->data);
        p = p->next;
    }
    printf("\n");
}

// 销毁链表
void DestroyList(LinkList *L){
    LNode *p = *L;
    while(p != NULL){
        LNode *q = p;
        p = p->next;
        free(q);
    }
    *L = NULL;
}

// 主函数，测试链表操作
int main(){
    LinkList L1, L2;
    int e, i;
    
    printf("=== 测试头插法创建链表 ===\n");
    printf("请输入链表元素（输入9999结束）: ");
    List_HeadInsert(&L1);
    PrintList(L1);
    printf("链表长度: %d\n", Length(L1));
    
    printf("\n=== 测试尾插法创建链表 ===\n");
    printf("请输入链表元素（输入9999结束）: ");
    List_TailInsert(&L2);
    PrintList(L2);
    printf("链表长度: %d\n", Length(L2));
    
    printf("\n=== 测试按位序插入 ===\n");
    printf("请输入插入位置和元素: ");
    scanf("%d %d", &i, &e);
    if(ListInsert(&L1, i, e)){
        printf("插入成功！");
        PrintList(L1);
    } else {
        printf("插入失败！");
    }
    
    printf("\n=== 测试按位序删除 ===\n");
    printf("请输入删除位置: ");
    scanf("%d", &i);
    if(ListDelete(&L1, i, &e)){
        printf("删除成功！删除的元素是: %d", e);
        PrintList(L1);
    } else {
        printf("删除失败！");
    }
    
    printf("\n=== 测试按值查找 ===\n");
    printf("请输入要查找的元素: ");
    scanf("%d", &e);
    LNode *p = LocateElem(L1, e);
    if(p != NULL){
        printf("找到元素 %d\n", p->data);
    } else {
        printf("未找到元素 %d\n", e);
    }
    
    printf("\n=== 测试按位查找 ===\n");
    printf("请输入要查找的位置: ");
    scanf("%d", &i);
    p = GetElem(L1, i);
    if(p != NULL){
        printf("位置 %d 的元素是: %d\n", i, p->data);
    } else {
        printf("位置 %d 不存在\n", i);
    }
    
    printf("\n=== 销毁链表 ===\n");
    DestroyList(&L1);
    DestroyList(&L2);
    printf("链表已销毁\n");
    
    return 0;
}
