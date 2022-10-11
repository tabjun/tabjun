
import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.sandbox.stats.multicomp import MultiComparison
import scipy.stats
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer

from xgboost import XGBClassifier
from xgboost import plot_importance 
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
# In[3]:

import os
os.chdir('C:\\Users\\215-05\\Downloads\\sca')
os.getcwd()
'''
unu예측
'''

#%%
train = pd.read_csv('train_unu_sca.csv')

# In[6]:
final = pd.get_dummies(train,columns = [ 'income_type',
                                              'employment_type', 'houseown_type', 'purpose'])
# In[8]:
print(final.is_applied.value_counts())
x = final.drop(['Unnamed: 0', 'is_applied','houseown_type_자가'],axis=1)
y = final['is_applied']
#%%
X_train, X_val, y_train, y_val = train_test_split(x, y, test_size=0.25, random_state=777)
#%%
# 오버 샘플링
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_train_over, y_train_over = smote.fit_sample(X_train, y_train)
print("SMOTE 적용 전 학습용 피처/레이블 데이터 세트 : ", X_train.shape, y_train.shape)
print('SMOTE 적용 후 학습용 피처/레이블 데이터 세트 :', X_train_over.shape, y_train_over.shape)
print('SMOTE 적용 후 값의 분포 :\n',pd.Series(y_train_over).value_counts() )
#%%
xgb1 = XGBClassifier(
learning_rate =0.1,
n_estimators=1000,
max_depth=5,
min_child_weight=1,
gamma=0,
subsample=0.8,
colsample_bytree=0.8,
objective= 'binary:logistic',
nthread=-1,
scale_pos_weight=1,
)
#%%
xgb1.fit( X_train, y_train)
#%%
xgb_pred = xgb1.predict(X_val)
#%%
print(classification_report(y_val, xgb_pred, target_names=['class 0', 'class 1']))
#%%
from sklearn.metrics import roc_curve
pred_positive_label = xgb1.predict_proba(X_val)[:,1]

fprs, tprs, thresholds = roc_curve(y_val, pred_positive_label)

precisions, recalls, thresholds = roc_curve(y_val, pred_positive_label)

plt.figure(figsize=(15, 5))

plt.plot([0,1], [0, 1], label='STR')

plt.plot(fprs, tprs, label='ROC')

plt.xlabel('FPR')

plt.ylabel('TPR')

plt.leunud()

plt.grid()

plt.show()



#%%
test_unu = pd.read_csv('test_unu_sca.csv')
test_credit = pd.read_csv('test_unu_credit_sca.csv')
#%%
dum_test = pd.get_dummies(test_unu,columns = [ 'income_type',
                                                'employment_type', 'houseown_type', 'purpose'])
#%%
x_test = dum_test.drop(['Unnamed: 0.1','Unnamed: 0', 'is_applied','houseown_type_자가'],axis=1)
#%%
test_nona_predict = xgb1.predict(x_test)
#%%
a1= pd.DataFrame(test_nona_predict)
#%%
test_unu.is_applied = a1
#%%
test_unu.to_csv('unu_unu예측완_cp.csv',encoding = 'cp949')
test_unu.to_csv('unu_unu예측완.csv')

#%%
dum_test = pd.get_dummies(test_credit,columns = [ 'income_type',
                                                'employment_type', 'houseown_type', 'purpose'])
#%%
x_test = dum_test.drop(['Unnamed: 0.1','Unnamed: 0', 'is_applied','houseown_type_자가'],axis=1)
#%%
test_credit_predict = xgb1.predict(x_test)
#%%
a1= pd.DataFrame(test_credit_predict)
#%%
test_credit.is_applied = a1
#%%
test_credit.to_csv('unu_credit예측완_cp.csv',encoding = 'cp949')
test_credit.to_csv('unu_credit예측완.csv')