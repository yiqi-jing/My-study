#include <stdio.h>
#include <stdlib.h>

// 定义元素类型
typedef int ElemType;

// 链栈节点
typedef struct LinkNode{
    ElemType data;
    struct LinkNode *next;
}LiStack;

// 初始化链栈（不带头结点）
LiStack *InitLiStack(){
    return NULL;
}

// 入栈（不带头结点，需要传指针的指针）
void PushLiStack(LiStack **s, ElemType e){
    LiStack *p = (LiStack *)malloc(sizeof(LiStack));
    p->data = e;
    p->next = *s;  // 新节点指向原来的栈顶
    *s = p;        // 更新栈顶指针
}

// 出栈（不带头结点）
int PopLiStack(LiStack **s, ElemType *e){
    if(*s == NULL){
        printf("链栈为空\n");
        return 0;
    }
    *e = (*s)->data;
    LiStack *p = *s;
    *s = (*s)->next;  // 更新栈顶指针
    free(p);
    return 1;
}

// 获取栈顶元素
ElemType GetTopLiStack(LiStack *s){
    if(s == NULL){
        printf("链栈为空\n");
        return -1;
    }
    return s->data;
}

// 判空
int IsEmptyLiStack(LiStack *s){
    return s == NULL;
}

// 遍历栈
void TraverseLiStack(LiStack *s){
    printf("栈元素（从栈顶到栈底）: ");
    LiStack *p = s;
    while(p != NULL){
        printf("%d ", p->data);
        p = p->next;
    }
    printf("\n");
}

// 主程序
int main(){
    LiStack *s = InitLiStack();
    
    PushLiStack(&s, 1);
    PushLiStack(&s, 2);
    PushLiStack(&s, 3);
    
    TraverseLiStack(s);
    printf("栈顶元素为：%d\n", GetTopLiStack(s));
    
    ElemType e;
    if(PopLiStack(&s, &e)){
        printf("出栈元素为：%d\n", e);
    }
    
    TraverseLiStack(s);
    printf("栈顶元素为：%d\n", GetTopLiStack(s));
    printf("链栈是否为空：%d\n", IsEmptyLiStack(s));
    
    // 清空栈
    while(!IsEmptyLiStack(s)){
        PopLiStack(&s, &e);
    }
    printf("清空后链栈是否为空：%d\n", IsEmptyLiStack(s));
    
    return 0;
}