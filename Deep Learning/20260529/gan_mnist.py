import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")

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

print("开始训练GAN...")

for epoch in range(epochs):
    epoch_G_loss = 0
    epoch_D_loss = 0
    
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
    
    print(f"[Epoch {epoch+1}/{epochs}] D loss: {avg_D_loss:.4f} | G loss: {avg_G_loss:.4f}")
    
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

plt.figure(figsize=(10, 5))
plt.plot(G_losses, label='Generator Loss')
plt.plot(D_losses, label='Discriminator Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('GAN Training Loss')
plt.savefig('gan_loss_curve.png')
plt.close()

print("\n训练完成！")
print("生成器模型已保存为 generator.pth")
print("判别器模型已保存为 discriminator.pth")

torch.save(generator.state_dict(), 'generator.pth')
torch.save(discriminator.state_dict(), 'discriminator.pth')

generator.eval()
with torch.no_grad():
    z = torch.randn(16, latent_dim).to(device)
    gen_imgs = generator(z).cpu()
    
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i, ax in enumerate(axes.flatten()):
        ax.imshow(gen_imgs[i].squeeze(), cmap='gray', vmin=-1, vmax=1)
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('gan_final_results.png')
    plt.show()

print("\n生成的图像已保存为 gan_final_results.png")
