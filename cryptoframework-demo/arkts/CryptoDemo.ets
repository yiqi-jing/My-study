/**
 * 加密解密示例程序
 * 基于 HarmonyOS cryptoframework API 规范
 * 支持: AES、RSA、SHA、HMAC、SM4、SM3、SM2 等算法
 * 
 * 参考文档: https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-cryptoframework
 */

import cryptoFramework from '@ohos.security.cryptoFramework';

class AESCrypto {
  static async generateKey(keySize: number = 256): Promise<cryptoFramework.SymKey> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator(`AES${keySize}`);
    return await symKeyGenerator.generateSymKey();
  }

  static async convertKey(keyData: Uint8Array): Promise<cryptoFramework.SymKey> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator('AES256');
    return await symKeyGenerator.convertKey({ data: keyData });
  }

  static async encryptCBC(
    plaintext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv?: Uint8Array
  ): Promise<{ iv: Uint8Array; ciphertext: Uint8Array }> {
    const cipher = cryptoFramework.createCipher('AES256|CBC|PKCS7');
    
    if (!iv) {
      iv = new Uint8Array(16);
      for (let i = 0; i < 16; i++) {
        iv[i] = Math.floor(Math.random() * 256);
      }
    }

    const ivParamsSpec: cryptoFramework.IvParamsSpec = {
      algName: 'IvParamsSpec',
      iv: { data: iv }
    };

    await cipher.init(cryptoFramework.CryptoMode.ENCRYPT_MODE, key, ivParamsSpec);
    const result = await cipher.doFinal({ data: plaintext });
    
    return { iv, ciphertext: result.data };
  }

  static async decryptCBC(
    ciphertext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv: Uint8Array
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('AES256|CBC|PKCS7');
    
    const ivParamsSpec: cryptoFramework.IvParamsSpec = {
      algName: 'IvParamsSpec',
      iv: { data: iv }
    };

    await cipher.init(cryptoFramework.CryptoMode.DECRYPT_MODE, key, ivParamsSpec);
    const result = await cipher.doFinal({ data: ciphertext });
    
    return result.data;
  }

  static async encryptGCM(
    plaintext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv?: Uint8Array,
    aad?: Uint8Array
  ): Promise<{ iv: Uint8Array; ciphertext: Uint8Array; authTag: Uint8Array }> {
    const cipher = cryptoFramework.createCipher('AES256|GCM|NoPadding');
    
    if (!iv) {
      iv = new Uint8Array(12);
      for (let i = 0; i < 12; i++) {
        iv[i] = Math.floor(Math.random() * 256);
      }
    }

    const gcmParamsSpec: cryptoFramework.GcmParamsSpec = {
      algName: 'GcmParamsSpec',
      iv: { data: iv },
      aad: { data: aad || new Uint8Array(0) },
      authTag: { data: new Uint8Array(16) }
    };

    await cipher.init(cryptoFramework.CryptoMode.ENCRYPT_MODE, key, gcmParamsSpec);
    const result = await cipher.doFinal({ data: plaintext });
    
    const ciphertext = result.data.slice(0, result.data.length - 16);
    const authTag = result.data.slice(result.data.length - 16);
    
    return { iv, ciphertext, authTag };
  }

  static async decryptGCM(
    ciphertext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv: Uint8Array,
    authTag: Uint8Array,
    aad?: Uint8Array
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('AES256|GCM|NoPadding');
    
    const gcmParamsSpec: cryptoFramework.GcmParamsSpec = {
      algName: 'GcmParamsSpec',
      iv: { data: iv },
      aad: { data: aad || new Uint8Array(0) },
      authTag: { data: authTag }
    };

    await cipher.init(cryptoFramework.CryptoMode.DECRYPT_MODE, key, gcmParamsSpec);
    const result = await cipher.doFinal({ data: ciphertext });
    
    return result.data;
  }
}

