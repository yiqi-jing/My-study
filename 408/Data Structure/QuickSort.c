#include <stdio.h>

// 交换两个整数的值
void Swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}

// 对 arr[low..high] 进行一趟划分
// 选取最后一个元素 arr[high] 作为枢轴 pivot
// 将数组分成两部分：
// 左边：<= pivot
// 右边：> pivot
// 返回枢轴元素最终所在位置
int Partition(int arr[], int low, int high)
{
    int pivot = arr[high]; // 枢轴元素
    int i = low - 1;       // i 表示“<= pivot 区”的最后一个位置

    for (int j = low; j < high; j++)
    {
        // 如果当前元素小于等于枢轴，则放到左侧区域
        if (arr[j] <= pivot)
        {
            i++;
            Swap(&arr[i], &arr[j]);
        }
    }

    // 将枢轴放到最终位置
    Swap(&arr[i + 1], &arr[high]);
    return i + 1; // 返回枢轴位置
}

// 快速排序主过程：递归地对左右子区间继续排序
void QuickSort(int arr[], int low, int high)
{
    if (low < high)
    {
        int pivotIndex = Partition(arr, low, high); // 一次划分
        QuickSort(arr, low, pivotIndex - 1);       // 排序左半部分
        QuickSort(arr, pivotIndex + 1, high);      // 排序右半部分
    }
}

// 打印数组内容
void PrintArray(int arr[], int n)
{
    for (int i = 0; i < n; i++)
    {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main(void)
{
    int arr[] = {49, 38, 65, 97, 76, 13, 27, 49};
    int n = sizeof(arr) / sizeof(arr[0]);

    printf("排序前：\n");
    PrintArray(arr, n);

    // 对整个数组进行快速排序
    QuickSort(arr, 0, n - 1);

    printf("排序后：\n");
    PrintArray(arr, n);

    return 0;
}

