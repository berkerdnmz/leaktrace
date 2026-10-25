import json, numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
D=json.load(open('../live_data.json'))
S=pd.read_csv('../../4_model_ciktilari/bina_sonuclari.csv')
B=D['b']; n=len(B); f=D['f']
assert list(S.osm_id)==[b['id'] for b in B]
LAT0=np.radians(38.436)
def area(poly):
    p=np.array(poly); x=p[:,0]*111320*np.cos(LAT0); y=p[:,1]*110540
    return 0.5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
ST={'Betonarme':0,'Yigma':1,'Yığma':1}; NZ={'Ayrık':0,'Köşe Bitişik':1,'Orta Bitişim':2}
nf=np.bincount(f['bi'],minlength=n); shop=np.bincount(f['bi'],weights=f['sh'],minlength=n)>0
X=pd.DataFrame({'yil':[b['yr'] for b in B],'kat':[b['fl'] for b in B],'daire':nf,'alan':[area(b['poly']) for b in B],
  'tasiyici':[0 if b['st'].lower().startswith('beton') else 1 for b in B],'nizam':[NZ.get(b['nz'],1) for b in B],'dukkan':shop.astype(int)})
y=S.verimlilik_skoru.values.astype(float); has=~np.isnan(y)
xy=np.c_[[b['c'][0]*111320*np.cos(LAT0) for b in B],[b['c'][1]*110540 for b in B]]
K=8
def neigh_mean(mask_src, target_idx, yv):
    src=np.where(mask_src)[0]; out=np.full(len(target_idx),np.nan)
    for j,i in enumerate(target_idx):
        d=np.hypot(*(xy[src]-xy[i]).T); d[src==i]=np.inf; nn=src[np.argsort(d)[:K]]; out[j]=yv[nn].mean()
    return out
kf=KFold(5,shuffle=True,random_state=0); idx=np.where(has)[0]
pred=np.full(n,np.nan); predN=np.full(n,np.nan)
params=dict(n_estimators=150,max_depth=3,learning_rate=0.05,subsample=0.8,random_state=0)
for tr,te in kf.split(idx):
    tr,te=idx[tr],idx[te]; m_src=np.zeros(n,bool); m_src[tr]=True
    Xtr=X.iloc[tr].copy(); Xtr['komsu']=neigh_mean(m_src,tr,y)
    Xte=X.iloc[te].copy(); Xte['komsu']=neigh_mean(m_src,te,y)
    m=GradientBoostingRegressor(**params).fit(Xtr,y[tr]); pred[te]=m.predict(Xte); predN[te]=Xte.komsu.values
r2=lambda p:1-np.nansum((y[has]-p[has])**2)/np.sum((y[has]-y[has].mean())**2)
mae=lambda p:np.nanmean(np.abs(y[has]-p[has]))
print('CV: model R2 %.3f MAE %.1f | sadece komsu ortalamasi R2 %.3f MAE %.1f | herkese ortalama MAE %.1f'%(r2(pred),mae(pred),r2(predN),mae(predN),np.mean(np.abs(y[has]-y[has].mean()))))
# tutarsizlik: gercek - tahmin
res=y-pred; sd=np.nanstd(res[has]); thr=1.5*sd
tm=np.array([b['t_mant'] for b in B]); era=np.array([b['era'] for b in B])
pre=has&(era=='pre2000')
print('artik sd %.1f esik %.1f'%(sd,thr))
print('2000 oncesi binalarda gizli mantolamayi bulma AUC: ham skor %.2f | artik (beklenenden iyi) %.2f'%(roc_auc_score(tm[pre],y[pre]),roc_auc_score(tm[pre],res[pre])))
iyi=pre&(res>thr); kotu=has&(res<-thr)
print('beklenenden iyi (2000 oncesi):',iyi.sum(),' icinde gercekten mantolu %%%.0f (taban %%%.0f)'%(tm[iyi].mean()*100,tm[pre].mean()*100))
print('beklenenden kotu:',kotu.sum())
# son model: tum veri
m_src=has.copy(); Xall=X.copy(); Xall['komsu']=neigh_mean(m_src,np.arange(n),y)
m=GradientBoostingRegressor(**params).fit(Xall[has],y[has])
T=[]
for est in m.estimators_[:,0]:
    t=est.tree_; T.append({'f':t.feature.tolist(),'t':[round(v,4) for v in t.threshold],'l':t.children_left.tolist(),'r':t.children_right.tolist(),'v':[round(v[0][0],4) for v in t.value]})
model={'features':list(Xall.columns),'init':float(m.init_.constant_[0][0]),'lr':params['learning_rate'],'trees':T,'K':K,'res_sd':round(float(sd),2),
  'cv':{'r2':round(float(r2(pred)),3),'mae':round(float(mae(pred)),1),'r2_komsu':round(float(r2(predN)),3),'mae_ort':round(float(np.mean(np.abs(y[has]-y[has].mean()))),1)},
  'imp':dict(zip(Xall.columns,np.round(m.feature_importances_,3).tolist()))}
json.dump(model,open('fill_model.json','w'),separators=(',',':'))
print('onem',model['imp']); import os; print('KB',os.path.getsize('fill_model.json')//1024)
