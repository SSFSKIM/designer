"""Exercise the real grid runner on noiseless synthetic data, before native fitting."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
import basis

HERE=Path(__file__).resolve().parent;rng=np.random.default_rng(3910)
with tempfile.TemporaryDirectory(prefix='w39-edge-synthetic-') as temp:
 root=Path(temp);cache=root/'cache';cache.mkdir()
 count=120;t=np.repeat(rng.uniform(.05,11.8,(count,1)),64,axis=1);ny=np.repeat(rng.uniform(-1,1,(count,1)),64,axis=1)
 rad=basis.radial(t,ny,.8,1);bins=np.arange(count)//4
 np.savez_compressed(cache/'shape.npz',t=t,ny=ny,binids=bins,xy=np.zeros((count,2)),inside=np.ones(count,bool))
 meta=[dict(member=0,part='arc',side=None,bin=i%16,shell=-1,depthCss=.5,pixels=4,admissible=True,status='measured') for i in range(30)]
 q=np.sin(np.arange(44)+1)*.01;records=[]
 for i in range(12):
  b=rng.uniform(.25,.7,3);y=b@np.array([.2126,.7152,.0722]);z=b-y
  colour=np.column_stack((np.ones(3),np.full(3,y),z,y*z))
  native=(b+(rad@q.reshape(11,4))@colour.T)*255
  np.savez_compressed(cache/(str(i)+'.npz'),native=native,states=native[None],stateix=np.zeros(7,int),
      backdrop=np.repeat((b*255)[None],count,axis=0),deep=b*255,bar=np.full((30,3),.5))
  records.append(dict(id=str(i),geometry='shape',cell='synthetic/'+str(i),member=0,role='calibration' if i<10 else 'validation',
      scheme='light',pose='rest',scale=1+i%2,span=44,backgroundKind='solid'))
 (cache/'manifest.json').write_text(json.dumps(dict(inventorySha256='synthetic-no-native-input',records=records,geometries={'shape':{'bins':meta}})))
 result=subprocess.run([sys.executable,str(HERE/'fit-grid.py'),str(cache),str(root/'output'),'--endpoint','light-active','--grid-limit','1'],capture_output=True,text=True)
 print(result.stdout);print(result.stderr,file=sys.stderr);assert result.returncode==0
 summary=json.loads((root/'output/summary.json').read_text())
 for method,key in [('leastSquares','bestLeastSquares'),('minimax','bestMinimax')]:
  row=summary[key][method];error=max(abs(np.array(row['coefficients'])-q))
  print(method,'converged',row['converged'],'coefficient error',error)
  assert row['converged'] and error<1e-5
 print('Native reads0; synthetic all44-coefficient recovery and real runner scoring pass.')