class RSACrypto {
  static async generateKeyPair(keySize: number = 2048): Promise<cryptoFramework.KeyPair> {
    const asyKeyGenerator = cryptoFramework.createAsyKeyGenerator(`RSA${keySize}`);
    return await asyKeyGenerator.generateKeyPair();
  }

  static async encrypt(
    plaintext: Uint8Array,
    publicKey: cryptoFramework.PubKey
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('RSA2048|PKCS1_OAEP|SHA256|MGF1_SHA256');
    await cipher.init(cryptoFramework.CryptoMode.ENCRYPT_MODE, publicKey, null);
    const result = await cipher.doFinal({ data: plaintext });
    return result.data;
  }

  static async decrypt(
    ciphertext: Uint8Array,
    privateKey: cryptoFramework.PriKey
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('RSA2048|PKCS1_OAEP|SHA256|MGF1_SHA256');
    await cipher.init(cryptoFramework.CryptoMode.DECRYPT_MODE, privateKey, null);
    const result = await cipher.doFinal({ data: ciphertext });
    return result.data;
  }

  static async sign(
    message: Uint8Array,
    privateKey: cryptoFramework.PriKey
  ): Promise<Uint8Array> {
    const signer = cryptoFramework.createSign('RSA2048|PKCS1|SHA256');
    await signer.init(privateKey);
    await signer.update({ data: message });
    return (await signer.sign(null)).data;
  }

  static async verify(
    message: Uint8Array,
    signature: Uint8Array,
    publicKey: cryptoFramework.PubKey
  ): Promise<boolean> {
    const verifier = cryptoFramework.createVerify('RSA2048|PKCS1|SHA256');
    await verifier.init(publicKey);
    await verifier.update({ data: message });
    return await verifier.verify(null, { data: signature });
  }
}

class HashCrypto {
  static async md5(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('MD5');
    await md.update({ data });
    return (await md.digest()).data;
  }

  static async sha1(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('SHA1');
    await md.update({ data });
    return (await md.digest()).data;
  }

  static async sha256(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('SHA256');
    await md.update({ data });
    return (await md.digest()).data;
  }

  static async sha384(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('SHA384');
    await md.update({ data });
    return (await md.digest()).data;
  }

  static async sha512(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('SHA512');
    await md.update({ data });
    return (await md.digest()).data;
  }

  static async sm3(data: Uint8Array): Promise<Uint8Array> {
    const md = cryptoFramework.createMd('SM3');
    await md.update({ data });
    return (await md.digest()).data;
  }
}

class HMACCrypto {
  static async hmacSHA256(key: Uint8Array, message: Uint8Array): Promise<Uint8Array> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator('HMAC|SHA256');
    const symKey = await symKeyGenerator.convertKey({ data: key });
    
    const mac = cryptoFramework.createMac('HMAC|SHA256');
    await mac.init(symKey);
    await mac.update({ data: message });
    return (await mac.doFinal()).data;
  }

  static async hmacSHA384(key: Uint8Array, message: Uint8Array): Promise<Uint8Array> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator('HMAC|SHA384');
    const symKey = await symKeyGenerator.convertKey({ data: key });
    
    const mac = cryptoFramework.createMac('HMAC|SHA384');
    await mac.init(symKey);
    await mac.update({ data: message });
    return (await mac.doFinal()).data;
  }

  static async hmacSHA512(key: Uint8Array, message: Uint8Array): Promise<Uint8Array> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator('HMAC|SHA512');
    const symKey = await symKeyGenerator.convertKey({ data: key });
    
    const mac = cryptoFramework.createMac('HMAC|SHA512');
    await mac.init(symKey);
    await mac.update({ data: message });
    return (await mac.doFinal()).data;
  }
}

class SM4Crypto {
  static async generateKey(): Promise<cryptoFramework.SymKey> {
    const symKeyGenerator = cryptoFramework.createSymKeyGenerator('SM4_128');
    return await symKeyGenerator.generateSymKey();
  }

