/*
 * ============================================================================
 * AES (Advanced Encryption Standard) - 高级加密标准
 * ============================================================================
 * 
 * 【形象比喻】
 * AES就像一位技艺精湛的"数据厨师"，把明文(生食材)通过一系列复杂的
 * "烹饪步骤"(轮函数)加工成密文(美味佳肴)。每轮操作都像是不同的
 * 烹饪手法：切菜(ShiftRows)、调味(SubBytes)、搅拌(MixColumns)、
 * 最后撒上秘制调料(AddRoundKey)。
 * 
 * 【核心特点】
 * - 分组大小：固定128位(16字节)，像是一个标准大小的"餐盘"
 * - 密钥长度：128/192/256位，密钥越长"秘方"越复杂
 * - 结构：SPN(Substitution-Permutation Network)替换-置换网络
 * 
 * 【安全保证】
 * 至今没有实用的攻击方法能破解完整轮数的AES，就像没有小偷能破解
 * 一个设计完美的保险柜。
 */

#include <stdint.h>
#include <string.h>
#include <stdio.h>

/* ============================================================================
 * 第一部分：常量定义 - AES的"配方书"
 * ============================================================================ */

/*
 * S-Box (Substitution Box) - 字节替换盒
 * 
 * 【形象理解】
 * 这是一个256个格子的"密码映射表"，每个字节(0-255)都对应一个
 * 独特的替换值。就像间谍使用的密码本，把明文"hello"变成密文。
 * 
 * 【数学原理】
 * 每个值的计算：先求乘法逆元(GF(2^8))，再进行仿射变换
 * 这是AES唯一的非线性操作，提供"混乱"(Confusion)
 */
static const uint8_t SBOX[256] = {
    /* 0x00-0x0F */
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    
    /* 0x10-0x1F */
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    
    /* 0x20-0x2F */
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,
    0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    
    /* 0x30-0x3F */
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,
    0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    
    /* 0x40-0x4F */
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    
    /* 0x50-0x5F */
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
    0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    
    /* 0x60-0x6F */
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,
    0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    
    /* 0x70-0x7F */
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    
    /* 0x80-0x8F */
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,
    0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    
    /* 0x90-0x9F */
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,
    0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    
    /* 0xA0-0xAF */
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    
    /* 0xB0-0xBF */
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,
    0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    
    /* 0xC0-0xCF */
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,
    0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    
    /* 0xD0-0xDF */
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    
    /* 0xE0-0xEF */
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,
    0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    
    /* 0xF0-0xFF */
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,
    0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

/*
 * 逆S-Box - 解密的"反向密码本"
 * 
 * 【形象理解】
 * 如果S-Box是把"A"变成"X"的密码本，逆S-Box就是把"X"变回"A"的解码本。
 * 加密和解密就像锁门和开门，需要配对的钥匙。
 */
static const uint8_t INV_SBOX[256] = {
    /* 0x00-0x0F */
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38,
    0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    
    /* 0x10-0x1F */
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87,
    0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    
    /* 0x20-0x2F */
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d,
    0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    
    /* 0x30-0x3F */
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2,
    0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    
    /* 0x40-0x4F */
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16,
    0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    
    /* 0x50-0x5F */
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda,
    0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    
    /* 0x60-0x6F */
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a,
    0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    
    /* 0x70-0x7F */
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02,
    0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    
    /* 0x80-0x8F */
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea,
    0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    
    /* 0x90-0x9F */
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85,
    0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    
    /* 0xA0-0xAF */
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89,
    0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    
    /* 0xB0-0xBF */
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20,
    0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    
    /* 0xC0-0xCF */
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31,
    0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    
    /* 0xD0-0xDF */
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d,
    0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    
    /* 0xE0-0xEF */
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0,
    0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    
    /* 0xF0-0xFF */
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26,
    0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
};

/*
 * 轮常数 (Round Constants) - 每轮的"独特调料"
 * 
 * 【形象理解】
 * 就像做咖喱，每轮都加一点不同的香料，让味道层层递进。
 * 这些常数确保每轮的轮密钥都不同，增加密码的复杂性。
 * 
 * 【数学来源】
 * RCON[i] = x^(i-1) mod (x^8 + x^4 + x^3 + x + 1)
 * 其中x = 0x02，在GF(2^8)中计算
 */
static const uint8_t RCON[11] = {
    0x00,  /* 第0轮不使用 */
    0x01,  /* x^0 = 1 */
    0x02,  /* x^1 = 2 */
    0x04,  /* x^2 = 4 */
    0x08,  /* x^3 = 8 */
    0x10,  /* x^4 = 16 */
    0x20,  /* x^5 = 32 */
    0x40,  /* x^6 = 64 */
    0x80,  /* x^7 = 128 */
    0x1b,  /* x^8 = 256 mod 多项式 = 0x1b */
    0x36   /* x^9 */
};

/* ============================================================================
 * 第二部分：基础工具函数 - AES的"厨房工具"
 * ============================================================================ */

/*
 * gmul - 伽罗瓦域乘法 (Galois Field Multiplication)
 * 
 * 【形象理解】
 * 普通乘法：3 × 7 = 21
 * GF(2^8)乘法：就像在一个只有256个数字的"循环世界"里做乘法，
 * 结果超出255就会"绕圈"回来。
 * 
 * 【技术细节】
 * 在GF(2^8)中，使用不可约多项式：
 * m(x) = x^8 + x^4 + x^3 + x + 1 (对应0x11b)
 * 
 * 参数:
 *   a, b - 输入的两个GF(2^8)元素
 * 返回:
 *   a × b mod m(x) 的结果
 */
uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;  /* 累积结果，初始为0 */
    
    /* 
     * 俄罗斯农民乘法算法的GF版本
     * 就像把乘法拆成多次加法和移位
     */
    while (b) {
        /* 如果b的最低位是1，把当前的a加到结果中 */
        if (b & 1) {
            p ^= a;  /* GF(2^8)中加法是异或 */
        }
        
        /* 记录a的最高位，用于判断是否需要"绕圈" */
        uint8_t hi_bit = a & 0x80;
        
        /* a左移一位（相当于乘以x） */
        a <<= 1;
        
        /* 
         * 如果移出了最高位，需要模约简
         * 这就像时钟超过12点要回到1点
         */
        if (hi_bit) {
            a ^= 0x1b;  /* 0x1b = 0x11b去掉最高位 */
        }
        
        /* b右移一位，处理下一位 */
        b >>= 1;
    }
    
    return p;
}

