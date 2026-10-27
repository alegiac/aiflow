"""Project-scoped daily digest: durable HTML/text report and best-effort SMTP."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import smtplib
import sqlite3
import ssl
from email.message import EmailMessage
from zoneinfo import ZoneInfo

CLOSED = {'done', 'completed', 'closed', 'finished'}
def local_day(value, timezone):
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(timezone).date()
    except (ValueError, TypeError):
        return None

def tables(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def rows(db, sql):
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error:
        return []

def snapshot(db, date, timezone):
    day = dt.date.fromisoformat(date)
    tz = ZoneInfo(timezone)
    events = [(when, kind, ref, details) for when, kind, ref, details in rows(db, 'SELECT created_at,kind,ref,details FROM events ORDER BY created_at') if local_day(when,tz)==day]
    activities = rows(db, 'SELECT epic_id,task_id,started_at,ended_at FROM activities')
    minutes = 0
    worked = set()
    tracked = []
    for epic, task, start, end in activities:
        if not start:
            continue
        try:
            a=dt.datetime.fromisoformat(start.replace('Z','+00:00'))
            b=dt.datetime.fromisoformat(end.replace('Z','+00:00')) if end else dt.datetime.now(dt.timezone.utc)
            if a.tzinfo is None: a=a.replace(tzinfo=dt.timezone.utc)
            if b.tzinfo is None: b=b.replace(tzinfo=dt.timezone.utc)
            start_of_day=dt.datetime.combine(day,dt.time.min,tz).astimezone(dt.timezone.utc)
            end_of_day=start_of_day+dt.timedelta(days=1)
            overlap=max(0,(min(b,end_of_day)-max(a,start_of_day)).total_seconds())
            if overlap:
                minutes+=overlap/60
                if task: worked.add((epic,task))
                tracked.append({'epic':epic,'task':task,'minutes':round(overlap/60,1),'open':not bool(end)})
        except (ValueError,TypeError):
            continue
    epics=rows(db,'SELECT id,title,status,created_at,updated_at FROM epics')
    tasks=rows(db,'SELECT epic_id,id,title,status,created_at,updated_at FROM tasks')
    for when,kind,ref,_ in events:
        if kind.startswith(('task.', 'workflow-task', 'track.')) and ref and '/' in ref:
            parts=ref.split('/')
            if len(parts)>=2: worked.add((parts[0],parts[1]))
    return {
        'date':date,'minutes':round(minutes,1),'tracking':tracked,
        'events':[{'time':w,'kind':k,'ref':r,'details':d} for w,k,r,d in events],
        'epics':{'created':[{'id':e[0],'title':e[1]} for e in epics if local_day(e[3],tz)==day],
                 'updated':[{'id':e[0],'title':e[1],'status':e[2]} for e in epics if local_day(e[4],tz)==day],
                 'open':[{'id':e[0],'title':e[1],'status':e[2]} for e in epics if e[2].lower() not in CLOSED],
                 'closed_today':[{'id':e[0],'title':e[1]} for e in epics if e[2].lower() in CLOSED and local_day(e[4],tz)==day]},
        'tasks':{'created':[{'id':e[0]+'/'+e[1],'title':e[2]} for e in tasks if local_day(e[4],tz)==day],
                 'worked':[{'id':e[0]+'/'+e[1],'title':e[2],'status':e[3]} for e in tasks if (e[0],e[1]) in worked or local_day(e[5],tz)==day],
                 'open':[{'id':e[0]+'/'+e[1],'title':e[2],'status':e[3]} for e in tasks if e[3].lower() not in CLOSED],
                 'closed_today':[{'id':e[0]+'/'+e[1],'title':e[2]} for e in tasks if e[3].lower() in CLOSED and local_day(e[5],tz)==day]},
    }

def render(project, data):
    def section(title, items, formatter):
        if not items: return '<p class="muted">Nessun elemento registrato.</p>'
        return '<ul>'+''.join('<li>'+formatter(x)+'</li>' for x in items)+'</ul>'
    esc=lambda x:html.escape(str(x or ''))
    events=data['events']
    decisions=[e for e in events if 'decision' in e['kind']]
    approvals=[e for e in events if 'approv' in e['kind'] or e['kind'].startswith('approve')]
    checkpoints=[e for e in events if 'checkpoint' in e['kind'] or e['kind']=='day.end']
    format_event=lambda e:'<strong>'+esc(e['kind'])+'</strong> · '+esc(e['ref'])+' — '+esc(e['details'])
    format_item=lambda e:'<strong>'+esc(e['id'])+'</strong> · '+esc(e['title'])+(' ('+esc(e['status'])+')' if 'status' in e else '')
    cards=[('Tempo tracciato',f"{int(data['minutes']//60)}h {int(data['minutes']%60):02d}m"),('Task lavorati',len(data['tasks']['worked'])),('Task chiusi',len(data['tasks']['closed_today'])),('Epic aggiornati',len(data['epics']['updated']))]
    cardhtml=''.join('<div class="metric"><span>'+esc(k)+'</span><b>'+esc(v)+'</b></div>' for k,v in cards)
    sections=[('Epic creati',data['epics']['created'],format_item),('Epic lavorati / aggiornati',data['epics']['updated'],format_item),('Epic chiusi oggi',data['epics']['closed_today'],format_item),('Epic ancora aperti',data['epics']['open'],format_item),('Task creati',data['tasks']['created'],format_item),('Task lavorati',data['tasks']['worked'],format_item),('Task chiusi oggi',data['tasks']['closed_today'],format_item),('Task ancora aperti',data['tasks']['open'],format_item),('Decisioni registrate oggi',decisions,format_event),('Approvazioni registrate oggi',approvals,format_event),('Checkpoint e chiusura',checkpoints,format_event),('Cronologia eventi',events,format_event)]
    body=''.join('<section><h2>'+esc(title)+'</h2>'+section(title,items,formatter)+'</section>' for title,items,formatter in sections)
    markup='''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;background:#f1f5f9;color:#17263d;font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}.wrap{max-width:760px;margin:auto;background:#fff}.hero{background:#14263c;color:#fff;padding:30px}.hero p{color:#c7d7ea}.content{padding:24px}.metrics{display:flex;flex-wrap:wrap;gap:10px}.metric{background:#eef3f8;padding:16px;min-width:120px;flex:1;border-radius:10px}.metric span{display:block;color:#52647a;font-size:12px}.metric b{display:block;font-size:25px;margin-top:6px}section{border-top:1px solid #e4eaf1;margin-top:22px;padding-top:12px}h2{font-size:17px}li{margin:9px 0;overflow-wrap:anywhere}.muted{color:#6b7788}.foot{color:#6b7788;font-size:12px;padding:22px}@media(max-width:480px){.hero,.content{padding:18px}.metric{min-width:110px}}</style></head><body><div class="wrap"><div class="hero"><h1>AIFlow · Daily Digest</h1><p>PROJECT · DATE</p></div><div class="content"><div class="metrics">CARDS</div>SECTIONS</div><div class="foot">Generato da AIFlow · Solo dati registrati localmente. I tempi non tracciati non sono stimati.</div></div></body></html>'''
    page=markup.replace('PROJECT',esc(project)).replace('DATE',esc(data['date'])).replace('CARDS',cardhtml).replace('SECTIONS',body)
    lines=[f"AIFlow Daily Digest — {project} — {data['date']}",f"Tempo tracciato: {data['minutes']:.1f} minuti",f"Task lavorati: {len(data['tasks']['worked'])}; chiusi: {len(data['tasks']['closed_today'])}; aperti: {len(data['tasks']['open'])}",f"Epic aggiornati: {len(data['epics']['updated'])}; aperti: {len(data['epics']['open'])}"]
    for title,items,_ in sections:
        lines.append('\n'+title+':')
        lines.extend(' - '+(str(x.get('id'))+' '+str(x.get('title')) if 'id' in x else str(x.get('kind'))+' '+str(x.get('ref'))+' '+str(x.get('details'))) for x in items)
    return page,'\n'.join(lines)+'\n'

def send_mail(project,date,page,plain):
    required=('AIFLOW_SMTP_HOST','AIFLOW_SMTP_USER','AIFLOW_SMTP_PASSWORD','AIFLOW_MAIL_TO')
    missing=[k for k in required if not os.environ.get(k)]
    if missing: return 'not_configured', 'Missing '+', '.join(missing)
    msg=EmailMessage()
    msg['Subject']=f'[AIFlow] {project} — Daily Digest — {date}'
    msg['From']=os.environ.get('AIFLOW_MAIL_FROM',os.environ['AIFLOW_SMTP_USER'])
    msg['To']=os.environ['AIFLOW_MAIL_TO']
    msg.set_content(plain)
    msg.add_alternative(page,subtype='html')
    try:
        host=os.environ['AIFLOW_SMTP_HOST'];port=int(os.environ.get('AIFLOW_SMTP_PORT','465'))
        with smtplib.SMTP_SSL(host,port,context=ssl.create_default_context(),timeout=30) as smtp:
            smtp.login(os.environ['AIFLOW_SMTP_USER'],os.environ['AIFLOW_SMTP_PASSWORD'])
            smtp.send_message(msg)
        return 'sent',None
    except (OSError,smtplib.SMTPException,ValueError) as exc:
        return 'failed',str(exc)

def generate(root,db,date,send=True):
    """Persist report before sending; never let SMTP failures break day end."""
    state=root/'.aiflow'/'state'/'digest'
    state.mkdir(parents=True,exist_ok=True)
    timezone=os.environ.get('AIFLOW_DIGEST_TIMEZONE','Europe/Rome')
    data=snapshot(db,date,timezone)
    page,plain=render(root.name,data)
    (state/(date+'.html')).write_text(page,encoding='utf-8')
    (state/(date+'.txt')).write_text(plain,encoding='utf-8')
    ledger=state/(date+'.json')
    try: previous=json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {}
    except (OSError,ValueError): previous={}
    if not send: status='skipped';error=None
    elif previous.get('status')=='sent': status='already_sent';error=None
    else: status,error=send_mail(root.name,date,page,plain)
    if status!='already_sent':
        ledger.write_text(json.dumps({'date':date,'status':status,'error':error},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'digest':str(state/(date+'.html')),'mail_status':status,'mail_error':error}
