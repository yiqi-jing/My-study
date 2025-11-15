-- Active: 1761883161570@@node1@10000@log_recovery_test
-- 1. 创建测试数据库和表
-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS log_recovery_test;
USE log_recovery_test;

-- 创建用户表
CREATE TABLE IF NOT EXISTS user_behavior (
    user_id INT,
    username STRING,
    action STRING,
    action_time TIMESTAMP,
    ip_address STRING
)
PARTITIONED BY (dt STRING)
STORED AS ORC;

-- 创建备份表
CREATE TABLE user_behavior_backup LIKE user_behavior;

-- 2. 生成模拟操作日志
-- 操作日志记录（模拟2024-01-15的操作）

-- 09:00: 插入初始数据
INSERT INTO TABLE user_behavior PARTITION(dt='2024-01-15')
VALUES 
(1, 'user1', 'login', '2024-01-15 08:30:00', '192.168.1.100'),
(2, 'user2', 'purchase', '2024-01-15 09:15:00', '192.168.1.101'),
(3, 'user3', 'logout', '2024-01-15 10:00:00', '192.168.1.102');

-- 10:30: 更新用户行为（模拟业务操作）
INSERT OVERWRITE TABLE user_behavior PARTITION(dt='2024-01-15')
SELECT 
    user_id,
    username,
    CASE 
        WHEN user_id = 1 THEN 'purchase'
        ELSE action
    END as action,
    action_time,
    ip_address
FROM user_behavior
WHERE dt='2024-01-15';

-- 11:45: 新增用户数据
INSERT INTO TABLE user_behavior PARTITION(dt='2024-01-15')
VALUES 
(4, 'user4', 'login', '2024-01-15 11:30:00', '192.168.1.103'),
(5, 'user5', 'view', '2024-01-15 11:45:00', '192.168.1.104');

-- 检查当前数据
SELECT * FROM user_behavior ORDER BY user_id;

-- 创建备份
INSERT OVERWRITE TABLE user_behavior_backup PARTITION(dt)
SELECT * FROM user_behavior WHERE dt='2024-01-15';

-- 3. 模拟误操作
-- 14:00: 模拟误操作 - 错误地清除了分区数据
INSERT OVERWRITE TABLE user_behavior PARTITION(dt='2024-01-15')
SELECT user_id, username, action, action_time, ip_address
FROM user_behavior
WHERE 1=0;  -- 这个条件会导致数据全部被清空

-- 验证数据已丢失
SELECT COUNT(*) as remaining_records FROM user_behavior WHERE dt='2024-01-15';
-- 返回结果应该是 0

-- 4. 基于备份的恢复方案

-- 从备份恢复数据
INSERT OVERWRITE TABLE user_behavior PARTITION(dt='2024-01-15')
SELECT user_id, username, action, action_time, ip_address, dt
FROM user_behavior_backup 
WHERE dt='2024-01-15';

-- 验证恢复结果
SELECT COUNT(*) as restored_records FROM user_behavior WHERE dt='2024-01-15';
SELECT * FROM user_behavior ORDER BY user_id;
