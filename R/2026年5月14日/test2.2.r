"
练习题 9（新数据集）：回归模型比较 —— 使用 BostonHousing 数据集
数据集说明
mlbench::BostonHousing 包含 506 个波士顿房价样本，目标变量 medv（房屋中位价格，单位：千美元），特征包括犯罪率、房间数、距离就业中心等 13 个变量。这是一个经典的回归问题。
题目
使用 BostonHousing 数据集预测 medv（房价）。要求：
（1）数据划分：按 80% 训练、20% 测试划分。
（2）比较三种模型：线性回归（lm）、随机森林（rf）、支持向量机径向基（svmRadial）。
（3）交叉验证：使用 5 折交叉验证（仅在训练集上）评估各模型的 RMSE 和 R2。
（4）选择最优模型：基于交叉验证的 RMSE 选出最优模型，并在测试集上输出其最终性能。
"
library(mlbench)
library(caret)
library(randomForest)
library(e1071)

data(BostonHousing)

set.seed(123)
train_index = createDataPartition(BostonHousing$medv, p = 0.8, list = FALSE)
train_data = BostonHousing[train_index, ]
test_data = BostonHousing[-train_index, ]

train_control = trainControl(method = "cv", number = 5)

set.seed(123)
lm_model = train(medv ~ ., data = train_data, method = "lm", trControl = train_control)

set.seed(123)
rf_model = train(medv ~ ., data = train_data, method = "rf", trControl = train_control, ntree = 500)

set.seed(123)
svm_model = train(medv ~ ., data = train_data, method = "svmRadial", trControl = train_control)

lm_results = data.frame(
  Model = "线性回归",
  RMSE = lm_model$results$RMSE,
  R2 = lm_model$results$Rsquared
)

rf_results = data.frame(
  Model = "随机森林",
  RMSE = rf_model$results$RMSE[which.min(rf_model$results$RMSE)],
  R2 = rf_model$results$Rsquared[which.min(rf_model$results$RMSE)]
)

svm_results = data.frame(
  Model = "支持向量机",
  RMSE = svm_model$results$RMSE[which.min(svm_model$results$RMSE)],
  R2 = svm_model$results$Rsquared[which.min(svm_model$results$RMSE)]
)

all_results = rbind(lm_results, rf_results, svm_results)
cat("5折交叉验证结果：\n")
print(all_results)

best_model_index = which.min(all_results$RMSE)
best_model_name = all_results$Model[best_model_index]
cat("\n最优模型：", best_model_name, "\n")

if (best_model_name == "线性回归") {
  final_model = lm_model
} else if (best_model_name == "随机森林") {
  final_model = rf_model
} else {
  final_model = svm_model
}

pred = predict(final_model, test_data)
rmse_test = sqrt(mean((pred - test_data$medv)^2))
r2_test = cor(pred, test_data$medv)^2

cat("\n测试集性能：\n")
cat("RMSE: ", rmse_test, "\n")
cat("R2: ", r2_test, "\n")