import pandas as pd, numpy as np
import os
rng=np.random.default_rng(21); R=2.2; HK=1.5; MN=float(os.environ.get('MN','0.35'))
ln=lambda sd,n=None: rng.lognormal(-0.5*sd*sd,sd,n)
w=pd.read_csv('../data/1_gercek_veri/open-meteo-38_42N27_20E14m.csv',skiprows=3); w.columns=['date','tmean','tmin','tmax','rad']
dates=pd.to_datetime(w.date); T=w.tmean.values; RAD=w.rad.values*1e6/86400; days=len(T)
F=pd.read_csv('yesilova_haneler.csv')
bld=F.groupby('osm_id').agg(year=('year','first')).reset_index()
bld['era']=np.where(bld.year<2000,'pre2000',np.where(bld.year<2009,'ts825','bep'))
bld['mantolu']=((bld.era=='pre2000')&(rng.random(len(bld))<0.25)).astype(int)
# OLAY 1: 2023 eylulunde mantolama (eski, mantolusuz binalarin %10'u)
cand=bld[(bld.era=='pre2000')&(bld.mantolu==0)].index
bld['retrofit']=0; bld.loc[rng.choice(cand,int(.10*len(cand)),replace=False),'retrofit']=1
F=F.merge(bld[['osm_id','era','mantolu','retrofit']],on='osm_id')
U={'pre2000':dict(wall=1.6,win=3.0,roof=2.0,floor=1.0,ach=1.1),'ts825':dict(wall=0.9,win=2.8,roof=0.6,floor=0.6,ach=0.75),'bep':dict(wall=0.6,win=2.4,roof=0.45,floor=0.45,ach=0.6)}
F['orient']=rng.choice([1.0,0.6,0.6,0.25],len(F)); F['shade']=rng.uniform(0.5,1.0,len(F))
F['boiler_eff']=np.where(rng.random(len(F))<0.3,rng.uniform(0.75,0.82,len(F)),rng.uniform(0.86,0.92,len(F)))
F['single_glz']=((F.era=='pre2000')&(rng.random(len(F))<0.3)).astype(int)
F['leak_b']=ln(0.25*R,len(F))            # binaya ait sizdirmazlik (sabit)
HHcols=['persona','persons','day_home','heat_hours','setpoint','hot_water_l_day','energy_poor']
def hh_hidden(n): return dict(heated_frac=np.clip(1-R*rng.uniform(0,0.5,n),0.4,1),vent=ln(0.25*R,n),gain_mult=ln(0.4*R,n),dhw_mult=ln(0.5*R,n))
for k,v in hh_hidden(len(F)).items(): F[k]=v
# OLAY 2: 2023 mayis-eylul arasi tasinma (dolu dairelerin %15'i)
occ=F.index[F.persons>0]; movers=rng.choice(occ,int(.15*len(occ)),replace=False)
F['move_day']=-1; md=rng.integers((dates>='2023-05-01').argmax(),(dates>='2023-09-30').argmax(),len(movers)); F.loc[movers,'move_day']=md
donor=rng.choice(occ,len(movers)); NEW=F.loc[donor,HHcols].reset_index(drop=True)
for k,v in hh_hidden(len(movers)).items(): NEW[k]=v
NEW.index=movers
h=2.7
def H_of(r,mant,heated_frac,vent):
    u=U[r.era]; uw=0.6 if mant else u['wall']
    af=r.area/0.85; L=r.ext_sides*np.sqrt(af); wall=L*h; win=0.2*wall; wall-=win
    Hc=uw*wall+(5.0 if r.single_glz else u['win'])*win
    if r.top: Hc+=0.6*u['roof']*af
    if r.ground: Hc+=0.5*u['floor']*af
    if r.above_shop: Hc+=0.3*u['floor']*af
    Hv=0.34*u['ach']*r.leak_b*vent*r.area*h
    return HK*(Hc+Hv)*heated_frac, win
