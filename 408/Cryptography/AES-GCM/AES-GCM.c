


/*
 * ============================================================================
 * AES-GCM (Galois/Counter Mode) - 伽罗瓦计数器模式
 * ============================================================================
 * 
 * 【形象理解】
 * GCM就像一位"既会保密又会防伪"的特工：
 * - CTR模式负责加密（保密）：像是一个计数器驱动的密码机
 * - GHASH负责认证（防伪）：像是一个特殊的"封条"，任何篡改都会破坏它
 * 
 * 【核心特点】
 * - 同时提供机密性(Confidentiality)和完整性(Integrity)
 * - 认证加密(AEAD: Authenticated Encryption with Associated Data)
 * - 可以保护明文的同时，认证未加密的附加数据（如包头信息）
 * 
 * 【工作流程】
 * 1. 用CTR模式加密明文
 * 2. 用GHASH计算认证标签
 * 3. 标签与密文一起发送
 */

/*
 * GF(2^128)乘法 - GHASH的核心运算
 * 
 * 【数学背景】
 * 在GF(2^128)中，使用不可约多项式：
 * g(x) = x^128 + x^7 + x^2 + x + 1
 * 
 * 【形象理解】
 * 想象两个128位的数字在一个特殊的"循环宇宙"中相乘。
 * 当结果超过128位时，不是简单截断，而是按照特定规则"折叠"回去。
 * 
 * 参数:
 *   x, y - 输入的两个128位元素（16字节）
 *   result - 输出结果
 */
void gf128_mul(const uint8_t x[16], const uint8_t y[16], uint8_t result[16]) {
    uint8_t z[16] = {0};  /* 累积结果，初始为0 */
    uint8_t v[16];        /* 临时变量，存储y的移位结果 */
    
    memcpy(v, y, 16);
    
    /* 
     * 逐位处理x（从最高位到最低位）
     * 这就像俄罗斯农民乘法的二进制版本
     */
    for (int i = 0; i < 16; i++) {
        for (int bit = 7; bit >= 0; bit--) {
            /* 如果x的当前位是1，把v加到结果中 */
            if ((x[i] >> bit) & 1) {
                for (int j = 0; j < 16; j++) {
                    z[j] ^= v[j];
                }
            }
            
            /* 
             * v右移一位（GF(2^128)中的除以x）
             * 如果最低位是1，需要异或0xe1（多项式的低7位）
             */
            uint8_t carry = v[15] & 1;  /* 保存移出的位 */
            
            /* 右移整个128位数 */
            for (int j = 15; j > 0; j--) {
                v[j] = (v[j] >> 1) | (v[j-1] << 7);
            }
            v[0] >>= 1;
            
            /* 如果移出了1，需要模约简 */
            if (carry) {
                v[0] ^= 0xe1;  /* 0xe1 = 0x1e1去掉最高位 */
            }
        }
    }
    
    memcpy(result, z, 16);
}

/*
 * GHASH函数 - 计算认证标签的核心
 * 
 * 【形象理解】
 * 想象H是一个"魔法常数"，GHASH就像用H作为"搅拌棒"，
 * 把所有数据块搅拌在一起，产生一个独特的"指纹"。
 * 
 * 数学公式: GHASH(H, X) = X_1·H^m ⊕ X_2·H^(m-1) ⊕ ... ⊕ X_m·H
 * 
 * 参数:
 *   h     - 哈希子密钥（E(K, 0^128)）
 *   x     - 输入数据（AAD || Ciphertext || 长度）
 *   x_len - 数据长度（字节）
 *   out   - 128位输出
 */
void ghash(const uint8_t *h, const uint8_t *x, size_t x_len, uint8_t *out) {
    uint8_t y[16] = {0};  /* 累加器，初始为0 */
    uint8_t block[16];    /* 当前处理的16字节块 */
    
    /* 逐块处理输入数据 */
    for (size_t i = 0; i < x_len; i += 16) {
        /* 取出当前块（不足16字节补0） */
        memset(block, 0, 16);
        size_t block_len = (x_len - i < 16) ? (x_len - i) : 16;
        memcpy(block, x + i, block_len);
        
        /* Y = (Y ⊕ X_i) · H */
        for (int j = 0; j < 16; j++) {
            y[j] ^= block[j];
        }
        
        gf128_mul(y, h, y);
    }
    
    memcpy(out, y, 16);
}

/*
 * GCTR - 计数器模式加密
 * 
 * 【形象理解】
 * 想象一个不断递增的"计数器"，每个值都通过AES加密变成
 * 一个"密钥流"块。明文与密钥流异或就得到密文。
 * 
 * 这就像一次性的密码本，但密码本是用AES动态生成的。
 * 
 * 参数:
 *   icb      - 初始计数器块（IV || 00000001）
 *   x        - 明文/密文输入
 *   x_len    - 数据长度
 *   key      - AES密钥
 *   y        - 输出（密文/明文）
 *   key_bits - 密钥长度
 */