/* ============================================================================
 * 第三部分：AES核心轮函数 - "烹饪四步法"
 * ============================================================================ */

/*
 * SubBytes - 字节替换（调味步骤）
 * 
 * 【形象理解】
 * 想象你有16个食材（16字节），每个都按照"神秘配方表"(S-Box)
 * 换成另一种食材。同样的食材总是换成同样的替代品，但看起来
 * 完全没有规律。
 * 
 * 【安全作用】
 * 提供非线性，这是抵抗线性攻击和差分攻击的关键。
 * 就像把明文和密钥的关系搅乱，让攻击者找不到规律。
 * 
 * 参数:
 *   state[16] - 4×4状态矩阵，按列优先存储
 *               视觉上的矩阵：
 *               [s0  s4  s8  s12]
 *               [s1  s5  s9  s13]
 *               [s2  s6  s10 s14]
 *               [s3  s7  s11 s15]
 */
void sub_bytes(uint8_t state[16]) {
    /* 遍历状态矩阵的每个字节 */
    for (int i = 0; i < 16; i++) {
        /* 用S-Box替换当前字节 */
        state[i] = SBOX[state[i]];
    }
}

/*
 * ShiftRows - 行移位（切菜摆盘）
 * 
 * 【形象理解】
 * 想象4×4的棋盘：
 * - 第0行：不动（国王不动）
 * - 第1行：左移1格（骑士左移）
 * - 第2行：左移2格（主教左移两格）
 * - 第3行：左移3格（城堡左移三格）
 * 
 * 这样每一列都会混合来自不同行的数据，实现"扩散"。
 * 
 * 【安全作用】
 * 提供扩散(Diffusion)，让一个字节影响多个字节。
 * 就像把不同食材切碎混合，味道互相渗透。
 */
