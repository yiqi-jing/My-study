### 案例题2：客户流失预测——逻辑回归与模型评估

## 背景
# 电信公司提供了一份客户数据 churn.csv，变量包括：
# churn：是否流失（Yes/No）
# tenure：客户在网时长（月）
# monthly_charges：月均费用
# total_charges：总费用
# contract_type：合同类型（Month-to-month / One year / Two year）

## 任务要求：
# 1.读取数据，将 churn 转换为0/1（Yes=1，No=0）。
# 2.将 contract_type 转换为因子。
# 3.划分训练集（70%）和测试集（30%）（设置随机种子123）。
# 4.在训练集上建立逻辑回归模型（glm，family=binomial）。
# 5.用模型对测试集进行预测，得到流失概率。
# 6.设定阈值0.5，计算混淆矩阵，并计算精确率（Precision）、召回率（Recall）和F1分数。
# 7.绘制ROC曲线并计算AUC值。
# 8.解释 tenure 系数的含义。


# 加载所需包
if(!require(pROC)) install.packages('pROC');
library(pROC)

# 1. 读取数据并转换 churn 为 0/1
churn_data = read.csv("R/2026年5月20日/churn.csv", stringsAsFactors = FALSE)
churn_data$churn = ifelse(churn_data$churn == "Yes", 1, 0)

# 2. 将 contract_type 转换为因子
churn_data$contract_type = factor(churn_data$contract_type)

# 查看数据结构
cat("=== 数据结构 ===\n")
str(churn_data)

# 查看 churn 分布
cat("\n=== churn 分布 ===\n")
table(churn_data$churn)


# 3. 划分训练集（70%）和测试集（30%）
set.seed(123)
train_index = sample(1:nrow(churn_data), size = 0.7 * nrow(churn_data))
train_data = churn_data[train_index, ]
test_data = churn_data[-train_index, ]

cat("\n=== 数据集划分 ===\n")
cat(sprintf("训练集样本数：%d\n", nrow(train_data)))
cat(sprintf("测试集样本数：%d\n", nrow(test_data)))


# 4. 建立逻辑回归模型
log_model = glm(churn ~ tenure + monthly_charges + total_charges + contract_type, 
                 data = train_data, family = binomial)

cat("\n=== 逻辑回归模型结果 ===\n")
summary(log_model)


# 5. 对测试集进行预测，得到流失概率
test_prob = predict(log_model, newdata = test_data, type = "response")


# 6. 设定阈值0.5，计算混淆矩阵和评估指标
test_pred = ifelse(test_prob >= 0.5, 1, 0)
confusion_matrix = table(Actual = test_data$churn, Predicted = test_pred)

cat("\n=== 混淆矩阵 ===\n")
print(confusion_matrix)

# 计算精确率、召回率和F1分数
TP = confusion_matrix[2, 2]
TN = confusion_matrix[1, 1]
FP = confusion_matrix[1, 2]
FN = confusion_matrix[2, 1]

precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1 = 2 * precision * recall / (precision + recall)

cat("\n=== 模型评估指标 ===\n")
cat(sprintf("精确率 (Precision): %.4f\n", precision))
cat(sprintf("召回率 (Recall): %.4f\n", recall))
cat(sprintf("F1分数 (F1 Score): %.4f\n", f1))


# 7. 绘制ROC曲线并计算AUC值
roc_obj = roc(test_data$churn, test_prob)
cat("\n=== ROC曲线 ===\n")
plot(roc_obj, main = "ROC Curve", col = "blue", lwd = 2)
auc_value = auc(roc_obj)
cat(sprintf("AUC值: %.4f\n", auc_value))


# 8. 解释 tenure 系数的含义
cat("\n=== tenure 系数解释 ===\n")
tenure_coef = coef(log_model)["tenure"]
cat(sprintf("tenure 的系数为 %.4f\n", tenure_coef))
cat("解释：在其他变量不变的情况下，客户在网时长每增加1个月，\n")
cat("流失的对数几率（log odds）平均变化", sprintf("%.4f", tenure_coef), "\n")
cat(sprintf("由于系数为负（%.4f），说明在网时长越长，流失概率越低。\n", tenure_coef))
cat("优势比（Odds Ratio）为", sprintf("%.4f", exp(tenure_coef)), "\n")