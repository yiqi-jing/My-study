"""
加密解密示例程序
基于 HarmonyOS cryptoframework API 规范
支持: AES、RSA、SHA、HMAC、SM4、SM3、SM2 等算法
"""

import os
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import utils


class AESCrypto:
    """AES 对称加密解密类"""
    
    @staticmethod
    def generate_key(key_size: int = 256) -> bytes:
        """生成 AES 密钥"""
        return os.urandom(key_size // 8)
    
    @staticmethod
    def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes = None) -> tuple:
        """AES-CBC 模式加密"""
        if iv is None:
            iv = os.urandom(16)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv, ciphertext
    
    @staticmethod
    def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """AES-CBC 模式解密"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        
        return plaintext
    
    @staticmethod
    def encrypt_gcm(plaintext: bytes, key: bytes, iv: bytes = None, aad: bytes = b'') -> tuple:
        """AES-GCM 模式加密"""
        if iv is None:
            iv = os.urandom(12)
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(aad)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return iv, ciphertext, encryptor.tag
    
    @staticmethod
    def decrypt_gcm(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes, aad: bytes = b'') -> bytes:
        """AES-GCM 模式解密"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(aad)
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext


class RSACrypto:
    """RSA 非对称加密解密类"""
    
    @staticmethod
    def generate_key_pair(key_size: int = 2048):
        """生成 RSA 密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def encrypt(plaintext: bytes, public_key) -> bytes:
        """RSA 公钥加密"""
        ciphertext = public_key.encrypt(
            plaintext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    @staticmethod
    def decrypt(ciphertext: bytes, private_key) -> bytes:
        """RSA 私钥解密"""
        plaintext = private_key.decrypt(
            ciphertext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    @staticmethod
    def sign(message: bytes, private_key) -> bytes:
        """RSA 私钥签名"""
        signature = private_key.sign(
            message,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    @staticmethod
    def verify(message: bytes, signature: bytes, public_key) -> bool:
        """RSA 公钥验签"""
        try:
            public_key.verify(
                signature,
                message,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


class HashCrypto:
    """消息摘要类"""
    
    @staticmethod
    def md5(data: bytes) -> str:
        """MD5 摘要"""
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def sha1(data: bytes) -> str:
        """SHA-1 摘要"""
        return hashlib.sha1(data).hexdigest()
    
    @staticmethod
    def sha256(data: bytes) -> str:
        """SHA-256 摘要"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha512(data: bytes) -> str:
        """SHA-512 摘要"""
        return hashlib.sha512(data).hexdigest()
    
    @staticmethod
    def sm3(data: bytes) -> str:
        """SM3 摘要 (需要安装 gmssl-python)"""
        try:
            from gmssl import sm3, func
            return sm3.sm3_hash(func.bytes_to_list(data))
        except ImportError:
            return "需要安装 gmssl-python: pip install gmssl-python"


class HMACCrypto:
    """HMAC 消息认证码类"""
    
    @staticmethod
    def hmac_sha256(key: bytes, message: bytes) -> str:
        """HMAC-SHA256"""
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    
    @staticmethod
    def hmac_sha512(key: bytes, message: bytes) -> str:
        """HMAC-SHA512"""
        return hmac.new(key, message, hashlib.sha512).hexdigest()
    
    @staticmethod
    def verify_hmac(key: bytes, message: bytes, expected_mac: str) -> bool:
        """验证 HMAC"""
        computed_mac = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_mac, expected_mac)


class SM4Crypto:
    """SM4 国密对称加密类 (需要安装 gmssl-python)"""
    
    @staticmethod
    def generate_key() -> bytes:
        """生成 SM4 密钥 (128位)"""
        return os.urandom(16)
    
    @staticmethod
    def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes = None) -> tuple:
        """SM4-CBC 模式加密"""
        try:
            from gmssl import sm4
            
            if iv is None:
                iv = os.urandom(16)
            
            cipher = sm4.CryptSM4()
            cipher.set_key(key, sm4.SM4_ENCRYPT)
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            
            ciphertext = cipher.crypt_cbc(iv, padded_data)
            return iv, ciphertext
        except ImportError:
            raise ImportError("需要安装 gmssl-python: pip install gmssl-python")
    
    @staticmethod
    def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """SM4-CBC 模式解密"""
        try:
            from gmssl import sm4
            
            cipher = sm4.CryptSM4()
            cipher.set_key(key, sm4.SM4_DECRYPT)
            
            padded_data = cipher.crypt_cbc(iv, ciphertext)
            
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext
        except ImportError:
            raise ImportError("需要安装 gmssl-python: pip install gmssl-python")


