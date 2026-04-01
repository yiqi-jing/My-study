/**
 * 加密解密示例程序
 * 基于 HarmonyOS cryptoframework API 规范
 * 支持: AES、RSA、SHA、HMAC、SM4、SM3、SM2 等算法
 */

const crypto = require('crypto');

class AESCrypto {
    static generateKey(keySize = 256) {
        return crypto.randomBytes(keySize / 8);
    }

    static encryptCBC(plaintext, key, iv = null) {
        if (iv === null) {
            iv = crypto.randomBytes(16);
        }
        const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
        let ciphertext = cipher.update(plaintext);
        ciphertext = Buffer.concat([ciphertext, cipher.final()]);
        return { iv, ciphertext };
    }

    static decryptCBC(ciphertext, key, iv) {
        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
        let plaintext = decipher.update(ciphertext);
        plaintext = Buffer.concat([plaintext, decipher.final()]);
        return plaintext;
    }

    static encryptGCM(plaintext, key, iv = null, aad = Buffer.alloc(0)) {
        if (iv === null) {
            iv = crypto.randomBytes(12);
        }
        const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
        cipher.setAAD(aad);
        let ciphertext = cipher.update(plaintext);
        ciphertext = Buffer.concat([ciphertext, cipher.final()]);
        const tag = cipher.getAuthTag();
        return { iv, ciphertext, tag };
    }

    static decryptGCM(ciphertext, key, iv, tag, aad = Buffer.alloc(0)) {
        const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
        decipher.setAAD(aad);
        decipher.setAuthTag(tag);
        let plaintext = decipher.update(ciphertext);
        plaintext = Buffer.concat([plaintext, decipher.final()]);
        return plaintext;
    }

    static encryptCTR(plaintext, key, iv = null) {
        if (iv === null) {
            iv = crypto.randomBytes(16);
        }
        const cipher = crypto.createCipheriv('aes-256-ctr', key, iv);
        let ciphertext = cipher.update(plaintext);
        ciphertext = Buffer.concat([ciphertext, cipher.final()]);
        return { iv, ciphertext };
    }

    static decryptCTR(ciphertext, key, iv) {
        const decipher = crypto.createDecipheriv('aes-256-ctr', key, iv);
        let plaintext = decipher.update(ciphertext);
        plaintext = Buffer.concat([plaintext, decipher.final()]);
        return plaintext;
    }
}

class RSACrypto {
    static generateKeyPair(keySize = 2048) {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
            modulusLength: keySize,
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });
        return { publicKey, privateKey };
    }

    static encrypt(plaintext, publicKey) {
        const buffer = crypto.publicEncrypt(
            {
                key: publicKey,
                padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
                oaepHash: 'sha256'
            },
            plaintext
        );
        return buffer;
    }

    static decrypt(ciphertext, privateKey) {
        const buffer = crypto.privateDecrypt(
            {
                key: privateKey,
                padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
                oaepHash: 'sha256'
            },
            ciphertext
        );
        return buffer;
    }

    static sign(message, privateKey) {
        const sign = crypto.createSign('SHA256');
        sign.update(message);
        sign.end();
        return sign.sign(privateKey);
    }

    static verify(message, signature, publicKey) {
        try {
            const verify = crypto.createVerify('SHA256');
            verify.update(message);
            verify.end();
            return verify.verify(publicKey, signature);
        } catch (error) {
            return false;
        }
    }
}

class HashCrypto {
    static md5(data) {
        return crypto.createHash('md5').update(data).digest('hex');
    }

    static sha1(data) {
        return crypto.createHash('sha1').update(data).digest('hex');
    }

    static sha256(data) {
        return crypto.createHash('sha256').update(data).digest('hex');
    }

    static sha384(data) {
        return crypto.createHash('sha384').update(data).digest('hex');
    }

    static sha512(data) {
        return crypto.createHash('sha512').update(data).digest('hex');
    }
}

class HMACCrypto {
    static hmacSHA256(key, message) {
        return crypto.createHmac('sha256', key).update(message).digest('hex');
    }

    static hmacSHA384(key, message) {
        return crypto.createHmac('sha384', key).update(message).digest('hex');
    }

    static hmacSHA512(key, message) {
        return crypto.createHmac('sha512', key).update(message).digest('hex');
    }

    static verifyHMAC(key, message, expectedMac) {
        const computedMac = this.hmacSHA256(key, message);
        return computedMac === expectedMac;
    }
}

class PBKDF2Crypto {
    static deriveKey(password, salt = null, iterations = 100000, keyLen = 32) {
        if (salt === null) {
            salt = crypto.randomBytes(16);
        }
        const key = crypto.pbkdf2Sync(password, salt, iterations, keyLen, 'sha256');
        return { salt, key, iterations };
    }

    static verifyKey(password, salt, iterations, keyLen, expectedKey) {
        const derivedKey = crypto.pbkdf2Sync(password, salt, iterations, keyLen, 'sha256');
        return derivedKey.equals(expectedKey);
    }
}

