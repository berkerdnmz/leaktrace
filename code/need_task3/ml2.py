import pandas as pd, numpy as np, json
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
X=pd.read_pickle('X.pkl'); g=pd.read_pickle('g2.pkl'); y=np.log(g.y)
feat=[f'type_{t}' for t in range(6)]+['age','area','epc','li','cwi','pv','elec']
for ne,d in [(150,4),(300,3)]:
    m=GradientBoostingRegressor(n_estimators=ne,max_depth=d,learning_rate=0.08,subsample=0.8,random_state=0)
    p=cross_val_predict(m,X[feat],y,cv=KFold(5,shuffle=True,random_state=0))
    r2=1-((y-p)**2).sum()/((y-y.mean())**2).sum(); print(ne,d,'R2=%.3f'%r2)
m=GradientBoostingRegressor(n_estimators=150,max_depth=4,learning_rate=0.08,subsample=0.8,random_state=0)
p=cross_val_predict(m,X[feat],y,cv=KFold(5,shuffle=True,random_state=0))
res=y-p
qs=[round(float(np.quantile(res,q)),4) for q in np.linspace(0,1,101)]
m.fit(X[feat],y)
trees=[]
for est in m.estimators_[:,0]:
    t=est.tree_
    trees.append([t.feature.tolist(),[round(v,3) for v in t.threshold.tolist()],t.children_left.tolist(),t.children_right.tolist(),[round(v[0][0],5) for v in t.value.tolist()]])
model={'features':feat,'init':float(m.init_.constant_[0][0]) if hasattr(m.init_,'constant_') else float(np.mean(y)),'lr':m.learning_rate,'trees':trees,'residual_quantiles':qs}
# verify JS-style predict
def pred(x):
    s=model['init']
    for f,th,l,r,v in trees:
        n=0
        while l[n]!=-1:
            n = l[n] if x[f[n]]<=th[n] else r[n]
        s+=model['lr']*v[n]
    return s
xs=X[feat].values[:5]; print([round(pred(x),4) for x in xs], np.round(m.predict(X[feat][:5]),4))
s=json.dumps(model,separators=(',',':')); print('bytes',len(s))
json.dump(model,open('model.json','w'),separators=(',',':'))
# importance
print(sorted(zip(m.feature_importances_.round(3),feat),reverse=True))
# EPC check top10 residual
g['pct']=pd.Series(res).rank(pct=True).values
print(g.assign(top=g.pct>=.9).groupby('EPC').top.mean().round(3))
