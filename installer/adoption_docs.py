"""Conservative project-document discovery and lossless adoption merges.

Only repository-relative paths are recorded. Originals are never moved or overwritten.
"""
from pathlib import Path
import re

SKIP={'.git','.aiflow','.ai','node_modules','vendor','.venv','venv','dist','build','.next','coverage'}
MAP={'agents.md':'AGENTS.md','claude.md':'AGENTS.md','readme.md':'project.md','architecture.md':'architecture.md','project.md':'project.md','contributing.md':'project.md'}
LIMIT=128_000
MAX_DOCS=80


def _safe_text(root, text):
    # Avoid persisting developer-specific locations in versioned project knowledge.
    text=text.replace(str(root),'.')
    text=re.sub(r'(?<![\w])/(?:Users|home)/[^/\s\x60"\x27<>]+(?:/[^\s\x60"\x27<>]*)?', '[LOCAL_PATH]', text)
    text=re.sub(r'(?i)[A-Z]:\\\\Users\\\\[^\\\\\s]+(?:\\\\[^\s]*)?', '[LOCAL_PATH]', text)
    return text


def scan(root):
    docs=[]
    for path in sorted(root.rglob('*.md')):
        rel=path.relative_to(root)
        if any(part in SKIP or part.startswith('.') for part in rel.parts[:-1]):
            continue
        if path.is_symlink() or not path.is_file() or path.stat().st_size>LIMIT:
            continue
        # Avoid arbitrary docs from deep nested dependencies or generated trees.
        if len(rel.parts)>4:
            continue
        name=path.name.lower()
        target=MAP.get(name)
        if target is None and rel.parts[0].lower() in ('docs','documentation'):
            if name in ('design.md','technical.md','system.md'): target='architecture.md'
            elif name in ('overview.md','requirements.md'): target='project.md'
        if target is None:
            continue
        docs.append({'source':rel.as_posix(),'target':target,
                     'recommendation':'merge-and-keep-source',
                     'requires_review':True})
        if len(docs)>=MAX_DOCS: break
    return docs


def merge(root, docs):
    merged=[]
    for doc in docs:
        source=root/doc['source']
        target=root/'.aiflow'/doc['target']
        if not source.is_file() or source.is_symlink():
            continue
        text=_safe_text(root,source.read_text(encoding='utf-8')).strip()
        if not text:
            continue
        # Idempotent, isolated source section; project instructions take precedence.
        start='<!-- aiflow:adopt:'+doc['source']+':start -->'
        end='<!-- aiflow:adopt:'+doc['source']+':end -->'
        block=start+'\n## Existing project document: '+doc['source']+' (authoritative)\n\n'+text+'\n'+end
        existing=target.read_text(encoding='utf-8') if target.exists() else ''
        if start in existing and end in existing:
            before,tail=existing.split(start,1)
            _,after=tail.split(end,1)
            updated=before+block+after
        else:
            updated=existing.rstrip()+'\n\n'+block+'\n'
        if updated!=existing:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(updated,encoding='utf-8')
        merged.append(doc['source'])
    return merged
