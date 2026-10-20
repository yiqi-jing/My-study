void quickSort(int arr[], int low, int high){
    if(low < high){
        int pivotloc = partition(arr, low, high); //对当前子数组进行划分
        quickSort(arr, low, pivotloc - 1); //递归地对左子数组进行排序
        quickSort(arr, pivotloc +1, high); //递归地对右子数组进行排序
    }
}

// 划分函数
int partion (int arr[], int low, int high){
    int pivot = arr[low]; //选择第一个元素作为枢轴
    while(low < high){
        while(low < high && arr[high] >= pivot)
            --high;
        arr[low] = arr[high];
        while(low < high && arr[low] <= pivot)
            ++low;
        arr[high] = arr[low]; 
    }
    arr[low] = arr[high];
    return low;
}


// 归并排序（408考研的简单书写格式）
void mergeSort(int arr[], int low, int high){
    if(low < high){
        int mid = (low + high) / 2; //找到中间位置
        mergeSort(arr, low, mid); //递归地对左子数组进行排序
        mergeSort(arr, mid + 1, high); //递归地对右子数组进行排序
        merge(arr, low, mid, high); //合并两个有序子数组
    }
}

// 合并函数
void merge(int arr[], int low, int mid, int high){
    int i = low; //左子数组的起始索引
    int j = mid + 1; //右子数组的起始索引
    int k = 0; //临时数组的索引
    int temp[high - low + 1]; //临时数组

    while(i <= mid && j <= high){
        if(arr[i] <= arr[j]){
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }

    while(i <= mid){
        temp[k++] = arr[i++];
    }

    while(j <= high){
        temp[k++] = arr[j++];
    }

    for(i = 0; i < k; i++){
        arr[low + i] = temp[i];
    }
}