void shift_rows(uint8_t state[16]) {
    uint8_t temp[16];  /* 临时存储，避免覆盖 */
    
    /* 第0行：保持不变 */
    temp[0]  = state[0];   /* 位置(0,0) */
    temp[4]  = state[4];   /* 位置(0,1) */
    temp[8]  = state[8];   /* 位置(0,2) */
    temp[12] = state[12];  /* 位置(0,3) */
    
    /* 第1行：循环左移1字节 */
    temp[1]  = state[5];   /* (1,0) ← (1,1) */
    temp[5]  = state[9];   /* (1,1) ← (1,2) */
    temp[9]  = state[13];  /* (1,2) ← (1,3) */
    temp[13] = state[1];   /* (1,3) ← (1,0) 绕回 */
    
    /* 第2行：循环左移2字节 */
    temp[2]  = state[10];  /* (2,0) ← (2,2) */
    temp[6]  = state[14];  /* (2,1) ← (2,3) */
    temp[10] = state[2];   /* (2,2) ← (2,0) */
    temp[14] = state[6];   /* (2,3) ← (2,1) */
    
    /* 第3行：循环左移3字节（等价于右移1字节） */
    temp[3]  = state[15];  /* (3,0) ← (3,3) */
    temp[7]  = state[3];   /* (3,1) ← (3,0) */
    temp[11] = state[7];   /* (3,2) ← (3,1) */
    temp[15] = state[11];  /* (3,3) ← (3,2) */
    
    /* 把结果复制回去 */
    memcpy(state, temp, 16);
}

/*
 * MixColumns - 列混淆（搅拌混合）
 * 
 * 【形象理解】
 * 想象每一列是4个不同颜色的颜料，MixColumns就像用一个
 * 特殊的搅拌器，按照固定配方把这4种颜料充分混合。
 * 混合后，每种新颜色都包含了原来4种颜色的信息。
 * 
 * 【数学原理】
 * 在GF(2^8)上的矩阵乘法：
 * 
 * [s'0]   [02 03 01 01]   [s0]
 * [s'1] = [01 02 03 01] × [s1]
 * [s'2]   [01 01 02 03]   [s2]
 * [s'3]   [03 01 01 02]   [s3]
 * 
 * 其中乘法就是gmul()，加法是异或。
 */
void mix_columns(uint8_t state[16]) {
    /* 逐列处理（共4列） */
    for (int c = 0; c < 4; c++) {
        /* 取出当前列的4个字节 */
        uint8_t a = state[c * 4 + 0];
        uint8_t b = state[c * 4 + 1];
        uint8_t c1 = state[c * 4 + 2];  /* 避免与列索引c冲突 */
        uint8_t d = state[c * 4 + 3];
        
        /* 
         * 计算新列的每个元素
         * 使用分配律优化：2×a = a<<1 (可能异或0x1b)
         */
        uint8_t a2 = gmul(a, 2);  /* 2×a */
        uint8_t b2 = gmul(b, 2);  /* 2×b */
        uint8_t c2 = gmul(c1, 2); /* 2×c */
        uint8_t d2 = gmul(d, 2);  /* 2×d */
        
        /* s'0 = 2×a + 3×b + c + d = 2×a + 2×b + b + c + d */
        state[c * 4 + 0] = a2 ^ b2 ^ b ^ c1 ^ d;
        
        /* s'1 = a + 2×b + 3×c + d */
        state[c * 4 + 1] = a ^ b2 ^ c2 ^ c1 ^ d;
        
        /* s'2 = a + b + 2×c + 3×d */
        state[c * 4 + 2] = a ^ b ^ c2 ^ d2 ^ d;
        
        /* s'3 = 3×a + b + c + 2×d */
        state[c * 4 + 3] = a2 ^ a ^ b ^ c1 ^ d2;
    }
}

/*
 * AddRoundKey - 轮密钥加（撒上秘制调料）
 * 
 * 【形象理解】
 * 这是每轮唯一使用密钥的地方。就像做菜最后撒上盐，
 * 把轮密钥和状态进行异或混合。没有这一步，前面的
 * 所有操作都是公开的、可逆的。
 * 
 * 【技术细节】
 * 轮密钥是通过密钥扩展算法从原始密钥派生出来的。
 * 每轮使用不同的16字节轮密钥。
 */
void add_round_key(uint8_t state[16], const uint8_t round_key[16]) {
    for (int i = 0; i < 16; i++) {
        state[i] ^= round_key[i];  /* 异或操作 */
    }
}

/* ============================================================================
 * 第四部分：密钥扩展 - 从主密钥派生轮密钥
 * ============================================================================ */

