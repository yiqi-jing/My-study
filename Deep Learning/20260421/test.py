import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 1. 加载和预处理数据
def load_and_preprocess_data():
    """加载MNIST数据集并进行预处理"""
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # 数据预处理
    x_train = x_train.reshape((60000, 28, 28, 1))
    x_test = x_test.reshape((10000, 28, 28, 1))
    
    # 归一化
    x_train = x_train.astype('float32') / 255
    x_test = x_test.astype('float32') / 255
    
    # 标签独热编码
    y_train = tf.keras.utils.to_categorical(y_train, 10)
    y_test = tf.keras.utils.to_categorical(y_test, 10)
    
    return (x_train, y_train), (x_test, y_test)

# 2. 构建卷积神经网络模型
def build_cnn_model():
    """构建卷积神经网络模型"""
    model = models.Sequential()
    
    # 第一层卷积层
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
    model.add(layers.MaxPooling2D((2, 2)))
    
    # 第二层卷积层
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    
    # 第三层卷积层
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    
    # 展平层
    model.add(layers.Flatten())
    
    # 全连接层
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(10, activation='softmax'))
    return model

# 3. 训练模型
def train_model(model, x_train, y_train, x_test, y_test, epochs=5):
    """训练模型并评估性能"""
    # 编译模型
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    # 训练模型
    history = model.fit(x_train, y_train, epochs=epochs, validation_data=(x_test, y_test))
    
    return history

# 4. 评估模型
def evaluate_model(model, x_test, y_test):
    """评估模型性能"""
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
    print(f'测试准确率: {test_acc:.4f}')
    return test_acc

# 5. 预测和可视化
def predict_and_visualize(model, x_test, y_test, num_samples=5):
    """预测并可视化结果"""
    # 随机选择测试样本
    indices = np.random.randint(0, x_test.shape[0], num_samples)
    sample_images = x_test[indices]
    sample_labels = y_test[indices]
    
    # 预测
    predictions = model.predict(sample_images)
    
    # 可视化
    plt.figure(figsize=(10, 4))
    for i in range(num_samples):
        plt.subplot(1, num_samples, i + 1)
        plt.imshow(sample_images[i].reshape(28, 28), cmap='gray')
        plt.axis('off')
        true_label = np.argmax(sample_labels[i])
        pred_label = np.argmax(predictions[i])
        plt.title(f'True: {true_label}\nPred: {pred_label}')
    plt.tight_layout()
    plt.show()

# 6. 主函数
def main():
    print("=== 卷积神经网络与手写数字识别实验 ===")
    
    # 加载数据
    print("1. 加载MNIST数据集...")
    (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
    print(f"训练集大小: {x_train.shape}")
    print(f"测试集大小: {x_test.shape}")
    
    # 构建模型
    print("\n2. 构建卷积神经网络模型...")
    model = build_cnn_model()
    model.summary()
    
    # 训练模型
    print("\n3. 训练模型...")
    history = train_model(model, x_train, y_train, x_test, y_test, epochs=5)
    
    # 评估模型
    print("\n4. 评估模型...")
    test_acc = evaluate_model(model, x_test, y_test)
    
    # 预测和可视化
    print("\n5. 预测和可视化结果...")
    predict_and_visualize(model, x_test, y_test)
    
    # 保存模型
    print("\n6. 保存模型...")
    import os
    model_dir = 'f:\\My-study\\Model'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'mnist_cnn_model.h5')
    model.save(model_path)
    print(f"模型已保存为 {model_path}")

if __name__ == '__main__':
    main()