def demo_aes():
    """AES 加密解密演示"""
    print("=" * 50)
    print("AES 加密解密演示")
    print("=" * 50)
    
    key = AESCrypto.generate_key()
    plaintext = b"Hello, HarmonyOS Crypto Framework!"
    
    print(f"原始数据: {plaintext.decode()}")
    print(f"密钥 (hex): {key.hex()}")
    
    iv, ciphertext = AESCrypto.encrypt_cbc(plaintext, key)
    print(f"CBC 加密结果 (hex): {ciphertext.hex()}")
    
    decrypted = AESCrypto.decrypt_cbc(ciphertext, key, iv)
    print(f"CBC 解密结果: {decrypted.decode()}")
    
    print("\n--- AES-GCM 模式 ---")
    iv, ciphertext, tag = AESCrypto.encrypt_gcm(plaintext, key)
    print(f"GCM 加密结果 (hex): {ciphertext.hex()}")
    print(f"认证标签 (hex): {tag.hex()}")
    
    decrypted = AESCrypto.decrypt_gcm(ciphertext, key, iv, tag)
    print(f"GCM 解密结果: {decrypted.decode()}")


def demo_rsa():
    """RSA 加密解密演示"""
    print("\n" + "=" * 50)
    print("RSA 加密解密演示")
    print("=" * 50)
    
    private_key, public_key = RSACrypto.generate_key_pair()
    plaintext = b"RSA Test Message"
    
    print(f"原始数据: {plaintext.decode()}")
    
    ciphertext = RSACrypto.encrypt(plaintext, public_key)
    print(f"加密结果 (hex): {ciphertext.hex()}")
    
    decrypted = RSACrypto.decrypt(ciphertext, private_key)
    print(f"解密结果: {decrypted.decode()}")
    
    print("\n--- RSA 签名验签 ---")
    message = b"Message to sign"
    signature = RSACrypto.sign(message, private_key)
    print(f"签名 (hex): {signature.hex()}")
    
    is_valid = RSACrypto.verify(message, signature, public_key)
    print(f"验签结果: {'成功' if is_valid else '失败'}")


def demo_hash():
    """消息摘要演示"""
    print("\n" + "=" * 50)
    print("消息摘要演示")
    print("=" * 50)
    
    data = b"Hello, Crypto!"
    
    print(f"原始数据: {data.decode()}")
    print(f"MD5: {HashCrypto.md5(data)}")
    print(f"SHA-1: {HashCrypto.sha1(data)}")
    print(f"SHA-256: {HashCrypto.sha256(data)}")
    print(f"SHA-512: {HashCrypto.sha512(data)}")
    print(f"SM3: {HashCrypto.sm3(data)}")


def demo_hmac():
    """HMAC 演示"""
    print("\n" + "=" * 50)
    print("HMAC 消息认证码演示")
    print("=" * 50)
    
    key = os.urandom(32)
    message = b"Hello, HMAC!"
    
    print(f"原始数据: {message.decode()}")
    print(f"密钥 (hex): {key.hex()}")
    print(f"HMAC-SHA256: {HMACCrypto.hmac_sha256(key, message)}")
    print(f"HMAC-SHA512: {HMACCrypto.hmac_sha512(key, message)}")


def demo_sm4():
    """SM4 加密解密演示"""
    print("\n" + "=" * 50)
    print("SM4 国密算法演示")
    print("=" * 50)
    
    try:
        key = SM4Crypto.generate_key()
        plaintext = b"Hello, SM4!"
        
        print(f"原始数据: {plaintext.decode()}")
        print(f"密钥 (hex): {key.hex()}")
        
        iv, ciphertext = SM4Crypto.encrypt_cbc(plaintext, key)
        print(f"SM4-CBC 加密结果 (hex): {ciphertext.hex()}")
        
        decrypted = SM4Crypto.decrypt_cbc(ciphertext, key, iv)
        print(f"SM4-CBC 解密结果: {decrypted.decode()}")
    except ImportError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    demo_aes()
    demo_rsa()
    demo_hash()
    demo_hmac()
    demo_sm4()
    
    print("\n" + "=" * 50)
    print("所有演示完成!")
    print("=" * 50)
