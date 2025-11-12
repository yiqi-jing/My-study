#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<pthread.h>
#include<semaphore.h>

#define N 5
#define TIME_EAT 5
#define TIME_THINK 5
#define LIMIT 4
#define left(phi_id) (phi_id + N - 1) % N
#define right(phi_id) (phi_id + 1) % N
sem_t chopstick[N];
sem_t limit;

void thinking(int id){
    sleep(TIME_THINK);
    printf("philosopher[%d] is thinking.../n", id);
}

void eating(int id){
    sleep(TIME_EAT);
    printf("philosopher[%d] is eating.../n", id);
}

void take_forks(int id){
    sem_wait(&chopstick[left(id)]);
    sem_wait(&chopstick[right(id)]);
    printf("philosopher[%d] is take_forks.../n", id);
}

void put_down_forks(int id){
    printf("philosopher[%d] is put_down_forks.../n", id);
    sem_post(&chopstick[left(id)]);
    sem_post(&chopstick[right(id)]);
}

void *philosopher_work(void *arg){
    int id = *(int *)arg;
    printf("philosopher init[%d]/n", id);
    while(1){
        thinking(id);
        sem_wait(&limit);  // 限制最多4个哲学家同时拿叉子，避免死锁
        take_forks(id);
        sem_post(&limit);
        eating(id);
        put_down_forks(id);
    }
}

int main(){
    pthread_t phiTid[N];
    int i;
    int *id = (int *)malloc(sizeof(int) * N);
    
    // 修复：第二个参数 NULL → 0（线程间共享信号量）
    for(i = 0; i < N; i++){
        sem_init(&chopstick[i], 0, 1);  // 每个筷子初始值为1（可用）
    }
    // 修复：第二个参数 NULL → 0
    sem_init(&limit, 0, LIMIT);  // 限制最多4个哲学家同时尝试拿叉子
    
    for(i = 0; i < N; ++i){
        id[i] = i;
        pthread_create(&phiTid[i], NULL, philosopher_work, (void *)(&id[i]));
    }
    
    while(1);  // 主线程无限循环，避免退出
    exit(0);
}
