import pandas as pd, numpy as np, json
exec(open('detect_time.py').read().split("# --- A)")[0])   # P1,P2,D hazir
F=pd.read_csv('zaman_daireler.csv').set_index('flat_id')
Bld=json.load(open('yesilova_binalar.geojson'))['features']
binfo=pd.read_csv('yesilova_binalar.csv').set_index('osm_id')
# durgun skor (S1 NAC, konum duzeltmeli)
A=D[(D.persons>0)&D.slope1.gt(0)].copy(); A['ly']=np.log(A.slope1/A.area)
X=np.c_[np.ones(len(A)),A.top,A.ground,A.above_shop,A.ext_sides,np.log(A.area)]
A['res']=A.ly-X@np.linalg.lstsq(X,A.ly,rcond=None)[0]
bs=A.groupby('osm_id').res.median(); bpct=bs.rank(pct=True)*100
A['rel']=(A.res-A.osm_id.map(bs)); A['rel_pct']=A.rel.rank(pct=True)*100
A[['osm_id','floor','top','ground','above_shop','area','persona','persons','heating','slope1','slope2','dlog','rel_pct','move_day']].rename(columns={'slope1':'nac_2022_23_kwh','slope2':'nac_2023_24_kwh','dlog':'log_degisim','rel_pct':'bina_ici_goreli_yuzdelik'}).to_csv('daire_sonuclari.csv')
nonmv=A[A.move_day<0]; ch=nonmv.groupby('osm_id').dlog.median(); chn=nonmv.groupby('osm_id').size()
nb=A.groupby('osm_id').size()
allf=F.groupby('osm_id').size(); heat=F.groupby('osm_id').heating.agg(lambda s:s.value_counts().to_dict())
out=[]
def rd(c): return [[round(x,6),round(y,6)] for x,y in c]
for f in Bld:
    p=f['properties']; oid=p['osm_id']
    if oid not in allf.index: 
        out.append(dict(id=oid,poly=rd(f['geometry']['coordinates'][0]),h=3,res=0)); continue
    b=binfo.loc[oid]; n=int(nb.get(oid,0))
    yr_real=b.year_src=='ruhsat'
    conf=None
    if n>0:
        lvl=2 if n>=6 else 1 if n>=3 else 0
        if not yr_real: lvl=max(lvl-1,0)
        conf=['Düşük','Orta','Yüksek'][lvl]
    c=ch.get(oid,np.nan); cn=int(chn.get(oid,0)); cpct=None if np.isnan(c) else round((np.exp(c)-1)*100)
    flag= cpct is not None and cn>=2 and cpct<=-20
    flats=[]
    for fid,r in F[F.osm_id==oid].sort_values(['floor']).iterrows():
        a=A.loc[fid] if fid in A.index else None
        pos=('en üst kat' if r.top else 'zemin kat' if r.ground else 'ara kat')+(', köşe' if r.end_unit and r.flats_per_floor>1 else '')+(', dükkân üstü' if r.above_shop else '')
        st='bos' if r.persons==0 else ('analiz' if a is not None else r.heating)
        flats.append(dict(fl=int(r.floor),pos=pos,st=st,rel=None if a is None else round(float(a.rel_pct)),
            mv=None if (a is None or r.move_day<0) else round((np.exp(a.dlog)-1)*100),area=round(r.area)))
    out.append(dict(id=oid,poly=rd(f['geometry']['coordinates'][0]),h=int(max(b.floors,1))*3,res=1,
        s=None if n==0 else round(float(bpct[oid])),conf=conf,yr=int(b.year),yrr=int(yr_real),ysrc=str(b.year_src),fl=int(b.floors),
        st=str(b.BINA_TASIYICI_SISTEM).title(),nz=str(b.YAPI_NIZAMI_ADI),sok=str(b.SOKAK_CADDE_KAPINO).split(' / ')[0].title() if isinstance(b.SOKAK_CADDE_KAPINO,str) else '',no=(str(b.SOKAK_CADDE_KAPINO).split('NO:')[-1] if isinstance(b.SOKAK_CADDE_KAPINO,str) and 'NO:' in str(b.SOKAK_CADDE_KAPINO) else ''),c=[round(float(np.mean([p[0] for p in f['geometry']['coordinates'][0]])),6),round(float(np.mean([p[1] for p in f['geometry']['coordinates'][0]])),6)],
        nf=int(allf[oid]),nb=n,heat=heat[oid],ch=cpct,chn=cn,flag=int(flag),
        t_ret=int(F[F.osm_id==oid].retrofit.iloc[0]),t_mant=int(F[F.osm_id==oid].mantolu.iloc[0]),era=F[F.osm_id==oid].era.iloc[0],flats=flats))
S=json.load(open('../data/1_gercek_veri/export_1.geojson'))['features']
streets=[dict(n=s['properties'].get('name'),p=rd(s['geometry']['coordinates'])) for s in S if s['geometry']['type']=='LineString']
res=[o for o in out if o['res']]
stats=dict(nb=len(res),nf=int(sum(o['nf'] for o in res)),analiz=int(sum(o['nb'] for o in res)),flag=int(sum(o['flag'] for o in res)),
           flag_true=int(sum(o['flag'] and o['t_ret'] for o in res)),ret_total=int(sum(o['t_ret'] for o in res)))
json.dump(dict(b=out,s=streets,stats=stats),open('map_data.json','w'),ensure_ascii=False,separators=(',',':'))
import os; print(stats, 'MB',round(os.path.getsize('map_data.json')/1e6,2))
