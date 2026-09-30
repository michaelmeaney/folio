#!/usr/bin/env python3
"""Build native benchmark archives and SHA-256 checksums; no generation calls."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import zipfile

TARGETS = [('darwin','arm64'),('darwin','amd64'),('linux','amd64'),('linux','arm64'),('windows','amd64')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='dist/folio-bench-release')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    output=Path(args.output).resolve()
    output.mkdir(parents=True,exist_ok=True)
    checksums=[]
    for system,arch in TARGETS:
        with tempfile.TemporaryDirectory(prefix='folio-bench-build-') as temp:
            binary=Path(temp)/('folio-bench.exe' if system=='windows' else 'folio-bench')
            env=dict(os.environ,GOOS=system,GOARCH=arch,CGO_ENABLED='0')
            subprocess.run(['go','build','-trimpath','-o',str(binary),'./cmd/folio-bench'],cwd=root,env=env,check=True)
            suffix='.zip' if system=='windows' else '.tar.gz'
            archive=output/f'folio-bench-{system}-{arch}{suffix}'
            if system=='windows':
                with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as stream:
                    stream.write(binary,binary.name)
            else:
                with tarfile.open(archive,'w:gz') as stream:
                    stream.add(binary,arcname=binary.name)
            checksums.append(f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}')
            print(archive)
    (output/'SHA256SUMS').write_text('\n'.join(checksums)+'\n')


if __name__=='__main__':
    main()
