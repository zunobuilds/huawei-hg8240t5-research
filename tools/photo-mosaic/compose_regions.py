"""Compose reviewed native-source regions; no detail generation or enlargement."""
from pathlib import Path
import argparse,json
import cv2 as cv,numpy as np,tifffile
from PIL import Image

def polygon_alpha(shape,points,feather):
    h,w=shape;mask=np.zeros((h,w),np.uint8);poly=np.rint(np.array(points)*[w-1,h-1]).astype(np.int32);cv.fillPoly(mask,[poly],255)
    return np.minimum(cv.distanceTransform(mask,cv.DIST_L2,3)/max(1,feather),1).astype(np.float32)

def compose(base,patches,crop,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);cache=out/'composition-cache';cache.mkdir(exist_ok=True)
    with tifffile.TiffFile(base) as t:shape=t.pages[0].shape;dtype=t.pages[0].dtype
    if dtype!=np.uint8 or len(shape)!=3 or shape[2]!=3:raise ValueError('Only checked 8-bit RGB bases supported')
    rgb=np.memmap(cache/'rgb.u8',mode='w+',dtype=dtype,shape=shape);tifffile.imread(base,out=rgb);records=[]
    for spec in patches:
        info=json.loads(Path(spec['metadata']).read_text());x,y,w,h=info['roiXYWH'];x-=crop[0];y-=crop[1]
        if min(x,y)<0 or x+w>shape[1] or y+h>shape[0]:raise ValueError('Patch is outside crop')
        p=Path(spec['file']);im=cv.imread(str(p),cv.IMREAD_COLOR)
        if im is None or im.shape[:2]!=(h,w):raise ValueError('Patch dimensions changed')
        patch=im[:,:,::-1];alpha=polygon_alpha((h,w),spec['polygon'],spec.get('feather',70));target=rgb[y:y+h,x:x+w]
        # Preserve source colour; per-channel normalization trials were rejected.
        gain=np.ones(3)  # Retain source white balance; per-channel gain trial was rejected.
        for row in range(0,h,256):
            a=alpha[row:row+256,:,None]
            mixed=patch[row:row+256].astype(np.float32)*gain*a+target[row:row+256].astype(np.float32)*(1-a)
            target[row:row+256]=np.clip(np.rint(mixed),0,255).astype(np.uint8)
        records.append({'file':str(p),'selection':spec['selection'],'roiInCrop':[x,y,w,h],'colourGainRGB':gain.tolist(),'polygon':spec['polygon'],'feather':spec.get('feather',70)})
    rgb.flush();return rgb,records

def main():
    p=argparse.ArgumentParser();p.add_argument('spec');p.add_argument('--preview-only',action='store_true');args=p.parse_args();spec=json.loads(Path(args.spec).read_text());out=Path(spec['output']);rgb,records=compose(spec['base'],spec['patches'],spec['cropXYWH'],out)
    top=spec.get('trimTop',0);view=rgb[top:];h,w=view.shape[:2]
    alpha=np.memmap(out/'composition-cache/alpha.u8',mode='w+',dtype=np.uint8,shape=rgb.shape[:2]);alpha[:]=255
    if spec.get('foregroundPolygons'):
        alpha[:]=0
        for points in spec['foregroundPolygons']:
            cv.fillPoly(alpha,[np.rint(points).astype(np.int32)],255)
        alpha[:]=cv.dilate(alpha,np.ones((25,25),np.uint8))
    alpha.flush();visible=alpha[top:]
    # Outside-subject pixels are removed, not reconstructed or inpainted.
    for yy in range(0,h,256):view[yy:yy+256][visible[yy:yy+256]==0]=0
    small=cv.resize(view,(2400,round(h*2400/w)),interpolation=cv.INTER_AREA)
    if spec.get('rotate180'):small=small[::-1,::-1]
    Image.fromarray(small).save(out/'preview.jpg',quality=95,subsampling=0)
    (out/'composition.json').write_text(json.dumps({'regions':records,'trimTop':top,'rotate180':spec.get('rotate180',False),'width':w,'height':h},indent=2)+'\n')
    print(json.dumps({'preview':str(out/'preview.jpg'),'width':w,'height':h}),flush=True)
    if args.preview_only:return
    tile=512
    def tiles():
        for y in range(0,h,tile):
            for x in range(0,w,tile):
                hh,ww=min(tile,h-y),min(tile,w-x);block=np.zeros((tile,tile,3),np.uint8)
                if spec.get('rotate180'):block[:hh,:ww]=view[h-y-hh:h-y,w-x-ww:w-x][::-1,::-1]
                else:block[:hh,:ww]=view[y:y+hh,x:x+ww]
                yield block
    dest=out/'mosaic.tif';temporary=dest.with_suffix('.tif.partial');tifffile.imwrite(temporary,data=tiles(),shape=(h,w,3),dtype=np.uint8,bigtiff=True,tile=(tile,tile),compression='deflate',photometric='rgb',metadata=None,software=False,maxworkers=1);temporary.replace(dest)
    # PNG encoding requires a contiguous image but remains within this dataset's RAM budget.
    final=np.ascontiguousarray(view[::-1,::-1] if spec.get('rotate180') else view)
    opacity=np.ascontiguousarray(visible[::-1,::-1] if spec.get('rotate180') else visible)
    temporary=out/'mosaic.png.partial';Image.fromarray(np.dstack([final,opacity])).save(temporary,format='PNG',compress_level=6);temporary.replace(out/'mosaic.png')
    tifffile.imwrite(out/'subject-mask.tif',opacity,compression='deflate',metadata=None,software=False)
    print(json.dumps({'tiffBytes':dest.stat().st_size,'pngBytes':(out/'mosaic.png').stat().st_size}),flush=True)
if __name__=='__main__':main()
