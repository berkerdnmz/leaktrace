import json, re, numpy as np, pandas as pd
from scipy.optimize import linear_sum_assignment
rng=np.random.default_rng(42)
LAT0=np.radians(38.436)
def xy(c): c=np.asarray(c); return np.c_[c[:,0]*111320*np.cos(LAT0), c[:,1]*110540]
def norm(x):
    x=str(x).upper().replace('İ','I').replace('Ş','S').replace('Ğ','G').replace('Ü','U').replace('Ö','O').replace('Ç','C').replace('.','')
    x=re.sub(r'\bSK\b|\bSOK\b','SOKAK',x); x=re.sub(r'\bCAD\b|\bCD\b|\bBULVARI\b','CADDESI',x)
    return re.sub(r'\s+',' ',x).strip()
# buildings
G=json.load(open('../data/1_gercek_veri/export.geojson'))['features']
B=[]
for f in G:
    if 'building' not in f['properties'] or f['geometry']['type']!='Polygon': continue
    p=xy(f['geometry']['coordinates'][0]); x,y=p[:,0],p[:,1]
    a=0.5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
    if a<30: continue
    B.append(dict(osm_id=f['properties']['@id'],area=a,cx=x.mean(),cy=y.mean(),geom=f['geometry'],btype=f['properties'].get('building')))
B=pd.DataFrame(B); print('OSM bina (>=30m2):',len(B))
# streets -> segments
S=json.load(open('../data/1_gercek_veri/export_1.geojson'))['features']
segs=[]
for f in S:
    p=xy(f['geometry']['coordinates']); n=norm(f['properties'].get('name'))
    for i in range(len(p)-1): segs.append((p[i,0],p[i,1],p[i+1,0],p[i+1,1],n))
sg=pd.DataFrame(segs,columns=['x1','y1','x2','y2','name'])
P=B[['cx','cy']].values; A=sg[['x1','y1']].values; Bv=sg[['x2','y2']].values; AB=Bv-A
best=np.full(len(P),np.inf); bname=np.empty(len(P),object)
for j in range(len(sg)):
    ap=P-A[j]; t=np.clip((ap@AB[j])/max(AB[j]@AB[j],1e-9),0,1); dist=np.linalg.norm(ap-np.outer(t,AB[j]),axis=1)
    m=dist<best; best[m]=dist[m]; bname[m]=sg.name.iloc[j]
B['street']=bname; B['street_dist']=best
# inventory
d=pd.read_csv('../data/1_gercek_veri/bornova_yapi_envanter.csv',dtype=str)
R=d[d.IL_ILCE_MAHALLE.str.contains('YEŞİLOVA',na=False)].copy().reset_index(drop=True)
R['street']=R.SOKAK_CADDE_KAPINO.str.split(' / ').str[0].map(norm)
R['zarea']=pd.to_numeric(R.ZEMIN_KAT_INSAAT_ALANI.str.extract(r'([\d.]+)')[0],errors='coerce')
R['year']=pd.to_numeric(R.RUHSAT_TARIHI.str[:4],errors='coerce')
R['floors']=pd.to_numeric(R.SERBEST_KAT_ADEDI,errors='coerce')
# eksik yapim yili: makine ogrenmesi modeli (impute.py, Bornova geneli egitildi)
YM=pd.read_csv('yil_tahmin.csv',dtype={'BINA_KIMLIK_NO':str}).set_index('BINA_KIMLIK_NO').year_model
R['year_src']=np.where(R.year.notna(),'ruhsat','model')
R['year']=R.year.fillna(R.BINA_KIMLIK_NO.map(YM))
def cost(ra,ba):
    ra=np.where(np.isnan(ra),np.nanmedian(R.zarea),ra)
    return np.abs(np.log(ra[:,None])-np.log(ba[None,:]))
R['osm_id']=None; R['match']=None
osm_streets=set(B.street)
for s,rs in R[R.street.isin(osm_streets)].groupby('street'):
    bs=B[(B.street==s)&(~B.osm_id.isin(R.osm_id.dropna()))]
    if len(bs)==0: continue
    c=cost(rs.zarea.values,bs.area.values); ri,ci=linear_sum_assignment(c)
    R.loc[rs.index[ri],'osm_id']=bs.osm_id.values[ci]; R.loc[rs.index[ri],'match']='sokak+alan'
# leftovers: area only
rl=R[R.osm_id.isna()]; bl=B[~B.osm_id.isin(R.osm_id.dropna())]
c=cost(rl.zarea.values,bl.area.values); ri,ci=linear_sum_assignment(c)
R.loc[rl.index[ri],'osm_id']=bl.osm_id.values[ci]; R.loc[rl.index[ri],'match']='sadece alan'
print(R.match.value_counts(dropna=False).to_dict())
M=B.merge(R[['osm_id','BINA_KIMLIK_NO','SOKAK_CADDE_KAPINO','year','year_src','floors','BINA_TASIYICI_SISTEM','YAPI_NIZAMI_ADI','ZEMIN_KAT','UST_KAT','BODRUM_KAT_ADEDI','zarea','match','street']].rename(columns={'street':'inv_street'}),on='osm_id',how='left')
print('envanter kaydi alan OSM bina:',M.BINA_KIMLIK_NO.notna().sum(),'/',len(M))
ok=M.zarea.notna()&M.BINA_KIMLIK_NO.notna()
print('alan uyumu (eslesen, alani olan): log fark ortanca %.2f, %%20 icinde %%%.0f'%(np.median(np.abs(np.log(M.zarea[ok]/M.area[ok]))),(np.abs(M.zarea[ok]/M.area[ok]-1)<0.2).mean()*100))
M.drop(columns=['geom']).to_csv('yesilova_binalar.csv',index=False)
json.dump({'type':'FeatureCollection','features':[{'type':'Feature','geometry':r.geom,'properties':{k:(None if (isinstance(v,float) and np.isnan(v)) else v) for k,v in r.drop('geom').items()}} for _,r in M.iterrows()]},open('yesilova_binalar.geojson','w'),ensure_ascii=False,default=str)
