### 案例题3：客户购买行为预测——随机森林与调优

## 背景
# 某电商平台提供了用户历史数据 ecommerce.csv，变量如下：
# purchase：是否购买（0/1，因变量）
# age：年龄
# income：年收入（千美元）
# pages_visited：浏览页面数
# time_on_site：网站停留时间（分钟）
# membership_years：会员年限

## 任务要求：
# 1.加载 randomForest 和 caret 包。
# 2.读取数据，确保因变量为因子类型。
# 3.将数据集按8:2分为训练集和测试集（随机种子456）。
# 4.使用随机森林算法在训练集上建模（默认参数，树的数量500）。
# 5.计算模型的OOB误差，并输出变量重要性排序（使用 importance() 和 varImpPlot()）。
# 6.使用 caret 包对 mtry 参数进行5折交叉验证调优（mtry 候选值：2, 3, 4, 5）。
# 7.用调优后的模型预测测试集，计算准确率（Accuracy）和AUC值。
# 8.解释为什么随机森林不容易过拟合。


# 1. 加载所需包
if(!require(randomForest)) install.packages('randomForest');
if(!require(caret)) install.packages('caret');
if(!require(pROC)) install.packages('pROC');
library(randomForest)
library(caret)
library(pROC)

# 2. 读取数据，确保因变量为因子类型
ecommerce_data = read.csv("R/2026年5月20日/ecommerce.csv", stringsAsFactors = FALSE)
ecommerce_data$purchase = factor(ecommerce_data$purchase, levels = c(0, 1), labels = c("No", "Yes"))

# 查看数据结构
cat("=== 数据结构 ===\n")
str(ecommerce_data)

# 查看 purchase 分布
cat("\n=== purchase 分布 ===\n")
table(ecommerce_data$purchase)


# 3. 将数据集按8:2分为训练集和测试集
set.seed(456)
train_index = sample(1:nrow(ecommerce_data), size = 0.8 * nrow(ecommerce_data))
train_data = ecommerce_data[train_index, ]
test_data = ecommerce_data[-train_index, ]

cat("\n=== 数据集划分 ===\n")
cat(sprintf("训练集样本数：%d\n", nrow(train_data)))
cat(sprintf("测试集样本数：%d\n", nrow(test_data)))


# 4. 使用随机森林算法在训练集上建模（默认参数，树的数量500）
rf_model = randomForest(purchase ~ age + income + pages_visited + time_on_site + membership_years,
                         data = train_data, ntree = 500)

cat("\n=== 随机森林模型结果 ===\n")
print(rf_model)


# 5. 计算模型的OOB误差，并输出变量重要性排序
cat("\n=== OOB误差 ===\n")
oob_error = 1 - rf_model$err.rate[nrow(rf_model$err.rate), "OOB"]
cat(sprintf("OOB准确率: %.4f\n", oob_error))
cat(sprintf("OOB误差率: %.4f\n", 1 - oob_error))

# 变量重要性
cat("\n=== 变量重要性 ===\n")
importance_table = importance(rf_model)
print(importance_table)

# 绘制变量重要性图
cat("\n=== 变量重要性图 ===\n")
varImpPlot(rf_model, main = "Variable Importance Plot")


# 6. 使用 caret 包对 mtry 参数进行5折交叉验证调优
cat("\n=== 5折交叉验证调优 mtry 参数 ===\n")
set.seed(456)
train_control = trainControl(method = "cv", number = 5, classProbs = TRUE, summaryFunction = twoClassSummary)

tune_grid = expand.grid(mtry = c(2, 3, 4, 5))

rf_tune = train(purchase ~ age + income + pages_visited + time_on_site + membership_years,
                 data = train_data,
                 method = "rf",
                 trControl = train_control,
                 tuneGrid = tune_grid,
                 ntree = 500,
                 metric = "ROC")

cat("\n=== 调优结果 ===\n")
print(rf_tune)

best_mtry = rf_tune$bestTune$mtry
cat(sprintf("\n最优 mtry 参数: %d\n", best_mtry))


# 7. 用调优后的模型预测测试集，计算准确率和AUC值
best_rf_model = rf_tune$finalModel

# 预测类别
test_pred = predict(best_rf_model, newdata = test_data)
accuracy = sum(test_pred == test_data$purchase) / nrow(test_data)

# 预测概率（用于AUC计算）
test_prob = predict(best_rf_model, newdata = test_data, type = "prob")[, "Yes"]
roc_obj = roc(test_data$purchase, test_prob)
auc_value = auc(roc_obj)

cat("\n=== 测试集评估结果 ===\n")
cat(sprintf("准确率 (Accuracy): %.4f\n", accuracy))
cat(sprintf("AUC值: %.4f\n", auc_value))

# 混淆矩阵
confusion_matrix = table(Actual = test_data$purchase, Predicted = test_pred)
cat("\n=== 混淆矩阵 ===\n")
print(confusion_matrix)


# 8. 解释为什么随机森林不容易过拟合
cat("\n=== 随机森林不易过拟合的原因 ===\n")
cat("1. 随机抽样（Bootstrap Samples）：\n")
cat("   - 每棵树使用不同的训练样本（有放回抽样），增加了模型的多样性\n")
cat("\n2. 随机特征选择（Random Feature Selection）：\n")
cat("   - 每个节点分裂时只考虑部分特征，防止单一强特征主导所有树\n")
cat("\n3. 集成学习（Ensemble Learning）：\n")
cat("   - 通过多棵树的投票/平均预测，降低了单棵树的过拟合影响\n")
cat("\n4. 无剪枝策略：\n")
cat("   - 每棵树可以完全生长，但通过随机化和集成，整体模型仍然具有较好的泛化能力\n")
cat("\n5. OOB（Out-of-Bag）评估：\n")
cat("   - 使用未参与训练的样本评估模型，可以及时发现过拟合问题\n")