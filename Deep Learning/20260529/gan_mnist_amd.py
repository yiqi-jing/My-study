﻿import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import time

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DIRECTML_AVAILABLE = False
OPENVINO_AVAILABLE = False

try:
    import onnxruntime as ort
    providers = ort.get_available_providers()
    if 'DmlExecutionProvider' in providers:
        DIRECTML_AVAILABLE = True
        print("ONNX Runtime DirectML 已加载 (AMD GPU支持)")
    else:
        print("ONNX Runtime 已加载，但DirectML不可用")
        print("请安装: pip install onnxruntime-directml")
except ImportError:
    print("ONNX Runtime 未安装")
    print("请安装: pip install onnxruntime-directml")

try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
    print("OpenVINO 已加载")
except ImportError:
    print("OpenVINO 未安装")

latent_dim = 100
img_size = 28
channels = 1
batch_size = 64
lr = 0.0002
epochs = 50

class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        
        def block(in_feat, out_feat, normalize=True):
            layers = [nn.Linear(in_feat, out_feat)]
            if normalize:
                layers.append(nn.BatchNorm1d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers
        
        self.model = nn.Sequential(
            *block(latent_dim, 128, normalize=False),
            *block(128, 256),
            *block(256, 512),
            *block(512, 1024),
            nn.Linear(1024, channels * img_size * img_size),
            nn.Tanh()
        )
    
    def forward(self, z):
        img = self.model(z)
        img = img.view(img.size(0), channels, img_size, img_size)
        return img

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(channels * img_size * img_size, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, img):
        img_flat = img.view(img.size(0), -1)
        validity = self.model(img_flat)
        return validity

def get_device():
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"使用CUDA设备: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device('cpu')
        print("使用CPU进行训练")
    return device

def train_gan(device, epochs=50):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    
    dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    generator = Generator().to(device)
    discriminator = Discriminator().to(device)
    
    adversarial_loss = nn.BCELoss()
    
    optimizer_G = optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
    optimizer_D = optim.Adam(discriminator.parameters(), lr=lr, betas=(0.5, 0.999))
    
    G_losses = []
    D_losses = []
    
    print(f"\n开始训练GAN...")
    start_time = time.time()
    
    for epoch in range(epochs):
        epoch_G_loss = 0
        epoch_D_loss = 0
        epoch_start = time.time()
        
        for i, (imgs, _) in enumerate(dataloader):
            batch_size_curr = imgs.shape[0]
            
            valid = torch.ones(batch_size_curr, 1).to(device)
            fake = torch.zeros(batch_size_curr, 1).to(device)
            
            real_imgs = imgs.to(device)
            
            optimizer_G.zero_grad()
            
            z = torch.randn(batch_size_curr, latent_dim).to(device)
            gen_imgs = generator(z)
            
            g_loss = adversarial_loss(discriminator(gen_imgs), valid)
            
            g_loss.backward()
            optimizer_G.step()
            
            optimizer_D.zero_grad()
            
            real_loss = adversarial_loss(discriminator(real_imgs), valid)
            fake_loss = adversarial_loss(discriminator(gen_imgs.detach()), fake)
            d_loss = (real_loss + fake_loss) / 2
            
            d_loss.backward()
            optimizer_D.step()
            
            epoch_G_loss += g_loss.item()
            epoch_D_loss += d_loss.item()
        
        avg_G_loss = epoch_G_loss / len(dataloader)
        avg_D_loss = epoch_D_loss / len(dataloader)
        G_losses.append(avg_G_loss)
        D_losses.append(avg_D_loss)
        
        epoch_time = time.time() - epoch_start
        print(f"[Epoch {epoch+1}/{epochs}] D loss: {avg_D_loss:.4f} | G loss: {avg_G_loss:.4f} | Time: {epoch_time:.2f}s")
        
        if (epoch + 1) % 10 == 0:
            generator.eval()
            with torch.no_grad():
                z = torch.randn(25, latent_dim).to(device)
                gen_imgs = generator(z).cpu()
                
                fig, axes = plt.subplots(5, 5, figsize=(10, 10))
                for ax in axes.flatten():
                    ax.axis('off')
                
                for j in range(25):
                    ax = axes[j // 5, j % 5]
                    ax.imshow(gen_imgs[j].squeeze(), cmap='gray', vmin=-1, vmax=1)
                
                plt.tight_layout()
                plt.savefig(f'gan_generated_epoch_{epoch+1}.png')
                plt.close()
            generator.train()
    
    total_time = time.time() - start_time
    print(f"\n训练完成! 总耗时: {total_time:.2f}秒")
    
    plt.figure(figsize=(10, 5))
    plt.plot(G_losses, label='Generator Loss')
    plt.plot(D_losses, label='Discriminator Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('GAN Training Loss')
    plt.savefig('gan_loss_curve.png')
    plt.close()
    
    return generator, discriminator

def convert_to_onnx(generator):
    print("\n转换生成器到ONNX格式...")
    
    class GeneratorWrapper(nn.Module):
        def __init__(self, gen):
            super().__init__()
            self.gen = gen
        
        def forward(self, z):
            return self.gen(z)
    
    wrapped_gen = GeneratorWrapper(generator)
    wrapped_gen.eval()
    
    for module in wrapped_gen.modules():
        if isinstance(module, nn.BatchNorm1d):
            module.eval()
    
    dummy_input = torch.randn(1, latent_dim)
    
    onnx_path = 'gan_generator.onnx'
    torch.onnx.export(wrapped_gen, dummy_input, onnx_path,
                     input_names=['latent'],
                     output_names=['generated_image'],
                     dynamo=False)
    
    print(f"ONNX模型已保存: {onnx_path}")
    return onnx_path

def check_devices():
    print("\n检查可用设备:")
    
    devices = []
    
    if DIRECTML_AVAILABLE:
        print("  DirectML (AMD GPU): 可用")
        devices.append('DirectML')
    
    if OPENVINO_AVAILABLE:
        core = ov.Core()
        available_devices = core.available_devices
        print(f"  OpenVINO设备: {available_devices}")
        for d in available_devices:
            try:
                name = core.get_property(d, 'FULL_DEVICE_NAME')
                print(f"    {d}: {name}")
            except:
                pass
            devices.append(f'OpenVINO.{d}')
    
    print(f"  CPU: 可用")
    devices.append('CPU')
    
    return devices

def benchmark_onnxruntime(onnx_path, generator, device, num_samples=100):
    print(f"\nONNX Runtime 性能测试 ({num_samples}次推理)...")
    
    generator.eval()
    
    pytorch_times = []
    with torch.no_grad():
        for _ in range(num_samples):
            z = torch.randn(1, latent_dim).to(device)
            start = time.time()
            _ = generator(z)
            pytorch_times.append(time.time() - start)
    pytorch_avg = np.mean(pytorch_times) * 1000
    
    results = {'PyTorch': pytorch_avg}
    
    sess_cpu = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    cpu_times = []
    for _ in range(num_samples):
        z = np.random.randn(1, latent_dim).astype(np.float32)
        start = time.time()
        _ = sess_cpu.run(None, {'latent': z})
        cpu_times.append(time.time() - start)
    cpu_avg = np.mean(cpu_times) * 1000
    results['ONNX CPU'] = cpu_avg
    
    if DIRECTML_AVAILABLE:
        try:
            sess_dml = ort.InferenceSession(onnx_path, providers=['DmlExecutionProvider'])
            dml_times = []
            for _ in range(num_samples):
                z = np.random.randn(1, latent_dim).astype(np.float32)
                start = time.time()
                _ = sess_dml.run(None, {'latent': z})
                dml_times.append(time.time() - start)
            dml_avg = np.mean(dml_times) * 1000
            results['DirectML (AMD)'] = dml_avg
        except Exception as e:
            print(f"DirectML测试失败: {e}")
    
    return results

def benchmark_openvino(onnx_path, generator, device, num_samples=100):
    if not OPENVINO_AVAILABLE:
        return {}
    
    print(f"\nOpenVINO 性能测试 ({num_samples}次推理)...")
    
    core = ov.Core()
    model = core.read_model(onnx_path)
    
    results = {}
    
    try:
        compiled_cpu = core.compile_model(model, 'CPU')
        output = compiled_cpu.output(0)
        cpu_times = []
        for _ in range(num_samples):
            z = np.random.randn(1, latent_dim).astype(np.float32)
            start = time.time()
            _ = compiled_cpu([z])[output]
            cpu_times.append(time.time() - start)
        results['OpenVINO CPU'] = np.mean(cpu_times) * 1000
    except Exception as e:
        print(f"OpenVINO CPU失败: {e}")
    
    if 'GPU' in core.available_devices:
        try:
            compiled_gpu = core.compile_model(model, 'GPU')
            output = compiled_gpu.output(0)
            gpu_times = []
            for _ in range(num_samples):
                z = np.random.randn(1, latent_dim).astype(np.float32)
                start = time.time()
                _ = compiled_gpu([z])[output]
                gpu_times.append(time.time() - start)
            results['OpenVINO GPU'] = np.mean(gpu_times) * 1000
        except Exception as e:
            print(f"OpenVINO GPU失败: {e}")
    
    if 'NPU' in core.available_devices:
        try:
            compiled_npu = core.compile_model(model, 'NPU')
            output = compiled_npu.output(0)
            npu_times = []
            for _ in range(num_samples):
                z = np.random.randn(1, latent_dim).astype(np.float32)
                start = time.time()
                _ = compiled_npu([z])[output]
                npu_times.append(time.time() - start)
            results['OpenVINO NPU'] = np.mean(npu_times) * 1000
        except Exception as e:
            print(f"OpenVINO NPU失败: {e}")
    
    return results

def generate_images(onnx_path, num_images=16, device_name='DirectML'):
    print(f"\n使用{device_name}生成图像...")
    
    if device_name == 'DirectML' and DIRECTML_AVAILABLE:
        sess = ort.InferenceSession(onnx_path, providers=['DmlExecutionProvider'])
    elif device_name.startswith('OpenVINO.'):
        if not OPENVINO_AVAILABLE:
            raise RuntimeError("OpenVINO不可用")
        core = ov.Core()
        ov_device = device_name.split('.')[1]
        model = core.read_model(onnx_path)
        compiled = core.compile_model(model, ov_device)
        output = compiled.output(0)
        
        inference_times = []
        images = []
        for _ in range(num_images):
            z = np.random.randn(1, latent_dim).astype(np.float32)
            start = time.time()
            result = compiled([z])[output]
            inference_times.append(time.time() - start)
            images.append(result.reshape(1, 28, 28))
        
        avg_time = np.mean(inference_times) * 1000
        print(f"平均推理时间: {avg_time:.2f} ms")
        return images, avg_time
    else:
        sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    
    inference_times = []
    images = []
    for _ in range(num_images):
        z = np.random.randn(1, latent_dim).astype(np.float32)
        start = time.time()
        result = sess.run(None, {'latent': z})[0]
        inference_times.append(time.time() - start)
        images.append(result.reshape(1, 28, 28))
    
    avg_time = np.mean(inference_times) * 1000
    print(f"平均推理时间: {avg_time:.2f} ms")
    return images, avg_time

def visualize_results(images, title="Generated Images"):
    n = len(images)
    rows = int(np.ceil(np.sqrt(n)))
    cols = int(np.ceil(n / rows))
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols*2, rows*2))
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1 or cols == 1:
        axes = axes.reshape(rows, cols)
    
    for i in range(rows * cols):
        ax = axes[i // cols, i % cols]
        if i < n:
            ax.imshow(images[i].squeeze(), cmap='gray', vmin=-1, vmax=1)
        ax.axis('off')
    
    plt.suptitle(title)
    plt.tight_layout()
    return fig

def main():
    print("="*60)
    print("GAN手写数字生成 - AMD GPU (DirectML) 加速")
    print("="*60)
    print("\n说明:")
    print("- 训练阶段: 使用PyTorch CPU (AMD GPU训练需要ROCm,仅Linux)")
    print("- 推理阶段: 使用ONNX Runtime DirectML (AMD GPU)")
    print("- Windows上AMD GPU通过DirectML完全支持")
    
    devices = check_devices()
    device = get_device()
    
    generator, discriminator = train_gan(device, epochs=epochs)
    
    print("\n保存PyTorch模型...")
    torch.save(generator.state_dict(), 'generator.pth')
    torch.save(discriminator.state_dict(), 'discriminator.pth')
    
    onnx_path = convert_to_onnx(generator)
    
    onnx_results = benchmark_onnxruntime(onnx_path, generator, device, num_samples=100)
    ov_results = benchmark_openvino(onnx_path, generator, device, num_samples=100)
    
    all_results = {**onnx_results, **ov_results}
    
    print("\n" + "="*60)
    print("性能对比结果:")
    print("="*60)
    
    baseline = all_results.get('PyTorch', 1)
    for name, time_ms in sorted(all_results.items(), key=lambda x: x[1]):
        if name == 'PyTorch':
            print(f"{name:20s}: {time_ms:.2f} ms")
        else:
            speedup = baseline / time_ms
            print(f"{name:20s}: {time_ms:.2f} ms  (加速: {speedup:.2f}x)")
    print("="*60)
    
    best_device = None
    best_time = float('inf')
    for name, time_ms in all_results.items():
        if name != 'PyTorch' and time_ms < best_time:
            best_time = time_ms
            if 'DirectML' in name:
                best_device = 'DirectML'
            elif name.startswith('OpenVINO'):
                best_device = name
            elif 'ONNX' in name:
                best_device = 'CPU'
    
    if best_device is None:
        best_device = 'CPU'
    
    print(f"\n使用最快设备 ({best_device}) 生成最终图像...")
    images, _ = generate_images(onnx_path, num_images=16, device_name=best_device)
    
    fig = visualize_results(images, f"GAN生成结果 ({best_device})")
    plt.savefig('gan_amd_results.png')
    plt.show()
    
    print("\n" + "="*60)
    print("实验完成!")
    print("="*60)

if __name__ == '__main__':
    main()
