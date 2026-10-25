import pandas as pd, numpy as np
d=pd.read_csv('../../data/1_gercek_veri/ideal/ideal_gunluk_csv.gz'); w=pd.read_csv('../../data/1_gercek_veri/ideal/hava.csv')
h=pd.read_csv('../../data/1_gercek_veri/ideal/metadata/home.csv'); rooms=pd.read_csv('../../data/1_gercek_veri/ideal/metadata/room.csv'); per=pd.read_csv('../../data/1_gercek_veri/ideal/metadata/person.csv')
d=d.merge(h[['homeid','location']],on='homeid').merge(w.rename(columns={'location':'location'}),on=['location','date'])
d['gas']=d.gas_sum/1000; d['tin']=d.temp_all_mean/10; d['tout']=d.tmean
d=d[(d.temp_n>0)]
d.loc[d.gas>300,'gas']=np.nan
d['gas']=d.gas.fillna(0).where(d.gas_n.ge(0))  # no pulses = 0 use
d['month']=d.date.str[:7]
res=[]
for hid,g in d.groupby('homeid'):
    m=g.groupby('month').agg(n=('gas','size'),gas=('gas','mean'),tout_list=('tout',list))
    m=m[m.n>=20]
    if len(m)<6: continue
    best=None
    for tb in np.arange(8,22.01,0.5):
        hdd=np.array([np.mean(np.maximum(tb-np.array(t),0)) for t in m.tout_list])
        if (hdd>0.5).sum()<3: continue
        b,a=np.polyfit(hdd,m.gas.values,1)
        pred=a+b*hdd; r2=1-((m.gas-pred)**2).sum()/((m.gas-m.gas.mean())**2).sum()
        if b>0 and a>=-2 and (best is None or r2>best[0]): best=(r2,tb,a,b)
    if best is None: continue
    cold=g[g.tout<8]; heat=g[g.tout<10]
    htc=np.nan
    if len(heat)>30:
        x=(heat.tin-heat.tout).values; ok=~np.isnan(x)
        if ok.sum()>30: htc=np.polyfit(x[ok],heat.gas.values[ok],1)[0]*1000/24
    res.append(dict(homeid=hid,months=len(m),r2=best[0],tb=best[1],base=best[2],slope=best[3]*1000/24,
        tin_cold=cold.tin.mean(),tin_living_cold=(cold.temp_living_mean/10).mean(),heat_hours=cold.chflow_hours_over400.mean(),
        htc=htc,annual_gas=g.gas.mean()*365,elec_kwh_day=(g.elec100_mean*24/1000).mean()))
r=pd.DataFrame(res)
area=rooms.groupby('homeid').floorarea.sum()/10
r=r.merge(h[['homeid','residents','hometype','build_era','occupied_days','entry_floor','income_band','equivalised_income']],on='homeid')
r['area']=r.homeid.map(area)
r.to_csv('prism.csv',index=False)
print('fitted homes',len(r),' median R2',r.r2.median().round(3), ' share R2>0.8', (r.r2>0.8).mean().round(2))
print(r[['tb','base','slope','htc','tin_cold','heat_hours','area']].describe().round(1))