F['Teff_set']=np.where(F.persons>0,F.setpoint,14.0); g=F.groupby('osm_id').Teff_set
F['T_neigh']=((g.transform('sum')-F.Teff_set)/(g.transform('count')-1).replace(0,np.nan)).fillna(F.Teff_set)
n_int=((1-F.top)+(1-F.ground)).values
ret_day=(dates>='2023-09-01').argmax()
gas=np.full((len(F),days),np.nan); elec=np.zeros((len(F),days))
has_ac=(F.heating=='klima')|(rng.random(len(F))<0.5)
def hh_series(hh,n):
    sp=hh['setpoint']+np.repeat(rng.normal(0,0.7*R*MN,n//30+2),30)[:n]
    hrs=np.clip(hh['heat_hours']*ln(0.25*R*MN,n//30+2).repeat(30)[:n],2,22)
    return sp,hrs
for i,r in enumerate(F.itertuples()):
    segs=[(0,days,{c:getattr(r,c) for c in HHcols+['heated_frac','vent','gain_mult','dhw_mult']})]
    if r.move_day>0:
        segs=[(0,r.move_day,segs[0][2]),(r.move_day,days,NEW.loc[r.Index].to_dict())]
    out=np.zeros(days); eout=np.zeros(days)
    for a,b,hh in segs:
        n=b-a; t=T[a:b]
        if hh['persons']==0: out[a:b]=rng.uniform(0,0.3,n); eout[a:b]=rng.uniform(0.3,1.0,n); continue
        sp,hrs=hh_series(hh,n); f_int=0.55+0.45*hrs/24
        mant_t=np.where(np.arange(a,b)>=ret_day, r.mantolu or r.retrofit, r.mantolu)
        H0,win=H_of(r,r.mantolu,hh['heated_frac'],hh['vent']); H1,_=H_of(r,1,hh['heated_frac'],hh['vent'])
        Ht=np.where(mant_t==1,H1,H0)
        Tin=np.where(t<sp,t+(sp-t)*f_int,t)
        gains=hh['gain_mult']*(80*hh['persons']*(0.5+0.5*hh['day_home'])+3*r.area)+win*0.6*RAD[a:b]*r.orient*r.shade*0.35
        loss=Ht*np.maximum(Tin-t,0)+1.2*(r.area/0.85)*n_int[i]*(sp-r.T_neigh)*f_int*(t<16)
        q=np.where(t>17,0,np.maximum(loss-gains,0)*24/1000)
        dhw=hh['hot_water_l_day']*0.0407*hh['dhw_mult']*ln(0.15*R,n); cook=(0.6+0.15*hh['persons'])*ln(0.4*R)
        base_e=(1600+600*hh['persons'])/365*ln(0.25*R)
        cool=(Ht*np.maximum(t-26,0)*np.clip(hrs,0,12)/1000/3.0) if has_ac.iloc[i] else 0
        if r.heating=='kombi': out[a:b]=(q+dhw)/r.boiler_eff+cook; eout[a:b]=base_e+cool
        elif r.heating=='klima': out[a:b]=dhw/r.boiler_eff+cook; eout[a:b]=base_e+q/2.8+cool
        else: out[a:b]=np.nan; eout[a:b]=base_e+cool
    gas[i]=out; elec[i]=eout
mon=dates.dt.to_period('M').astype(str).values; ms=pd.unique(mon)
G=pd.DataFrame({m:np.nansum(gas[:,mon==m],1)*ln(float(os.environ.get('BN','0.2')),len(F)) for m in ms},index=F.flat_id)
G[F.set_index('flat_id').heating.isin(['soba','merkezi']).values]=np.nan
E=pd.DataFrame({m:elec[:,mon==m].sum(1)*ln(0.08,len(F)) for m in ms},index=F.flat_id); E.to_csv('zaman_elektrik.csv.gz')
G.to_csv('zaman_faturalar.csv.gz'); F.to_csv('zaman_daireler.csv',index=False)
NEW.assign(flat_id=F.loc[movers,'flat_id'].values).to_csv('zaman_yeni_haneler.csv',index=False)
print('mantolanan bina',bld.retrofit.sum(),' tasinan daire',len(movers),' yillik ort. gaz (2022, kombi dolu) %.0f m3'%(G.loc[F[(F.heating=="kombi")&(F.persons>0)].flat_id,[m for m in ms if m.startswith('2022')]].sum(1).mean()/10.64))
