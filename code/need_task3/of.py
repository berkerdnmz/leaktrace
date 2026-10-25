import pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold, GroupKFold
X=pd.read_pickle('X.pkl'); g=pd.read_pickle('g2.pkl'); y=np.log(g.y).values
X['type']=g.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5}).values
X['elec']=(X['elec']/100).round()
f=['type','age','area','epc','li','cwi','pv','elec']
def r2(p): return 1-((y-p)**2).sum()/((y-y.mean())**2).sum()
mk=lambda ne,d:GradientBoostingRegressor(n_estimators=ne,max_depth=d,learning_rate=0.15,subsample=0.8,random_state=0)
m=mk(60,4).fit(X[f],y); print('app modeli: egitim R2=%.3f'%r2(m.predict(X[f])))
print('app modeli: 5-kat CV R2=%.3f'%r2(cross_val_predict(mk(60,4),X[f],y,cv=KFold(5,shuffle=True,random_state=0))))
p=cross_val_predict(mk(60,4),X[f],y,cv=GroupKFold(10),groups=g.REGION.values); print('bolge disarida birakma R2=%.3f'%r2(p))
for reg in sorted(g.REGION.unique()):
    k=g.REGION.values==reg; print(reg, '%.3f'%(1-((y[k]-p[k])**2).sum()/((y[k]-y[k].mean())**2).sum()))
# deliberately overfit model for contrast
m2=GradientBoostingRegressor(n_estimators=800,max_depth=10,learning_rate=0.2,random_state=0)
m2.fit(X[f],y); print('asiri karmasik: egitim R2=%.3f'%r2(m2.predict(X[f])))
print('asiri karmasik: CV R2=%.3f'%r2(cross_val_predict(m2,X[f],y,cv=KFold(5,shuffle=True,random_state=0))))
