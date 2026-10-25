import pandas as pd, numpy as np, json
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
df=pd.read_csv('../../data/1_gercek_veri/anon2025_50k.csv')
g=df[(df.MAIN_HEAT_FUEL==1)&(df.GasValFlag2023=='V')].copy()
g['y']=g.Gcons2023
print('gas valid 2023 n=',len(g))
# EPC vs consumption
print(g.groupby('EPC').y.median())
print(g.groupby('PROP_AGE_BAND').y.median())
# segment table
seg=g.groupby(['PROP_TYPE','PROP_AGE_BAND','FLOOR_AREA_BAND']).y.agg(n='count',p10=lambda s:s.quantile(.1),p25=lambda s:s.quantile(.25),p50='median',p75=lambda s:s.quantile(.75),p90=lambda s:s.quantile(.9)).reset_index()
print('segments',len(seg),'with n>=30',(seg.n>=30).sum(), 'covering', seg[seg.n>=30].n.sum())
# models
def cv(cols):
    X=g[cols].copy()
    cat=[]
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c]=X[c].astype('category').cat.codes; cat.append(True)
        else: cat.append(False)
    m=HistGradientBoostingRegressor(categorical_features=cat,random_state=0)
    p=cross_val_predict(m,X,np.log(g.y),cv=KFold(5,shuffle=True,random_state=0))
    r=np.log(g.y)-p
    ss=1-((r)**2).sum()/((np.log(g.y)-np.log(g.y).mean())**2).sum()
    mape=np.median(np.abs(np.exp(p)-g.y)/g.y)
    return ss,mape,p
base=['PROP_TYPE','PROP_AGE_BAND','FLOOR_AREA_BAND']
full=base+['CONSERVATORY_FLAG','COUNCIL_TAX_BAND','REGION','EPC','LI_FLAG','CWI_FLAG','IMD_BAND_ENG']
for name,cols in [('base',base),('full',full)]:
    ss,mape,p=cv(cols); print(name,'R2(log)=%.3f medAPE=%.3f'%(ss,mape))
    if name=='full': g['pred']=np.exp(p)
g['ratio']=g.y/g.pred
print(g.ratio.describe(percentiles=[.1,.25,.5,.75,.9]))
g.to_pickle('g.pkl'); seg.to_pickle('seg.pkl')
