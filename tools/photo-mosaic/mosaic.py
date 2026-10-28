"""Offline, tiled mosaics for overlapping photographs of a mostly planar surface."""
from pathlib import Path
import argparse, collections, datetime, fcntl, hashlib, json, os, shutil, sys, zipfile
import cv2 as cv
import numpy as np
from PIL import Image
from scipy import sparse
from scipy.sparse.linalg import lsmr
from scipy.optimize import least_squares
import tifffile

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
EXT={'.jpg','.jpeg','.png','.tif','.tiff','.webp','.bmp'}
VERSION=1

def save(p,v):
    p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def project(p):
    p=Path(p).resolve()
    if not p.is_relative_to(ROOT):raise ValueError('Output/work paths must remain inside the project')
    return p
def name(s):
    if not s or Path(s).name!=s or s in {'.','..'}:raise ValueError('Use a simple dataset/run name')
    return s
def load(p):
    # OpenCV unchanged preserves16-bit TIFF/PNG. Apply EXIF orientation explicitly.
    a=cv.imread(str(p),cv.IMREAD_UNCHANGED)
    if a is None:raise ValueError(f'Unsupported/corrupt image: {p}')
    if a.dtype not in (np.uint8,np.uint16):raise ValueError('Only8/16-bit integer images are supported')
    with Image.open(p) as im:o=im.getexif().get(274,1)
    if o==2:a=np.fliplr(a)
    elif o==3:a=np.rot90(a,2)
    elif o==4:a=np.flipud(a)
    elif o==5:a=np.swapaxes(a,0,1)
    elif o==6:a=np.rot90(a,3)
    elif o==7:a=np.flip(np.swapaxes(a,0,1),(0,1))
    elif o==8:a=np.rot90(a,1)
    if a.ndim==2:a=cv.cvtColor(a,cv.COLOR_GRAY2BGR)
    if a.shape[2]!=3:raise ValueError('Inputs must be opaque RGB/grayscale; flatten alpha on a separate copy first')
    return np.ascontiguousarray(a)
def project_points(H,p):
    q=np.c_[p,np.ones(len(p))]@H.T
    return q[:,:2]/q[:,2,None]
def corners(w,h):return np.array([[0,0],[w,0],[w,h],[0,h]],np.float64)
def checked(H,w,h):
    if not np.isfinite(H).all():return False
    c=corners(w,h);z=np.c_[c,np.ones(4)]@H[2]
    if np.min(z)<=0:return False
    q=project_points(H,c)
    area=cv.contourArea(q.astype(np.float32),oriented=True)
    return area>0 and .03<area/(w*h)<30

