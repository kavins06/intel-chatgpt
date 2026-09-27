#!/usr/bin/env python3
"""Build a deterministic public archive; private sources cannot enter the allowlist."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from distribution import package_paths,read_public_file
from validate import validate


def build(root,output):
    root=Path(root).resolve();output=Path(output).resolve()
    errors=validate(root)
    if errors: raise ValueError('\n'.join(errors))
    if output in [(root/x).resolve() for x in package_paths()]: raise ValueError('Output cannot overwrite a package source file.')
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for relative in package_paths():
            info=zipfile.ZipInfo('intel/'+relative,date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3
            info.external_attr=0o100644<<16
            archive.writestr(info,read_public_file(root,relative))
    temp.replace(output)
    return {'archive':str(output),'files':len(package_paths()),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}


def main():
    root=Path(__file__).resolve().parents[1]
    version=json.loads((root/'plugin.json').read_text())['version']
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=root/'dist'/f'intel-{version}.zip')
    args=parser.parse_args()
    try: print(json.dumps(build(root,args.output),indent=2));return 0
    except (ValueError,OSError) as exc: print(json.dumps({'error':str(exc)}));return 1


if __name__=='__main__': raise SystemExit(main())
