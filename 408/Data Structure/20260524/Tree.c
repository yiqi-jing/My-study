#include <stdio.h>
#include <stdlib.h>

// 二叉树结点结构定义
typedef struct BiTNode {
    char data;                    // 数据域
    struct BiTNode *lchild, *rchild;  // 左、右孩子指针
} BiTNode, *BiTree;

// 孩子兄弟表示法的树/森林结点结构定义
typedef struct CSNode {
    char data;                    // 数据域
    struct CSNode *firstchild, *nextsibling;  // 第一个孩子、右兄弟指针
} CSNode, *CSTree;

// 链式队列结点结构
typedef struct LinkNode {
    BiTree data;                  // 数据域（二叉树结点指针）
    struct LinkNode *next;        // 指针域
} LinkNode;

// 链式队列结构
typedef struct {
    LinkNode *front, *rear;       // 队头、队尾指针
} LinkQueue;

// 链式栈结点结构
typedef struct StackNode {
    BiTree data;                  // 数据域（二叉树结点指针）
    struct StackNode *next;       // 指针域
} StackNode, *LinkStack;

// 先序创建二叉树（空结点用#表示）
BiTree CreateBiTree() {
    char ch;
    scanf("%c", &ch);             // 输入一个字符
    if (ch == '#') {              // 如果是#，表示空结点
        return NULL;
    }
    BiTree T = (BiTree)malloc(sizeof(BiTNode));  // 分配内存
    T->data = ch;                 // 赋值数据
    T->lchild = CreateBiTree();   // 递归创建左子树
    T->rchild = CreateBiTree();   // 递归创建右子树
    return T;
}

// 二叉树前序遍历（递归）
void PreOrder(BiTree T) {
    if (T) {
        printf("%c ", T->data);   // 访问根结点
        PreOrder(T->lchild);      // 递归遍历左子树
        PreOrder(T->rchild);      // 递归遍历右子树
    }
}

// 二叉树中序遍历（递归）
void InOrder(BiTree T) {
    if (T) {
        InOrder(T->lchild);       // 递归遍历左子树
        printf("%c ", T->data);   // 访问根结点
        InOrder(T->rchild);       // 递归遍历右子树
    }
}

// 二叉树后序遍历（递归）
void PostOrder(BiTree T) {
    if (T) {
        PostOrder(T->lchild);     // 递归遍历左子树
        PostOrder(T->rchild);     // 递归遍历右子树
        printf("%c ", T->data);   // 访问根结点
    }
}

// 初始化链式栈
void InitStack(LinkStack *S) {
    *S = NULL;                    // 栈顶指针置空
}

// 判断栈是否为空
int StackEmpty(LinkStack S) {
    return S == NULL;
}

// 入栈操作
void Push(LinkStack *S, BiTree e) {
    StackNode *p = (StackNode*)malloc(sizeof(StackNode));  // 分配新结点
    p->data = e;                 // 赋值
    p->next = *S;                // 新结点指向原栈顶
    *S = p;                      // 更新栈顶指针
}

// 出栈操作
int Pop(LinkStack *S, BiTree *e) {
    if (*S == NULL) return 0;    // 栈空，返回失败
    StackNode *p = *S;           // p指向栈顶
    *e = p->data;                // 取出栈顶元素
    *S = p->next;                // 更新栈顶
    free(p);                     // 释放内存
    return 1;
}

// 获取栈顶元素
int GetTop(LinkStack S, BiTree *e) {
    if (S == NULL) return 0;     // 栈空
    *e = S->data;                // 取栈顶
    return 1;
}

// 二叉树前序遍历（非递归，使用栈）
void PreOrder2(BiTree T) {
    LinkStack S;
    InitStack(&S);
    BiTree p = T;
    while (p || !StackEmpty(S)) {
        if (p) {                  // 结点非空
            printf("%c ", p->data);  // 访问结点
            Push(&S, p);         // 入栈
            p = p->lchild;       // 向左走
        } else {
            Pop(&S, &p);         // 出栈
            p = p->rchild;       // 转向右子树
        }
    }
}

// 二叉树中序遍历（非递归，使用栈）
void InOrder2(BiTree T) {
    LinkStack S;
    InitStack(&S);
    BiTree p = T;
    while (p || !StackEmpty(S)) {
        if (p) {
            Push(&S, p);         // 入栈
            p = p->lchild;       // 向左走
        } else {
            Pop(&S, &p);         // 出栈
            printf("%c ", p->data);  // 访问结点
            p = p->rchild;       // 转向右子树
        }
    }
}

