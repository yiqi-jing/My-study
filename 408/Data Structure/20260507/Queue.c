/**
 * 循环队列6种实现方式对比 - 408数据结构复习专用
 * 
 * 核心问题：循环队列如何区分"队空"和"队满"状态？
 * 因为两种状态都可能表现为 front == rear，需要额外区分手段。
 * 
 * 分类体系：
 * ┌─────────────────────────────────────────────────────────────┐
 * │ 第一维度：rear指针的含义                                    │
 * │   1. rear指向队尾元素的后一个位置（更常用）                   │
 * │   2. rear指向队尾元素本身                                     │
 * ├─────────────────────────────────────────────────────────────┤
 * │ 第二维度：判空/判满的区分方法                                │
 * │   a. 牺牲一个存储空间（经典方法）                            │
 * │   b. 增加size变量记录队列长度（最直观，推荐）                 │
 * │   c. 增加tag标记（记录最近一次操作类型）                      │
 * └─────────────────────────────────────────────────────────────┘
 * 
 * 组合结果：6种方式 = 2（rear含义） × 3（区分方法）
 */

#include <stdio.h>

#define MaxSize 10  // 队列最大容量
#define SUCCESS 1   // 操作成功返回值
#define FAILURE 0   // 操作失败返回值

// ============================================================================
// 方式1a：rear指向队尾后一个位置 + 牺牲一个存储空间
// 判空：front == rear
// 判满：(rear + 1) % MaxSize == front
// 特点：无需额外字段，但浪费1个存储单元
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素的后一个位置
} Queue1a;

/**
 * @brief 初始化队列
 * @param Q 队列指针
 */
void InitQueue1a(Queue1a *Q) {
    if (Q == NULL) return;  // 健壮性检查：防止空指针
    Q->front = Q->rear = 0;
}

/**
 * @brief 判断队列是否为空
 * @param Q 队列
 * @return SUCCESS(1) 为空, FAILURE(0) 不为空
 */
int IsEmpty1a(Queue1a Q) {
    return Q.front == Q.rear;
}

/**
 * @brief 判断队列是否为满
 * @param Q 队列
 * @return SUCCESS(1) 已满, FAILURE(0) 未满
 */
int IsFull1a(Queue1a Q) {
    return (Q.rear + 1) % MaxSize == Q.front;
}

/**
 * @brief 入队操作
 * @param Q 队列指针
 * @param x 待入队元素
 * @return SUCCESS(1) 成功, FAILURE(0) 失败（队列已满）
 */
int EnQueue1a(Queue1a *Q, int x) {
    if (Q == NULL) return FAILURE;  // 健壮性检查
    if (IsFull1a(*Q)) return FAILURE;
    
    Q->data[Q->rear] = x;           // 将元素放入队尾位置
    Q->rear = (Q->rear + 1) % MaxSize;  // rear循环后移
    return SUCCESS;
}

/**
 * @brief 出队操作
 * @param Q 队列指针
 * @param x 用于接收出队元素的指针
 * @return SUCCESS(1) 成功, FAILURE(0) 失败（队列已空）
 */
int DeQueue1a(Queue1a *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;  // 健壮性检查
    if (IsEmpty1a(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];         // 取出队头元素
    Q->front = (Q->front + 1) % MaxSize;  // front循环后移
    return SUCCESS;
}

/**
 * @brief 获取队列长度
 * @param Q 队列
 * @return 队列中元素个数
 */
int GetLength1a(Queue1a Q) {
    return (Q.rear - Q.front + MaxSize) % MaxSize;
}

// ============================================================================
// 方式1b：rear指向队尾后一个位置 + size变量
// 判空：size == 0
// 判满：size == MaxSize
// 特点：空间利用率100%，逻辑直观，推荐使用
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素的后一个位置
    int size;           // 记录队列当前长度（核心新增字段）
} Queue1b;

void InitQueue1b(Queue1b *Q) {
    if (Q == NULL) return;
    Q->front = Q->rear = Q->size = 0;
}

int IsEmpty1b(Queue1b Q) {
    return Q.size == 0;
}

int IsFull1b(Queue1b Q) {
    return Q.size == MaxSize;
}

int EnQueue1b(Queue1b *Q, int x) {
    if (Q == NULL) return FAILURE;
    if (IsFull1b(*Q)) return FAILURE;
    
    Q->data[Q->rear] = x;
    Q->rear = (Q->rear + 1) % MaxSize;
    Q->size++;  // 入队成功，长度加1
    return SUCCESS;
}