/*
 * key_expansion - AES密钥扩展算法
 * 
 * 【形象理解】
 * 想象主密钥是一颗种子，密钥扩展就是让它"生长"出多把钥匙。
 * 128位密钥长出11把钥匙（初始+10轮），256位长出15把。
 * 每把钥匙都是从前一把通过特定规则"变形"而来。
 * 
 * 【算法流程】
 * 1. 前N个字直接复制原始密钥（N=4/6/8，对应128/192/256位）
 * 2. 后续每个字W[i] = W[i-1] ⊕ W[i-N]
 * 3. 如果i是N的倍数，对W[i-1]进行特殊变换后再异或
 * 
 * 参数:
 *   key       - 原始密钥
 *   round_keys - 输出的轮密钥数组（11/13/15轮 × 16字节）
 *   key_bits  - 密钥长度（128/192/256）
 */
void key_expansion(const uint8_t *key, uint8_t *round_keys, int key_bits) {
    /* 
     * nk: 密钥字数（每个字4字节）
     * nr: 轮数（AES-128=10轮，AES-192=12轮，AES-256=14轮）
     * total_words: 总共需要的字数（每轮4个字 + 初始轮）
     */
    int nk = key_bits / 32;           /* 4, 6, 或 8 */
    int nr = nk + 6;                  /* 10, 12, 或 14 */
    int total_words = 4 * (nr + 1);   /* 44, 52, 或 60个字 */
    
    /* 步骤1: 复制原始密钥作为前nk个字 */
    for (int i = 0; i < nk; i++) {
        round_keys[i * 4 + 0] = key[i * 4 + 0];
        round_keys[i * 4 + 1] = key[i * 4 + 1];
        round_keys[i * 4 + 2] = key[i * 4 + 2];
        round_keys[i * 4 + 3] = key[i * 4 + 3];
    }
    
    /* 步骤2: 生成扩展密钥 */
    uint8_t temp[4];  /* 临时存储一个字 */
    
    for (int i = nk; i < total_words; i++) {
        /* 复制前一个字 */
        temp[0] = round_keys[(i-1) * 4 + 0];
        temp[1] = round_keys[(i-1) * 4 + 1];
        temp[2] = round_keys[(i-1) * 4 + 2];
        temp[3] = round_keys[(i-1) * 4 + 3];
        
        /* 每nk个字进行特殊变换 */
        if (i % nk == 0) {
            /*
             * RotWord: 循环左移1字节
             * [a,b,c,d] → [b,c,d,a]
             * 就像把四个数字的队列，第一个移到最后
             */
            uint8_t t = temp[0];
            temp[0] = temp[1];
            temp[1] = temp[2];
            temp[2] = temp[3];
            temp[3] = t;
            
            /* SubWord: 用S-Box替换每个字节 */
            temp[0] = SBOX[temp[0]];
            temp[1] = SBOX[temp[1]];
            temp[2] = SBOX[temp[2]];
            temp[3] = SBOX[temp[3]];
            
            /* 与轮常数异或（只异或第一个字节） */
            temp[0] ^= RCON[i / nk];
        }
        /* AES-256特殊情况：每4个字但非8的倍数时也做SubWord */
        else if (nk > 6 && i % nk == 4) {
            temp[0] = SBOX[temp[0]];
            temp[1] = SBOX[temp[1]];
            temp[2] = SBOX[temp[2]];
            temp[3] = SBOX[temp[3]];
        }
        
        /* W[i] = W[i-Nk] ⊕ temp */
        round_keys[i * 4 + 0] = round_keys[(i - nk) * 4 + 0] ^ temp[0];
        round_keys[i * 4 + 1] = round_keys[(i - nk) * 4 + 1] ^ temp[1];
        round_keys[i * 4 + 2] = round_keys[(i - nk) * 4 + 2] ^ temp[2];
        round_keys[i * 4 + 3] = round_keys[(i - nk) * 4 + 3] ^ temp[3];
    }
}

/* ============================================================================
 * 第五部分：AES加密主函数 - 完整的加密流程
 * ============================================================================ */

/*
 * aes_encrypt_block - AES单分组加密
 * 
 * 【形象理解】
 * 这就像一条16字节的"数据生产线"：
 * 1. 原材料（明文）进入
 * 2. 先做一次初始调味（AddRoundKey）
 * 3. 然后经过多轮精细加工（SubBytes→ShiftRows→MixColumns→AddRoundKey）
 * 4. 最后一轮少了搅拌步骤（MixColumns）
 * 5. 成品（密文）出炉
 * 
 * 参数:
 *   plaintext  - 16字节明文输入
 *   key        - 原始密钥
 *   ciphertext - 16字节密文输出
 *   key_bits   - 密钥长度（128/192/256）
 */
