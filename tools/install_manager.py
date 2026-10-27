#!/usr/bin/env python3
"""Install/upgrade AIFlow from verified GitHub release assets (stdlib only)."""
import argparse
import hashlib
import json
import shutil as _shutil
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

REPO="alegiac/aiflow"
API=f"https://api.github.com/repos/{REPO}/releases/latest"
USER_AGENT="AIFlow-Installer/1.2"
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=25) as response:
        return response.read()
def release():
    data=json.loads(fetch(API))
    asset=next((x for x in data.get("assets",[]) if x["name"]=="aiflow-release.zip"),None)
    checksum=next((x for x in data.get("assets",[]) if x["name"]=="aiflow-release.zip.sha256"),None)
    if not asset or not checksum:
        raise RuntimeError("Release incompleta: richiesti aiflow-release.zip e aiflow-release.zip.sha256")
    return data,asset,checksum
def unpack_safe(data,destination):
    archive=destination/"download.zip";archive.write_bytes(data)
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            path=Path(entry.filename)
            if path.is_absolute() or ".." in path.parts or entry.is_dir() and not entry.filename.endswith("/"):
                raise RuntimeError("Archivio con percorso non sicuro")
            if (entry.external_attr>>16)&0o170000 == 0o120000:
                raise RuntimeError("Symlink non consentiti nel pacchetto")
        z.extractall(destination/"extract")
    matches=list((destination/"extract").rglob("bin/aiflow"))
    if len(matches)!=1:
        raise RuntimeError("Pacchetto non valido: atteso un solo bin/aiflow")
    return matches[0].parents[1]
def wizard(args, target, tag):
    print("\n╔════════════════════════════════════════╗")
    print("║        AIFlow Setup Assistant          ║")
    print("╚════════════════════════════════════════╝\n")
    print("Python:", sys.version.split()[0])
    for tool in ("git", "codex", "claude"):
        print(f"{tool:7}:", _shutil.which(tool) or "non rilevato")
    if not args.yes and sys.stdin.isatty():
        proposed = input(f"\nDirectory [{target}]: ").strip()
        if proposed:
            target=Path(proposed).expanduser().resolve()
        if args.action == "install":
            print("\nAgenti: 1) Codex  2) Claude  3) Entrambi  4) Nessuno")
            selected=input("Scelta [3]: ").strip() or "3"
            agents={"1":"codex","2":"claude","3":"both","4":"none"}.get(selected)
            if agents is None: raise RuntimeError("Scelta agenti non valida")
            print("Integrazione agenti: esegui `aiflow integrate " + agents + "` in ogni progetto inizializzato.") if agents != "none" else None
            daily=input("Vuoi configurare un riepilogo quotidiano? [s/N]: ").strip().lower()
            if daily in ('s','si','sì','y','yes'):
                print("Per la mail configura SMTP e launchd seguendo DAILY_DIGEST.md; nessuna credenziale richiesta qui.")
        print(f"\nOperazione: {args.action} | release {tag} | destinazione {target}")
    return target

def execute():
    parser=argparse.ArgumentParser(description="AIFlow install / upgrade from GitHub Releases")
    parser.add_argument("action",choices=["install","upgrade","check"])
    parser.add_argument("--prefix",default=os.environ.get("AIFLOW_INSTALL_DIR",str(Path.home()/".local/share/aiflow")))
    parser.add_argument("--yes",action="store_true",help="Non-interactive install/upgrade")
    args=parser.parse_args()
    target=Path(args.prefix).expanduser().resolve()
    data,asset,checksum=release()
    tag=data.get("tag_name","unknown")
    print("Release GitHub:",tag)
    if args.action=="check":return
    target=wizard(args,target,tag)
    if args.action=="install" and target.exists(): raise RuntimeError(f"Già installato: {target}. Usa upgrade.")
    if args.action=="upgrade" and not (target/"bin/aiflow").is_file(): raise RuntimeError(f"Installazione assente: {target}. Usa install.")
    if not args.yes and sys.stdin.isatty() and input("Procedere? [s/N]: ").lower() not in ("s","si","sì","y","yes"):return
    with tempfile.TemporaryDirectory(prefix="aiflow-install-") as td:
        tmp=Path(td)
        content=fetch(asset["browser_download_url"])
        expected=fetch(checksum["browser_download_url"]).decode().split()[0].lower()
        actual=hashlib.sha256(content).hexdigest()
        if expected!=actual: raise RuntimeError("SHA256 non corrispondente: installazione annullata")
        candidate=unpack_safe(content,tmp)
        subprocess.run([sys.executable,"-m","compileall","-q",str(candidate/"bin"),str(candidate/"installer")],check=True)
        # install to sibling staging dir; rollback on failure
        target.parent.mkdir(parents=True,exist_ok=True)
        staging=Path(tempfile.mkdtemp(prefix=".aiflow-new-",dir=target.parent))
        backup=target.with_name(target.name+".previous")
        try:
            shutil.rmtree(staging)
            shutil.copytree(candidate,staging,ignore=shutil.ignore_patterns("__pycache__","*.pyc",".git"))
            (staging/"bin/aiflow").chmod(0o755)
            if backup.exists():shutil.rmtree(backup)
            if target.exists():target.rename(backup)
            try:staging.rename(target)
            except Exception:
                if backup.exists():backup.rename(target)
                raise
        finally:
            if staging.exists():shutil.rmtree(staging)
    print(f"Installato {tag} in {target}")
    print(f'Aggiungi al PATH: export PATH="{target}/bin:$PATH"')
    print("I progetti (.ai/) non sono stati modificati.")
    print("Dopo upgrade, dentro ogni progetto: aiflow integrate both")
if __name__=="__main__":
    try:execute()
    except Exception as e:
        print("Errore installazione:",e,file=sys.stderr)
        sys.exit(1)
