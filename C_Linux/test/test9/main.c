#define _CRT_SECURE_NO_DEPRECATE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define MAXJOB  50

typedef struct node
{
    int number;
    int reach_time;
    int need_time;
    int privilege;
    float excellent;
    int start_time;
    int wait_time;
    int visited;
} job;

job jobs[MAXJOB];
int quantity;

// 初始化作业
void initial_jobs()
{
    int i;
    for (i = 0; i < MAXJOB; i++)
    {
        jobs[i].number = 0;
        jobs[i].reach_time = 0;
        jobs[i].privilege = 0;
        jobs[i].excellent = 0;
        jobs[i].start_time = 0;
        jobs[i].wait_time = 0;
        jobs[i].visited = 0;
    }
    quantity = 0;
}

// 读取作业信息并输出
void readJobdata()
{
    FILE* fp;
    char fname[20];
    int i;
    printf("请输入作业数据文件名：\n");  // 修正换行符：将/n改为\n
    scanf("%s", fname);
    if ((fp = fopen(fname, "r")) == NULL)
    {
        printf("错误！文件打开失败，请检查\n");
    }
    else
    {
        while (!feof(fp))
        {
            if (fscanf(fp, "%d %d %d %d", &jobs[quantity].number, &jobs[quantity].reach_time, &jobs[quantity].need_time, &jobs[quantity].privilege) == 4)
                quantity++;
        }
        printf("\n\n原始作业数据\n");
        printf("---------------------------------------------------------------\n");
        printf(" 作业ID\t\t到达时间\t执行时间\t优先权\n");
        printf("---------------------------------------------------------------\n");

        for (i = 0; i < quantity; i++)
        {
            // 用%-8d控制字段宽度，确保对齐
            printf("  %-8d\t%-8d\t%-8d\t%-8d\n", jobs[i].number, jobs[i].reach_time, jobs[i].need_time, jobs[i].privilege);
        }
        printf("---------------------------------------------------------------\n");
    }
}

// 重置作业信息
void reset_jinfo()
{
    int i;
    for (i = 0; i < MAXJOB; i++)
    {
        jobs[i].start_time = 0;
        jobs[i].wait_time = 0;
        jobs[i].visited = 0;
    }
}

// 找到最早到达作业，返回地址，全部到达返回-1
int findrearlyjob(job jobs[], int count)
{
    int rearlyloc = -1;
    int rearlyjob = -1;
    for (int i = 0; i < count; i++)
    {
        if (rearlyloc == -1)
        {
            if (jobs[i].visited == 0)
            {
                rearlyloc = i;
                rearlyjob = jobs[i].reach_time;
            }
        }
        else if (rearlyjob > jobs[i].reach_time && jobs[i].visited == 0)
        {
            rearlyjob = jobs[i].reach_time;
            rearlyloc = i;
        }
    }
    return rearlyloc;
}

// 查找当前current_time已到达未执行的最短作业,若无返回最早到达作业
int findminjob(job jobs[], int count, int current_time)
{
    int minjob = -1;
    int minloc = -1;
    for (int i = 0; i < count; i++)
    {
        if (minloc == -1)
        {
            if (jobs[i].reach_time <= current_time && jobs[i].visited == 0)
            {
                minjob = jobs[i].need_time;
                minloc = i;
            }
        }
        else if (minjob > jobs[i].need_time && jobs[i].visited == 0 && jobs[i].reach_time <= current_time)
        {
            minjob = jobs[i].need_time;
            minloc = i;
        }
        // 作业执行时间一样最短，但到达时间不同
        else if (minjob == jobs[i].need_time && jobs[i].visited == 0 && jobs[i].reach_time <= current_time && jobs[minloc].reach_time > jobs[i].reach_time)
        {
            minloc = i;
        }
    }
    if (minloc == -1)
        minloc = findrearlyjob(jobs, quantity);
    return minloc;
}

// 查找当前current_time已到达未执行的最优先作业
int findhighprivilegejob(job jobs[], int count, int current_time)
{
    int privilegejob = -1;
    int privilegeloc = -1;
    int privilege = -1;

    for (int i = 0; i < count; i++)
    {
        if (privilegeloc == -1)
        {
            if (jobs[i].reach_time <= current_time && jobs[i].visited == 0)
            {
                privilege = jobs[i].privilege;
                privilegejob = jobs[i].need_time;
                privilegeloc = i;
            }
        }
        else if (privilege < jobs[i].privilege && jobs[i].visited == 0 && jobs[i].reach_time <= current_time)
        {
            privilege = jobs[i].privilege;
            privilegejob = jobs[i].need_time;
            privilegeloc = i;
        }
        else if (privilege == jobs[i].privilege && jobs[i].visited == 0 && jobs[i].reach_time <= current_time && privilegejob > jobs[i].need_time)
        {
            privilegejob = jobs[i].need_time;
            privilegeloc = i;
        }
    }
    if (privilegeloc == -1)
        privilegeloc = findrearlyjob(jobs, quantity);
    return privilegeloc;
}