void aes_encrypt_block(const uint8_t *plaintext, const uint8_t *key, 
                       uint8_t *ciphertext, int key_bits) {
    /* 状态矩阵：AES处理的核心数据结构 */
    uint8_t state[16];
    
    /* 轮密钥数组：最大240字节（AES-256需要15轮×16字节） */
    uint8_t round_keys[240];
    
    /* 根据密钥长度确定轮数 */
    int nk = key_bits / 32;   /* 4, 6, 或 8 */
    int nr = nk + 6;          /* 10, 12, 或 14轮 */
    
    /* 步骤1: 复制明文到状态矩阵 */
    memcpy(state, plaintext, 16);
    
    /* 步骤2: 密钥扩展，生成所有轮密钥 */
    key_expansion(key, round_keys, key_bits);
    
    /* 步骤3: 初始轮密钥加（Whitening） */
    add_round_key(state, round_keys);
    
    /* 步骤4: 主轮循环（前nr-1轮） */
    for (int round = 1; round < nr; round++) {
        sub_bytes(state);        /* 字节替换 */
        shift_rows(state);       /* 行移位 */
        mix_columns(state);      /* 列混淆 */
        /* 使用当前轮的轮密钥 */
        add_round_key(state, round_keys + round * 16);
    }
    
    /* 步骤5: 最后一轮（无MixColumns） */
    sub_bytes(state);
    shift_rows(state);
    add_round_key(state, round_keys + nr * 16);
    
    /* 步骤6: 输出密文 */
    memcpy(ciphertext, state, 16);
}

/* ============================================================================
 * 第六部分：AES解密 - 逆向操作
 * ============================================================================ */

/*
 * 逆操作函数：就像把烹饪过程倒放
 */

/*
 * inv_sub_bytes - 逆字节替换
 * 
 * 【形象理解】
 * 用逆S-Box把替换后的字节还原回来。
 * 就像用解码本把密文翻译回明文。
 */
void inv_sub_bytes(uint8_t state[16]) {
    for (int i = 0; i < 16; i++) {
        state[i] = INV_SBOX[state[i]];
    }
}

/*
 * inv_shift_rows - 逆行移位
 * 
 * 【形象理解】
 * 加密时左移，解密时就右移。
 * 第1行右移1，第2行右移2，第3行右移3。
 */
void inv_shift_rows(uint8_t state[16]) {
    uint8_t temp[16];
    
    /* 第0行不变 */
    temp[0]  = state[0];   temp[4]  = state[4];   
    temp[8]  = state[8];   temp[12] = state[12];
    
    /* 第1行：右移1（等价于左移3） */
    temp[1]  = state[13];  temp[5]  = state[1];
    temp[9]  = state[5];   temp[13] = state[9];
    
    /* 第2行：右移2 */
    temp[2]  = state[10];  temp[6]  = state[14];
    temp[10] = state[2];   temp[14] = state[6];
    
    /* 第3行：右移3（等价于左移1） */
    temp[3]  = state[7];   temp[7]  = state[11];
    temp[11] = state[15];  temp[15] = state[3];
    
    memcpy(state, temp, 16);
}

/*
 * inv_mix_columns - 逆列混淆
 * 
 * 【数学原理】
 * 使用逆矩阵：
 * [0e 0b 0d 09]
 * [09 0e 0b 0d]
 * [0d 09 0e 0b]
 * [0b 0d 09 0e]
 * 
 * 这些系数是MixColumns矩阵在GF(2^8)中的逆。
 */
void inv_mix_columns(uint8_t state[16]) {
    for (int c = 0; c < 4; c++) {
        uint8_t a = state[c * 4 + 0];
        uint8_t b = state[c * 4 + 1];
        uint8_t c1 = state[c * 4 + 2];
        uint8_t d = state[c * 4 + 3];
        
        /* 使用逆矩阵系数计算 */
        state[c * 4 + 0] = gmul(a, 0x0e) ^ gmul(b, 0x0b) 
                         ^ gmul(c1, 0x0d) ^ gmul(d, 0x09);
        state[c * 4 + 1] = gmul(a, 0x09) ^ gmul(b, 0x0e) 
                         ^ gmul(c1, 0x0b) ^ gmul(d, 0x0d);
        state[c * 4 + 2] = gmul(a, 0x0d) ^ gmul(b, 0x09) 
                         ^ gmul(c1, 0x0e) ^ gmul(d, 0x0b);
        state[c * 4 + 3] = gmul(a, 0x0b) ^ gmul(b, 0x0d) 
                         ^ gmul(c1, 0x09) ^ gmul(d, 0x0e);
    }
}

