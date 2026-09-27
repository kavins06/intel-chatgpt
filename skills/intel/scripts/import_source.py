#!/usr/bin/env python3
"""Index an authorized local PDF or page-text JSON without uploading it."""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

SKILL=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_id',help='Use U01, U02, etc. for your own sources. S01-S28 are reserved for exact bibliography originals.')
    parser.add_argument('--title')
    parser.add_argument('--data-dir',default=os.environ.get('INTEL_SOURCE_DIR',str(SKILL/'local-sources')))
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--pdf')
    inputs.add_argument('--pages-json',help='Array of {page:1,text:"...",method:"..."} records, for a custom source ID.')
    args=parser.parse_args()
    sid=args.source_id.upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9_-]{1,31}',sid):
        raise ValueError('Use a source ID such as U01.')
    bibliography={r['id']:r for r in json.loads((SKILL/'references/source-index.json').read_text())}
    source=Path(args.pdf or args.pages_json).expanduser().resolve()
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if sid in bibliography and (not args.pdf or digest!=bibliography[sid]['sha256']):
        raise ValueError('This reserved ID requires the exact original PDF. Use a new ID for another source or edition.')
    title=args.title or bibliography.get(sid,{}).get('title') or source.stem
    if not title.strip(): raise ValueError('Supply a non-empty title.')
    root=Path(args.data_dir).expanduser().resolve()
    index_path=root/'source-index.json'
    existing=json.loads(index_path.read_text()) if index_path.exists() else []
    if not isinstance(existing,list) or any(not isinstance(x,dict) for x in existing):
        raise ValueError('Existing local index must be an array of source objects.')
    if any(r.get('id')==sid for r in existing) or (root/(sid+'.json')).exists() or (root/(sid+'.pdf')).exists():
        raise ValueError('Source ID already exists locally; use a new ID or intentionally remove the old local entry first.')
    if args.pdf:
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ValueError('PDF import needs the optional pypdf package: python3 -m pip install pypdf. Page-text JSON import uses only the standard library.')
        reader=PdfReader(str(source))
        pages=[{'page':i+1,'text':page.extract_text() or '', 'method':'pypdf-embedded-text'} for i,page in enumerate(reader.pages)]
    else:
        pages=json.loads(source.read_text())
    if not isinstance(pages,list) or not pages or any(not isinstance(p,dict) or p.get('page')!=i+1 or not isinstance(p.get('text'),str) for i,p in enumerate(pages)):
        raise ValueError('Page data must be a non-empty array of ordered one-based pages with string text.')
    if not any(p['text'].strip() for p in pages):
        raise ValueError('No text extracted. OCR scanned pages with an authorized local tool, then import page-text JSON under a custom ID.')
    for p in pages: p.setdefault('method','user-provided-text')
    record={**bibliography.get(sid,{}),'id':sid,'title':title,'pages':len(pages),'sha256':digest,'page_data':sid+'.json','availability':'indexed_locally'}
    record.setdefault('tags',[])
    record.setdefault('limitations','User-provided local source; extraction and claim support require inspection.')
    if args.pdf: record['pdf']=sid+'.pdf'
    root.mkdir(parents=True,exist_ok=True)
    if args.pdf: shutil.copyfile(source,root/(sid+'.pdf'))
    (root/(sid+'.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n')
    temporary=index_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(existing+[record],ensure_ascii=False,indent=2)+'\n')
    temporary.replace(index_path)
    sparse=[p['page'] for p in pages if len(p['text'].strip())<80]
    print(json.dumps({'source':sid,'title':title,'pages':len(pages),'sparse_pages':sparse,'local_directory':str(root),'notice':'Local indexing only. No upload performed. Inspect sparse pages and exact extracted claims against the original.'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    try: main()
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr)
        sys.exit(2)
