"
10.使用随机森林对iris分类。
（1）计算混淆矩阵及各项指标（准确率、召回率、F1）
（2）对“versicolor”类别绘制一堆多ROC曲线，计算auc。
（3）使用vip包绘制变量重要性条形图
"

# 导包
if(!require(pROC)) install.packages("pROC"); library(pROC)
if(!require(vip))  install.packages("vip");library(vip)
if(!require(caret)) install.packages("caret"); library(caret)
if(!require(randomForest)) install.packages("randomForest"); library(randomForest)

data(iris)
# 构建随机森林模型
rf = randomForest(Species ~., data = iris )
pred = predict(rf)
print(pred)


# （1）计算混淆矩阵及各项指标（准确率、召回率、F1）
cm = confusionMatrix(pred, iris$Species)
print(cm$byClass)

# （2）对“versicolor”类别绘制一堆多ROC曲线，计算auc。
binary_labels = ifelse(iris$Species == 'versicolor', 1,0)
prob_versi = predict(rf, type = 'prob')[,'versicolor']
roc_versi = roc(binary_labels, prob_versi)
auc(roc_versi)
print(plot(roc_versi, mian = 'versicolor vs 其他'))

# （3）使用vip包绘制变量重要性条形图

print(vip(rf) + theme_minimal())