  static async encryptCBC(
    plaintext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv?: Uint8Array
  ): Promise<{ iv: Uint8Array; ciphertext: Uint8Array }> {
    const cipher = cryptoFramework.createCipher('SM4_128|CBC|PKCS7');
    
    if (!iv) {
      iv = new Uint8Array(16);
      for (let i = 0; i < 16; i++) {
        iv[i] = Math.floor(Math.random() * 256);
      }
    }

    const ivParamsSpec: cryptoFramework.IvParamsSpec = {
      algName: 'IvParamsSpec',
      iv: { data: iv }
    };

    await cipher.init(cryptoFramework.CryptoMode.ENCRYPT_MODE, key, ivParamsSpec);
    const result = await cipher.doFinal({ data: plaintext });
    
    return { iv, ciphertext: result.data };
  }

  static async decryptCBC(
    ciphertext: Uint8Array,
    key: cryptoFramework.SymKey,
    iv: Uint8Array
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('SM4_128|CBC|PKCS7');
    
    const ivParamsSpec: cryptoFramework.IvParamsSpec = {
      algName: 'IvParamsSpec',
      iv: { data: iv }
    };

    await cipher.init(cryptoFramework.CryptoMode.DECRYPT_MODE, key, ivParamsSpec);
    const result = await cipher.doFinal({ data: ciphertext });
    
    return result.data;
  }
}

class SM2Crypto {
  static async generateKeyPair(): Promise<cryptoFramework.KeyPair> {
    const asyKeyGenerator = cryptoFramework.createAsyKeyGenerator('SM2_256');
    return await asyKeyGenerator.generateKeyPair();
  }

  static async encrypt(
    plaintext: Uint8Array,
    publicKey: cryptoFramework.PubKey
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('SM2_256|SM2');
    await cipher.init(cryptoFramework.CryptoMode.ENCRYPT_MODE, publicKey, null);
    const result = await cipher.doFinal({ data: plaintext });
    return result.data;
  }

  static async decrypt(
    ciphertext: Uint8Array,
    privateKey: cryptoFramework.PriKey
  ): Promise<Uint8Array> {
    const cipher = cryptoFramework.createCipher('SM2_256|SM2');
    await cipher.init(cryptoFramework.CryptoMode.DECRYPT_MODE, privateKey, null);
    const result = await cipher.doFinal({ data: ciphertext });
    return result.data;
  }

  static async sign(
    message: Uint8Array,
    privateKey: cryptoFramework.PriKey
  ): Promise<Uint8Array> {
    const signer = cryptoFramework.createSign('SM2_256|SM3');
    await signer.init(privateKey);
    await signer.update({ data: message });
    return (await signer.sign(null)).data;
  }

  static async verify(
    message: Uint8Array,
    signature: Uint8Array,
    publicKey: cryptoFramework.PubKey
  ): Promise<boolean> {
    const verifier = cryptoFramework.createVerify('SM2_256|SM3');
    await verifier.init(publicKey);
    await verifier.update({ data: message });
    return await verifier.verify(null, { data: signature });
  }
}

class PBKDF2Crypto {
  static async deriveKey(
    password: string,
    salt?: Uint8Array,
    iterations: number = 10000,
    keySize: number = 32
  ): Promise<{ salt: Uint8Array; key: Uint8Array }> {
    if (!salt) {
      salt = new Uint8Array(16);
      for (let i = 0; i < 16; i++) {
        salt[i] = Math.floor(Math.random() * 256);
      }
    }

    const kdfSpec: cryptoFramework.PBKDF2Spec = {
      algName: 'PBKDF2',
      password: password,
      salt: salt,
      iterations: iterations,
      keySize: keySize
    };

    const kdf = cryptoFramework.createKdf('PBKDF2|SHA256');
    const result = await kdf.generateSecret(kdfSpec);
    
    return { salt, key: result.data };
  }
}

