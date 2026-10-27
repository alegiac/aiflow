#!/usr/bin/env python3
"""Daily summary across local AIFlow projects. No cloud data upload."""
import argparse, datetime as dt, os, sqlite3, smtplib, ssl
from pathlib import Path
from email.message import EmailMessage
from zoneinfo import ZoneInfo

def report(root, day, tz):
    result=[]
    for dbfile in root.rglob('.aiflow/state/aiflow.sqlite3'):
        project=dbfile.parents[2]
        try:
            db=sqlite3.connect(f"file:{dbfile}?mode=ro",uri=True)
            rows=db.execute("SELECT created_at,kind,ref,details FROM events ORDER BY created_at").fetchall()
            selected=[]
            for when,kind,ref,details in rows:
                try:
                    local=dt.datetime.fromisoformat(when.replace('Z','+00:00')).astimezone(tz).date()
                except ValueError: continue
                if local==day: selected.append((when,kind,ref,details))
            if selected:
                result.append(f"\n## {project.name} ({len(selected)} eventi)")
                for _,kind,ref,details in selected:
                    result.append(f"- {kind} | {ref or '-'} | {(details or '')[:220]}")
            db.close()
        except (sqlite3.Error,OSError) as exc:
            result.append(f"\n## {project.name}\n- ERRORE lettura: {exc}")
    return '\n'.join(result) or "Nessuna attività AIFlow registrata nella giornata."

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--projects-root',default=str(Path.home()/'Development'))
    p.add_argument('--date',help='YYYY-MM-DD (default oggi)')
    p.add_argument('--timezone',default='Europe/Rome')
    p.add_argument('--send',action='store_true')
    a=p.parse_args()
    tz=ZoneInfo(a.timezone)
    day=dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(tz).date()
    body=f"AIFlow — Riepilogo {day.isoformat()}\n"+report(Path(a.projects_root).expanduser(),day,tz)
    print(body)
    if not a.send:return
    keys=['AIFLOW_SMTP_HOST','AIFLOW_SMTP_USER','AIFLOW_SMTP_PASSWORD','AIFLOW_MAIL_TO']
    missing=[k for k in keys if not os.environ.get(k)]
    if missing: raise SystemExit('Configurazione SMTP mancante: '+', '.join(missing))
    msg=EmailMessage()
    msg['Subject']=f"AIFlow — Riepilogo {day.isoformat()}"
    msg['From']=os.environ.get('AIFLOW_MAIL_FROM',os.environ['AIFLOW_SMTP_USER'])
    msg['To']=os.environ['AIFLOW_MAIL_TO']
    msg.set_content(body)
    host=os.environ['AIFLOW_SMTP_HOST'];port=int(os.environ.get('AIFLOW_SMTP_PORT','465'))
    with smtplib.SMTP_SSL(host,port,context=ssl.create_default_context(),timeout=30) as smtp:
        smtp.login(os.environ['AIFLOW_SMTP_USER'],os.environ['AIFLOW_SMTP_PASSWORD'])
        smtp.send_message(msg)
if __name__=='__main__':main()
