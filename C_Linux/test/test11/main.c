#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>  // Linux 中需要显式包含 bool 类型头文件

#define VM_PAGE 7        /* 虚页数：7（虚页号 1~7） */
#define PM_PAGE 4        /* 内存块数：4 */
#define TOTAL_INSERT 18  /* 指令序列长度 */

// 页表项结构
typedef struct {
    int vmn;     // 虚页号
    int pmn;     // 实页号（-1 表示未分配）
    int exist;   // 存在位（1：在内存，0：不在）
    int time;    // 时间戳（FIFO/LRU 用）
} vpage_item;

vpage_item page_table[VM_PAGE];       // 页表
vpage_item* ppage_bitmap[PM_PAGE];    // 物理块映射（指向页表项）
// 指令序列（对应虚页访问序列）
int vpage_arr[TOTAL_INSERT] = {1,2,3,4,2,6,2,1,2,3,7,6,3,2,1,2,3,6};

// 数据初始化
void init_data() {
    // 初始化页表
    for (int i = 0; i < VM_PAGE; i++) {
        page_table[i].vmn = i + 1;  // 虚页号 1~7
        page_table[i].pmn = -1;     // 初始无实页分配
        page_table[i].exist = 0;    // 初始不在内存
        page_table[i].time = -1;    // 初始时间戳无效
    }
    // 初始化物理块（全部为空）
    for (int i = 0; i < PM_PAGE; i++) {
        ppage_bitmap[i] = NULL;
    }
}

// FIFO 页面置换算法（原代码修正适配）
void FIFO() {
    int k = 0;                      // 已使用的物理块数
    int sum = 0;                    // 已处理的指令数
    int missing_page_count = 0;     // 缺页次数
    int current_time = 0;           // 当前时间戳

    while (sum < TOTAL_INSERT) {
        int vpage_num = vpage_arr[sum];  // 当前访问的虚页号
        vpage_item* curr_page = &page_table[vpage_num - 1];  // 对应页表项

        // 缺页（当前虚页不在内存）
        if (curr_page->exist == 0) {
            missing_page_count++;

            // 物理块还有空闲，直接分配
            if (k < PM_PAGE) {
                ppage_bitmap[k] = curr_page;
                curr_page->exist = 1;
                curr_page->pmn = k;
                curr_page->time = current_time;
                k++;
            } else {  // 物理块已满，执行 FIFO 置换（淘汰最早进入的页）
                int replace_idx = 0;  // 要置换的物理块索引
                // 找到时间戳最小（最早进入）的页
                for (int i = 1; i < PM_PAGE; i++) {
                    if (ppage_bitmap[i]->time < ppage_bitmap[replace_idx]->time) {
                        replace_idx = i;
                    }
                }
                // 淘汰旧页
                ppage_bitmap[replace_idx]->exist = 0;
                ppage_bitmap[replace_idx]->pmn = -1;
                // 分配新页
                ppage_bitmap[replace_idx] = curr_page;
                curr_page->exist = 1;
                curr_page->pmn = replace_idx;
                curr_page->time = current_time;
            }
        }

        current_time++;
        sum++;
    }

    // 计算置换次数（缺页次数 - 初始加载的4个页）
    int replace_count = missing_page_count - PM_PAGE;
    printf("FIFO算法：\n");
    printf("  缺页次数：%d\n", missing_page_count);
    printf("  缺页率：%.2f%%\n", (missing_page_count / (float)TOTAL_INSERT) * 100);
    printf("  置换次数：%d\n", replace_count);
    printf("  置换率：%.2f%%\n\n", (replace_count / (float)TOTAL_INSERT) * 100);
}