function uint8ArrayToHex(data: Uint8Array): string {
  return Array.from(data)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

function stringToUint8Array(str: string): Uint8Array {
  const encoder = new TextEncoder();
  return encoder.encode(str);
}

function uint8ArrayToString(data: Uint8Array): string {
  const decoder = new TextDecoder();
  return decoder.decode(data);
}

async function demoAES(): Promise<void> {
  console.log('='.repeat(50));
  console.log('AES 加密解密演示');
  console.log('='.repeat(50));

  const key = await AESCrypto.generateKey();
  const plaintext = stringToUint8Array('Hello, HarmonyOS Crypto Framework!');

  console.log('原始数据:', uint8ArrayToString(plaintext));
  console.log('密钥 (hex):', uint8ArrayToHex(key.getEncoded().data));

  const { iv, ciphertext } = await AESCrypto.encryptCBC(plaintext, key);
  console.log('CBC 加密结果 (hex):', uint8ArrayToHex(ciphertext));

  const decrypted = await AESCrypto.decryptCBC(ciphertext, key, iv);
  console.log('CBC 解密结果:', uint8ArrayToString(decrypted));

  console.log('\n--- AES-GCM 模式 ---');
  const gcmResult = await AESCrypto.encryptGCM(plaintext, key);
  console.log('GCM 加密结果 (hex):', uint8ArrayToHex(gcmResult.ciphertext));
  console.log('认证标签 (hex):', uint8ArrayToHex(gcmResult.authTag));

  const gcmDecrypted = await AESCrypto.decryptGCM(
    gcmResult.ciphertext,
    key,
    gcmResult.iv,
    gcmResult.authTag
  );
  console.log('GCM 解密结果:', uint8ArrayToString(gcmDecrypted));
}

async function demoRSA(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('RSA 加密解密演示');
  console.log('='.repeat(50));

  const keyPair = await RSACrypto.generateKeyPair();
  const plaintext = stringToUint8Array('RSA Test Message');

  console.log('原始数据:', uint8ArrayToString(plaintext));

  const ciphertext = await RSACrypto.encrypt(plaintext, keyPair.pubKey);
  console.log('加密结果 (hex):', uint8ArrayToHex(ciphertext));

  const decrypted = await RSACrypto.decrypt(ciphertext, keyPair.priKey);
  console.log('解密结果:', uint8ArrayToString(decrypted));

  console.log('\n--- RSA 签名验签 ---');
  const message = stringToUint8Array('Message to sign');
  const signature = await RSACrypto.sign(message, keyPair.priKey);
  console.log('签名 (hex):', uint8ArrayToHex(signature));

  const isValid = await RSACrypto.verify(message, signature, keyPair.pubKey);
  console.log('验签结果:', isValid ? '成功' : '失败');
}

async function demoHash(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('消息摘要演示');
  console.log('='.repeat(50));

  const data = stringToUint8Array('Hello, Crypto!');

  console.log('原始数据:', uint8ArrayToString(data));
  console.log('MD5:', uint8ArrayToHex(await HashCrypto.md5(data)));
  console.log('SHA-1:', uint8ArrayToHex(await HashCrypto.sha1(data)));
  console.log('SHA-256:', uint8ArrayToHex(await HashCrypto.sha256(data)));
  console.log('SHA-384:', uint8ArrayToHex(await HashCrypto.sha384(data)));
  console.log('SHA-512:', uint8ArrayToHex(await HashCrypto.sha512(data)));
  console.log('SM3:', uint8ArrayToHex(await HashCrypto.sm3(data)));
}

async function demoHMAC(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('HMAC 消息认证码演示');
  console.log('='.repeat(50));

  const key = new Uint8Array(32);
  for (let i = 0; i < 32; i++) {
    key[i] = Math.floor(Math.random() * 256);
  }
  const message = stringToUint8Array('Hello, HMAC!');

  console.log('原始数据:', uint8ArrayToString(message));
  console.log('密钥 (hex):', uint8ArrayToHex(key));
  console.log('HMAC-SHA256:', uint8ArrayToHex(await HMACCrypto.hmacSHA256(key, message)));
  console.log('HMAC-SHA384:', uint8ArrayToHex(await HMACCrypto.hmacSHA384(key, message)));
  console.log('HMAC-SHA512:', uint8ArrayToHex(await HMACCrypto.hmacSHA512(key, message)));
}

async function demoSM4(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('SM4 国密算法演示');
  console.log('='.repeat(50));

  const key = await SM4Crypto.generateKey();
  const plaintext = stringToUint8Array('Hello, SM4!');

  console.log('原始数据:', uint8ArrayToString(plaintext));
  console.log('密钥 (hex):', uint8ArrayToHex(key.getEncoded().data));

  const { iv, ciphertext } = await SM4Crypto.encryptCBC(plaintext, key);
  console.log('SM4-CBC 加密结果 (hex):', uint8ArrayToHex(ciphertext));

  const decrypted = await SM4Crypto.decryptCBC(ciphertext, key, iv);
  console.log('SM4-CBC 解密结果:', uint8ArrayToString(decrypted));
}

async function demoSM2(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('SM2 国密算法演示');
  console.log('='.repeat(50));

  const keyPair = await SM2Crypto.generateKeyPair();
  const plaintext = stringToUint8Array('Hello, SM2!');

  console.log('原始数据:', uint8ArrayToString(plaintext));

  const ciphertext = await SM2Crypto.encrypt(plaintext, keyPair.pubKey);
  console.log('SM2 加密结果 (hex):', uint8ArrayToHex(ciphertext));

  const decrypted = await SM2Crypto.decrypt(ciphertext, keyPair.priKey);
  console.log('SM2 解密结果:', uint8ArrayToString(decrypted));

  console.log('\n--- SM2 签名验签 ---');
  const message = stringToUint8Array('Message to sign');
  const signature = await SM2Crypto.sign(message, keyPair.priKey);
  console.log('签名 (hex):', uint8ArrayToHex(signature));

  const isValid = await SM2Crypto.verify(message, signature, keyPair.pubKey);
  console.log('验签结果:', isValid ? '成功' : '失败');
}

async function demoPBKDF2(): Promise<void> {
  console.log('\n' + '='.repeat(50));
  console.log('PBKDF2 密钥派生演示');
  console.log('='.repeat(50));

  const password = 'myPassword123';
  const { salt, key } = await PBKDF2Crypto.deriveKey(password);

  console.log('密码:', password);
  console.log('盐值 (hex):', uint8ArrayToHex(salt));
  console.log('派生密钥 (hex):', uint8ArrayToHex(key));
}

@Entry
@Component
struct CryptoDemoPage {
  @State message: string = '加密解密演示';

  async runDemo(): Promise<void> {
    try {
      await demoAES();
      await demoRSA();
      await demoHash();
      await demoHMAC();
      await demoSM4();
      await demoSM2();
      await demoPBKDF2();

      console.log('\n' + '='.repeat(50));
      console.log('所有演示完成!');
      console.log('='.repeat(50));
    } catch (error) {
      console.error('演示出错:', JSON.stringify(error));
    }
  }

  build() {
    Column() {
      Text(this.message)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 20 })

      Button('运行加密演示')
        .width('80%')
        .height(50)
        .onClick(() => {
          this.runDemo();
        })

      Button('AES 加解密')
        .width('80%')
        .height(50)
        .margin({ top: 10 })
        .onClick(async () => {
          await demoAES();
        })

      Button('RSA 加解密')
        .width('80%')
        .height(50)
        .margin({ top: 10 })
        .onClick(async () => {
          await demoRSA();
        })

      Button('消息摘要')
        .width('80%')
        .height(50)
        .margin({ top: 10 })
        .onClick(async () => {
          await demoHash();
        })

      Button('SM4 国密')
        .width('80%')
        .height(50)
        .margin({ top: 10 })
        .onClick(async () => {
          await demoSM4();
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .padding(20)
  }
}