// 查找当前current_time已到达未执行的响应比最高的作业
int findhrrfjob(job jobs[], int count, int current_time)
{
    int hrrfjob = -1;
    int hrrfloc = -1;
    float responsejob = -1.0;
    for (int i = 0; i < count; i++)
    {
        if (hrrfloc == -1)
        {
            if (jobs[i].reach_time <= current_time && jobs[i].visited == 0)
            {
                hrrfjob = jobs[i].need_time;
                responsejob = (float)(current_time - jobs[i].reach_time + jobs[i].need_time) / jobs[i].need_time;
                hrrfloc = i;
            }
        }
        else if (responsejob < ((float)(current_time - jobs[i].reach_time + jobs[i].need_time) / jobs[i].need_time) && jobs[i].visited == 0 && jobs[i].reach_time <= current_time)
        {
            responsejob = (float)(current_time - jobs[i].reach_time + jobs[i].need_time) / jobs[i].need_time;
            hrrfjob = jobs[i].need_time;
            hrrfloc = i;
        }
        else if (responsejob == ((float)(current_time - jobs[i].reach_time + jobs[i].need_time) / jobs[i].need_time) && jobs[i].visited == 0 && jobs[i].reach_time <= current_time && hrrfjob > jobs[i].need_time)
        {
            hrrfjob = jobs[i].need_time;
            hrrfloc = i;
        }
    }
    if (hrrfloc == -1)
        hrrfloc = findrearlyjob(jobs, quantity);
    return hrrfloc;
}

void FCFS()
{
    int i;
    int current_time = 0;
    int loc;
    int total_waitime = 0;
    int total_roundtime = 0;
    loc = findrearlyjob(jobs, quantity);
    printf("\n\nFCFS算法作业流\n");
    printf("------------------------------------------------------------------------\n");
    printf(" 作业ID\t\t到达时间\t开始时间\t等待时间\t周转时间\n");
    printf("------------------------------------------------------------------------\n");
    current_time = jobs[loc].reach_time;
    for (i = 0; i < quantity; i++)
    {
        if (jobs[loc].reach_time > current_time)
        {
            jobs[loc].start_time = jobs[loc].reach_time;
            current_time = jobs[loc].reach_time;
        }
        else
        {
            jobs[loc].start_time = current_time;
        }
        jobs[loc].wait_time = current_time - jobs[loc].reach_time;
        printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
        jobs[loc].visited = 1;
        current_time += jobs[loc].need_time;
        total_waitime += jobs[loc].wait_time;
        total_roundtime = total_roundtime + jobs[loc].wait_time + jobs[loc].need_time;
        loc = findrearlyjob(jobs, quantity);
    }
    printf("------------------------------------------------------------------------\n");
    printf("总等待时间:%-8d 总周转时间:%-8d\n", total_waitime, total_roundtime);
    printf("平均等待时间: %4.2f 平均周转时间: %4.2f\n", (float)total_waitime / (quantity), (float)total_roundtime / (quantity));
}

void SFJschdulejob(job jobs[], int count)
{
    int i;
    int current_time = 0;
    int loc;
    int total_waitime = 0;
    int total_roundtime = 0;
    loc = findrearlyjob(jobs, quantity);
    printf("\n\nSFJ算法作业流\n");
    printf("------------------------------------------------------------------------\n");
    printf(" 作业ID\t\t到达时间\t开始时间\t等待时间\t周转时间\n");
    printf("------------------------------------------------------------------------\n");
    current_time = jobs[loc].reach_time;
    jobs[loc].start_time = jobs[loc].reach_time;
    jobs[loc].wait_time = 0;
    printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
    jobs[loc].visited = 1;
    current_time += jobs[loc].need_time;
    total_waitime = 0;
    total_roundtime = jobs[loc].need_time;
    loc = findminjob(jobs, quantity, current_time);
    for (i = 1; i < quantity; i++)
    {
        if (jobs[loc].reach_time > current_time)
        {
            jobs[loc].start_time = jobs[loc].reach_time;
            current_time = jobs[loc].reach_time;
        }
        else
        {
            jobs[loc].start_time = current_time;
        }
        jobs[loc].wait_time = current_time - jobs[loc].reach_time;
        printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
        jobs[loc].visited = 1;
        current_time += jobs[loc].need_time;
        total_waitime += jobs[loc].wait_time;
        total_roundtime = total_roundtime + jobs[loc].wait_time + jobs[loc].need_time;
        loc = findminjob(jobs, quantity, current_time);
    }
    printf("------------------------------------------------------------------------\n");
    printf("总等待时间:%-8d 总周转时间:%-8d\n", total_waitime, total_roundtime);
    printf("平均等待时间: %4.2f 平均周转时间: %4.2f\n", (float)total_waitime / (quantity), (float)total_roundtime / (quantity));
}

