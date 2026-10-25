import pandas as pd, numpy as np, json
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
g=pd.read_pickle('g2.pkl'); X=pd.read_pickle('X.pkl'); y=np.log(g.y).values
X['type']=g.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5}).values
X['elec']=(X['elec']/100).round()
print('median gas by LI flag:',g.groupby('LI_FLAG').y.median().to_dict(),' by CWI:',g.groupby('CWI_FLAG').y.median().to_dict())
model=json.load(open('./dedektif_model.json'))
def contrib(x):
    c=np.zeros(8)
    for t in model['trees']:
        n=0
        while t['l'][n]!=-1:
            ch=t['l'][n] if x[t['f'][n]]<=t['t'][n] else t['r'][n]; c[t['f'][n]]+=0.15*(t['v'][ch]-t['v'][n]); n=ch
    return c
f=model['features']; xs=X[f].values[:3000]
C=np.array([contrib(x) for x in xs])
for k,i in [('li',4),('cwi',5)]:
    for val in [0,1]:
        m=xs[:,i]==val; print(k,val,'mean contrib %',round((np.exp(C[m,i].mean())-1)*100,1))
kf=KFold(5,shuffle=True,random_state=0)
for feats in [f,['type','age','area','epc','elec']]:
    p=cross_val_predict(GradientBoostingRegressor(n_estimators=60,max_depth=4,learning_rate=0.15,subsample=0.8,random_state=0),X[feats],y,cv=kf)
    print(len(feats),'R2=%.3f'%(1-((y-p)**2).sum()/((y-y.mean())**2).sum()))
