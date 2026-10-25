import pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
df=pd.read_csv('../../data/1_gercek_veri/anon2025_50k.csv')
e=df[(df.ElecValFlag2023=='V')].copy()
e['type']=e.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5})
e['epc']=e.EPC.map({'No EPC':0,'A/B':1,'C':2,'D':3,'E':4,'F/G':5})
e['gasheat']=(e.MAIN_HEAT_FUEL==1).astype(int)
f=['type','PROP_AGE_BAND','FLOOR_AREA_BAND','epc','LI_FLAG','CWI_FLAG','PV_FLAG','gasheat']
y=np.log(e.Econs2023)
for name,sub in [('tum evler',e),('gazla isinan',e[e.gasheat==1]),('gazsiz (elektrikle isinma olasi)',e[e.gasheat==0])]:
    yy=np.log(sub.Econs2023); p=cross_val_predict(GradientBoostingRegressor(n_estimators=60,max_depth=4,learning_rate=0.15,random_state=0),sub[f],yy,cv=KFold(5,shuffle=True,random_state=0))
    print(name,len(sub),'R2=%.3f'%(1-((yy-p)**2).sum()/((yy-yy.mean())**2).sum()))
