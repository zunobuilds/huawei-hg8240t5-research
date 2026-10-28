from pathlib import Path
import sys,json,argparse,os,fcntl
import numpy as np,cv2 as cv,tifffile
sys.path.insert(0,str(Path(__file__).parent));import mosaic,image_render
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Render a verified saved alignment using original photographs.')
parser.add_argument('--parent',required=True);parser.add_argument('--alignment-run',required=True);parser.add_argument('--output',required=True)
parser.add_argument('--preview',action='store_true');parser.add_argument('--blend',choices=['feather','best','focus'],default='focus')
parser.add_argument('--geometry')
args=parser.parse_args();parent=(root/args.parent).resolve();run=(root/args.alignment_run).resolve();output=(root/args.output).resolve()
for path in [parent,run,output]:
 if not path.is_relative_to(root):raise ValueError('All paths must stay in project')
output.mkdir(parents=True,exist_ok=True)
lock=(output/'render.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
state=json.loads((parent/'manifest.json').read_text());alignment=json.loads((run/'alignment.json').read_text());records=state['inputs'];a=argparse.Namespace(**state['config']);fs=[]
a.blend=args.blend
if any(e.get('median',0)>a.max_error for e in alignment.get('edgeErrors',[])):raise ValueError('Alignment exceeds measured edge-error guard')
for i in range(len(records)):
 with np.load(parent/'features'/f'{i:05}.npz') as d:fs.append({'shape':d['shape'],'dtype':d['dtype']})
M=[np.array(m) for m in alignment['transforms']];w,h=alignment['width'],alignment['height']
if args.preview:
 scale=min(1,2048/max(w,h));W,H=round(w*scale),round(h*scale);S=np.diag([scale,scale,1]);out=output/'quick-preview';out.mkdir(parents=True,exist_ok=True);mats=[]
 def reduced(p):
  im=cv.imread(str(p),cv.IMREAD_REDUCED_COLOR_4)
  if im is None:raise ValueError('Cannot load reduced JPEG')
  return im
 for m,f,r in zip(M,fs,records):
  im=reduced(r['path']);hh,ww=im.shape[:2];ih,iw=f['shape'][:2];mats.append(S@m@np.diag([iw/ww,ih/hh,1]))
 image_render.render(records,fs,mats,W,H,out,a,reduced,mosaic.project_points,mosaic.corners,mosaic.save)
 rgb=tifffile.imread(out/'mosaic.tif');cv.imwrite(str(output/'preview-fast.png'),rgb[:,:,::-1]);print(json.dumps({'preview':str(output/'preview-fast.png')}),flush=True)
else:
 geometry=json.loads((root/args.geometry).read_text()) if args.geometry else alignment;M=[np.array(m) for m in geometry['transforms']];w,h=geometry['width'],geometry['height']
 out=output;out.mkdir(parents=True,exist_ok=True)
 image_render.render(records,fs,M,w,h,out,a,mosaic.load,mosaic.project_points,mosaic.corners,mosaic.save)
 print(json.dumps({'file':str(out/'mosaic.tif'),'bytes':(out/'mosaic.tif').stat().st_size,'width':w,'height':h}),flush=True)
