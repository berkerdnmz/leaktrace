import pandas as pd, numpy as np
df=pd.read_csv('../../data/1_gercek_veri/anon2025_50k.csv')
df=df[df.MAIN_HEAT_FUEL==1]
def gas(r,y):
    if r.get(f'GasValFlag{y}')!='V': return np.nan
    return r[f'Gcons{y}']
res=[]
for Y in range(2007,2015):
    pre=[Y-2,Y-1]; post=[Y+1,Y+2]
    def chg(sub):
        a=sub[[f'Gcons{y}' for y in pre]].where(sub[[f'GasValFlag{y}' for y in pre]].values=='V').mean(axis=1)
        b=sub[[f'Gcons{y}' for y in post]].where(sub[[f'GasValFlag{y}' for y in post]].values=='V').mean(axis=1)
        ok=a.notna()&b.notna()
        return a[ok],b[ok]
    t=df[(df.CWI_FLAG==1)&(df.CWI_DATE==Y)&(df.LI_DATE!=Y)]
    c=df[(df.CWI_FLAG==0)&(df.LI_FLAG==0)&(df.PROP_AGE_BAND.isin([2,3]))]
    ta,tb=chg(t); ca,cb=chg(c)
    # match by prop type weights: use per-home % change medians
    tch=((tb-ta)/ta); cch=((cb-ca)/ca)
    res.append((Y,len(tch),tch.median(),cch.median(),ta.median()))
r=pd.DataFrame(res,columns=['year','n_treated','treated_med_change','control_med_change','pre_median_kwh'])
print(r.round(3))
w=r.n_treated
print('weighted treated',np.average(r.treated_med_change,weights=w),'control',np.average(r.control_med_change,weights=w),'n',w.sum())
# age band of CWI homes
print(df[df.CWI_FLAG==1].PROP_AGE_BAND.value_counts())