void gctr(const uint8_t *icb, const uint8_t *x, size_t x_len, 
          const uint8_t *key, uint8_t *y, int key_bits) {
    uint8_t cb[16];           /* 当前计数器值 */
    uint8_t encrypted_cb[16]; /* 加密后的计数器 = 密钥流 */
    
    /* 复制初始计数器 */
    memcpy(cb, icb, 16);
    
    /* 逐块处理数据 */
    for (size_t i = 0; i < x_len; i += 16) {
        /* 加密当前计数器，生成密钥流 */
        aes_encrypt_block(cb, key, encrypted_cb, key_bits);
        
        /* 确定当前块长度（最后一块可能不足16字节） */
        size_t block_len = (x_len - i < 16) ? (x_len - i) : 16;
        
        /* 明文/密文与密钥流异或 */
        for (size_t j = 0; j < block_len; j++) {
            y[i + j] = x[i + j] ^ encrypted_cb[j];
        }
        
        /* 递增计数器（只递增最后32位，像里程表一样） */
        for (int j = 15; j >= 12; j--) {
            if (++cb[j] != 0) break;  /* 无进位时停止 */
        }
    }
}

/*
 * aes_gcm_encrypt - AES-GCM完整加密
 * 
 * 【输入输出】
 * 输入: 明文、附加数据(AAD)、密钥、IV
 * 输出: 密文、认证标签
 * 
 * 【完整流程】
 * 1. 计算H = E(K, 0^128)
 * 2. 构造J0（基于IV）
 * 3. 用GCTR加密明文
 * 4. 用GHASH计算认证标签
 * 5. 加密标签
 */
void aes_gcm_encrypt(const uint8_t *plaintext, size_t pt_len,
                     const uint8_t *aad, size_t aad_len,
                     const uint8_t *key, const uint8_t *iv, size_t iv_len,
                     uint8_t *ciphertext, uint8_t *tag, int key_bits) {
    
    /* ========== 步骤1: 计算哈希密钥H ========== */
    uint8_t h[16] = {0};  /* 全0块 */
    aes_encrypt_block(h, key, h, key_bits);
    /* 现在H = E(K, 0^128)，这是GHASH的"魔法搅拌棒" */
    
    /* ========== 步骤2: 构造初始计数器J0 ========== */
    uint8_t j0[16];
    
    if (iv_len == 12) {
        /* 标准情况：IV正好是96位 */
        memcpy(j0, iv, 12);       /* 前12字节是IV */
        j0[12] = 0; j0[13] = 0;   /* 后4字节是计数器，初始为1 */
        j0[14] = 0; j0[15] = 1;
    } else {
        /* 非标准IV：用GHASH计算J0 */
        ghash(h, iv, iv_len, j0);
        /* 附加长度信息... */
    }
    
    /* ========== 步骤3: 加密明文（GCTR）========== */
    uint8_t icb[16];  /* 初始计数器块 */
    memcpy(icb, j0, 16);
    
    /* 递增计数器用于加密（J0本身保留用于计算标签） */
    for (int i = 15; i >= 12; i--) {
        if (++icb[i] != 0) break;
    }
    
    gctr(icb, plaintext, pt_len, key, ciphertext, key_bits);
    
    /* ========== 步骤4: 计算认证标签 ========== */
    /*
     * GHASH输入格式: AAD || 0^v || Ciphertext || 0^u || len(AAD) || len(C)
     * 其中v和u是填充到16字节边界所需的0的个数
     */
    size_t ghash_len = ((aad_len + 15) / 16) * 16    /* AAD（填充后） */
                     + ((pt_len + 15) / 16) * 16     /* 密文（填充后） */
                     + 16;                            /* 两个64位长度字段 */
    
    uint8_t *ghash_input = malloc(ghash_len);
    size_t pos = 0;
    
    /* 添加AAD */
    memcpy(ghash_input + pos, aad, aad_len);
    pos += aad_len;
    /* 填充AAD到16字节边界 */
    while (pos % 16 != 0) ghash_input[pos++] = 0;
    
    /* 添加密文 */
    memcpy(ghash_input + pos, ciphertext, pt_len);
    pos += pt_len;
    /* 填充密文到16字节边界 */
    while (pos % 16 != 0) ghash_input[pos++] = 0;
    
    /* 添加长度字段（64位大端序） */
    uint64_t aad_bits = aad_len * 8;
    uint64_t c_bits = pt_len * 8;
    for (int i = 7; i >= 0; i--) {
        ghash_input[pos++] = (aad_bits >> (i * 8)) & 0xff;
    }
    for (int i = 7; i >= 0; i--) {
        ghash_input[pos++] = (c_bits >> (i * 8)) & 0xff;
    }
    
    /* 计算GHASH */
    uint8_t s[16];
    ghash(h, ghash_input, pos, s);
    free(ghash_input);
    
    /* ========== 步骤5: 加密标签 ========== */
    /* Tag = GCTR(J0, S) */
    gctr(j0, s, 16, key, tag, key_bits);
}