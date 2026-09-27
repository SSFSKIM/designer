from analyse import *
knots=['neutral-40','neutral-56','neutral-72','neutral-88','neutral-104','neutral-128','neutral-150','g255']
print('NEUTRAL LS: multiplicative/affine max residual and coefs')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for part,b in [('straight',12),('arc',0)]:
   rr=[filt(base,background=bg,scheme=scheme,pose=pose,scale=1,shell=0,part=part,bin=b)[0] for bg in knots]
   x=np.array([r['backgroundRGB'][1] for r in rr]);y=np.array([r['native'][1] for r in rr]);
   c=np.linalg.lstsq(x[:,None],y,rcond=None)[0]; X=np.stack([x,np.ones(len(x))],1);d=np.linalg.lstsq(X,y,rcond=None)[0]
   print(scheme,pose,part,'mult',c.round(5),max(abs(x*c-y)).round(3),'affine',d.round(5),max(abs(X@d-y)).round(3))
print('CHROMATIC SAMPLE shell0')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for bg in ['red','green','factor-y1-c24-h0','factor-y1-c24-h120','factor-y1-c24-h240','matched-channel-0','matched-channel-1']:
   rr=filt(base,background=bg,scheme=scheme,pose=pose,scale=1,shell=0)
   print(scheme,pose,bg,[(r['part'],r['backgroundRGB'],r['native']) for r in rr if (r['part'],r['bin']) in [('straight',12),('arc',0)]])
print('GRADIENTS 1x all cal placements shell0')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for r in rows:
   if r['scheme']==scheme and r['pose']==pose and r['scale']==1 and r['background'] in ['v90','v270'] and r['shell']==0 and (r['part'],r['bin']) in [('straight',12),('straight',4),('arc',0),('arc',12),('arc',4)]:
    print(scheme,pose,r['cell'].split('/')[1],r['member'],r['part'],r['bin'],r['backgroundRGB'][1],r['native'][1],r['delta'][1])
