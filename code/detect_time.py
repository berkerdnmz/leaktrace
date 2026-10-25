import pandas as pd, numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score
w=pd.read_csv('../data/1_gercek_veri/open-meteo-38_42N27_20E14m.csv',skiprows=3); w.columns=['date','tmean','tmin','tmax','rad']; w['m']=w.date.str[:7]
G=pd.read_csv('zaman_faturalar.csv.gz',index_col=0); F=pd.read_csv('zaman_daireler.csv').set_index('flat_id'); NEW=pd.read_csv('zaman_yeni_haneler.csv').set_index('flat_id')
S1=[m for m in G.columns if '2022-07'<=m<='2023-06']; S2=[m for m in G.columns if '2023-07'<=m<='2024-06']
nd=w.groupby('m').size()
def prism(cols):
    Y=G[cols].values/nd[cols].values; best=None
    for tb in np.arange(10,20.01,0.5):
        hdd=w.assign(h=np.maximum(tb-w.tmean,0)).groupby('m').h.mean()[cols].values
        X=np.c_[np.ones(len(cols)),hdd]; beta=np.linalg.lstsq(X,np.nan_to_num(Y.T),rcond=None)[0]
        r2=1-((Y-(X@beta).T)**2).sum(1)/((Y-Y.mean(1,keepdims=True))**2).sum(1)
        hn=np.maximum(tb-w.tmean,0).sum()/3  # normal yil isitma derece-gunu (3 yil ortalamasi)
        nac=beta[1]*hn
        if best is None: best=[r2,beta[1].copy(),beta[0].copy(),nac.copy()]
        else:
            m=(r2>best[0])&(beta[1]>0); best[0]=np.where(m,r2,best[0]); best[1]=np.where(m,beta[1],best[1]); best[2]=np.where(m,beta[0],best[2]); best[3]=np.where(m,nac,best[3])
    return pd.DataFrame({'slope':best[3],'base':best[2],'r2':best[0]},index=G.index)
P1,P2=prism(S1),prism(S2)
D=F.join(P1.add_suffix('1')).join(P2.add_suffix('2'))
D=D[(D.heating=='kombi')&D.slope1.gt(0)&D.slope2.gt(0)]
occ_both=(D.persons>0)
D['dlog']=np.log(D.slope2/D.slope1)
# --- A) MANTOLAMA TESPITI: tasinmayan, dolu dairelerin bina medyan degisimi
st=D[occ_both&(D.move_day<0)]
bb=st.groupby('osm_id').agg(d=('dlog','median'),n=('dlog','size'),retro=('retrofit','first'),era=('era','first'),mant=('mantolu','first'))
c=bb[(bb.era=='pre2000')&(bb.mant==0)]
print('A) MANTOLAMA TESPITI (eski, mantolusuz binalar, n=%d, mantolanan %d)'%(len(c),c.retro.sum()))
print('   AUC tum binalar: %.2f'%roc_auc_score(c.retro,-c.d))
for lo,hi in [(1,2),(3,5),(6,999)]:
    s=c[(c.n>=lo)&(c.n<=hi)]
    if s.retro.nunique()>1: print('   %s daireli (n=%d): AUC %.2f'%(f'{lo}-{hi}' if hi<999 else f'{lo}+',len(s),roc_auc_score(s.retro,-s.d)))
print('   mantolanan binalarda tuketim degisimi ortanca %%%.0f, digerlerinde %%%.0f'%((np.exp(c[c.retro==1].d.median())-1)*100,(np.exp(c[c.retro==0].d.median())-1)*100))
thr=c.d.quantile(c.retro.mean()); fl=c.d<=thr
print('   en cok dusen binalari isaretleyince: yakalama %%%.0f, isabet %%%.0f'%((fl&(c.retro==1)).sum()/c.retro.sum()*100,(fl&(c.retro==1)).sum()/fl.sum()*100))
# --- B) TASINMA: ayni dairede hane degisince tuketim degisimi davranisi gosteriyor mu
mv=D[D.move_day>0].join(NEW,rsuffix='_new')
mv=mv[(mv.persons>0)&(mv.persons_new>0)]
z=lambda a,b,mu,sd:(a-b)/sd
sdS,sdH=F.setpoint[F.persons>0].std(),F.heat_hours[F.persons>0].std()
beh_old=(mv.setpoint-17)*(0.55+0.45*mv.heat_hours/24)*mv.heated_frac*mv.vent
beh_new=(mv.setpoint_new-17)*(0.55+0.45*mv.heat_hours_new/24)*mv.heated_frac_new*mv.vent_new
mv['dbeh']=np.log(np.clip(beh_new,0.1,None)/np.clip(beh_old,0.1,None))
nm=D[occ_both&(D.move_day<0)&(D.retrofit==0)]
print('\nB) TASINMA (n=%d daire)'%len(mv))
print('   tuketim egimi degisimi vs gercek davranis degisimi rho=%.2f'%stats.spearmanr(mv.dlog,mv.dbeh)[0])
print('   tasinmayan dairelerde yil-yil degisim sapmasi %.2f, tasinanlarda %.2f'%(nm.dlog.std(),mv.dlog.std()))
big=mv.dbeh.abs()>=mv.dbeh.abs().quantile(.5)
print('   buyuk davranis degisimlerinde yon dogru tahmin: %%%.0f'%((np.sign(mv.dlog[big])==np.sign(mv.dbeh[big])).mean()*100))
# davranis payi tahmini: tasinan dairelerde hane etkisi = dlog; kalan bina etkisi
print('   tasinmayla aciklanan tuketim degisimi (R2): %.2f'%(stats.pearsonr(mv.dlog,mv.dbeh)[0]**2))
print('\nKALIBRASYON: sezonluk PRISM R2 ortanca S1 %.2f S2 %.2f (IDEAL gercek: 0.90)'%(D.r21.median(),D.r22.median()))
# adil karsilastirma: ayni NAC ile durgun bina skoru (S1), mevcut mantolu binalari bulma
s1=D[occ_both&(D.move_day<0)].copy(); s1['ly']=np.log(s1.slope1/s1.area)
X=np.c_[np.ones(len(s1)),s1.top,s1.ground,s1.above_shop,s1.ext_sides,np.log(s1.area)]
s1['res']=s1.ly-X@np.linalg.lstsq(X,s1.ly,rcond=None)[0]
b=s1.groupby('osm_id').agg(sc=('res','median'),era=('era','first'),m=('mantolu','first'),n=('res','size'))
p=b[b.era=='pre2000']
print('DURGUN (NAC ile) mantolu bina tespiti AUC %.2f | 6+ daireli %.2f'%(roc_auc_score(1-p.m,p.sc),roc_auc_score(1-p[p.n>=6].m,p[p.n>=6].sc)))
