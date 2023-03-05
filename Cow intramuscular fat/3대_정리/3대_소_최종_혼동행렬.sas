/* 3대 소 단변량 */
/* 소 3대 처리 */ 

/* import full */
filename a 'C:\Users\Owner\Desktop\윤태준\소\3차 요청자료\소_3대 정리\등급추가_full_cp.csv' encoding='cp949';
proc import datafile= a
dbms=csv
out = cow_3_full
replace;
getnames=yes;
run;

proc print data= cow_3_full (obs=);
run;

proc contents data= cow_3_full;
run;

/* import train */
filename a 'C:\Users\Owner\Desktop\윤태준\소\3차 요청자료\소_3대 정리\등급추가_train_cp.csv' encoding='cp949';
proc import datafile= a
dbms=csv
out = cow_3_train
replace;
getnames=yes;
run;
proc print data= cow_3_train (obs=50);
run;

/* import test */
filename a 'C:\Users\Owner\Desktop\윤태준\소\3차 요청자료\소_3대 정리\등급추가_test_cp.csv' encoding='cp949';
proc import datafile= a
dbms=csv
out = cow_3_val
replace;
getnames=yes;
run;
proc print data= cow_3_val (obs=5);
run;

/* Baseline Characterics */

/*full set */
title1 'full_Data, Baseline characteristics';
proc means data=cow_3_full n nmiss min max mean std maxdec=1;
var s_w sl_m s_m_w s_m_i s_t_m a_s_m_w a_s_t_m b_s_m_w b_s_t_m;
run;

proc freq data= cow_3_full;
tables gender farm_level target/ nocum;
run;

/* train set*/
title1 'Train_Data, Baseline characteristics';
proc means data=cow_3_train n nmiss min max mean std maxdec=1;
var s_w sl_m s_m_w s_m_i s_t_m a_s_m_w a_s_t_m b_s_m_w b_s_t_m;
run;

proc freq data= cow_3_train;
tables gender farm_level target/ nocum;
run;

/* validation set*/
title1 'Validation_Data, Baseline characteristics';
proc means data=cow_3_val n nmiss min max mean std maxdec=1;
var s_w sl_m s_m_w s_m_i s_t_m a_s_m_w a_s_t_m b_s_m_w b_s_t_m;
run;

proc freq data= cow_3_val;
tables gender farm_level target/ nocum;
run;


/*3대 Uni&Multi */
title1 'Uni&Multi, train에서 validation바로 적용, target:1{7,8,9}';
ods graphics on;
proc logistic data=cow_3_train;
class farm_level(ref='A') / param=ref;
model target(event='1') = s_w sl_m s_m_w s_m_i s_t_m a_s_m_w a_s_t_m b_s_m_w 
b_s_t_m farm_level/ outroc=troc;
score data=cow_3_val out=valpred outroc=vroc;
roc; roccontrast;
run;

proc print data=valpred (obs=10);
run;

/* Cut-off: */
data valpred;
set valpred;
if P_1 = . then expected5 = .; 
if P_1 >= 0.5 then expected5 = 1; else expected5 = 0;

if P_1 = . then expected6 = .; 
if P_1 >= 0.6 then expected6 = 1; else expected6 = 0;

if P_1 = . then expected7 = .; 
if P_1 >= 0.7 then expected7 = 1; else expected7 = 0;

if P_1 = . then expected8 = .; 
if P_1 >= 0.8 then expected8 = 1; else expected8 = 0;

if P_1 = . then expected9 = .; 
if P_1 >= 0.9 then expected9 = 1; else expected9 = 0;
run;

proc freq data= valpred;
tables F_target*expected/nocol norow nopercent;
run;

/* Cut-off: 0.6 */
data valpred_6;
set valpred;
if P_1 = . then expected = .;
if P_1 >= 0.6 then expected = 1; else expected = 0;
run;

proc freq data= valpred_6;
tables F_target*expected/nocol norow nopercent;
run;

/* Cut-off: 0.7 */
data valpred_7;
set valpred;
if P_1 = . then expected = .;
if P_1 >= 0.7 then expected = 1; else expected = 0;
run;

