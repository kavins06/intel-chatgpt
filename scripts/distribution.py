"""Explicit allowlist shared by validation and reproducible public packaging."""
from pathlib import Path

SKILLS=('intel','intel-research','intel-diagnose','intel-compete','intel-stakeholders','intel-foresight','intel-innovate','intel-risk','intel-red-team','intel-brief')
REFERENCES=('case-lessons.md','evidence-standards.md','method-map.md','method-notes.md','source-catalog.md','source-index.json','templates.md')
ROOT_FILES=('plugin.json','README.md','LICENSE','SOURCE_NOTICE.md','.gitignore','.gitattributes')
TOOLING=('scripts/distribution.py','scripts/validate.py','scripts/package.py','tests/test_tooling.py')
DOCS=('docs/local-sources.md','docs/examples.md')
RUNTIME=('check_evidence.py','source_library.py','import_source.py')
PUBLIC_EXTRAS=('.github/workflows/validate.yml',)


def package_paths():
    paths=list(ROOT_FILES+TOOLING+DOCS)
    for name in SKILLS:
        paths.extend([f'skills/{name}/SKILL.md',f'skills/{name}/agents/openai.yaml'])
    paths.extend('skills/intel/references/'+name for name in REFERENCES)
    paths.extend('skills/intel/scripts/'+name for name in RUNTIME)
    return sorted(paths)


def read_public_file(root,relative):
    root=Path(root).resolve()
    path=root/relative
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('Public files must be regular files inside the repository: '+relative)
    if not path.is_file():
        raise ValueError('Missing public file: '+relative)
    if path.stat().st_size>100000:
        raise ValueError('Unexpectedly large public text file: '+relative)
    return path.read_bytes()
