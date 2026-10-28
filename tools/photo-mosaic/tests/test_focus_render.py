from pathlib import Path
import argparse,json,tempfile,unittest,sys
import cv2 as cv
import numpy as np
import tifffile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import mosaic,focus_render

class FocusRender(unittest.TestCase):
    def test_focus_selection_resume_and_identity_guard(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);rng=np.random.default_rng(41)
            sharp=rng.integers(20,235,(256,256,3),dtype=np.uint8)
            blur=cv.GaussianBlur(sharp,(0,0),3)
            first=sharp.copy();first[:,128:]=blur[:,128:]
            second=sharp.copy();second[:,:128]=blur[:,:128]
            records=[]
            for i,im in enumerate([first,second]):
                p=root/f'{i}.png';cv.imwrite(str(p),im)
                records.append({'path':str(p),'sha256':mosaic.sha(p)})
            fs=[{'dtype':np.array('uint8')},{'dtype':np.array('uint8')}]
            matrices=[np.eye(3),np.eye(3)];a=argparse.Namespace(tile=64)
            def run(mats=matrices):
                focus_render.render(records,fs,mats,256,256,root,a,mosaic.load,mosaic.project_points,mosaic.corners,mosaic.save)
            run();out=tifffile.imread(root/'mosaic.tif')[:,:,::-1]
            interior=np.s_[20:230,20:230]
            error=np.abs(out.astype(float)-sharp).mean(2)
            baseline=np.abs(((first.astype(float)+second)/2)-sharp).mean(2)
            self.assertLess(error[interior].mean(),baseline[interior].mean()*.25)
            before=(root/'mosaic.tif').read_bytes()
            state=root/'focus-cache/checkpoint.json';s=json.loads(state.read_text());s['nextImage']=1;s['qualities']=s['qualities'][:1];mosaic.save(state,s)
            run();self.assertEqual(before,(root/'mosaic.tif').read_bytes())
            run();self.assertEqual(before,(root/'mosaic.tif').read_bytes())
            changed=[np.eye(3),np.array([[1,0,1],[0,1,0],[0,0,1]])]
            with self.assertRaisesRegex(ValueError,'identity mismatch'):run(changed)
            for r in records:self.assertEqual(mosaic.sha(r['path']),r['sha256'])

if __name__=='__main__':unittest.main()
