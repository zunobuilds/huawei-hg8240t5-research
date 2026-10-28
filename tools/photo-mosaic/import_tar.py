"""Safe, resumable TAR image intake; source archive is opened read-only."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,tarfile

def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def extract(source,destination):
    destination=Path(destination).resolve();raw=destination/'raw';raw.mkdir(parents=True,exist_ok=True)
    entries=[];total=0
    with tarfile.open(source,'r:*') as archive:
        for member in archive:
            rel=PurePosixPath(member.name)
            if rel.is_absolute() or '..' in rel.parts or member.issym() or member.islnk():raise ValueError('Unsafe archive path/link')
            if member.isdir():continue
            if not member.isfile():raise ValueError('Special archive entries are not supported')
            total+=member.size
            if member.size>1_000_000_000 or total>100_000_000_000 or len(entries)>=20000:raise ValueError('Archive limits exceeded')
            path=raw/str(rel)
            if not path.resolve().is_relative_to(raw.resolve()) or path.is_symlink():raise ValueError('Destination escapes raw input directory')
            path.parent.mkdir(parents=True,exist_ok=True)
            checksum=hashlib.sha256();temporary=path.with_name(path.name+'.partial')
            if temporary.is_symlink():raise ValueError('Symlink temporary output rejected')
            exists=path.exists()
            with archive.extractfile(member) as inp:
                output=None if exists else temporary.open('wb')
                try:
                    for block in iter(lambda:inp.read(1024*1024),b''):
                        checksum.update(block)
                        if output:output.write(block)
                finally:
                    if output:output.close()
            if exists:
                if path.stat().st_size!=member.size or digest(path)!=checksum.hexdigest():raise ValueError('Existing original differs from archive; not overwritten')
            else:
                if temporary.stat().st_size!=member.size:raise ValueError('Truncated archive member')
                temporary.replace(path)
            entries.append({'file':str(path),'entry':member.name,'bytes':member.size,'sha256':checksum.hexdigest()})
            if len(entries)%50==0:print(json.dumps({'stage':'extract','files':len(entries),'bytes':total}),flush=True)
    result={'sourceArchive':str(Path(source).resolve()),'archiveBytes':Path(source).stat().st_size,'files':entries}
    temporary=destination/'manifest.json.tmp';temporary.write_text(json.dumps(result,indent=2)+'\n');temporary.replace(destination/'manifest.json')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--destination',required=True);a=p.parse_args()
    result=extract(Path(a.source),Path(a.destination));print(json.dumps({'files':len(result['files']),'manifest':str(Path(a.destination)/'manifest.json')}))
if __name__=='__main__':main()
