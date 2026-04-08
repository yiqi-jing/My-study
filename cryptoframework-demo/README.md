# 加密解密示例程序

基于 HarmonyOS cryptoframework API 规范，提供多种常用编程语言的加密解密示例代码。

参考文档: https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-cryptoframework

## 目录结构

```
cryptoframework-demo/
├── python/
│   ├── crypto_demo.py      # Python 加密解密示例
│   └── sm9.py              # SM9 算法实现
├── javascript/
│   ├── package.json
│   └── crypto_demo.js      # Node.js 加密解密示例
├── java/
│   └── CryptoDemo.java     # Java 加密解密示例
└── arkts/
    └── CryptoDemo.ets      # HarmonyOS ArkTS 加密解密示例
```

## 支持的算法

### 对称加密
- **AES**: CBC、GCM、CTR 模式
- **SM4**: 国密对称加密算法 (CBC 模式)
- **DES/3DES**: 传统对称加密

### 非对称加密
- **RSA**: 加密解密、签名验签
- **SM2**: 国密非对称加密算法
- **SM9**: 国密标识密码算法
- **EC**: 椭圆曲线加密

### 消息摘要
- **MD5**: 128位摘要
- **SHA-1**: 160位摘要
- **SHA-256/384/512**: SHA-2 系列摘要
- **SM3**: 国密摘要算法

### 消息认证码
- **HMAC-SHA256/384/512**: 基于哈希的消息认证码

### 密钥派生
- **PBKDF2**: 基于密码的密钥派生函数

## 使用说明

### Python 示例

```bash
# 安装依赖
pip install cryptography gmssl-python

# 运行示例
cd python
python crypto_demo.py
```

### JavaScript/Node.js 示例

```bash
# 安装依赖
cd javascript
npm install

# 运行示例
node crypto_demo.js
```

### Java 示例

```bash
# 编译
cd java
javac CryptoDemo.java

# 运行
java CryptoDemo
```

### ArkTS (HarmonyOS) 示例

将 `CryptoDemo.ets` 文件复制到 HarmonyOS 项目的 `entry/src/main/ets/pages/` 目录下，然后在 `module.json5` 中注册页面即可使用。

## 算法对比

| 算法类型 | 国际标准 | 国密标准 |
|---------|---------|--------|
| 对称加密 | AES | SM4 |
| 非对称加密 | RSA、EC | SM2、SM9 |
| 摘要算法 | SHA-256 | SM3 |

## 注意事项

1. **密钥管理**: 示例中的密钥是随机生成的，实际应用中需要安全地存储和管理密钥
2. **IV/Nonce**: 每次加密应使用不同的 IV 或 Nonce 值
3. **安全建议**: 
   - 推荐使用 AES-GCM 模式（提供认证加密）
   - RSA 密钥长度建议至少 2048 位
   - PBKDF2 迭代次数建议至少 10000 次
4. **国密算法**: SM2/SM3/SM4 是中国国家密码管理局发布的商用密码算法

## API 参考

详细 API 文档请参考:
- [HarmonyOS CryptoFramework API](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-cryptoframework)
