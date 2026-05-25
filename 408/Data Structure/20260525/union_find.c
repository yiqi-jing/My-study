/*
 * 并查集（Union-Find）数据结构 C语言实现
 * 
 * 并查集用于处理不相交集合的合并与查询问题，主要操作：
 * 1. Find（查找）：查找元素所属的集合（根节点）
 * 2. Union（合并）：将两个集合合并为一个
 * 
 * 本文件包含两种实现：
 * - 基础版本：无优化
 * - 优化版本：路径压缩 + 按秩合并
 */

#include <stdio.h>
#include <stdlib.h>

/* ============================================
 * 第一部分：基础并查集（无优化）
 * ============================================ */

/* 基础并查集结构体 */
typedef struct {
    int *parent;    /* parent[i] 表示元素i的父节点 */
    int size;       /* 集合中元素的总数量 */
} BasicUnionFind;

/*
 * 初始化基础并查集
 * 参数：n - 元素个数（元素编号为 0 到 n-1）
 * 返回：初始化好的并查集指针
 * 
 * 初始时，每个元素各自构成一个独立的集合
 * 即 parent[i] = i，表示自己是自己的父节点（根节点）
 */
BasicUnionFind* basicInit(int n) {
    BasicUnionFind *uf = (BasicUnionFind*)malloc(sizeof(BasicUnionFind));
    uf->parent = (int*)malloc(sizeof(int) * n);
    uf->size = n;
    
    for (int i = 0; i < n; i++) {
        uf->parent[i] = i;
    }
    
    return uf;
}

/*
 * 查找操作（基础版本）
 * 参数：uf - 并查集指针，x - 要查找的元素
 * 返回：元素x所在集合的根节点
 * 
 * 原理：沿着父节点指针一直向上查找，直到找到根节点
 * 时间复杂度：O(n) 最坏情况（树退化成链表）
 */
int basicFind(BasicUnionFind *uf, int x) {
    if (uf->parent[x] == x) {
        return x;
    }
    return basicFind(uf, uf->parent[x]);
}

/*
 * 合并操作（基础版本）
 * 参数：uf - 并查集指针，x, y - 要合并的两个元素
 * 
 * 原理：将x所在集合的根节点的父节点指向y所在集合的根节点
 * 时间复杂度：O(n) = Find操作的时间
 */
void basicUnion(BasicUnionFind *uf, int x, int y) {
    int rootX = basicFind(uf, x);
    int rootY = basicFind(uf, y);
    
    if (rootX == rootY) {
        return;
    }
    
    uf->parent[rootX] = rootY;
}

/*
 * 判断两个元素是否在同一个集合
 * 参数：uf - 并查集指针，x, y - 要判断的两个元素
 * 返回：1表示在同一集合，0表示不在
 */
int basicIsConnected(BasicUnionFind *uf, int x, int y) {
    return basicFind(uf, x) == basicFind(uf, y);
}

/*
 * 释放基础并查集内存
 */
void basicDestroy(BasicUnionFind *uf) {
    free(uf->parent);
    free(uf);
}


/* ============================================
 * 第二部分：优化版并查集
 * 优化策略：
 * 1. 路径压缩（Path Compression）- 优化Find操作
 * 2. 按秩合并（Union by Rank）- 优化Union操作
 * ============================================ */

/* 优化版并查集结构体 */
typedef struct {
    int *parent;    /* parent[i] 表示元素i的父节点 */
    int *rank;      /* rank[i] 表示以i为根的树的高度（秩） */
    int size;       /* 集合中元素的总数量 */
} OptimizedUnionFind;

/*
 * 初始化优化版并查集
 * 参数：n - 元素个数
 * 返回：初始化好的并查集指针
 */
OptimizedUnionFind* optimizedInit(int n) {
    OptimizedUnionFind *uf = (OptimizedUnionFind*)malloc(sizeof(OptimizedUnionFind));
    uf->parent = (int*)malloc(sizeof(int) * n);
    uf->rank = (int*)malloc(sizeof(int) * n);
    uf->size = n;
    
    for (int i = 0; i < n; i++) {
        uf->parent[i] = i;
        uf->rank[i] = 1;
    }
    
    return uf;
}

/*
 * 查找操作（路径压缩优化）
 * 参数：uf - 并查集指针，x - 要查找的元素
 * 返回：元素x所在集合的根节点
 * 
 * 路径压缩原理：
 * 在查找过程中，将查找路径上的所有节点直接连接到根节点
 * 这样下次再查找这些节点时，只需一步就能到达根节点
 * 
 * 时间复杂度：接近 O(α(n))，实际应用中可视为常数时间
 */
int optimizedFind(OptimizedUnionFind *uf, int x) {
    if (uf->parent[x] == x) {
        return x;
    }
    
    uf->parent[x] = optimizedFind(uf, uf->parent[x]);
    return uf->parent[x];
}

/*
 * 合并操作（按秩合并优化）
 * 参数：uf - 并查集指针，x, y - 要合并的两个元素
 * 
 * 按秩合并原理：
 * 总是将较矮的树合并到较高的树下，避免树的高度增加
 * 这样可以保持树的平衡，减少查找时间
 */
