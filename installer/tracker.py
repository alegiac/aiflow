"""Opt-in Jira REST bridge; remote writes are explicit and idempotent."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import urllib.parse
import urllib.error
import urllib.request
import base64


def _request(method, path, payload=None):
    base=os.environ.get('AIFLOW_JIRA_URL','').rstrip('/')
    email=os.environ.get('AIFLOW_JIRA_EMAIL','')
    token=os.environ.get('AIFLOW_JIRA_TOKEN','')
    if not base or not email or not token:
        raise ValueError('Set AIFLOW_JIRA_URL, AIFLOW_JIRA_EMAIL and AIFLOW_JIRA_TOKEN in environment')
    if not base.startswith('https://'): raise ValueError('Jira URL must use HTTPS')
    auth=base64.b64encode((email+':'+token).encode()).decode()
    data=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(base+'/rest/api/3/'+path,method=method,data=data,headers={'Authorization':'Basic '+auth,'Accept':'application/json','Content-Type':'application/json','User-Agent':'AIFlow/1.4'})
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            body=resp.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise ValueError('Jira HTTP '+str(e.code)) from e


def _schema(db):
    db.execute('CREATE TABLE IF NOT EXISTS tracker_mappings(local_id TEXT PRIMARY KEY,remote_key TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS tracker_worklogs(activity_id INTEGER PRIMARY KEY,remote_key TEXT NOT NULL,remote_id TEXT NOT NULL,seconds INTEGER NOT NULL)')
    db.commit()


def tracker_command(root,db,args):
    _schema(db)
    if args.action=='status':
        print('Jira configured:',bool(all(os.environ.get(k) for k in ('AIFLOW_JIRA_URL','AIFLOW_JIRA_EMAIL','AIFLOW_JIRA_TOKEN'))))
        for a,b in db.execute('SELECT local_id,remote_key FROM tracker_mappings ORDER BY local_id'):print(a,'=>',b)
        return
    if args.action=='map':
        if not args.local_id or not args.remote_key:raise ValueError('IDs required')
        db.execute('INSERT INTO tracker_mappings(local_id,remote_key) VALUES(?,?) ON CONFLICT(local_id) DO UPDATE SET remote_key=excluded.remote_key',(args.local_id,args.remote_key))
        db.commit()
        print('Mapped',args.local_id,'=>',args.remote_key)
        return
    if args.action=='pull':
        data=_request('GET','issue/'+urllib.parse.quote(args.remote_key,safe=''))
        fields=data.get('fields',{})
        print(json.dumps({'key':data.get('key'),'summary':fields.get('summary'),'status':(fields.get('status') or {}).get('name')},ensure_ascii=False,indent=2))
        return
    if args.action=='worklog':
        row=db.execute('SELECT epic_id,task_id,started_at,ended_at FROM activities WHERE id=?',(args.activity_id,)).fetchone()
        if not row:raise ValueError('Activity not found')
        epic,task,start,end=row
        if not end:raise ValueError('Stop activity before worklog')
        local=epic+'/'+task if epic and task else None
        if not local:raise ValueError('Activity needs epic and task')
        mapping=db.execute('SELECT remote_key FROM tracker_mappings WHERE local_id=?',(local,)).fetchone()
        if not mapping:raise ValueError('Map local task to Jira issue first')
        if db.execute('SELECT 1 FROM tracker_worklogs WHERE activity_id=?',(args.activity_id,)).fetchone():
            print('Worklog already synchronized');return
        seconds=max(0,round((dt.datetime.fromisoformat(end)-dt.datetime.fromisoformat(start)).total_seconds()))
        if seconds<60:raise ValueError('Activity shorter than 60 seconds; not exported')
        payload={'started':dt.datetime.fromisoformat(start).strftime('%Y-%m-%dT%H:%M:%S.000+0000'),'timeSpentSeconds':seconds,'comment':{'type':'doc','version':1,'content':[{'type':'paragraph','content':[{'type':'text','text':'AIFlow activity #'+str(args.activity_id)}]}]}}
        if not args.apply:
            print(json.dumps({'dry_run':True,'remote_key':mapping[0],'seconds':seconds,'payload':payload},indent=2));return
        from urllib.parse import quote
        result=_request('POST','issue/'+quote(mapping[0],safe='')+'/worklog',payload)
        remote_id=result.get('id')
        if not remote_id:raise ValueError('Jira did not return worklog ID; check remote before retrying to prevent duplicates')
        db.execute('INSERT INTO tracker_worklogs(activity_id,remote_key,remote_id,seconds) VALUES(?,?,?,?)',(args.activity_id,mapping[0],str(remote_id),seconds))
        db.commit()
        print('Jira worklog created:',remote_id)
