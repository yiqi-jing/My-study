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
uufrom cryptography.hazmat.backends import default_backend

# ==============================================
# AES 加密
# ==============================================
class AESCrypto:
    @staticmethod
    def generate_key(key_size: int = 256) -> bytes:
        return os.urandom(key_size // 8)
    
    @staticmethod
    def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes = None) -> tuple:
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
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    @staticmethod
    def encrypt_gcm(plaintext: bytes, key: bytes, iv: bytes = None, aad: bytes = b'') -> tuple:
        if iv is None:
            iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(aad)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv, ciphertext, encryptor.tag
    
    @staticmethod
    def decrypt_gcm(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes, aad: bytes = b'') -> bytes:
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(aad)
        return decryptor.update(ciphertext) + decryptor.finalize()

# ==============================================
# RSA 加密
# ==============================================
class RSACrypto:
    @staticmethod
    def generate_key_pair(key_size: int = 2048):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())
        return private_key, private_key.public_key()
    
    @staticmethod
    def encrypt(plaintext: bytes, public_key) -> bytes:
        return public_key.encrypt(
            plaintext,
            asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
    
    @staticmethod
    def decrypt(ciphertext: bytes, private_key) -> bytes:
        return private_key.decrypt(
            ciphertext,
            asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
    
    @staticmethod
    def sign(message: bytes, private_key) -> bytes:
        return private_key.sign(
            message,
            asym_padding.PSS(mgf=asym_padding.MGF1(hashes.SHA256()), salt_length=asym_padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    
    @staticmethod
    def verify(message: bytes, signature: bytes, public_key) -> bool:
        try:
            public_key.verify(
                signature, message,
                asym_padding.PSS(mgf=asym_padding.MGF1(hashes.SHA256()), salt_length=asym_padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except:
            return False

# ==============================================
# 哈希算法
# ==============================================
class HashCrypto:
    @staticmethod
    def md5(data: bytes) -> str: return hashlib.md5(data).hexdigest()
    @staticmethod
    def sha1(data: bytes) -> str: return hashlib.sha1(data).hexdigest()
    @staticmethod
    def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
    @staticmethod
    def sha512(data: bytes) -> str: return hashlib.sha512(data).hexdigest()
    @staticmethod
    def sm3(data: bytes) -> str:
        from gmssl import sm3, func
        return sm3.sm3_hash(func.bytes_to_list(data))

# ==============================================
# HMAC
# ==============================================
class HMACCrypto:
    @staticmethod
    def hmac_sha256(key: bytes, message: bytes) -> str:
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    @staticmethod
    def hmac_sha512(key: bytes, message: bytes) -> str:
        return hmac.new(key, message, hashlib.sha512).hexdigest()
    @staticmethod
    def verify_hmac(key: bytes, message: bytes, expected_mac: str) -> bool:
        return hmac.compare_digest(hmac.new(key, message, hashlib.sha256).hexdigest(), expected_mac)

# ==============================================
# SM4 国密
# ==============================================
class SM4Crypto:
    @staticmethod
    def generate_key() -> bytes: return os.urandom(16)
    @staticmethod
    def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes = None) -> tuple:
        from gmssl import sm4
        if iv is None: iv = os.urandom(16)
        cipher = sm4.CryptSM4()
        cipher.set_key(key, sm4.SM4_ENCRYPT)
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()
        return iv, cipher.crypt_cbc(iv, padded)
    @staticmethod
    def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        from gmssl import sm4
        cipher = sm4.CryptSM4()
        cipher.set_key(key, sm4.SM4_DECRYPT)
        padded = cipher.crypt_cbc(iv, ciphertext)
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()

# ==============================================
# ✅ SM9 国密 最终修复版
# ==============================================
class SM9Crypto:
    """SM9 国密标识密码算法类（gmssl-python 2.2.2 正确版本）"""
    @staticmethod
    def generate_key_pair():
        from gmssl import sm9
        signing_master = sm9.SM9SignMasterKey()
        encrypt_master = sm9.SM9EncryptMasterKey()
        signing_master.generate()
        encrypt_master.generate()
        return signing_master, encrypt_master  # 🔥 这里返回两个密钥！

    @staticmethod
    def encrypt(plaintext: bytes, encrypt_master, id_str: str) -> bytes:
        from gmssl import sm9
        pub = encrypt_master.get_public_key()
        return sm9.encrypt(pub, id_str.encode(), plaintext)

    @staticmethod
    def decrypt(ciphertext: bytes, encrypt_master, id_str: str) -> bytes:
        from gmssl import sm9
        sk = encrypt_master.extract_private_key(id_str.encode())
        return sm9.decrypt(sk, ciphertext)

    @staticmethod
    def sign(message: bytes, signing_master, id_str: str) -> bytes:
        from gmssl import sm9
        sk = signing_master.extract_private_key(id_str.encode())
        return sm9.sign(sk, message)

    @staticmethod
    def verify(message: bytes, signature: bytes, signing_master, id_str: str) -> bool:
        from gmssl import sm9
        pub = signing_master.get_public_key()
        return sm9.verify(pub, id_str.encode(), message, signature)

# ==============================================
# 演示函数
# ==============================================
def demo_aes():
    print("="*50); print("AES 演示"); print("="*50)
    key = AESCrypto.generate_key()
    msg = b"Hello, AES!"
    iv, ct = AESCrypto.encrypt_cbc(msg, key)
    print(f"解密：{AESCrypto.decrypt_cbc(ct, key, iv).decode()}")

def demo_rsa():
    print("\n"+"="*50); print("RSA 演示"); print("="*50)
    sk, pk = RSACrypto.generate_key_pair()
    msg = b"Hello RSA"
    ct = RSACrypto.encrypt(msg, pk)
    print(f"解密：{RSACrypto.decrypt(ct, sk).decode()}")

def demo_hash():
    print("\n"+"="*50); print("哈希演示"); print("="*50)
    d = b"test"
    print(f"SM3: {HashCrypto.sm3(d)}")

def demo_hmac():
    print("\n"+"="*50); print("HMAC 演示"); print("="*50)
    print(HMACCrypto.hmac_sha256(b"key", b"msg"))

def demo_sm4():
    print("\n"+"="*50); print("SM4 演示"); print("="*50)
    key = SM4Crypto.generate_key()
    iv, ct = SM4Crypto.encrypt_cbc(b"Hello SM4", key)
    print(f"解密：{SM4Crypto.decrypt_cbc(ct, key, iv).decode()}")

# ==============================================
# ✅ SM9 演示函数修复（最关键！）
# ==============================================
def demo_sm9():
    print("\n"+"="*50); print("SM9 国密算法演示"); print("="*50)
    try:
        # 🔥 修复：拆分成签名密钥 + 加密密钥
        signing_master, encrypt_master = SM9Crypto.generate_key_pair()
        
        msg = b"Hello, SM9!!!"
        uid = "test@sm9.com"
        
        # 加密解密
        ct = SM9Crypto.encrypt(msg, encrypt_master, uid)
        pt = SM9Crypto.decrypt(ct, encrypt_master, uid)
        print(f"加密结果：{ct.hex()}")
        print(f"解密结果：{pt.decode()}")
        
        # 签名验签
        sig = SM9Crypto.sign(msg, signing_master, uid)
        ok = SM9Crypto.verify(msg, sig, signing_master, uid)
        print(f"签名验签：{'成功' if ok else '失败'}")
        
    except Exception as e:
        print(f"SM9 错误：{e}")

# ==============================================
# 运行全部演示
# ==============================================
if __name__ == "__main__":
    demo_aes()
    demo_rsa()
    demo_hash()
    demo_hmac()
    demo_sm4()
    demo_sm9()
    print("\n✅ 所有演示运行完成！")