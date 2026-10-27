"""Regression tests for project-scoped digest and SMTP failure isolation."""
import datetime as dt
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from installer import digest

class DigestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'SampleProject'
        (self.root/'.aiflow/state').mkdir(parents=True)
        self.db=sqlite3.connect(':memory:')
        self.db.executescript("""
            CREATE TABLE events(created_at TEXT,kind TEXT,ref TEXT,details TEXT);
            CREATE TABLE epics(id TEXT,title TEXT,status TEXT,created_at TEXT,updated_at TEXT);
            CREATE TABLE tasks(epic_id TEXT,id TEXT,title TEXT,status TEXT,created_at TEXT,updated_at TEXT);
            CREATE TABLE activities(epic_id TEXT,task_id TEXT,started_at TEXT,ended_at TEXT);
        """)
        self.day='2026-10-27'
        self.db.execute("INSERT INTO epics VALUES ('EPIC-001','Refunds','active','2026-10-27T08:00:00+00:00','2026-10-27T08:00:00+00:00')")
        self.db.execute("INSERT INTO tasks VALUES ('EPIC-001','TASK-001','Webhook','done','2026-10-27T08:00:00+00:00','2026-10-27T09:00:00+00:00')")
        self.db.execute("INSERT INTO activities VALUES ('EPIC-001','TASK-001','2026-10-27T08:00:00+00:00','2026-10-27T09:00:00+00:00')")
        self.db.execute("INSERT INTO events VALUES ('2026-10-27T09:00:00+00:00','decision.approve','EPIC-001','Use queue')")
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_report_contains_metrics_and_decisions(self):
        data=digest.snapshot(self.db,self.day,'Europe/Rome')
        self.assertEqual(data['minutes'],60)
        self.assertEqual(len(data['tasks']['worked']),1)
        page,plain=digest.render(self.root.name,data)
        self.assertIn('Use queue',page)
        self.assertIn('60.0 minuti',plain)
        self.assertIn('TASK-001',page)
    def test_missing_smtp_never_prevents_report(self):
        with patch.dict('os.environ',{},clear=True):
            result=digest.generate(self.root,self.db,self.day)
        self.assertEqual(result['mail_status'],'not_configured')
        self.assertTrue(Path(result['digest']).is_file())
    def test_duplicate_send_prevention(self):
        with patch.object(digest,'send_mail',return_value=('sent',None)) as sender:
            first=digest.generate(self.root,self.db,self.day)
            second=digest.generate(self.root,self.db,self.day)
        self.assertEqual(first['mail_status'],'sent')
        self.assertEqual(second['mail_status'],'already_sent')
        self.assertEqual(sender.call_count,1)
    def test_failed_delivery_is_retryable(self):
        with patch.object(digest,'send_mail',side_effect=[('failed','temporary'),('sent',None)]) as sender:
            self.assertEqual(digest.generate(self.root,self.db,self.day)['mail_status'],'failed')
            self.assertEqual(digest.generate(self.root,self.db,self.day)['mail_status'],'sent')
        self.assertEqual(sender.call_count,2)

if __name__=='__main__':unittest.main()