void optimizedUnion(OptimizedUnionFind *uf, int x, int y) {
    int rootX = optimizedFind(uf, x);
    int rootY = optimizedFind(uf, y);
    
    if (rootX == rootY) {
        return;
    }
    
    if (uf->rank[rootX] < uf->rank[rootY]) {
        uf->parent[rootX] = rootY;
    } else if (uf->rank[rootX] > uf->rank[rootY]) {
        uf->parent[rootY] = rootX;
    } else {
        uf->parent[rootY] = rootX;
        uf->rank[rootX]++;
    }
}

/*
 * 判断两个元素是否在同一个集合（优化版）
 */
int optimizedIsConnected(OptimizedUnionFind *uf, int x, int y) {
    return optimizedFind(uf, x) == optimizedFind(uf, y);
}

/*
 * 释放优化版并查集内存
 */
void optimizedDestroy(OptimizedUnionFind *uf) {
    free(uf->parent);
    free(uf->rank);
    free(uf);
}


/* ============================================
 * 第三部分：测试代码
 * ============================================ */

void printBasicUF(BasicUnionFind *uf) {
    printf("元素: ");
    for (int i = 0; i < uf->size; i++) {
        printf("%d ", i);
    }
    printf("\n父节点: ");
    for (int i = 0; i < uf->size; i++) {
        printf("%d ", uf->parent[i]);
    }
    printf("\n");
}

void printOptimizedUF(OptimizedUnionFind *uf) {
    printf("元素: ");
    for (int i = 0; i < uf->size; i++) {
        printf("%d ", i);
    }
    printf("\n父节点: ");
    for (int i = 0; i < uf->size; i++) {
        printf("%d ", uf->parent[i]);
    }
    printf("\n秩:     ");
    for (int i = 0; i < uf->size; i++) {
        printf("%d ", uf->rank[i]);
    }
    printf("\n");
}

int main() {
    
    printf("========================================\n");
    printf("      并查集（Union-Find）测试程序       \n");
    printf("========================================\n\n");
    
    /* ========== 基础版本测试 ========== */
    printf("【基础版并查集测试】\n");
    printf("--------------------\n");
    
    BasicUnionFind *basicUF = basicInit(10);
    printf("初始化并查集（10个元素）:\n");
    printBasicUF(basicUF);
    printf("\n");
    
    printf("执行合并操作: Union(0,1), Union(1,2), Union(3,4)\n");
    basicUnion(basicUF, 0, 1);
    basicUnion(basicUF, 1, 2);
    basicUnion(basicUF, 3, 4);
    printBasicUF(basicUF);
    
    printf("\n查询操作:\n");
    printf("Find(0) = %d\n", basicFind(basicUF, 0));
    printf("Find(2) = %d\n", basicFind(basicUF, 2));
    printf("0 和 2 是否连通: %s\n", basicIsConnected(basicUF, 0, 2) ? "是" : "否");
    printf("0 和 4 是否连通: %s\n", basicIsConnected(basicUF, 0, 4) ? "是" : "否");
    
    basicDestroy(basicUF);
    
    /* ========== 优化版本测试 ========== */
    printf("\n\n【优化版并查集测试（路径压缩 + 按秩合并）】\n");
    printf("-------------------------------------------\n");
    
    OptimizedUnionFind *optUF = optimizedInit(10);
    printf("初始化并查集（10个元素）:\n");
    printOptimizedUF(optUF);
    printf("\n");
    
    printf("执行合并操作: Union(0,1), Union(1,2), Union(3,4), Union(2,4)\n");
    optimizedUnion(optUF, 0, 1);
    optimizedUnion(optUF, 1, 2);
    optimizedUnion(optUF, 3, 4);
    optimizedUnion(optUF, 2, 4);
    printOptimizedUF(optUF);
    
    printf("\n执行Find(0)触发路径压缩:\n");
    printf("Find(0) = %d\n", optimizedFind(optUF, 0));
    printf("路径压缩后的状态:\n");
    printOptimizedUF(optUF);
    
    printf("\n更多合并操作: Union(5,6), Union(7,8), Union(5,8), Union(0,5)\n");
    optimizedUnion(optUF, 5, 6);
    optimizedUnion(optUF, 7, 8);
    optimizedUnion(optUF, 5, 8);
    optimizedUnion(optUF, 0, 5);
    printOptimizedUF(optUF);
    
    printf("\n最终连通性查询:\n");
    printf("0 和 8 是否连通: %s\n", optimizedIsConnected(optUF, 0, 8) ? "是" : "否");
    printf("2 和 6 是否连通: %s\n", optimizedIsConnected(optUF, 2, 6) ? "是" : "否");
    printf("0 和 9 是否连通: %s\n", optimizedIsConnected(optUF, 0, 9) ? "是" : "否");
    
    optimizedDestroy(optUF);
    
    printf("\n========================================\n");
    printf("              测试完成！                 \n");
    printf("========================================\n");
    
    return 0;
}
