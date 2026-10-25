import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_predict, StratifiedKFold
X=pd.read_pickle('X.pkl'); g=pd.read_pickle('g2.pkl')
X['type']=g.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5}).values
X['gas']=g.y.values
m=g.EPC!='No EPC'; lab=g.EPC[m].map({'A/B':0,'C':1,'D':2,'E':3,'F/G':4}).values
print('n with EPC',m.sum(), 'class dist',np.bincount(lab)/len(lab))
sets={'envanter (tip,donem,alan)':['type','age','area'],
'+yalitim,pv':['type','age','area','li','cwi','pv'],
'+faturalar (gaz,elektrik)':['type','age','area','li','cwi','pv','elec','gas']}
for k,c in sets.items():
    p=cross_val_predict(HistGradientBoostingClassifier(random_state=0),X.loc[m.values,c],lab,cv=StratifiedKFold(5,shuffle=True,random_state=0),method='predict_proba')
    pr=p.argmax(1); acc=(pr==lab).mean(); w1=(np.abs(pr-lab)<=1).mean()
    # identify poor (E,F/G) recall/precision
    poor=lab>=3; flag=p[:,3:].sum(1)>=0.3
    rec=(flag&poor).sum()/poor.sum(); prec=(flag&poor).sum()/flag.sum()
    print(f'{k}: dogruluk={acc:.3f} +-1sinif={w1:.3f} | E-F/G yakalama={rec:.2f} isabet={prec:.2f} (isaretlenen %{flag.mean()*100:.0f})')
print('baseline (hep en sik sinif):',np.bincount(lab).max()/len(lab))
print('E-F/G orani',(lab>=3).mean())
