import pandas as pd, numpy as np, json
g=pd.read_pickle('g.pkl'); seg=pd.read_pickle('seg.pkl')
seg=seg[seg.n>=30]
# fallback type x age
fb=g.groupby(['PROP_TYPE','PROP_AGE_BAND']).y.quantile([.1,.25,.5,.75,.9]).unstack()
# percentile within own segment for each home
key=['PROP_TYPE','PROP_AGE_BAND','FLOOR_AREA_BAND']
g['seg_pct']=g.groupby(key).y.rank(pct=True)
g['top10']=g.seg_pct>=0.9
print('Top10% by EPC share:'); print(g.groupby('EPC').top10.mean().round(3))
print('Top10% by CWI:'); print(g.groupby('CWI_FLAG').top10.mean().round(3))
print('Top10% by IMD:'); print(g.groupby('IMD_BAND_ENG').top10.mean().round(3))
# potential: if top quartile homes came down to segment median
m=g.merge(seg[key+['p50']],on=key)
exc=(m.y-m.p50).clip(lower=0)[m.seg_pct>=0.75]
print('top quartile excess over median, share of total gas: %.3f'%(exc.sum()/m.y.sum()))
print('median excess per top-quartile home kWh',exc.median())
out={'units':'kWh/yil, hava duzeltmeli dogalgaz (NEED 2023)',
 'age_bands':{1:'1930 oncesi',2:'1930-1972',3:'1973-1999',4:'2000 ve sonrasi'},
 'area_bands':{1:'50 m2 ve alti',2:'51-100 m2',3:'101-150 m2',4:'151-200 m2',5:'200 m2 ustu'},
 'segments':[{'type':r.PROP_TYPE,'age':int(r.PROP_AGE_BAND),'area':int(r.FLOOR_AREA_BAND),'n':int(r.n),
   'p10':int(r.p10),'p25':int(r.p25),'p50':int(r.p50),'p75':int(r.p75),'p90':int(r.p90)} for r in seg.itertuples()],
 'cwi_effect':{'treated_median_change':-0.187,'control_median_change':-0.081,'net_effect_pct_points':-10.6,'n_homes':2566,'note':'Dolgu duvar yalitimi (2007-2014), 2 yil once vs 2 yil sonra, yalitimsiz benzer evlerle karsilastirma'},
 'epc_median_kwh':g.groupby('EPC').y.median().astype(int).to_dict()}
json.dump(out,open('./dedektif_veri.json','w'),ensure_ascii=False)
print(len(out['segments']),'segments; json bytes',len(json.dumps(out)))
# demo homes
d=m.copy()
pick=[]
pick.append(d[(d.seg_pct.between(.45,.55))&(d.PROP_TYPE=='Semi detached')&(d.PROP_AGE_BAND==2)&(d.FLOOR_AREA_BAND==2)].iloc[0])
pick.append(d[(d.seg_pct>=.95)&(d.PROP_TYPE=='Mid terrace')&(d.PROP_AGE_BAND==1)&(d.FLOOR_AREA_BAND==2)&(d.CWI_FLAG==0)].iloc[0])
pick.append(d[(d.seg_pct.between(.85,.92))&(d.PROP_TYPE=='Flat')&(d.PROP_AGE_BAND==2)].iloc[0])
for p in pick: print(p[key+['EPC','CWI_FLAG','y','p50','seg_pct']].to_dict())
