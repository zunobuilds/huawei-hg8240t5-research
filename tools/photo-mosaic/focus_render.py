"""Disk-backed native-resolution focus selection; no super-resolution or sharpening."""
from pathlib import Path
import hashlib,json,shutil
import cv2 as cv
import numpy as np
import tifffile


def render(records,fs,M,w,h,run,a,load,project_points,corners,save):
    dtype=np.dtype(str(fs[0]['dtype']));maximum=np.iinfo(dtype).max;tile=a.tile
    identity=hashlib.sha256(json.dumps({'inputs':records,'transforms':[np.asarray(m).tolist() for m in M], 'shape':[h,w],'dtype':str(dtype),'version':3},sort_keys=True).encode()).hexdigest()
    cache=Path(run)/'focus-cache';cache.mkdir(exist_ok=True);checkpoint=cache/'checkpoint.json'
    old=json.loads(checkpoint.read_text()) if checkpoint.exists() else None
    if old and old['identity']!=identity:raise ValueError('Focus cache identity mismatch; use a new output directory')
    resume=bool(old)
    if not resume and shutil.disk_usage(run).free<w*h*22:raise ValueError('Insufficient disk space for native focus selection')
    rgb=np.memmap(cache/'rgb.dat',dtype=dtype,mode='r+' if resume else 'w+',shape=(h,w,3))
    weights=np.memmap(cache/'weights.f32',dtype=np.float32,mode='r+' if resume else 'w+',shape=(h,w))
    if not resume:rgb[:]=0;weights[:]=0;rgb.flush();weights.flush();save(checkpoint,{'identity':identity,'nextImage':0,'qualities':[]})
    start=old['nextImage'] if resume else 0;qualities=old['qualities'] if resume else []
    cv.setNumThreads(4)
    for i in range(start,len(records)):
        r,m=records[i],np.asarray(M[i]);im=load(r['path']);ih,iw=im.shape[:2]
        if im.dtype!=dtype:raise ValueError('Mixed input depth')
        scale=min(1,1000/max(iw,ih));small=cv.resize(im,(max(1,round(iw*scale)),max(1,round(ih*scale))),interpolation=cv.INTER_AREA)
        gray=cv.cvtColor(small,cv.COLOR_BGR2GRAY).astype(np.float32)/maximum
        # Broadly smoothed multiscale Laplacian energy favors coherent regions:
        # not a claim of physical resolution or sharpness recovery.
        energy=np.zeros_like(gray)
        for sigma in [.6,1.2]:
            response=cv.Laplacian(cv.GaussianBlur(gray,(0,0),sigma),cv.CV_32F)
            energy+=cv.GaussianBlur(response*response,(0,0),35)
        score=np.sqrt(np.maximum(energy,0))+.0002
        bright=(np.min(small,axis=2)>maximum*.98).astype(np.float32)
        score*=np.clip(1-cv.GaussianBlur(bright,(0,0),4),.02,1)
        gh,gw=score.shape;yy,xx=np.mgrid[:gh,:gw].astype(np.float32)
        edge=np.minimum.reduce([xx+.5,yy+.5,gw-.5-xx,gh-.5-yy])
        score*=np.clip(edge/(min(gw,gh)*.04),0,1)
        alpha=cv.resize(score,(iw,ih),interpolation=cv.INTER_LINEAR);alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0
        q=project_points(m,corners(iw,ih));low=np.floor(q.min(0)).astype(int);high=np.ceil(q.max(0)).astype(int)
        xmin,ymin=max(0,int(low[0])),max(0,int(low[1]));xmax,ymax=min(w,int(high[0])),min(h,int(high[1]));wins=0
        for y in range(ymin,ymax,192):
            th=min(192,ymax-y);tw=xmax-xmin
            if tw<=0:continue
            local=np.array([[1,0,-xmin],[0,1,-y],[0,0,1]])@m
            confidence=cv.warpPerspective(alpha,local,(tw,th),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT)
            pixels=cv.warpPerspective(im,local,(tw,th),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT)
            previous=weights[y:y+th,xmin:xmax];take=confidence>previous
            region=rgb[y:y+th,xmin:xmax];region[take]=pixels[take];previous[take]=confidence[take];wins+=int(take.sum())
        qualities.append({'image':i,'medianFocusScore':float(np.median(score)),'pixelsWinningAtInsertion':wins})
        if (i+1)%10==0 or i+1==len(records):
            rgb.flush();weights.flush();save(checkpoint,{'identity':identity,'nextImage':i+1,'qualities':qualities})
            save(Path(run)/'render-progress.json',{'renderer':'local-focus-selection-v3','images':i+1,'totalImages':len(records),'stage':'accumulating'})
            print(json.dumps({'stage':'focus-accumulate','image':i+1,'of':len(records)}),flush=True)
    if 'im' in locals():del im
    def tiles(mask):
        for y in range(0,h,tile):
            for x in range(0,w,tile):
                tw,th=min(tile,w-x),min(tile,h-y)
                out=np.zeros((tile,tile),np.uint8) if mask else np.zeros((tile,tile,3),dtype)
                if mask:out[:th,:tw]=(weights[y:y+th,x:x+tw]>0)*255
                else:out[:th,:tw]=rgb[y:y+th,x:x+tw,::-1]
                yield out
    for filename,mask in [('mosaic.tif',False),('coverage.tif',True)]:
        dest=Path(run)/filename;partial=dest.with_suffix('.tif.partial')
        tifffile.imwrite(partial,data=tiles(mask),shape=(h,w) if mask else (h,w,3),dtype=np.uint8 if mask else dtype,bigtiff=True,tile=(tile,tile),compression='deflate',photometric='minisblack' if mask else 'rgb',metadata=None,maxworkers=1)
        partial.replace(dest)
    save(Path(run)/'focus-quality.json',{'method':'Local multiscale contrast selects one aligned native source per pixel; hard source transitions can remain. Not calibrated sharpness or super-resolution.','images':qualities,'identity':identity})
    save(Path(run)/'render-progress.json',{'renderer':'local-focus-selection-v3','stage':'complete','images':len(records),'totalImages':len(records)})
    del rgb,weights
    # Keep resumable cache until exported results have been independently verified.
