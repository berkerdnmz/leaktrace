# IDEAL gercek ev verisiyle yontem dogrulamasi. Once prism_ve_gercek_degerler.py calistirilir (prism.csv uretir).
import pandas as pd, numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_predict, KFold
r=pd.read_csv('prism.csv'); r=r[(r.htc>0)&(r.r2>0.5)].copy()
r['slope_m2']=r.slope/r.area; r['htc_m2']=r.htc/r.area; r['gas_m2']=r.annual_gas/r.area
sp=lambda a,b: stats.spearmanr(r[a],r[b],nan_policy='omit')[0]
print('ev sayisi',len(r))
print('isitma egimi vs olculen isi kaybi rho=%.2f (m2 basina %.2f)'%(sp('slope','htc'),sp('slope_m2','htc_m2')))
true=r.htc_m2>=r.htc_m2.quantile(.75)
for m in ['slope_m2','gas_m2']:
    f=r[m]>=r[m].quantile(.75); print('en kotu ceyrek yakalama (%s): %%%.0f'%(m,(f&true).sum()/true.sum()*100))
print('denge sicakligi vs olculen ic sicaklik rho=%.2f'%sp('tb','tin_cold'))
print('baz yuk vs kisi rho=%.2f | elektrik vs kisi rho=%.2f'%(sp('base','residents'),sp('elec_kwh_day','residents')))
q=r.dropna(subset=['tin_cold','elec_kwh_day']).copy(); q['flat']=(q.hometype=='flat').astype(int); q['ls']=np.log(q.slope_m2)
p=cross_val_predict(LinearRegression(),q[['tb','ls','base','area','flat','residents','elec_kwh_day','occupied_days']],q.tin_cold,cv=KFold(5,shuffle=True,random_state=0))
print('faturadan ic sicaklik tahmini CV R2=%.2f, hata %.2f C (ortalama tahmin %.2f C)'%(1-((q.tin_cold-p)**2).sum()/((q.tin_cold-q.tin_cold.mean())**2).sum(),np.abs(q.tin_cold-p).mean(),np.abs(q.tin_cold-q.tin_cold.mean()).mean()))
s=pd.read_csv('../../data/1_gercek_veri/ideal/surveys/survey_responses.csv',low_memory=False)
m=r.merge(s[['homeid','extra_clothes_need_2g_end']].dropna(),on='homeid')
print(m.groupby('extra_clothes_need_2g_end').tin_cold.median().round(1).to_dict())
