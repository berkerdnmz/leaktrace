import pandas as pd, numpy as np, json
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
X=pd.read_pickle('X.pkl'); g=pd.read_pickle('g2.pkl'); y=np.log(g.y)
feat=['type','age','area','epc','li','cwi','pv','elec']
X['type']=g.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5}).values
X['elec']=(X['elec']/100).round()  # hundreds of kWh
for ne,d,lr in [(60,4,0.15),(40,5,0.2)]:
    m=GradientBoostingRegressor(n_estimators=ne,max_depth=d,learning_rate=lr,subsample=0.8,random_state=0)
    p=cross_val_predict(m,X[feat],y,cv=KFold(5,shuffle=True,random_state=0))
    print(ne,d,'R2=%.3f'%(1-((y-p)**2).sum()/((y-y.mean())**2).sum()))
m=GradientBoostingRegressor(n_estimators=60,max_depth=4,learning_rate=0.15,subsample=0.8,random_state=0)
p=cross_val_predict(m,X[feat],y,cv=KFold(5,shuffle=True,random_state=0)); res=(y-p).values
m.fit(X[feat],y)
T=[]
for est in m.estimators_[:,0]:
    t=est.tree_
    T.append({'f':t.feature.tolist(),'t':[round(v,2) for v in t.threshold],'l':t.children_left.tolist(),'r':t.children_right.tolist(),'v':[round(v[0][0],4) for v in t.value]})
model={'features':feat,'encoding':{'type':'0 Mustakil,1 Ikiz,2 Sira-kose,3 Sira-orta,4 Tek katli mustakil,5 Daire','age':'1 <1930, 2 1930-1972, 3 1973-1999, 4 2000+','area':'1 <=50,2 51-100,3 101-150,4 151-200,5 >200 m2','epc':'0 EKB yok,1 A/B,2 C,3 D,4 E,5 F/G','li':'cati yalitimi 0/1','cwi':'duvar yalitimi 0/1','pv':'gunes paneli 0/1','elec':'yillik elektrik kWh/100, bilinmiyorsa -1'},
 'init':round(float(m.init_.constant_[0][0]),5),'lr':0.15,'trees':T,'residual_quantiles':[round(float(np.quantile(res,q)),3) for q in np.linspace(0,1,101)]}
def pred(x):
    s=model['init']
    for t in T:
        n=0
        while t['l'][n]!=-1: n=t['l'][n] if x[t['f'][n]]<=t['t'][n] else t['r'][n]
        s+=0.15*t['v'][n]
    return s
pp=np.array([pred(x) for x in X[feat].values[:2000]]); print('maxdiff',np.abs(pp-m.predict(X[feat][:2000])).max())
s=json.dumps(model,separators=(',',':'),ensure_ascii=False); print('bytes',len(s))
open('./dedektif_model.json','w').write(s)
g['X']=0
# demo homes with model
d=X[feat].copy(); d['y']=g.y.values; d['pred']=np.exp(p); d['pct']=pd.Series(res).rank(pct=True).values; d['EPC']=g.EPC.values
for cond in [(d.pct.between(.48,.52))&(d.type==1)&(d.age==2)&(d.area==2)&(d.elec>0),
             (d.pct>=.97)&(d.type==3)&(d.age==1)&(d.area==2)&(d.elec>0)&(d.cwi==0),
             (d.pct.between(.85,.9))&(d.type==5)&(d.age==2)&(d.elec>0)]:
    print(d[cond].iloc[0].to_dict())
