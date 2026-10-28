from pathlib import Path
import sys,unittest
import cv2 as cv,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mask_pcb_cached import pcb_mask
class PCBMask(unittest.TestCase):
    def test_board_plane_separate_from_green_connector_and_chip(self):
        im=np.full((300,400,3),100,np.uint8)
        im[120:280,50:350]=[0,140,0]
        im[160:240,120:250]=[15,15,15]
        im[20:60,200:250]=[0,140,0]
        im[143:147,80:110]=255
        mask=pcb_mask(im)
        self.assertGreater(mask[140,100],0)
        self.assertGreater(mask[145,100],0)
        self.assertEqual(mask[40,225],0)
        self.assertEqual(mask[200,180],0)
        self.assertEqual(mask[100,20],0)
    def test_absent_green_does_not_invent_subject(self):
        self.assertFalse(pcb_mask(np.full((100,100,3),120,np.uint8)).any())
if __name__=='__main__':unittest.main()
