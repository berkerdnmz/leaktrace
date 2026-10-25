import pandas as pd, numpy as np, json
w=pd.read_csv('../data/1_gercek_veri/open-meteo-38_42N27_20E14m.csv',skiprows=3); w.columns=['date','tmean','tmin','tmax','rad']; w['m']=w.date.str[:7]
months=sorted(w.m.unique())
dt=[[round(x,1) for x in w[w.m==m].tmean] for m in months]
F=pd.read_csv('zaman_daireler.csv'); G=pd.read_csv('zaman_faturalar.csv.gz',index_col=0)[months]; E=pd.read_csv('zaman_elektrik.csv.gz',index_col=0)[months]
binfo=pd.read_csv('yesilova_binalar.csv').set_index('osm_id')
Bld=json.load(open('yesilova_binalar.geojson'))['features']
rd=lambda c:[[round(x,6),round(y,6)] for x,y in c]
res_ids=list(F.osm_id.unique()); idx={o:i for i,o in enumerate(res_ids)}
truth=F.groupby('osm_id').agg(era=('era','first'),m=('mantolu','first'),r=('retrofit','first'))
B=[];NR=[]
for f in Bld:
    p=f['properties']; oid=p['osm_id']; poly=rd(f['geometry']['coordinates'][0])
    if oid not in idx: NR.append(poly); continue
    b=binfo.loc[oid]; s=b.SOKAK_CADDE_KAPINO if isinstance(b.SOKAK_CADDE_KAPINO,str) else ''
    B.append(dict(id=oid,poly=poly,h=int(max(b.floors,1))*3,yr=int(b.year),yrr=int(b.year_src=='ruhsat'),fl=int(b.floors),st=str(b.BINA_TASIYICI_SISTEM).title(),nz=str(b.YAPI_NIZAMI_ADI),
        sok=s.split(' / ')[0].title(),no=s.split('NO:')[-1] if 'NO:' in s else '',c=[round(float(np.mean([q[0] for q in poly])),6),round(float(np.mean([q[1] for q in poly])),6)],
        t_ret=int(truth.loc[oid,'r']),t_mant=int(truth.loc[oid,'m']),era=truth.loc[oid,'era']))
order={b['id']:i for i,b in enumerate(B)}
F=F[F.osm_id.isin(order)].copy()
dates=pd.to_datetime(w.date); mon_of_day=np.array([months.index(m) for m in w.m])
def gl(v): return None if np.isnan(v).any() else [int(round(x)) for x in v]
code={'kombi':0,'klima':1,'soba':2,'merkezi':3}
f=dict(bi=[order[o] for o in F.osm_id],fl=F.floor.tolist(),top=F.top.tolist(),gr=F.ground.tolist(),sh=F.above_shop.tolist(),ext=F.ext_sides.round(1).tolist(),
       fpf=F.flats_per_floor.tolist(),end=F.end_unit.tolist(),ar=F.area.round(1).tolist(),per=F.persons.tolist(),
       mv=[int(mon_of_day[d]) if d>0 else -1 for d in F.move_day],th=[code[h] for h in F.heating],
       g=[gl(G.loc[i].values) for i in F.flat_id],e=[[int(round(x)) for x in E.loc[i].values] for i in F.flat_id],id=F.flat_id.tolist())
S=json.load(open('../data/1_gercek_veri/export_1.geojson'))['features']
streets=[rd(s['geometry']['coordinates']) for s in S if s['geometry']['type']=='LineString']
json.dump(dict(months=months,dt=dt,b=B,nr=NR,s=streets,f=f),open('live_data.json','w'),ensure_ascii=False,separators=(',',':'))
import os; print('bina',len(B),'daire',len(F),'MB',round(os.path.getsize('live_data.json')/1e6,2))