def ingest(a):
    dest=BASE/'inbox'/name(a.dataset);dest.mkdir(parents=True,exist_ok=True)
    manifest=dest/'import.json';old=json.loads(manifest.read_text()) if manifest.exists() else []
    seen={x['sha256'] for x in old};records=list(old);src=Path(a.source).resolve()
    def copy(label,reader):
        if Path(label).suffix.lower() not in EXT:return
        tmp=dest/'.import-partial';h=hashlib.sha256()
        with tmp.open('wb') as f:
            while b:=reader.read(4*1024*1024):h.update(b);f.write(b)
        digest=h.hexdigest()
        if digest in seen:tmp.unlink();return
        stem=''.join(c if c.isalnum() or c in '-_.' else '_' for c in Path(label).stem)[:100]
        target=dest/(stem+'__'+digest[:16]+Path(label).suffix.lower());tmp.replace(target)
        seen.add(digest);records.append({'sourceName':label,'file':target.name,'sha256':digest});save(manifest,records)
    if src.is_dir():
        if dest.is_relative_to(src):raise ValueError('Import source may not contain destination')
        for p in sorted(src.rglob('*')):
            if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXT:
                with p.open('rb') as f:copy(str(p.relative_to(src)),f)
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for i in sorted(z.infolist(),key=lambda x:x.filename):
                if i.is_dir():continue
                if Path(i.filename).is_absolute() or '..' in Path(i.filename).parts or (i.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe ZIP member')
                with z.open(i) as f:copy(i.filename,f)
    else:raise ValueError('Provide an image directory or ZIP')
    print(json.dumps({'dataset':str(dest),'uniqueImages':len(records)}))

def features(records,run,a):
    from concurrent.futures import ThreadPoolExecutor
    # A SIFT instance per worker avoids sharing mutable detector state.
    cv.setNumThreads(1)
    def one(item):
        i,r=item
        sift=cv.SIFT_create(nfeatures=a.features)
        path=run/'features'/f'{i:05}.npz'
        if path.exists():
            with np.load(path,allow_pickle=False) as d:f={k:d[k] for k in d.files}
        else:
            im=load(r['path']);h,w=im.shape[:2];s=min(1,a.work_size/max(h,w));ww,hh=max(1,round(w*s)),max(1,round(h*s))
            small=cv.resize(im,(ww,hh),interpolation=cv.INTER_AREA)
            gray=cv.cvtColor(small,cv.COLOR_BGR2GRAY)
            if gray.dtype==np.uint16:gray=(gray/257).astype(np.uint8)
            kp,desc=sift.detectAndCompute(gray,None)
            f={'points':np.array([k.pt for k in kp],np.float32).reshape(-1,2),'desc':desc if desc is not None else np.empty((0,128),np.float32),'shape':np.array([h,w,hh,ww]),'dtype':np.array(im.dtype.name)}
            temp=path.with_suffix('.tmp.npz');np.savez_compressed(temp,**f);temp.replace(path)
        return f
    workers=max(1,min(6,int(os.environ.get('PHOTO_MOSAIC_FEATURE_WORKERS','4'))))
    fs=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending=collections.deque();items=iter(enumerate(records))
        for _ in range(workers*2):
            item=next(items,None)
            if item is not None:pending.append(pool.submit(one,item))
        while pending:
            f=pending.popleft().result();fs.append(f)
            print(json.dumps({'stage':'features','image':len(fs),'of':len(records),'keypoints':len(f['points']),'workers':workers}),flush=True)
            item=next(items,None)
            if item is not None:pending.append(pool.submit(one,item))
    return fs

def candidates(fs,a):
    n=len(fs);pairs=set()
    if a.all_pairs:return [(i,j) for i in range(n) for j in range(i+1,n)]
    samples=[f['desc'][::max(1,len(f['desc'])//64)][:64] for f in fs if len(f['desc'])]
    if not samples:return []
    sample=np.concatenate(samples);rng=np.random.default_rng(42)
    if len(sample)>16000:sample=sample[rng.choice(len(sample),16000,replace=False)]
    cv.setRNGSeed(42);k=min(64,len(sample));_,_,centers=cv.kmeans(sample.astype(np.float32),k,None,(cv.TERM_CRITERIA_MAX_ITER|cv.TERM_CRITERIA_EPS,12,.1),1,cv.KMEANS_PP_CENTERS)
    matcher=cv.FlannBasedMatcher(dict(algorithm=1,trees=4),dict(checks=32));hist=np.zeros((n,k),np.float32)
    for i,f in enumerate(fs):
        if len(f['desc']):
            ix=[m.trainIdx for m in matcher.match(f['desc'],centers)];hist[i]=np.bincount(ix,minlength=k)
    hist*=np.log((n+1)/(1+(hist>0).sum(0)))+1;hist/=np.maximum(np.linalg.norm(hist,axis=1,keepdims=True),1e-9)
    # Descriptor voting complements coarse histograms for close-ups with similar textures.
    retrieval=[];owners=[]
    for i,f in enumerate(fs):
        if len(f['desc']):
            sample=f['desc'][np.linspace(0,len(f['desc'])-1,min(128,len(f['desc'])),dtype=int)]
            retrieval.append(sample);owners.extend([i]*len(sample))
    pool=np.concatenate(retrieval).astype(np.float32);owners=np.array(owners)
    index=cv.flann_Index(pool,dict(algorithm=1,trees=5))
    for i in range(n):
        votes=np.zeros(n)
        if len(fs[i]['desc']):
            query=fs[i]['desc'][np.linspace(0,len(fs[i]['desc'])-1,min(128,len(fs[i]['desc'])),dtype=int)]
            indices,dist=index.knnSearch(query.astype(np.float32),min(10,len(pool)),params=dict(checks=64))
            for ids,ds in zip(indices,dist):
                candidates=set(owners[ids[ds<250**2]].tolist());candidates.discard(i)
                for j in candidates:votes[j]+=1
        voted=[int(j) for j in np.argsort(-votes)[:a.neighbors] if votes[j]>=2]
        js=list(np.argsort(-(hist@hist[i]))[:min(n,max(3,a.neighbors//3)+1)])+voted
        for j in list(js)+list(range(max(0,i-a.window),min(n,i+a.window+1))):
            if i!=j:pairs.add(tuple(sorted((i,int(j)))))
    return sorted(pairs)

def match_pair(i,j,fs,a):
    f,g=fs[i],fs[j];x,y=f['desc'],g['desc']
    if min(len(x),len(y))<a.min_inliers:return None
    matcher=cv.FlannBasedMatcher(dict(algorithm=1,trees=5),dict(checks=64))
    def good(x,y):
        return {m.queryIdx:m.trainIdx for row in matcher.knnMatch(x,y,k=2) if len(row)==2 for m,n in [row] if m.distance<a.ratio*n.distance}
    ab,ba=good(x,y),good(y,x);ix=[(u,v) for u,v in ab.items() if ba.get(v)==u]
    if len(ix)<a.min_inliers:return None
    p=np.array([f['points'][u] for u,v in ix]);q=np.array([g['points'][v] for u,v in ix])
    if a.model=='affine':
        M,mask=cv.estimateAffine2D(p,q,method=cv.RANSAC,ransacReprojThreshold=2.5,maxIters=4000,confidence=.999);H=np.vstack((M,[0,0,1])) if M is not None else None
    else:H,mask=cv.findHomography(p,q,cv.RANSAC,2.5,maxIters=4000,confidence=.999)
    if H is None:return None
    ok=mask.ravel().astype(bool);p,q=p[ok],q[ok]
    if len(p)<a.min_inliers or ok.mean()<.25:return None
    h,w=f['shape'][2:];gh,gw=g['shape'][2:]
    if not checked(H,w,h):return None
    def coverage(pts,w,h):return np.prod(np.ptp(pts,axis=0))/(w*h)
    if min(coverage(p,w,h),coverage(q,gw,gh))<.02:return None
    error=float(np.median(np.linalg.norm(project_points(H,p)-q,axis=1)))
    if error>2.5:return None
    if len(p)>a.edge_points:
        ids=np.linspace(0,len(p)-1,a.edge_points,dtype=int);p,q=p[ids],q[ids]
    return {'i':i,'j':j,'H':H.tolist(),'p':p.tolist(),'q':q.tolist(),'inliers':int(ok.sum()),'medianError':error}

def components(n,edges):
    graph=[[] for _ in range(n)]
    for e in edges:graph[e['i']].append(e['j']);graph[e['j']].append(e['i'])
    groups=[];seen=set()
    for i in range(n):
        if i in seen:continue
        todo=[i];seen.add(i);group=[]
        while todo:
            j=todo.pop();group.append(j)
            for k in graph[j]:
                if k not in seen:seen.add(k);todo.append(k)
        groups.append(group)
    return groups

def solve(n,edges,fs,a):
    degree=np.zeros(n)
    for e in edges:degree[e['i']]+=e['inliers'];degree[e['j']]+=e['inliers']
    anchor=int(np.argmax(degree));T=[None]*n;T[anchor]=np.eye(3);todo=[anchor]
    graph=[[] for _ in range(n)]
    for e in sorted(edges,key=lambda e:-e['inliers']):
        H=np.array(e['H']);graph[e['i']].append((e['j'],H));graph[e['j']].append((e['i'],np.linalg.inv(H)))
    while todo:
        i=todo.pop(0)
        for j,H in graph[i]:
            if T[j] is None:T[j]=T[i]@np.linalg.inv(H);T[j]/=T[j][2,2];todo.append(j)
    others=[i for i in range(n) if i!=anchor];offset={i:k for k,i in enumerate(others)};d=6 if a.model=='affine' else 8
    def pack(T):return np.concatenate([T[i].ravel()[:d] for i in others])
    def unpack(x):
        out=[None]*n;out[anchor]=np.eye(3)
        for i,k in offset.items():out[i]=np.r_[x[k*d:(k+1)*d],[0,0,1] if d==6 else [1]].reshape(3,3)
        return out
    if d==6:
        rows=[];cols=[];values=[];rhs=[];row=0
        for e in edges:
            for p,q in zip(e['p'],e['q']):
                for axis in range(2):
                    fixed=0.
                    for image,pt,sign in [(e['i'],p,1),(e['j'],q,-1)]:
                        v=[*pt,1]
                        if image==anchor:fixed+=sign*pt[axis]
                        else:
                            for c,value in enumerate(v):rows.append(row);cols.append(offset[image]*6+axis*3+c);values.append(sign*value)
                    rhs.append(-fixed);row+=1
        A=sparse.csr_matrix((values,(rows,cols)),shape=(row,6*(n-1)));b=np.array(rhs);x=pack(T)
        scale=1/np.maximum(np.sqrt(np.asarray(A.power(2).sum(axis=0))).ravel(),1e-12)
        normalized=A.multiply(scale).tocsr()
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=2):
            for iteration in range(getattr(a,"affine_iterations",5)):
                residual=(A@x-b).reshape(-1,2);norm=np.linalg.norm(residual,axis=1);weights=np.repeat(np.minimum(1,3/np.maximum(norm,1e-6)),2)**.5
                fit=lsmr(normalized.multiply(weights[:,None]).tocsr(),b*weights,atol=1e-7,btol=1e-7,maxiter=getattr(a,"affine_maxiter",1000),x0=x/scale)
                x=fit[0]*scale
                print(json.dumps({'stage':'global-affine','iteration':iteration+1,'solverSteps':fit[2],'stop':fit[1],'medianResidual':float(np.median(norm))}),flush=True)
        T=unpack(x)
    else:
        from projective_bundle import refine
        T,result=refine(T,anchor,edges)
        if not result.success:raise ValueError('Global projective refinement did not converge; inspect alignment or try affine')
    errors=[]
    for e in edges:
        err=np.linalg.norm(project_points(T[e['i']],np.array(e['p']))-project_points(T[e['j']],np.array(e['q'])),axis=1);errors.append({'i':e['i'],'j':e['j'],'median':float(np.median(err)),'p95':float(np.percentile(err,95))})
    if getattr(a,'initialization_only',False):return T,anchor,errors
    for i,t in enumerate(T):
        h,w=fs[i]['shape'][2:]
        if not checked(t,w,h):raise ValueError(f'Unstable/reflected transform for image{i}; no render produced')
    if any(e['median']>a.max_error for e in errors):raise ValueError(f'Overlap graph has inconsistent loops/parallax: {sum(e["median"]>a.max_error for e in errors)} of {len(errors)} edges exceed {a.max_error}px; worst median {max(e["median"] for e in errors):.2f}px')
    return T,anchor,errors

def native_transforms(T,fs,a):
    native=[];scales=[]
    for t,f in zip(T,fs):
        h,w,hh,ww=f['shape'];m=t@np.diag([ww/w,hh/h,1]);native.append(m);scales.append(np.linalg.svd(m[:2,:2],compute_uv=False)[-1])
    # Choose a canvas resolution retaining the finest input sampling near each center.
    output_scale=a.output_scale/min(scales);S=np.diag([output_scale,output_scale,1]);M=[S@m for m in native]
    all_corners=np.concatenate([project_points(m,corners(f['shape'][1],f['shape'][0])) for m,f in zip(M,fs)])
    low=np.floor(all_corners.min(0));high=np.ceil(all_corners.max(0));w,h=(high-low).astype(int)
    if min(w,h)<=0 or w*h>a.max_gigapixels*1e9:raise ValueError(f'Canvas {w}x{h} exceeds configured size limit; inspect geometry before changing limit')
    shift=np.array([[1,0,-low[0]],[0,1,-low[1]],[0,0,1]])
    return [shift@m for m in M],int(w),int(h)

class ImageCache:
    def __init__(self,limit):self.limit=limit;self.data=collections.OrderedDict();self.bytes=0
    def get(self,p):
        if p in self.data:self.data.move_to_end(p);return self.data[p]
        im=load(p)
        while self.data and self.bytes+im.nbytes>self.limit:
            _,old=self.data.popitem(last=False);self.bytes-=old.nbytes
        if im.nbytes<=self.limit:self.data[p]=im;self.bytes+=im.nbytes
        return im

def render(records,fs,M,w,h,run,a,preview=False):
    if not preview:
        from image_render import render as disk_render
        return disk_render(records,fs,M,w,h,run,a,load,project_points,corners,save)
    scale=min(1,2048/max(w,h)) if preview else 1.
    W,H=max(1,round(w*scale)),max(1,round(h*scale));transforms=[np.diag([scale,scale,1])@m for m in M]
    boxes=[]
    for m,f in zip(transforms,fs):
        p=project_points(m,corners(f['shape'][1],f['shape'][0]));boxes.append((*p.min(0),*p.max(0)))
    dtype=np.dtype(str(fs[0]['dtype']));maxval=np.iinfo(dtype).max
    cache=ImageCache(a.cache_mb*1024**2);tile=a.tile
    def make(x,y,tw,th):
        sums=np.zeros((th,tw,3),np.float64);weights=np.zeros((th,tw),np.float64);contributors=0
        for i,(left,top,right,bottom) in enumerate(boxes):
            if right<=x or bottom<=y or left>=x+tw or top>=y+th:continue
            im=cache.get(records[i]['path'])
            if im.dtype!=dtype:raise ValueError('Mixed8/16-bit input requires explicit normalization on copies')
            ih,iw=im.shape[:2];local=np.array([[1,0,-x],[0,1,-y],[0,0,1]])@transforms[i]
            warped=cv.warpPerspective(im,local,(tw,th),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT)
            yy,xx=np.mgrid[:th,:tw].astype(np.float64);dest=np.stack((xx+x,yy+y),axis=-1).reshape(-1,2);src=project_points(np.linalg.inv(transforms[i]),dest).reshape(th,tw,2)
            # Analytic edge feather weights prevent treating valid black pixels as holes.
            sx,sy=src[:,:,0],src[:,:,1];weight=np.minimum.reduce([sx+.5,sy+.5,iw-.5-sx,ih-.5-sy]);weight=np.clip(weight/np.maximum(1,min(iw,ih)*.10),0,1)
            valid=cv.warpPerspective(np.ones((ih,iw),np.uint8),local,(tw,th),flags=cv.INTER_NEAREST)>0;weight*=valid
            if a.blend=='best':
                take=weight>weights;sums[take]=warped[take];weights[take]=weight[take]
            else:sums+=warped.astype(np.float64)*weight[:,:,None];weights+=weight
            contributors+=1
        out=np.clip(np.rint(sums if a.blend=='best' else sums/np.maximum(weights[:,:,None],1e-12)),0,maxval).astype(dtype)
        return out[:,:,::-1],weights>0,contributors
    if preview:
        image,mask,_=make(0,0,W,H);cv.imwrite(str(run/'preview.png'),image[:,:,::-1]);cv.imwrite(str(run/'preview-coverage.png'),mask.astype(np.uint8)*255);return
    required=w*h*(dtype.itemsize*3+1)
    if shutil.disk_usage(run).free<required*1.1:raise ValueError(f'Insufficient free disk for conservative render estimate {required}bytes')
    def tiles(mask_only=False):
        done=0;total=((w+tile-1)//tile)*((h+tile-1)//tile)
        for y in range(0,h,tile):
            for x in range(0,w,tile):
                tw,th=min(tile,w-x),min(tile,h-y);im,mask,count=make(x,y,tw,th)
                out=np.zeros((tile,tile),np.uint8) if mask_only else np.zeros((tile,tile,3),dtype)
                if mask_only:out[:th,:tw]=mask*255
                else:out[:th,:tw]=im
                done+=1
                if done%10==0 or done==total:save(run/'render-progress.json',{'tiles':done,'total':total,'coveragePass':mask_only});print(json.dumps({'stage':'render','tiles':done,'of':total,'mask':mask_only}),flush=True)
                yield out
    # TIFF holds an alpha channel as a second coverage file, avoiding an in-memory canvas.
    for filename,mask in [('mosaic.tif',False),('coverage.tif',True)]:
        target=run/(filename+'.partial')
        tifffile.imwrite(target,data=tiles(mask),shape=(h,w) if mask else (h,w,3),dtype=np.uint8 if mask else dtype,bigtiff=True,tile=(tile,tile),compression='deflate',photometric='minisblack' if mask else 'rgb',metadata=None,maxworkers=1)
        target.replace(run/filename)

def _build(a,lock):
    source=Path(a.source).resolve();run=BASE/'runs'/name(a.run);run.mkdir(parents=True,exist_ok=True)
    manifest=run/'manifest.json'
    if manifest.exists() and not a.resume:lock.close();raise ValueError('Run already exists; use --resume or choose a new run')
    config={k:v for k,v in vars(a).items() if k not in ['resume','func','run']};config['version']=VERSION
    records=[];seen={};duplicates=[]
    for p in sorted(source.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in EXT:continue
        if p.is_symlink():raise ValueError('Symlink input rejected')
        digest=sha(p)
        if digest in seen:duplicates.append({'path':str(p),'sameAs':seen[digest]});continue
        seen[digest]=str(p);records.append({'path':str(p),'sha256':digest,'bytes':p.stat().st_size})
    if len(records)<2:raise ValueError('Need at least2 unique readable photographs')
    identity=hashlib.sha256(json.dumps({'config':config,'records':records},sort_keys=True).encode()).hexdigest()
    if manifest.exists():
        old=json.loads(manifest.read_text())
        if old['identity']!=identity:raise ValueError('Inputs/options changed; choose a new run to avoid stale cache')
        if old['status']=='complete':
            for filename,digest in old['outputHashes'].items():
                if sha(run/filename)!=digest:raise ValueError('Completed output changed; choose new run')
            print(json.dumps({'status':'already-complete','run':str(run)}));lock.close();return
    state={'identity':identity,'status':'running','config':config,'inputs':records,'duplicates':duplicates,'started':datetime.datetime.now(datetime.timezone.utc).isoformat()};save(manifest,state)
    try:
        (run/'features').mkdir(exist_ok=True);(run/'pairs').mkdir(exist_ok=True)
        fs=features(records,run,a);pairs=candidates(fs,a);save(run/'candidates.json',pairs);edges=[]
        from concurrent.futures import ThreadPoolExecutor
        def process_pair(pair):
            i,j=pair;p=run/'pairs'/f'{i:05}-{j:05}.json'
            if p.exists():return json.loads(p.read_text())
            e=match_pair(i,j,fs,a);save(p,e);return e
        workers=max(1,min(8,int(os.environ.get('PHOTO_MOSAIC_WORKERS','6'))))
        pool=ThreadPoolExecutor(max_workers=workers);queue=collections.deque();iterator=iter(pairs)
        try:
            for _ in range(workers*2):
                pair=next(iterator,None)
                if pair is not None:queue.append(pool.submit(process_pair,pair))
            index=0
            while queue:
                e=queue.popleft().result()
                if e:edges.append(e)
                if index%25==0:print(json.dumps({'stage':'matching','pair':index+1,'of':len(pairs),'accepted':len(edges),'workers':workers}),flush=True)
                index+=1;pair=next(iterator,None)
                if pair is not None:queue.append(pool.submit(process_pair,pair))
        finally:pool.shutdown(wait=True,cancel_futures=True)
        groups=components(len(records),edges);save(run/'graph.json',{'components':groups,'acceptedEdges':len(edges),'candidatePairs':len(pairs)})
        if len(groups)!=1:raise ValueError(f'Overlap graph has {len(groups)} disconnected components; inspect graph.json, add bridge photos or start a new run with more neighbors')
        T,anchor,errors=solve(len(records),edges,fs,a);M,w,h=native_transforms(T,fs,a);save(run/'alignment.json',{'anchor':anchor,'width':w,'height':h,'model':a.model,'transforms':[m.tolist() for m in M],'edgeErrors':errors,'warning':'Small residuals cannot rule out false repetitive-pattern matches or3D parallax; inspect preview.'})
        render(records,fs,M,w,h,run,a,preview=True)
        if not a.preview_only:render(records,fs,M,w,h,run,a)
        outputs=['preview.png','preview-coverage.png']+([] if a.preview_only else ['mosaic.tif','coverage.tif'])
        state.update(status='complete',width=w,height=h,outputHashes={p:sha(run/p) for p in outputs});save(manifest,state);print(json.dumps({'status':'complete','run':str(run),'width':w,'height':h,'previewOnly':a.preview_only}))
    except BaseException as e:
        state.update(status='interrupted' if isinstance(e,KeyboardInterrupt) else 'failed',error=str(e));save(manifest,state);raise

def build(a):
    run=BASE/'runs'/name(a.run);run.mkdir(parents=True,exist_ok=True)
    with (run/'lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return _build(a,lock)

def render_saved(a):
    run=BASE/'runs'/name(a.run)
    with (run/'lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((run/'manifest.json').read_text());alignment=json.loads((run/'alignment.json').read_text())
        for r in state['inputs']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Input changed since alignment')
        settings=argparse.Namespace(**state['config']);settings.preview_only=False
        fs=[]
        for i in range(len(state['inputs'])):
            with np.load(run/'features'/f'{i:05}.npz',allow_pickle=False) as d:fs.append({'shape':d['shape'],'dtype':d['dtype']})
        render(state['inputs'],fs,[np.array(m) for m in alignment['transforms']],alignment['width'],alignment['height'],run,settings)
        state.setdefault('outputHashes',{}).update({p:sha(run/p) for p in ['mosaic.tif','coverage.tif']});state.update(status='complete',fullResolutionRendered=True);save(run/'manifest.json',state)
        print(json.dumps({'status':'full-resolution-render-complete','run':str(run)}))

def main():
    os.umask(0o077);cv.setNumThreads(2)
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('import');p.add_argument('source');p.add_argument('--dataset',required=True);p.set_defaults(func=ingest)
    p=sub.add_parser('render');p.add_argument('--run',required=True);p.set_defaults(func=render_saved)
    p=sub.add_parser('build');p.add_argument('source');p.add_argument('--run',required=True);p.add_argument('--resume',action='store_true');p.add_argument('--preview-only',action='store_true');p.add_argument('--blend',choices=['feather','best','focus'],default='feather');p.add_argument('--model',choices=['affine','homography'],default='affine');p.add_argument('--work-size',type=int,default=1400);p.add_argument('--features',type=int,default=5000);p.add_argument('--neighbors',type=int,default=12);p.add_argument('--window',type=int,default=2);p.add_argument('--all-pairs',action='store_true');p.add_argument('--min-inliers',type=int,default=25);p.add_argument('--ratio',type=float,default=.72);p.add_argument('--edge-points',type=int,default=100);p.add_argument('--max-error',type=float,default=5);p.add_argument('--tile',type=int,default=512);p.add_argument('--cache-mb',type=int,default=512);p.add_argument('--max-gigapixels',type=float,default=2);p.add_argument('--output-scale',type=float,default=1);p.set_defaults(func=build)
    a=parser.parse_args()
    if a.command=='build':
        if a.tile<16 or a.tile%16 or min(a.work_size,a.features,a.min_inliers,a.edge_points,a.cache_mb,a.neighbors)<1 or a.window<0 or not 0<a.ratio<1 or min(a.output_scale,a.max_gigapixels,a.max_error)<=0:parser.error('Invalid size/matching/resource limits')
        if not Path(a.source).is_dir():parser.error('Source must be an image directory')
        if (BASE/'runs').resolve().is_relative_to(Path(a.source).resolve()):parser.error('Input directory may not contain output runs')
    try:a.func(a)
    except (ValueError,OSError,cv.error) as e:print(json.dumps({'status':'failed','error':str(e)}),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
