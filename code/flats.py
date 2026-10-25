import pandas as pd, numpy as np
B=pd.read_csv('yesilova_binalar.csv')
rows=[]; skipped=collections=0
exp_sides={'Ayrık':4,'Köşe Bitişik':3,'Orta Bitişim':2}
for b in B.itertuples():
    if b.UST_KAT in ('Ticari','Metruk') and b.ZEMIN_KAT!='Konut': continue
    nf=int(b.floors) if pd.notna(b.floors) and b.floors>0 else 1
    fpf=1 if b.area<140 else 2 if b.area<260 else 3
    start=1 if (b.ZEMIN_KAT=='Ticari' and nf>1) else 0
    if b.ZEMIN_KAT=='Ticari' and nf==1: continue
    sides=exp_sides.get(b.YAPI_NIZAMI_ADI,3)
    for fl in range(start,nf):
        for k in range(fpf):
            end_unit = fpf==1 or k in (0,fpf-1)
            # exposed facades of this flat: share building facades; end units keep side walls
            ext = sides if fpf==1 else (sides/2+ (0.5 if end_unit else 0))
            rows.append(dict(flat_id=f"{b.osm_id.split('/')[1]}-{fl}-{k}",osm_id=b.osm_id,bina_kimlik=b.BINA_KIMLIK_NO,
                floor=fl,n_floors=nf,top=int(fl==nf-1),ground=int(fl==0),above_shop=int(start==1 and fl==1),
                flats_per_floor=fpf,end_unit=int(end_unit),ext_sides=round(ext,1),
                area=round(b.area*0.85/fpf,1),year=int(b.year),year_src=b.year_src,structure=b.BINA_TASIYICI_SISTEM,
                nizam=b.YAPI_NIZAMI_ADI,cx=b.cx,cy=b.cy))
F=pd.DataFrame(rows); F.to_csv('yesilova_daireler.csv',index=False)
print('daire',len(F),' bina',F.osm_id.nunique(),' bina basina ortanca',F.groupby('osm_id').size().median(),' ortalama %.1f'%F.groupby('osm_id').size().mean())
print('daire alani ortanca',F.area.median(), ' en ust kat %',round(F.top.mean()*100), ' zemin %',round(F.ground.mean()*100),' dukkan ustu %',round(F.above_shop.mean()*100))
print('bina basina daire dagilimi', F.groupby('osm_id').size().describe(percentiles=[.25,.5,.75,.9]).round(1).to_dict())
