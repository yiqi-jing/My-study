import numpy as np
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import openvino.runtime as ov
import time
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class CNN(nn.Module):
    """卷积神经网络模型"""
    def __init__(self):
        super(CNN, self).__init__()

        self.conv_block = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU()
        )

        self.fc_block = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )

    def forward(self, x):
        x = self.conv_block(x)
        x = self.fc_block(x)
        return x

def load_and_preprocess_data():
    """加载MNIST数据集"""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

    x_train = train_dataset.data.numpy().reshape((60000, 1, 28, 28)).astype(np.float32) / 255
    y_train = train_dataset.targets.numpy().astype(np.int64)

    x_test = test_dataset.data.numpy().reshape((10000, 1, 28, 28)).astype(np.float32) / 255
    y_test = test_dataset.targets.numpy().astype(np.int64)

    return (x_train, y_train), (x_test, y_test)

def train_model(x_train, y_train, x_test, y_test, epochs=5):
    """训练模型"""
    train_dataset = torch.utils.data.TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train))
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

    model = CNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

            if batch_idx % 300 == 299:
                print(f'Epoch {epoch+1}, Batch {batch_idx+1}: Loss: {running_loss/300:.3f}, Acc: {100.*correct/total:.2f}%')
                running_loss = 0.0

    return model

def convert_to_openvino(model):
    """转换模型为OpenVINO格式"""
    dummy_input = torch.randn(1, 1, 28, 28)

    onnx_path = 'mnist_cnn_model.onnx'
    torch.onnx.export(model, dummy_input, onnx_path,
                     input_names=['input'],
                     output_names=['output'])

    core = ov.Core()
    model_onnx = core.read_model(onnx_path)

    ov.serialize(model_onnx, 'mnist_cnn_model.xml', 'mnist_cnn_model.bin')

    return core, model_onnx

def evaluate_model_cpu(model, x_test, y_test):
    """使用PyTorch CPU评估模型"""
    model.eval()
    correct = 0
    total = 0
    inference_times = []

    with torch.no_grad():
        for i in range(len(x_test)):
            data = torch.from_numpy(x_test[i:i+1])
            target = y_test[i]

            start_time = time.time()
            output = model(data)
            inference_time = time.time() - start_time
            inference_times.append(inference_time)

            pred = output.argmax(1).item()
            if pred == target:
                correct += 1
            total += 1

            if i >= 999:
                break

    accuracy = 100. * correct / total
    avg_time = np.mean(inference_times) * 1000
    return accuracy, avg_time

def evaluate_model_npu(core, model_onnx, x_test, y_test):
    """使用OpenVINO NPU评估模型"""
    compiled_model = core.compile_model(model_onnx, 'NPU')
    output_layer = compiled_model.output(0)

    correct = 0
    total = 0
    inference_times = []

    with torch.no_grad():
        for i in range(len(x_test)):
            input_data = x_test[i:i+1]

            start_time = time.time()
            result = compiled_model([input_data])[output_layer]
            inference_time = time.time() - start_time
            inference_times.append(inference_time)

            pred = np.argmax(result, axis=1)[0]
            if pred == y_test[i]:
                correct += 1
            total += 1

            if i >= 999:
                break

    accuracy = 100. * correct / total
    avg_time = np.mean(inference_times) * 1000
    return accuracy, avg_time

def predict_and_visualize(core, model_onnx, x_test, y_test, num_samples=10):
    """预测并可视化结果"""
    compiled_model = core.compile_model(model_onnx, 'NPU')
    output_layer = compiled_model.output(0)

    indices = np.random.randint(0, min(1000, len(x_test)), num_samples)
    sample_images = x_test[indices]
    sample_labels = y_test[indices]

    predictions = []
    with torch.no_grad():
        for i in range(len(sample_images)):
            input_data = sample_images[i:i+1]
            result = compiled_model([input_data])[output_layer]
            pred = np.argmax(result, axis=1)[0]
            predictions.append(pred)

    plt.figure(figsize=(15, 6))
    for i in range(num_samples):
        plt.subplot(2, 5, i + 1)
        plt.imshow(sample_images[i].squeeze(), cmap='gray')
        plt.axis('off')
        plt.title(f'True: {sample_labels[i]}\nPred: {predictions[i]}')
    plt.tight_layout()
    plt.show()

def main():
    print("=== 卷积神经网络与手写数字识别实验 (PyTorch + OpenVINO NPU) ===")

    print("\n1. 加载MNIST数据集...")
    (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
    print(f"训练集大小: {x_train.shape}")
    print(f"测试集大小: {x_test.shape}")

    print("\n2. 构建并训练模型...")
    model = train_model(x_train, y_train, x_test, y_test, epochs=5)

    print("\n3. 转换为OpenVINO格式...")
    core, model_onnx = convert_to_openvino(model)

    print("\n4. 检查可用设备...")
    available_devices = core.available_devices
    print(f"可用设备: {available_devices}")
    for device in available_devices:
        device_name = core.get_property(device, 'FULL_DEVICE_NAME')
        print(f"  {device}: {device_name}")

    print("\n5. CPU推理评估...")
    cpu_accuracy, cpu_time = evaluate_model_cpu(model, x_test, y_test)
    print(f"CPU准确率: {cpu_accuracy:.4f}%")
    print(f"CPU平均推理时间: {cpu_time:.2f} ms")

    print("\n6. NPU推理评估...")
    npu_accuracy, npu_time = evaluate_model_npu(core, model_onnx, x_test, y_test)
    print(f"NPU准确率: {npu_accuracy:.4f}%")
    print(f"NPU平均推理时间: {npu_time:.2f} ms")

    print("\n7. 性能对比...")
    print(f"速度提升: {cpu_time/npu_time:.2f}x")

    print("\n8. 预测可视化...")
    predict_and_visualize(core, model_onnx, x_test, y_test)

    print("\n=== 实验完成 ===")

if __name__ == '__main__':
    main()
