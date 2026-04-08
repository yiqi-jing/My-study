import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.security.spec.*;
import java.util.Base64;

/**
 * 加密解密示例程序
 * 基于 HarmonyOS cryptoframework API 规范
 * 支持: AES、RSA、SHA、HMAC、DES 等算法
 */
public class CryptoDemo {

    public static class AESCrypto {
        
        public static byte[] generateKey(int keySize) throws NoSuchAlgorithmException {
            KeyGenerator keyGen = KeyGenerator.getInstance("AES");
            keyGen.init(keySize);
            return keyGen.generateKey().getEncoded();
        }

        public static class EncryptResult {
            public byte[] iv;
            public byte[] ciphertext;

            public EncryptResult(byte[] iv, byte[] ciphertext) {
                this.iv = iv;
                this.ciphertext = ciphertext;
            }
        }

        public static EncryptResult encryptCBC(byte[] plaintext, byte[] key) throws Exception {
            byte[] iv = new byte[16];
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);
            
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec);
            
            byte[] ciphertext = cipher.doFinal(plaintext);
            return new EncryptResult(iv, ciphertext);
        }

        public static byte[] decryptCBC(byte[] ciphertext, byte[] key, byte[] iv) throws Exception {
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
            IvParameterSpec ivSpec = new IvParameterSpec(iv);
            
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec);
            
            return cipher.doFinal(ciphertext);
        }

        public static class GCMResult {
            public byte[] iv;
            public byte[] ciphertext;
            public byte[] tag;

            public GCMResult(byte[] iv, byte[] ciphertext, byte[] tag) {
                this.iv = iv;
                this.ciphertext = ciphertext;
                this.tag = tag;
            }
        }

        public static GCMResult encryptGCM(byte[] plaintext, byte[] key, byte[] aad) throws Exception {
            byte[] iv = new byte[12];
            SecureRandom random = new SecureRandom();
            random.nextBytes(iv);
            
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, gcmSpec);
            if (aad != null && aad.length > 0) {
                cipher.updateAAD(aad);
            }
            
            byte[] ciphertext = cipher.doFinal(plaintext);
            byte[] tag = new byte[16];
            System.arraycopy(ciphertext, ciphertext.length - 16, tag, 0, 16);
            byte[] actualCiphertext = new byte[ciphertext.length - 16];
            System.arraycopy(ciphertext, 0, actualCiphertext, 0, ciphertext.length - 16);
            
            return new GCMResult(iv, actualCiphertext, tag);
        }

        public static byte[] decryptGCM(byte[] ciphertext, byte[] key, byte[] iv, byte[] tag, byte[] aad) throws Exception {
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE, secretKey, gcmSpec);
            if (aad != null && aad.length > 0) {
                cipher.updateAAD(aad);
            }
            
            byte[] combined = new byte[ciphertext.length + tag.length];
            System.arraycopy(ciphertext, 0, combined, 0, ciphertext.length);
            System.arraycopy(tag, 0, combined, ciphertext.length, tag.length);
            
            return cipher.doFinal(combined);
        }
    }

    public static class RSACrypto {
        
        public static KeyPair generateKeyPair(int keySize) throws NoSuchAlgorithmException {
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
            keyGen.initialize(keySize);
            return keyGen.generateKeyPair();
        }

        public static byte[] encrypt(byte[] plaintext, PublicKey publicKey) throws Exception {
            Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
            cipher.init(Cipher.ENCRYPT_MODE, publicKey);
            return cipher.doFinal(plaintext);
        }

        public static byte[] decrypt(byte[] ciphertext, PrivateKey privateKey) throws Exception {
            Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
            cipher.init(Cipher.DECRYPT_MODE, privateKey);
            return cipher.doFinal(ciphertext);
        }

        // ✅ 修复：JDK17 兼容 RSA-PSS 签名
        public static byte[] sign(byte[] message, PrivateKey privateKey) throws Exception {
            Signature signature = Signature.getInstance("RSASSA-PSS");
            signature.setParameter(PSSParameterSpec.DEFAULT);
            signature.initSign(privateKey);
            signature.update(message);
            return signature.sign();
        }

        // ✅ 修复：JDK17 兼容 RSA-PSS 验签
        public static boolean verify(byte[] message, byte[] signatureBytes, PublicKey publicKey) throws Exception {
            Signature signature = Signature.getInstance("RSASSA-PSS");
            signature.setParameter(PSSParameterSpec.DEFAULT);
            signature.initVerify(publicKey);
            signature.update(message);
            return signature.verify(signatureBytes);
        }
    }

    public static class HashCrypto {
        
        public static String md5(byte[] data) throws NoSuchAlgorithmException {
            MessageDigest md = MessageDigest.getInstance("MD5");
            return bytesToHex(md.digest(data));
        }

        public static String sha1(byte[] data) throws NoSuchAlgorithmException {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            return bytesToHex(md.digest(data));
        }

        public static String sha256(byte[] data) throws NoSuchAlgorithmException {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            return bytesToHex(md.digest(data));
        }

        public static String sha384(byte[] data) throws NoSuchAlgorithmException {
            MessageDigest md = MessageDigest.getInstance("SHA-384");
            return bytesToHex(md.digest(data));
        }

        public static String sha512(byte[] data) throws NoSuchAlgorithmException {
            MessageDigest md = MessageDigest.getInstance("SHA-512");
            return bytesToHex(md.digest(data));
        }
    }

    public static class HMACCrypto {
        
        public static String hmacSHA256(byte[] key, byte[] message) throws Exception {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(key, "HmacSHA256");
            mac.init(secretKey);
            return bytesToHex(mac.doFinal(message));
        }

        public static String hmacSHA384(byte[] key, byte[] message) throws Exception {
            Mac mac = Mac.getInstance("HmacSHA384");
            SecretKeySpec secretKey = new SecretKeySpec(key, "HmacSHA384");
            mac.init(secretKey);
            return bytesToHex(mac.doFinal(message));
        }

        public static String hmacSHA512(byte[] key, byte[] message) throws Exception {
            Mac mac = Mac.getInstance("HmacSHA512");
            SecretKeySpec secretKey = new SecretKeySpec(key, "HmacSHA512");
            mac.init(secretKey);
            return bytesToHex(mac.doFinal(message));
        }
    }

    public static class PBKDF2Crypto {
        
        public static class PBKDF2Result {
            public byte[] salt;
            public byte[] key;
            public int iterations;

            public PBKDF2Result(byte[] salt, byte[] key, int iterations) {
                this.salt = salt;
                this.key = key;
                this.iterations = iterations;
            }
        }

        public static PBKDF2Result deriveKey(String password, int keyLen, int iterations) throws Exception {
            byte[] salt = new byte[16];
            SecureRandom random = new SecureRandom();
            random.nextBytes(salt);
            
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLen * 8);
            byte[] key = factory.generateSecret(spec).getEncoded();
            
            return new PBKDF2Result(salt, key, iterations);
        }

        public static boolean verifyKey(String password, byte[] salt, int iterations, int keyLen, byte[] expectedKey) throws Exception {
            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLen * 8);
            byte[] derivedKey = factory.generateSecret(spec).getEncoded();
            return MessageDigest.isEqual(derivedKey, expectedKey);
        }
    }

    public static class ECCrypto {
        
        public static KeyPair generateKeyPair() throws NoSuchAlgorithmException, InvalidAlgorithmParameterException {
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("EC");
            ECGenParameterSpec ecSpec = new ECGenParameterSpec("secp256r1");
            keyGen.initialize(ecSpec);
            return keyGen.generateKeyPair();
        }

        public static byte[] sign(byte[] message, PrivateKey privateKey) throws Exception {
            Signature signature = Signature.getInstance("SHA256withECDSA");
            signature.initSign(privateKey);
            signature.update(message);
            return signature.sign();
        }

        public static boolean verify(byte[] message, byte[] signatureBytes, PublicKey publicKey) throws Exception {
            Signature signature = Signature.getInstance("SHA256withECDSA");
            signature.initVerify(publicKey);
            signature.update(message);
            return signature.verify(signatureBytes);
        }
    }

    public static class SM9Crypto {
        
        public static byte[] generateMasterKey() throws Exception {
            // 注意：Java 标准库不直接支持 SM9 算法
            // 需要使用 Bouncy Castle 等第三方库
            // 这里返回一个模拟的主密钥
            byte[] masterKey = new byte[32];
            new SecureRandom().nextBytes(masterKey);
            return masterKey;
        }

        public static byte[] encrypt(byte[] plaintext, byte[] masterKey, String id) throws Exception {
            // 注意：Java 标准库不直接支持 SM9 算法
            // 需要使用 Bouncy Castle 等第三方库
            // 这里返回一个模拟的加密结果
            byte[] ciphertext = new byte[plaintext.length + 16];
            System.arraycopy(plaintext, 0, ciphertext, 0, plaintext.length);
            new SecureRandom().nextBytes(ciphertext, plaintext.length, 16);
            return ciphertext;
        }

        public static byte[] decrypt(byte[] ciphertext, byte[] masterKey, String id) throws Exception {
            // 注意：Java 标准库不直接支持 SM9 算法
            // 需要使用 Bouncy Castle 等第三方库
            // 这里返回一个模拟的解密结果
            byte[] plaintext = new byte[ciphertext.length - 16];
            System.arraycopy(ciphertext, 0, plaintext, 0, plaintext.length);
            return plaintext;
        }

        public static byte[] sign(byte[] message, byte[] masterKey, String id) throws Exception {
            // 注意：Java 标准库不直接支持 SM9 算法
            // 需要使用 Bouncy Castle 等第三方库
            // 这里返回一个模拟的签名
            byte[] signature = new byte[64];
            new SecureRandom().nextBytes(signature);
            return signature;
        }

        public static boolean verify(byte[] message, byte[] signature, byte[] masterKey, String id) throws Exception {
            // 注意：Java 标准库不直接支持 SM9 算法
            // 需要使用 Bouncy Castle 等第三方库
            // 这里返回一个模拟的验签结果
            return true;
        }
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    public static void demoAES() throws Exception {
        System.out.println("=".repeat(50));
        System.out.println("AES 加密解密演示");
        System.out.println("=".repeat(50));

        byte[] key = AESCrypto.generateKey(256);
        byte[] plaintext = "Hello, HarmonyOS Crypto Framework!".getBytes();

        System.out.println("原始数据: " + new String(plaintext));
        System.out.println("密钥 (hex): " + bytesToHex(key));

        AESCrypto.EncryptResult cbcResult = AESCrypto.encryptCBC(plaintext, key);
        System.out.println("CBC 加密结果 (hex): " + bytesToHex(cbcResult.ciphertext));

        byte[] decrypted = AESCrypto.decryptCBC(cbcResult.ciphertext, key, cbcResult.iv);
        System.out.println("CBC 解密结果: " + new String(decrypted));

        System.out.println("\n--- AES-GCM 模式 ---");
        AESCrypto.GCMResult gcmResult = AESCrypto.encryptGCM(plaintext, key, null);
        System.out.println("GCM 加密结果 (hex): " + bytesToHex(gcmResult.ciphertext));
        System.out.println("认证标签 (hex): " + bytesToHex(gcmResult.tag));

        byte[] gcmDecrypted = AESCrypto.decryptGCM(gcmResult.ciphertext, key, gcmResult.iv, gcmResult.tag, null);
        System.out.println("GCM 解密结果: " + new String(gcmDecrypted));
    }

    public static void demoRSA() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("RSA 加密解密演示");
        System.out.println("=".repeat(50));

        KeyPair keyPair = RSACrypto.generateKeyPair(2048);
        byte[] plaintext = "RSA Test Message".getBytes();

        System.out.println("原始数据: " + new String(plaintext));

        byte[] ciphertext = RSACrypto.encrypt(plaintext, keyPair.getPublic());
        System.out.println("加密结果 (hex): " + bytesToHex(ciphertext));

        byte[] decrypted = RSACrypto.decrypt(ciphertext, keyPair.getPrivate());
        System.out.println("解密结果: " + new String(decrypted));

        System.out.println("\n--- RSA 签名验签 ---");
        byte[] message = "Message to sign".getBytes();
        byte[] signature = RSACrypto.sign(message, keyPair.getPrivate());
        System.out.println("签名 (hex): " + bytesToHex(signature));

        boolean isValid = RSACrypto.verify(message, signature, keyPair.getPublic());
        System.out.println("验签结果: " + (isValid ? "成功" : "失败"));
    }

    public static void demoHash() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("消息摘要演示");
        System.out.println("=".repeat(50));

        byte[] data = "Hello, Crypto!".getBytes();

        System.out.println("原始数据: " + new String(data));
        System.out.println("MD5: " + HashCrypto.md5(data));
        System.out.println("SHA-1: " + HashCrypto.sha1(data));
        System.out.println("SHA-256: " + HashCrypto.sha256(data));
        System.out.println("SHA-384: " + HashCrypto.sha384(data));
        System.out.println("SHA-512: " + HashCrypto.sha512(data));
    }

    public static void demoHMAC() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("HMAC 消息认证码演示");
        System.out.println("=".repeat(50));

        byte[] key = new byte[32];
        new SecureRandom().nextBytes(key);
        byte[] message = "Hello, HMAC!".getBytes();

        System.out.println("原始数据: " + new String(message));
        System.out.println("密钥 (hex): " + bytesToHex(key));
        System.out.println("HMAC-SHA256: " + HMACCrypto.hmacSHA256(key, message));
        System.out.println("HMAC-SHA384: " + HMACCrypto.hmacSHA384(key, message));
        System.out.println("HMAC-SHA512: " + HMACCrypto.hmacSHA512(key, message));
    }

    public static void demoPBKDF2() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("PBKDF2 密钥派生演示");
        System.out.println("=".repeat(50));

        String password = "myPassword123";
        PBKDF2Crypto.PBKDF2Result result = PBKDF2Crypto.deriveKey(password, 32, 100000);

        System.out.println("密码: " + password);
        System.out.println("盐值 (hex): " + bytesToHex(result.salt));
        System.out.println("迭代次数: " + result.iterations);
        System.out.println("派生密钥 (hex): " + bytesToHex(result.key));

        boolean isValid = PBKDF2Crypto.verifyKey(password, result.salt, result.iterations, 32, result.key);
        System.out.println("密钥验证: " + (isValid ? "成功" : "失败"));
    }

    public static void demoEC() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("EC 椭圆曲线加密演示");
        System.out.println("=".repeat(50));

        KeyPair keyPair = ECCrypto.generateKeyPair();
        byte[] message = "EC Sign Test".getBytes();

        System.out.println("原始数据: " + new String(message));

        byte[] signature = ECCrypto.sign(message, keyPair.getPrivate());
        System.out.println("签名 (hex): " + bytesToHex(signature));

        boolean isValid = ECCrypto.verify(message, signature, keyPair.getPublic());
        System.out.println("验签结果: " + (isValid ? "成功" : "失败"));
    }

    public static void demoSM9() throws Exception {
        System.out.println("\n" + "=".repeat(50));
        System.out.println("SM9 国密算法演示");
        System.out.println("=".repeat(50));

        byte[] masterKey = SM9Crypto.generateMasterKey();
        byte[] plaintext = "Hello, SM9!".getBytes();
        String id = "user@example.com";

        System.out.println("原始数据: " + new String(plaintext));
        System.out.println("用户标识: " + id);

        // 加密解密
        byte[] ciphertext = SM9Crypto.encrypt(plaintext, masterKey, id);
        System.out.println("SM9 加密结果 (hex): " + bytesToHex(ciphertext));

        byte[] decrypted = SM9Crypto.decrypt(ciphertext, masterKey, id);
        System.out.println("SM9 解密结果: " + new String(decrypted));

        // 签名验签
        System.out.println("\n--- SM9 签名验签 ---");
        byte[] message = "Message to sign with SM9".getBytes();
        byte[] signature = SM9Crypto.sign(message, masterKey, id);
        System.out.println("签名 (hex): " + bytesToHex(signature));

        boolean isValid = SM9Crypto.verify(message, signature, masterKey, id);
        System.out.println("验签结果: " + (isValid ? "成功" : "失败"));
        System.out.println("注意: 由于 Java 标准库不直接支持 SM9 算法，这里使用的是模拟实现。");
        System.out.println("要使用真实的 SM9 算法，需要添加 Bouncy Castle 等第三方库。");
    }

    public static void main(String[] args) {
        try {
            demoAES();
            demoRSA();
            demoHash();
            demoHMAC();
            demoPBKDF2();
            demoEC();
            demoSM9();

            System.out.println("\n" + "=".repeat(50));
            System.out.println("所有演示完成!");
            System.out.println("=".repeat(50));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}