// 二叉树后序遍历（非递归，使用栈）
void PostOrder2(BiTree T) {
    LinkStack S;
    InitStack(&S);
    BiTree p = T;
    BiTree r = NULL;             // 辅助指针，记录上一个访问的结点
    while (p || !StackEmpty(S)) {
        if (p) {
            Push(&S, p);         // 入栈
            p = p->lchild;       // 向左走
        } else {
            GetTop(S, &p);       // 查看栈顶
            // 如果右孩子存在且未访问过
            if (p->rchild && p->rchild != r) {
                p = p->rchild;   // 转向右子树
            } else {
                Pop(&S, &p);     // 出栈
                printf("%c ", p->data);  // 访问结点
                r = p;           // 记录已访问
                p = NULL;        // p置空，继续循环
            }
        }
    }
}

// 初始化链式队列
void InitQueue(LinkQueue *Q) {
    Q->front = Q->rear = (LinkNode*)malloc(sizeof(LinkNode));  // 创建头结点
    Q->front->next = NULL;       // 头结点指针域置空
}

// 判断队列是否为空
int QueueEmpty(LinkQueue Q) {
    return Q.front == Q.rear;    // 头尾指针相同则为空
}

// 入队操作
void EnQueue(LinkQueue *Q, BiTree e) {
    LinkNode *p = (LinkNode*)malloc(sizeof(LinkNode));  // 分配新结点
    p->data = e;                 // 赋值
    p->next = NULL;
    Q->rear->next = p;           // 新结点插入队尾
    Q->rear = p;                 // 更新队尾指针
}

// 出队操作
int DeQueue(LinkQueue *Q, BiTree *e) {
    if (Q->front == Q->rear) return 0;  // 队空
    LinkNode *p = Q->front->next;  // p指向队头结点
    *e = p->data;                // 取出数据
    Q->front->next = p->next;    // 头结点指向下一结点
    if (Q->rear == p) Q->rear = Q->front;  // 如果是最后一个结点，更新队尾
    free(p);                     // 释放内存
    return 1;
}

// 二叉树层序遍历（使用队列）
void LevelOrder(BiTree T) {
    LinkQueue Q;
    InitQueue(&Q);
    BiTree p;
    if (T) EnQueue(&Q, T);       // 根结点入队
    while (!QueueEmpty(Q)) {
        DeQueue(&Q, &p);         // 出队
        printf("%c ", p->data);  // 访问
        if (p->lchild) EnQueue(&Q, p->lchild);  // 左孩子入队
        if (p->rchild) EnQueue(&Q, p->rchild);  // 右孩子入队
    }
}

// 先序创建孩子兄弟表示法的树/森林（空结点用#表示）
CSTree CreateCSTree() {
    char ch;
    scanf(" %c", &ch);           // 输入一个字符（注意前面的空格，跳过换行）
    if (ch == '#') {
        return NULL;
    }
    CSTree T = (CSTree)malloc(sizeof(CSNode));
    T->data = ch;
    T->firstchild = CreateCSTree();  // 递归创建第一个孩子
    T->nextsibling = CreateCSTree(); // 递归创建右兄弟
    return T;
}

// 森林的前序遍历（对应二叉树的前序遍历）
void ForestPreOrder(CSTree T) {
    if (T) {
        printf("%c ", T->data);  // 访问根结点
        ForestPreOrder(T->firstchild);  // 访问孩子
        ForestPreOrder(T->nextsibling); // 访问兄弟
    }
}

// 森林的中序遍历（对应二叉树的中序遍历）
void ForestInOrder(CSTree T) {
    if (T) {
        ForestInOrder(T->firstchild);  // 访问孩子
        printf("%c ", T->data);        // 访问根结点
        ForestInOrder(T->nextsibling); // 访问兄弟
    }
}

int main() {
    printf("请输入二叉树的先序序列（空节点用#表示）：\n");
    BiTree T = CreateBiTree();
    
    printf("\n二叉树遍历结果：\n");
    printf("前序遍历（递归）："); PreOrder(T); printf("\n");
    printf("前序遍历（非递归）："); PreOrder2(T); printf("\n");
    printf("中序遍历（递归）："); InOrder(T); printf("\n");
    printf("中序遍历（非递归）："); InOrder2(T); printf("\n");
    printf("后序遍历（递归）："); PostOrder(T); printf("\n");
    printf("后序遍历（非递归）："); PostOrder2(T); printf("\n");
    printf("层序遍历："); LevelOrder(T); printf("\n");
    
    printf("\n请输入森林的孩子兄弟表示法序列（空节点用#表示）：\n");
    CSTree F = CreateCSTree();
    
    printf("\n森林遍历结果：\n");
    printf("前序遍历："); ForestPreOrder(F); printf("\n");
    printf("中序遍历："); ForestInOrder(F); printf("\n");
    
    return 0;
}
