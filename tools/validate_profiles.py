#!/usr/bin/env python3
"""Validate Markdown technology profile contributions (stdlib only)."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['Ambito e rilevamento','Organizzazione del codice','Dipendenze e toolchain','Testing e qualità','Sicurezza e dati','Deployment e operatività','Interazione con AIFlow','Riferimenti']
def validate(root=ROOT):
    errors=[]
    for folder in sorted((root/'profiles').iterdir()):
        if not folder.is_dir() or folder.name=='TEMPLATE': continue
        if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',folder.name):
            errors.append(f'{folder}: slug non valido')
        file=folder/'PROFILE.md'
        if not file.is_file(): errors.append(f'{folder}: manca PROFILE.md');continue
        text=file.read_text(encoding='utf-8')
        if not text.startswith('# '):errors.append(f'{file}: manca titolo H1')
        # Older bundled profiles are accepted; new profiles follow the full template.
        if folder.name!='php-laravel':
            for section in REQUIRED:
                if not re.search(r'^## '+re.escape(section)+r'\s*$',text,re.M):
                    errors.append(f'{file}: manca sezione {section}')
            if '...' in text or '<linguaggio-framework>' in text:
                errors.append(f'{file}: placeholder non compilati')
    return errors
if __name__=='__main__':
    errors=validate()
    if errors:
        print('\n'.join(errors),file=sys.stderr);sys.exit(1)
    print('Profili validati correttamente')
