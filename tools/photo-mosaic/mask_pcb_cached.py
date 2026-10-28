"""PCB-colour constrained re-registration of an existing cached photo set."""
from pathlib import Path
import argparse,json,sys,os,hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np,cv2 as cv
sys.path.insert(0,str(Path(__file__).parent));import mosaic

def pcb_mask(im):
 hsv=cv.cvtColor(im,cv.COLOR_BGR2HSV);green=cv.inRange(hsv,np.array([35,40,30]),np.array([100,255,255]))
 connected=cv.morphologyEx(green,cv.MORPH_CLOSE,np.ones((17,17),np.uint8));connected=cv.dilate(connected,np.ones((7,7),np.uint8))
 n,labels,stats,_=cv.connectedComponentsWithStats(connected)
 mask=np.zeros_like(green)
 if n>1:
  label=1+int(np.argmax(stats[1:,cv.CC_STAT_AREA]));ys,xs=np.where(labels==label)
  hull=cv.convexHull(np.column_stack([xs,ys]).astype(np.int32));region=np.zeros_like(green);cv.fillConvexPoly(region,hull,255)
  mask=cv.dilate(cv.bitwise_and(green,region),np.ones((11,11),np.uint8))
 return mask

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--parent',required=True);parser.add_argument('--run',required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[2];parent=(root/args.parent).resolve();run=(root/args.run).resolve()
    if not all(p.is_relative_to(root) for p in [parent,run]):raise ValueError('Project-relative paths required')
    run.mkdir(parents=True,exist_ok=True);(run/'features').mkdir(exist_ok=True);(run/'pairs').mkdir(exist_ok=True);(run/'masks').mkdir(exist_ok=True)
    state=json.loads((parent/'manifest.json').read_text());a=argparse.Namespace(**state['config']);records=state['inputs'];cv.setNumThreads(1)
    identity=hashlib.sha256((state['identity']+'pcb-colour-core-v1').encode()).hexdigest()
    if (run/'manifest.json').exists() and json.loads((run/'manifest.json').read_text())['identity']!=identity:raise ValueError('Mask-run identity mismatch')
    manifest={**state,'identity':identity,'status':'masking','parentRun':str(parent),'masking':'PCB green core and nearby silkscreen; case and broad raised-component interiors excluded from registration only'};mosaic.save(run/'manifest.json',manifest)
    def feature(item):
     i,r=item;dest=run/'features'/f'{i:05}.npz';maskpath=run/'masks'/f'{i:05}.png'
     if dest.exists() and maskpath.exists():
      with np.load(dest) as d:f={k:d[k] for k in d.files}
      return f,cv.imread(str(maskpath),cv.IMREAD_GRAYSCALE)
     with np.load(parent/'features'/f'{i:05}.npz') as d:f={k:d[k] for k in d.files}
     hh,ww=f['shape'][2:];im=cv.imread(r['path'],cv.IMREAD_REDUCED_COLOR_4);im=cv.resize(im,(int(ww),int(hh)))
     mask=pcb_mask(im)
     pts=np.rint(f['points']).astype(int);pts[:,0]=np.clip(pts[:,0],0,ww-1);pts[:,1]=np.clip(pts[:,1],0,hh-1);keep=mask[pts[:,1],pts[:,0]]>0
     f['points']=f['points'][keep];f['desc']=f['desc'][keep]
     temporary=dest.with_suffix('.tmp.npz');np.savez_compressed(temporary,**f);temporary.replace(dest);cv.imwrite(str(maskpath),mask)
     return f,mask
    fs=[];masks=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
     for i,(f,mask) in enumerate(pool.map(feature,enumerate(records))):
      fs.append(f);masks.append(mask)
      if i%100==0:print(json.dumps({'stage':'pcb-masks','image':i+1,'of':len(records)}),flush=True)
    # Reuse only measured correspondences inside both PCB masks. New matching is
    # necessary where a previous RANSAC fit preferred the case/background plane.
    def pair(pair):
     i,j=pair;dest=run/'pairs'/f'{i:05}-{j:05}.json'
     if dest.exists():return json.loads(dest.read_text())
     old=json.loads((parent/'pairs'/dest.name).read_text());result=None
     if old:
      p,q=np.array(old['p'],np.float32),np.array(old['q'],np.float32)
      def inside(points,mask):
       xy=np.rint(points).astype(int);h,w=mask.shape;xy[:,0]=np.clip(xy[:,0],0,w-1);xy[:,1]=np.clip(xy[:,1],0,h-1);return mask[xy[:,1],xy[:,0]]>0
      keep=inside(p,masks[i])&inside(q,masks[j]);p,q=p[keep],q[keep]
      if len(p)>=a.min_inliers:
       M,ok=cv.estimateAffine2D(p,q,method=cv.RANSAC,ransacReprojThreshold=2.5,maxIters=4000,confidence=.999)
       if M is not None:
        ok=ok.ravel()>0;p,q=p[ok],q[ok];H=np.vstack([M,[0,0,1]])
        def coverage(points,shape):return float(np.prod(np.ptp(points,axis=0))/np.prod(shape)) if len(points) else 0
        if len(p)>=a.min_inliers and mosaic.checked(H,int(fs[i]['shape'][3]),int(fs[i]['shape'][2])) and min(coverage(p,fs[i]['shape'][2:]),coverage(q,fs[j]['shape'][2:]))>=.02:
         result={**old,'H':H.tolist(),'p':p.tolist(),'q':q.tolist(),'inliers':len(p),'medianError':float(np.median(np.linalg.norm(mosaic.project_points(H,p)-q,axis=1))),'maskVerified':True}
     if result is None:result=mosaic.match_pair(i,j,fs,a)
     mosaic.save(dest,result);return result
    pairs=json.loads((parent/'candidates.json').read_text());edges=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
     for k,e in enumerate(pool.map(pair,pairs)):
      if e:edges.append(e)
      if k%100==0:print(json.dumps({'stage':'pcb-pairs','pair':k+1,'of':len(pairs),'accepted':len(edges)}),flush=True)
    groups=mosaic.components(len(records),edges);mosaic.save(run/'graph.json',{'components':groups,'acceptedEdges':len(edges),'candidatePairs':len(pairs)})
    manifest.update(status='matched',componentSizes=[len(g) for g in groups]);mosaic.save(run/'manifest.json',manifest)
    print(json.dumps({'stage':'pcb-graph','components':manifest['componentSizes'],'edges':len(edges)}),flush=True)

if __name__=='__main__':main()
