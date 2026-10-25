import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold
d=pd.read_csv('../data/1_gercek_veri/bornova_yapi_envanter.csv',dtype=str)
d['MAH']=d.IL_ILCE_MAHALLE.str.split(' / ').str[-1]; d['SOK']=d.MAH+'|'+d.SOKAK_CADDE_KAPINO.str.split(' / ').str[0]
d['year']=pd.to_numeric(d.RUHSAT_TARIHI.str[:4],errors='coerce')
num=lambda c: pd.to_numeric(d[c].astype(str).str.extract(r'([\d.]+)')[0],errors='coerce')
X=pd.DataFrame({'kat':num('SERBEST_KAT_ADEDI'),'bodrum':num('BODRUM_KAT_ADEDI'),'normal':num('NORMAL_KAT_ADEDI'),'alan':num('ZEMIN_KAT_INSAAT_ALANI')})
for c in ['BINA_TASIYICI_SISTEM','YAPI_NIZAMI_ADI','ZEMIN_KAT','UST_KAT','BINA_KULLANIM_SINIFI']:
    X[c]=d[c].astype('category').cat.codes
lab=d.year.notna().values; y=d.year.values
kf=KFold(5,shuffle=True,random_state=0); idx=np.where(lab)[0]
pm=np.full(len(d),np.nan); pb_s=np.full(len(d),np.nan); pb_m=np.full(len(d),np.nan)
for tr,te in kf.split(idx):
    tr,te=idx[tr],idx[te]
    t=pd.DataFrame({'y':y[tr],'MAH':d.MAH.values[tr],'SOK':d.SOK.values[tr]})
    mm=t.groupby('MAH').y.median(); sm=t.groupby('SOK').y.agg(['median','size'])
    Xf=X.copy(); Xf['mah_med']=d.MAH.map(mm).values; Xf['sok_med']=d.SOK.map(sm['median']).values; Xf['sok_n']=d.SOK.map(sm['size']).fillna(0).values
    m=HistGradientBoostingRegressor(max_iter=300,learning_rate=0.06,random_state=0).fit(Xf.iloc[tr],y[tr])
    pm[te]=m.predict(Xf.iloc[te])
    pb_s[te]=np.where(~np.isnan(Xf.sok_med.values[te]),Xf.sok_med.values[te],Xf.mah_med.values[te])
    pb_m[te]=Xf.mah_med.values[te]
era=lambda v: np.where(v<2000,0,np.where(v<2009,1,2))
L=lab
for name,p in [('model',pm),('sokak ortancasi',pb_s),('mahalle ortancasi',pb_m)]:
    ok=L&~np.isnan(p); e=np.abs(p[ok]-y[ok])
    print(f'{name:18s} ort. hata {e.mean():.1f} yil | 5 yil icinde %{(e<=5).mean()*100:.0f} | TS825 donemi dogru %{(era(p[ok])==era(y[ok])).mean()*100:.0f}')
# son model: tum etiketli veriyle egit, eksikleri tahmin et
t=pd.DataFrame({'y':y[lab],'MAH':d.MAH.values[lab],'SOK':d.SOK.values[lab]})
mm=t.groupby('MAH').y.median(); sm=t.groupby('SOK').y.agg(['median','size'])
X['mah_med']=d.MAH.map(mm).values; X['sok_med']=d.SOK.map(sm['median']).values; X['sok_n']=d.SOK.map(sm['size']).fillna(0).values
m=HistGradientBoostingRegressor(max_iter=300,learning_rate=0.06,random_state=0).fit(X[lab],y[lab])
d['year_model']=np.round(m.predict(X)).astype(int)
d[['BINA_KIMLIK_NO','year','year_model']].to_csv('yil_tahmin.csv',index=False)
print('Bornova eksik yil:',(~lab).sum(),' Yesilova eksik:',(~lab&d.MAH.str.contains('YEŞİLOVA').values).sum())
