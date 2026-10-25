import pandas as pd, numpy as np, json
g=pd.read_pickle('g2.pkl'); X=pd.read_pickle('X.pkl')
model=json.load(open('./dedektif_model.json'))
f=model['features']
X['type']=g.PROP_TYPE.map({'Detached':0,'Semi detached':1,'End terrace':2,'Mid terrace':3,'Bungalow':4,'Flat':5}).values
X['elec']=(X['elec']/100).round()
mid={1:40,2:75,3:125,4:175,5:250}
idx=g.y.values/g.FLOOR_AREA_BAND.map(mid).values
iq=[round(float(np.quantile(idx,q)),1) for q in np.linspace(0,1,101)]
def contrib(x):
    c=np.zeros(len(f)); s=model['init']
    for t in model['trees']:
        n=0; s+=model['lr']*t['v'][0]
        while t['l'][n]!=-1:
            ch=t['l'][n] if x[t['f'][n]]<=t['t'][n] else t['r'][n]
            c[t['f'][n]]+=model['lr']*(t['v'][ch]-t['v'][n]); n=ch
    return s,c
def pct(q,r):
    if r<=q[0]: return 0
    if r>=q[100]: return 100
    for i in range(100):
        if r<=q[i+1]: return i+(r-q[i])/(q[i+1]-q[i]) if q[i+1]>q[i] else i
xs=X[f].values; y=g.y.values
P=[];I=[]
for i in range(len(xs)):
    b,c=contrib(xs[i]); p=b+c.sum()
    P.append(pct(model['residual_quantiles'],np.log(y[i])-p)); I.append(pct(iq,idx[i]))
P=np.array(P);I=np.array(I)
a=np.where((P>=92)&(I<55)&(xs[:,7]>0))[0]; b2=np.where((P<50)&(I>=90)&(xs[:,7]>0))[0]
for k in [a[0],a[1],a[2],b2[0],b2[1]]:
    base,c=contrib(xs[k]); print(dict(zip(f,xs[k])),'gas',y[k],'EPC',g.EPC.values[k],'ml',round(P[k]),'idx',round(I[k]),'base',round(np.exp(base)),'contrib%',{f[j]:round((np.exp(c[j])-1)*100) for j in range(len(f))})
json.dump(iq,open('iq.json','w'))
print('overlap app model', ((P>=90)&(I>=90)).sum()/(P>=90).sum())