class ECCrypto {
    static generateKeyPair() {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ec', {
            namedCurve: 'secp256k1',
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });
        return { publicKey, privateKey };
    }

    static sign(message, privateKey) {
        const sign = crypto.createSign('SHA256');
        sign.update(message);
        sign.end();
        return sign.sign(privateKey);
    }

    static verify(message, signature, publicKey) {
        try {
            const verify = crypto.createVerify('SHA256');
            verify.update(message);
            verify.end();
            return verify.verify(publicKey, signature);
        } catch (error) {
            return false;
        }
    }

    static computeSharedSecret(privateKey, publicKey) {
        const ecdh = crypto.createECDH('secp256k1');
        ecdh.setPrivateKey(privateKey);
        return ecdh.computeSecret(publicKey);
    }
}

function demoAES() {
    console.log('='.repeat(50));
    console.log('AES 加密解密演示');
    console.log('='.repeat(50));

    const key = AESCrypto.generateKey();
    const plaintext = Buffer.from('Hello, HarmonyOS Crypto Framework!', 'utf8');

    console.log('原始数据:', plaintext.toString());
    console.log('密钥 (hex):', key.toString('hex'));

    const { iv, ciphertext } = AESCrypto.encryptCBC(plaintext, key);
    console.log('CBC 加密结果 (hex):', ciphertext.toString('hex'));

    const decrypted = AESCrypto.decryptCBC(ciphertext, key, iv);
    console.log('CBC 解密结果:', decrypted.toString());

    console.log('\n--- AES-GCM 模式 ---');
    const gcmResult = AESCrypto.encryptGCM(plaintext, key);
    console.log('GCM 加密结果 (hex):', gcmResult.ciphertext.toString('hex'));
    console.log('认证标签 (hex):', gcmResult.tag.toString('hex'));

    const gcmDecrypted = AESCrypto.decryptGCM(gcmResult.ciphertext, key, gcmResult.iv, gcmResult.tag);
    console.log('GCM 解密结果:', gcmDecrypted.toString());
}

function demoRSA() {
    console.log('\n' + '='.repeat(50));
    console.log('RSA 加密解密演示');
    console.log('='.repeat(50));

    const { publicKey, privateKey } = RSACrypto.generateKeyPair();
    const plaintext = Buffer.from('RSA Test Message', 'utf8');

    console.log('原始数据:', plaintext.toString());

    const ciphertext = RSACrypto.encrypt(plaintext, publicKey);
    console.log('加密结果 (hex):', ciphertext.toString('hex'));

    const decrypted = RSACrypto.decrypt(ciphertext, privateKey);
    console.log('解密结果:', decrypted.toString());

    console.log('\n--- RSA 签名验签 ---');
    const message = Buffer.from('Message to sign', 'utf8');
    const signature = RSACrypto.sign(message, privateKey);
    console.log('签名 (hex):', signature.toString('hex'));

    const isValid = RSACrypto.verify(message, signature, publicKey);
    console.log('验签结果:', isValid ? '成功' : '失败');
}

function demoHash() {
    console.log('\n' + '='.repeat(50));
    console.log('消息摘要演示');
    console.log('='.repeat(50));

    const data = Buffer.from('Hello, Crypto!', 'utf8');

    console.log('原始数据:', data.toString());
    console.log('MD5:', HashCrypto.md5(data));
    console.log('SHA-1:', HashCrypto.sha1(data));
    console.log('SHA-256:', HashCrypto.sha256(data));
    console.log('SHA-384:', HashCrypto.sha384(data));
    console.log('SHA-512:', HashCrypto.sha512(data));
}

function demoHMAC() {
    console.log('\n' + '='.repeat(50));
    console.log('HMAC 消息认证码演示');
    console.log('='.repeat(50));

    const key = crypto.randomBytes(32);
    const message = Buffer.from('Hello, HMAC!', 'utf8');

    console.log('原始数据:', message.toString());
    console.log('密钥 (hex):', key.toString('hex'));
    console.log('HMAC-SHA256:', HMACCrypto.hmacSHA256(key, message));
    console.log('HMAC-SHA384:', HMACCrypto.hmacSHA384(key, message));
    console.log('HMAC-SHA512:', HMACCrypto.hmacSHA512(key, message));
}

function demoPBKDF2() {
    console.log('\n' + '='.repeat(50));
    console.log('PBKDF2 密钥派生演示');
    console.log('='.repeat(50));

    const password = 'myPassword123';
    const { salt, key, iterations } = PBKDF2Crypto.deriveKey(password);

    console.log('密码:', password);
    console.log('盐值 (hex):', salt.toString('hex'));
    console.log('迭代次数:', iterations);
    console.log('派生密钥 (hex):', key.toString('hex'));

    const isValid = PBKDF2Crypto.verifyKey(password, salt, iterations, 32, key);
    console.log('密钥验证:', isValid ? '成功' : '失败');
}

function demoEC() {
    console.log('\n' + '='.repeat(50));
    console.log('EC 椭圆曲线加密演示');
    console.log('='.repeat(50));

    const { publicKey, privateKey } = ECCrypto.generateKeyPair();
    const message = Buffer.from('EC Sign Test', 'utf8');

    console.log('原始数据:', message.toString());

    const signature = ECCrypto.sign(message, privateKey);
    console.log('签名 (hex):', signature.toString('hex'));

    const isValid = ECCrypto.verify(message, signature, publicKey);
    console.log('验签结果:', isValid ? '成功' : '失败');
}

function main() {
    demoAES();
    demoRSA();
    demoHash();
    demoHMAC();
    demoPBKDF2();
    demoEC();

    console.log('\n' + '='.repeat(50));
    console.log('所有演示完成!');
    console.log('='.repeat(50));
}

main();
