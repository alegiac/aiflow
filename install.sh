#!/bin/sh
set -eu
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required" >&2; exit 1; }
exec python3 - "$@" <<'PY'
import argparse, hashlib, io, json, os, pathlib, shutil, sys, tempfile, urllib.request, zipfile
p=argparse.ArgumentParser(description="AIFlow installer (macOS/Linux)")
p.add_argument("--dev",action="store_true",help="Install current main branch for testing")
p.add_argument("--yes",action="store_true")
p.add_argument("--prefix",default=str(pathlib.Path.home()/".local/share/aiflow"))
a=p.parse_args()
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"AIFlow-installer","Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=40) as r:return r.read()
try:
    if a.dev:
        version="main (development)"
        data=get("https://codeload.github.com/alegiac/aiflow/zip/refs/heads/main")
    else:
        try: release=json.loads(get("https://api.github.com/repos/alegiac/aiflow/releases/latest"))
        except Exception as e:raise RuntimeError("No stable release available yet; use --dev to test main") from e
        version=release["tag_name"]
        assets={x["name"]:x["browser_download_url"] for x in release.get("assets",[])}
        if not {"aiflow-release.zip","aiflow-release.zip.sha256"} <= assets.keys():raise RuntimeError("Release assets missing: zip and SHA256")
        data=get(assets["aiflow-release.zip"])
        digest=get(assets["aiflow-release.zip.sha256"]).decode().split()[0].lower()
        if hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError("Checksum mismatch")
    target=pathlib.Path(a.prefix).expanduser().resolve()
    print("AIFlow",version,"| Python",sys.version.split()[0])
    for tool in ("git","codex","claude"):print(tool+":",shutil.which(tool) or "not installed")
    if sys.stdin.isatty() and not a.yes:
        entered=input("Install directory ["+str(target)+"]: ").strip()
        if entered:target=pathlib.Path(entered).expanduser().resolve()
        if input("Proceed? [y/N]: ").strip().lower() not in ("y","yes","s","si","sì"):sys.exit(0)
    with tempfile.TemporaryDirectory(prefix="aiflow-") as d:
        base=pathlib.Path(d)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for item in z.infolist():
                name=pathlib.PurePosixPath(item.filename)
                mode=item.external_attr>>16
                if name.is_absolute() or ".." in name.parts or (mode&0o170000)==0o120000:raise RuntimeError("Unsafe archive")
            z.extractall(base)
        matches=list(base.glob("*/bin/aiflow"))
        if len(matches)!=1:raise RuntimeError("Invalid archive structure")
        source=matches[0].parent.parent
        target.parent.mkdir(parents=True,exist_ok=True)
        staging=pathlib.Path(tempfile.mkdtemp(prefix=".aiflow-",dir=target.parent))
        backup=target.with_name(target.name+".previous")
        try:
            staging.rmdir()
            shutil.copytree(source,staging)
            (staging/"bin/aiflow").chmod(0o755)
            if backup.exists():shutil.rmtree(backup)
            if target.exists():target.rename(backup)
            try:staging.rename(target)
            except BaseException:
                if backup.exists():backup.rename(target)
                raise
        finally:
            if staging.exists():shutil.rmtree(staging)
    bindir=pathlib.Path.home()/".local/bin"
    bindir.mkdir(parents=True,exist_ok=True)
    link=bindir/"aiflow"
    if not link.exists() and not link.is_symlink():link.symlink_to(target/"bin/aiflow")
    print("Installed in",target)
    print('Add to PATH if needed: export PATH="$HOME/.local/bin:$PATH"')
    print("Project .ai/ directories were not modified.")
except Exception as e:
    print("AIFlow installation failed:",e,file=sys.stderr)
    sys.exit(1)
PY
