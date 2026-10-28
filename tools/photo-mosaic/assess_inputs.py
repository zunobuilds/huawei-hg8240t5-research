"""Read-only JPEG proxy quality assessment; scores are indicators, not diagnoses."""
from pathlib import Path
import argparse,json,hashlib
from concurrent.futures import ThreadPoolExecutor
import cv2 as cv
import numpy as np

def assess(path):
    im=cv.imread(str(path),cv.IMREAD_REDUCED_COLOR_4)
    if im is None:raise ValueError(f'Cannot decode {path}')
    gray=cv.cvtColor(im,cv.COLOR_BGR2GRAY)
    dh=cv.resize(gray,(17,16));bits=dh[:,1:]>dh[:,:-1]
    return {'path':str(path),'proxyShape':list(im.shape[:2]),'laplacianVariance':float(cv.Laplacian(gray,cv.CV_32F).var()),'clippedHighlightFraction':float((np.min(im,axis=2)>=250).mean()),'dHash256':np.packbits(bits).tobytes().hex()}

def main():
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--output',required=True);a=p.parse_args();cv.setNumThreads(1)
    paths=sorted(x for x in Path(a.source).rglob('*') if x.suffix.lower() in ['.jpg','.jpeg'])
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(assess,paths))
    scores=np.array([r['laplacianVariance'] for r in rows]);cut=float(np.percentile(scores,10))
    groups={}
    for i,r in enumerate(rows):groups.setdefault(r['dHash256'],[]).append(i)
    result={'images':rows,'relativeLowDetailThreshold':cut,'relativeLowDetailIndices':[i for i,r in enumerate(rows) if r['laplacianVariance']<=cut],'matchingProxyHashGroups':[g for g in groups.values() if len(g)>1],'warning':'Reduced-image focus and perceptual-hash indicators are scene-dependent. Matching hashes are not proof of identical original bytes; no inputs are discarded by this assessment.'}
    out=Path(a.output);temp=out.with_suffix('.json.tmp');temp.write_text(json.dumps(result,indent=2)+'\n');temp.replace(out)
    print(json.dumps({'assessed':len(rows),'relativeLowDetail':len(result['relativeLowDetailIndices']),'matchingProxyHashGroups':len(result['matchingProxyHashGroups'])}))
if __name__=='__main__':main()
