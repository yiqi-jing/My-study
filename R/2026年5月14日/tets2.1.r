"
练习题 10（新数据集）：随机森林分类评估 —— 使用 PimaIndiansDiabetes2 数据集
数据集说明
mlbench::PimaIndiansDiabetes2 包含 768 名印第安女性的医疗记录，目标变量 diabetes 为 pos（糖尿病阳性）或 neg（阴性）。特征包括怀孕次数、血糖浓度、血压等。数据中存在缺失值。
题目
使用随机森林对 PimaIndiansDiabetes2 进行分类。要求：
（1）缺失值处理：删除任意含缺失值的行。
（2）数据划分：按 70% 训练、30% 测试划分。
（3）训练随机森林：使用默认参数（ntree = 500）。
（4）计算混淆矩阵 及各项指标（精确率、召回率、F1 值）。
（5）对 (pos) 类别（糖尿病阳性）绘制 ROC 曲线，计算 AUC。
（6）使用 vip 包绘制变量重要性条形图，并解释前 3 个重要特征的临床意义。
"
library(mlbench)
library(randomForest)
library(caret)
library(pROC)
library(vip)
library(ggplot2)

data(PimaIndiansDiabetes2)

data_clean = na.omit(PimaIndiansDiabetes2)

set.seed(123)
train_index = createDataPartition(data_clean$diabetes, p = 0.7, list = FALSE)
train_data = data_clean[train_index, ]
test_data = data_clean[-train_index, ]

rf_model = randomForest(diabetes ~ ., data = train_data, ntree = 500)

pred = predict(rf_model, test_data)
conf_matrix = confusionMatrix(pred, test_data$diabetes, positive = "pos")
print(conf_matrix)

precision = conf_matrix$byClass["Precision"]
recall = conf_matrix$byClass["Recall"]
f1 = conf_matrix$byClass["F1"]
cat("\n精确率: ", precision, "\n")
cat("召回率: ", recall, "\n")
cat("F1 值: ", f1, "\n")

prob_pos = predict(rf_model, test_data, type = "prob")[, "pos"]
roc_obj = roc(test_data$diabetes, prob_pos, positive = "pos")
plot(roc_obj, main = "ROC 曲线", print.auc = TRUE)
print(plot)
vip(rf_model, num_features = 10, geom = "col", fill = "steelblue") +
  labs(title = "变量重要性", x = "变量", y = "重要性") +
  theme_minimal()

print(vip)

cat("\n前3个重要特征的临床意义：\n")
cat("1. glucose（血糖浓度）：血糖水平是诊断糖尿病的核心指标，高血糖是糖尿病的典型特征\n")
cat("2. mass（体重指数BMI）：肥胖是糖尿病的重要风险因素，BMI越高患病风险越大\n")
cat("3. age（年龄）：随着年龄增长，胰岛素分泌能力下降，患糖尿病风险增加\n")