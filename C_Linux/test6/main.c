#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<pthread.h>
#include<semaphore.h>
#include<inttypes.h>  // 仅添加这一个头文件（用于intptr_t类型）

#define PRODUCER_NUM 5
#define CONSUMER_NUM 5
#define POOL_SIZE 11

int pool [POOL_SIZE];
int head = 0;
int rear = 0;
sem_t empty_sem;
sem_t full_sem;
pthread_mutex_t mutex;

void *producer_fun(void *arg)
{
    while (1)
    {
        sleep(1);
            sem_wait(&empty_sem);
            pthread_mutex_lock(&mutex);
            pool[rear] = 1;
            rear = (rear + 1)%POOL_SIZE;
            // 改动1：(int)arg → (int)(intptr_t)arg
            printf("profucer %d write to pool/n",(int)(intptr_t)arg);
            printf("pool size is %d/n",(rear - head + POOL_SIZE)%POOL_SIZE);
            pthread_mutex_unlock(&mutex);
            sem_post(&full_sem);
    
    }
}

void *consumer_fun(void *arg)
{
    while (1)
    {
        int data;
        sleep(10);
        sem_wait(&full_sem);
        pthread_mutex_lock(&mutex);
        data = pool[head];
        head = (head + 1)%POOL_SIZE;
        // 改动2：(int)arg → (int)(intptr_t)arg
        printf("consumer [%d] read from pool/n",(int)(intptr_t)arg);
        printf("pool size is [%d]/n",(rear - head + POOL_SIZE)%POOL_SIZE);
        pthread_mutex_unlock(&mutex);
        sem_post(&empty_sem);
        /* code */
    }
}

int main()
{
    int i ;
    pthread_t producer_id[PRODUCER_NUM];
    pthread_t consumer_id[CONSUMER_NUM];
    pthread_mutex_init(&mutex,NULL);
    sem_init(&empty_sem,0,POOL_SIZE-1);
    sem_init(&full_sem,0,0);
    for ( i = 0; i < PRODUCER_NUM; i++)
    {
        // 改动3：(void *)i → (void*)(intptr_t)i（两处都改）
        pthread_create(&producer_id[i],NULL,producer_fun,(void*)(intptr_t)i);
        pthread_create(&consumer_id[i],NULL,consumer_fun,(void*)(intptr_t)i);
        /* code */
    }
    for ( i = 0; i < PRODUCER_NUM; i++)
    {
        pthread_join(producer_id[i], NULL);
        pthread_join(producer_id[i], NULL);
        /* code */
    }
    exit(0);
}
