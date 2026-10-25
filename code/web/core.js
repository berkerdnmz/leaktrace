// LeakTrace canli analiz cekirdegi: ham aylik faturalar + gunluk sicaklik -> bina skorlari
function analyzeLT(D){
  const t0=(typeof performance!=='undefined'?performance.now():Date.now());
  const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
  const median=a=>{const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;};
  const M=D.months.length, nd=D.dt.map(a=>a.length);
  const TB=[];for(let t=10;t<=20.0001;t+=0.5)TB.push(Math.round(t*10)/10);
  const HDD=TB.map(tb=>D.dt.map(a=>a.reduce((s,x)=>s+Math.max(tb-x,0),0)/a.length));
  const allT=D.dt.flat(), HN=TB.map(tb=>allT.reduce((s,x)=>s+Math.max(tb-x,0),0)/3);
  const S1=[],S2=[],WIN=[],SUM=[],SHO=[];
  D.months.forEach((m,i)=>{if(m>='2022-07'&&m<='2023-06')S1.push(i);if(m>='2023-07'&&m<='2024-06')S2.push(i);
    const k=+m.slice(5,7);if([12,1,2].includes(k))WIN.push(i);else if([6,7,8,9].includes(k))SUM.push(i);else if([4,5,10,11].includes(k))SHO.push(i);});
  function prism(g,idx){
    const y=idx.map(i=>g[i]/nd[i]),ym=mean(y);let best=null;
    for(let k=0;k<TB.length;k++){
      const x=idx.map(i=>HDD[k][i]),xm=mean(x);let sxx=0,sxy=0;
      for(let j=0;j<x.length;j++){sxx+=(x[j]-xm)**2;sxy+=(x[j]-xm)*(y[j]-ym);}
      if(sxx<1e-9)continue;const b=sxy/sxx,a=ym-b*xm;let ss=0,st=0;
      for(let j=0;j<x.length;j++){ss+=(y[j]-a-b*x[j])**2;st+=(y[j]-ym)**2;}
      const r2=st>0?1-ss/st:0;
      if(b>0&&(!best||r2>best.r2))best={tb:TB[k],k,a,b,r2};
    }
    if(best)best.nac=best.b*HN[best.k];
    return best;
  }
  const f=D.f,n=f.bi.length,nb=D.b.length;
  const cls=new Array(n),fit1=new Array(n),fit2=new Array(n),res=new Array(n).fill(null),rel=new Array(n).fill(null),dl=new Array(n).fill(null);
  for(let i=0;i<n;i++){
    const g=f.g[i],e=f.e[i];
    if(f.per[i]===0){cls[i]='bos';continue;}
    if(!g){cls[i]='gazsiz';continue;}
    const gw=mean(WIN.map(j=>g[j]/nd[j])),gs=mean(SUM.map(j=>g[j]/nd[j])),ew=mean(WIN.map(j=>e[j]/nd[j])),eh=mean(SHO.map(j=>e[j]/nd[j]));
    if(gw/Math.max(gs,0.1)>=1.3)cls[i]='kombi';else if(ew/Math.max(eh,0.1)>=1.25)cls[i]='klima';else cls[i]='belirsiz';
    if(cls[i]!=='kombi')continue;
    fit1[i]=prism(g,S1);fit2[i]=prism(g,S2);
  }
  // konum duzeltmesi: log(NAC/m2) ~ 1 + en ust + zemin + dukkan ustu + dis cephe + log(alan)
  const rows=[];for(let i=0;i<n;i++)if(fit1[i]&&fit1[i].nac>0)rows.push(i);
  const X=i=>[1,f.top[i],f.gr[i],f.sh[i],f.ext[i],Math.log(f.ar[i])],P=6;
  const A=Array.from({length:P},()=>new Array(P).fill(0)),bv=new Array(P).fill(0);
  rows.forEach(i=>{const x=X(i),y=Math.log(fit1[i].nac/f.ar[i]);for(let r=0;r<P;r++){bv[r]+=x[r]*y;for(let c=0;c<P;c++)A[r][c]+=x[r]*x[c];}});
  for(let c=0;c<P;c++){let p=c;for(let r=c+1;r<P;r++)if(Math.abs(A[r][c])>Math.abs(A[p][c]))p=r;[A[c],A[p]]=[A[p],A[c]];[bv[c],bv[p]]=[bv[p],bv[c]];
    for(let r=0;r<P;r++){if(r===c)continue;const k=A[r][c]/A[c][c];for(let q=c;q<P;q++)A[r][q]-=k*A[c][q];bv[r]-=k*bv[c];}}
  const beta=bv.map((v,i)=>v/A[i][i]);
  rows.forEach(i=>{const x=X(i);res[i]=Math.log(fit1[i].nac/f.ar[i])-x.reduce((s,v,k)=>s+v*beta[k],0);
    if(fit2[i]&&fit2[i].nac>0)dl[i]=Math.log(fit2[i].nac/fit1[i].nac);});
  // bina duzeyi
  const flatsOf=Array.from({length:nb},()=>[]);for(let i=0;i<n;i++)flatsOf[f.bi[i]].push(i);
  const bs=new Array(nb).fill(null);
  for(let b=0;b<nb;b++){const r=flatsOf[b].filter(i=>res[i]!==null).map(i=>res[i]);if(r.length)bs[b]=median(r);}
  const pct=(vals)=>{const idx=vals.map((v,i)=>[v,i]).filter(x=>x[0]!==null).sort((a,b)=>a[0]-b[0]),out=new Array(vals.length).fill(null),N=idx.length;
    let i=0;while(i<N){let j=i;while(j+1<N&&idx[j+1][0]===idx[i][0])j++;const r=((i+1)+(j+1))/2;for(let k=i;k<=j;k++)out[idx[k][1]]=r/N*100;i=j+1;}return out;};
  const bpct=pct(bs);
  for(let i=0;i<n;i++)if(res[i]!==null)rel[i]=res[i]-bs[f.bi[i]];
  const relp=pct(rel);
  const out=D.b.map((B,b)=>{
    const fl=flatsOf[b],an=fl.filter(i=>res[i]!==null),nm=an.filter(i=>f.mv[i]<0&&dl[i]!==null);
    let lvl=an.length>=6?2:an.length>=3?1:0;if(!B.yrr)lvl=Math.max(lvl-1,0);
    const ch=nm.length?Math.round((Math.exp(median(nm.map(i=>dl[i])))-1)*100):null;
    const heat={};fl.forEach(i=>heat[cls[i]]=(heat[cls[i]]||0)+1);
    return {s:bs[b]===null?null:Math.round(bpct[b]),conf:an.length?['Düşük','Orta','Yüksek'][lvl]:null,nb:an.length,ch,chn:nm.length,flag:ch!==null&&nm.length>=2&&ch<=-20?1:0,heat,fl};
  });
  // dogrulama (simulasyonun gercek cevabina karsi)
  const thName=['kombi','klima','gazsiz','gazsiz'];let ok=0,tot=0;const conf={};
  for(let i=0;i<n;i++){if(f.per[i]===0)continue;tot++;const t=thName[f.th[i]],p=cls[i];if(t===p)ok++;const k=t+'>'+p;conf[k]=(conf[k]||0)+1;}
  const cand=D.b.map((B,b)=>[B,out[b]]).filter(([B,o])=>B.era==='pre2000'&&!B.t_mant&&o.chn>=1);
  const auc=(()=>{const pos=cand.filter(c=>c[0].t_ret).map(c=>-c[1].ch),neg=cand.filter(c=>!c[0].t_ret).map(c=>-c[1].ch);let s=0;pos.forEach(p=>neg.forEach(q=>{s+=p>q?1:p===q?0.5:0;}));return s/(pos.length*neg.length);})();
  const flags=out.filter(o=>o.flag).length,flagTrue=D.b.filter((B,b)=>out[b].flag&&B.t_ret).length;
  const t1=(typeof performance!=='undefined'?performance.now():Date.now());
  return {out,cls,fit1,fit2,rel:relp,dl,flatsOf,beta,HDD,nd,S1,S2,stats:{flats:n,analyzed:rows.length,clsAcc:ok/tot,conf,auc,flags,flagTrue,retTotal:D.b.filter(B=>B.t_ret).length,ms:Math.round(t1-t0),buildings:out.filter(o=>o.s!==null).length}};
}
if(typeof module!=='undefined')module.exports=analyzeLT;