int DeQueue1b(Queue1b *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;
    if (IsEmpty1b(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];
    Q->front = (Q->front + 1) % MaxSize;
    Q->size--;  // 出队成功，长度减1
    return SUCCESS;
}

int GetLength1b(Queue1b Q) {
    return Q.size;  // 直接返回size，O(1)时间复杂度
}

// ============================================================================
// 方式1c：rear指向队尾后一个位置 + tag标记
// 判空：front == rear && tag == 0（最近出队导致空）
// 判满：front == rear && tag == 1（最近入队导致满）
// 特点：空间利用率100%，逻辑稍复杂
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素的后一个位置
    int tag;            // 标记最近操作：0-出队，1-入队（核心新增字段）
} Queue1c;

void InitQueue1c(Queue1c *Q) {
    if (Q == NULL) return;
    Q->front = Q->rear = 0;
    Q->tag = 0;  // 初始状态视为"出队后为空"
}

int IsEmpty1c(Queue1c Q) {
    return Q.front == Q.rear && Q.tag == 0;
}

int IsFull1c(Queue1c Q) {
    return Q.front == Q.rear && Q.tag == 1;
}

int EnQueue1c(Queue1c *Q, int x) {
    if (Q == NULL) return FAILURE;
    if (IsFull1c(*Q)) return FAILURE;
    
    Q->data[Q->rear] = x;
    Q->rear = (Q->rear + 1) % MaxSize;
    Q->tag = 1;  // 标记最近操作为入队
    return SUCCESS;
}

int DeQueue1c(Queue1c *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;
    if (IsEmpty1c(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];
    Q->front = (Q->front + 1) % MaxSize;
    Q->tag = 0;  // 标记最近操作为出队
    return SUCCESS;
}

int GetLength1c(Queue1c Q) {
    if (IsEmpty1c(Q)) return 0;
    if (IsFull1c(Q)) return MaxSize;
    return (Q.rear - Q.front + MaxSize) % MaxSize;
}

// ============================================================================
// 方式2a：rear指向队尾元素 + 牺牲一个存储空间
// 注意：入队时先移动rear再赋值，与方式1a不同！
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素（与方式1的核心区别）
} Queue2a;

void InitQueue2a(Queue2a *Q) {
    if (Q == NULL) return;
    Q->front = Q->rear = 0;
}

int IsEmpty2a(Queue2a Q) {
    return Q.front == Q.rear;
}

int IsFull2a(Queue2a Q) {
    return (Q.rear + 1) % MaxSize == Q.front;
}

int EnQueue2a(Queue2a *Q, int x) {
    if (Q == NULL) return FAILURE;
    if (IsFull2a(*Q)) return FAILURE;
    
    Q->rear = (Q->rear + 1) % MaxSize;  // 先移动rear（与方式1a的关键区别）
    Q->data[Q->rear] = x;               // 再赋值
    return SUCCESS;
}

int DeQueue2a(Queue2a *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;
    if (IsEmpty2a(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];
    Q->front = (Q->front + 1) % MaxSize;
    return SUCCESS;
}

int GetLength2a(Queue2a Q) {
    return (Q.rear - Q.front + MaxSize) % MaxSize;
}

// ============================================================================
// 方式2b：rear指向队尾元素 + size变量
// 注意：入队时先移动rear再赋值
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素
    int size;           // 记录队列当前长度
} Queue2b;

void InitQueue2b(Queue2b *Q) {
    if (Q == NULL) return;
    Q->front = Q->rear = Q->size = 0;
}

int IsEmpty2b(Queue2b Q) {
    return Q.size == 0;
}

int IsFull2b(Queue2b Q) {
    return Q.size == MaxSize;
}

int EnQueue2b(Queue2b *Q, int x) {
    if (Q == NULL) return FAILURE;
    if (IsFull2b(*Q)) return FAILURE;
    
    Q->rear = (Q->rear + 1) % MaxSize;  // 先移动rear
    Q->data[Q->rear] = x;
    Q->size++;
    return SUCCESS;
}

