#include<stdio.h>  // 新增：printf函数的声明头文件
#include<stdlib.h>
#include<unistd.h>
#include<pthread.h>
#include<semaphore.h>
#include<string.h>
#include<stdbool.h>

sem_t mutex1, mutex2, amount, empty, full;
int fullcount = 0;  // 水缸水量（全局变量，需通过mutex2保护）

void *LittleMonk(void *p) {
    while (true) {
        sem_wait(&empty);    // 等待水缸有空位（最多10桶水）
        sem_wait(&amount);   // 限制同时操作的和尚数量（最多3个）
        sem_wait(&mutex1);   // 保护水井操作（同一时间只能1个小和尚提水）
        printf("第%d个小和尚在水井提水\n", *(int *)p);
        sem_post(&mutex1);
        
        sem_wait(&mutex2);   // 保护水缸操作（修改fullcount需互斥）
        printf("水缸已有%d桶水，第%d个小和尚在水缸旁倒水\n", fullcount, *(int *)p);
        fullcount++;
        sem_post(&mutex2);
        
        sem_post(&amount);
        sem_post(&full);     // 通知水缸有新水（full计数+1）
    }
}

void *BigMonk(void *p) {
    while (true) {
        sem_wait(&full);     // 等待水缸有水
        sem_wait(&amount);   // 限制同时操作的和尚数量（最多3个）
        sem_wait(&mutex2);   // 保护水缸操作（修改fullcount需互斥）
        printf("\t水缸已有%d桶水,第%d个大和尚在水缸旁提水\n", fullcount, *(int *)p);
        fullcount--;
        sem_post(&mutex2);
        
        sem_post(&amount);
        sem_post(&empty);    // 通知水缸有空位（empty计数+1）
    }
}

int main() {
    int i, j;
    pthread_t little[20], big[20];
    // 初始化信号量（第二个参数0表示线程间共享）
    sem_init(&mutex1, 0, 1);    // 水井互斥锁（1表示独占）
    sem_init(&mutex2, 0, 1);    // 水缸互斥锁（保护fullcount）
    sem_init(&amount, 0, 3);    // 同时操作的和尚数量限制（3个）
    sem_init(&full, 0, 0);      // 水缸有水的数量（初始0）
    sem_init(&empty, 0, 10);    // 水缸空位数量（初始10）

    // 创建3个大和尚线程（修复：用动态内存存储ID，避免野指针）
    for (i = 1; i < 4; ++i) {
        int *id = malloc(sizeof(int));  // 为每个线程分配独立的ID内存
        *id = i;
        pthread_create(&big[i], NULL, BigMonk, (void *)id);
    }

    // 创建10个小和尚线程（修复：用动态内存存储ID，避免野指针）
    for (j = 1; j <= 10; ++j) {
        int *id = malloc(sizeof(int));  // 每个线程的ID独立，不会被覆盖
        *id = j;
        pthread_create(&little[j], NULL, LittleMonk, (void *)id);
    }

    // 主线程阻塞（避免主线程退出导致子线程被终止）
    pthread_exit(NULL);  // 比while(1)更优雅，主线程退出但子线程继续运行
    exit(0);
}
