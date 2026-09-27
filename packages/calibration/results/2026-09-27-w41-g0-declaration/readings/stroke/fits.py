from analyse import *
fits=[]
for bg in ['g128','g255']:
 for scheme in ['light','dark']:
  for pose in ['rest','inactive']:
   rr=filt(base,background=bg,scheme=scheme,pose=pose,scale=1,shell=0)
   a=np.array([r['bin']*np.pi/8 for r in rr]); X=np.stack([np.ones(len(a)),np.cos(a)**2,np.maximum(0,-np.sin(a))],1); y=np.array([r['delta'][1] for r in rr]); coef=np.linalg.lstsq(X,y,rcond=None)[0]; e=X@coef-y
   fits.append(dict(bg=bg,scheme=scheme,pose=pose,coef=coef.tolist(),rmse=float(np.sqrt(np.mean(e**2))),max=float(max(abs(e))),measuredMax=float(max(abs(e)[np.array([r['pixels']>=4 for r in rr])]))))
print(json.dumps(fits,indent=1))
print('neutral knots output shell0: top,apex')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  rr=filt(base,scheme=scheme,pose=pose,scale=1,shell=0)
  print(scheme,pose)
  for bg in ['neutral-40','neutral-56','neutral-72','neutral-88','neutral-104','neutral-128','neutral-150','g255']:
   print(bg,[(r['part'],r['native'][1],r['backgroundRGB'][1]) for r in filt(rr,background=bg) if (r['part'],r['bin']) in [('straight',12),('arc',0)]])
(scratch/'angular-fits.json').write_text(json.dumps(fits))