void HPF(job jobs[], int count)
{
    int i;
    int current_time = 0;
    int loc;
    int total_waitime = 0;
    int total_roundtime = 0;
    loc = findrearlyjob(jobs, quantity);
    printf("\n\nHPF算法作业流\n");
    printf("------------------------------------------------------------------------\n");
    printf(" 作业ID\t\t到达时间\t开始时间\t等待时间\t周转时间\n");
    printf("------------------------------------------------------------------------\n");
    current_time = jobs[loc].reach_time;
    jobs[loc].start_time = jobs[loc].reach_time;
    jobs[loc].wait_time = 0;
    printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
    jobs[loc].visited = 1;
    current_time += jobs[loc].need_time;
    total_waitime = 0;
    total_roundtime = jobs[loc].need_time;
    loc = findhighprivilegejob(jobs, quantity, current_time);
    for (i = 1; i < quantity; i++)
    {
        if (jobs[loc].reach_time > current_time)
        {
            jobs[loc].start_time = jobs[loc].reach_time;
            current_time = jobs[loc].reach_time;
        }
        else
        {
            jobs[loc].start_time = current_time;
        }
        jobs[loc].wait_time = current_time - jobs[loc].reach_time;
        printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
        jobs[loc].visited = 1;
        current_time += jobs[loc].need_time;
        total_waitime += jobs[loc].wait_time;
        total_roundtime = total_roundtime + jobs[loc].wait_time + jobs[loc].need_time;
        loc = findhighprivilegejob(jobs, quantity, current_time);
    }
    printf("------------------------------------------------------------------------\n");
    printf("总等待时间:%-8d 总周转时间:%-8d\n", total_waitime, total_roundtime);
    printf("平均等待时间: %4.2f 平均周转时间: %4.2f\n", (float)total_waitime / (quantity), (float)total_roundtime / (quantity));
}

void HRRF(job jobs[], int count)
{
    int i;
    int current_time = 0;
    int loc;
    int total_waitime = 0;
    int total_roundtime = 0;
    loc = findrearlyjob(jobs, quantity);
    printf("\n\nHRRF算法作业流\n");
    printf("------------------------------------------------------------------------\n");
    printf(" 作业ID\t\t到达时间\t开始时间\t等待时间\t周转时间\n");
    printf("------------------------------------------------------------------------\n");
    current_time = jobs[loc].reach_time;
    jobs[loc].start_time = jobs[loc].reach_time;
    jobs[loc].wait_time = 0;
    printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
    jobs[loc].visited = 1;
    current_time += jobs[loc].need_time;
    total_waitime = 0;
    total_roundtime = jobs[loc].need_time;
    loc = findhrrfjob(jobs, quantity, current_time);
    for (i = 1; i < quantity; i++)
    {
        if (jobs[loc].reach_time > current_time)
        {
            jobs[loc].start_time = jobs[loc].reach_time;
            current_time = jobs[loc].reach_time;
        }
        else
        {
            jobs[loc].start_time = current_time;
        }
        jobs[loc].wait_time = current_time - jobs[loc].reach_time;
        printf("  %-8d\t%-8d\t%-8d\t%-8d\t%-8d\n", loc + 1, jobs[loc].reach_time, jobs[loc].start_time, jobs[loc].wait_time, jobs[loc].wait_time + jobs[loc].need_time);
        jobs[loc].visited = 1;
        current_time += jobs[loc].need_time;
        total_waitime += jobs[loc].wait_time;
        total_roundtime = total_roundtime + jobs[loc].wait_time + jobs[loc].need_time;
        loc = findhrrfjob(jobs, quantity, current_time);
    }
    printf("------------------------------------------------------------------------\n");
    printf("总等待时间:%-8d 总周转时间:%-8d\n", total_waitime, total_roundtime);
    printf("平均等待时间: %4.2f 平均周转时间: %4.2f\n", (float)total_waitime / (quantity), (float)total_roundtime / (quantity));
}

int main()
{
    initial_jobs();
    readJobdata();
    FCFS();
    reset_jinfo();
    SFJschdulejob(jobs, quantity);
    reset_jinfo();
    HPF(jobs, quantity);
    reset_jinfo();
    HRRF(jobs, quantity);
    // Ubuntu 下无 system("pause")，替换为交互提示
    printf("\n按回车键退出...");
    getchar();
    getchar();  // 防止输入缓冲区残留导致直接退出
    return 0;
}
