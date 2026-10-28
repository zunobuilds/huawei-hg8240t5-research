from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prune_refinement import connected_filter
class PruneGraph(unittest.TestCase):
    def test_redundant_edge_can_be_rejected_without_dropping_images(self):
        edges=[{'i':0,'j':1},{'i':1,'j':2},{'i':0,'j':2}]
        result=connected_filter(3,edges,{(0,2)})
        self.assertEqual(len(result),2);self.assertEqual(len(edges),3)
    def test_bridge_rejection_is_blocked(self):
        with self.assertRaisesRegex(ValueError,'disconnects'):connected_filter(3,[{'i':0,'j':1},{'i':1,'j':2}],{(1,2)})
if __name__=='__main__':unittest.main()
