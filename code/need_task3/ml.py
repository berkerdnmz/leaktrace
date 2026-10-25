import pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
g=pd.read_pickle('g.pkl')
g['elec']=np.where(g.ElecValFlag2023=='V',g.Econs2023,np.nan)
maps={'PROP_TYPE':{'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5},
'EPC':{'A/B':1,'C':2,'D':3,'E':4,'F/G':5,'No EPC':0},
'COUNCIL_TAX_BAND':{k:i for i,k in enumerate('ABCDEFGHI')}}
X=pd.DataFrame()
X['type']=g.PROP_TYPE.map(maps['PROP_TYPE'])
for t in range(6): X[f'type_{t}']=(X.type==t).astype(int)
X['age']=g.PROP_AGE_BAND; X['area']=g.FLOOR_AREA_BAND
X['conserv']=g.CONSERVATORY_FLAG.fillna(-1)
X['ctax']=g.COUNCIL_TAX_BAND.map(maps['COUNCIL_TAX_BAND'])
X['epc']=g.EPC.map(maps['EPC'])
X['li']=g.LI_FLAG; X['cwi']=g.CWI_FLAG; X['pv']=g.PV_FLAG
X['imd']=g.IMD_BAND_ENG.fillna(g.IMD_BAND_WALES).fillna(-1)
regs=sorted(g.REGION.unique()); X['region']=g.REGION.map({r:i for i,r in enumerate(regs)})
X['elec']=g.elec.fillna(-1)
X=X.drop(columns='type')
y=np.log(g.y)
sets={'bina3':['age','area']+[f'type_{t}' for t in range(6)],
 'bina_tum':['age','area','conserv','ctax','epc','li','cwi','pv']+[f'type_{t}' for t in range(6)],
 'bina_tum+bolge+imd':['age','area','conserv','ctax','epc','li','cwi','pv','imd','region']+[f'type_{t}' for t in range(6)],
 'hepsi+elektrik':list(X.columns)}
kf=KFold(5,shuffle=True,random_state=0)
for k,c in sets.items():
    m=GradientBoostingRegressor(n_estimators=200,max_depth=4,learning_rate=0.08,subsample=0.8,random_state=0)
    p=cross_val_predict(m,X[c],y,cv=kf)
    r2=1-((y-p)**2).sum()/((y-y.mean())**2).sum()
    print(k,len(c),'R2=%.3f'%r2,'medAPE=%.3f'%np.median(np.abs(np.exp(p)-g.y)/g.y))
    if k=='hepsi+elektrik': g['pred']=np.exp(p); g['res']=y-p
X.to_pickle('X.pkl'); g.to_pickle('g2.pkl')
