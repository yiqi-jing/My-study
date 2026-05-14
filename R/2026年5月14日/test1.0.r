"
9.使用mtcars预测mpg（回归）
（1）比较三种模型：线性回归、随机森林、支持向量机
（2）使用5折交叉验证，输出各模型的rmse和r²
（3）选择最优模型
"

# 加载包
if(! require(caret)) install.packages("caret"); library(caret)

# 导入数据
data(mtcars)
# print(mtcars)

# 设置参数
control = trainControl(method = 'cv', number = 5)
# （1）比较三种模型：线性回归、随机森林、支持向量机
# 线性回归
lm_model = train(mpg ~., data = mtcars, method = 'lm', trControl = control)
rf_model = train(mpg ~., data = mtcars, method = 'rf', trControl = control)
svm_model = train(mpg ~., data = mtcars, method = 'svmRadial', trControl = control)

# （2）使用5折交叉验证，输出各模型的rmse和r²
res = resamples(list(Lm = lm_model, RF = rf_model , SVM = svm_model))
print(summary(res))
# （3）选择最优模型