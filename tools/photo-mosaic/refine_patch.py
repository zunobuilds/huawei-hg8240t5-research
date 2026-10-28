"""Select source-detail patches and locally align a raised planar component."""
from pathlib import Path
import argparse,json,sys,subprocess,shutil
import numpy as np,cv2 as cv
sys.path.insert(0,str(Path(__file__).parent));import mosaic

def main():
 root=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--parent',required=True);p.add_argument('--alignment-run',required=True);p.add_argument('--output',required=True);p.add_argument('--roi',type=float,nargs=4,required=True,help='Union preview x y width height at max2048');p.add_argument('--count',type=int,default=8);p.add_argument('--reference-only',action='store_true');p.add_argument('--focus-stack',help='Explicit local focus-stack executable');args=p.parse_args()
 parent=(root/args.parent).resolve();ar=(root/args.alignment_run).resolve();out=(root/args.output).resolve()
 if not all(x.is_relative_to(root) for x in [parent,ar,out]):raise ValueError('Paths must stay in project')
 out.mkdir(parents=True,exist_ok=True);state=json.loads((parent/'manifest.json').read_text());alignment=json.loads((ar/'alignment.json').read_text());records=state['inputs'];scale=max(alignment['width'],alignment['height'])/2048;x,y,w,h=[round(v*scale) for v in args.roi];small=min(1,720/max(w,h));W,H=round(w*small),round(h*small);S=np.diag([small,small,1]);shift=np.array([[1,0,-x],[0,1,-y],[0,0,1]]);rows=[];cv.setNumThreads(4)
 for i,(r,m) in enumerate(zip(records,alignment['transforms'])):
  with np.load(parent/'features'/f'{i:05}.npz') as f:ih,iw=f['shape'][:2]
  m=shift@np.array(m);q=mosaic.project_points(m,mosaic.corners(iw,ih));low=q.min(0);high=q.max(0)
  if low[0]>w*.05 or low[1]>h*.05 or high[0]<w*.95 or high[1]<h*.95:continue
  im=cv.imread(r['path'],cv.IMREAD_REDUCED_COLOR_4)
  if im is None:continue
  hh,ww=im.shape[:2];mat=S@m@np.diag([iw/ww,ih/hh,1]);valid=cv.warpPerspective(np.full((hh,ww),255,np.uint8),mat,(W,H));coverage=float((valid>254).mean())
  if coverage<.995:continue
  warped=cv.warpPerspective(im,mat,(W,H));gray=cv.cvtColor(warped,cv.COLOR_BGR2GRAY);core=gray[H//6:H*5//6,W//6:W*5//6];contrast=float(cv.Laplacian(core,cv.CV_32F).var());bright=float((np.min(warped,2)>250).mean());density=1/max(np.linalg.svd(m[:2,:2],compute_uv=False));score=contrast*np.clip(density,.15,1.5)**.5*(1-bright)
  rows.append({'image':i,'score':score,'contrast':contrast,'density':float(density),'coverage':coverage,'preview':warped,'matrix':m})
 rows.sort(key=lambda r:-r['score']);chosen=rows[:args.count*3]
 if not chosen:raise ValueError('No full-coverage patch candidates')
 ref=chosen[0]['preview'];reference=cv.cvtColor(ref,cv.COLOR_BGR2GRAY).astype(np.float32)/255;mask=np.zeros((H,W),np.uint8);mask[H//7:H*6//7,W//7:W*6//7]=255;accepted=[]
 for row in chosen:
  warp=np.eye(3,dtype=np.float32);corr=1.
  if row is not chosen[0]:
   gray=cv.cvtColor(row['preview'],cv.COLOR_BGR2GRAY).astype(np.float32)/255
   try:corr,warp=cv.findTransformECC(reference,gray,warp,cv.MOTION_HOMOGRAPHY,(cv.TERM_CRITERIA_COUNT|cv.TERM_CRITERIA_EPS,100,1e-5),mask,5)
   except cv.error:continue
   q=mosaic.project_points(warp,mosaic.corners(W,H));delta=np.linalg.norm(q-mosaic.corners(W,H),axis=1)
   if corr<.75 or np.max(delta)>max(W,H)*.15:continue
  native=np.linalg.inv(S)@warp@S;matrix=np.linalg.inv(native)@row['matrix'];im=mosaic.load(records[row['image']]['path']);patch=cv.warpPerspective(im,matrix,(w,h));dest=out/f"source-{row['image']:05}.png";cv.imwrite(str(dest),patch)
  row={k:v for k,v in row.items() if k not in ['preview','matrix']};row.update(file=dest.name,correlation=float(corr),localWarp=native.tolist(),sourceToPatch=matrix.tolist());accepted.append(row)
  if args.reference_only or len(accepted)>=args.count:break
 report={'roiXYWH':[x,y,w,h],'previewROI':args.roi,'sources':accepted,'candidateCount':len(rows),'method':'Native-source patch selection and locally bounded ECC homography; only measured source pixels, no super-resolution'};mosaic.save(out/'patch.json',report)
 if args.reference_only:
  print(json.dumps({'reference':str(out/accepted[0]['file']),'candidates':len(rows),'dimensions':[w,h]}),flush=True);return
 if len(accepted)<2:raise ValueError('Fewer than two locally consistent source patches; retain reference but no stack produced')
 prefix=[args.focus_stack] if args.focus_stack else ([str(root/'photo_tools/bin/run'),'focus-stack'] if (root/'photo_tools/bin/run').is_file() else ['focus-stack'])
 command=prefix+['--threads=4','--batchsize=4','--no-opencl','--no-align','--no-whitebalance','--no-contrast','--denoise=0','--output='+str(out/'stacked.tif')]+[str(out/r['file']) for r in accepted]
 with (out/'focus-stack.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
 im=cv.imread(str(out/'stacked.tif'));cv.imwrite(str(out/'stack-preview.jpg'),cv.resize(im,(W,H)))
 print(json.dumps({'sources':len(accepted),'candidates':len(rows),'output':str(out/'stacked.tif'),'dimensions':[w,h]}),flush=True)
if __name__=='__main__':main()
