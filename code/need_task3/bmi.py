import pandas as pd, numpy as np
g=pd.read_pickle('g2.pkl'); X=pd.read_pickle('X.pkl')
mid={1:40,2:75,3:125,4:175,5:250}
g['idx']=g.y/g.FLOOR_AREA_BAND.map(mid)
y=np.log(g.y)
# simple model R2: log gas ~ log area mid
a=np.log(g.FLOOR_AREA_BAND.map(mid)); b=np.polyfit(a,y,1); p=np.polyval(b,a)
print('basit endeks R2=%.3f'%(1-((y-p)**2).sum()/((y-y.mean())**2).sum()))
g['p_idx']=g.idx.rank(pct=True)
g['p_ml']=pd.Series(g.res.values).rank(pct=True).values  # from 17-feature cv model
t1=g.p_idx>=.9; t2=g.p_ml>=.9
print('ust %10 ortaklik:', (t1&t2).sum()/t2.sum())
# examples where differ
d=g[(t2)&(g.p_idx<.6)]
print(len(d)); print(d[['PROP_TYPE','PROP_AGE_BAND','FLOOR_AREA_BAND','y','elec','p_idx','p_ml']].head(5))
d2=g[(t1)&(g.p_ml<.5)]
print(len(d2)); print(d2[['PROP_TYPE','PROP_AGE_BAND','FLOOR_AREA_BAND','y','elec','p_idx','p_ml']].head(5))
