import pandas as pd, numpy as np
rng=np.random.default_rng(7)
F=pd.read_csv('yesilova_daireler.csv')
P={ # pay, kisi, gunduz_evde, isitma_saat(ort), termostat(ort), kiraci_olasiligi, ses agirliklari (dusuk,orta,yuksek)
 'bos':                (10,[0],0,0,0,0,(0,1,0)),
 'yalniz_emekli':      (10,[1],1,13,21.0,.25,(.45,.45,.10)),
 'yalniz_calisan':     (6,[1],0,6,20.0,.60,(.25,.55,.20)),
 'emekli_cift':        (15,[2],1,14,21.0,.20,(.35,.50,.15)),
 'calisan_cift':       (10,[2],0,7,20.5,.45,(.20,.55,.25)),
 'cocuklu_biri_evde':  (21,[3,4],1,12,21.0,.40,(.35,.50,.15)),
 'cocuklu_ikisi_calisan':(17,[3,4],0,8,20.5,.40,(.20,.55,.25)),
 'genis_aile':         (9,[5,6],1,13,21.0,.35,(.55,.40,.05)),
 'ogrenci':            (2,[2,3],0,8,20.0,1.0,(.40,.55,.05)),
}
names=list(P); w=np.array([P[n][0] for n in names],float); w/=w.sum()
F=F.sample(frac=1,random_state=1).reset_index(drop=True)
pers=rng.choice(names,len(F),p=w)
# kucuk dairelere genis aile koyma, ogrenciyi buyuk daireye koyma: takas
big=F.area>=90
for bad,need in [('genis_aile',True),('ogrenci',False)]:
    idx=np.where((pers==bad)&(big.values!=need))[0]
    pool=np.where((big.values==need)&np.isin(pers,['cocuklu_biri_evde','cocuklu_ikisi_calisan','calisan_cift']))[0]
    sw=rng.choice(pool,len(idx),replace=False); pers[idx],pers[sw]=pers[sw],pers[idx]
F['persona']=pers
H=[]
for r in F.itertuples():
    p=P[r.persona]
    n=int(rng.choice(p[1])); ses=rng.choice(['dusuk','orta','yuksek'],p=p[6]) if n else ''
    renter=int(rng.random()<p[5]) if n else 0
    hours=float(np.clip(rng.normal(p[3],2),3,20)) if n else 0
    tset=float(np.clip(rng.normal(p[4],1.0),17,25)) if n else 0
    poor = n>0 and ses=='dusuk' and rng.random()<0.35
    if poor: tset=float(rng.uniform(15.5,17.5)); hours=hours*0.7
    over65 = n if r.persona in ('yalniz_emekli','emekli_cift') else (int(rng.random()<.5) if r.persona=='genis_aile' else 0)
    H.append(dict(flat_id=r.flat_id,persona=r.persona,persons=n,over65=over65,day_home=p[2],heat_hours=round(hours,1),
                  setpoint=round(tset,1),ses=ses,renter=renter,energy_poor=int(poor),
                  hot_water_l_day=round(n*rng.normal(45,10),0) if n else 0))
H=pd.DataFrame(H); F=F.merge(H,on=['flat_id','persona'])
# isitma sistemi
bld=F.groupby('osm_id').agg(nf=('n_floors','first'),nflats=('flat_id','size'),year=('year','first'),st=('structure','first'))
central=bld.index[(bld.nf>=8)&(bld.nflats>=12)]
cent_extra=bld.index[(bld.year>=2000)&(bld.nflats>=10)&~bld.index.isin(central)]
cent=set(central)|set(rng.choice(cent_extra,min(len(cent_extra),max(0,int(.07*len(F)/ max(bld.nflats.mean(),1))-len(central))),replace=False))
def heat(r):
    if r.osm_id in cent: return 'merkezi'
    if r.persons==0: return 'kombi'
    ps=0.03+0.12*(r.structure=='YIGMA')+0.08*(r.year<1980)+0.10*(r.ses=='dusuk')
    pa=0.05+0.06*(r.area<70)+0.04*r.renter
    u=rng.random(); return 'soba' if u<ps else 'klima' if u<ps+pa else 'kombi'
F['heating']=F.apply(heat,axis=1)
F.to_csv('yesilova_haneler.csv',index=False)
occ=F[F.persons>0]
print('daire',len(F),' dolu',len(occ),' ortalama hane %.2f'%occ.persons.mean(),' tek kisilik %%%.0f'%((occ.persons==1).mean()*100),' 65+ kisi payi %%%.0f'%(occ.over65.sum()/occ.persons.sum()*100))
print('kiraci %%%.0f'%(occ.renter.mean()*100),' enerji yoksulu %%%.1f'%(occ.energy_poor.mean()*100),' nufus',occ.persons.sum())
print('isitma:',(F.heating.value_counts(normalize=True)*100).round(1).to_dict())
print(occ.persona.value_counts().to_dict())
