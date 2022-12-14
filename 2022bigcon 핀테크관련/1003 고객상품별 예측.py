# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 12:09:17 2022

@author: 215-01
"""

'''
고객유형으로 분류하고, 예측을 내놓게 된다면, 상품 종류에 관계없이, 0과 1로 예측함.

유형 분류보다 상품분류를 기준으로 분석을 하고, 지금까지 하던 고객유형별 데이터셋을
들고 분석하는게 좋을 듯
이 때 6월이냐 아니냐에 & 개인회생 여부 따라 train,test나누기
'''

import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
from sklearn.preprocessing import LabelEncoder
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.sandbox.stats.multicomp import MultiComparison
import scipy.stats
from sklearn.preprocessing import RobustScaler
import statsmodels.api as sm
import random
from sklearn import linear_model  # logistic regression model
from statsmodels.stats.outliers_influence import variance_inflation_factor
#%%
# 경로지정
os.chdir('C:\\Users\\215-01\\Desktop\\빅콘\\2022빅콘테스트_데이터분석리그_데이터분석분야_퓨처스부문_데이터셋_220908')
os.getcwd()
#%%
#숫자 지수표현없이 출력
pd.options.display.float_format = '{:.2f}'.format
#%%
# 플랏 한글
from matplotlib import font_manager, rc
font_path = "C:/Windows/Fonts/NGULIM.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)
#%%
loan = pd.read_csv('loan_result.csv')
log = pd.read_csv('log_data.csv')
user = pd.read_csv('user_spec.csv',encoding=('UTF-8'))
#%%
print(loan.info()) # 데이터가 너무 커서 dtype이 안나옴
print(loan.dtypes)
print(loan.isnull().sum())
print(loan.describe(include='all'))
#%%
print(log.info())
print(log.dtypes)
print(log.isnull().sum())
print(log.describe(include='all'))
#%%
print(user.info())
print(user.dtypes)
print(user.isnull().sum())
print(user.describe(include='all'))
#%%
#log_data의 어플 버전, 안드로이드 ios구분, 값이 다르다. 
# 태경 안드로이드 폰으로 버전 보여주고, 소문자 값이 휴대폰인지 확인
print(log['mp_os'].value_counts())
print(log['mp_app_version'].value_counts())

#%%
# left join으로 진행
# user 와 loan 데이터 셋의 application_id 정렬 이후 
sort_loan = loan.sort_values('application_id')
sort_log = log.sort_values('user_id')
sort_user = user.sort_values('application_id')
#%%
left = pd.merge(sort_loan, sort_user, left_on='application_id', 
                 right_on='application_id', how='left')
print(left.isnull().sum())
left_copy = left.copy()
#%%
#datetime변환을 이용하여 6월 데이터 개수 확인
left_copy['loanapply_insert_time'] = pd.to_datetime(left_copy['loanapply_insert_time'])
# datetime변수에서 month추출
left_copy['month'] = pd.DatetimeIndex(left_copy['loanapply_insert_time']).month
#%%
# purpose 값 바꿔주기
left_copy = left_copy.replace('LIVING','생활비')
left_copy = left_copy.replace('SWITCHLOAN', '대환대출')
left_copy = left_copy.replace('BUSINESS', '사업자금')
left_copy = left_copy.replace('ETC', '기타')
left_copy = left_copy.replace('HOUSEDEPOSIT', '전월세보증금')
left_copy = left_copy.replace('BUYHOUSE', '주택구입')
left_copy = left_copy.replace('INVEST', '투자')
left_copy = left_copy.replace('BUYCAR', '자동차구입')

#%%
# 단변량 로짓으로 유의성 판단, 이 때 개인회생 여부로 나눠서, 일반적인 경우, 
# 개인 회생만 고려할 것이 아니라, 개인 회생 납입 완료 여부도 고려해서 함께 나눠줘야 함.
# 개인 회생이 결측이라도, 개인 회생 납입 여부 == 1, 이면 개인 회생 신청한 애들
# 개인 회생을 신청했어도, 변제 금액을 다 갚고, 신용 점수 회복한 애들(5~6등급)
# 다시 일반적인 범위로 들어온 애들
# 아닌 경우도 함께 파악
# 개인회생 !=1 & !6월 = general train셋, 개인회생 ==1 & !6월 = unusual train셋
# 개인회생 !=1 & 6월 = 일반적인 test셋, 개인회생 ==1 & 6월 = 일반적이지 않은 test셋

# unusual train set, 6월이 아니면서, 개인회생이 1이거나, 개인 회생 납입 완료 여부 1
train_unu = left_copy[(left_copy['month']!=6)&
                      ((left_copy['personal_rehabilitation_yn']==1)|
                       (left_copy['personal_rehabilitation_complete_yn']==1))]
# general train set, 6월이 아니면서, 개인회생이 !=1 이면서, 개인 회생 납입 완료 여부 != 1
train_gen = left_copy[(left_copy['month']!=6)&
                      ((left_copy['personal_rehabilitation_yn']!=1)&
                       (left_copy['personal_rehabilitation_complete_yn']!=1))]
# unusual train set, 6월이면서, 개인회생이 1이거나, 개인 회생 납입 완료 여부 1
test_unu = left_copy[(left_copy['month']==6)&
                     ((left_copy['personal_rehabilitation_yn']==1)|
                       (left_copy['personal_rehabilitation_complete_yn']==1))]
# unusual train set, 6월이 아니면서, 개인회생이 1이거나, 개인 회생 납입 완료 여부 1
test_gen = left_copy[(left_copy['month']==6)&
                     ((left_copy['personal_rehabilitation_yn']!=1)&
                     (left_copy['personal_rehabilitation_complete_yn']!=1))]
#%%
train_unu.to_csv('train_unu.csv',encoding = 'cp949')
test_unu.to_csv('test_unu.csv',encoding = 'cp949')
train_gen.to_csv('train_gen.csv',encoding = 'cp949')
test_gen.to_csv('test_gen.csv',encoding = 'cp949')
#%%
train_unu = pd.read_csv('train_unu.csv',encoding = 'cp949')
test_unu = pd.read_csv('test_unu.csv',encoding = 'cp949')
train_gen = pd.read_csv('train_gen.csv',encoding = 'cp949')
test_gen = pd.read_csv('test_gen.csv',encoding = 'cp949')

#%%
# gen의 개인 회생, 납입 완료 값 확인 0 또는 결측만 있음, 잘 담김
print('일반 훈련셋')
print(train_gen[['personal_rehabilitation_yn','personal_rehabilitation_complete_yn']].value_counts())
print('일반 테스트 셋')
print(test_gen[['personal_rehabilitation_yn','personal_rehabilitation_complete_yn']].value_counts())
print('특별 훈련셋')
print(train_unu[['personal_rehabilitation_yn','personal_rehabilitation_complete_yn']].value_counts())
print('특별 테스트')
print(test_unu[['personal_rehabilitation_yn','personal_rehabilitation_complete_yn']].value_counts())

#%%
# 일반적인 경우를 분석하기 위해 train_gen 먼저
print(train_gen.isnull().sum())
print(train_gen.personal_rehabilitation_complete_yn.value_counts())
print(test_gen.isnull().sum())
print(test_gen.personal_rehabilitation_complete_yn.value_counts())
# 결측치 종류 MAR, 개인 회생 납입 완료 여부 변수, 1을 제외하곤 개인회생조차 신청안했거나,
# 개인회생을 신청안했지만 납입 하지 않은 경우, 결측치 0으로 채워주면 됨
print('결측치 개수 파악')
train_gen['personal_rehabilitation_complete_yn'].fillna(0,inplace = True)
test_gen['personal_rehabilitation_complete_yn'].fillna(0,inplace = True)
train_gen['personal_rehabilitation_yn'].fillna(0,inplace = True)
test_gen['personal_rehabilitation_yn'].fillna(0,inplace = True)
print(f'개인회생납입 완료 여부 결측 개수: {train_gen.personal_rehabilitation_complete_yn.isnull().sum()}')
print(f'개인회생 여부 결측 개수: {train_gen.personal_rehabilitation_yn.isnull().sum()}')
print(f'test개인회생납입 완료 여부 결측 개수: {test_gen.personal_rehabilitation_complete_yn.isnull().sum()}')
print(f'test개인회생 여부 결측 개수: {test_gen.personal_rehabilitation_yn.isnull().sum()}')

#%%
# 나눠진 데이터 셋들의 정보에는, 개인 회생을 신청한 사람과, 신청하지 않은 사람의 정보가 담겨있음.
# 정보가 다 담겨 있기 때문에, 굳이 결측을 채워주지 않고, 변수를 제거하고 사용
# 개인회생 여부 포함하면서 나눠줌, gen, unu 셋에는 개인회생을 신청한 애들과, 신청안한 애들
# 나눠짐, 변수 제거해도 그 속성은 남아있어서 변수 제거
# unu는 개인회생 완납, 미납 차이있는지 살펴봐야해서 완납은 살려 둠
train_unu.drop(['personal_rehabilitation_yn'],axis=1,inplace =True)
train_gen.drop(['personal_rehabilitation_yn','personal_rehabilitation_complete_yn'],axis=1,inplace =True)
test_unu.drop(['personal_rehabilitation_yn'],axis=1,inplace =True)
test_gen.drop(['personal_rehabilitation_yn','personal_rehabilitation_complete_yn'],axis=1,inplace =True)

#%%
# 6월에 존재하는 결측치, train셋에도 있는지 살표보기
a = test_gen[test_gen['month']==6]['application_id'].tolist()
app = train_gen[train_gen['application_id'].isin(a)]
print(app.isnull().sum())
#%%
# 로지스틱
logis_gen_birth = sm.Logit.from_formula('is_applied ~ birth_year', train_gen).fit()
print(logis_gen_birth.summary())
print(np.exp(logis_gen_birth.params)) #  로짓값 출력
print(f'train_gen:{logis_gen_birth.aic}')

logis_unu_birth = sm.Logit.from_formula('is_applied ~ birth_year', train_unu).fit()
print(logis_unu_birth.summary())
print(np.exp(logis_unu_birth.params)) #  로짓값 출력
print(f'train_unu:{logis_unu_birth.aic}')
#%%
logis_gen_bank = sm.Logit.from_formula('is_applied ~ bank_id', train_gen).fit()
print(logis.summary())
print(np.exp(logis_gen_bank.params)) #  로짓값 출력
print(f'train_gen:{logis_gen_bank.aic}')

logis_unu_bank = sm.Logit.from_formula('is_applied ~ bank_id', train_unu).fit()
print(logis.summary())
print(np.exp(logis_gen_birth.params)) #  로짓값 출력
print(f'train_gen:{logis_gen_birth.aic}')
#%%
logis = sm.Logit.from_formula('is_applied ~ product_id', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ product_id', train_unu).fit()
print(logis.summary())

#%%
logis = sm.Logit.from_formula('is_applied ~ loan_limit', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ loan_limit', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ loan_rate', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ loan_rate', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ gender', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ gender', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ credit_score', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ credit_score', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ yearly_income', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ yearly_income', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ income_type', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ income_type', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ employment_type', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ employment_type', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ houseown_type', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ houseown_type', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ desired_amount', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ desired_amount', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ purpose', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ purpose', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ existing_loan_cnt', train_gen).fit()
print(logis.summary())

logis = sm.Logit.from_formula('is_applied ~ existing_loan_cnt', train_unu).fit()
print(logis.summary())
#%%
logis = sm.Logit.from_formula('is_applied ~ existing_loan_amt', train_gen).fit()
print(logis.summary())


logis = sm.Logit.from_formula('is_applied ~ existing_loan_amt', train_unu).fit()
print(logis.summary())
''' 
단변량 전부 다 유의, 표본이 상당히 많으므로 편차가 줄어든다, 데이터가 중앙으로 몰림
정규분포 형태를 띔,
'''
#%%
# 수치형 변수 스케일링
# 이상치 확인
train_gen_num = train_gen.copy()[['loan_limit','loan_rate','credit_score','yearly_income','desired_amount',
                        'existing_loan_cnt','existing_loan_amt']]

f, ax = plt.subplots(figsize=(16, 14))
#ax.set_xscale("log")
ax = sns.boxplot(data = train_gen_num , orient="h", palette="Set1")

ax.xaxis.grid(False)

plt.xlabel("Numeric values", fontsize = 10)
plt.ylabel("Feature names", fontsize = 10)
plt.title("Numeric Distribution of Features", fontsize = 15)
sns.despine(trim = True, left = True)
#%%
# train_gen 스케일링을 위한 수치형, 범주형 나누기
train_gen_num = train_gen.copy()[['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']]
train_gen_ob = train_gen.copy().drop(['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                      'existing_loan_cnt','existing_loan_amt'],axis=1)
#%%
# train_unu 스케일링을 위한 수치형, 범주형 나누기
train_unu_num = train_unu.copy()[['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']]
train_unu_ob = train_unu.copy().drop(['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                      'existing_loan_cnt','existing_loan_amt'],axis=1)
#%%
# test_gen 스케일링을 위한 수치형, 범주형 나누기
test_gen_num = test_gen.copy()[['loan_limit','loan_rate','birth_year','credit_score','yearly_income','desired_amount',
                                 'existing_loan_cnt','existing_loan_amt']]
test_gen_ob = test_gen.copy().drop(['loan_limit','loan_rate','birth_year','credit_score','yearly_income','desired_amount',
                                     'existing_loan_cnt','existing_loan_amt'],axis=1)
#%%
# train_unu 스케일링을 위한 수치형, 범주형 나누기
test_unu_num = test_unu.copy()[['loan_limit','loan_rate','birth_year','credit_score','yearly_income','desired_amount',
                                 'existing_loan_cnt','existing_loan_amt']]
test_unu_ob = test_unu.copy().drop(['loan_limit','loan_rate','birth_year','credit_score','yearly_income','desired_amount',
                                     'existing_loan_cnt','existing_loan_amt'],axis=1)
#%%
# 이상치가 존재하므로 수치형 변수 gen 스케일링
rbs = RobustScaler()
train_gen_scaled = rbs.fit_transform(train_gen_num)
test_gen_scaled = rbs.transform(test_gen_num)
#%%
# unu 스케일링
train_unu_scaled = rbs.fit_transform(train_unu_num)
test_unu_scaled = rbs.transform(test_unu_num)
#%%
# 배열 형태로 반환되므로, 데이터 프레임으로 변환
train_gen_scaled = pd.DataFrame(data = train_gen_scaled )
test_gen_scaled = pd.DataFrame(data = test_gen_scaled)
train_unu_scaled = pd.DataFrame(data = train_unu_scaled)
test_unu_scaled = pd.DataFrame(data = test_unu_scaled)
#%%
# 변수명 삽입
train_gen_scaled.columns = ['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']

train_unu_scaled.columns = ['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']

test_gen_scaled.columns = ['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']

test_unu_scaled.columns = ['loan_limit','birth_year','loan_rate','credit_score','yearly_income','desired_amount',
                                  'existing_loan_cnt','existing_loan_amt']
#%%
# 나눠준 데이터 합치기 concat
train_gen_sca = pd.concat([train_gen_ob,train_gen_scaled])
train_unu_sca = pd.concat([train_unu_ob,train_unu_scaled])
test_gen_sca = pd.concat([test_gen_ob,test_gen_scaled])
test_unu_sca = pd.concat([test_unu_ob,test_unu_scaled])
#%%
train_gen_sca.to_csv('scaled_train_gen.csv')
train_unu_sca.to_csv('scaled_train_unu.csv')
test_gen_sca.to_csv('scaled_test_gen.csv')
test_unu_sca.to_csv('scaled_test_unu.csv')
#%%
# train, validation 나누기
train_gen_x = train_gen.drop('is_applied',axis=1)
train_gen_y = train_gen['is_applied']

x_train, x_val, y_train, y_val = train_test_split(train_gen_x,train_gen_y, test_size=0.4, random_state=777)

#%%
#수치형 변수만 남기기
#tr_gen_num = train_gen.copy().drop(['application_id', 'loanapply_insert_time', 'bank_id', 'product_id',
#       'user_id', 'birth_year','gender', 'insert_time','income_type',
#       'company_enter_month', 'employment_type', 'houseown_type',
#       'purpose', 'existing_loan_cnt','existing_loan_amt','month','Unnamed: 0'],axis=1)

tr_gen_num = train_gen.copy()[['loan_limit','loan_rate','birth_year','credit_score','yearly_income',
                               'month','desired_amount',
                               'existing_loan_cnt','existing_loan_amt']]

#다중공선성
tr_gen_num = tr_gen_num.dropna(axis=0)
vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(tr_gen_num.values, i) for i in range(tr_gen_num.shape[1])]
vif["features"] = tr_gen_num.columns
print(vif)
# 다중공선성 없음
#%%
logis = sm.Logit.from_formula('is_applied ~ existing_loan_amt', train_unu).fit()
print(logis.summary())
#%%
multi_num_logit = sm.Logit.from_formula('''is_applied ~ employment_type:income_type+ employment_type:houseown_type +employment_type:purpose+ employment_type:gender+ employment_type:bank_id+ employment_type:product_id
                                        +income_type:purpose +income_type:houseown_type +income_type:gender+ income_type:bank_id +income_type:product_id+ purpose:houseown_type+ pose:gender 
                                        +purpose:bank_id +purpose:product_id+ houseown_type:gender+ houseown_type:bank_id+ houseown_type:product_id +gender:bank_id+ gender:product_id+ bank_id:product_id
                                        +employment_type:income_type:houseown_type+ employment_type:income_type:purpose+ employment_type:income_type:houseown_type+ employment_type:income_type:gender
                                        +employment_type:income_type:bank_id+ employment_type:income_type:product_id+ income_type:purpose:houseown_type +income_type:purpose:gender
                                        +income_type:purpose:bank_id +income_type:purpose:product_id+ purpose:houseown_type:gender+ purpose:houseown_type:bank_id+ purpose:houseown_type:product_id
                                        +houseown_type:gender:bank_id+ houseown_type:gender:product_id+ gender:bank_id:product_id +employment_type:income_type:purpose:houseown_type
                                        +employment_type:income_type:purpose:gender +employment_type:income_type:purpose:bank_id +employment_type:income_type:purpose:product_id
                                        +income_type:purpose:houseown_type:gender+ income_type:purpose:houseown_type:bank_id +income_type:purpose:houseown_type:product_id
                                        +purpose:houseown_type:gender:bank_id+ purpose:houseown_type:gender:product_id +houseown_type:gender:bank_id:product_id
                                        +employment_type:income_type:purpose:houseown_type:gender+ employment_type:income_type:purpose:houseown_type:bank_id +employment_type:income_type:purpose:houseown_type:product_id
                                        +income_type:purpose:houseown_type:gender:bank_id +income_type:purpose:houseown_type:gender:product_id
                                        +purpose:houseown_type:gender:bank_id:product_id+ employment_type:income_type:purpose:houseown_type:gender:bank_id:product_id
                                        +income_type+ gender +income_type + purpose + houseown_type +existing_loan_cnt+  existing_loan_amt + loan_rate ;
''', data= train_gen).fit()
#%%
logis = sm.Logit.from_formula('is_applied ~ employment_type + birth_year + gender + insert_time + credit_score + yearly_income + company_enter_month + income_type + purpose + houseown_type + loan_limit + desired_amount + existing_loan_cnt + existing_loan_amt + loan_rate + product_id + bank_id + loanapply_insert_time', train_gen).fit()
#%%
print(logis.summary())
#%%
f, ax = plt.subplots(figsize=(16, 14))
ax.set_xscale("log")
ax = sns.boxplot(data = tr , orient="h", palette="Set1")

ax.xaxis.grid(False)

plt.xlabel("Numeric values", fontsize = 10)
plt.ylabel("Feature names", fontsize = 10)
plt.title("Numeric Distribution of Features", fontsize = 15)
sns.despine(trim = True, left = True)
#%%
print(multi_num_logit.summary())
print(multi_num_logit.aic)
#%%
tr_null = train_gen[train_gen.isnull().any()==False].copy()