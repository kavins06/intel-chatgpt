#!/usr/bin/env python3
"""Validate the public plugin structure and distribution boundaries."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from distribution import ASSETS, SKILLS, PUBLIC_EXTRAS, package_paths, read_public_file


def validate(root,check_git=True):
    root=Path(root).resolve()
    errors=[]
    paths=package_paths()
    contents={}
    for relative in paths:
        try:
            data=read_public_file(root,relative)
            if relative in ASSETS:
                if not data.startswith(b'\xff\xd8\xff') or not data.endswith(b'\xff\xd9'):
                    errors.append('Invalid JPEG asset: '+relative)
            else:
                contents[relative]=data.decode('utf-8')
        except (ValueError,OSError,UnicodeError) as exc: errors.append(str(exc))
    if errors: return errors
    try:
        manifest=json.loads(contents['plugin.json'])
        if manifest.get('name')!='intel': errors.append('Plugin name must be intel.')
        if manifest.get('$schema')!='https://agent-plugins.org/schemas/1.0.0/plugin.schema.json': errors.append('Missing portable plugin schema.')
        if not re.fullmatch(r'\d+\.\d+\.\d+',manifest.get('version','')): errors.append('Invalid semantic version.')
        interface=manifest['extensions']['com.openai']['interface']
        if not interface.get('displayName'): errors.append('Missing display name.')
        prompts=interface.get('defaultPrompt')
        if not isinstance(prompts,(str,list)) or not prompts or (isinstance(prompts,list) and (len(prompts)>3 or any(not isinstance(p,str) or not p.strip() for p in prompts))): errors.append('Invalid default prompts.')
        for key in ['logo','composerIcon']:
            if key in interface:
                target=interface[key].removeprefix('./')
                if target not in paths: errors.append('Referenced asset is outside packaging allowlist: '+target)
    except (ValueError,KeyError,TypeError) as exc: errors.append('Manifest error: '+str(exc))
    try:
        marketplace=json.loads(contents['.agents/plugins/marketplace.json'])
        if marketplace.get('name')!='intel-chatgpt': errors.append('Marketplace name must be intel-chatgpt.')
        entries=marketplace.get('plugins',[])
        if len(entries)!=1: errors.append('Marketplace must expose exactly one intel plugin.')
        for entry in entries:
            if entry.get('name')!=manifest.get('name'): errors.append('Marketplace entry must match the plugin identity.')
            if 'pluginId' in entry: errors.append('Public marketplace must not bind to an existing private plugin.')
            source=entry['source']
            path=source.get('path','')
            if source.get('source')!='local' or not path.startswith('./'):
                errors.append('Marketplace source must use a relative local path.')
            elif (root/path).resolve()!=root:
                errors.append('Marketplace source must resolve to this repository root.')
    except (ValueError,KeyError,TypeError,AttributeError) as exc: errors.append('Marketplace error: '+str(exc))
    for name in SKILLS:
        relative=f'skills/{name}/SKILL.md';text=contents[relative]
        parts=text.split('---',2)
        if len(parts)<3 or parts[0].strip():
            errors.append(name+': missing frontmatter.');continue
        front=parts[1].strip().splitlines()
        if not any(line.strip()=='name: '+name for line in front): errors.append(name+': directory and frontmatter name differ.')
        desc=next((line[len('description: '):] for line in front if line.startswith('description: ')),None)
        try:
            if not isinstance(json.loads(desc or ''),str): raise ValueError('Not a string')
        except ValueError: errors.append(name+': description must be a JSON-quoted YAML string.')
        if len(text.splitlines())>500: errors.append(name+': move long reference content out of SKILL.md.')
        ui=contents[f'skills/{name}/agents/openai.yaml']
        if '$'+name not in ui: errors.append(name+': default prompt does not target skill.')
    index=json.loads(contents['skills/intel/references/source-index.json'])
    if len(index)!=28 or len({r.get('id') for r in index})!=28: errors.append('Expected 28 unique bibliography entries.')
    for record in index:
        if record.get('availability')!='not_bundled' or any(k in record for k in ('text','page_data','pdf')):
            errors.append('Public index contains source content or a misleading availability claim.')
    for relative,text in contents.items():
        if any(marker in text for marker in ('/'+'workspace/','/'+'root/.codex/')) or re.search(r'plugins_[a-f0-9]{20,}',text):
            errors.append('Private environment or plugin identifier in '+relative)
        if relative.endswith('.md'):
            for match in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
                if match.startswith(('https://','http://','#','mailto:')): continue
                target=(root/relative).parent/match.split('#')[0]
                if not target.resolve().is_relative_to(root) or not target.exists(): errors.append(f'Broken local link in {relative}: {match}')
    if check_git and (root/'.git').exists():
        process=subprocess.run(['git','-C',str(root),'ls-files','-z'],capture_output=True,text=True)
        if process.returncode: errors.append('Unable to inspect tracked-file boundary.')
        else:
            allowed=set(paths)|set(PUBLIC_EXTRAS)|{f'downloads/intel-{manifest["version"]}.zip'}
            for filename in process.stdout.split('\0'):
                if filename and filename not in allowed: errors.append('Unapproved tracked file: '+filename)
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    errors=validate(args.root)
    print(json.dumps({'valid':not errors,'skills':len(SKILLS),'public_package_files':len(package_paths()),'errors':errors},indent=2))
    return 1 if errors else 0


if __name__=='__main__': raise SystemExit(main())
