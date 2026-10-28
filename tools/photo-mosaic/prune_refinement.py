"""Refine a saved fit after explicit, logged rejection of inconsistent edges."""
from pathlib import Path
import argparse,json,sys,fcntl
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import mosaic
from projective_bundle import refine

def connected_filter(n,edges,rejected):
    result=[e for e in edges if (e['i'],e['j']) not in rejected]
    if len(mosaic.components(n,result))!=1:raise ValueError('Edge rejection disconnects source images; no component is silently discarded')
    return result

def main():
    root=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--parent',required=True);p.add_argument('--initial-run',required=True);p.add_argument('--run',required=True);p.add_argument('--max-evaluations',type=int,default=40);a=p.parse_args()
    parent=(root/a.parent).resolve();initial=(root/a.initial_run).resolve();run=(root/a.run).resolve()
    if not all(x.is_relative_to(root) for x in [parent,initial,run]):raise ValueError('Paths must stay within project')
    run.mkdir(parents=True,exist_ok=True);lock=(run/'refinement.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state=json.loads((parent/'manifest.json').read_text());previous=json.loads((initial/'refinement.json').read_text());records=state['inputs'];config=argparse.Namespace(**state['config']);threshold=config.max_error
    rejected=[e for e in previous['edges'] if e['median']>threshold];ids={(e['i'],e['j']) for e in rejected};edges=[]
    for path in sorted((parent/'pairs').glob('*.json')):
        e=json.loads(path.read_text())
        if e:edges.append(e)
    edges=connected_filter(len(records),edges,ids)
    mosaic.save(run/'rejected-edges.json',{'criterion':f'Previous global-fit median correspondence error > {threshold} working pixels','initialRun':str(initial),'rejected':rejected,'allImagesConnectedAfterRejection':True,'retainedEdges':len(edges)})
    fs=[]
    for i in range(len(records)):
        with np.load(parent/'features'/f'{i:05}.npz') as f:fs.append({'shape':f['shape'],'dtype':f['dtype']})
    small=[]
    for e in edges:
        ix=np.linspace(0,len(e['p'])-1,min(25,len(e['p'])),dtype=int);small.append({**e,'p':[e['p'][j] for j in ix],'q':[e['q'][j] for j in ix]})
    from threadpoolctl import threadpool_limits
    print(json.dumps({'stage':'logged-edge-rejection','rejected':len(rejected),'retained':len(edges),'sources':len(records)}),flush=True)
    with threadpool_limits(limits=2):T,result=refine([np.array(t) for t in previous['transforms']],previous['anchor'],small,max_evaluations=a.max_evaluations)
    errors=[]
    for e in edges:
        err=np.linalg.norm(mosaic.project_points(T[e['i']],np.array(e['p']))-mosaic.project_points(T[e['j']],np.array(e['q'])),axis=1);errors.append({'i':e['i'],'j':e['j'],'median':float(np.median(err)),'p95':float(np.percentile(err,95))})
    mosaic.save(run/'refinement.json',{'transforms':[t.tolist() for t in T],'anchor':previous['anchor'],'edges':errors,'converged':bool(result.success),'evaluations':result.nfev,'message':str(result.message)})
    for t,f in zip(T,fs):
        h,w=f['shape'][2:]
        if not mosaic.checked(t,w,h):raise ValueError('Unstable/reflected transform; no accepted alignment exported')
    if any(e['median']>threshold for e in errors):raise ValueError('Retained overlap edges still exceed the unchanged error guard')
    M,w,h=mosaic.native_transforms(T,fs,config)
    mosaic.save(run/'alignment.json',{'width':w,'height':h,'anchor':previous['anchor'],'transforms':[m.tolist() for m in M],'edgeErrors':errors,'rejectedEdgeCount':len(rejected),'warning':'Native sampling is estimated. Outlier rejection and residual checks do not rule out local 3D parallax.'})
    mosaic.save(run/'manifest.json',{'status':'alignment-verified','inputs':records,'parentIdentity':state['identity'],'parentRun':str(parent),'config':state['config'],'rejectedEdgeCount':len(rejected),'allImagesConnected':True})
    print(json.dumps({'stage':'alignment-verified','width':w,'height':h,'median':float(np.median([e['median'] for e in errors])),'worstMedian':max(e['median'] for e in errors)}),flush=True)
if __name__=='__main__':main()
