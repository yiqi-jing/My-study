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

try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
    print("OpenVINO 已加载")
except ImportError:
    OPENVINO_AVAILABLE = False
    print("警告: OpenVINO 未安装，NPU推理加速不可用")
    print("请运行: pip install openvino")

latent_dim = 100
img_size = 28
channels = 1
batch_size = 64
lr = 0.0002
epochs = 2

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

def convert_to_openvino(generator):
    if not OPENVINO_AVAILABLE:
        print("OpenVINO不可用，跳过转换")
        return None, None
    
    print("\n转换生成器到OpenVINO格式...")
    
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
    
    core = ov.Core()
    model_onnx = core.read_model(onnx_path)
    
    ov.serialize(model_onnx, 'gan_generator.xml', 'gan_generator.bin')
    
    print("OpenVINO模型已保存: gan_generator.xml")
    return core, model_onnx

def check_npu_device(core):
    print("\n检查可用设备:")
    available_devices = core.available_devices
    print(f"可用设备: {available_devices}")
    
    for device in available_devices:
        try:
            device_name = core.get_property(device, 'FULL_DEVICE_NAME')
            print(f"  {device}: {device_name}")
        except:
            print(f"  {device}: (无法获取详细信息)")
    
    if 'NPU' in available_devices:
        print("\n✓ NPU设备可用!")
        return True
    else:
        print("\n✗ NPU设备不可用，将使用CPU")
        return False

def generate_with_npu(core, model_onnx, num_images=16, device_name='NPU'):
    actual_device = device_name
    
    if device_name == 'NPU' and 'NPU' not in core.available_devices:
        device_name = 'GPU' if 'GPU' in core.available_devices else 'CPU'
        print(f"NPU不可用，使用{device_name}")
    
    print(f"\n尝试使用{device_name}生成图像...")
    
    compiled_model = None
    try:
        compiled_model = core.compile_model(model_onnx, device_name)
    except Exception as e:
        print(f"{device_name}编译失败: {e}")
        if device_name == 'NPU':
            print("尝试使用GPU...")
            device_name = 'GPU'
            try:
                compiled_model = core.compile_model(model_onnx, device_name)
            except Exception as e2:
                print(f"GPU编译失败: {e2}")
                device_name = 'CPU'
                compiled_model = core.compile_model(model_onnx, device_name)
        elif device_name == 'GPU':
            device_name = 'CPU'
            compiled_model = core.compile_model(model_onnx, device_name)
    
    if compiled_model is None:
        raise RuntimeError("无法在任何设备上编译模型")
    
    actual_device = device_name
    print(f"使用{actual_device}进行推理...")
    
    output_layer = compiled_model.output(0)
    
    inference_times = []
    generated_images = []
    
    for i in range(num_images):
        z = np.random.randn(1, latent_dim).astype(np.float32)
        
        start_time = time.time()
        result = compiled_model([z])[output_layer]
        inference_time = time.time() - start_time
        inference_times.append(inference_time)
        
        img = result.reshape(1, 28, 28)
        generated_images.append(img)
    
    avg_time = np.mean(inference_times) * 1000
    print(f"平均推理时间: {avg_time:.2f} ms")
    
    return generated_images, avg_time, actual_device