proc freq data= valpred_7;
tables F_target*expected/senspec nocol norow nopercent;
run;

/* Cut-off: 0.8 */
data valpred;
set valpred;
if P_1 = . then expected = .;
if P_1 >= 0.8 then expected = 1; else expected = 0;
run;

proc freq data= valpred;
tables F_target*expected/senspec nocol norow nopercent;
run;

/* Cut-off: 0.9 */
data valpred;
set valpred;
if P_1 = . then expected = .;
if P_1 >= 0.9 then expected = 1; else expected = 0;
run;

proc freq data= valpred;
tables F_target*expected/ nocol norow nopercent;
run;

/* macro */
%macro diag(gs, var, data) ;
proc sort data = &DATA ; by descending &GS; run;
proc freq data = &data order=data; table &var * &gs / out=table0 ; run ;

* 0,1 coding, 1,2 coding에 따라 바꿔줌;
data table ;
	set table0 ;
	if &var   = 0 and &gs  = 0 then class = 'TN' ;
	else if &var   = 0 and &gs  = 1 then class = 'FN' ;
	else if &var   = 1 and &gs  = 0 then class = 'FP' ;
	else if &var   = 1 and &gs  = 1 then class = 'TP' ;
run ;

proc transpose data = table out = report0 ;
	var count ;
	id class;
run ;

data report ;
	set report0 ;
	if TP = . then TP = 0 ;
	if TN = . then TN = 0 ;
	if FP = . then FP = 0 ;
	if FN = . then FN = 0 ;
N=sum(TP,TN,FP,FN) ;

Sensitivity=(TP/(TP+FN))*100;
Sensitivity_l=(Sensitivity/100-1.96*sqrt( (Sensitivity/100)*(1-(Sensitivity/100))/(TP+FN) ) )*100;
Sensitivity_u=(Sensitivity/100+1.96*sqrt( (Sensitivity/100)*(1-(Sensitivity/100))/(TP+FN) ) )*100;

Specificity=(1-FP/(TN+FP))*100;
Specificity_l=(Specificity/100-1.96*sqrt( (Specificity/100)*(1-(Specificity/100))/(FP+TN) ) )*100;
Specificity_u=(Specificity/100+1.96*sqrt( (Specificity/100)*(1-(Specificity/100))/(FP+TN) ) )*100;

Accuracy=((TP+TN)/(TP+TN+FP+FN))*100;
Accuracy_l=(Accuracy/100-1.96*sqrt( (Accuracy/100)*(1-(Accuracy/100))/N ) )*100;
Accuracy_u=(Accuracy/100+1.96*sqrt( (Accuracy/100)*(1-(Accuracy/100))/N ) )*100;

PPV= (TP/(TP+FP))*100 ;
PPV_l=(PPV/100-1.96*sqrt( (PPV/100)*(1-(PPV/100))/(TP+FP) ) )*100;
PPV_u=(PPV/100+1.96*sqrt( (PPV/100)*(1-(PPV/100))/(TP+FP) ) )*100;

NPV= (TN/(TN+FN))*100 ;
NPV_l=(NPV/100-1.96*sqrt( (NPV/100)*(1-(NPV/100))/(TN+FN) ) )*100;
NPV_u=(NPV/100+1.96*sqrt( (NPV/100)*(1-(NPV/100))/(TN+FN) ) )*100;
run ;

proc print data = report ;
	var TP TN FP FN Sensitivity Sensitivity_l Sensitivity_u Specificity Specificity_l Specificity_u 
			accuracy accuracy_l accuracy_u PPV PPV_l PPV_u NPV NPV_l NPV_u ;
run ;
%mend ;



title1 'cut-off 0.5';
%diag(F_target, expected5, valpred);

title1 'cut-off 0.6';
%diag(F_target, expected6, valpred);

title1 'cut-off 0.7';
%diag(F_target, expected7, valpred);

title1 'cut-off 0.8';
%diag(F_target, expected8, valpred);

title1 'cut-off 0.9';
%diag(F_target, expected9, valpred);
