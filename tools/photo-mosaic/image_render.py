"""Image-driven, disk-backed renderer: decode each full-resolution source once."""
from pathlib import Path
import json,shutil
import cv2 as cv
import numpy as np
import tifffile

def render(records,fs,M,w,h,run,a,load,project_points,corners,save):
 if a.blend=='focus':
  from focus_render import render as focus_render
  return focus_render(records,fs,M,w,h,run,a,load,project_points,corners,save)
 dtype=np.dtype(str(fs[0]['dtype']));maxval=np.iinfo(dtype).max;tile=a.tile
 required=w*h*(16+dtype.itemsize*3+1)
 if shutil.disk_usage(run).free<required*1.1:raise ValueError('Insufficient disk for disk-backed blend and TIFF outputs')
 cache=run/'render-cache';cache.mkdir(exist_ok=True)
 sums=np.memmap(cache/'rgb.f32',mode='w+',dtype=np.float32,shape=(h,w,3));weights=np.memmap(cache/'weights.f32',mode='w+',dtype=np.float32,shape=(h,w));sums[:]=0;weights[:]=0
 qualities=[]
 for i,(r,m,f) in enumerate(zip(records,M,fs)):
  im=load(r['path']);ih,iw=im.shape[:2]
  if im.dtype!=dtype:raise ValueError('Mixed bit depth')
  scale=min(1,1000/max(iw,ih));small=cv.resize(im,(max(1,round(iw*scale)),max(1,round(ih*scale))),interpolation=cv.INTER_AREA)
  gray=cv.cvtColor(small,cv.COLOR_BGR2GRAY)
  if gray.dtype==np.uint16:gray=(gray/257).astype(np.uint8)
  clarity=float(np.clip(np.sqrt(cv.Laplacian(gray,cv.CV_64F).var())/20,.03,3))
  bright=(np.min(small,axis=2)>maxval*.96).astype(np.float32)
  confidence=np.clip(1-cv.GaussianBlur(bright,(0,0),5),.02,1)*clarity
  qualities.append({'image':i,'clarityWeight':clarity,'broadClippedFraction':float((confidence<clarity*.4).mean()),'contributingPixels':0})
  # Build smooth source-space feather/quality alpha once; warp premultiplied
  # RGB+alpha in large native OpenCV stripes, avoiding Python output-pixel grids.
  gh,gw=confidence.shape;yy,xx=np.mgrid[:gh,:gw].astype(np.float32)
  edge=np.minimum.reduce([(xx+.5)*iw/gw,(yy+.5)*ih/gh,(gw-.5-xx)*iw/gw,(gh-.5-yy)*ih/gh])
  alpha_small=confidence*np.clip(edge/max(1,min(iw,ih)*.10),0,1)
  alpha=cv.resize(alpha_small,(iw,ih),interpolation=cv.INTER_LINEAR)
  alpha[0,:]=alpha[-1,:]=0;alpha[:,0]=alpha[:,-1]=0
  source=np.empty((ih,iw,4),np.float32);source[:,:,:3]=im.astype(np.float32)*alpha[:,:,None];source[:,:,3]=alpha
  q=project_points(m,corners(iw,ih));low=np.floor(q.min(0)).astype(int);high=np.ceil(q.max(0)).astype(int)
  xmin,ymin=max(0,int(low[0])),max(0,int(low[1]));xmax,ymax=min(w,int(high[0])),min(h,int(high[1]))
  cv.setNumThreads(4)
  for y in range(ymin,ymax,256):
   th=min(256,ymax-y);tw=xmax-xmin
   if tw<=0:continue
   local=np.array([[1,0,-xmin],[0,1,-y],[0,0,1]])@m
   warped=cv.warpPerspective(source,local,(tw,th),flags=cv.INTER_LINEAR,borderMode=cv.BORDER_CONSTANT)
   weight=warped[:,:,3];qualities[-1]['contributingPixels']+=int(np.count_nonzero(weight))
   region=sums[y:y+th,xmin:xmax];old=weights[y:y+th,xmin:xmax]
   if a.blend=='best':
    take=weight>old;region[take]=warped[:,:,:3][take]/weight[take,None];old[take]=weight[take]
   else:region+=warped[:,:,:3];old+=weight
  del source,alpha
  if i%10==0 or i+1==len(records):
   save(run/'render-progress.json',{'renderer':'premultiplied-stripes-v3','images':i+1,'totalImages':len(records),'stage':'accumulating'});print(json.dumps({'stage':'render-accumulate','image':i+1,'of':len(records)}),flush=True)
 save(run/'blend-quality.json',{'method':'edge feather multiplied by per-frame clarity and broad clipped-highlight confidence; no generated detail','images':qualities})
 del im
 def tiles(mask):
  for y in range(0,h,tile):
   for x in range(0,w,tile):
    tw,th=min(tile,w-x),min(tile,h-y);weight=weights[y:y+th,x:x+tw]
    out=np.zeros((tile,tile),np.uint8) if mask else np.zeros((tile,tile,3),dtype)
    if mask:out[:th,:tw]=(weight>0)*255
    else:
     rgb=np.array(sums[y:y+th,x:x+tw]);rgb=rgb if a.blend=='best' else rgb/np.maximum(weight[:,:,None],1e-12)
     out[:th,:tw]=np.clip(np.rint(rgb),0,maxval).astype(dtype)[:,:,::-1]
    yield out
 for filename,mask in [('mosaic.tif',False),('coverage.tif',True)]:
  p=run/(filename+'.partial');tifffile.imwrite(p,data=tiles(mask),shape=(h,w) if mask else (h,w,3),dtype=np.uint8 if mask else dtype,bigtiff=True,tile=(tile,tile),compression='deflate',photometric='minisblack' if mask else 'rgb',metadata=None,maxworkers=1);p.replace(run/filename)
 sums.flush();weights.flush();del sums,weights
 shutil.rmtree(cache)
 save(run/'render-progress.json',{'renderer':'premultiplied-stripes-v3','stage':'complete','images':len(records),'totalImages':len(records)})