def compare_performance(core, model_onnx, generator, device, num_samples=100):
    print(f"\n性能对比测试 ({num_samples}次推理)...")
    
    generator.eval()
    
    pytorch_times = []
    with torch.no_grad():
        for _ in range(num_samples):
            z = torch.randn(1, latent_dim).to(device)
            start = time.time()
            _ = generator(z)
            pytorch_times.append(time.time() - start)
            if device.type == 'cuda':
                torch.cuda.synchronize()
    pytorch_avg = np.mean(pytorch_times) * 1000
    
    compiled_model_cpu = core.compile_model(model_onnx, 'CPU')
    output_layer = compiled_model_cpu.output(0)
    ov_cpu_times = []
    for _ in range(num_samples):
        z = np.random.randn(1, latent_dim).astype(np.float32)
        start = time.time()
        _ = compiled_model_cpu([z])[output_layer]
        ov_cpu_times.append(time.time() - start)
    ov_cpu_avg = np.mean(ov_cpu_times) * 1000
    
    gpu_avg = None
    if 'GPU' in core.available_devices:
        try:
            compiled_model_gpu = core.compile_model(model_onnx, 'GPU')
            gpu_times = []
            for _ in range(num_samples):
                z = np.random.randn(1, latent_dim).astype(np.float32)
                start = time.time()
                _ = compiled_model_gpu([z])[output_layer]
                gpu_times.append(time.time() - start)
            gpu_avg = np.mean(gpu_times) * 1000
        except Exception as e:
            print(f"GPU编译失败: {e}")
    
    npu_avg = None
    if 'NPU' in core.available_devices:
        try:
            compiled_model_npu = core.compile_model(model_onnx, 'NPU')
            npu_times = []
            for _ in range(num_samples):
                z = np.random.randn(1, latent_dim).astype(np.float32)
                start = time.time()
                _ = compiled_model_npu([z])[output_layer]
                npu_times.append(time.time() - start)
            npu_avg = np.mean(npu_times) * 1000
        except Exception as e:
            print(f"NPU编译失败: {e}")
            print("提示: GAN模型中的某些操作可能不被NPU完全支持")
    
    print("\n" + "="*50)
    print("性能对比结果:")
    print("="*50)
    print(f"PyTorch ({device.type.upper()}):  {pytorch_avg:.2f} ms")
    print(f"OpenVINO CPU:      {ov_cpu_avg:.2f} ms  (加速: {pytorch_avg/ov_cpu_avg:.2f}x)")
    if gpu_avg:
        print(f"OpenVINO GPU:      {gpu_avg:.2f} ms  (加速: {pytorch_avg/gpu_avg:.2f}x)")
    if npu_avg:
        print(f"OpenVINO NPU:      {npu_avg:.2f} ms  (加速: {pytorch_avg/npu_avg:.2f}x)")
    print("="*50)
    
    return pytorch_avg, ov_cpu_avg, npu_avg

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
    print("GAN手写数字生成 - OpenVINO NPU推理加速")
    print("="*60)
    print("\n说明:")
    print("- 训练阶段: 使用PyTorch (CPU/CUDA)")
    print("- 推理阶段: 使用OpenVINO (CPU/NPU)")
    print("- Windows上NPU通过OpenVINO完全支持")
    
    device = get_device()
    
    generator, discriminator = train_gan(device, epochs=epochs)
    
    print("\n保存PyTorch模型...")
    torch.save(generator.state_dict(), 'generator.pth')
    torch.save(discriminator.state_dict(), 'discriminator.pth')
    
    if not OPENVINO_AVAILABLE:
        print("\nOpenVINO未安装，跳过NPU推理测试")
        print("请安装: pip install openvino")
        return
    
    core, model_onnx = convert_to_openvino(generator)
    
    if core and model_onnx:
        npu_available = check_npu_device(core)
        
        pytorch_avg, ov_cpu_avg, npu_avg = compare_performance(
            core, model_onnx, generator, device, num_samples=100
        )
        
        print("\n生成最终图像...")
        best_device = 'NPU' if npu_avg else ('GPU' if 'GPU' in core.available_devices else 'CPU')
        generated_images, avg_time, actual_device = generate_with_npu(
            core, model_onnx, num_images=16, device_name=best_device
        )
        
        fig = visualize_results(generated_images, f"OpenVINO {actual_device} 生成结果")
        plt.savefig('gan_npu_results.png')
        plt.show()
    
    print("\n" + "="*60)
    print("实验完成!")
    print("="*60)

if __name__ == '__main__':
    main()
