import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares,linprog
R=Path('/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-26-w39-g2-identification');sys.path.insert(0,str(R/'instrument'))
import body
out=Path.home()/'vitrea-w41/grounding/body';data=json.loads((out/'readings.json').read_text());fits=json.loads((out/'h3.json').read_text());results=[]
def interp_basis(v,nodes):return np.stack([np.interp(v,nodes,np.eye(len(nodes))[j]) for j in range(len(nodes))],1)
for f in fits:
 rows=[r for r in data['rows'] if r['scheme']==f['scheme'] and r['pose']==f['pose']];x=np.array([r['input'] for r in rows])/255;y=np.array([r['median'] for r in rows]);nc=np.array(f['neutral'])/255;W=body.W;lev=x@W;ch=x-lev[:,None];base=body.curve(lev,body.KNOTS,nc)[:,None]*255
 basis=interp_basis(lev,np.array([63,93,118])/255)
 lab=body.lab(body.decode(x));theta=(np.arctan2(lab[:,2],lab[:,1])/(2*np.pi)*6)%6;j=np.floor(theta).astype(int);t=theta-j;hb=np.zeros((len(x),6));hb[np.arange(len(x)),j]=1-t;hb[np.arange(len(x)),(j+1)%6]=t
 for name,b in [('encoded-Y3',basis),('encoded-hue6',hb),('encoded-constant',np.ones((len(x),1)))]:
  A=(ch[:,:,None]*b[:,None,:]*255).reshape(-1,b.shape[1]);target=(y-base).ravel();cy=y.ravel();keep=(cy>5)&(cy<250)
  # Encoded forward clipping has same interval structure; censored rails one-sided at5/250.
  lower=np.where(cy>=250,250,np.where(cy<=5,-np.inf,cy));upper=np.where(cy<=5,5,np.where(cy>=250,np.inf,cy));bas=np.broadcast_to(base,y.shape).ravel()
  au=[];bu=[]
  for k in range(len(cy)):
   if np.isfinite(upper[k]):au.append(np.r_[A[k],-1]);bu.append(upper[k]-bas[k])
   if np.isfinite(lower[k]):au.append(np.r_[-A[k],-1]);bu.append(bas[k]-lower[k])
  lp=linprog(np.r_[np.zeros(b.shape[1]),1],A_ub=au,b_ub=bu,bounds=[(0,3)]*b.shape[1]+[(0,None)],method='highs');assert lp.success
  p=np.clip(base+(A@lp.x[:-1]).reshape(y.shape),0,255)
  error=np.where(y>=250,np.maximum(250-p,0),np.where(y<=5,np.maximum(p-5,0),abs(p-y)))
  rr=dict(scheme=f['scheme'],pose=f['pose'],family=name,max=float(error.max()),parameters=b.shape[1],scores=[dict(cell=r['cell'],sid=r['sid'],scale=r['scale'],pred=pp.tolist(),native=r['median'],error=ee.tolist()) for r,pp,ee in zip(rows,p,error)])
  results.append(rr);print(f['scheme'],f['pose'],name,'max',error.max(),'ordinary',max(max(r['error']) for r in rr['scores'] if not r['sid'].startswith(('red-','green-'))),flush=True)
 # OKLab matrix interpolated between three L nodes. Frozen F(L) of H3prime.
 nk=body.lab(body.decode(np.repeat(body.KNOTS[:,None],3,axis=1)))[:,0];ny=body.lab(body.decode(np.repeat(nc[:,None],3,axis=1)))[:,0]
 bb=interp_basis(lab[:,0],np.cbrt([.05,.11,.18]));baseL=body.curve(lab[:,0],nk,ny)
 def forward(q):
  mats=np.einsum('ni,ijk->njk',bb,q.reshape(3,2,2));ab=np.einsum('nij,nj->ni',mats,lab[:,1:]);return body.encode(body.unlab(np.column_stack([baseL,ab])))*255
 def err(q):
  p=forward(q);return np.where(y>=250,np.minimum(p-250,0),np.where(y<=5,np.maximum(p-5,0),p-y)).ravel()
 rr=least_squares(err,np.tile([1,0,0,1],3),max_nfev=3000);p=forward(rr.x);ee=abs(err(rr.x)).reshape(y.shape)
 results.append(dict(scheme=f['scheme'],pose=f['pose'],family='OKLab-L-matrix3',max=float(ee.max()),success=bool(rr.success),parameters=12,scores=[dict(cell=r['cell'],sid=r['sid'],scale=r['scale'],pred=pp.tolist(),native=r['median'],error=e.tolist()) for r,pp,e in zip(rows,p,ee)]))
 print(f['scheme'],f['pose'],'OKLab-L-matrix3 LS max',ee.max(),flush=True)
(out/'exploratory.json').write_text(json.dumps(results))