/*
 * aes_decrypt_block - AES单分组解密
 * 
 * 【流程说明】
 * 解密是加密的完全逆过程，轮密钥使用顺序也倒过来。
 */
void aes_decrypt_block(const uint8_t *ciphertext, const uint8_t *key,
                       uint8_t *plaintext, int key_bits) {
    uint8_t state[16];
    uint8_t round_keys[240];
    
    int nk = key_bits / 32;
    int nr = nk + 6;
    
    /* 复制密文到状态 */
    memcpy(state, ciphertext, 16);
    
    /* 密钥扩展（与加密相同） */
    key_expansion(key, round_keys, key_bits);
    
    /* 最后一轮密钥加（使用最后一轮密钥） */
    add_round_key(state, round_keys + nr * 16);
    
    /* 逆主轮（倒序） */
    for (int round = nr - 1; round > 0; round--) {
        inv_shift_rows(state);   /* 先行移位 */
        inv_sub_bytes(state);    /* 再字节替换 */
        add_round_key(state, round_keys + round * 16);
        inv_mix_columns(state);  /* 最后逆列混淆 */
    }
    
    /* 初始逆轮 */
    inv_shift_rows(state);
    inv_sub_bytes(state);
    add_round_key(state, round_keys);  /* 使用初始轮密钥 */
    
    /* 输出明文 */
    memcpy(plaintext, state, 16);
}


/* ============================================================================
 * 第七部分：测试与验证 - 证明AES正确工作
 * ============================================================================ */



/*
 * print_hex - 以十六进制格式打印字节数组
 * 
 * 用于调试和验证，方便查看加密/解密结果
 */
void print_hex(const char* label, const uint8_t* data, int len) {
    printf("%s: ", label);
    for (int i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

/*
 * main - 程序入口点
 * 
 * 测试AES-128加密和解密功能
 * 使用官方NIST测试向量验证正确性
 */
int main() {
    printf("========================================\n");
    printf("AES-128 加密解密测试\n");
    printf("========================================\n\n");
    
    /* 
     * 测试向量（来自NIST FIPS-197附录A.1）
     * 这是官方标准测试数据，用于验证实现正确性
     */
    
    /* 128位密钥 (16字节) */
    uint8_t key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    
    /* 128位明文 (16字节) */
    uint8_t plaintext[16] = {
        0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d,
        0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34
    };
    
    /* 预期的密文（用于验证） */
    uint8_t expected_ciphertext[16] = {
        0x39, 0x25, 0x84, 0x1d, 0x02, 0xdc, 0x09, 0xfb,
        0xdc, 0x11, 0x85, 0x97, 0x19, 0x6a, 0x0b, 0x32
    };
    
    uint8_t ciphertext[16];
    uint8_t decrypted[16];
    
    /* 打印测试参数 */
    print_hex("密钥 (Key)", key, 16);
    print_hex("明文 (Plaintext)", plaintext, 16);
    printf("\n");
    
    /* 执行加密 */
    printf("--- 执行加密 ---\n");
    aes_encrypt_block(plaintext, key, ciphertext, 128);
    print_hex("计算密文", ciphertext, 16);
    print_hex("预期密文", expected_ciphertext, 16);
    
    /* 验证加密结果 */
    int match = 1;
    for (int i = 0; i < 16; i++) {
        if (ciphertext[i] != expected_ciphertext[i]) {
            match = 0;
            break;
        }
    }
    
    if (match) {
        printf("✓ 加密验证通过！密文与NIST标准一致\n");
    } else {
        printf("✗ 加密验证失败！请检查实现\n");
    }
    printf("\n");
    
    /* 执行解密 */
    printf("--- 执行解密 ---\n");
    aes_decrypt_block(ciphertext, key, decrypted, 128);
    print_hex("解密结果", decrypted, 16);
    
    /* 验证解密结果 */
    match = 1;
    for (int i = 0; i < 16; i++) {
        if (decrypted[i] != plaintext[i]) {
            match = 0;
            break;
        }
    }
    
    if (match) {
        printf("✓ 解密验证通过！明文与原始数据一致\n");
    } else {
        printf("✗ 解密验证失败！请检查实现\n");
    }
    
    printf("\n");
    printf("========================================\n");
    printf("所有测试完成\n");
    printf("========================================\n");
    
    return 0;
}