from pathlib import Path
import io,sys,tarfile,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import import_tar

class TarIntake(unittest.TestCase):
    def archive(self,path,name,data=b'original'):
        with tarfile.open(path,'w:gz') as out:
            member=tarfile.TarInfo(name);member.size=len(data);out.addfile(member,io.BytesIO(data))
    def test_resume_and_conflicting_original(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);archive=root/'photos.tar.gz';dest=root/'intake'
            self.archive(archive,'set/frame.jpg')
            first=import_tar.extract(archive,dest);before=import_tar.digest(archive)
            second=import_tar.extract(archive,dest)
            self.assertEqual(first,second);self.assertEqual(before,import_tar.digest(archive))
            original=dest/'raw/set/frame.jpg';self.assertEqual(original.read_bytes(),b'original')
            self.archive(archive,'set/frame.jpg',b'different')
            with self.assertRaisesRegex(ValueError,'not overwritten'):import_tar.extract(archive,dest)
            self.assertEqual(original.read_bytes(),b'original')
    def test_traversal_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);archive=root/'photos.tar.gz';dest=root/'intake'
            self.archive(archive,'../escape.jpg')
            with self.assertRaisesRegex(ValueError,'Unsafe'):import_tar.extract(archive,dest)
            self.assertFalse((root/'escape.jpg').exists())
            with tarfile.open(archive,'w:gz') as out:
                member=tarfile.TarInfo('link');member.type=tarfile.SYMTYPE;member.linkname='/tmp';out.addfile(member)
            with self.assertRaisesRegex(ValueError,'Unsafe'):import_tar.extract(archive,dest)
if __name__=='__main__':unittest.main()
