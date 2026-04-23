import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# ======================
# 中文显示
# ======================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ======================
# 设备检测（训练永远用 CPU，推理用 NPU）
# ======================
print('=== 设备信息 ===')
print(f'PyTorch版本: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')

# 训练只能用 CPU
device_train = torch.device('cpu')
print(f'训练使用设备: {device_train}')

# ======================
# 随机种子
# ======================
torch.manual_seed(42)
np.random.seed(42)

# ======================
# 数据
# ======================
def generate_data(n_samples=100):
    x = np.random.rand(n_samples, 1) * 10
    y = 2 * x + 3 + np.random.randn(n_samples, 1) * 0.5
    return x, y

# ======================
# 模型
# ======================
class SingleNeuronModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)
    def forward(self, x):
        return self.linear(x)

# ======================
# 训练（CPU）
# ======================
def train_model(model, X_train, y_train, epochs=1000, lr=0.01):
    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    losses = []
    
    for epoch in range(epochs):
        y_pred = model(X_train)
        loss = criterion(y_pred, y_train)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        losses.append(loss.item())
        if (epoch+1) % 100 == 0:
            print(f'Epoch {epoch+1:4d} | Loss: {loss.item():.4f}')
    return losses

# ======================
# NPU 推理（核心！你电脑能跑）
# ======================
def predict_with_npu(model, x):
    try:
        import onnxruntime as ort
        import tempfile
        import os

        model.eval()
        dummy = torch.randn(1, 1).float()

        # 导出 ONNX
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp:
            torch.onnx.export(model, dummy, tmp.name, opset_version=12)

        # NPU 加速推理
        providers = ['NpuExecutionProvider', 'CPUExecutionProvider']
        sess = ort.InferenceSession(tmp.name, providers=providers)
        
        print(f"\n 推理使用设备: {sess.get_providers()[0]}")
        out = sess.run(None, {'input.1': x.astype(np.float32)})[0]
        
        os.unlink(tmp.name)
        return out
    except:
        print("\n NPU 不可用，使用 CPU 推理")
        with torch.no_grad():
            return model(torch.tensor(x, dtype=torch.float32)).numpy()

# ======================
# 主程序
# ======================
def main():
    x, y = generate_data()
    
    # 训练用 CPU
    X_train = torch.tensor(x, dtype=torch.float32).to(device_train)
    y_train = torch.tensor(y, dtype=torch.float32).to(device_train)
    
    model = SingleNeuronModel().to(device_train)
    print("\n初始权重:")
    for n, p in model.named_parameters():
        print(f"  {n}: {p.data.numpy()}")
    
    print("\n开始训练...")
    losses = train_model(model, X_train, y_train)
    
    print("\n训练完成:")
    for n, p in model.named_parameters():
        print(f"  {n}: {p.data.numpy()}")
    
    # ======================
    # NPU 推理
    # ======================
    y_pred = predict_with_npu(model, x)
    
    # 保存模型
    print("\n保存模型...")
    import os
    model_dir = 'f:\\My-study\\Model'
    os.makedirs(model_dir, exist_ok=True)
    
    # 保存 PyTorch 模型
    model_path = os.path.join(model_dir, 'single_neuron_model.pth')
    torch.save(model.state_dict(), model_path)
    print(f"模型已保存为 {model_path}")
    
    # 保存 ONNX 模型
    onnx_path = os.path.join(model_dir, 'single_neuron_model.onnx')
    dummy = torch.randn(1, 1).float()
    torch.onnx.export(model, dummy, onnx_path, opset_version=12)
    print(f"ONNX 模型已保存为 {onnx_path}")
    
    # 绘图
    plt.figure(figsize=(12,5))
    
    plt.subplot(1,2,1)
    plt.plot(losses)
    plt.title('训练损失')
    
    plt.subplot(1,2,2)
    plt.scatter(x, y)
    plt.plot(x, y_pred, 'r', linewidth=2)
    plt.title('NPU 推理结果')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()