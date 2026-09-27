from analyse import *
def dec(x):
 x=np.asarray(x)/255;return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def enc(x):
 x=np.maximum(0,x);return 255*np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  rr=filt(base,scheme=scheme,pose=pose,scale=1,shell=0,part='straight',bin=12)
  rr=[r for r in rr if r['background'].startswith('neutral-') or r['background']=='g255']
  x=np.array([r['backgroundRGB'][1] for r in rr]);y=np.array([r['native'][1] for r in rr]); X=np.stack([dec(x),np.ones(len(x))],1);c=np.linalg.lstsq(X,dec(y),rcond=None)[0]
  print('LINEAR affine',scheme,pose,c,'max code',max(abs(enc(X@c)-y)))
print('COLOUR versus neutral perchannel curve, only fresh colours within 40..150, knots by fixed same bin')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for part,bn in [('straight',12),('arc',0)]:
   rr=filt(base,scheme=scheme,pose=pose,scale=1,shell=0,part=part,bin=bn)
   nr=sorted([r for r in rr if r['background'].startswith('neutral-')],key=lambda r:r['backgroundRGB'][1]);xs=np.array([r['backgroundRGB'][1] for r in nr]);ys=np.array([r['native'][1] for r in nr])
   cr=[r for r in rr if r['background'].startswith(('factor-','matched-channel-'))]
   errors=[(np.max(abs(np.interp(r['backgroundRGB'],xs,ys)-r['native'])),r['background']) for r in cr]
   print(scheme,pose,part,max(errors))
print('CHANNEL matched input spread across fresh colours, no fit')
for scheme in ['light','dark']:
 for pose in ['rest','inactive']:
  for part,bn in [('straight',12),('arc',0)]:
   rr=filt(base,scheme=scheme,pose=pose,scale=1,shell=0,part=part,bin=bn); groups=collections.defaultdict(list)
   for r in rr:
    if r['background'].startswith(('factor-','matched-channel-','neutral-')):
     for j in range(3):groups[r['backgroundRGB'][j]].append((r['native'][j],r['background'],j))
   mx=max((max(v)[0]-min(v)[0],k,min(v),max(v)) for k,v in groups.items())
   print(scheme,pose,part,mx)
print('CALIBRATION gradient input range of near shells',min(r['backgroundRGB'][1] for r in rows if r['background'] in ['v90','v270']),max(r['backgroundRGB'][1] for r in rows if r['background'] in ['v90','v270']))
print('DISPLAY RINGS 1x center')
for bg in ['g128','g255','v90','v270']:
 for scheme in ['light','dark']:
  for pose in ['rest','inactive']:
   rr=filt(base,background=bg,scheme=scheme,pose=pose,scale=1,shell=0)
   vals=[round(filt(rr,part='arc',bin=i)[0]['delta'][1],2) for i in range(16)]
   sides=[next((round(r['delta'][1],2) for r in rr if r['side']==side),None) for side in ['top','bottom','left','right']]
   print(bg,scheme,pose,vals,sides)
