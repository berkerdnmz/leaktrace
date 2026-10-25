const fs=require('fs');const D=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const A=require('./core.js')(D);
const q=v=>v==null?'':(typeof v==='string'&&v.includes(',')?`"${v}"`:v);
let rows=['osm_id,sokak,kapi_no,yapim_yili,yil_ruhsattan,kat,daire_sayisi,analiz_edilen_daire,verimlilik_skoru,guven,degisim_2023_yuzde,degisim_daire_sayisi,olasi_iyilestirme,daire_durumlari,SIM_GERCEK_donem,SIM_GERCEK_bastan_mantolu,SIM_GERCEK_mantolama_2023'];
D.b.forEach((b,k)=>{const o=A.out[k];rows.push([b.id,b.sok,b.no,b.yr,b.yrr,b.fl,o.fl.length,o.nb,o.s==null?null:100-o.s,o.conf,o.ch,o.chn,o.flag,Object.entries(o.heat).map(([a,c])=>a+':'+c).join('; '),b.era,b.t_mant,b.t_ret].map(q).join(','));});
fs.writeFileSync(process.argv[3]+'/bina_sonuclari.csv',rows.join('\n'));
const th=['kombi','klima','soba','merkezi'];let r2=['flat_id,osm_id,kat,alan_m2,kisi_ADNKS,tasinma_ayi,tahmin_isitma,SIM_GERCEK_isitma,tb_C,isitma_egimi_kWh_dg,baz_yuk_kWh_gun,r2,nac_2022_23,nac_2023_24,bina_ici_goreli_yuzdelik'];
const f=D.f;for(let i=0;i<f.bi.length;i++){const F1=A.fit1[i],F2=A.fit2[i];r2.push([f.id[i],D.b[f.bi[i]].id,f.fl[i],f.ar[i],f.per[i],f.mv[i]>=0?D.months[f.mv[i]]:'',A.cls[i],th[f.th[i]],F1?F1.tb:'',F1?F1.b.toFixed(3):'',F1?F1.a.toFixed(2):'',F1?F1.r2.toFixed(3):'',F1?Math.round(F1.nac):'',F2?Math.round(F2.nac):'',A.rel[i]==null?'':A.rel[i].toFixed(1)].join(','));}
fs.writeFileSync(process.argv[3]+'/daire_sonuclari.csv',r2.join('\n'));console.log(JSON.stringify(A.stats));
