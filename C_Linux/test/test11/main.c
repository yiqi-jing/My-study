// OS.cpp: 定义控制台应用程序的入口点。
#include "stdafx.h"
#include<stdio.h>
#include<stdlib.h>

#define VM_PAGE 7      /*假设每个页面可以存放10条指令,则共有32个虚页*/
#define PM_PAGE 4         /*分配给作业的内存块数为4*/
#define TOTAL_INSERT 18
typedef struct
{
    int vmn;
    int pmn;
    int exist;
    int time;
}vpage_item;
vpage_item page_table[VM_PAGE];
vpage_item* ppage_bitmap[PM_PAGE];
int vpage_arr[TOTAL_INSERT] = { 1,2,3,4,2,6,2,1,2,3,7,6,3,2,1,2,3,6 };
void init_data() //数据初始化
{
         for (int i = 0; i<VM_PAGE; i++)
         {
            page_table[i].vmn = i + 1;  //虚页号
            page_table[i].pmn = -1;    //实页号
            page_table[i].exist = 0;
            page_table[i].time = -1;
         }
         for (int i = 0; i<PM_PAGE; i++) /*最初4个物理块为空*/
         {
            ppage_bitmap[i] = NULL;
         }
}
void FIFO()/*FIFO页面置换算法*/
{
         int k = 0;
         int i;
         int sum = 0;
         int missing_page_count = 0;
         int current_time = 0;
         bool isleft = true;   /*当前物理块中是否有剩余*/
         while (sum < TOTAL_INSERT)
         {
                   if (page_table[vpage_arr[sum] - 1].exist == 0)
                   {
                        missing_page_count++;
                        if (k < 4)
                        {
                            if (ppage_bitmap[k] == NULL) /*找到一个空闲物理块*/
                            {
                                ppage_bitmap[k] = &page_table[vpage_arr[sum] - 1];
                                ppage_bitmap[k]->exist = 1;
                                ppage_bitmap[k]->pmn = k;
                                ppage_bitmap[k]->time = current_time;
                                k++;
                            }
                        }
                        else
                        {
                            int temp = ppage_bitmap[0]->time; /*记录物理块中作业最早到达时间*/
                            int j = 0;       /*记录应当被替换的物理块号*/
                            for (i = 0; i < PM_PAGE; i++)
                            {
                                if (ppage_bitmap[i]->time < temp)
                                {
                                    temp = ppage_bitmap[i]->time;
                                    j = i;
                                }
                            }
                            ppage_bitmap[j]->exist = 0;
                            ppage_bitmap[j] = &page_table[vpage_arr[sum] - 1]; /*更新页表项*/
                            ppage_bitmap[j]->exist = 1;
                            ppage_bitmap[j]->pmn = j;
                            ppage_bitmap[j]->time = current_time;
                        }
                   }
                   current_time++;
                   sum++;
         }
         printf("FIFO算法缺页次数为:%d\t缺页率为:%f\t置换次数为:%d\t置换率为:%f", missing_page_count, missing_page_count / (float)TOTAL_INSERT, missing_page_count - 4, (missing_page_count - 4) / (float)TOTAL_INSERT);
}
void LRU()
{
}
void OPT()
{
}
int main()
{
    int a;
    printf("请输入需要选择的页面置换算法：1.FIFO\t2.LRU\t3.OPT\t输入0结束\n");
    do
    {
        scanf_s("%d", &a);
        switch (a)
        {
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
        }
    } while (a != 0);
    return 0;
}
