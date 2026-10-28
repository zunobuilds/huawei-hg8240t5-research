from pathlib import Path
import unittest,tempfile,sys,json,subprocess,hashlib,zipfile
import cv2 as cv,numpy as np,tifffile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import mosaic

class Pipeline(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent);self.base=Path(self.tmp.name);self.images=self.base/'images';self.images.mkdir()
 def tearDown(self):self.tmp.cleanup()
 def fixture(self,dtype=np.uint8):
  rng=np.random.default_rng(22);im=np.full((700,900,3),180,np.uint8)
  for j in range(650):
   x,y=rng.integers([8,8],[890,690]);cv.circle(im,(int(x),int(y)),int(rng.integers(2,9)),tuple(int(v) for v in rng.integers(0,255,3)),-1)
  for k,(x,y) in enumerate([(0,0),(340,0),(0,240),(340,240)]):
   crop=im[y:y+460,x:x+560].copy()
   if dtype==np.uint16:crop=crop.astype(np.uint16)*257
   cv.imwrite(str(self.images/f'{k:03}.tif'),crop)
  return im
 def args(self,run,model='affine'):
  import argparse
  return argparse.Namespace(source=str(self.images),run=run,resume=False,preview_only=False,blend='feather',model=model,work_size=500,features=2500,neighbors=8,window=2,all_pairs=False,min_inliers=20,ratio=.72,edge_points=80,max_error=5,tile=256,cache_mb=32,max_gigapixels=.02,output_scale=1,func=None)
 def execute(self,a):
  old=mosaic.BASE;mosaic.BASE=self.base/'workspace';(mosaic.BASE/'runs').mkdir(parents=True,exist_ok=True)
  try:mosaic.build(a)
  finally:mosaic.BASE=old
  return self.base/'workspace/runs'/a.run
 def test_affine_mosaic_resume_and_stale_input(self):
  self.fixture();before={p.name:mosaic.sha(p) for p in self.images.iterdir()};a=self.args('test');r=self.execute(a)
  m=json.loads((r/'manifest.json').read_text());self.assertEqual(m['status'],'complete');self.assertGreater(m['width'],850);self.assertGreater(m['height'],650)
  with tifffile.TiffFile(r/'mosaic.tif') as t:self.assertTrue(t.is_bigtiff);self.assertTrue(t.pages[0].is_tiled)
  im=tifffile.imread(r/'mosaic.tif');mask=tifffile.imread(r/'coverage.tif');self.assertEqual(im.dtype,np.uint8);self.assertGreater((mask>0).mean(),.9)
  self.assertEqual(before,{p.name:mosaic.sha(p) for p in self.images.iterdir()});a.resume=True;self.execute(a)
  cv.imwrite(str(self.images/'new.png'),np.zeros((10,10,3),np.uint8))
  with self.assertRaisesRegex(ValueError,'Inputs/options changed'):self.execute(a)
 def test_16bit_and_tile_boundaries(self):
  self.fixture(np.uint16);r=self.execute(self.args('sixteen'));self.assertEqual(tifffile.imread(r/'mosaic.tif').dtype,np.uint16)
 def test_disconnected_refuses_to_drop_images(self):
  self.fixture();cv.imwrite(str(self.images/'blank.png'),np.zeros((300,300,3),np.uint8))
  with self.assertRaisesRegex(ValueError,'disconnected'):self.execute(self.args('bad'))
  self.assertFalse((self.base/'workspace/runs/bad/mosaic.tif').exists())
 def test_projective_model(self):
  self.fixture();a=self.args('projective','homography');r=self.execute(a);self.assertEqual(json.loads((r/'manifest.json').read_text())['status'],'complete')
 def test_import_dedup_and_zip_traversal(self):
  self.fixture();archive=self.base/'photos.zip'
  with zipfile.ZipFile(archive,'w') as z:
   z.write(self.images/'000.tif','x.tif');z.write(self.images/'000.tif','duplicate.tif')
  import argparse
  old=mosaic.BASE;mosaic.BASE=self.base/'workspace'
  try:
   mosaic.ingest(argparse.Namespace(source=str(archive),dataset='test'));self.assertEqual(len(json.loads((mosaic.BASE/'inbox/test/import.json').read_text())),1)
   bad=self.base/'bad.zip'
   with zipfile.ZipFile(bad,'w') as z:z.writestr('../escape.jpg',b'x')
   with self.assertRaisesRegex(ValueError,'Unsafe ZIP'):mosaic.ingest(argparse.Namespace(source=str(bad),dataset='bad'))
  finally:mosaic.BASE=old
 def test_preview_then_best_pixel_render(self):
  self.fixture();a=self.args('preview');a.preview_only=True;a.blend='best';r=self.execute(a)
  self.assertTrue((r/'preview.png').exists());self.assertFalse((r/'mosaic.tif').exists())
  import argparse
  old=mosaic.BASE;mosaic.BASE=self.base/'workspace'
  try:mosaic.render_saved(argparse.Namespace(run='preview'))
  finally:mosaic.BASE=old
  self.assertTrue((r/'mosaic.tif').exists());self.assertTrue(json.loads((r/'manifest.json').read_text())['fullResolutionRendered'])
 def test_geometry_rejects_foldover(self):
  self.assertFalse(mosaic.checked(np.diag([-1,1,1]),100,100));self.assertTrue(mosaic.checked(np.eye(3),100,100))

if __name__=='__main__':unittest.main()