int DeQueue2b(Queue2b *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;
    if (IsEmpty2b(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];
    Q->front = (Q->front + 1) % MaxSize;
    Q->size--;
    return SUCCESS;
}

int GetLength2b(Queue2b Q) {
    return Q.size;
}

// ============================================================================
// 方式2c：rear指向队尾元素 + tag标记
// 注意：入队时先移动rear再赋值
// ============================================================================
typedef struct {
    int data[MaxSize];  // 存储队列元素的数组
    int front;          // 指向队头元素
    int rear;           // 指向队尾元素
    int tag;            // 标记最近操作：0-出队，1-入队
} Queue2c;

void InitQueue2c(Queue2c *Q) {
    if (Q == NULL) return;
    Q->front = Q->rear = 0;
    Q->tag = 0;
}

int IsEmpty2c(Queue2c Q) {
    return Q.front == Q.rear && Q.tag == 0;
}

int IsFull2c(Queue2c Q) {
    return Q.front == Q.rear && Q.tag == 1;
}

int EnQueue2c(Queue2c *Q, int x) {
    if (Q == NULL) return FAILURE;
    if (IsFull2c(*Q)) return FAILURE;
    
    Q->rear = (Q->rear + 1) % MaxSize;  // 先移动rear
    Q->data[Q->rear] = x;
    Q->tag = 1;
    return SUCCESS;
}

int DeQueue2c(Queue2c *Q, int *x) {
    if (Q == NULL || x == NULL) return FAILURE;
    if (IsEmpty2c(*Q)) return FAILURE;
    
    *x = Q->data[Q->front];
    Q->front = (Q->front + 1) % MaxSize;
    Q->tag = 0;
    return SUCCESS;
}

int GetLength2c(Queue2c Q) {
    if (IsEmpty2c(Q)) return 0;
    if (IsFull2c(Q)) return MaxSize;
    return (Q.rear - Q.front + MaxSize) % MaxSize;
}

// ============================================================================
// 测试函数：对比6种实现方式的行为
// ============================================================================
void TestAllQueues() {
    printf("====== 循环队列6种实现方式对比测试 ======\n\n");
    
    // 声明6种队列
    Queue1a q1a; Queue1b q1b; Queue1c q1c;
    Queue2a q2a; Queue2b q2b; Queue2c q2c;
    
    // 初始化所有队列
    InitQueue1a(&q1a); InitQueue1b(&q1b); InitQueue1c(&q1c);
    InitQueue2a(&q2a); InitQueue2b(&q2b); InitQueue2c(&q2c);
    
    int i, x;
    
    // 阶段1：初始状态（空队列）
    printf("【阶段1】初始状态（空队列）\n");
    printf("  1a: 空=%d, 满=%d, 长度=%d\n", IsEmpty1a(q1a), IsFull1a(q1a), GetLength1a(q1a));
    printf("  1b: 空=%d, 满=%d, 长度=%d\n", IsEmpty1b(q1b), IsFull1b(q1b), GetLength1b(q1b));
    printf("  1c: 空=%d, 满=%d, 长度=%d\n", IsEmpty1c(q1c), IsFull1c(q1c), GetLength1c(q1c));
    printf("  2a: 空=%d, 满=%d, 长度=%d\n", IsEmpty2a(q2a), IsFull2a(q2a), GetLength2a(q2a));
    printf("  2b: 空=%d, 满=%d, 长度=%d\n", IsEmpty2b(q2b), IsFull2b(q2b), GetLength2b(q2b));
    printf("  2c: 空=%d, 满=%d, 长度=%d\n", IsEmpty2c(q2c), IsFull2c(q2c), GetLength2c(q2c));
    
    // 阶段2：入队1-9（9个元素）
    printf("\n【阶段2】入队1-9（9个元素）\n");
    for (i = 1; i <= 9; i++) {
        EnQueue1a(&q1a, i); EnQueue1b(&q1b, i); EnQueue1c(&q1c, i);
        EnQueue2a(&q2a, i); EnQueue2b(&q2b, i); EnQueue2c(&q2c, i);
    }
    printf("  1a: 空=%d, 满=%d, 长度=%d\n", IsEmpty1a(q1a), IsFull1a(q1a), GetLength1a(q1a));
    printf("  1b: 空=%d, 满=%d, 长度=%d\n", IsEmpty1b(q1b), IsFull1b(q1b), GetLength1b(q1b));
    printf("  1c: 空=%d, 满=%d, 长度=%d\n", IsEmpty1c(q1c), IsFull1c(q1c), GetLength1c(q1c));
    printf("  2a: 空=%d, 满=%d, 长度=%d\n", IsEmpty2a(q2a), IsFull2a(q2a), GetLength2a(q2a));
    printf("  2b: 空=%d, 满=%d, 长度=%d\n", IsEmpty2b(q2b), IsFull2b(q2b), GetLength2b(q2b));
    printf("  2c: 空=%d, 满=%d, 长度=%d\n", IsEmpty2c(q2c), IsFull2c(q2c), GetLength2c(q2c));
    
    // 阶段3：尝试入队第10个元素（测试满队）
    printf("\n【阶段3】尝试入队第10个元素（测试满队）\n");
    printf("  1a入队10: %s\n", EnQueue1a(&q1a, 10) ? "成功" : "失败(已满)");
    printf("  1b入队10: %s\n", EnQueue1b(&q1b, 10) ? "成功" : "失败(已满)");
    printf("  1c入队10: %s\n", EnQueue1c(&q1c, 10) ? "成功" : "失败(已满)");
    printf("  2a入队10: %s\n", EnQueue2a(&q2a, 10) ? "成功" : "失败(已满)");
    printf("  2b入队10: %s\n", EnQueue2b(&q2b, 10) ? "成功" : "失败(已满)");
    printf("  2c入队10: %s\n", EnQueue2c(&q2c, 10) ? "成功" : "失败(已满)");
    
    // 阶段4：出队3个元素
    printf("\n【阶段4】出队3个元素\n");
    for (i = 0; i < 3; i++) {
        DeQueue1a(&q1a, &x); DeQueue1b(&q1b, &x); DeQueue1c(&q1c, &x);
        DeQueue2a(&q2a, &x); DeQueue2b(&q2b, &x); DeQueue2c(&q2c, &x);
    }
    printf("  1a: 空=%d, 满=%d, 长度=%d\n", IsEmpty1a(q1a), IsFull1a(q1a), GetLength1a(q1a));
    printf("  1b: 空=%d, 满=%d, 长度=%d\n", IsEmpty1b(q1b), IsFull1b(q1b), GetLength1b(q1b));
    printf("  1c: 空=%d, 满=%d, 长度=%d\n", IsEmpty1c(q1c), IsFull1c(q1c), GetLength1c(q1c));
    printf("  2a: 空=%d, 满=%d, 长度=%d\n", IsEmpty2a(q2a), IsFull2a(q2a), GetLength2a(q2a));
    printf("  2b: 空=%d, 满=%d, 长度=%d\n", IsEmpty2b(q2b), IsFull2b(q2b), GetLength2b(q2b));
    printf("  2c: 空=%d, 满=%d, 长度=%d\n", IsEmpty2c(q2c), IsFull2c(q2c), GetLength2c(q2c));
    
    // 阶段5：继续入队（测试循环特性）
    printf("\n【阶段5】继续入队10（测试循环）\n");
    EnQueue1a(&q1a, 10); EnQueue1b(&q1b, 10); EnQueue1c(&q1c, 10);
    EnQueue2a(&q2a, 10); EnQueue2b(&q2b, 10); EnQueue2c(&q2c, 10);
    printf("  1a: 空=%d, 满=%d, 长度=%d\n", IsEmpty1a(q1a), IsFull1a(q1a), GetLength1a(q1a));
    printf("  1b: 空=%d, 满=%d, 长度=%d\n", IsEmpty1b(q1b), IsFull1b(q1b), GetLength1b(q1b));
    printf("  1c: 空=%d, 满=%d, 长度=%d\n", IsEmpty1c(q1c), IsFull1c(q1c), GetLength1c(q1c));
    printf("  2a: 空=%d, 满=%d, 长度=%d\n", IsEmpty2a(q2a), IsFull2a(q2a), GetLength2a(q2a));
    printf("  2b: 空=%d, 满=%d, 长度=%d\n", IsEmpty2b(q2b), IsFull2b(q2b), GetLength2b(q2b));
    printf("  2c: 空=%d, 满=%d, 长度=%d\n", IsEmpty2c(q2c), IsFull2c(q2c), GetLength2c(q2c));
    
    // 阶段6：清空队列（测试空队判断）
    printf("\n【阶段6】清空队列（测试空队）\n");
    while (!IsEmpty1a(q1a)) DeQueue1a(&q1a, &x);
    while (!IsEmpty1b(q1b)) DeQueue1b(&q1b, &x);
    while (!IsEmpty1c(q1c)) DeQueue1c(&q1c, &x);
    while (!IsEmpty2a(q2a)) DeQueue2a(&q2a, &x);
    while (!IsEmpty2b(q2b)) DeQueue2b(&q2b, &x);
    while (!IsEmpty2c(q2c)) DeQueue2c(&q2c, &x);
    printf("  1a: 空=%d, 满=%d, 长度=%d\n", IsEmpty1a(q1a), IsFull1a(q1a), GetLength1a(q1a));
    printf("  1b: 空=%d, 满=%d, 长度=%d\n", IsEmpty1b(q1b), IsFull1b(q1b), GetLength1b(q1b));
    printf("  1c: 空=%d, 满=%d, 长度=%d\n", IsEmpty1c(q1c), IsFull1c(q1c), GetLength1c(q1c));
    printf("  2a: 空=%d, 满=%d, 长度=%d\n", IsEmpty2a(q2a), IsFull2a(q2a), GetLength2a(q2a));
    printf("  2b: 空=%d, 满=%d, 长度=%d\n", IsEmpty2b(q2b), IsFull2b(q2b), GetLength2b(q2b));
    printf("  2c: 空=%d, 满=%d, 长度=%d\n", IsEmpty2c(q2c), IsFull2c(q2c), GetLength2c(q2c));
    
    // 阶段7：尝试出队（测试空队时出队）
    printf("\n【阶段7】尝试出队（测试空队）\n");
    printf("  1a出队: %s\n", DeQueue1a(&q1a, &x) ? "成功" : "失败(已空)");
    printf("  1b出队: %s\n", DeQueue1b(&q1b, &x) ? "成功" : "失败(已空)");
    printf("  1c出队: %s\n", DeQueue1c(&q1c, &x) ? "成功" : "失败(已空)");
    printf("  2a出队: %s\n", DeQueue2a(&q2a, &x) ? "成功" : "失败(已空)");
    printf("  2b出队: %s\n", DeQueue2b(&q2b, &x) ? "成功" : "失败(已空)");
    printf("  2c出队: %s\n", DeQueue2c(&q2c, &x) ? "成功" : "失败(已空)");
}

// ============================================================================
// 打印知识总结表格
// ============================================================================
void PrintKnowledgeSummary() {
    printf("\n\n====== 循环队列知识体系总结 ======\n");
    printf("┌──────────────────────────────────────────────────────────────────────┐\n");
    printf("│                    循环队列6种实现方式对比表                          │\n");
    printf("├──────┬──────────────────────┬─────────────────┬──────────────────────┤\n");
    printf("│ 方式 │   front/rear 含义    │   判空条件      │   判满条件           │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  1a  │ front=队头           │ front == rear   │ (rear+1)%%n == front │\n");
    printf("│      │ rear=队尾后一个位置  │                 │                      │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  1b  │ front=队头           │ size == 0       │ size == MaxSize      │\n");
    printf("│      │ rear=队尾后一个位置  │                 │                      │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  1c  │ front=队头           │ f==r && tag==0  │ f==r && tag==1       │\n");
    printf("│      │ rear=队尾后一个位置  │                 │                      │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  2a  │ front=队头           │ front == rear   │ (rear+1)%%n == front │\n");
    printf("│      │ rear=队尾元素        │                 │                      │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  2b  │ front=队头           │ size == 0       │ size == MaxSize      │\n");
    printf("│      │ rear=队尾元素        │                 │                      │\n");
    printf("├──────┼──────────────────────┼─────────────────┼──────────────────────┤\n");
    printf("│  2c  │ front=队头           │ f==r && tag==0  │ f==r && tag==1       │\n");
    printf("│      │ rear=队尾元素        │                 │                      │\n");
    printf("└──────┴──────────────────────┴─────────────────┴──────────────────────┘\n");
    
    printf("\n★ 三种区分方法特点对比：\n");
    printf("┌──────────────────────────────────────────────────────────────────────┐\n");
    printf("│  方法a（牺牲空间） │ 优点：无需额外字段；缺点：浪费1个存储单元         │\n");
    printf("│  方法b（size变量） │ 优点：逻辑直观，O(1)求长度；缺点：需额外字段     │\n");
    printf("│  方法c（tag标记）  │ 优点：空间利用率100%%；缺点：逻辑稍复杂          │\n");
    printf("└──────────────────────────────────────────────────────────────────────┘\n");
    
    printf("\n★ 两种rear定义对比：\n");
    printf("┌──────────────────────────────────────────────────────────────────────┐\n");
    printf("│  rear=队尾后一个位置（推荐）：入队时先赋值后移动rear                   │\n");
    printf("│  rear=队尾元素：入队时先移动rear后赋值                               │\n");
    printf("└──────────────────────────────────────────────────────────────────────┘\n");
    
    printf("\n★ 核心考点总结（408高频考点）：\n");
    printf("  1. 循环队列的核心问题：front==rear无法区分空/满                     \n");
    printf("  2. 三种解决方法的原理和区别                                         \n");
    printf("  3. 入队/出队操作中指针的移动顺序                                   \n");
    printf("  4. 队列长度计算：(rear - front + MaxSize) %% MaxSize                 \n");
    printf("  5. 推荐使用方式1b或2b（size变量法），逻辑最简单                     \n");
}

int main() {
    TestAllQueues();
    PrintKnowledgeSummary();
    return 0;
}