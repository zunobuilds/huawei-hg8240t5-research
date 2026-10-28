from pathlib import Path
import sys,json,argparse,os,hashlib,shutil,fcntl
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import mosaic
from projective_bundle import refine
os.umask(0o077)
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Refine cached affine inliers with a projective bundle adjustment.')
parser.add_argument('--parent',required=True);parser.add_argument('--run',required=True)
args=parser.parse_args();parent=(root/args.parent).resolve();run=(root/args.run).resolve()
if not parent.is_relative_to(root) or not run.is_relative_to(root):raise ValueError('Paths must stay within project')
run.mkdir(parents=True,exist_ok=True)
lock=(run/'refinement.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
original=json.loads((parent/'manifest.json').read_text())
if (run/'manifest.json').exists():
 previous=json.loads((run/'manifest.json').read_text())
 if previous.get('parentIdentity')!=original.get('identity'):raise ValueError('Parent input/configuration identity changed; use a new refinement directory')
records=original['inputs'];settings=dict(original['config']);settings.update(model='homography',preview_only=True);settings.pop('version',None);a=argparse.Namespace(**settings)
fs=[]
for i in range(len(records)):
 with np.load(parent/'features'/f'{i:05}.npz',allow_pickle=False) as d:fs.append({k:d[k] for k in ['shape','dtype']})
edges=[]
for p in sorted((parent/'pairs').glob('*.json')):
 e=json.loads(p.read_text())
 if e:edges.append(e)
assert len(mosaic.components(len(records),edges))==1
mosaic.save(run/'manifest.json',{'status':'refining','inputs':records,'parentRun':str(parent),'parentIdentity':original.get('identity'),'config':settings,'purpose':'Image alignment only; no text analysis'})
init=run/'initialization.json'
if init.exists():
 data=json.loads(init.read_text());T=[np.array(x) for x in data['transforms']];anchor=data['anchor']
else:
 a.model='affine';a.initialization_only=True;a.affine_iterations=3;a.affine_maxiter=400;T,anchor,error=mosaic.solve(len(records),edges,fs,a);mosaic.save(init,{'transforms':[x.tolist() for x in T],'anchor':anchor,'errors':error});a.model='homography'
small=[]
for e in edges:
 ids=np.linspace(0,len(e['p'])-1,min(25,len(e['p'])),dtype=int);small.append({**e,'p':[e['p'][i] for i in ids],'q':[e['q'][i] for i in ids]})
print(json.dumps({'stage':'projective-refinement','images':len(records),'edges':len(small),'correspondences':sum(len(e['p']) for e in small)}),flush=True)
from threadpoolctl import threadpool_limits
with threadpool_limits(limits=2):T,result=refine(T,anchor,small,max_evaluations=80)
errors=[]
for e in edges:
 p,q=np.array(e['p']),np.array(e['q']);err=np.linalg.norm(mosaic.project_points(T[e['i']],p)-mosaic.project_points(T[e['j']],q),axis=1);errors.append({'i':e['i'],'j':e['j'],'median':float(np.median(err))})
mosaic.save(run/'refinement.json',{'converged':bool(result.success),'evaluations':result.nfev,'message':str(result.message),'medianEdgeError':float(np.median([x['median'] for x in errors])),'edges':errors,'transforms':[t.tolist() for t in T],'anchor':anchor})
for i,t in enumerate(T):
 h,w=fs[i]['shape'][2:]
 if not mosaic.checked(t,w,h):raise ValueError(f'Unstable perspective transform {i}')
M,w,h=mosaic.native_transforms(T,fs,a)
mosaic.save(run/'alignment.json',{'width':w,'height':h,'anchor':anchor,'model':'projective; affine-RANSAC inlier measurements','transforms':[m.tolist() for m in M],'edgeErrors':errors})
# Native preview is rendered separately after checking geometric residuals.
if any(e['median']>a.max_error for e in errors):raise ValueError('Measured projective edge errors exceed the configured guard; inspect refinement.json')
mosaic.save(run/'preview-ready.json',{'status':'preview-ready','width':w,'height':h,'images':len(records),'converged':bool(result.success),'medianEdgeError':float(np.median([x['median'] for x in errors]))})
print(json.dumps({'stage':'preview-ready','directory':str(run),'width':w,'height':h}),flush=True)