// LRU 页面置换算法（最近最少使用）
void LRU() {
    int k = 0;                      // 已使用的物理块数
    int sum = 0;                    // 已处理的指令数
    int missing_page_count = 0;     // 缺页次数
    int current_time = 0;           // 当前时间戳

    while (sum < TOTAL_INSERT) {
        int vpage_num = vpage_arr[sum];  // 当前访问的虚页号
        vpage_item* curr_page = &page_table[vpage_num - 1];  // 对应页表项

        // 页面命中：更新时间戳为当前时间（最近使用）
        if (curr_page->exist == 1) {
            curr_page->time = current_time;
        } else {  // 缺页：需要加载或置换
            missing_page_count++;

            // 物理块有空闲，直接分配
            if (k < PM_PAGE) {
                ppage_bitmap[k] = curr_page;
                curr_page->exist = 1;
                curr_page->pmn = k;
                curr_page->time = current_time;
                k++;
            } else {  // 物理块已满，淘汰最近最少使用的页（时间戳最小）
                int replace_idx = 0;
                for (int i = 1; i < PM_PAGE; i++) {
                    if (ppage_bitmap[i]->time < ppage_bitmap[replace_idx]->time) {
                        replace_idx = i;
                    }
                }
                // 淘汰旧页
                ppage_bitmap[replace_idx]->exist = 0;
                ppage_bitmap[replace_idx]->pmn = -1;
                // 分配新页
                ppage_bitmap[replace_idx] = curr_page;
                curr_page->exist = 1;
                curr_page->pmn = replace_idx;
                curr_page->time = current_time;
            }
        }

        current_time++;
        sum++;
    }

    int replace_count = missing_page_count - PM_PAGE;
    printf("LRU算法：\n");
    printf("  缺页次数：%d\n", missing_page_count);
    printf("  缺页率：%.2f%%\n", (missing_page_count / (float)TOTAL_INSERT) * 100);
    printf("  置换次数：%d\n", replace_count);
    printf("  置换率：%.2f%%\n\n", (replace_count / (float)TOTAL_INSERT) * 100);
}

// OPT 页面置换算法（最佳置换：未来最久不使用）
void OPT() {
    int k = 0;                      // 已使用的物理块数
    int sum = 0;                    // 已处理的指令数
    int missing_page_count = 0;     // 缺页次数

    while (sum < TOTAL_INSERT) {
        int vpage_num = vpage_arr[sum];  // 当前访问的虚页号
        vpage_item* curr_page = &page_table[vpage_num - 1];  // 对应页表项

        // 页面命中：无需操作
        if (curr_page->exist == 1) {
            sum++;
            continue;
        }

        // 缺页：需要加载或置换
        missing_page_count++;

        // 物理块有空闲，直接分配
        if (k < PM_PAGE) {
            ppage_bitmap[k] = curr_page;
            curr_page->exist = 1;
            curr_page->pmn = k;
            k++;
        } else {  // 物理块已满，选择未来最久不使用的页淘汰
            int replace_idx = 0;
            int max_dist = -1;  // 记录最远使用距离

            // 遍历每个物理块中的页，计算其下次使用的距离
            for (int i = 0; i < PM_PAGE; i++) {
                int curr_vmn = ppage_bitmap[i]->vmn;
                int dist = TOTAL_INSERT;  // 默认：未来不再使用（距离为总长度）

                // 查找当前页在后续指令中的首次出现位置
                for (int j = sum + 1; j < TOTAL_INSERT; j++) {
                    if (vpage_arr[j] == curr_vmn) {
                        dist = j - sum;  // 下次使用距离
                        break;
                    }
                }

                // 选择距离最远的页作为置换目标
                if (dist > max_dist) {
                    max_dist = dist;
                    replace_idx = i;
                }
            }

            // 淘汰旧页
            ppage_bitmap[replace_idx]->exist = 0;
            ppage_bitmap[replace_idx]->pmn = -1;
            // 分配新页
            ppage_bitmap[replace_idx] = curr_page;
            curr_page->exist = 1;
            curr_page->pmn = replace_idx;
        }

        sum++;
    }

    int replace_count = missing_page_count - PM_PAGE;
    printf("OPT算法：\n");
    printf("  缺页次数：%d\n", missing_page_count);
    printf("  缺页率：%.2f%%\n", (missing_page_count / (float)TOTAL_INSERT) * 100);
    printf("  置换次数：%d\n", replace_count);
    printf("  置换率：%.2f%%\n\n", (replace_count / (float)TOTAL_INSERT) * 100);
}

int main() {
    int a;
    printf("请输入需要选择的页面置换算法：\n");
    printf("1.FIFO\t2.LRU\t3.OPT\t输入0结束\n");

    do {
        scanf("%d", &a);  // Linux 中使用标准 scanf（替换 Windows 的 scanf_s）
        switch (a) {
            case 1:
                init_data();
                FIFO();
                break;
            case 2:
                init_data();
                LRU();
                break;
            case 3:
                init_data();
                OPT();
                break;
            case 0:
                printf("程序结束！\n");
                break;
            default:
                printf("输入错误，请重新选择（1-3或0）：\n");
                break;
        }
    } while (a != 0);

    return 0;
}
