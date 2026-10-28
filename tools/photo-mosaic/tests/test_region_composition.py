from pathlib import Path
import tempfile,sys,json,subprocess,hashlib,unittest
import cv2 as cv,numpy as np,tifffile
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from compose_regions import compose
class RegionComposition(unittest.TestCase):
    def test_rgb_order_and_unchanged_outside_patch(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);base=np.full((64,80,3),40,np.uint8);tifffile.imwrite(root/'base.tif',base,metadata=None)
            patch=np.full((12,20,3),[200,80,30],np.uint8);cv.imwrite(str(root/'patch.png'),patch[:,:,::-1])
            (root/'patch.json').write_text(json.dumps({'roiXYWH':[110,210,20,12]}))
            spec={'metadata':str(root/'patch.json'),'file':str(root/'patch.png'),'selection':'synthetic fixture','polygon':[[0,0],[1,0],[1,1],[0,1]],'feather':2}
            before=hashlib.file_digest((root/'base.tif').open('rb'),'sha256').hexdigest()
            result,_=compose(root/'base.tif',[spec],[100,200,80,64],root/'result')
            self.assertTrue(np.array_equal(result[10:22,10:30],patch))
            outside=np.ones((64,80),bool);outside[10:22,10:30]=False
            self.assertTrue(np.array_equal(result[outside],base[outside]))
            self.assertEqual(before,hashlib.file_digest((root/'base.tif').open('rb'),'sha256').hexdigest())
    def test_lossless_export_rotation_trim_and_alpha(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);base=np.random.default_rng(7).integers(0,255,(64,80,3),dtype=np.uint8);tifffile.imwrite(root/'base.tif',base,metadata=None)
            spec={'base':str(root/'base.tif'),'patches':[],'cropXYWH':[0,0,80,64],'output':str(root/'out'),'trimTop':4,'rotate180':True,'foregroundPolygons':[[[20,20],[60,20],[60,50],[20,50]]]}
            (root/'spec.json').write_text(json.dumps(spec))
            subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'compose_regions.py'),str(root/'spec.json')],check=True,capture_output=True)
            rgb=tifffile.imread(root/'out/mosaic.tif');png=np.array(Image.open(root/'out/mosaic.png'))
            self.assertEqual(rgb.shape,(60,80,3));self.assertTrue(np.array_equal(rgb,png[:,:,:3]))
            expected=base[4:][::-1,::-1];self.assertTrue(np.array_equal(rgb[png[:,:,3]>0],expected[png[:,:,3]>0]))
            self.assertTrue(np.all(rgb[png[:,:,3]==0]==0));self.assertTrue((png[:,:,3]==0).any())
if __name__=='__main__':unittest.main()
